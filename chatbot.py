import random
import nltk
from nltk.chat.util import Chat, reflections
from flask import Flask, render_template, request, jsonify

# Antes de tentar executar rodar os comandos `python -m venv venv`,`.\venv\Scripts\Activate`, `pip install nltk`, pip install flask, `python -m nltk.downloader all` 
pares = [
    [
        r"Oi|Olá|E ai",
        ["Olá", "Como posso ajudar você?", "Oi como está?"],
    ],
    [
        r"Qual o seu nome\?",
        ["Meu nome é Chatbot", "Você pode me chamar de Chatbot", "Sou o Chatbot IX"],
    ],
    [
        r"Qual é a sua idade\?",
        ["Eu sou um programa de computador, não tenho idade.", "Idade é apenas um número, certo?"],
    ],
    [
        r"Qual é o seu propósito\?",
        ["Meu propósito é ajudar você com suas perguntas e dúvidas.", "Estou aqui para ajudar!"],
    ],
    [
        r"Como você está\?",
        ["Estou ótimo","Estou apenas um programa, mas obrigado por perguntar!", "Estou aqui para ajudar!"],
    ],
    [
        r"Olá meu nome é (.*)",
        ["Olá %1, prazer em te conhcer!"],
    ],
    [
        r"adeus|tchau",
        ["Adeus foi um prazer conversar com você!"],
    ],
    [
        r"(.*)\?",
        ["Desculpe, não tenho uma resposta para essa pergunta.", "Pode reformular a pergunta?"],
    ],
]

def carregar_conhecimento(arquivo_pdf):
    pares_personalizados = []
    try:
        reader = PdfReader(arquivo_pdf)
        texto = ""
        for pagina in reader.pages:
            texto += pagina.extract_text()

        linhas = texto.split("\n")

        for linha in linhas:
                if ":" in linha:
                    partes = linha.strip().split(":")
                    if len(partes) == 2:
                        pergunta = partes[0].strip()
                        resposta = partes[1].strip()
                        pares_personalizados.append([pergunta, [resposta]])
    except FileNotFoundError:
        print(f"Arquivo PDF {arquivo_pdf} não encontrado. Usando pares padrão.")
    except Exception as e:
        print(f"Erro ao carregar o arquivo PDF: {e}. Usando pares padrão.")
    return pares_personalizados

pares_personalizados = carregar_conhecimento("Algorithms.pdf")

pares.extend(pares_personalizados)

pares.extend([
    [r"(.*)", ["Entendi. Diga-me mais.", "Pode me contar mais sobre isso?", "Interessante. Conte me mais..."]],
])

reflections = {
    "eu" : "você",
    "meu" : "seu",
    "meus" : "seus",
    "minha" : "sua",
    "minhas" : "suas",
    "sou" : "é",
    "estou" : "está",
    "fui" : "foi",
    "era" : "é",
    "você" : "eu",
    "seu" : "meu",
    "eu sou": "você é",
    "você é" : "eu sou",
    "você estava" : "eu estava",
    "eu estava" : "você estava",
}

chatbot = Chat(pares, reflections)

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("chat.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    print(f"Dados recebidos: {data}")
    user_input = data.get("message")
    response = chatbot.respond(user_input)
    print(f"Resposta do chatbot: {response}")
    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
