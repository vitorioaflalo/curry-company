import streamlit as st
from PIL import Image

st.set_page_config(
    page_title = "Home",
    page_icon = ":fork_and_knife_with_plate:",
    layout="wide",
)

image = Image.open('logo.png')

st.sidebar.image(image, width = 120)

st.sidebar.markdown(' # Curry Company')
st.sidebar.markdown(' ## Delivery mais Rápido da Cidade')
st.sidebar.markdown("""---""")

st.write('# Crescimento Curry Company Dashboard')

st.markdown(
"""
Dashboard de Crescimento foi construído para acompanhar as métricas de crescimento dos Entregadores e Restaurantes.
### Como utilizar? 
- Visão Empresa:
    - Visão Gerencial: Métricas Gerais de Comportamento
    - Visão Tática: Indicadores Semanais de Crescimento
    - Visão Geográfica: Insights de Geolocalização
- Visão Entregador:
    - Visão Gerencial: Acompanhamento dos indicadores semanais de crescimento
- Visão Restaurante:
    - Indicadores semanais de crescimento dos restaurantes 
### Ajuda
- Time de Data Science no Discord
    - @vitorioaflalo
"""
)