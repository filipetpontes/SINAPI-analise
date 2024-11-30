import streamlit as st
import pandas as pd
import plotly.express as px
from st_aggrid import AgGrid, GridOptionsBuilder
from functions import detalha_composicao, verifica_meses

caminho_csvs_sintetico = 'BASE/Sintético'
caminho_csvs_analitico = 'BASE/Analítico'

# Configuração da página
st.set_page_config(
    page_title="Análise SINAPI",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    "<h2 style='text-align: left; color: #f37421;'>SINAPI - Detalhamento de Composições</h2>",
    unsafe_allow_html=True
)

imagem = "marca_cesar_school.png"
st.sidebar.image(imagem, use_container_width=False, width=150)

# Inicialização do estado
if "codigo" not in st.session_state:
    st.session_state["codigo"] = ""
if "mostrar_detalhes" not in st.session_state:
    st.session_state["mostrar_detalhes"] = False

# Campos para entrada de dados
col1, col2, col3 = st.columns(3)

with col1:
    estado_selecionado = st.selectbox("Estado:", options=['PE'])

    # Campo de texto para entrada do código
    st.text_input(
        "Código da Composição:",
        value=st.session_state["codigo"],
        key="codigo"
    )

with col2:
    datas_disponiveis = verifica_meses(caminho_csvs_analitico)
    data_selecionada = st.selectbox("Tabela SINAPI:", options=datas_disponiveis)
    mes, ano = data_selecionada.split('/')
    st.write("")
    st.write("")
    if st.button("Detalhar"):
        st.session_state["mostrar_detalhes"] = True

with col3:
    desoneracao = st.selectbox("Desoneração:", options=['Desonerado'])
    if desoneracao == 'Não Desonerado':
        desoneracao = 'NaoDesonerado'

# Exibição dos detalhes
if st.session_state["mostrar_detalhes"]:
    if st.session_state["codigo"]:
        st.markdown("---")
        st.markdown("<h4 style='color: #f37421;'>Detalhes da Composição</h4>", unsafe_allow_html=True)
        arquivo_csv = f'{caminho_csvs_analitico}/SINAPI_Custo_Ref_Composicoes_Analitico_{estado_selecionado}_{ano}{mes}_{desoneracao}.csv'
        
        # Obtendo as informações e o gráfico
        informacoes, fig, itens, historico = detalha_composicao(arquivo_csv, st.session_state["codigo"])
        
        if informacoes is None:  # Código não encontrado
            st.warning(f"Código **{st.session_state['codigo']}** não encontrado na tabela selecionada.")
        else:
            st.write(f"**Código:** {st.session_state['codigo']}")
            st.write(f"**Classe:** {informacoes['DESCRICAO DA CLASSE']}")
            st.write(f"**Tipo:** {informacoes['DESCRICAO DO TIPO 1']}")
            st.write(f"**Descrição:** {informacoes['DESCRICAO DA COMPOSICAO']}")
            st.write(f"**Referência:** {estado_selecionado} - {data_selecionada}")
            st.write(f"**Valor:** R$ {informacoes['CUSTO TOTAL']}")
            # st.write(itens)

            # Configurar Ag-Grid
            gb = GridOptionsBuilder.from_dataframe(itens)
            gb.configure_column("Descrição", wrapText=True, autoHeight=True, maxWidth=400)  # Limitar largura máxima
            gb.configure_column("Tipo", maxWidth=105)
            gb.configure_column("Código", maxWidth=70)
            gb.configure_column("Unidade", maxWidth=70)
            gb.configure_column("Coeficiente", maxWidth=85)
            gb.configure_column("Preço Unitário", maxWidth=100)
            gb.configure_selection('single')  # Permite seleção de uma linha
            grid_options = gb.build()

            # Renderizar com Ag-Grid
            grid_response = AgGrid(
                itens,
                gridOptions=grid_options,
                fit_columns_on_grid_load=False,  # Evita que ajuste automático esconda colunas
                enable_enterprise_modules=False,
                allow_unsafe_jscode=True,
                update_mode='MODEL_CHANGED'
            )
            st.markdown("---")
            st.markdown("<h4 style='color: #f37421;'>Distribuição dos Valores</h4>", unsafe_allow_html=True)
            st.plotly_chart(fig)
            st.markdown("---")
            st.markdown("<h4 style='color: #f37421;'>Histórico de Preços</h4>", unsafe_allow_html=True)
            st.write(historico)
            
    else:
        st.warning("Por favor, insira um código válido.")
