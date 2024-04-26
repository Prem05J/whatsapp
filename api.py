from flask import Flask, request, jsonify
import requests
import os
import openai
import custom_chatgpt
from langdetect import detect
import os
app = Flask(__name__)

# Configure your OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')
MYTOKEN = "SIVRA"  
TOKEN = "EAAT4CLfbRNQBO7kEZA2HrmV6OK5eKMIjAaFY0KCa6Ud8xEis9ZBSVf9ZBUSwOl7ZBn2X0dbMD8zkH6yaNF0vAGwYgiZBe3QmSwdUnyTBxVrCUypybddhNK4ZBoUI94PSftSUjvDd9xZBprUFJAlk9Hi51TIrjHjkJQ9ZAZAVgU0ZAWhE71i7UPyoPCwvs4Vd9QZBbChwXnmHXct2mquRiN3SQZDZD"


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
            if entry and entry[0].get('changes') and entry[0]['changes'][0].get('value', {}).get('messages'):
                phone_no_id = entry[0]['changes'][0]['value']['metadata']['phone_number_id']
                from_number = entry[0]['changes'][0]['value']['messages'][0]['from']
                msg_body = entry[0]['changes'][0]['value']['messages'][0]['text']['body']

                print("phone number:", phone_no_id)
                print("from:", from_number)
                print("message body:", msg_body)
                

                # Generate response using ChatGPT
                response_text = custom_chatgpt.process_message(msg_body)
                language = detect(response_text)
                print(response_text)
                print(language)
                # Send the response back
                response = requests.post(
                    f"https://graph.facebook.com/v13.0/{phone_no_id}/messages?access_token={TOKEN}",
                    json={
                        "messaging_product": "whatsapp",
                        "to": from_number,
                        "text": {"body": response_text},
                        "language": language
                    }
                )
                # response = requests.post(
                #     f"https://graph.facebook.com/v18.0/{phone_no_id}/messages?access_token={TOKEN}",
                #     json={
                #         "messaging_product": "whatsapp",
                #         "recipient_type": "individual",
                #         "to": from_number,
                #         "type": "template",
                #         "template": {
                #             "name": "language",
                #             "language": {
                #                 "code": language
                #             }
                #         },
                #         "components": 
                #             {
                #                 "type": "body",
                #                 "parameters": [
                #                     {
                #                         "type": "text",
                #                         "text": response_text
                #                     }
                #                 ]
                #             }
                #         }
                #     )

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




