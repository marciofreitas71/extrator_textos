from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import logging

CLASSE_JUDICIAL = 'PRESTAÇÃO DE CONTAS ELEITORAIS (12193)'
MOVIMENTO_PROCESSUAL = 'Contas Aprovadas com Ressalvas (12654)'
JURISDICAO = 'SALVADOR BA'
ORGAO_JULGADOR = ''

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Configurações do ChromeDriver
chrome_options = Options()
chrome_options.add_experimental_option("detach", True)

# Use o WebDriver Manager para instalar e gerenciar o ChromeDriver
service = Service(ChromeDriverManager().install())

# Iniciar o navegador
driver = webdriver.Chrome(service=service, options=chrome_options)

# URL da página que você deseja fazer scraping
url = "https://pje1g-ba.tse.jus.br/pje/login.seam"

# Abrir a página
driver.get(url)

# Esperar alguns segundos para garantir que a página carregue completamente
wait = WebDriverWait(driver, 10)

logging.info("Navegador aberto")

# Esperar até o iframe estar presente
iframe = wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[3]/iframe")))

# Entrar no iframe
driver.switch_to.frame(iframe)

# Preencher o campo de login
input_login = wait.until(EC.presence_of_element_located((By.ID, "username")))
input_login.send_keys("50559036515")
logging.info("Usuário inserido")

# Preencher o campo de senha
input_password = wait.until(EC.presence_of_element_located((By.ID, "password")))
input_password.send_keys("Amanlena1540!")
logging.info("Senha inserida")

# Clicar no botão de login
botao_login = wait.until(EC.element_to_be_clickable((By.ID, "kc-login")))
botao_login.click()
logging.info("Botão de login clicado")

# Esperar o redirecionamento para a nova página
wait.until(EC.url_changes(url))

# Voltar para o contexto da página principal
driver.switch_to.default_content()

# Agora você pode interagir com a nova página, se necessário
try:
    # Esperar até o token estar disponível e clicar nele
    token = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="divBas"]/div[2]/div[4]/a')))
    token.click()
    logging.info("Token clicado com sucesso")
except Exception as e:
    logging.error(f"Erro ao tentar encontrar o token: {e}")

def buscar_processos(CLASSE_JUDICIAL, MOVIMENTO_PROCESSUAL, JURISDICAO, ORGAO_JULGADOR):

    # Esperar até o iframe estar presente novamente
    iframe = wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[5]/div/div/iframe")))

    # Entrar no iframe
    driver.switch_to.frame(iframe)

    # Encontrar o ícone de consulta e clicar
    icone_consulta = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/app-root/selector/div/div/div[1]/side-bar/nav/ul/li[9]')))
    logging.info("Ícone de consulta encontrado")

    icone_consulta.click()
    logging.info("Ícone de consulta clicado")

    #TODO Entrar no iframe id='ngFrame'

     # Esperar até o iframe estar presente novamente
    iframe = wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[5]/div/div/iframe")))
    # Entrar no iframe
    driver.switch_to.frame(iframe)


    iframe = wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/app-root/selector/div/div/div[2]/right-panel/div/consulta-processual/div/iframe")))
    # Entrar no iframe
    driver.switch_to.frame(iframe)

    campo_classe_judicial = driver.find_element(By.XPATH,'/html/body/div[1]/div/div/div/div[2]/form/div[1]/div/div/div[10]/div[2]/input[1]' )
    campo_classe_judicial = CLASSE_JUDICIAL

    filtro_avancado = driver.find_element(By.XPATH,'/html/body/div[2]/div/div/div/div[2]/form/div[1]/div/div/div[17]/div[2]/div/div[1]/div/div[2]')
    filtro_avancado.click()

    campo_movimento_processual = driver.find_element(By.XPATH, '/html/body/div[3]/div/div/div/div[2]/form/div[1]/div/div/div[17]/div[2]/div/div[3]/div/div[1]/div/div[2]/input[1]')
    campo_movimento_processual.send_keys(MOVIMENTO_PROCESSUAL)

    campo_orgao_julgador = driver.find_element(By.XPATH, '/html/body/div[3]/div/div/div/div[2]/form/div[1]/div/div/div[17]/div[2]/div/div[3]/div/div[5]/div/div[2]/select')
    campo_orgao_processual.send_keys(ORGAO_JULGADOR)

    time.sleep(1)





        

buscar_processos(CLASSE_JUDICIAL, MOVIMENTO_PROCESSUAL, JURISDICAO, ORGAO_JULGADOR)

