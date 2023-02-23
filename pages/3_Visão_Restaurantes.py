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
import numpy as np
import plotly.graph_objects as go

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
def media_entrega_festival(df1):
    """
        Essa função faz uma métrica 
        INPUT: Dataframe
        OUTPUT: None
    """
    cols = ['City', 'Time_taken(min)', 'Festival']
    df_aux = df1.loc[:, ['Time_taken(min)', 'Festival']].groupby('Festival').agg({'Time_taken(min)': ['mean', 'std']})
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()
    linhas_selecionadas = df_aux['Festival'] == 'Yes'        
    df_aux = np.round(df_aux.loc[linhas_selecionadas, 'avg_time'], 2)
    col3.metric('Média entrega festival', df_aux)
    
def media_entrega(df1):
    """
        Essa função faz uma métrica 
        INPUT: Dataframe
        OUTPUT: None
    """
    cols = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']        
    df1['distance'] = (df1.loc[:, cols].apply(lambda x: haversine((x['Restaurant_latitude'], x['Restaurant_longitude']),                                                            (x['Delivery_location_latitude'],x['Delivery_location_longitude'])), axis = 1))
    df_grouped = df1[['City', 'distance']].groupby('City').mean().reset_index()
    avg_distance = np.round(df1['distance'].mean(),2)
    col2.metric('Média Entrega', avg_distance) 
    
def entrega_std_festival(df1):
    """
        Essa função faz uma métrica 
        INPUT: Dataframe
        OUTPUT: None
    """
    df_aux = df1.loc[:, ['Time_taken(min)', 'Festival']].groupby('Festival').agg({'Time_taken(min)': ['mean', 'std']})
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()
    linhas_selecionadas = df_aux['Festival'] == 'Yes'
    df_aux = np.round(df_aux.loc[linhas_selecionadas, 'std_time'], 2)
    col1.metric('STD entrega festival', df_aux)

def entrega_media_sem_festival(df1):
    """
        Essa função faz uma métrica 
        INPUT: Dataframe
        OUTPUT: None
    """
    df_aux = df1.loc[:, ['Time_taken(min)', 'Festival']].groupby('Festival').agg({'Time_taken(min)': ['mean', 'std']})
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()
    linhas_selecionadas = df_aux['Festival'] == 'No'
    df_aux = np.round(df_aux.loc[linhas_selecionadas, 'avg_time'], 2)
    col2.metric('Média entrega sem festival ', df_aux)

def entrega_std_sem_festival(df1):
    """
        Essa função faz uma métrica 
        INPUT: Dataframe
        OUTPUT: None
    """
    df_aux = df1.loc[:, ['Time_taken(min)', 'Festival']].groupby('Festival').agg({'Time_taken(min)': ['mean', 'std']})
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()
    linhas_selecionadas = df_aux['Festival'] == 'No'
    df_aux = np.round(df_aux.loc[linhas_selecionadas, 'std_time'], 2)
    col3.metric('STD entrega sem festival', df_aux)

def tempo_medio_std_entrega_cidade(df1):
    """
        Essa função retorna uma figura (gráfico de barras)
        INPUT: Dataframe
        OUTPUT: figura
    """    
    cols = ['City', 'Time_taken(min)']
    linhas_selecionadas = df1['City'] != 'NaN'
    df_aux = df1.loc[linhas_selecionadas, cols].groupby('City').agg({'Time_taken(min)': ['mean', 'std']})
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()
    fig = go.Figure()
    fig.add_trace(go.Bar(name = 'Control', x = df_aux['City'], y = df_aux['avg_time'], error_y = dict(type = 'data', array=df_aux['std_time'])))
    fig.update_layout(barmode = 'group', width = 300)
    return fig

def tempo_medio_std_entrega_cidade_pedido(df1):
    cols = ['City', 'Time_taken(min)', 'Type_of_order']
    df_grouped = df1.loc[df1['City'] != 'NaN', :]
    df_grouped = df_grouped.loc[:, cols].groupby(['City', 'Type_of_order']).agg({'Time_taken(min)':['mean', 'std']})
    df_grouped.columns = ['avg_time', 'std_time']
    return df_grouped

def pizza(df1):
    """
        Essa função retorna uma figura (gráfico de pizza)
        INPUT: Dataframe
        OUTPUT: figura
    """ 
    cols = ['Delivery_location_latitude', 'Delivery_location_longitude', 'Restaurant_latitude', 'Restaurant_longitude']
    linhas_selecionadas = df1['City'] != 'NaN'
    df1['distance'] = df1.loc[linhas_selecionadas, cols].apply(lambda x: haversine ((x['Restaurant_latitude'], x['Restaurant_longitude']), (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis = 1)
    avg_distance = df1.loc[:, ['City', 'distance']].groupby('City').mean().reset_index()
    fig = go.Figure(data = [go.Pie(labels = avg_distance['City'], values = avg_distance['distance'], pull = [0.1, 0, 0])])
    return fig

def sunsburst(df1):
    """
        Essa função retorna uma figura (gráfico sunsburst)
        INPUT: Dataframe
        OUTPUT: figura
    """ 
    cols = ['City', 'Time_taken(min)', 'Road_traffic_density']
    df_grouped = df1.loc[(df1['City'] != 'NaN') & (df1['Road_traffic_density'] != 'NaN')]
    df_grouped = df_grouped.loc[:, cols].groupby(['City', 'Road_traffic_density']).agg({'Time_taken(min)':['mean', 'std']})
    df_grouped.columns = ['avg_time', 'std_time']
    df_grouped = df_grouped.reset_index()
    fig = px.sunburst(df_grouped, path = ['City', 'Road_traffic_density'], values = 'avg_time',
                                      color = 'std_time', color_continuous_scale = 'RdBu',
                                      color_continuous_midpoint = np.average(df_grouped['std_time'])
                                  )
    return fig
#---------------------------------INÍCIO DA ESTRUTURA LÓGICA---------------------------------#
# lendo o arquivo importado
df = pd.read_csv( 'dataset/train.csv' ) 

# limpandando dataset
df1 = clean_code(df)
#----------------------------------STREAMLIT: CONFIG-------------------------------------------#

st.set_page_config(page_title = "Visão Restaurante", page_icon = ":fork_and_knife_with_plate:", layout="wide")

#----------------------------------STREAMLIT: BARRA LATERAL------------------------------------#
st.header('Marketplace - Visão Restaurante')

image = Image.open('logo.png')
st.sidebar.image(image, width = 200)

## Labels Sidebar
st.sidebar.markdown(' # Curry Company')
st.sidebar.markdown(' ## Fastest Delivery in Town')
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

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '-', '-'])

with tab1:
    with st.container():
        st.title('Métricas Gerais')
        
        col1, col2, col3 = st.columns(3)
                
        with col1:
            entregadores_unicos = len(df1.loc[:, 'Delivery_person_ID'].unique().tolist())
            col1.metric('Entregadores únicos', entregadores_unicos)
        with col2:
            media_entrega(df1)
        with col3:
            media_entrega_festival(df1)
        
    with st.container():
        
        col1, col2, col3 = st.columns(3)
        with col1:
            entrega_std_festival(df1)
        with col2:
            entrega_media_sem_festival(df1)
        with col3:
            entrega_std_sem_festival(df1)

    
    with st.container():
        st.markdown("""---""")
        col1, col2 = st.columns(2, gap = 'large')
        with col1:
            st.markdown('##### Tempo médio e o desvio padrão de entrega por cidade')
            fig = tempo_medio_std_entrega_cidade(df1)
            st.plotly_chart(fig)
        with col2:
            st.markdown('##### Tempo médio e o desvio padrão de entrega por cidade e tipo de pedido.')
            df_grouped = tempo_medio_std_entrega_cidade_pedido(df1)
            st.dataframe(df_grouped)

    with st.container():
        st.markdown("""---""")
        col1, col2 = st.columns([1.5, 2])
        with col1:
            st.markdown('###### Distância média dos resturantes e dos locais de entrega por cidade')
            fig = pizza(df1)
            st.plotly_chart(fig,use_container_width=True)
        with col2:
            st.markdown('###### Desvio padrão de entrega por cidade e tipo de tráfego.')
            fig = sunsburst(df1)
            st.plotly_chart(fig)  
            
        st.markdown("""---""")