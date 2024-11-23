import psycopg2
import socket
import logging

# Configuração do logging para registrar mensagens de erro
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Função para verificar se o servidor está acessível
def verificar_conectividade(host, port, timeout=5):
    """
    Verifica se o host e a porta estão acessíveis via socket.

    Args:
        host (str): O endereço do servidor do banco de dados.
        port (int): A porta que o banco de dados está ouvindo.
        timeout (int): Tempo limite para a tentativa de conexão.

    Returns:
        bool: True se a conexão foi bem-sucedida, False caso contrário.
    """
    try:
        # Tentativa de conectar ao host e porta
        socket.create_connection((host, port), timeout)
        logging.info(f"Conectividade com {host}:{port} OK")
        return True
    except socket.error as e:
        logging.error(f"Erro de conectividade com {host}:{port} - {e}")
        return False

# Função para verificar a conexão com o banco de dados
def verificar_conexao_banco(db_name, user, password, host, port):
    """
    Tenta se conectar ao banco de dados e captura possíveis erros.

    Args:
        db_name (str): O nome do banco de dados.
        user (str): O nome do usuário do banco de dados.
        password (str): A senha do banco de dados.
        host (str): O endereço do servidor do banco de dados.
        port (int): A porta do banco de dados.

    Returns:
        bool: True se a conexão foi bem-sucedida, False caso contrário.
    """
    try:
        # Tenta criar uma conexão com o banco de dados sem SSL
        connection = psycopg2.connect(
            dbname=db_name,
            user=user,
            password=password,
            host=host,
            port=port,
            sslmode='disable'
        )
        logging.info("Conexão com o banco de dados bem-sucedida!")
        connection.close()
        return True
    except psycopg2.OperationalError as e:
        logging.error(f"Erro ao conectar ao banco de dados: {e}")
        return False
    except Exception as e:
        logging.error(f"Erro inesperado: {e}")
        return False

# Configurações de exemplo para a conexão com o banco de dados
db_config = {
    'db_name': 'pje',
    'user': 'msfreitas_tre-ba',
    'password': 'mar5041cio',
    'host': '192.168.220.250',  # endereço do servidor de banco de dados
    'port': 7105  # porta padrão para PostgreSQL
}

if __name__ == "__main__":
    # Verificar conectividade de rede
    if verificar_conectividade(db_config['host'], db_config['port']):
        # Verificar conexão com o banco de dados
        verificar_conexao_banco(
            db_config['db_name'], 
            db_config['user'], 
            db_config['password'], 
            db_config['host'], 
            db_config['port']
        )