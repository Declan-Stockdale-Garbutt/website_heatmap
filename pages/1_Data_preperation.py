import streamlit as st
import pandas as pd
import numpy as np
import os

st.header('Process Adobe Analytics data')

st.write("")
uploaded_files = st.file_uploader("Upload CSV Files", type="csv", accept_multiple_files=True)


if len(uploaded_files) != 0:
    ##############
    df_combined = pd.DataFrame()

    for file_path in uploaded_files:
        #print(file_path)
        df = pd.read_csv(file_path,skiprows=12)
        df = df.rename(columns={'Unnamed: 0':'section'})  
        df = df.iloc[1:]
        
        # melt
        melted_df = pd.melt(df, id_vars='section', var_name='date', value_name='views')
        # concat
        df_combined = pd.concat([df_combined,melted_df], axis = 0, ignore_index=True)

    # drop 0 values
    df_combined = df_combined.drop(df_combined[df_combined['views'] == 0].index)

    # change date formatting
    df_combined['date'] = pd.to_datetime(df_combined['date'], format='%b %d, %Y')

    # Convert date column to string with YYYYMMDD format
    df_combined['date'] = df_combined['date'].dt.strftime('%Y%m%d').astype(str)

    df_combined['section'] = df_combined['section'].str.lower()

    # fix row stuff
    df_combined['section'] = df_combined['section'].replace('sbs new podcast playlist', 'sbs news podcast playlist')

    # convert to utf 8 (removes weird html issues)
    df_combined['section'] = df_combined['section'].str.encode('utf-8')
    

    # download
    st.download_button(
        label="Download data as CSV",
        data=df_combined.to_csv(index=False),#.encode('utf-8'),
        file_name='combined.csv',
        mime='text/csv',
    )