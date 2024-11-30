import pandas as pd
import plotly.express as px
import os

def sinapi_leitura_csv(caminho_csv):
    
    df = pd.read_csv(caminho_csv, sep=';', dtype='str')
    return df

def pesquisa_codigo_sinapi_analitico(caminho_csv, codigo_composicao):
    chunks = []
    chunksize = 10000

    for chunk in pd.read_csv(caminho_csv, sep=';', chunksize=chunksize, dtype='str'):
        filtered_chunk = chunk[chunk['CODIGO DA COMPOSICAO'] == codigo_composicao]
        chunks.append(filtered_chunk)

    if chunks:  # Verifica se há dados nos chunks
        df_filtrado = pd.concat(chunks, ignore_index=True)
        return df_filtrado
    else:
        return pd.DataFrame()  # Retorna um DataFrame vazio se não houver resultados

def historico_preco(caminho_csvs, codigo_composicao):
    dados_variacao = []
    arquivos_csv = [os.path.join(caminho_csvs, f) for f in os.listdir(caminho_csvs) if f.endswith('.csv')]
    for caminho_csv in arquivos_csv:
        data_ref = caminho_csv.split('_')[-2]
        
        mes_ano = f"{data_ref[4:]}/{data_ref[:4]}"
        
        for chunk in pd.read_csv(caminho_csv, sep=';', chunksize=10000, dtype='str'):
            filtered_chunk = chunk[chunk['CODIGO  DA COMPOSICAO'] == codigo_composicao]
            if not filtered_chunk.empty:
                custo_total = filtered_chunk['CUSTO TOTAL'].iloc[0]
                dados_variacao.append({'Data': mes_ano, 'Custo Total': float(custo_total.replace(',', '.'))})
                break

    if dados_variacao:
        df_variacao = pd.DataFrame(dados_variacao)
        df_variacao['Data_aux'] = pd.to_datetime(df_variacao['Data'], format='%m/%Y')
        df_variacao = df_variacao.sort_values(by='Data_aux')

        fig = px.line(
            df_variacao,
            x='Data',
            y='Custo Total',
            labels={'Data': 'Data', 'Custo Total': 'Valor (R$)'},
            markers=True
        )
        fig.update_yaxes(tickformat=".2f")
        return fig
    else:
        return pd.DataFrame()  # Retorna vazio se não houver dados
    
def detalha_composicao(caminho_csv, codigo):
    df = pesquisa_codigo_sinapi_analitico(caminho_csv, codigo)

    if df.empty:
        return None, None  # Retorna None se o código não for encontrado

    informacoes = df.iloc[0]
    
    # Convertendo as colunas para numérico:
    cols = ['% MAO DE OBRA', '% MATERIAL', '% EQUIPAMENTO', '% SERVICOS TERCEIROS', '% OUTROS']
    informacoes[cols] = pd.to_numeric(informacoes[cols].str.replace(',', '.'), errors='coerce')

    valores = informacoes[cols].values
    labels = ['Mão de Obra', 'Material', 'Equipamento', 'Serviços Terceiros', 'Outros']

    # Filtrando valores 0:
    df_grafico = pd.DataFrame({'labels': labels, 'valores': valores})
    df_grafico = df_grafico[df_grafico['valores'] != 0]

    # Gerando o gráfico usando Plotly
    fig = px.pie(df_grafico, values='valores', names='labels')
   
    itens = df[1:][['TIPO ITEM', 'CODIGO ITEM', 'DESCRIÇÃO ITEM', 'UNIDADE ITEM', 'COEFICIENTE', 'PRECO UNITARIO', 'CUSTO TOTAL.1']]
    itens = itens.rename(
        columns={
            'TIPO ITEM': 'Tipo',
            'CODIGO ITEM': 'Código',
            'DESCRIÇÃO ITEM': 'Descrição',
            'UNIDADE ITEM': 'Unidade',
            'COEFICIENTE': 'Coeficiente',
            'PRECO UNITARIO': 'Preço Unitário',
            'CUSTO TOTAL.1': 'Custo Total'
        })
    
    historico = historico_preco('BASE/Sintético', codigo)
    return informacoes, fig, itens, historico

def verifica_meses(caminho):
    meses = []
    arquivos_csv = [os.path.join(caminho, f) for f in os.listdir(caminho) if f.endswith('.csv')]
    for arquivo_csv in arquivos_csv:
        data_ref = arquivo_csv.split('_')[-2]
        
        mes_ano = f"{data_ref[4:]}/{data_ref[:4]}"
        meses.append(mes_ano)

    meses_ordenados = sorted(meses, key=lambda x: (int(x.split('/')[1]), int(x.split('/')[0])))
    return meses_ordenados