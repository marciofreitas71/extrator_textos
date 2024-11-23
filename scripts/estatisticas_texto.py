import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np


pasta = Path('/mnt/D/projetos/ia_projetos/CLS_PCE_SENTENCAS/artefatos_sinapses/DATASET/OUTROS/')

textos = []
tokens_por_texto = []

for arquivo in pasta.glob('*.txt'):
    with arquivo.open('r', encoding='utf-8') as f:
        conteudo = f.read() 
        tokens_texto = conteudo.split()
        textos.append(tokens_texto)
        tokens_por_texto.append(len(tokens_texto))
      
soma_tokens = 0
for texto in textos:
    soma_tokens += len(texto)
    


print('Quantidade total de tokens')
print(soma_tokens)

print('Quantidade total de textos')
total_textos = len(textos)
print(total_textos)

print('Média de tamanho dos textos')
media_tokens = soma_tokens / total_textos
print(media_tokens)

# layout
fig, ax = plt.subplots(figsize = (10,10))

# plot
ax.hist(tokens_por_texto, bins=50, edgecolor= 'black')

plt.show()




