import streamlit as st

st.set_page_config(
     page_title="Contato",
     page_icon="📞",
     layout="wide",
     initial_sidebar_state="expanded",
)

imagem = "marca_cesar_school.png"
st.sidebar.image(imagem, use_container_width=False, width=125)

st.markdown(
    "<h2 style='text-align: left; color: #f37421;'>Contato</h2>",
    unsafe_allow_html=True
)

st.markdown("#### Filipe Pontes - (81) 99859-8451")
st.markdown("[![LinkedIn](https://img.shields.io/badge/LinkedIn-blue)](https://www.linkedin.com/in/filipetpontes/)")
st.markdown("[![GitHub](https://img.shields.io/badge/GitHub-gray)](https://github.com/filipetpontes)")