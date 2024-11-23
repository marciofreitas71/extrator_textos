def formata_num_processo(num_original, formatado='f'):
    '''
    Converte um número de processo sem pontuação para o
    formato padrão, com pontos e hifens.
    args:
        num_processo (str): O número do processo sem pontuação.
    returns:
        str: O número do processo formatado.
    '''
    
    if formatado == 'f':

        # Verifica se o número do processo é string

        if isinstance(num_original, str):
            str_inicial = "0" + num_original[:-13] + "0"
        else:
            num_original = str(num_original)
            str_inicial = "0" + num_original[:-13]    
        
        num_formatado = str_inicial + "-"
        num_formatado = num_formatado + num_original[-13:-11]
        num_formatado = num_formatado + "."
        num_formatado = num_formatado + num_original[-11:-7]
        num_formatado = num_formatado + "."
        num_formatado = num_formatado + num_original[-7]
        num_formatado = num_formatado + "."
        num_formatado = num_formatado + num_original[-6:-4]
        num_formatado = num_formatado + "."
        num_formatado = num_formatado + num_original[-4:]



        return num_formatado

    else:
        return num_original
            
        
        
        

if __name__ == "__main__":
    num_original = "6001804720206050121"
    print(formata_num_processo(num_original))