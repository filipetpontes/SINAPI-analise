import streamlit as st
import pandas as pd
from functions import sinapi_leitura_csv, verifica_meses
from st_aggrid import AgGrid, GridOptionsBuilder

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

# Inicialização do estado
if "codigo" not in st.session_state:
    st.session_state["codigo"] = ""
if "mostrar_detalhes" not in st.session_state:
    st.session_state["mostrar_detalhes"] = False
if "palavra_chave" not in st.session_state:
    st.session_state["palavra_chave"] = ""
if "df" not in st.session_state:
    st.session_state["df"] = None  # Para armazenar o DataFrame carregado
if "descricao_classe" not in st.session_state:
    st.session_state["descricao_classe"] = "Todos"
if "descricao_tipo_1" not in st.session_state:
    st.session_state["descricao_tipo_1"] = "Todos"

# Redirecionar para a página correta baseado no session_state
if "page" in st.session_state and st.session_state["page"] == "2_Detalhamento":
    # Evita múltiplos redirecionamentos
    if "redirecionado" not in st.session_state or not st.session_state["redirecionado"]:
        st.session_state["redirecionado"] = True  # Marca como redirecionado
        st.query_params = {"page": "2_Detalhamento", "codigo": st.session_state.get("codigo", "")}
        st.stop()  # Para evitar que o restante do código no 1_Tabelas.py seja executado
    else:
        st.session_state["page"] = "1_Tabelas"  # Reseta para a página principal


# Função para redefinir a palavra-chave quando os dropdowns mudarem
def reset_palavra_chave():
    st.session_state["palavra_chave"] = ""

# Campos de entrada em colunas
col1, col2, col3 = st.columns(3)

with col1:
    estado_selecionado = st.selectbox("Estado:", options=['PE'])
    st.session_state["estado"] = estado_selecionado

with col2:
    datas_disponiveis = verifica_meses(caminho_csvs_analitico)

    data_selecionada = st.selectbox("Tabela SINAPI:", options=datas_disponiveis)
    st.session_state.data_selecionada = data_selecionada
    mes, ano = data_selecionada.split('/')

with col3:
    desoneracao = st.selectbox("Desoneração:", options=['Desonerado'])
    st.session_state["desoneracao"] = desoneracao
    if desoneracao == 'Não Desonerado':
        desoneracao = 'NaoDesonerado'

# Botão para exibir o DataFrame
if st.button("Exibir"):
    arquivo_csv = f'{caminho_csvs_sintetico}/SINAPI_Custo_Ref_Composicoes_Sintetico_{estado_selecionado}_{ano}{mes}_{desoneracao}.csv'
    try:
        df = sinapi_leitura_csv(arquivo_csv)
        st.session_state["df"] = df[['DESCRICAO DA CLASSE', 'DESCRICAO DO TIPO 1', 'CODIGO  DA COMPOSICAO', 'DESCRICAO DA COMPOSICAO', 'UNIDADE', 'CUSTO TOTAL']]  # Armazenar o DataFrame no session_state
    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {e}")

# Exibição do DataFrame e Filtros
if st.session_state["df"] is not None:
    # Filtro por Descrição da Classe e Tipo (lado a lado)
    st.markdown("### Filtros")
    col1, col2 = st.columns(2)

    with col1:
        descricoes_classe = ["Todos"] + st.session_state["df"]['DESCRICAO DA CLASSE'].dropna().unique().tolist()
        descricao_classe_selecionada = st.selectbox(
            "Descrição da Classe:",
            options=descricoes_classe,
            key="descricao_classe",
            on_change=reset_palavra_chave  # Limpa o campo de texto
        )

    with col2:
        df_filtrado_classe = st.session_state["df"]
        if descricao_classe_selecionada != "Todos":
            df_filtrado_classe = df_filtrado_classe[df_filtrado_classe['DESCRICAO DA CLASSE'] == descricao_classe_selecionada]

        descricoes_tipo_1 = ["Todos"] + df_filtrado_classe['DESCRICAO DO TIPO 1'].dropna().unique().tolist()
        descricao_tipo_1_selecionada = st.selectbox(
            "Descrição do Tipo:",
            options=descricoes_tipo_1,
            key="descricao_tipo_1",
            on_change=reset_palavra_chave  # Limpa o campo de texto
        )

    # Aplicar Filtros Combinados
    df_filtrado = df_filtrado_classe
    if descricao_tipo_1_selecionada != "Todos":
        df_filtrado = df_filtrado[df_filtrado['DESCRICAO DO TIPO 1'] == descricao_tipo_1_selecionada]

    palavra_chave = st.text_input(
        "Digite uma palavra-chave:",
        value=st.session_state["palavra_chave"],
        key="input_palavra_chave"
    )

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

    # Configurar Ag-Grid
    gb = GridOptionsBuilder.from_dataframe(df_exibicao)
    gb.configure_column("Descrição da Composição", wrapText=True, autoHeight=True, maxWidth=650)  # Limitar largura máxima
    gb.configure_column("Unidade", maxWidth=90)  # Manter Unidade visível
    gb.configure_column("Valor", maxWidth=100)  # Manter Valor visível
    gb.configure_selection('single', use_checkbox=True)

    grid_options = gb.build()

    # Renderizar com Ag-Grid
    grid_response = AgGrid(
        df_exibicao,
        gridOptions=grid_options,
        height=700,
        fit_columns_on_grid_load=False,
        enable_enterprise_modules=False,
        allow_unsafe_jscode=True,
        update_mode='MODEL_CHANGED'
    )

    if st.button("Detalhar"):
        if grid_response['selected_rows'] is not None:
            codigo = grid_response['selected_rows']['Código'].iloc[0]
            st.session_state["codigo"] = codigo
            st.session_state["page"] = "2_Detalhamento"
        st.query_params = {"page": "2_Detalhamento", 
                           "codigo": codigo, "estado": st.session_state["estado"], 
                           "estado": st.session_state["estado"], 
                           "desoneracao": st.session_state["desoneracao"]}
        
        st.switch_page("pages/2_Detalhamento.py")

 


