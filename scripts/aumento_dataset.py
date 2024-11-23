import random
import shutil
import re
import logging
import concurrent.futures
import pandas as pd
from pathlib import Path

# Configurando o logging para exibir as alterações no console e salvar em arquivo
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

# caminhos para os arquivos
lista_nomes = Path('/mnt/D/projetos/ia_projetos/CLS_PCE_SENTENCAS/arquivos/nomes.xlsx')
df_nomes = pd.read_excel(lista_nomes)

lista_zonas = Path('/mnt/D/projetos/ia_projetos/CLS_PCE_SENTENCAS/arquivos/zona_cidade.csv')
df_zonas = pd.read_csv(lista_zonas, sep=';', encoding='latin-1')

lista_partidos = Path('/mnt/D/projetos/ia_projetos/CLS_PCE_SENTENCAS/arquivos/partidos.xlsx')
df_partidos = pd.read_excel(lista_partidos)

lista_trechos = Path('/mnt/D/projetos/ia_projetos/CLS_PCE_SENTENCAS/arquivos/frases_chave.xlsx')
df_trechos = pd.read_excel(lista_trechos)

def gerar_num_processo():
    """Função para gerar um número de processo aleatório com o final '6.05.2024'."""
    return f"{random.randint(6000000, 6009999)}-{random.randint(10, 99)}.{random.randint(2020, 2024)}.6.05.2024".upper()

def substituir_num_processo(texto):
    """
    Substitui todos os números de processos por um número aleatório com o final '6.05.2024'.
    """
    regex_processo = r'\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}'    
    texto, num_substituicoes = re.subn(regex_processo, lambda _: gerar_num_processo(), texto)
    logging.info(f"Substituídos {num_substituicoes} números de processos.")
    return texto

def gerar_nome(df=df_nomes):
    """
    Gera um nome fictício a partir de um arquivo XLSX com nomes.
    """    

    numero = random.randint(1, len(df) - 1)
    nome = df.iloc[numero]['nome'].title()
    sobrenome1 = df.iloc[numero]['sobrenome1'].title()
    sobrenome2 = df.iloc[numero]['sobrenome2'].title()
    nome_completo = f'{nome} {sobrenome1} {sobrenome2}'
    logging.info(f"Gerado nome fictício: {nome_completo}")
    
    return nome_completo.upper()

def substituir_nome_juiz(texto):
    """
    Substitui o nome do juiz ou juíza no texto por um nome fictício gerado.
    """
    linhas = texto.splitlines()

    # Verificar se a última linha contém "Juiz" ou "Juíza" (case-insensitive)
    if re.search(r'\b(juiz|juíza|juiza)\b', linhas[-1], re.IGNORECASE):
        for i in range(len(linhas) - 2, -1, -1):
            if linhas[i].strip():
                novo_nome = gerar_nome().upper()
                logging.info(f"Substituindo nome do juiz por '{novo_nome}'")
                linhas[i] = novo_nome
                break

    return "\n".join(linhas)

def substituir_nomes(texto):
    """
    Substitui o nome do requerente, interessado, advogado ou responsável no texto por nomes fictícios diferentes.
    """

    return re.sub(r'((requerente|interessado|responsável|interessada!interessado\(a\)|fiscal da lei|requerente|requerido|advogado\(a\) do\(a\) requerente):)\s*.+', 
                lambda m: m.group(1) + ' ' + gerar_nome(), texto, flags=re.IGNORECASE)

def gerar_zona(df=df_zonas):
    """
    Gera zona eleitoral e cidade fictícia a partir de um arquivo CSV.
    """
    
    ordem_zona = random.randint(1, len(df) - 1)
    NR_ZONA = (df.iloc[ordem_zona]['NR_ZONA'])
    NM_MUNICIPIO = df.iloc[ordem_zona]['NM_MUNICIPIO']
    logging.info(f"Gerado zona/cidade: {NR_ZONA}ª zona eleitoral de {NM_MUNICIPIO.upper()}")
    
    return NR_ZONA, NM_MUNICIPIO.upper()

def substituir_zona(texto):
    """
    Substitui aleatoriamente a zona eleitoral e a cidade
    """
    regex_zona = r"(\d{1,3}ª zona eleitoral de) (.+?) ba"
    zonas_encontradas = re.findall(regex_zona, texto, re.IGNORECASE)
    zona_sub, cidade_sub = gerar_zona()

    for zona, cidade in zonas_encontradas:
        num_zona = zona[:4]
        logging.info(f"Substituindo '{num_zona}' e '{cidade}' por '{zona_sub}' e '{cidade_sub}'")
        texto = texto.replace(zona[:4], str(zona_sub) + 'ª').replace(cidade.lower(), cidade_sub.upper())

    return texto

def substituir_partido(texto, df=df_partidos):
    """
    Substitui o nome do partido aleatoriamente
    """
    
    for _, row in  df.iterrows():
        sigla_partido = row['sigla_partido']
        nome_partido = row['nome_partido']
        match_nome = re.search(nome_partido, texto)
        if match_nome:
            # seleciona sigla e nome de partido de forma aleatórioa
            index_df = random.randint(1,len(df))
            nome_sub = (df.iloc[index_df]['nome_partido']).upper()
            re.sub(match_nome,nome_sub.upper(),texto)
            match_sigla = re.search(sigla_partido, texto)
            if match_sigla:
                sigla_sub = df.iloc[index_df]['sigla_partido']
                re.sub(match_sigla, sigla_sub.upper(), texto)
    return texto

def substituir_trechos(texto, df=df_trechos):
    """
    Substitui todos os trechos do texto com base no arquivo 'frases_chave.xlsx'.
    Todas as expressões são procuradas e, se encontradas, são substituídas no texto.

    Args:
        texto (str): O texto no qual os trechos serão substituídos.

    Returns:
        str: O texto com os trechos substituídos.
    """
    logging.info(f"Substituindo trechos...")

    # Contador de substituições realizadas
    substituicoes = 0  

    # Iterar sobre cada linha do DataFrame, fazendo substituições
    trechos = []
    for _, row in df.iterrows():
        
        original = row['original'].lower()  # Obter a expressão original (minúsculas)
        substituto = row['substituto'].upper()  # Obter o substituto (maiúsculas)
        trechos.append((original, substituto))

    if len(trechos) > 2:
        trechos = random.sample(trechos, len(trechos)//3)
            
    for original, substituto in trechos:
        # Criar padrão de expressão regular para palavras inteiras
        pattern = r'\b' + re.escape(original) + r'\b'

        # Substituir todas as ocorrências do trecho original pelo substituto (palavra inteira)
        texto, num_substituicoes = re.subn(pattern, substituto, texto, flags=re.IGNORECASE)

        if num_substituicoes > 0:
            logging.info(f"Substituindo '{original}' por '{substituto}'")
            substituicoes += num_substituicoes

    logging.info(f'Total de {substituicoes} substituições realizadas.')
    return texto

def substituir_data(texto):
    """
    Substitui todas as datas no formato 'dd de mês de aaaa' no texto por um placeholder.
    """
    regex_data = r"\d{2} de (janeiro|fevereiro|março|abril|maio|junho|julho|agosto|setembro|outubro|novembro|dezembro) de \d{4}"
    matches = re.finditer(regex_data, texto)
    
    for match in matches:
        data_str = match.group()
        logging.info(f"Substituindo data '{data_str}' por '<data>'")
        texto = texto.replace(data_str, "<DATA>")
    
    return texto

def processar_arquivo(arquivo, quantidade, output_dir):

    """
    Processa o arquivo de texto em um diretório, aplicando as funções de substituição de informações
    sensíveis como números de processos, datas, nomes de juízes, advogados, partes, zona eleitoral e cidade.
    Os arquivos modificados são salvos em um novo diretório.
    
    Args:
        path (Path): Caminho do diretório que contém os arquivos de texto a serem processados.
        output_dir (Path): Caminho do diretório onde os arquivos processados serão salvos.
    """   
    with arquivo.open('r', encoding='utf-8') as file:
        texto = file.read().lower()

        texto = substituir_zona(texto)
        texto = substituir_num_processo(texto)
        texto = substituir_nomes(texto)
        texto = substituir_nome_juiz(texto)
        texto = substituir_data(texto)
        texto = substituir_partido(texto)
        texto = substituir_trechos(texto)

    novo_nome = f'{arquivo.stem}_gerado_{quantidade}{arquivo.suffix}'
    novo_arquivo = output_dir / novo_nome

    with novo_arquivo.open('w', encoding='utf-8') as file_out:
        file_out.write(texto)
        logging.info(f'Arquivo {novo_nome} salvo com sucesso.')

if __name__ == '__main__':

    # Caminho e configuração dos diretórios
    path = Path('/mnt/D/projetos/ia_projetos/CLS_PCE_SENTENCAS/artefatos_sinapses/sentencas_extensao_originais')
    output_dir = Path('/mnt/D/projetos/ia_projetos/CLS_PCE_SENTENCAS/artefatos_sinapses/DATASET/sentenca_extincao')
    # output_dir.mkdir(exist_ok=True)

    # Quantidade de arquivos a serem gerados
    num_arquivos = 3454
    contador = 0

    # Copiando os arquivos originais


    # ThreadPoolExecutor para processar os arquivos em paralelo
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        while contador < num_arquivos:                   
            for arquivo in path.glob('*.txt'):
                if contador > num_arquivos:
                    break
                logging.info(f"Processando arquivo {arquivo.name}...")         
                # Submeter a tarefa de processamento ao executor
                futures.append(executor.submit(processar_arquivo, arquivo, contador, output_dir)) 
                shutil.copy(arquivo, output_dir)
                contador += 1           

            # Esperar por todas as tarefas serem concluídas
            for future in concurrent.futures.as_completed(futures):
                # Opcional: acessar o resultado ou tratar erros
                try:
                    resultado = future.result()
                except Exception as e:
                    print(f"Erro ao processar o arquivo: {e}")