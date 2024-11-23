from pathlib import Path
import re
import filecmp

diretorio = Path('D:\\datasets\\DATASET_SENTENCAS\\DEFERIDO')

# Regex para o padrão sem "sentença_"
sem_sentenca = re.compile(r'^\d{7}-\d{2}\.\d{4}\.\d{1}\.\d{2}\.\d{4}\.txt$')

# Regex para o padrão com "sentença_"
com_sentenca = re.compile(r'^sentença_\d{7}-\d{2}\.\d{4}\.\d{1}\.\d{2}\.\d{4}\.txt$')

# Obter todos os arquivos que têm "sentença_"
arquivos_com_sentenca = list(diretorio.glob('sentença_*.txt'))

# Renomear os arquivos que têm "sentença_" e excluir duplicatas
for arquivo in arquivos_com_sentenca:
    if com_sentenca.match(arquivo.name):
        novo_nome = diretorio / arquivo.name.replace('sentença_', '', 1)
        
        # Verifique se o arquivo sem "sentença_" já existe
        if novo_nome.exists():
            # Compare os arquivos, se forem iguais, remova o com o prefixo
            if filecmp.cmp(arquivo, novo_nome, shallow=False):
                print(f"Arquivo duplicado encontrado e excluído: {arquivo.name}")
                arquivo.unlink()
        else:
            # Se não existe, renomeia o arquivo
            arquivo.rename(novo_nome)
            print(f"Arquivo renomeado: {arquivo.name} para {novo_nome.name}")

# Verifique se o loop não encontrou arquivos
if not arquivos_com_sentenca:
    print("Nenhum arquivo encontrado.")
