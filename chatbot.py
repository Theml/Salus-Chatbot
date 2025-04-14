import random
import nltk
from nltk.chat.util import Chat, reflections
from nltk.tokenize import sent_tokenize
from flask import Flask, render_template, request, jsonify
import re

# Antes de tentar executar rodar os comandos `python -m venv venv`,`.\venv\Scripts\Activate`, `pip install nltk`, pip install flask, `python -m nltk.downloader all` http://127.0.0.1:5000

reflections = {
    "eu": "você",
    "meu": "seu",
    "meus": "seus",
    "minha": "sua",
    "minhas": "suas",
    "sou": "é",
    "estou": "está",
    "fui": "foi",
    "era": "é",
    "você": "eu",
    "seu": "meu",
    "seus": "meus",
    "sua": "minha",
    "suas": "minhas",
    "eu sou": "você é",
    "você é": "eu sou",
    "você estava": "eu estava",
    "eu estava": "você estava",
}

pares = [
    [
        r"Qual (é )?a sua idade\?|Há quanto tempo existe(s)?\?",
        ["Sou um assistente virtual de saúde recém-desenvolvido, focado em fornecer informações úteis sobre saúde e bem-estar.", 
         "Não tenho idade no sentido humano, mas estou sempre atualizado com as melhores informações de saúde para ajudá-lo."]
    ],
    [
        r"Qual (é )?o seu propósito\?",
        ["Meu propósito é orientar sobre hábitos saudáveis e fornecer informações sobre saúde e bem-estar.", 
         "Estou aqui para ajudar você a cuidar melhor da sua saúde, fornecendo dicas e orientações baseadas em boas práticas."]
    ],
    [
        r"Como você está\?",
        ["Estou funcionando perfeitamente e pronto para ajudar com suas dúvidas sobre saúde!", 
         "Estou bem e preparado para auxiliar você com questões de saúde e bem-estar. Como posso ajudar hoje?"]
    ],
    [
        r"Ol(á|a) meu nome (é|e) (.*)",
        ["Olá %3, prazer em conhecê-lo! Como posso ajudar com sua saúde hoje?", 
         "Muito prazer, %3! Sou Salus, seu assistente de saúde. Como posso ajudá-lo?"]
    ],
    [
        r"(.*)prevenir(.*)diabetes(.*)",
        ["Para prevenir diabetes, recomendo: 1) Manter uma alimentação balanceada rica em fibras e baixa em açúcares, 2) Praticar exercícios regularmente, 3) Manter peso saudável, 4) Fazer exames de glicemia periodicamente. Gostaria de dicas específicas sobre algum desses pontos?",
         "A prevenção da diabetes envolve alimentação equilibrada, atividade física regular, controle do peso e check-ups médicos anuais. Posso detalhar alguma dessas medidas preventivas?"]
    ],
    [
        r"(.*)melhorar(.*)alimentação(.*)",
        ["Para melhorar sua alimentação: 1) Aumente o consumo de alimentos naturais, 2) Reduza ultraprocessados, 3) Beba bastante água, 4) Inclua frutas e vegetais em todas as refeições. Gostaria de um exemplo de cardápio saudável?",
         "Uma boa estratégia para melhorar a alimentação é o método do prato: metade com vegetais, um quarto com proteínas e um quarto com carboidratos. Quer algumas sugestões de lanches saudáveis?"]
    ],
    [
        r"(.*)burnout(.*)",
        ["O burnout é caracterizado por exaustão extrema, cinismo e redução da eficácia profissional. Sinais incluem cansaço persistente, irritabilidade, dificuldade de concentração e desmotivação. Recomendo procurar um psicólogo ou médico para avaliação. Posso ajudar a encontrar recursos de apoio?",
         "Para lidar com o burnout, é importante estabelecer limites no trabalho, praticar autocuidado, buscar apoio social e, principalmente, procurar ajuda profissional. Gostaria de dicas para gerenciar o estresse diário?"]
    ],
    [
        r"(.*)(ansioso|ansiedade|ansio)(.*)",
        ["Para controlar a ansiedade, experimente: 1) Técnicas de respiração profunda, 2) Meditação por 10 minutos diários, 3) Atividade física regular, 4) Reduzir consumo de cafeína. Para casos persistentes, é fundamental buscar ajuda profissional. Posso explicar alguma dessas técnicas?",
         "Sentir ansiedade é comum, mas quando interfere na qualidade de vida, merece atenção. Além de técnicas de relaxamento, sono adequado e alimentação balanceada ajudam. Considera consultar um psicólogo ou psiquiatra para orientação personalizada?"]
    ],
    [
        r"O que devo evitar comer com frequência\?",
        ["Recomendo evitar: 1) Alimentos ultraprocessados, 2) Excesso de açúcar refinado, 3) Gorduras trans, 4) Bebidas açucaradas, 5) Excesso de sódio. Tente substituir por opções naturais como frutas, legumes, grãos integrais e proteínas magras. Posso sugerir alternativas saudáveis para algum alimento específico?",
         "Para uma alimentação saudável, limite alimentos com corantes artificiais, conservantes, excesso de açúcar, sal e gorduras saturadas. Prefira sempre alimentos na sua forma natural. Gostaria de dicas para interpretar rótulos de alimentos?"]
    ],
    [
        r"Quantas vezes por semana devo me exercitar\?",
        ["A OMS recomenda pelo menos 150 minutos semanais de atividade física moderada (como caminhada rápida) ou 75 minutos de atividade intensa, distribuídos em pelo menos 3 dias da semana. Além disso, exercícios de fortalecimento muscular 2 vezes por semana. O ideal é encontrar atividades que você goste para manter a consistência. Posso sugerir algumas opções?",
         "O ideal é praticar atividade física de 3 a 5 vezes por semana, combinando exercícios aeróbicos e de força. Mas lembre-se: qualquer movimento é melhor que nenhum! Comece devagar e aumente gradualmente. Qual tipo de exercício mais lhe interessa?"]
    ],
    [
        r"Como faço para marcar consulta pelo SUS\?",
        ["Para marcar consulta pelo SUS: 1) Vá à Unidade Básica de Saúde (UBS) mais próxima com seu cartão SUS, RG e comprovante de residência, 2) No local, informe sua necessidade e solicite o agendamento, 3) Para especialistas, normalmente é necessário encaminhamento do clínico geral. Algumas cidades também oferecem agendamento por aplicativo ou telefone. Posso ajudar a encontrar a UBS mais próxima de você?",
         "O primeiro passo é procurar a Unidade Básica de Saúde do seu bairro com documentos pessoais e cartão SUS. Lá você pode agendar consultas com médicos da família ou clínicos gerais. Para especialistas, normalmente precisa de encaminhamento. Você já tem seu cartão SUS?"]
    ],
    [
        r"Qual o melhor horário para tomar sol\?",
        ["Os horários mais seguros para exposição solar são antes das 10h e depois das 16h, quando a radiação UV é menos intensa. Mesmo nesses horários, use protetor solar FPS 30 ou maior, reaplique a cada 2 horas e limite a exposição direta. A exposição solar moderada é importante para a síntese de vitamina D. Você tem dúvidas sobre proteção solar?",
         "Para benefícios da vitamina D com menor risco, exponha-se ao sol antes das 10h ou após as 16h, por 15-20 minutos. Evite o período entre 10h e 16h, quando os raios UV são mais prejudiciais. Lembre-se que protetor solar é essencial em qualquer horário!"]
    ],
    [
        r"Faz mal ficar muito tempo (parado|sentado)\?",
        ["Sim, o sedentarismo prolongado está associado a diversos problemas de saúde, como doenças cardiovasculares, diabetes tipo 2, obesidade e problemas musculoesqueléticos. Recomenda-se levantar e movimentar-se por 5 minutos a cada hora de atividade sentada. Pequenas mudanças como usar escadas, caminhar durante ligações telefônicas ou fazer pausas ativas podem fazer grande diferença. Gostaria de dicas de exercícios rápidos para fazer durante o dia?",
         "Ficar muito tempo sentado ou parado é considerado o 'novo fumo' por especialistas devido aos riscos à saúde. Mesmo quem pratica exercícios regularmente deve evitar passar longos períodos sem se movimentar. Tente estabelecer um alarme para levantar a cada 50 minutos. Posso sugerir alguns exercícios de alongamento para esses intervalos?"]
    ],
    [
        r"Onde posso (vacinar|tomar vacina)(.*)\?",
        ["Vacinas do calendário básico estão disponíveis gratuitamente em Unidades Básicas de Saúde (UBS). Para saber quais vacinas estão disponíveis e os horários de atendimento, recomendo contatar a Secretaria de Saúde do seu município ou visitar a UBS mais próxima. Em campanhas específicas, podem existir postos móveis em locais públicos. Posso ajudar você a encontrar informações sobre alguma vacina específica?",
         "A vacinação é geralmente realizada em postos de saúde, UBS e alguns hospitais públicos. Durante campanhas, podem ser montados postos temporários em locais de grande circulação. Você está com alguma vacina específica em mente?"]
    ],
    [
        r"(.*)litros de água devo beber(.*)",
        ["A recomendação geral é de aproximadamente 35ml de água por kg de peso corporal por dia (cerca de 2-3 litros para adultos), mas isso varia conforme seu peso, nível de atividade física, clima e condições de saúde. Sinais de boa hidratação incluem urina clara ou amarelo-claro. Em dias quentes ou durante exercícios, aumente a ingestão. Gostaria de dicas para se manter bem hidratado?",
         "Embora o famoso '8 copos por dia' (cerca de 2 litros) seja uma boa referência, a necessidade hídrica varia para cada pessoa. Fatores como peso, clima e atividade física influenciam essa necessidade. Uma dica prática: observe a cor da sua urina - se estiver escura, você precisa beber mais água."]
    ],
    [
        r"Quais exames devo fazer todo ano\?",
        ["Os check-ups anuais geralmente incluem: 1) Exames de sangue (hemograma completo, glicemia, colesterol), 2) Aferição de pressão arterial, 3) Avaliação de IMC e circunferência abdominal. Dependendo da idade, sexo e histórico familiar, outros exames específicos podem ser recomendados, como mamografia, PSA, colonoscopia. O ideal é consultar um médico para recomendações personalizadas. Você tem alguma condição específica de saúde?",
         "Para adultos, recomenda-se anualmente: exames de sangue básicos, verificação de pressão arterial, avaliação de peso e consultas com clínico geral. Mulheres devem incluir consulta ginecológica e homens acima de 45 anos, avaliação da próstata. O médico pode recomendar exames adicionais com base no seu histórico. Posso explicar a importância de algum exame específico?"]
    ],
    [
        r"(.*)(dor(es)? de cabeça|cefaleia)(.*)",
        ["Dores de cabeça podem ter diversas causas: estresse, desidratação, má postura, problemas de visão, tensão muscular ou mesmo condições médicas mais sérias. Para dores ocasionais, recomendo descanso, hidratação adequada e técnicas de relaxamento. Caso as dores sejam frequentes ou intensas, é importante consultar um médico. Você identifica algum padrão ou gatilho para suas dores de cabeça?",
         "Para aliviar dores de cabeça comuns, experimente: 1) Descansar em ambiente calmo e escuro, 2) Aplicar compressas mornas ou frias, 3) Manter boa hidratação, 4) Praticar técnicas de relaxamento. Se a dor for intensa, recorrente ou acompanhada de outros sintomas, busque avaliação médica. Suas dores de cabeça seguem algum padrão?"]
    ],
    [
        r"(.*)dormir melhor(.*)",
        ["Para melhorar a qualidade do sono: 1) Mantenha horários regulares para dormir e acordar, 2) Evite telas (celular, TV) 1h antes de dormir, 3) Evite cafeína após o meio-dia, 4) Crie um ambiente escuro, silencioso e confortável, 5) Pratique atividade física regularmente, mas não próximo da hora de dormir. Você está tendo dificuldades específicas com o sono?",
         "Uma boa higiene do sono inclui: estabelecer rotina noturna relaxante, manter o quarto fresco e escuro, evitar refeições pesadas à noite e limitar líquidos antes de dormir. Técnicas de relaxamento como respiração profunda também podem ajudar. Quantas horas de sono você geralmente consegue por noite?"]
    ],
    [
        r"(.*)gripe|resfriado(.*)",
        ["Para aliviar sintomas de gripe e resfriado: 1) Descanse bastante, 2) Mantenha-se bem hidratado, 3) Use solução salina nasal para descongestionar, 4) Faça gargarejo com água morna e sal para dor de garganta, 5) Considere analgésicos de venda livre para febre e dores. Procure um médico se tiver febre alta persistente, dificuldade para respirar ou sintomas que pioram após 7-10 dias. Está com algum sintoma específico que o incomoda mais?",
         "A diferença básica é que a gripe geralmente causa febre alta, dores no corpo e sintomas mais intensos, enquanto o resfriado tende a afetar mais as vias aéreas superiores com congestão e coriza. Para ambos, repouso e hidratação são fundamentais. A vacina anual contra gripe é uma medida preventiva importante. Você costuma se vacinar contra a gripe?"]
    ],
    [
        r"(.*)emagrecer|perder peso(.*)",
        ["Para um emagrecimento saudável: 1) Priorize mudanças sustentáveis de hábitos em vez de dietas restritivas, 2) Combine alimentação balanceada com déficit calórico moderado, 3) Pratique atividade física regular (aeróbica e de força), 4) Mantenha boa hidratação e sono adequado, 5) Considere acompanhamento com nutricionista para um plano personalizado. O ideal é perder 0,5-1kg por semana. Gostaria de dicas específicas sobre alimentação ou exercícios?",
         "O emagrecimento saudável envolve equilíbrio entre alimentação e atividade física, sem eliminar grupos alimentares. Alimentos ricos em fibras e proteínas promovem saciedade. Evite açúcares simples e processados. Lembre-se que resultados sustentáveis levam tempo. Já tentou alguma estratégia específica para emagrecer?"]
    ],
    [
        r"(.*)estou (cansado|cansada)(.*)",
        ["Cansaço pode ser causado por estresse, falta de sono, má alimentação ou sedentarismo. Tente identificar a causa e faça ajustes: durma bem, mantenha-se ativo e cuide da alimentação. Se o cansaço persistir, consulte um médico para investigar possíveis causas. Como tem sido sua rotina?",
         "O cansaço pode ser resultado de diversos fatores: estresse, má alimentação, falta de sono ou sedentarismo. Avalie sua rotina e veja se há algo que possa melhorar. Você tem conseguido dormir bem?"]
    ],
    [
        r"(.*)estou (doente|mal)(.*)",
        ["Se você está doente, recomendo procurar um médico para avaliação e tratamento adequado. Enquanto isso, descanse, hidrate-se e evite automedicação. Você tem algum sintoma específico que gostaria de discutir?",
         "Se você está se sentindo mal, é importante consultar um médico para diagnóstico e tratamento. Enquanto isso, mantenha-se hidratado e descanse. Posso ajudar com dicas de autocuidado enquanto você aguarda atendimento médico?"]
    ],
    [
        r"estou com dor no peito(.*)",
        ["Dor no peito pode ser um sinal sério e deve ser avaliada imediatamente por um médico. Se a dor for intensa, acompanhada de falta de ar, sudorese ou dor irradiando para o braço esquerdo, procure atendimento de emergência. Não hesite em buscar ajuda médica!",
         "Dor no peito pode ter várias causas, algumas graves. É essencial procurar atendimento médico imediatamente para avaliação. Não ignore esse sintoma! Você está sentindo outros sintomas associados?"]
    ],
    [
        r"estou com febre(.*)",
        ["Febre é um sinal de que o corpo está lutando contra uma infecção. Mantenha-se hidratado, descanse e use antitérmicos se necessário. Se a febre persistir por mais de 3 dias ou for muito alta, consulte um médico.",
         "A febre pode ser um sinal de infecção. Mantenha-se hidratado e descanse. Se a febre for alta ou persistente, busque orientação médica. Você tem outros sintomas associados?"]
    ],
    [
        r"estou com dor de barriga(.*)",
        ["Dor de barriga pode ter várias causas, desde indigestão até infecções. Se a dor for intensa, persistente ou acompanhada de vômitos, diarreia ou febre, consulte um médico. Enquanto isso, evite alimentos pesados e mantenha-se hidratado.",
         "A dor de barriga pode ser causada por diversos fatores. Se for leve, experimente chá de camomila ou gengibre. Mas se a dor persistir ou piorar, busque atendimento médico. Você tem notado outros sintomas?"]
    ],
    [
        r"(.*)dor no coração(.*)",
        ["Dor no coração pode ser um sinal sério. Se você está sentindo dor no peito, falta de ar ou outros sintomas associados, procure atendimento médico imediatamente. Não hesite em buscar ajuda!",
         "Dor no coração é um sintoma que não deve ser ignorado. Se você está sentindo isso, busque atendimento médico imediatamente. Você está tendo outros sintomas?"]
    ],
    [
        r"estou com tosse(.*)",
        ["Tosse pode ser um sintoma de várias condições, desde resfriados até alergias. Se a tosse persistir por mais de uma semana, for acompanhada de febre alta ou dificuldade para respirar, consulte um médico.",
         "A tosse pode ser causada por resfriados, alergias ou outras condições. Se for persistente ou acompanhada de outros sintomas como febre alta, consulte um médico. Você tem notado outros sintomas?"]
    ],
    [
        r"obrigado|valeu|agradeço(.*)",
        ["De nada! Estou aqui para ajudar com suas dúvidas de saúde.", 
         "Fico feliz em ajudar! Se precisar de mais informações sobre saúde, estou à disposição."]
    ],
    [
        r"obrigado|valeu|agradeço",
        ["De nada! Estou aqui para ajudar com suas dúvidas de saúde.", 
         "Fico feliz em ajudar! Se precisar de mais informações sobre saúde, estou à disposição."]
    ],
    [
        r"adeus|tchau",
        ["Até logo! Espero ter ajudado com suas dúvidas de saúde. Estou aqui quando precisar novamente.", 
         "Adeus! Cuide-se bem e volte quando tiver mais perguntas sobre saúde e bem-estar."]
    ],
    [
        r"(.*)\?",
        ["Desculpe, não tenho uma resposta para essa pergunta.", "Pode reformular a pergunta?"],
    ],
]

pares.extend([
    [r"(.*)\?", ["Como seu assistente de saúde, não tenho uma resposta específica para essa pergunta. Posso ajudar com dúvidas sobre alimentação saudável, exercícios, prevenção de doenças ou outros temas relacionados à saúde.", 
                "Essa é uma pergunta interessante, mas foge um pouco da minha especialidade em saúde. Posso ajudar com questões sobre bem-estar, nutrição, atividade física ou prevenção de doenças?"]],
])

pares.extend([
    [r"(.*)", ["Entendi. Como posso ajudar com sua saúde hoje?", 
              "Interessante. Há alguma dúvida específica sobre saúde que eu possa esclarecer?", 
              "Como seu assistente de saúde, estou aqui para orientá-lo. Tem alguma pergunta sobre hábitos saudáveis?"]],
])

categorias = {
    "nutricao": [
        [r"(.*)alimentação saudável(.*)", ["Uma alimentação saudável deve ser variada e colorida, incluindo todos os grupos alimentares em proporções adequadas. Priorize alimentos naturais, limite ultraprocessados e mantenha boa hidratação."]],
        [r"(.*)proteína(.*)", ["Boas fontes de proteína incluem carnes magras, peixes, ovos, laticínios, leguminosas e algumas sementes. A recomendação diária varia entre 0,8g a 2g por kg de peso corporal, dependendo do seu nível de atividade física."]],
        [r"(.*)carboidrato(.*)", ["Os carboidratos são nossa principal fonte de energia. Prefira carboidratos complexos como grãos integrais, tubérculos e leguminosas, que liberam energia gradualmente e contêm mais fibras e nutrientes."]],
        [r"(.*)gordura(.*)", ["Nem todas as gorduras fazem mal! Gorduras boas (insaturadas) encontradas em azeite, abacate, nozes e peixes são essenciais para a saúde cerebral e hormonal. Limite gorduras saturadas e evite as trans."]],
        [r"(.*)jejum intermitente(.*)", ["O jejum intermitente pode trazer benefícios como melhor controle glicêmico e ajuda na perda de peso, mas não é indicado para todos. Pessoas com certas condições médicas, gestantes e adolescentes devem evitar. Consulte um profissional antes de iniciar."]],
    ],
    "exercicios": [
        [r"(.*)exercício em casa(.*)", ["Exercícios eficazes para fazer em casa incluem: agachamentos, flexões, pranchas, afundos, elevação de panturrilha e exercícios com peso corporal. Comece com 3 séries de 10-15 repetições, 3 vezes por semana."]],
        [r"(.*)alongamento(.*)", ["Alongar-se diariamente melhora a flexibilidade, reduz tensão muscular e pode prevenir lesões. Mantenha cada alongamento por 15-30 segundos, sem fazer movimentos bruscos ou sentir dor."]],
        [r"(.*)cardio(.*)", ["Exercícios cardiovasculares como caminhada, corrida, natação e ciclismo fortalecem o coração, melhoram a capacidade pulmonar e ajudam no controle do peso. O ideal é praticar pelo menos 150 minutos por semana."]],
        [r"(.*)musculação(.*)", ["O treinamento de força ajuda a aumentar a massa muscular, acelera o metabolismo e fortalece os ossos. Para iniciantes, recomenda-se 2-3 sessões semanais com intervalo de 48h para os mesmos grupos musculares."]],
    ],
    "saude_mental": [
        [r"(.*)estresse(.*)", ["Para gerenciar o estresse, experimente técnicas de respiração profunda, meditação, atividade física regular e estabeleça limites saudáveis entre trabalho e descanso. Hobbies e conexões sociais também são importantes."]],
        [r"(.*)depressão(.*)", ["A depressão é uma condição médica séria caracterizada por tristeza persistente, perda de interesse em atividades, alterações no sono e apetite. É fundamental buscar ajuda profissional com psicólogo ou psiquiatra."]],
        [r"(.*)meditação(.*)", ["A meditação regular pode reduzir ansiedade, melhorar concentração e promover bem-estar emocional. Comece com 5 minutos diários, focando na respiração, e aumente gradualmente o tempo."]],
        [r"(.*)terapia(.*)", ["A terapia psicológica é eficaz para tratar diversas condições emocionais e mentais. Existem diferentes abordagens como TCC, psicanálise e terapia comportamental. O SUS oferece atendimento psicológico gratuito."]],
    ],
    "prevenção": [
        [r"(.*)pressão alta(.*)", ["Para prevenir hipertensão: reduza o consumo de sal, mantenha peso saudável, pratique exercícios regularmente, limite o álcool, evite fumo e gerencie o estresse. Faça verificações periódicas mesmo sem sintomas."]],
        [r"(.*)diabetes(.*)", ["Prevenção de diabetes inclui manter peso saudável, atividade física regular, alimentação balanceada com baixo consumo de açúcar refinado e carboidratos simples, e check-ups regulares para monitorar a glicemia."]],
        [r"(.*)colesterol(.*)", ["Para controlar o colesterol: limite gorduras saturadas e trans, consuma mais fibras e ômega-3, pratique exercícios regularmente e mantenha peso adequado. Aveia, peixes, nozes e azeite são aliados nesse controle."]],
        [r"(.*)câncer(.*)", ["Medidas preventivas contra câncer incluem: não fumar, limitar álcool, manter peso saudável, dieta rica em vegetais, proteção solar, atividade física regular e exames preventivos específicos por idade e sexo."]],
    ],
    "covid": [
        [r"(.*)covid|coronavírus(.*)", ["Mesmo com a redução dos casos, é importante manter a higiene das mãos, atualizar a vacinação conforme recomendações e ficar atento a sintomas. Em caso de contágio, o isolamento ajuda a prevenir a disseminação."]],
        [r"(.*)vacina covid(.*)", ["As vacinas contra COVID-19 são seguras e eficazes na prevenção de casos graves e hospitalizações. Reforços podem ser recomendados periodicamente, especialmente para grupos de risco."]],
        [r"(.*)sintomas covid(.*)", ["Os principais sintomas da COVID-19 incluem febre, tosse seca, cansaço, dores no corpo, dor de garganta, perda de paladar ou olfato. Se apresentar sintomas, faça um teste e consulte um médico."]],
    ],
    "primeiros_socorros": [
        [r"(.*)desmaio(.*)", ["Se alguém desmaiar: 1) Deite a pessoa de costas e eleve as pernas, 2) Verifique respiração e pulso, 3) Afrouxe roupas apertadas, 4) Não ofereça alimentos ou bebidas, 5) Busque ajuda médica se o desmaio durar mais de 1-2 minutos ou se houver outros sinais preocupantes."]],
        [r"(.*)queimadura(.*)", ["Para queimaduras leves: resfrie a área com água corrente (não gelada) por 10-15 minutos, não aplique gelo, manteiga ou pasta de dente. Cubra com gaze estéril. Para queimaduras graves ou extensas, busque atendimento médico imediato."]],
        [r"(.*)engasgo(.*)", ["Se alguém estiver engasgado e não conseguir falar ou tossir: posicione-se atrás da pessoa, coloque uma mão fechada acima do umbigo e a outra por cima, e faça movimentos rápidos para dentro e para cima (Manobra de Heimlich)."]],
    ],
}

contexto = {
    "ultima_pergunta": None,
    "topico_atual" : None,
}

salus = Chat(pares, reflections)

def buscar_por_categoria(pergunta):
    for categoria, pares_categoria in categorias.items():
        for regex, respostas in pares_categoria:
            if re.search(regex, pergunta, re.IGNORECASE):
                contexto["topico_atual"] = categoria
                return random.choice(respostas)
    return None

def save_conversation_message(conversation_id, user_message, bot_response):
    """
    Salva mensagens da conversa em um arquivo JSON no servidor.
    Isto é opcional e complementa o armazenamento no localStorage do navegador.
    """
    conversation_file = os.path.join(CONVERSATIONS_DIR, f"{conversation_id}.json")
    
    if os.path.exists(conversation_file):
        with open(conversation_file, 'r', encoding='utf-8') as f:
            conversation = json.load(f)
    else:
        conversation = {
            "id": conversation_id,
            "created_at": datetime.now().isoformat(),
            "messages": []
        }
    
    conversation["messages"].append({
        "sender": "user",
        "text": user_message,
        "timestamp": datetime.now().isoformat()
    })
    
    conversation["messages"].append({
        "sender": "bot",
        "text": bot_response,
        "timestamp": datetime.now().isoformat()
    })
    
    with open(conversation_file, 'w', encoding='utf-8') as f:
        json.dump(conversation, f, ensure_ascii=False, indent=2)

app = Flask(__name__)
app.secret_key = 'salus_health_assistant'

@app.route("/")
def index():
    return render_template("chat.html")

@app.route("/chat", methods=["POST"])
def chat():
    global contexto
    data = request.json
    user_input = data.get("message")

    # tenta responder com base nos pares padrão
    response = salus.respond(user_input)

    if not response:
        response = buscar_por_categoria(user_input)

    contexto["ultima_pergunta"] = user_input

    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
