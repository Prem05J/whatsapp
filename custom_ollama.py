import os
import ollama
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings

class OllamaHelper:
    def __init__(self, file_path):
        self.file_path = file_path
        self.retriever = None

    def initialize(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, "r", encoding="utf-8") as file:
                text = file.read()

            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            splits = text_splitter.split_text(text)

            embeddings = OllamaEmbeddings(model="mistral")
            vectorstore = Chroma.from_texts(texts=splits, embedding=embeddings)

            self.retriever = vectorstore.as_retriever()
        else:
            print("File not found at the specified path.")
    
    def rag_chain(self, question):
        if self.retriever:
            retrieved_docs = self.retriever.invoke(question)
            doc_texts = [doc.page_content for doc in retrieved_docs]
            formatted_context = "\n\n".join(doc_texts)
            return self.ollama_llm(question, formatted_context)
        else:
            print("Retriever not initialized. Call initialize() first.")
    
    def ollama_llm(self, question, context):
        formatted_prompt = f"Question: {question}\n\nContext: {context}"
        response = ollama.chat(model='mistral', messages=[{'role': 'user', 'content': formatted_prompt}])
        return response['message']['content']


