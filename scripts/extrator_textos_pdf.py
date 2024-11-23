import os
from pathlib import Path
from PyPDF2 import PdfReader
import pandas as pd

# Defina o caminho da pasta base
base_path = Path('D:\\Users\\059405720540\\Desktop\\Dataset')

# Itera sobre todas as pastas e subpastas
for folder in base_path.rglob('*'):
    if folder.is_dir():
        # Lista todos os arquivos .pdf na pasta atual
        pdf_files = list(folder.glob('*.pdf'))
        
        # Lista para armazenar os dados
        data = []

        for pdf_file in pdf_files:
            print(f'Processando: {pdf_file}')
            
            with open(pdf_file, 'rb') as file:
                reader = PdfReader(file)
                text = ''
                
                for page_num in range(len(reader.pages)):
                    page = reader.pages[page_num]
                    text += page.extract_text()

            # Adiciona os dados à lista
            data.append({
                'nome_arquivo': pdf_file.name,
                'texto': text
            })

        # Se houver PDFs na pasta, crie o arquivo .xls
        if data:
            df = pd.DataFrame(data)
            # Usa o nome da pasta para nomear o arquivo .xls
            output_file = folder / f'{folder.name}.xls'
            df.to_excel(output_file, index=False)
            print(f'Arquivo salvo: {output_file}')
