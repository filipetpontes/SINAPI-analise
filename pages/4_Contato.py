import streamlit as st

st.set_page_config(
     page_title="CamVote - Contato",
     page_icon="📞",
     layout="wide",
     initial_sidebar_state="expanded",
)

imagem = "marca_cesar_school.png"
st.sidebar.image(imagem, use_container_width=False, width=100)

st.header("📞 Contato")

st.markdown("#### Filipe Pontes")
st.markdown("[![LinkedIn](https://img.shields.io/badge/LinkedIn-blue)](https://www.linkedin.com/in/filipetpontes/)")
st.markdown("[![GitHub](https://img.shields.io/badge/GitHub-gray)](https://github.com/filipetpontes)")