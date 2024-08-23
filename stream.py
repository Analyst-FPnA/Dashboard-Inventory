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

def download_file_from_google_drive(file_id, dest_path):
    if not os.path.exists(dest_path):
        url = f"https://drive.google.com/uc?id={file_id}"
        gdown.download(url, dest_path, quiet=False)

        
file_id = '1gm-_ZJ1Uitq2-f5-ETuO2PAXkOzzfjZM'
dest_path = f'downloaded_file.zip'
download_file_from_google_drive(file_id, dest_path)


if not os.path.exists('full_4401.csv'):
    with zipfile.ZipFile(f'downloaded_file.zip', 'r') as z:
        concatenated_df= []
        for file_name in z.namelist():
            if file_name.endswith('.xlsx') or file_name.endswith('.xls'):  # Memastikan hanya file Excel yang dibaca
                print(file_name)
                with z.open(file_name) as f:
                    # Membaca file Excel ke dalam DataFrame
                    df_4101 =   pd.read_excel(f, header=4)
                    df_4101['Nama Cabang'] = df_4101['Nama Cabang'].astype(str)
                    
                    data_remove = ["Nama Cabang", "GiS", "#41.01", "Dari", "Cabang"]
                    df_4101a = df_4101[~df_4101['Nama Cabang'].str.startswith(tuple(data_remove))]
                    
                    df_4101a['Nama Cabang'] = df_4101a['Nama Cabang'].replace('nan', "")
                    
                    df_4101a['Keterangan'] = df_4101a['Keterangan'].fillna("").astype(str)
                    
                    df_4101a['Keterangan'] = df_4101a.groupby((df_4101a['Nomor #'].notna()).cumsum())['Keterangan'].transform(lambda x: ' '.join(x))
                    
                    df_4101a = df_4101a.loc[:, ~df_4101.columns.str.startswith('Unnamed')]
                    
                    df_4101a = df_4101a[df_4101a['Nama Cabang'] != ""]
                    
                    df_4101a['Tanggal'] = pd.to_datetime(df_4101a['Tanggal'], format='%d/%m/%Y %H:%M:%S')
                    
                    df_4101a['Tanggal'] = df_4101a['Tanggal'].dt.strftime('%d/%m/%Y')
                    concatenated_df.append(df_4101a) 
        pd.concat(concatenated_df, ignore_index=True).to_csv('full_4401.csv',index=False)

if 'df_4401' not in locals():
    df_4401 = pd.read_csv('full_4401.csv')
  
list_bulan = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December']

df_4101_1 = df_4401[~df_4401['Kode Barang'].str.startswith('1')]
df_4101_1['Tanggal'] = pd.to_datetime(df_4101_1['Tanggal'], format="%d/%m/%Y")
df_4101_1['Month'] = df_4101_1['Tanggal'].dt.month_name()
df_4101_1 = df_4101_1.groupby(['Month','Nama Barang'])[['Kuantitas']].sum().reset_index()
df_4101_1['Month'] = pd.Categorical(df_4101_1['Month'], categories=list_bulan, ordered=True)
df_4101_1 = df_4101_1.sort_values('Month')
df_4101_1 = df_4101.pivot(index='Nama Barang', columns='Month',values='Kuantitas').reset_index().fillna('')
st.dataframe(df_4401_1, use_container_width=True, hide_index=True)

df_4101_2 = df_4401[~df_4401['Kode Barang'].str.startswith('1')]
df_4101_2['Tanggal'] = pd.to_datetime(df_4101_2['Tanggal'], format="%d/%m/%Y")
df_4101_2['Month'] = df_4101_2['Tanggal'].dt.month_name()
df_4101_2 = df_4101_2.groupby(['Nama Cabang','Nomor #','Kode Barang','Nama Barang','Tipe Penyesuaian'])[['Kuantitas']].sum().reset_index()
df_4101_2 = df_4101_2.pivot(index=['Nama Cabang','Nomor #','Kode Barang','Nama Barang'],columns='Tipe Penyesuaian',values='Kuantitas').reset_index().fillna('')
st.dataframe(df_4101_2, use_container_width=True, hide_index=True)
