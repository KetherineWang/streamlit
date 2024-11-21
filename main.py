import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import requests
import zipfile
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from io import BytesIO
from my_plots import *

@st.cache_data
def load_name_data():
    names_files_url = 'https://www.ssa.gov/oact/babynames/names.zip'
    names_response = requests.get(names_files_url)
    with zipfile.ZipFile(BytesIO(names_response.content)) as names_files:
        dfs = []
        files = [file for file in names_files.namelist() if file.endswith('.txt')]

        for file in files:
            with names_files.open(file) as f:
                df = pd.read_csv(f, header=None)
                df.columns = ['name','sex','count']
                df['year'] = int(file[3:7])
                dfs.append(df)

        names_data = pd.concat(dfs, ignore_index=True)

    names_data['pct'] = names_data['count'] / names_data.groupby(['year', 'sex'])['count'].transform('sum')
    
    return names_data

@st.cache_data
def ohw(df):
    nunique_year = df.groupby(['name', 'sex'])['year'].nunique()
    one_hit_wonders = nunique_year[nunique_year == 1].index
    one_hit_wonder_data = df.set_index(['name', 'sex']).loc[one_hit_wonders].reset_index()
    return one_hit_wonder_data

names_data = load_name_data()
names_csv = names_data.to_csv(index=False).encode('utf-8')
ohw_data = ohw(names_data)

st.title('Social Security National Names App')

with st.sidebar:
    name_input = st.text_input('Enter a name:', 'Katherine')
    year_input = st.slider('Select a year', min_value=1880, max_value=2023, value=2001)
    n_names = st.radio('Number of names per sex', [3, 5, 10])
    st.download_button(
        label='Download data as CSV',
        data=names_csv,
        file_name='social_security_national_names.csv',
        mime='text/csv'
    )

tab1, tab2, tab3, tab4 = st.tabs(['Name Trends by Gender', 'Top Names by Year', 'Unique Names Summary', 'One-Hit Wonders Summary'])

with tab1:
    # input_name = st.text_input('Enter a name:', 'Mary')
    name_data = names_data[names_data['name']==name_input].copy()
    name_plot = px.line(name_data, x='year', y='count', color='sex')
    name_plot.update_layout(title=f'"{name_input}" Trends by Gender')
    st.plotly_chart(name_plot)

with tab2:
    # year_input = st.slider('Year', min_value=1880, max_value=2023, value=2001)
    year_plot = top_names_plot(names_data, year=year_input, n=n_names)
    st.plotly_chart(year_plot)

with tab3:
    st.write(f'Unique Names Summary Table in "{year_input}"')
    output_table = unique_names_summary(names_data, year=year_input)
    st.data_editor(output_table)

with tab4:
    st.write(f'One-Hit Wonders Summary Statistics in "{year_input}"')
    one_hit_wonders(ohw_data, year=year_input)