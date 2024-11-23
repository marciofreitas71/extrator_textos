from concurrent.futures import ThreadPoolExecutor

# Criando um ThreadPoolExecutor com 5 threads
executor = ThreadPoolExecutor(max_workers=5)

# Acessando o número de workers
num_workers = executor._max_workers
print(f"Número de workers: {num_workers}")
