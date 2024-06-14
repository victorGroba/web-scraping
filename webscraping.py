from bs4 import BeautifulSoup
import requests
import pandas as pd
import os
import re


output_folder = 'Output'
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

url = 'https://www.magazineluiza.com.br/busca/notebooks/?from=submit'
domain = 'https://www.magazineluiza.com.br'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    'Referer': 'https://www.google.com',  # Cabeçalhos HTTP para simular um navegador real
}

page_number = 1 # Variáveis para controle de paginação
max_pages = 17

data_melhores = []  
data_piores = []
# Loop para percorrer todas as páginas de resultados
while page_number <= max_pages:
    url_pag = f'{url}&page={page_number}'  
    site = requests.get(url_pag, headers=headers)
    soup = BeautifulSoup(site.content, 'html.parser')
    notbooks = soup.find_all('a', class_='sc-eBMEME')

    for notbook in notbooks: # Loop para extrair dados de cada notebook na página atual
        descricao = notbook.find('h2', class_='sc-fvwjDU fbccdO').get_text().strip()
        avaliacao_tag = notbook.find('span', class_='sc-epqpcT jdMYPv')

        
        if avaliacao_tag:
            avaliacao_text = avaliacao_tag.get_text().strip()
            
            
            match = re.search(r'\((\d+)\)', avaliacao_text)
            qtd_avaliacao = int(match.group(1)) if match else 0 #Se um padrão correspondente for encontrado, extraímos o número de avaliações e o convertemos em um inteiro. Caso contrário, definimos qtd_avaliacao como 0.
        else:
            qtd_avaliacao = 0

        link = notbook.get('href') # Obtém o link do notebook
        linkcompleto = f'{domain}{link}'

        # Adicionei os dados à lista apropriada com base na avaliação
        if qtd_avaliacao >= 100:
            data_melhores.append((descricao, qtd_avaliacao, linkcompleto))
        else:
            data_piores.append((descricao, qtd_avaliacao, linkcompleto))

    print(f"Página {page_number} de {max_pages} processada.")
    page_number += 1

# Converte os dados para DataFrames do Pandas
df_melhores = pd.DataFrame(data_melhores, columns=['PRODUTO', 'QTD_AVAL', 'URL'])
df_piores = pd.DataFrame(data_piores, columns=['PRODUTO', 'QTD_AVAL', 'URL'])

# Defini o caminho completo para o arquivo Excel e o nome do arquivo
excel_file_path = os.path.join(output_folder, 'Notebooks.xlsx')

# Salvei os DataFrames em um arquivo Excel com diferentes abas
with pd.ExcelWriter(excel_file_path) as writer:
    df_melhores.to_excel(writer, sheet_name='Melhores', index=False)
    df_piores.to_excel(writer, sheet_name='Piores', index=False)

print(f'Arquivo Excel salvo em: {excel_file_path}')
