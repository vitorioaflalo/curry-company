# bibliotecas necessárias
import pandas as pd
import plotly.express as px
import folium
import math
from haversine import haversine, Unit
import streamlit as st
from streamlit_folium import folium_static
from PIL import Image
import datetime

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
    df1 = df1.loc[df1['Weatherconditions']!= 'conditions NaN', :].copy()
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

def metric(df1): 
    """
        Essa função retorna as métricas gerais na seção de entregadores, divididas em 4 colunas
        INPUT: Dataframe
        OUTPUT: None
    """    
    with col1:
        maior = df1.loc[:, 'Delivery_person_Age'].max()
        col1.metric('Maior de Idade', maior)

    with col2:
        menor = df1.loc[:, 'Delivery_person_Age'].min()
        col2.metric('Menor de Idade', menor)

    with col3:
        melhor = df1.loc[:, 'Vehicle_condition'].max()
        col3.metric('Melhor Condição Veículo', melhor)

    with col4:
        pior = df1.loc[:, 'Vehicle_condition'].min()
        col4.metric('Pior Condição Veículo', pior)
            
def avaliacao_media_entregador(df1):
    """
        Essa função retorna um dataframe agrupado pela ID do entregador
        INPUT: Dataframe
        OUTPUT: Dataframe
    """   
    df_grouped = (df1[['Delivery_person_ID',                           'Delivery_person_Ratings']].groupby('Delivery_person_ID').mean().sort_values('Delivery_person_Ratings', ascending = False).reset_index())
    return df_grouped

def avaliacao_media_transito(df1):
    """
        Essa função retorna um dataframe agrupado pela condição de tráfego
        INPUT: Dataframe
        OUTPUT: Dataframe
    """  
    df_grouped = df1[['Delivery_person_Ratings', 'Road_traffic_density']].groupby('Road_traffic_density').agg(['mean', 'std']).sort_values([('Delivery_person_Ratings', 'mean')], ascending = False).reset_index()
    return df_grouped

def avaliacao_media_condicao_climatica(df1):
    """
        Essa função retorna um dataframe agrupado pela condição de tempo
        INPUT: Dataframe
        OUTPUT: Dataframe
    """
    df_std_avg_weather = df1[['Weatherconditions', 'Delivery_person_Ratings']].groupby('Weatherconditions').agg(['mean', 'std']).reset_index()
    return df_std_avg_weather
        
    
def entregadores_rapidez(df1, top_asc):
    """
        Essa função retorna um dataframe agrupado pelo entregador e cidade
        INPUT: Dataframe
        OUTPUT: Dataframe
    """
    df2 = df1.loc[:, ['Delivery_person_ID', 'City', 'Time_taken(min)']].groupby(['City', 'Delivery_person_ID']).min().sort_values(['City','Time_taken(min)'], ascending = top_asc).reset_index()
    df_aux01 = df2.loc[df2['City'] == 'Metropolitian', :].head(10)
    df_aux02 = df2.loc[df2['City'] == 'Urban', :].head(10)
    df_aux03 = df2.loc[df2['City'] == 'Semi-Urban', :].head(10)
    df3 = pd.concat([df_aux01, df_aux02, df_aux03]).reset_index(drop=True)
    return df3



#---------------------------------INÍCIO DA ESTRUTURA LÓGICA---------------------------------#
# lendo o arquivo importado
df = pd.read_csv( 'dataset/train.csv' ) 

# limpandando dataset
df1 = clean_code(df)
#----------------------------------STREAMLIT: CONFIG-------------------------------------------#

st.set_page_config(page_title = "Visão Entregador", page_icon = ":fork_and_knife_with_plate:", layout="wide")

#----------------------------------STREAMLIT: BARRA LATERAL------------------------------------#

st.header('Marketplace - Visão Entregadores')

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

## Filtro Tráfico
st.sidebar.markdown('## Selecione as condições de trânsito')
traffic_options = st.sidebar.multiselect(
    'Quais as condições de trânsito?',
    ['Low', 'Medium', 'High', 'Jam'],
    default = ['Low', 'Medium', 'High', 'Jam']
)

#Filtro Clima
st.sidebar.markdown('## Selecione o clima desejado')
clima_options = st.sidebar.multiselect(
    'Qual o clima?',
    ['conditions Sunny',
 'conditions Stormy',
 'conditions Sandstorms',
 'conditions Cloudy',
 'conditions Fog',
 'conditions Windy'],
    default = ['conditions Sunny',
 'conditions Stormy',
 'conditions Sandstorms',
 'conditions Cloudy',
 'conditions Fog',
 'conditions Windy']
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

#Filtro de Clima
linhas_selecionadas = df1['Weatherconditions'].isin(clima_options)
df1 = df1.loc[linhas_selecionadas, :]

#----------------------------------STREAMLIT: LAYOUT PRINCIPAL---------------------------------#
tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '-', '-'])

with tab1:
    
    with st.container():
        st.title('Métricas Gerais')
        col1, col2, col3, col4 = st.columns(4)
        metric(df1)
            
    with st.container():
        st.markdown("""---""")
        st.title('Avaliações Médias')
        col1, col2 = st.columns(2, gap = 'large')
        
        with col1:
            st.markdown('##### Avaliação Média por entregador ')
            df_grouped = avaliacao_media_entregador(df1)
            st.dataframe(df_grouped)
        with col2:
            st.markdown('##### Avaliação Média por Trânsito')
            df_grouped = avaliacao_media_transito(df1)
            st.dataframe(df_grouped)        
            st.markdown('##### Avaliação Média por Condição Climática')
            df_std_avg_weather = avaliacao_media_condicao_climatica(df1)
            st.dataframe(df_std_avg_weather)
    
    with st.container():
        st.markdown("""---""")
        st.title('Velocidade de Entrega')
        col1, col2 = st.columns(2, gap = 'large')
        
        with col1:
            st.markdown('#### Top Entregadores mais Rápidos por Cidade')
            df3 = entregadores_rapidez(df1, True)
            st.dataframe(df3)
            
        with col2:
            st.markdown('#### Top Entregadores mais Lentos por Cidade')
            df3 = entregadores_rapidez(df1, False)
            st.dataframe(df3)
    