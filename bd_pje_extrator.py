import base64
import logging
import requests
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configuração básica do logging para registrar informações importantes
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def recuperar_por_Classe_Tarefa(grau, codigoClasse, anoExercicio, tarefa, UF):
    """
    Recupera um processo pelo número.

    Args:
        grau (int): O grau do processo (1G, 2G, etc.).
        numero (str): O número do processo no formato string.

    Returns:
        dict: Um dicionário contendo os detalhes do processo, ou None se houver um erro.

    Levanta:
        Exception: Captura e registra exceções que podem ocorrer durante a requisição.
    """
    url = f'http://10.5.132.133:8084/janus/processos/recuperarPorClasseTarefa/{grau}/{codigoClasse}?anoExercicio={anoExercicio}&tarefa={tarefa}&UF={UF}'
    

    headers = {'accept': 'application/json'}
    
    try:
        response = requests.post(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            logging.error(f"Resposta com status {response.status_code}.")
            return None
    except Exception as e:
        return None

def recuperarPorNumero(grau, numero):
    """
    Recupera um processo pelo número.

    Args:
        grau (int): O grau do processo (1G, 2G, etc.).
        numero (str): O número do processo no formato string.

    Returns:
        dict: Um dicionário contendo os detalhes do processo, ou None se houver um erro.

    Levanta:
        Exception: Captura e registra exceções que podem ocorrer durante a requisição.
    """
    url = f'http://10.5.132.133:8084/janus/processos/recuperarPorNumero/{grau}/{numero}'
    headers = {'accept': 'application/json'}
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            logging.info(f"Processo {numero} recuperado com sucesso.")
            return response.json()
        else:
            logging.error(f"Resposta com status {response.status_code}.")
            return None
    except Exception as e:
        logging.error(f"Erro ao recuperar o processo nº {numero}: {e}")
        return None

def recuperarPorGrauId(grau, idProcesso, tipoDocumento):
    """
    Recupera as peças processuais de um processo pelo ID e tipo de documento.

    Args:
        grau (int): O grau do processo.
        idProcesso (int): O ID único do processo.
        tipoDocumento (str): O tipo de documento que deseja recuperar (ex.: SENTENCA, PARECER).

    Returns:
        dict: Um dicionário contendo as peças processuais, ou None se houver um erro.

    Levanta:
        Exception: Captura e registra exceções que podem ocorrer durante a requisição.
    """
    url = f'http://10.5.132.133:8084/janus/processos/recuperarPecasProcessuais?grau={grau}&idProcesso={idProcesso}&tipoDocumento={tipoDocumento}'
    headers = {'accept': 'application/json'}
    
    try:
        response = requests.post(url, headers=headers)
        if response.status_code == 200:
            logging.info(f"Processo recuperado com sucesso pelo id {idProcesso}.")
            return response.json()
        else:
            logging.error(f"Resposta com status {response.status_code} no id {idProcesso}.")
            return None
    except Exception as e:
        logging.error(f"Erro ao recuperar o processo pelo id nº {idProcesso}: {e}")
        return None

def recupera_conteudo_processo(grau, numero, tipoDocumento):
    """
    Recupera o conteúdo do processo para um dado tipo de documento.

    Args:
        grau (int): O grau do processo (1G, 2G, etc.).
        numero (str): O número do processo.
        tipoDocumento (str): O tipo de documento que deseja recuperar.

    Returns:
        str: O conteúdo decodificado do processo em formato string, ou None se houver um erro.

    Levanta:
        Exception: Captura e registra exceções durante o processamento do conteúdo.
    """
    try:
        # Recuperar o processo pelo número
        processo = recuperarPorNumero(grau, numero)
        if processo:
            # Extrair o ID do processo para realizar a próxima requisição
            idProcesso = processo.get('idProcesso')
            resposta = recuperarPorGrauId(grau, idProcesso, tipoDocumento)
            if resposta and resposta[0].get('conteudo'):
                conteudo_resposta = resposta[0]['conteudo']
                try:
                    # Tentar decodificar com utf-8
                    conteudo_resposta = base64.b64decode(conteudo_resposta).decode('utf-8')
                except UnicodeDecodeError:
                    logging.warning(f"Falha ao decodificar em UTF-8 para o processo nº {numero}. Tentando latin-1.")
                    try:
                        # Tentar decodificar com latin-1
                        conteudo_resposta = base64.b64decode(conteudo_resposta).decode('latin-1')
                    except UnicodeDecodeError:
                        logging.error(f"Falha ao decodificar o conteúdo do processo nº {numero} com latin-1 também.")
                        return None

                logging.info(f"Conteúdo recuperado para o processo nº {numero}.")
                return conteudo_resposta
            else:
                logging.error(f"Erro ao recuperar o conteúdo do processo nº {numero} para o documento {tipoDocumento}.")
                return None
        else:
            logging.error(f"Erro ao recuperar o processo nº {numero}.")
            return None
    except Exception as e:
        logging.error(f"Ocorreu um erro ao processar o processo nº {numero}: {e}")
        return None

def salvar_conteudo_em_arquivo(conteudo, output_path):
    """
    Salva o conteúdo recuperado em um arquivo de texto.

    Args:
        conteudo (str): O conteúdo a ser salvo.
        output_path (Path): O caminho completo onde o arquivo será salvo.

    Levanta:
        Exception: Captura e registra exceções durante a criação do diretório ou gravação do arquivo.
    """
    try:
        # Criar diretórios se necessário
        output_path.parent.mkdir(parents=True, exist_ok=True)
        # Salvar o conteúdo em UTF-8
        with output_path.open('w', encoding='utf-8') as f:
            f.write(conteudo)
        logging.info(f"Conteúdo salvo em {output_path}.")
    except Exception as e:
        logging.error(f"Erro ao salvar o conteúdo do processo no arquivo {output_path}: {e}")

def processar_tipo_documento(grau, numProcesso, tipo, output_dir, nome_arquivo):
    """
    Processa um tipo de documento para um determinado processo, recupera o conteúdo e o salva.

    Args:
        grau (int): O grau do processo (1G, 2G, etc.).
        numProcesso (str): O número do processo a ser recuperado.
        tipo (str): O tipo de documento a ser recuperado (ex.: SENTENCA, PARECER).
        output_dir (str): O diretório base onde o conteúdo será salvo.
        nome_arquivo (str): O nome base do arquivo CSV sendo processado.

    Levanta:
        Exception: Captura e registra exceções durante a recuperação e salvamento do conteúdo.
    """
    # Definir o diretório correto (SENTENCA ou PARECER)
    if tipo == 'SENTENCA':
        tipo_dir = 'SENTENCA'
    else:
        tipo_dir = 'PARECER'
    
    # Definir o caminho completo do arquivo de saída
    output_path = Path(output_dir) / tipo_dir / nome_arquivo / f'{numProcesso}.txt'
    
    # Verificar se o arquivo já existe, e pular o processamento se existir
    if output_path.exists():
        logging.info(f"Arquivo {output_path} já existe. Pulando processamento.")
        return
    
    # Recuperar o conteúdo do processo para o tipo de documento especificado
    conteudo = recupera_conteudo_processo(grau, numProcesso, tipo)
    if conteudo:
        # Salvar o conteúdo em arquivo se a recuperação foi bem-sucedida
        salvar_conteudo_em_arquivo(conteudo, output_path)

def processar_arquivo(arquivo, tipos_parecer, output_dir, max_workers=10):
    """
    Processa um arquivo CSV contendo uma lista de números de processos e recupera seus conteúdos.

    Args:
        arquivo (Path): O caminho do arquivo CSV a ser processado.
        tipos_parecer (list): A lista de tipos de pareceres a serem recuperados.
        output_dir (str): O diretório base onde os conteúdos recuperados serão salvos.
        max_workers (int): O número máximo de threads a serem usadas para o processamento paralelo.

    Levanta:
        Exception: Captura e registra exceções durante o processamento do arquivo.
    """
    nome_arquivo = arquivo.stem  # Nome base do arquivo sem extensão
    logging.info(f'Processando arquivo: {arquivo.name}')

    try:
        with arquivo.open('r', encoding='utf-8') as file:
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = []
                for linha in file:
                    numProcesso = linha.strip()  # Remover espaços em branco da linha
                    for tipo in tipos_parecer:
                        # Criar uma tarefa para cada tipo de parecer
                        futures.append(executor.submit(
                            processar_tipo_documento, 1, numProcesso, tipo, output_dir, nome_arquivo))
                
                # Aguardar que todas as tarefas terminem antes de processar a próxima linha
                for future in as_completed(futures):
                    try:
                        future.result()  # Verificar exceções nas threads
                    except Exception as e:
                        logging.error(f'Erro durante o processamento: {e}')
    except Exception as e:
        logging.error(f'Erro ao processar o arquivo {arquivo.name}: {e}')

if __name__ == '__main__':
    
    """
    Ponto de entrada principal do script.

    Configura os tipos de documentos a serem recuperados, define o diretório base e inicia
    o processamento de todos os arquivos CSV encontrados no diretório especificado.
    """
    # Lista dos tipos de pareceres e sentenças a serem recuperados
    tipos_documentos = ['MANIFESTACAO', 'MANIFESTACAO_MPE_1G', 'PARECER', 
                        'PARECER_PROCURADORIA_1G', 'COTA_MINISTERIAL', 'SENTENCA']
    
    # Diretório onde estão localizados os arquivos CSV com os números dos processos
    arquivos = Path("D:/datasets/DATASET_16-08-2024").glob('*.csv')
    
    # Lista para registrar processos que falharam durante o processamento
    processos_com_erro = []
    
    # Diretório base para salvar os conteúdos recuperados
    output_dir = "D:/datasets/DATASET_16-08-2024"

    # Processar cada arquivo CSV encontrado no diretório
    for arquivo in arquivos:
        if not arquivo.exists():
            logging.warning(f'O arquivo {arquivo} não existe.')
        else:
            logging.info(f'Processando o arquivo: {arquivo.name}')
            processar_arquivo(arquivo, tipos_documentos, output_dir)

    # # Testar com enumerate
    # for i, tipo in enumerate(tipos_documentos):
    #     print(tipo.upper())
    #     print(recupera_conteudo_processo(1,'0600293-09.2020.6.05.0086',tipo))


 
