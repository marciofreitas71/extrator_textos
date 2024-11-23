import os
from pathlib import Path
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd
import requests
import time
from functools import lru_cache

# Configuração do logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Retry configurável
MAX_RETRIES = 5
RETRY_DELAY = 2

# Cache simples para evitar chamadas redundantes
@lru_cache(maxsize=None)
def fetch_with_retry(url, headers, retries=MAX_RETRIES):
    delay = RETRY_DELAY
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            if attempt < retries - 1:
                logging.warning(f"Retrying... Attempt {attempt + 1}/{retries}, URL: {url}")
                time.sleep(delay)
                delay *= 2  # Incremental delay
            else:
                logging.error(f"Failed to fetch {url} after {retries} attempts: {e}")
                return None

def retrieve_metadata(num_processo, headers):
    url = f"https://codex-backend.ia.pje.jus.br/rest/processo/recuperarPorNumero/{num_processo}"
    response = fetch_with_retry(url, headers)
    return response.json() if response else None

def retrieve_documents(processo_id, headers):
    url = f"https://codex-backend.ia.pje.jus.br/rest/processoDocumento/recuperarPorProcessoId/{processo_id}"
    response = fetch_with_retry(url, headers)
    return response.json() if response else None

def retrieve_text(processo_id, documento_id, headers):
    url = f"https://codex-backend.ia.pje.jus.br/rest/processoDocumento/recuperarTextoPorId/{processo_id}/{documento_id}"
    response = fetch_with_retry(url, headers)
    return response.text if response else None

def process_document(num_processo, tipo_documento, output_dir, headers):
    try:
        metadata = retrieve_metadata(num_processo, headers)
        if not metadata:
            return None

        processo_id = metadata[0]['id']
        documents = retrieve_documents(processo_id, headers)
        if not documents:
            return None

        for doc in documents:
            if doc['nome'] == tipo_documento:
                text = retrieve_text(processo_id, doc['id'], headers)
                if text and len(text.strip()) > 150:
                    save_content_to_file(text, output_dir / f"{num_processo}_{tipo_documento}.txt")
                break
    except Exception as e:
        logging.error(f"Error processing document for process {num_processo}: {e}")

def save_content_to_file(content, file_path):
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with file_path.open('w', encoding='utf-8') as f:
        f.write(content)
    logging.info(f"Content saved to {file_path}")

def process_file(input_file, output_dir, document_types, headers, max_workers=4):
    df = pd.read_csv(input_file, encoding='utf-8', sep=';')
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for _, row in df.iterrows():
            num_processo = row['NR_PROCESSO']
            for doc_type in document_types:
                futures.append(executor.submit(process_document, num_processo, doc_type, output_dir, headers))
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                logging.error(f"Error during document processing: {e}")

# Exemplo de uso
if __name__ == "__main__":
    HEADERS = {'accept': 'application/json', 'Authorization': 'your_token_here'}
    INPUT_FILE = Path('D:\projetos\ia_projetos\CLS_ANALISE_PRESTACAO_CONTAS/processos_pareceres.csv')
    OUTPUT_DIR = Path('D:\projetos\ia_projetos\CLS_ANALISE_PRESTACAO_CONTAS/dataset_extraido')
    DOCUMENT_TYPES = ['Cota Ministerial.html', 'Manifestacao.html']

    process_file(INPUT_FILE, OUTPUT_DIR, DOCUMENT_TYPES, HEADERS, max_workers=8)
