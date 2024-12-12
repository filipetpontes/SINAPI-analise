import streamlit as st
from functions import detalha_composicao, verifica_meses

caminho_csvs_sintetico = 'BASE/Sintético'
caminho_csvs_analitico = 'BASE/Analítico'

# Configuração da página
st.set_page_config(
    page_title="Análise SINAPI",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    "<h2 style='text-align: left; color: #f37421;'>SINAPI - Detalhamento de Composições</h2>",
    unsafe_allow_html=True
)

imagem = "marca_cesar_school.png"
st.sidebar.image(imagem, use_container_width=False, width=125)

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
    data_selecionada = st.selectbox("Tabela SINAPI:", options=datas_disponiveis, key="data_selecionada")
    mes, ano = data_selecionada.split('/')

with col3:
    desoneracao = st.selectbox("Desoneração:", options=['Desonerado'])
    if desoneracao == 'Não Desonerado':
        desoneracao = 'NaoDesonerado'
if st.button("Detalhar"):
        st.session_state["mostrar_detalhes"] = True
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

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(label='Código', value=st.session_state['codigo'])
            with col2:
                st.metric(label='Referência', value=f"{data_selecionada} - {estado_selecionado}")
            with col3:
                st.metric(label='Valor', value=f"R$ {informacoes['CUSTO TOTAL']}")

            st.write(f"**Classe:** {informacoes['DESCRICAO DA CLASSE']}")
            st.write(f"**Tipo:** {informacoes['DESCRICAO DO TIPO 1']}")
            st.write(f"**Descrição:** {informacoes['DESCRICAO DA COMPOSICAO']}")

            st.dataframe(
                        itens,
                        hide_index=True
                        )

            st.markdown("---")
            st.markdown("<h4 style='color: #f37421;'>Distribuição dos Valores</h4>", unsafe_allow_html=True)
            st.plotly_chart(fig)
            st.markdown("---")
            st.markdown("<h4 style='color: #f37421;'>Histórico de Preços</h4>", unsafe_allow_html=True)
            st.write(historico)
            
    else:
        st.warning("Por favor, insira um código válido.")
