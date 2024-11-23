import psycopg2
from psycopg2 import OperationalError

def create_connection(db_name, db_user, db_password, db_host, db_port):
    try:
        connection = psycopg2.connect(
            database=db_name,
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port,
        )
        print("Conexão ao banco de dados PostgreSQL bem-sucedida!")
        return connection
    except OperationalError as e:
        print(f"Erro ao conectar ao PostgreSQL: {e}")
        return None

# Configurações de conexão
db_name = "pje"
db_user = "msfreitas_tre-ba"
db_password = "mar5041cio"
db_host = "192.168.220.250"  # ou o IP do servidor
db_port = "7105"       # porta padrão do PostgreSQL

# Teste de conexão
connection = create_connection(db_name, db_user, db_password, db_host, db_port)

# Fechar conexão após o teste
if connection:
    connection.close()
