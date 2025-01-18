import streamlit as st
import pandas as pd
import plotly.express as px

st.title("Proyecto de comparación de la experiencia en diferentes aerolineas")
st.sidebar.title("Proyecto de comparación de la experiencia en diferentes aerolineas")

DATA_URL = "data/airlines_reviews.csv"

@st.cache_data
def load_data():
    data = pd.read_csv(DATA_URL)
    return data

data = load_data()


lista_aerolineas = data['Airline'].unique()

st.markdown("### Las aerolíneas tenidas en cuenta son las siguientes:")
for airline in lista_aerolineas:
    st.markdown(f"- {airline}")


st.markdown("### Número de reseñas por aerolinea")
numero_reviews = data['Airline'].value_counts()
st.write(numero_reviews)

numero_reviews = numero_reviews.reset_index()
numero_reviews.columns = ['Airline', 'Reviews']
numero_reviews = numero_reviews.sort_values('Reviews', ascending=False)

fig = px.bar(numero_reviews, y='Airline', x='Reviews',
             title="Número de reseñas por aerolínea",
             labels={'Airline': 'Aerolínea', 'Reviews': 'Número de reseñas'},
             color='Airline',
             color_discrete_sequence=px.colors.qualitative.Set2,
             orientation='h')
fig.update_layout(showlegend=False)
st.plotly_chart(fig)