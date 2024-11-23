import bd_pje_extrator as sj
import codex_extrator as sc
import os
import pandas as pd
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configuração do logging para registrar mensagens de log com nível INFO
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def texto_valido(texto: str):
    """
    Verifica se um texto é válido.

    Args:
        texto (str): O texto a ser verificado.

    Returns:
        bool: True se o texto for válido, False caso contrário.
    """
    return 'Promot' in texto

def processar_arquivo(arquivo, caminho):
    """
    Processa um arquivo CSV para recuperar conteúdos de processos judiciais e salvá-los em arquivos de texto.

    Args:
        arquivo (str): O nome do arquivo CSV a ser processado.
        caminho (str): O caminho do diretório onde o arquivo CSV está localizado.
    """
    total_processados = 0
    textos_recuperados = 0
    textos_nao_recuperados = 0
    
    pasta = os.path.splitext(arquivo)[0]
    pasta_caminho = os.path.join(caminho, 'parecer', pasta)

    if not os.path.exists(pasta_caminho):
        os.makedirs(pasta_caminho)
        logging.info(f'Pasta criada: {pasta_caminho}')
    
    df = pd.read_csv(os.path.join(caminho, arquivo))

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = []
        for _, row in df.iterrows():
            num_processo = row['Processo']
            futures.append(executor.submit(processar_processo, num_processo, pasta_caminho))

        for future in as_completed(futures):
            try:
                futuro = future.result()
                if futuro['recuperado']:
                    textos_recuperados += 1
                else:
                    textos_nao_recuperados += 1
            except Exception as e:
                logging.error(f'Erro durante o processamento: {e}')

    logging.info(f'Total de processos: {total_processados}')
    logging.info(f'Textos recuperados: {textos_recuperados}')
    logging.info(f'Textos não recuperados: {textos_nao_recuperados}')

def processar_processo(num_processo, pasta_caminho):
    """
    Processa um único processo, tentando recuperar e salvar os textos correspondentes.

    Args:
        num_processo (str): O número do processo a ser processado.
        pasta_caminho (str): O caminho da pasta onde os arquivos de texto serão salvos.
    """
    for tipo_documento in ['MANIFESTACAO', 'MANIFESTACAO_MPE_1G', 'PARECER', 'PARECER_PROCURADORIA_1G', 'COTA_MINISTERIAL', 'SENTENCA', "Parecer cn"]:
        texto = sc.recupera_conteudo_processo(num_processo, tipo_documento)
        if texto and texto_valido(texto):
            arquivo_texto = os.path.join(pasta_caminho, f'{num_processo}_{tipo_documento}.txt')
            if not os.path.exists(arquivo_texto):
                with open(arquivo_texto, 'w', encoding='utf-8') as f:
                    f.write(texto)
                logging.info(f'Arquivo salvo: {arquivo_texto}')
                return {'recuperado': True}
            else:
                logging.info(f'Arquivo já existe: {arquivo_texto}')
                return {'recuperado': True}

    logging.warning(f'Conteúdo não recuperado para Processo: {num_processo}')
    return {'recuperado': False}

if __name__ == '__main__':
    caminho = "D:\\datasets\\DATASET_16-08-2024"
    
    try:
        arquivos = [arquivo for arquivo in os.listdir(caminho) if arquivo.endswith('.csv')]

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            for arquivo in arquivos:
                futures.append(executor.submit(processar_arquivo, arquivo, caminho))

            for future in as_completed(futures):
                future.result()

        logging.info("Processamento concluído.")
    except Exception as e:
        logging.error(f'Erro: {e}')
