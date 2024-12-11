import streamlit as st
import pandas as pd
from functions import sinapi_leitura_csv, verifica_meses, detalha_composicao

caminho_csvs_sintetico = 'BASE/Sintético'
caminho_csvs_analitico = 'BASE/Analítico'

# Configuração da página
st.set_page_config(
    page_title="Análise SINAPI",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Título e imagem na barra lateral
st.markdown(
    "<h2 style='text-align: left; color: #f37421;'>SINAPI - Tabelas</h2>",
    unsafe_allow_html=True
)
imagem = "marca_cesar_school.png"
st.sidebar.image(imagem, use_container_width=False, width=125)

# Linha divisória
st.markdown("---")

# Inicialização do estado para o DataFrame
if "df" not in st.session_state:
    st.session_state["df"] = None

# Função para redefinir o campo de palavra-chave
def reset_palavra_chave():
    return ""

# Campos de entrada em colunas
col1, col2, col3 = st.columns(3)

with col1:
    estado_selecionado = st.selectbox("Estado:", options=['PE'])

with col2:
    datas_disponiveis = verifica_meses(caminho_csvs_analitico)

    data_selecionada = st.selectbox("Tabela SINAPI:", options=datas_disponiveis)
    mes, ano = data_selecionada.split('/')

with col3:
    desoneracao = st.selectbox("Desoneração:", options=['Desonerado'])
    if desoneracao == 'Não Desonerado':
        desoneracao = 'NaoDesonerado'

# Botão para exibir o DataFrame
if st.button("Exibir"):
    arquivo_csv = f'{caminho_csvs_sintetico}/SINAPI_Custo_Ref_Composicoes_Sintetico_{estado_selecionado}_{ano}{mes}_{desoneracao}.csv'
    try:
        df = sinapi_leitura_csv(arquivo_csv)
        st.session_state["df"] = df[['DESCRICAO DA CLASSE', 'DESCRICAO DO TIPO 1', 'CODIGO  DA COMPOSICAO', 'DESCRICAO DA COMPOSICAO', 'UNIDADE', 'CUSTO TOTAL']]
    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {e}")

# Exibição do DataFrame e Filtros
if st.session_state["df"] is not None:
    df = st.session_state["df"]
    # Filtro por Descrição da Classe e Tipo (lado a lado)
    st.markdown("### Filtros")
    col1, col2 = st.columns(2)

    with col1:
        descricoes_classe = ["Todos"] + df['DESCRICAO DA CLASSE'].dropna().unique().tolist()
        descricao_classe_selecionada = st.selectbox("Descrição da Classe:", options=descricoes_classe)

    with col2:
        df_filtrado_classe = df
        if descricao_classe_selecionada != "Todos":
            df_filtrado_classe = df_filtrado_classe[df_filtrado_classe['DESCRICAO DA CLASSE'] == descricao_classe_selecionada]

        descricoes_tipo_1 = ["Todos"] + df_filtrado_classe['DESCRICAO DO TIPO 1'].dropna().unique().tolist()
        descricao_tipo_1_selecionada = st.selectbox("Descrição do Tipo:", options=descricoes_tipo_1)

    # Aplicar Filtros Combinados
    df_filtrado = df_filtrado_classe
    if descricao_tipo_1_selecionada != "Todos":
        df_filtrado = df_filtrado[df_filtrado['DESCRICAO DO TIPO 1'] == descricao_tipo_1_selecionada]

    palavra_chave = st.text_input("Digite uma palavra-chave:", value=reset_palavra_chave())

    if palavra_chave:
        df_filtrado = df_filtrado[df_filtrado['DESCRICAO DA COMPOSICAO'].str.contains(palavra_chave, case=False, na=False)]

    # Remover as colunas "DESCRICAO DA CLASSE" e "DESCRICAO DO TIPO 1" da exibição
    df_exibicao = df_filtrado.drop(columns=['DESCRICAO DA CLASSE', 'DESCRICAO DO TIPO 1'])

    # Renomear as colunas para exibição
    df_exibicao = df_exibicao.rename(
        columns={
            'CODIGO  DA COMPOSICAO': 'Código',
            'DESCRICAO DA COMPOSICAO': 'Descrição da Composição',
            'UNIDADE': 'Unidade',
            'CUSTO TOTAL': 'Valor'
        }
    )

    selecao = st.dataframe(
                df_exibicao,
                hide_index=True,
                selection_mode="single-row",
                on_select="rerun"
                )

    codigo = df_exibicao.iloc[selecao["selection"]["rows"][0]]["Código"]
    arquivo_csv = f'{caminho_csvs_analitico}/SINAPI_Custo_Ref_Composicoes_Analitico_{estado_selecionado}_{ano}{mes}_{desoneracao}.csv'

    informacoes, fig, itens, historico = detalha_composicao(arquivo_csv, codigo)

    st.markdown("---")
    st.markdown("<h4 style='color: #f37421;'>Detalhes da Composição</h4>", unsafe_allow_html=True)

    if informacoes is None:
        st.warning(f"Código **{codigo}** não encontrado na tabela selecionada.")
    else:
        st.write(f"**Código:** {codigo}")
        st.write(f"**Classe:** {informacoes['DESCRICAO DA CLASSE']}")
        st.write(f"**Tipo:** {informacoes['DESCRICAO DO TIPO 1']}")
        st.write(f"**Descrição:** {informacoes['DESCRICAO DA COMPOSICAO']}")
        st.write(f"**Referência:** {estado_selecionado} - {data_selecionada}")
        st.write(f"**Valor:** R$ {informacoes['CUSTO TOTAL']}")
    st.markdown("---")
    st.markdown("<h4 style='color: #f37421;'>Distribuição dos Valores</h4>", unsafe_allow_html=True)
    st.plotly_chart(fig)
    st.markdown("---")
    st.markdown("<h4 style='color: #f37421;'>Histórico de Preços</h4>", unsafe_allow_html=True)
    st.write(historico)
