import pandas as pd
from pathlib import Path
import re

# Carregar o arquivo CSV contendo os trechos e as palavras substitutas
df = pd.read_csv('/mnt/D/projetos/ia_projetos/CLS_PCE_SENTENCAS/artefatos_sinapses/DATASET/OUTROS/frases_chave.csv', sep='@', encoding='utf-8')

# Definir o caminho onde os arquivos de texto estão localizados
path = Path('/mnt/D/projetos/ia_projetos/CLS_PCE_SENTENCAS/artefatos_sinapses/DATASET/OUTROS')

# Pasta onde os arquivos modificados serão armazenados
output_dir = path / "arquivos_modificados"
output_dir.mkdir(parents=True, exist_ok=True)

# Para cada linha do DataFrame (cada trecho a ser substituído)
for _, row in df.iterrows():
    trecho = row['original']
    substituto = row['substituto']
    
    # Iterar sobre os arquivos de texto, incluindo os que foram previamente modificados
    for arquivo in path.glob('*.txt'):
        print(f'Procurando trecho no arquivo {arquivo}')

        with arquivo.open('r', encoding='utf-8') as file:
            texto = file.read()

        # Inicializar o texto modificado com o conteúdo original
        texto_modificado = texto

        # Usar regex para buscar o trecho no texto
        if re.search(re.escape(trecho), texto):
            # Se o trecho for encontrado, substituí-lo pelo substituto
            texto_modificado = re.sub(re.escape(trecho), substituto, texto)
            
            # Gerar o novo nome do arquivo precedido de 'iter_' e um contador de substituições
            novo_nome_arquivo = f"{arquivo.stem}_modificado.txt"
            novo_caminho_arquivo = output_dir / novo_nome_arquivo

            # Salvar o novo texto no arquivo com o novo nome
            with novo_caminho_arquivo.open('w', encoding='utf-8') as novo_arquivo:
                novo_arquivo.write(texto_modificado)

            print(f"Novo texto gerado e salvo em: {novo_caminho_arquivo}")
            
            # Atualizar o caminho de origem do arquivo para o modificado
            path = output_dir

print("Processo concluído.")
