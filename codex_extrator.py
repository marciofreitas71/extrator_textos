import base64
import logging
import requests
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import config
import time
import utils.utils as utils
import pandas as pd
import os

# Configuração básica do logging para registrar informações importantes
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def recuperar_processo_metadados_por_numero(num_processo):
    url = f'https://codex-backend.ia.pje.jus.br/rest/processo/recuperarPorNumero/{num_processo}'
    headers = {'accept': 'application/json', 'Authorization': config.chave}
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            logging.info(f"Metadados do processo {num_processo} recuperados com sucesso.")
            return response.json()
        else:
            logging.warning(f"Metadados do processo {num_processo} não foram recuperados. Status: {response.status_code}")
            return None
    except Exception as e:
        logging.error(f"Erro ao recuperar os metadados do processo nº {num_processo}: {e}")
        return None

def recuperarPorProcessoId(processoID):
    url = f'https://codex-backend.ia.pje.jus.br/rest/processoDocumento/recuperarPorProcessoId/{processoID}'
    headers = {'accept': 'application/json', 'Authorization': config.chave}

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            logging.info(f"Lista de documentos recuperados para o processo de ID {processoID}.")
            return response.json()
        else:
            logging.warning(f"Não foi possível recuperar documentos para o processo de ID {processoID}. Status: {response.status_code}")
            return None
    except Exception as e:
        logging.error(f"Erro ao recuperar lista de documentos para o processo com ID {processoID}: {e}")
        return None

def recuperarTextoPorId(id_processo, id_documento):
    url = f'https://codex-backend.ia.pje.jus.br/rest/processoDocumento/recuperarTextoPorId/{id_processo}/{id_documento}'
    headers = {'accept': 'text/plain', 'Authorization': config.chave}

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            logging.info(f'Texto do documento {id_documento} recuperado com sucesso')
            return response.text
        else:
            logging.warning(f"Falha ao recuperar texto para o documento {id_documento} do processo {id_processo}. Status: {response.status_code}")
            return None
    except Exception as e:
        logging.error(f"Erro ao recuperar o texto do documento {id_documento} do processo {id_processo}: {e}")
        return None

def recupera_conteudo_processo(num_processo, tipo_documento):
    try:
        metadados_processo = recuperar_processo_metadados_por_numero(num_processo)
        if metadados_processo:
            processo_id = metadados_processo[0]['id']
            documentos = recuperarPorProcessoId(processo_id)
            if documentos:
                for documento in documentos:
                    if tipo_documento == documento['nome']:
                        logging.info(f"Documento {tipo_documento} encontrado para o processo {num_processo}.")
                        texto = recuperarTextoPorId(processo_id, documento['id'])
                        if texto:
                            if len(texto.replace(' ', '')) > 150:
                                texto = recuperarTextoPorId(processo_id, documento['id'])
                            else:
                                texto = recuperarTextoPorId(processo_id, documento['id'] + 1)
                                logging.info(f"Documento {documento['id']} é muito pequeno. Tentando documento {documento['id'] + 1}")
                        return texto

        else:
            logging.error(f"Metadados não encontrados para o processo {num_processo}.")
            return None
    except Exception as e:
        logging.error(f"Ocorreu um erro ao processar o processo nº {num_processo}: {e}")
        return None

def salvar_conteudo_em_arquivo(conteudo, output_path):
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open('w', encoding='utf-8') as f:
            f.write(conteudo)
        logging.info(f"Conteúdo salvo em {output_path}.")
    except Exception as e:
        logging.exception(f"Erro ao salvar o conteúdo do processo no arquivo {output_path}")

def processar_tipo_documento(num_processo, output_dir, nome_arquivo, status, tipo_documento, tipos_documento):
    output_path = None  # Inicialize como None para detectar casos não tratados

    try:
        tipo_dir = tipo_documento.replace('.html', '')
        logging.info(f"Processando o(a) {tipo_documento} para o processo {num_processo}.")
        str_documento = tipo_documento.replace(' ', '_').replace('.html', '')
        
        # Define o caminho base para o arquivo, sem o número no final
        # base_output_path = Path(output_dir) / tipo_dir / status / f'{str_documento.lower()}_{num_processo}'
        base_output_path = Path(output_dir) /  status  / tipo_dir / f'{str_documento.lower()}_{num_processo}'
        
        # Verifica se o arquivo já existe e ajusta o nome com um número ao final se necessário
        counter = 1
        output_path = base_output_path.with_suffix('.txt')
        
        # Loop para evitar sobreposição de nomes de arquivos
        while output_path.exists():
            output_path = base_output_path.with_name(f"{base_output_path.stem}_{counter}").with_suffix('.txt')
            counter += 1
    except Exception as e:
        logging.error(f"Tipo de documento {tipo_documento} não reconhecido para o processo {num_processo}: {e}")
        return  # Pula este tipo de documento

    retries = 5
    delay = 1
    for attempt in range(retries):
        try:
            conteudo = recupera_conteudo_processo(num_processo, tipo_documento)
            if conteudo:
                salvar_conteudo_em_arquivo(conteudo, output_path)
            break
        except requests.exceptions.RequestException as e:
            logging.error(f"Erro ao processar {num_processo}: {e}. Tentativa {attempt+1} de {retries}.")
            time.sleep(delay)
            delay *= 2

def processar_arquivo(arquivo, tipos_documento, output_dir, max_workers=4):
    
    num_cpus = os.cpu_count()
    max_workers = min(32, num_cpus * 5) 
    
    nome_arquivo = arquivo.stem
    logging.info(f'Processando arquivo: {arquivo.name}')

    df = pd.read_csv(arquivo, encoding='utf-8')       

    try:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            for _, row in df.iterrows():
                num_processo = utils.formata_num_processo(row['NR_PROCESSO'])
                status = row['NM_TIPO'].upper()
                for tipo_documento in tipos_documento:
                    futures.append(executor.submit(
                        processar_tipo_documento, num_processo, output_dir, nome_arquivo, status, tipo_documento, tipos_documento))
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    logging.error(f'Erro durante o processamento: {e}')
    except Exception as e:
        logging.exception(f'Erro ao processar o arquivo {arquivo.name}')

if __name__ == '__main__':

    num_cpus = os.cpu_count()
    max_workers = min(32, num_cpus * 5)
    
    DOCS_MP = ['Cota Ministerial.html', 'Manifestacao.html', 'Parecer.html', 'Parecer da Procuradoria.html']
    DOCS_SERVIDOR = ['Parecer conclusivo.html', 'Parecer.html']
    DOCS_JUIZ = ['Sentença.html', 'Decisão.html', 'Acórdão.html']
        
    tipos_documento = DOCS_SERVIDOR + DOCS_MP

    nome_arquivo = Path('D:\projetos\ia_projetos\CLS_ANALISE_PRESTACAO_CONTAS/processos_pareceres.csv')
    output_base_dir = Path('D:\projetos\ia_projetos\CLS_ANALISE_PRESTACAO_CONTAS/dataset_extraido')
    output_base_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(nome_arquivo, encoding='utf-8', sep=';')

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for _, row in df.iterrows():
            num_processo = row['NR_PROCESSO']
            status = row['NM_TIPO'].upper()
            for tipo_documento in tipos_documento:
                futures.append(executor.submit(
                    processar_tipo_documento, num_processo, output_base_dir, nome_arquivo, status, tipo_documento, tipos_documento))
        for future in as_completed(futures):
            future.result()
