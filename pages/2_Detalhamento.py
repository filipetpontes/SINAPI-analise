import streamlit as st
from functions import detalha_composicao, verifica_meses, detalhar_composicoes_em_insumos, sinapi_leitura_csv
import time

caminho_base = 'BASE'
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
# st.session_state["status"] = ""

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
    desoneracao = st.selectbox("Desoneração:", options=['Desonerado', 'Não Desonerado'], key="desoneracao")
    caminho_csvs_sintetico = f'{caminho_base}/{desoneracao}/Sintético'
    caminho_csvs_analitico = f'{caminho_base}/{desoneracao}/Analítico'
    if desoneracao == 'Não Desonerado':
        desoneracao = 'NaoDesonerado'

with col3:
    datas_disponiveis = verifica_meses(caminho_csvs_analitico)
    data_selecionada = st.selectbox("Tabela SINAPI:", options=datas_disponiveis, key="data_selecionada")
    mes, ano = data_selecionada.split('/')

if st.button("Detalhar"):
    st.session_state["mostrar_detalhes"] = True

with st.spinner('Carregando...'):
    if st.session_state["mostrar_detalhes"]:
        if st.session_state["codigo"]:
            st.markdown("---")
            st.markdown("<h4 style='color: #f37421;'>Detalhes da Composição</h4>", unsafe_allow_html=True)
            arquivo_csv = f'{caminho_csvs_analitico}/SINAPI_Custo_Ref_Composicoes_Analitico_{estado_selecionado}_{ano}{mes}_{desoneracao}.csv'

            # Obtendo as informações e o gráfico
            informacoes, fig, itens, historico, historico_valores = detalha_composicao(arquivo_csv, st.session_state["codigo"])

            if informacoes is None:  # Código não encontrado
                st.warning(f"Código **{st.session_state['codigo']}** não encontrado na tabela selecionada.")
            else:

                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric(label='Código', value=st.session_state['codigo'])
                with col2:
                    st.metric(label='Referência', value=f"{data_selecionada} - {estado_selecionado}")
                with col3:
                    st.metric(label='Unidade', value=f"{informacoes['UNIDADE']}")
                with col4:
                    st.metric(label='Valor', value=f"R$ {informacoes['CUSTO TOTAL']}")

                st.write(f"**Descrição:** {informacoes['DESCRICAO DA COMPOSICAO']}")
                st.write(f"**Classe:** {informacoes['DESCRICAO DA CLASSE']}")
                st.write(f"**Tipo:** {informacoes['DESCRICAO DO TIPO 1']}")

                on = st.toggle(
                    "Detalhamento Avançado", 
                    help="Habilite o detalhamento avançado para expandir a composição."
                )

                with st.expander("ℹ️ O que é o Detalhamento Avançado?"):
                    st.write("""
                    Cada composição é formada por insumos e/ou outras composições. Dessa forma, o detalhamento avançado permite:
                    - Expandir as composições de forma recursiva;
                    - Destrinchar cada composição até chegar ao nível de insumos;
                    - Visualizar insumos e quantidades em detalhes;
                    - É uma ferramenta poderosa para planejamento de obras.
                    """)

                if on:
                    st.dataframe(
                                detalhar_composicoes_em_insumos(sinapi_leitura_csv(arquivo_csv), st.session_state['codigo']),
                                hide_index=True
                                )

                else:
                    st.dataframe(
                                itens,
                                hide_index=True,
                                column_config={
                                    "hist_coef": st.column_config.LineChartColumn(
                                        "Histórico Coeficiente", y_min=0, y_max=1
                                    ),
                                },
                                )

                st.markdown("---")
                st.markdown("<h4 style='color: #f37421;'>Histórico de Preços</h4>", unsafe_allow_html=True)
                st.write(historico)
                st.markdown("---")
                st.markdown("<h4 style='color: #f37421;'>Distribuição dos Valores</h4>", unsafe_allow_html=True)
                st.plotly_chart(fig)
                
        else:
            st.warning("Por favor, insira um código válido.")

