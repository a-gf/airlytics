import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
from wordcloud import WordCloud #, STOPWORDS
from sklearn.feature_extraction.text import CountVectorizer
from nltk.corpus import stopwords
import nltk

# st.title("Experiencia de usuario en diferentes aerolíneas 🛫")
# st.sidebar.title("Experiencia de usuario en diferentes aerolíneas 🛫")

st.title("Airlytics 🛫")
st.text("Compare la experiencia en diferentes aerolíneas")
st.sidebar.title("Airlytics 🛫")
# st.sidebar.text("Compare la experiencia en diferentes aerolíneas")

DATA_URL = "data/airline-reviews-test.csv"
archivo_comentarios = "data/comentarios-test.csv"

@st.cache_data
def load_data():
    data = pd.read_csv(DATA_URL)
    return data

# import chardet
#
# with open(archivo_comentarios, "rb") as f:
#     resultado = chardet.detect(f.read())
#
# st.text(resultado["encoding"])

# @st.cache_data
# def cargar_comentarios():
#     comentarios = pd.read_csv(archivo_comentarios, usecols=[0, 1, 2], encoding="utf-8", errors="replace")
#     return comentarios

data = load_data()
# comentarios = cargar_comentarios()

lista_aerolineas = data['Airline'].unique()

#st.markdown("### Las aerolíneas tenidas en cuenta son las siguientes:")
#for airline in lista_aerolineas:
#    st.markdown(f"- {airline}")

st.markdown("### Lista de aerolíneas:")

# Crear columnas en la interfaz
col1, col2 = st.columns(2)

# Dividir las aerolíneas en dos partes
midpoint = len(lista_aerolineas) // 2
aerolineas_col1 = lista_aerolineas[:midpoint]
aerolineas_col2 = lista_aerolineas[midpoint:]

# Mostrar las aerolíneas en las columnas
with col1:
    for airline in aerolineas_col1:
        st.markdown(f"- {airline}")

with col2:
    for airline in aerolineas_col2:
        st.markdown(f"- {airline}")


st.text(" ")
st.sidebar.subheader('Número de reseñas por aerolínea')
if not st.sidebar.checkbox("Cerrar gráfico", True, key="numero-resenas"):
    st.markdown("### Número de reseñas por aerolínea")
    numero_reviews = data['Airline'].value_counts()

    numero_reviews = numero_reviews.reset_index()
    numero_reviews.columns = ['Airline', 'Reviews']
    numero_reviews = numero_reviews.sort_values('Reviews', ascending=False)

    fig = px.bar(numero_reviews, y='Airline', x='Reviews',
                 #title="Número de reseñas por aerolínea",
                 labels={'Airline': 'Aerolínea', 'Reviews': 'Número de reseñas'},
                 color='Airline',
                 color_discrete_sequence=px.colors.qualitative.Set2,
                 orientation='h')
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig)


# ## Gráfico de recomendación por aerolíneas
st.sidebar.subheader('Recomendación por aerolínea')
if not st.sidebar.checkbox("Cerrar gráfico", True, key="recomendacion-aerolinea"):
    ## Gráfico de porcentaje de recomendación por aerolínea
    st.markdown("### Recomendación por aerolínea")

    # Agrupar y calcular el total
    recommended_data = data.groupby(['Airline', 'Recommended']).size().reset_index(name='Count')

    # Crear una tabla pivote
    pivot_data = recommended_data.pivot(index='Airline', columns='Recommended', values='Count').fillna(0).reset_index()

    # Asegurarse de que las columnas estén en minúsculas
    pivot_data.columns = pivot_data.columns.str.lower()

    # Calcular el total y los porcentajes
    pivot_data['total'] = pivot_data['yes'] + pivot_data['no']
    pivot_data['% Sí'] = (pivot_data['yes'] / pivot_data['total']) * 100
    pivot_data['% No'] = (pivot_data['no'] / pivot_data['total']) * 100

    # Ordenar por porcentaje de recomendación positiva
    pivot_data = pivot_data.sort_values(by='% Sí', ascending=False)

    # Renombrar las columnas para la leyenda
    pivot_data.rename(columns={'% Sí': 'Porcentaje Sí', '% No': 'Porcentaje No'}, inplace=True)

    # Crear el gráfico
    fig_recommendation = px.bar(
        pivot_data,
        x='airline',
        y=['Porcentaje Sí', 'Porcentaje No'],
        labels={'value': 'Porcentaje', 'variable': 'Recomendada', 'airline':'Aerolínea'},
        barmode='group',
        color_discrete_sequence=px.colors.qualitative.Pastel,
        #title="Porcentaje de recomendación por aerolínea"
    )

    # Mostrar el gráfico en Streamlit
    st.plotly_chart(fig_recommendation)

# st.markdown("### Comparación de recomendaciones por aerolínea")
#
# recommended_data = data.groupby(['Airline', 'Recommended']).size().reset_index(name='Count')
#
# pivot_data = recommended_data.pivot(index='Airline', columns='Recommended', values='Count').fillna(0).reset_index()
#
# pivot_data['Total'] = pivot_data['yes'] + pivot_data['no']
# pivot_data = pivot_data.sort_values(by='Total', ascending=False)
#
# # Renombrar columnas para la leyenda
# pivot_data.rename(columns={'yes': 'Sí', 'no': 'No'}, inplace=True)
#
# fig_recommendation = px.bar(
#     pivot_data,
#     x='Airline',
#     y=['Sí', 'No'],
#     #title="Recomendación de aerolíneas",
#     labels={'value': 'Número de recomendaciones', 'variable': 'Recomendada'},
#     barmode='group',
#     color_discrete_sequence=px.colors.qualitative.Pastel
# )
#
# st.plotly_chart(fig_recommendation)



### Puntajes internos
st.sidebar.subheader("Desglose de puntuaciones por aerolínea")
choice = st.sidebar.multiselect('Elige la aerolínea',lista_aerolineas, key='multiselect')

#to avoid an error
#if len(choice)>0:
#    choice_data = data[data.airline.isin(choice)]
#    fig_choice = px.histogram(choice_data, x='airline', y='airline_sentiment', histfunc='count', color= 'airline_sentiment', facet_col='airline_sentiment', labels={'airline_sentiment':'tweets'}, height=600, width=800)
#    st.plotly_chart(fig_choice)

if len(choice) > 0:

    # Título de sección
    st.subheader("Desglose de puntuaciones por aerolínea")

    # Filtrar los datos según las aerolíneas seleccionadas
    choice_data = data[data['Airline'].isin(choice)]

    # Calcular los promedios de las columnas de interés para cada aerolínea
    avg_scores = choice_data.groupby('Airline')[['Seat Comfort', 'Staff Service', 'Food & Beverages',
                                                 'Inflight Entertainment', 'Value For Money',
                                                 ]].mean().reset_index()

    # Renombrar las columnas para la leyenda
    avg_scores.rename(columns={
        'Seat Comfort': 'Comodidad del Asiento',
        'Staff Service': 'Servicio del Personal',
        'Food & Beverages': 'Comida y Bebidas',
        'Inflight Entertainment': 'Entretenimiento a Bordo',
        'Value For Money': 'Relación Calidad-Precio',
        'Overall Rating': 'Calificación General'
    }, inplace=True)

    # Crear el gráfico de columnas
    fig_choice = px.bar(
        avg_scores,
        x='Airline',
        y=['Comodidad del Asiento', 'Servicio del Personal', 'Comida y Bebidas',
           'Entretenimiento a Bordo', 'Relación Calidad-Precio'],
        #title="Promedio de puntuaciones por categoría",
        labels={'value': 'Promedio', 'variable': 'Categoría', 'Airline':'Aerolínea'},
        barmode='group',  # Agrupar las barras
        color_discrete_sequence=px.colors.qualitative.Pastel
    )

    # Mostrar el gráfico en Streamlit
    st.plotly_chart(fig_choice)


# st.markdown("### Puntuación general según la clase y aerolínea")
#
# # Verificar que las columnas necesarias existan en los datos
# if 'Overall Rating' in data.columns and 'Class' in data.columns:
#     # Calcular el promedio de puntuación general por aerolínea y clase
#     rating_data = data.groupby(['Airline', 'Class'])['Overall Rating'].mean().reset_index()
#
#     # Crear el gráfico de barras agrupadas
#     fig_rating = px.bar(
#         rating_data,
#         x='Airline',
#         y='Overall Rating',
#         color='Class',
#         barmode='group',
#         title="Puntuación general según la clase y aerolínea",
#         labels={
#             'Overall Rating': 'Puntuación General',
#             'Class': 'Clase',
#             'Airline': 'Aerolínea'
#         },
#         color_discrete_sequence=px.colors.qualitative.Pastel
#     )
#
#     # Mostrar el gráfico en Streamlit
#     st.plotly_chart(fig_rating)
# else:
#     st.error("Las columnas necesarias ('Overall Rating', 'Class') no están presentes en los datos.")



# Verificar que las columnas necesarias existan en los datos
if 'Overall Rating' in data.columns and 'Class' in data.columns:
    # Crear un diccionario para las traducciones de las clases
    class_translations = {
        "Business Class": "Clase Ejecutiva",
        "Economic Class": "Clase Económica",
        "First Class": "Primera Clase",
        "Premium Economy": "Premium Económica"
    }

    # Sidebar con subheader
    st.sidebar.subheader("Puntuación general según la clase y aerolínea")

    # Agregar la casilla de control para mostrar/ocultar el gráfico
    show_chart = st.sidebar.checkbox("Cerrar gráfico", value=True)

    # Obtener las clases únicas del conjunto de datos
    available_classes = data['Class'].unique()

    # Agregar el filtro de clase en el sidebar
    selected_class = st.sidebar.selectbox(
        "Selecciona una clase",
        options=available_classes,
        format_func=lambda x: class_translations.get(x, x)  # Traducción al español
    )

    # Si la casilla para mostrar el gráfico está marcada
    if not show_chart:
        st.markdown("### Puntuación general según la clase y aerolínea")
        # Filtrar los datos según la clase seleccionada
        filtered_data = data[data['Class'] == selected_class]

        # Calcular el promedio de puntuación general por aerolínea
        rating_data = filtered_data.groupby(['Airline', 'Class'])['Overall Rating'].mean().reset_index()

        # Crear el gráfico de barras agrupadas
        fig_rating = px.bar(
            rating_data,
            x='Airline',
            y='Overall Rating',
            color='Class',
            barmode='group',
            title=f"{class_translations.get(selected_class, selected_class)}",
            labels={
                'Overall Rating': 'Puntuación General',
                'Class': 'Clase',
                'Airline': 'Aerolínea'
            },
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        # Quitar la leyenda del gráfico
        fig_rating.update_layout(showlegend=False)
        # Mostrar el gráfico en Streamlit
        st.plotly_chart(fig_rating)
  #  else:
 #       st.info("El gráfico está cerrado. Marca la opción 'Mostrar gráfico' para visualizarlo.")

#else:
#    st.error("Las columnas necesarias ('Overall Rating', 'Class') no están presentes en los datos.")


#### Nube

# # Configuración del sidebar
# st.sidebar.subheader("Nube de palabras")
# sentimiento = st.sidebar.radio('Elija el sentimiento para la nube: ', ('positivo', 'negativo'))
#
# if not st.sidebar.checkbox("Cerrar", True, key="3"):
#     st.header(f"Nube de palabras para el sentimiento {sentimiento}")
#
#     # Mapear sentimientos a valores en la columna 'Recommended'
#     if sentimiento == 'positivo':
#         df = data[data['Recommended'] == 'yes']
#     else:
#         df = data[data['Recommended'] == 'no']
#
#     # Procesar las palabras
#     words = ' '.join(data['Title'])  # Ajusta 'text' al nombre correcto de tu columna de texto
#     processed_words = ' '.join(
#         [word for word in words.split() if 'http' not in word and not word.startswith('@') and word != 'RT'])
#
#     # Generar la nube de palabras
#     wordcloud = WordCloud(stopwords=STOPWORDS, background_color='white', height=640, width=800).generate(
#         processed_words)
#
#     # Crear la figura de Matplotlib
#     fig, ax = plt.subplots()
#     ax.imshow(wordcloud, interpolation='bilinear')
#     ax.axis('off')  # Eliminar los ejes
#
#     # Mostrar la figura en Streamlit
#     st.pyplot(fig)

#from deep_translator import GoogleTranslator

#### Nube

# # Configuración del sidebar
# st.sidebar.subheader("Nube de palabras")
# # Sidebar para seleccionar el sentimiento
# sentimiento_seleccionado = st.sidebar.radio("Selecciona el Sentimiento", ("Positivo", "Negativo"))
#
# # Descargar las stopwords en español de nltk (si no están descargadas)
# nltk.download('stopwords')
# spanish_stopwords = stopwords.words('spanish')
#
# # Filtrar comentarios según el sentimiento seleccionado
# comentarios_filtrados = comentarios[comentarios['Sentimiento'] == sentimiento_seleccionado]
#
# # Convertir los textos a una sola cadena
# words = ' '.join(comentarios_filtrados['Resenas'].fillna('').astype(str))
#
# # Preprocesar eliminando URLs, menciones, etc.
# processed_words = ' '.join(
#     [word for word in words.split() if 'http' not in word and not word.startswith('@') and word != 'RT']
# )
#
# if not st.sidebar.checkbox("Cerrar gráfico", True, key="3"):
#
#     st.markdown(f"### Nube de palabras para el sentimiento {sentimiento_seleccionado}")
#
#     # Usar el vectorizador con las palabras de parada en español
#     vectorizer = CountVectorizer(stop_words=spanish_stopwords)
#     word_counts = vectorizer.fit_transform([processed_words])
#     word_frequencies = dict(zip(vectorizer.get_feature_names_out(), word_counts.toarray()[0]))
#
#     # Generar la nube de palabras basada en frecuencias
#     wordcloud = WordCloud(stopwords=spanish_stopwords, background_color='white', height=640, width=800).generate_from_frequencies(word_frequencies)
#
#     # Crear la figura de Matplotlib
#     fig, ax = plt.subplots()
#     ax.imshow(wordcloud, interpolation='bilinear')
#     ax.axis('off')  # Eliminar los ejes
#
#     # Mostrar la figura
#     st.pyplot(fig)
