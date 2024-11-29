import base64
import logging
import requests
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import config
import time
import pandas as pd
import os

# Configuração básica do logging
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


def recuperar_documentos_processo(num_processo):
    try:
        metadados_processo = recuperar_processo_metadados_por_numero(num_processo)
        if metadados_processo:
            processo_id = metadados_processo[0]['id']
            documentos = recuperarPorProcessoId(processo_id)
            if documentos:
                logging.info(f"{len(documentos)} documentos encontrados para o processo {num_processo}.")
                return documentos, processo_id
        else:
            logging.warning(f"Metadados não encontrados para o processo {num_processo}.")
            return None, None
    except Exception as e:
        logging.error(f"Erro ao recuperar documentos do processo {num_processo}: {e}")
        return None, None


def salvar_conteudo_em_arquivo(conteudo, output_path):
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open('w', encoding='utf-8') as f:
            f.write(conteudo)
        logging.info(f"Conteúdo salvo em {output_path}.")
    except Exception as e:
        logging.exception(f"Erro ao salvar o conteúdo do processo no arquivo {output_path}")


def processar_tipo_documento(num_processo, output_dir, documento, processo_id, status):
    try:
        tipo_dir = documento['nome'].replace('.html', '').replace(' ', '_')
        output_path = Path(output_dir) / status / tipo_dir / f"{documento['id']}_{num_processo}.txt"

        # Evitar sobrescrever arquivos existentes
        counter = 1
        while output_path.exists():
            output_path = output_path.with_name(f"{output_path.stem}_{counter}.txt")
            counter += 1

        conteudo = recuperarTextoPorId(processo_id, documento['id'])
        if conteudo:
            salvar_conteudo_em_arquivo(conteudo, output_path)
    except Exception as e:
        logging.error(f"Erro ao processar o documento {documento['id']} do processo {num_processo}: {e}")


def processar_arquivo(arquivo, output_dir, max_workers=4):
    logging.info(f'Processando arquivo: {arquivo.name}')
    df = pd.read_csv(arquivo, encoding='utf-8', sep=';')

    try:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            for _, row in df.iterrows():
                num_processo = row['NR_PROCESSO']
                status = row['NM_TIPO'].upper()
                documentos, processo_id = recuperar_documentos_processo(num_processo)

                if documentos:
                    for documento in documentos:
                        futures.append(executor.submit(
                            processar_tipo_documento, num_processo, output_dir, documento, processo_id, status))

            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    logging.error(f"Erro durante o processamento: {e}")
    except Exception as e:
        logging.exception(f"Erro ao processar o arquivo {arquivo.name}")


if __name__ == '__main__':
    # max_workers = min(32, os.cpu_count() * 5)
    max_workers = 10

    nome_arquivo = Path('processos_pareceres.csv')
    output_base_dir = Path('datasets/dataset_extraido')
    output_base_dir.mkdir(parents=True, exist_ok=True)

    processar_arquivo(nome_arquivo, output_base_dir, max_workers=max_workers)
