import streamlit as st
import requests
import zipfile
import io
import pandas as pd
import numpy as np
import os
import gdown
import tempfile
import matplotlib.pyplot as plt
import seaborn as sns

import plotly.express as px
import plotly.graph_objs as go

st.set_page_config(layout="wide")
if 'button_clicked' not in st.session_state:
    st.session_state.button_clicked = False

# Fungsi untuk mereset state button
def reset_button_state():
    st.session_state.button_clicked = False

def download_file_from_google_drive(file_id, dest_path):
    if not os.path.exists(dest_path):
        url = f"https://drive.google.com/uc?id={file_id}"
        gdown.download(url, dest_path, quiet=False)

        
file_id = '1KCY_Rr97Y1yaf-4LOE1NsZQQ2DdDBfIR'
dest_path = f'downloaded_file.zip'
download_file_from_google_drive(file_id, dest_path)


if 'df_4101.csv' not in os.listdir():
    with zipfile.ZipFile(f'downloaded_file.zip', 'r') as z:
        concatenated_df= []
        for file_name in z.namelist():
            if file_name.endswith('.xlsx') or file_name.endswith('.xls'):  # Memastikan hanya file Excel yang dibaca
                print(file_name)
                with z.open(file_name) as f:
                    # Membaca file Excel ke dalam DataFrame
                    df =   pd.read_excel(f)
                    concatenated_df.append(df) 
        pd.concat(concatenated_df, ignore_index=True).to_csv('df_4101.csv',index=False)

if 'df_4101' not in locals():
    df_4101 = pd.read_csv('df_4101.csv')
    
st.title('Dashboard - Inventaris')  

df_4101 = df_4101[~df_4101['Kode Barang'].astype(str).str.startswith('1')]
col = st.columns(3)
with col[0]:
    gudang = st.selectbox("NAMA GUDANG:", ['All'] + sorted(df_4101['Nama Gudang'].unique().tolist()), index=0, on_change=reset_button_state)
with col[1]:
    tipe = st.selectbox("PENAMBAHAN/PENGURANGAN:", ['All','Penambahan','Pengurangan'], index=0, on_change=reset_button_state)
with col[2]:
    qty_nom = st.selectbox("KUANTITAS/TOTAL BIAYA:", ['Kuantitas','Total Biaya'], index=0, on_change=reset_button_state)

list_bulan = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December']




if gudang != 'All':
    df_4101 = df_4101[df_4101['Nama Gudang']== gudang]
df_4101['Tanggal'] = pd.to_datetime(df_4101['Tanggal'], format="%d/%m/%Y")
df_4101['Month'] = df_4101['Tanggal'].dt.month_name()

if tipe != 'All':
    df_4101_1 = df_4101[df_4101['Tipe Penyesuaian']== tipe]
if tipe == 'All':
    df_4101_1 = df_4101
df_4101_1= df_4101_1.groupby(['Month','Nama Barang'])[[f'{qty_nom}']].sum().reset_index()

df_4101_1['Month'] = pd.Categorical(df_4101_1['Month'], categories=list_bulan, ordered=True)
df_4101_1 = df_4101_1.sort_values('Month')
df_4101_1 = df_4101_1.pivot(index='Nama Barang', columns='Month',values=f'{qty_nom}').reset_index().fillna('')

df_4101_2 = df_4101.groupby(['Nama Cabang','Nomor #','Kode Barang','Nama Barang','Tipe Penyesuaian'])[['Kuantitas','Total Biaya']].sum().reset_index()
df_4101_2 = df_4101_2.pivot(index=['Nama Cabang','Nomor #','Kode Barang','Nama Barang'],columns=['Tipe Penyesuaian'],values=['Kuantitas','Total Biaya']).reset_index().fillna('')
st.dataframe(df_4101_1, use_container_width=True, hide_index=True)
ia = st.multiselect("NOMOR IA:", ['All'] + sorted(df_4101_2['Nomor #'].unique().tolist()), default=['All'], on_change=reset_button_state)
if 'All' not in ia:
    df_4101_2 = df_4101_2[df_4101_2['Nomor #'].isin(ia)]

st.dataframe(df_4101_2, use_container_width=True, hide_index=True)
st.write(df_4101_2.style.set_table_styles([{'selector': 'th', 'props': [('font-size', '12pt')]}]))
