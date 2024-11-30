import os
import pandas as pd
import csv
import re

def sinapi_excel_to_csv(caminho_excel, pasta_destino):
  nome_arquivo = os.path.basename(caminho_excel)
  if 'analitico' in nome_arquivo.lower():
    sr = 5
  elif 'sintetico' in nome_arquivo.lower():
    sr = 4
  elif 'insumos' in nome_arquivo.lower():
     sr = 6

  df = pd.read_excel(caminho_excel, skiprows=sr, dtype='str')
  if 'insumos' not in nome_arquivo.lower():
    df_final = df[~df['DESCRICAO DA CLASSE'].isna()]
  else:
    df_final = df
  df_final.to_csv(f'{pasta_destino}/{nome_arquivo.split(".")[0]}.csv', index=False, sep=';', quoting=csv.QUOTE_ALL)

desoneracao = 'Desonerado'
ano = '2024'
relatorio = 'Sintetico'

caminho_pasta = "BASE"

padrao = r"SINAPI_ref_Insumos_Composicoes_PE_\d{6}_Desonerado"
padrao_insumo = r"SINAPI_Preco_Ref_Insumos_PE_\d{6}_Desonerado"
padrao_analitico = r"SINAPI_Custo_Ref_Composicoes_Analitico_PE_\d{6}_Desonerado"
padrao_sintetico = r"SINAPI_Custo_Ref_Composicoes_Sintetico_PE_\d{6}_Desonerado"

pastas_correspondentes = []

for item in os.listdir(caminho_pasta):
    item_caminho = os.path.join(caminho_pasta, item)
    if os.path.isdir(item_caminho) and re.match(padrao, item):
        pastas_correspondentes.append(item)

for pasta in pastas_correspondentes:
    data_ref = pasta.split("_")[-2]
    mes_ano = f"{data_ref[4:]}/{data_ref[:4]}"

    caminho = f'{caminho_pasta}/{pasta}'
    arquivos_xlsx = [f"{caminho}/{f}" for f in os.listdir(caminho) if f.endswith('.xlsx')]
    print(mes_ano)
    for arquivo in arquivos_xlsx:
      nome_arquivo = os.path.basename(arquivo)
    
      if re.match(padrao_sintetico, nome_arquivo):
        sinapi_excel_to_csv(arquivo, 'BASE/Sintético')
      elif re.match(padrao_analitico, nome_arquivo):
        sinapi_excel_to_csv(arquivo, 'BASE/Analítico') 
      elif re.match(padrao_insumo, nome_arquivo):
        sinapi_excel_to_csv(arquivo, 'BASE/Insumos')