import openai
import os

# Defina sua chave de API da OpenAI


# Função para carregar sentenças de uma pasta
def carregar_sentencas(pasta_origem):
    sentencas = []
    for arquivo in os.listdir(pasta_origem):
        if arquivo.endswith(".txt"):
            caminho_arquivo = os.path.join(pasta_origem, arquivo)
            with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                sentencas += f.readlines()  # Carrega cada linha (sentença) do arquivo
    return [s.strip() for s in sentencas if s.strip()]

# Função para gerar sentenças usando a API do ChatGPT
def gerar_novas_sentencas(sentencas_iniciais, num_novas_sentencas, modelo='gpt-3.5-turbo'):
    novas_sentencas = []
    prompt_inicial = "\n".join(sentencas_iniciais) + "\n\nBaseado nas sentenças acima, crie novas sentenças-modelo:"

    for _ in range(num_novas_sentencas):
        resposta = openai.ChatCompletion.create(
            model=modelo,
            messages=[{"role": "system", "content": "Você é um assistente útil."},
                      {"role": "user", "content": prompt_inicial}],
            max_tokens=100,
            n=1,
            temperature=0.7,
        )
        nova_sentenca = resposta['choices'][0]['message']['content'].strip()
        novas_sentencas.append(nova_sentenca)
    
    return novas_sentencas

# Função para salvar as novas sentenças em um arquivo em outro diretório
def salvar_sentencas(novas_sentencas, pasta_destino, nome_arquivo='novas_sentencas.txt'):
    if not os.path.exists(pasta_destino):
        os.makedirs(pasta_destino)
    
    caminho_arquivo = os.path.join(pasta_destino, nome_arquivo)
    with open(caminho_arquivo, 'w', encoding='utf-8') as f:
        for sentenca in novas_sentencas:
            f.write(sentenca + '\n')
    print(f"Novas sentenças salvas em: {caminho_arquivo}")

# Definir os diretórios de origem e destino
pasta_origem = '/mnt/D/projetos/ia_projetos/CLS_PCE_SENTENCAS/artefatos_sinapses/DATASET/OUTROS'  # Diretório onde estão os arquivos de sentenças
pasta_destino = '/mnt/D/projetos/ia_projetos/CLS_PCE_SENTENCAS/artefatos_sinapses/DATASET/OUTROS/modelos_chatgpt'  # Diretório onde serão salvas as novas sentenças

# Carregar as sentenças existentes
sentencas_iniciais = carregar_sentencas(pasta_origem)

# Gerar 50 novas sentenças-modelo
num_novas_sentencas = 50
novas_sentencas = gerar_novas_sentencas(sentencas_iniciais, num_novas_sentencas)

# Salvar as novas sentenças no diretório de destino
salvar_sentencas(novas_sentencas, pasta_destino)
