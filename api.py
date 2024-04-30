from flask import Flask, request, jsonify
import requests
import os
import openai
import custom_chatgpt
from langdetect import detect
import os
app = Flask(__name__)
from flask_mysqldb import MySQL
import custom_ollama

app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Premkumar@05'
app.config['MYSQL_DB'] = 'whatsapp'


mysql = MySQL(app)

# Configure your OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')
MYTOKEN = "SIVRA"  
TOKEN = "EAAT4CLfbRNQBOythLRG0RFVhTgXu6t0tu9qjZBij7tHvqELiKdLKWF89arpuJQDD8TnaG3S0ekvhuxRVCFnuvhZCO6QYMl96qZCjtA3468m3LwqCn6m88mLmUD1BnaK5FMtTZCoCIrmIFq5WztenoWIZAZC2BePZBpORctYZCHoZC1MnL8TP4P6AUQpzqCKepDkwBJRq2Y0ON6VcP5gcCnAZDZD"


def insert_user(username):
    try:
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (user_name) VALUES (%s)", (username,))
        mysql.connection.commit()
        cur.close()
        return "User inserted successfully"
    except Exception as e:
        return f"Error inserting user: {str(e)}"

def check_user_existence(username):
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT COUNT(*) FROM users WHERE user_name = %s", (username,))
        count = cur.fetchone()[0]
        cur.close()
        return count > 0
    except Exception as e:
        return f"Error checking user existence: {str(e)}"

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        mode = request.args.get('hub.mode')
        challenge = request.args.get('hub.challenge')
        verify_token = request.args.get('hub.verify_token')

        if mode and verify_token:
            if mode == "subscribe" and verify_token == MYTOKEN:
                return challenge, 200
            else:
                return "Forbidden", 403
    elif request.method == 'POST':
        data = request.json
        if 'object' in data:
            entry = data.get('entry', [])
            print(entry)
            if entry and entry[0].get('changes') and entry[0]['changes'][0].get('value', {}).get('messages'):
                phone_no_id = entry[0]['changes'][0]['value']['metadata']['phone_number_id']
                from_number = entry[0]['changes'][0]['value']['messages'][0]['from']
                button_text = entry[0]['changes'][0]['value']['messages'][0]['type']
                if button_text == "text":
                    msg_body = entry[0]['changes'][0]['value']['messages'][0]['text']['body']
                    

                
                print("phone number:", phone_no_id)
                print("from:", from_number)
                # language = detect(response_text)
                # print(response_text)
                # print(language)
                if False:
                    return 
                if check_user_existence(from_number) and button_text == "text":
                    custom_ai = custom_ollama.OllamaHelper("./file.txt")
                    custom_ai.initialize()
                    response_text = custom_ai.rag_chain(msg_body)
                    print(response_text)
                    # Send the response back
                    response = requests.post(
                        f"https://graph.facebook.com/v18.0/{phone_no_id}/messages?access_token={TOKEN}",
                        json={
                            "messaging_product": "whatsapp",
                            "recipient_type": "individual",
                            "to": from_number,
                            "type": "template",
                            "template": {
                                "name": "image_",
                                "language": {
                                    "code": "en_GB"
                                },
                                "components": [
                                    {
                                        "type": "header",
                                        "parameters": [
                                            {
                                                "type": "image",
                                                "image": {
                                                    "link": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c1/71-715457_bjp-logo-hd-image-co.jpg/1280px-71-715457_bjp-logo-hd-image-co.jpg"
                                                }
                                            }
                                        ]
                                    },
                                    {
                                        "type": "body",
                                        "parameters": [
                                            {
                                                "type": "text",
                                                "text": response_text
                                            }
                                        ]
                                    }
                                ]
                            }
                        }
                        )
                elif button_text == "button":
                    button_language = entry[0]['changes'][0]['value']['messages'][0]["button"]["payload"]
                    response_text = {
                            "Telugu": "కొనసాగు",
                            "Hindi": "जारी रखें",
                            "Kannada": "ಮುಂದುವರೆಸು",
                            "English" : "Continue"
                        }
                    language = {
                            "Telugu": "te",
                            "Hindi": "hi",
                            "Kannada": "kn",
                            "English" : "en"
                        }
                    response_data = response_text[button_language]
                    lang = language[button_language]
                    response = requests.post(
                        f"https://graph.facebook.com/v18.0/{phone_no_id}/messages?access_token={TOKEN}",
                        json={
                            "messaging_product": "whatsapp",
                            "to": from_number,
                            "text": {"body": response_data},
                            "language": lang
                        }
                    )
                    insert_user(from_number)
                elif not check_user_existence(from_number):
                    response = requests.post(
                        f"https://graph.facebook.com/v18.0/{phone_no_id}/messages?access_token={TOKEN}",
                        json={
                            "messaging_product": "whatsapp",
                            "recipient_type": "individual",
                            "to": from_number,
                            "type": "template",
                            "template": {
                                "name": "language_preferrence",
                                "language": {
                                    "code": "en_GB"
                                }
                            }
                        }
                    )
                    return "", 200
                if response.ok:
                    return "", 200
                else:
                    return "", 500
                

    return "", 404

@app.route('/')
def index():
    return "Hello, this is webhook setup"

# def generate_answer(question):
#     model_engine = "gpt-3.5-turbo-instruct"
#     prompt = (f"Q: {question}\n"
#               "A:")
#     response = openai.Completion.create(
#         engine=model_engine,
#         prompt=prompt,
#         max_tokens=1024,
#         n=1,
#         stop=None,
#         temperature=0.7,
#     )
#     answer = response.choices[0].text.strip()
#     return answer


if __name__ == '__main__':
    app.run(port=int(os.getenv("PORT", 80)))



