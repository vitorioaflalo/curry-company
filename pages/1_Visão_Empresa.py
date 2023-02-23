# bibliotecas necessárias
import pandas as pd
import plotly.express as px
import math
import folium
from haversine import haversine, Unit
import streamlit as st
from streamlit_folium import folium_static
from PIL import Image

#-------------------------------FUNÇÕES: LIMPEZA-------------------------------#
def clean_code(df1):
    """ Essa função tem a responsabilidade de limpar o dataframe 
    
        1) Tipos de limpeza: remoção dos dados NA
        2) Mudança do tipo da coluna de dados
        3) Remoção dos espaços das variáveis de texto
        4) Formatação da coluna de datas
        5) Limpeza da coluna de tempo (remoção do texto da variável numérica)
        
        Input: Dataframe
        Output: Dataframe
    """
    #removendo NA
    df1 = df1.loc[df1['Road_traffic_density'] != 'NaN ', :].copy()
    df1 = df1.loc[df1['City']!='NaN ', :].copy()
    df1 = df1.loc[df1['Delivery_person_Age'] != 'NaN ',:].copy()
    df1 = df1.loc[df1['multiple_deliveries'] != 'NaN ',:].copy()
    #convertendo a coluna age para número

    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)

    #convertendo a coluan rating para float
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)

    #convertendo order date para data
    df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format = '%d-%m-%Y')

    #convertendo multiple deliveries para int

    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype(int)

    #removendo os espaços dentro de string
    df1 = df1.reset_index(drop=True)
    df1.loc[:, 'ID'] = df1.loc[:, 'ID'].str.strip()
    df1.loc[:, 'Road_traffic_density'] = df1.loc[:, 'Road_traffic_density'].str.strip()
    df1.loc[:, 'Type_of_order'] = df1.loc[:, 'Type_of_order'].str.strip()
    df1.loc[:, 'Type_of_vehicle'] = df1.loc[:, 'Type_of_vehicle'].str.strip()
    df1.loc[:, 'City'] = df1.loc[:, 'City'].str.strip()
    df1.loc[:, 'Festival'] = df1.loc[:, 'Festival'].str.strip()

    #limpando a coluna time taken
    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply(lambda x: x.split('(min) ')[1])
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(int)

    return df1

#-------------------------------FUNÇÕES: GRÁFICOS E MAPAS-------------------------------#
def order_metric(df1):
    """ Essa função tem a responsabilidade gerar um gráfico de barras
        Input: Dataframe
        Output: Figura
    """
    df_aux = df1[['ID','Order_Date']].groupby('Order_Date').count().reset_index()
    fig = px.bar(df_aux, x = 'Order_Date', y = 'ID')
    return fig

def pedidos_por_trafico(df1):
    """ Essa função tem a responsabilidade gerar um gráfico de pizza
        Input: Dataframe
        Output: Figura
    """
    df_aux = df1[['ID', 'Road_traffic_density']].groupby('Road_traffic_density').count().reset_index()
    fig = px.pie(df_aux, values = 'ID', names = 'Road_traffic_density')
    return fig

def pedidos_por_cidade_trafico(df1):
    """ Essa função tem a responsabilidade gerar um gráfico de distribuição
        Input: Dataframe
        Output: Figura
    """
    df_aux = df1[['ID', 'City', 'Road_traffic_density']].groupby(['City', 'Road_traffic_density']).count().reset_index()
    fig = px.scatter(df_aux, x = 'City', y = 'Road_traffic_density', size = 'ID', color = 'City')
    return fig

def pedidos_por_semana(df1):
    # criar a coluna de semana
    """ Essa função tem a responsabilidade gerar um gráfico de linha
        Input: Dataframe
        Output: Figura
    """
    df1['week_of_year'] = df1['Order_Date'].dt.strftime('%U')
    df_aux = df1[['ID', 'week_of_year']].groupby(['week_of_year']).count().reset_index()
    fig = px.line(df_aux, x = 'week_of_year', y = 'ID')
    return fig

def pedidos_por_semana_entregador(df1):
    """ Essa função tem a responsabilidade gerar um gráfico de linha
        Input: Dataframe
        Output: Figura
    """
    df_aux1 = df1[['ID', 'week_of_year']].groupby(['week_of_year']).count().reset_index()
    df_aux2 = df1[['Delivery_person_ID', 'week_of_year']].groupby(['week_of_year']).nunique().reset_index()
    df_aux = pd.merge(df_aux1, df_aux2, on = 'week_of_year', how = 'inner')
    df_aux['Order_by_delivery'] = df_aux['ID']/df_aux['Delivery_person_ID']
    fig = px.line(df_aux, x = 'week_of_year', y = 'Order_by_delivery')
    return fig

def mapa(df1):
    """ Essa função tem a responsabilidade gerar um mapa
        Input: Dataframe
        Output: Figura
    """
    df_aux = df1[['ID', 'Road_traffic_density', 'City', 'Delivery_location_latitude',  'Delivery_location_longitude']].groupby(['City', 'Road_traffic_density']).median().reset_index()
    df_aux = df_aux.loc[df_aux['City']!='NaN', :]
    df_aux = df_aux.loc[df_aux['Road_traffic_density']!='NaN', :]
    map = folium.Map()
    for index, location_info in df_aux.iterrows():
        folium.Marker([location_info
                       ['Delivery_location_latitude'], 
                       location_info['Delivery_location_longitude']], 
                      popup = location_info[['City', 'Road_traffic_density']]).add_to(map)  

    return map
#---------------------------------INÍCIO DA ESTRUTURA LÓGICA---------------------------------#
# lendo o arquivo importado
df = pd.read_csv( 'dataset/train.csv' ) 

# limpandando dataset
df1 = clean_code(df)
#----------------------------------STREAMLIT: CONFIG-------------------------------------------#

st.set_page_config(page_title = "Visão Empresa", page_icon = ":fork_and_knife_with_plate:", layout="wide")

#----------------------------------STREAMLIT: BARRA LATERAL------------------------------------#

st.header('Marketplace - Visão Empresa ')

image = Image.open('logo.png')
st.sidebar.image(image, width = 200)

## Labels Sidebar
st.sidebar.markdown(' # Curry Company')
st.sidebar.markdown(' ## Delivery mais Rápido da Cidade')
st.sidebar.markdown("""---""")

## Filtro de data
st.sidebar.markdown('## Selecione uma data limite')
data_slider = st.sidebar.slider(
    'Até qual valor?',
    value = pd.datetime(2022, 4, 13),
    min_value = pd.datetime(2022, 2, 11),
    max_value = pd.datetime(2022, 4, 6),
    format = 'DD-MM-YYYY'
)

data_somente_data =data_slider.date()
data_formatada = data_somente_data.strftime("%d-%m-%Y")
st.header(f'Base de dados até a data {data_formatada}')
st.sidebar.markdown("""---""")

## Segundo filtro
st.sidebar.markdown('## Selecione as condições de trânsito')
traffic_options = st.sidebar.multiselect(
    'Quais as condições de trânsito?',
    ['Low', 'Medium', 'High', 'Jam'],
    default = ['Low', 'Medium', 'High', 'Jam']
)

st.sidebar.markdown("""---""")
st.sidebar.markdown('### Powered by Comunidade DS ')


#Filtro de data
linhas_selecionadas = df1['Order_Date'] <= data_slider
df1 = df1.loc[linhas_selecionadas, :]

#Filtro de Tráfico
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas, :]
st.dataframe(df1) 


#----------------------------------STREAMLIT: LAYOUT PRINCIPAL---------------------------------#

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

with tab1: 
    with st.container():
        st.header('Pedidos por Dia')
        fig = order_metric(df1)
        st.plotly_chart(fig, use_container_width = True)
        st.markdown("""---""")
        
    with st.container():
        col1, col2 = st.columns(2)
        st.markdown("""---""")
        
        with col1:
            st.header('Pedidos por Tráfico de Trânsito')
            fig = pedidos_por_trafico(df1)
            st.plotly_chart(fig, use_container_width = True)
            
        with col2:
            st.header('Pedidos por Cidade e Tráfico de Trânsito')
            fig = pedidos_por_cidade_trafico(df1)
            st.plotly_chart(fig, use_container_width = True) 
            
with tab2:
    with st.container():
        st.header('Pedidos por Semana')
        fig = pedidos_por_semana(df1)
        st.plotly_chart(fig, use_container_width = True) 
        
    with st.container():
        st.markdown("""---""")
        st.header('Pedidos por Semana por Entregador')
        fig = pedidos_por_semana_entregador(df1)
        st.plotly_chart(fig, use_container_width = True) 
    
with tab3:
    st.header('Mapa das Entregas')
    map = mapa(df1)
    folium_static(map, height = 600, width = 1024)
