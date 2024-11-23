# Projeto de Recuperação de Documentos Jurídicos
Este projeto tem como objetivo recuperar e processar documentos de processos jurídicos a partir de dados fornecidos em arquivos CSV. Utilizando APIs, o sistema coleta metadados, documentos e textos relacionados a processos judiciais específicos.

### Estrutura do Projeto
- main.py: Script principal que gerencia a execução das tarefas, incluindo a leitura de arquivos CSV, recuperação de documentos e processamento paralelo usando threads.
- swager_codex.py: Módulo responsável por interagir com a API Codex para recuperar documentos e textos associados a processos.

### Pré-requisitos
Python 3.x
Bibliotecas Python: requests, pandas, logging, threading
Arquivos de configuração (não inclusos neste repositório):
config.py: Deve conter as chaves de autorização e outras configurações necessárias para acessar as APIs.
Instalação
Clone o repositório:

bash
Copiar código
git clone https://github.com/seu-usuario/projeto-recuperacao-documentos.git
Navegue até o diretório do projeto:

bash
Copiar código
cd projeto-recuperacao-documentos
Instale as dependências necessárias:

bash
Copiar código
pip install -r requirements.txt
Configure o arquivo config.py com suas chaves de acesso e outras configurações.

Uso
Para executar o projeto, use o seguinte comando:

bash
Copiar código
python main.py
O script principal (main.py) realiza as seguintes tarefas:

Leitura de Arquivos CSV: Lê todos os arquivos CSV no diretório especificado, contendo informações de processos.
Processamento Paralelo: Cria uma thread para cada arquivo CSV para processar os dados em paralelo.
Recuperação de Documentos: Para cada linha dos arquivos CSV, recupera os documentos e textos associados ao processo utilizando as APIs.
Armazenamento de Resultados: Salva os textos recuperados em arquivos de texto organizados em pastas correspondentes aos nomes dos arquivos CSV.
Estrutura de Pastas
W:\\RESTRITA\\Janus\\dataset_2024\\TRE-BA: Diretório de entrada contendo os arquivos CSV.
Dentro do diretório de entrada, para cada arquivo CSV, uma pasta é criada para armazenar os resultados processados.
Configuração de Logging
O projeto utiliza a biblioteca logging para registrar informações, avisos e erros durante a execução. O nível de logging está configurado para INFO, mas pode ser ajustado conforme necessário.

Contribuição
Contribuições são bem-vindas! Sinta-se à vontade para abrir issues e pull requests.

Licença
Este projeto está licenciado sob a licença MIT. Consulte o arquivo LICENSE para obter mais informações.

Contato
Para mais informações ou dúvidas, entre em contato com seu-email@example.com.