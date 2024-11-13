import numpy as np
import pandas as pd
import zipfile
import plotly.express as px
import matplotlib.pyplot as plt
import requests
from io import BytesIO
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from my_plots import *
import streamlit as st

@st.cache_data
def load_name_data():
    names_file = 'https://www.ssa.gov/oact/babynames/names.zip'
    response = requests.get(names_file)
    with zipfile.ZipFile(BytesIO(response.content)) as z:
        dfs = []
        files = [file for file in z.namelist() if file.endswith('.txt')]
        for file in files:
            with z.open(file) as f:
                df = pd.read_csv(f, header=None)
                df.columns = ['name','sex','count']
                df['year'] = int(file[3:7])
                dfs.append(df)
        data = pd.concat(dfs, ignore_index=True)
    data['pct'] = data['count'] / data.groupby(['year', 'sex'])['count'].transform('sum')
    return data

@st.cache_data
def ohw(df):
    nunique_year = df.groupby(['name', 'sex'])['year'].nunique()
    one_hit_wonders = nunique_year[nunique_year == 1].index
    one_hit_wonder_data = df.set_index(['name', 'sex']).loc[one_hit_wonders].reset_index()
    return one_hit_wonder_data

data = load_name_data()
ohw_data = ohw(data)


#Actually Making the App
st.title("My Cool Name App")

with st.sidebar:
    input_name = st.text_input('Enter a name:', 'Mary')
    year_input = st.slider('year', min_value=1880, max_value = 2023, value=2000)
    n_names = st.radio('Number of names per sex', [3, 5, 10])

tab1, tab2, tab3, tab4 = st.tabs(["Names", "Years", "Sex Dist.", "Top Names by Decade"])
with tab1:
    name_data = data[data['name']==input_name].copy()
    fig=px.line(name_data, x='year', y='count', color='sex')
    st.plotly_chart(fig)

    if not name_data.empty:
        most_common_year = name_data.loc[name_data['count'].idxmax()]
        year_most_common = most_common_year['year']
        max_count = most_common_year['count']
        
        # Display the result below the graph
        st.write(f"The name **{input_name}** was most common in **{year_most_common}** with **{max_count}** uses.")
    else:
        st.write(f"The name **{input_name}** does not have any data.")
with tab2:
    fig2 = top_names_plot(data, year=year_input, n=n_names)
    st.plotly_chart(fig2)

    st.write('Unique Names Table')
    output_table = unique_names_summary(data, 2000)
    st.dataframe(output_table)
with tab3:
    fig3 = name_trend_plot(data, name=input_name, width=800, height=600)
    st.plotly_chart(fig3)
with tab4:
    # Create two columns
    col1, col2 = st.columns([1, 3])

    # Place the decade selector in the first column
    with col1:
        selected_decade = col1.selectbox("Select a decade:", range(1880, 2020, 10))

    # Display the top names chart in the second column
    with col2:
        # Filter the data for the selected decade
        decade_data = data[(data['year'] >= selected_decade) & (data['year'] < selected_decade + 10)]
        top_names_decade = decade_data.groupby('name')['count'].sum().nlargest(10).reset_index()

        # Create a bar chart of the top names for the selected decade
        fig_decade = px.bar(top_names_decade, x='name', y='count', title=f"Top 10 Names in the {selected_decade}s")
        col2.plotly_chart(fig_decade)




