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
def highlight_header(x):
    """
    Meng-highlight header tabel dengan warna merah.
    
    Parameters:
    - x: DataFrame yang akan diterapkan styling
    
    Returns:
    - DataFrame dengan styling untuk header
    """
    # CSS styling untuk header
    header_color = 'background-color: #FF4B4B; color: white;'  # Warna merah dengan teks putih
    df_styles = pd.DataFrame('', index=x.index, columns=x.columns)
    
    # Memberikan warna khusus pada header
    df_styles.loc[x.columns, :] = header_color

    return df_styles
    
if 'button_clicked' not in st.session_state:
    st.session_state.button_clicked = False

# Fungsi untuk mereset state button
def reset_button_state():
    st.session_state.button_clicked = False

def download_file_from_google_drive(file_id, dest_path):
    if not os.path.exists(dest_path):
        url = f"https://drive.google.com/uc?id={file_id}"
        gdown.download(url, dest_path, quiet=False)
def highlight_header(s):
    return ['background-color: red; color: white'] * len(s)

        
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
    
st.title('Inventaris Control')  

df_4101 = df_4101[~df_4101['Kode Barang'].astype(str).str.startswith('1')]
col = st.columns(3)
with col[0]:
    cabang = st.selectbox("NAMA CABANG:", sorted(df_4101['Nama Cabang'].unique().tolist()), index=0, on_change=reset_button_state)
with col[1]:
    tipe = st.selectbox("PENAMBAHAN/PENGURANGAN:", ['Penambahan','Pengurangan'], index=1, on_change=reset_button_state)
with col[2]:
    qty_nom = st.selectbox("KUANTITAS/TOTAL BIAYA:", ['Kuantitas','Total Biaya'], index=0, on_change=reset_button_state)

list_bulan = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December']


df_4101 = df_4101[(df_4101['Nama Cabang']==cabang) & (df_4101['Kategori'].isin(['00.COST', '21.COST.ASSET', '20.ASSET.ASSET']))]
df_4101['Tanggal'] = pd.to_datetime(df_4101['Tanggal'], format="%d/%m/%Y")
df_4101['Month'] = df_4101['Tanggal'].dt.month_name()
month = df_4101['Month'].unique().tolist()

df_4101 = df_4101[(df_4101['Nama Cabang']== cabang) & (df_4101['Tipe Penyesuaian']== tipe)]
df_4101_1 = df_4101.groupby(['Month','Nama Barang'])[[f'{qty_nom}']].sum().reset_index()

df_4101_1['Month'] = pd.Categorical(df_4101_1['Month'], categories=list_bulan, ordered=True)
df_4101_1 = df_4101_1.sort_values('Month')
df_4101_1 = df_4101_1.pivot(index='Nama Barang', columns='Month',values=f'{qty_nom}').reset_index().fillna(0)
#df_4101_1.iloc[:,1:] = df_4101_1.iloc[:,1:].applymap(lambda x: '' if x=='' else f'{x:.0f}')
df_4101_1['Total']=df_4101_1.iloc[:,2:].sum(axis=1)

pd.options.display.float_format = '{:,.0f}'.format
df_4101_2 = df_4101.groupby(['Nama Cabang','Nomor #','Kode Barang','Nama Barang','Tipe Penyesuaian'])[['Kuantitas','Total Biaya']].sum().reset_index()
df_4101_2 = df_4101_2.pivot(index=['Nama Cabang','Nomor #','Kode Barang','Nama Barang'],columns=['Tipe Penyesuaian'],values=['Kuantitas','Total Biaya']).reset_index().fillna('')
st.dataframe(df_4101_1.style.apply(highlight_header, axis=None), use_container_width=True, hide_index=True)

all_month = []
for i in month:
    all_month.append(pd.DataFrame(df_4101[df_4101['Month']==f'{i}']['Nomor #'].unique(),columns=[f'{i}']))
df_ia = pd.concat(all_month,axis=1, ignore_index=True)
for i, x in enumerate(month):
    df_ia = df_ia.rename(columns={i:x})
df_ia['Nama Cabang'] = cabang
df_ia = df_ia[[df_ia.columns[-1]]+list(df_ia.columns[:-1])].fillna('')
st.dataframe(df_ia, use_container_width=True, hide_index=True)

list_ia = sorted(df_4101_2['Nomor #'].unique().tolist())
ia = st.selectbox("NOMOR IA:",list_ia ,index=len(list_ia)-1, on_change=reset_button_state)
df_4101_2 = df_4101_2[df_4101_2['Nomor #'] == ia].drop(columns='Nomor #')
df_4101_2.columns = ['_'.join(col).strip() for col in df_4101_2.columns.values]
df_4101_2.iloc[:,3:] = df_4101_2.iloc[:,3:].applymap(lambda x: '' if x=='' else f'{x:,.0f}')
st.dataframe(df_4101_2, use_container_width=True, hide_index=True)
