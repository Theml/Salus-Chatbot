# Salus - Assistente da Saúde 🤖💚

Salus é um chatbot desenvolvido como atividade acadêmica para a disciplina de Inteligência Artificial e Machine Learning. Ele atua como um assistente virtual de saúde, respondendo dúvidas sobre nutrição, prevenção de doenças, exercícios físicos, saúde mental e outros temas relacionados ao bem-estar.

## Funcionalidades

- Responde perguntas sobre saúde, nutrição, exercícios e prevenção de doenças.
- Mantém contexto de conversa para fornecer dicas específicas quando solicitado.
- Interface web simples e intuitiva.
- Fácil de personalizar e expandir com novos tópicos e respostas.

## Tecnologias Utilizadas

- Python 3
- Flask (backend)
- HTML, CSS e JavaScript (frontend)
- Regex para categorização de perguntas

## Como Executar

1. Clone este repositório:
   ```bash
   git clone https://github.com/seu-usuario/chatbot-salus.git
   ```
2. Instale as dependências:
   ```bash
   pip install flask
   ```
3. Execute o servidor:
   ```bash
   python chatbot.py
   ```
4. Acesse no navegador: [http://localhost:5000](http://localhost:5000)

## Estrutura do Projeto

```
ChatBot/
├── chatbot.py
├── templates/
│   └── chat.html
├── static/
│   └── chat.css
├── README.md
```

## Exemplos de Uso

- **Usuário:** Oi  
  **Salus:** Olá! O que você gostaria de saber sobre saúde hoje?

- **Usuário:** Como posso prevenir diabetes?  
  **Salus:** Para prevenir diabetes, recomendo: 1) Manter uma alimentação balanceada rica em fibras e baixa em açúcares, 2) Praticar exercícios regularmente, 3) Manter peso saudável, 4) Fazer exames de glicemia periodicamente. Gostaria de dicas específicas sobre algum desses pontos?

- **Usuário:** Sim  
  **Salus:** Aqui estão algumas dicas específicas:  
  - Inclua mais fibras na alimentação, como aveia, frutas e vegetais.  
  - Evite bebidas açucaradas e prefira água ou sucos naturais sem açúcar.  
  - Pratique pelo menos 150 minutos de atividade física por semana.  
  - Mantenha um peso saudável e faça exames de glicemia regularmente.

## Contribuição

Sinta-se à vontade para abrir issues ou enviar pull requests com melhorias, correções ou novas funcionalidades!

## Licença

Este projeto é apenas para fins acadêmicos e educacionais.

---

Desenvolvido por Luis Gustavo Theml Novais e Marciana Pereira Costa para a disciplina de Inteligência Artificial e Machine Learning.