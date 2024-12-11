import streamlit as st

st.set_page_config(
     page_title="Sobre",
     page_icon="📝",
     layout="wide",
     initial_sidebar_state="expanded",
)

imagem = "marca_cesar_school.png"
st.sidebar.image(imagem, use_container_width=False, width=100)

st.markdown(
    "<h2 style='text-align: left; color: #f37421;'>Sobre</h2>",
    unsafe_allow_html=True
)

texto = """
    <p style="text-align: justify;font-size: 22px;">
    Este é um projeto desenvolvido por <strong>Filipe Pontes</strong> como Trabalho de Conclusão de Curso da Pós-Graduação em <strong>Engenharia e Análise de Dados</strong> na <strong>CESAR School</strong>, turma 2023.1.
    </p>
    """
    
st.markdown(texto, unsafe_allow_html=True)


