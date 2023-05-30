import streamlit as st
import json
import pandas as pd
import os


st.header('Merge Adobe info and json, only for news due to a lot of hard coded edge cases')

df_csv = st.file_uploader("Upload csv", accept_multiple_files=False)

json_file = st.file_uploader("Upload json", accept_multiple_files=False)

if df_csv is not None and json_file is not None:

    df = pd.read_csv(df_csv,index_col = False, dtype={'section': str}) # new dtype
    st.write('dtypes')
    st.write(df.dtypes)
    
    df['section'] = df['section'].astype(str)
    
    st.write('dtypes after section to string')
    st.write(df.dtypes)
    
    df['date'] = df['date'].astype(str)

    st.write('csv data')
    st.dataframe(df)



    data = json.load(json_file)



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

            if section.lower() == 'watch current affairs programs':
                    section = 'current affairs video'

            elif section.lower() == 'carousel':
                section = 'header carousel' #'herocarousel'

            #elif section.lower() == 'sbs news in mandarin':
                #section = 'sbs-news-in-mandarin'

            #elif section.lower() == 'sbs news in arabic' and int(day_scrape['Date']) <= 20230128: 
                #section = 'sbs-news-in-arabic'

            elif section.lower() == 'sbs news in arabic' and int(day_scrape['Date']) > 20230128: 
                section = 'Arabic News and Current Affairs'

            elif section.lower() == '#alwayswasalwayswillbe':
                section = 'Always Was Always Will Be'               

            elif section.lower() == 'celebrate lunar new year with sbs #lnysbs':
                section = 'celebrate lunar new year with sbs' 

            elif section.lower() == 'sbs cultural atlas' and int(day_scrape['Date']) < 20230129:
                section = 'sbs cultural atlas' 

            elif section.lower() == 'january 26' and int(day_scrape['Date']) <= 20230128:
                section = 'Jan 26'

            elif section.lower() == 'january 26' and int(day_scrape['Date']) > 20230128 and int(day_scrape['Date']) < 20230226:
                section = 'Jan 26'

            elif section.lower() == 'january 26' and int(day_scrape['Date']) >= 20230226:
                section = 'Jan 26'

            elif section.lower() == 'sbs cultural atlas' and int(day_scrape['Date']) >= 20230129 and int(day_scrape['Date']) <= 20230204:
                continue

            elif section.lower() == ' sbs news podcast playlist' and int(day_scrape['Date']) < 20230226: # this might  be incorrect
                section = 'news podcasts' 

            elif section.lower() == 'sbs news podcast playlist' and int(day_scrape['Date']) >= 20230226: # this might  be incorrect
                section = 'news podcasts' 

            elif section.lower() == 'sbs world watch':
                continue

            elif section.lower() == 'watch news programs':
                continue                 

            elif 'copyright' in section.lower():
                continue

            elif 'sbs home' in section.lower():
                continue           

            elif 'news straight to your inbox' in section.lower():
                continue   
            
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
        file_name='matched_news.csv',
        mime='text/csv',
    )




