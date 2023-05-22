import streamlit as st
import json
import pandas as pd
import os


st.header('Merge Adobe info and json, only for sport due to a lot of hard coded edge cases')

df_csv = st.file_uploader("Upload csv", accept_multiple_files=False, type = 'csv')
df = pd.read_csv(df_csv,index_col = False)
df['date'] = df['date'].astype(str)

st.write('csv data')
st.dataframe(df)


json_file = st.file_uploader("Upload json", accept_multiple_files=False,type = 'json')
data = json.load(json_file)

if df_csv is not None and json_file is not None:

    # do the matching

    df_total =  pd.DataFrame({
            'Date'                : pd.Series(dtype='str'),
            'Section'             : pd.Series(dtype='str'),
            'Position'            : pd.Series(dtype='int'),
            'Page_views'          : pd.Series(dtype='int'),
            'Matched'             : pd.Series(dtype='int')
    })

    unmatched_list = []
    unmatched = 0
    matched = 0
    for day_scrape in data[3:]:

        current_position = 1

        for section in day_scrape['Results']:

            if 'copyright' in section.lower():
                continue

            elif 'sbs home' in section.lower():
                continue   

            elif section.lower() == 'stay informed with sbs news':
                continue

            # This might have to be multiple fields
            elif section.lower() == 'indigenous news in sport on nitv':
                #section = 'indigenous news in sport on nitv ->doesnt exist in most files' 
                section = 'indigenous news in sport on nitv'

            elif section.lower() == 'watch sport programs':
                #section = 'watch sport programs ->skip is mostly 0 for when it does match' 
                section = 'watch sport programs'

            elif section.lower() == 'carousel':
                section = 'header carousel'

            elif section.lower() == '2023 dakar rally on sbs':
                section = 'Dakar Rally 2023'  
            
            filtered_df_init = df[df['date'] == day_scrape['Date']]#) & (df['section'] == section.lower())].
            filtered_df_final = filtered_df_init[filtered_df_init['section'] == section.lower()]


            #st.write('filtered_df_init test')
            #st.dataframe(filtered_df_final)

            #st.write('views = ',filtered_df_final['views'])
            #st.write('views test = ',filtered_df_final['views'].iloc[0])

            #print(section, day_scrape['Date'])
            #print(filtered_df)
            
            #st.write(f"looking for {day_scrape['Date']}")
            #st.write(f"looking for {filtered_df_final['section']}")
            #st.write(filtered_df)
            
            if len(filtered_df_final['views']) == 0:
                unmatched +=1
                unmatched_list.append((section.lower() ,day_scrape['Date']))
                was_matched = 0
                page_views = 0
            else:
                matched +=1
                was_matched = 1
                page_views = filtered_df_final['views'].iloc[0]


            # create row of data
            new_row =  [{'Date'       :     day_scrape['Date'],
                        'Section'    :     section,
                        'Position'   :     current_position,
                        "Page_views" :     page_views,
                        'Matched'    :     was_matched}]
            
            
            # this is new
            new_row_df = pd.DataFrame(data = new_row)
            
            
            #df_total = df_total.append(new_row, ignore_index=True)
            df_total = pd.concat([df_total, new_row_df], ignore_index=True)
            current_position +=1


st.write(f'Number of matches {matched}')
st.write(f"Number unmatched  {unmatched}")

st.write('These were missing')
unmatched_list_df = pd.DataFrame(unmatched_list)
st.dataframe(unmatched_list_df)


# download
st.download_button(
    label="Download data as CSV",
    data=df_total.to_csv(index=False),#.encode('utf-8'),
    file_name='matched_sport.csv',
    mime='text/csv',
)




