import streamlit as st
import os
import json
import datetime
import plotly.express as px
import project_utils
import pandas as pd
import datetime
import ast



st.header('Data visualizations')

df_csv = st.file_uploader("Upload matched csv", accept_multiple_files=False, type = 'csv')

df = pd.read_csv(df_csv,index_col = False)
# convert date to string
df['Date'] = df['Date'].astype(str)

st.subheader('Look at the df')
st.dataframe(df)

# only get non missing values that didn't match
df_matched = df.query('Matched == 1')

######################################################################################
st.markdown("""---""")
st.subheader('Average of each section by Position as it appears on SBS website')
st.write('Not entirely useful as key news events (Covid, World cup, jan 26 etc) can alter the position of other sections')

# convert the views column to numeric data type
df['Page_views'] = pd.to_numeric(df['Page_views'], errors='coerce')
# do aggregating stuff
avg_section = df_matched.groupby(['Position']).agg({'Page_views': ['count', 'sum', 'mean']})
# flatten the column names
avg_section.columns = ['_'.join(col).strip() for col in avg_section.columns.values]
# reset the index to turn the groupby result into a dataframe
avg_section = avg_section.reset_index()
# round the views_mean column to one decimal place
avg_section['Page_views_mean'] = avg_section['Page_views_mean'].round(1)
# sort the dataframe by views_mean
avg_section = avg_section.sort_values('Page_views_mean', ascending=False)
# write df
st.write(avg_section)

######################################################################################
st.markdown("""---""")
st.subheader('Average of each section by name')

# convert the views column to numeric data type
df_matched['Page_views'] = pd.to_numeric(df_matched['Page_views'], errors='coerce')
# do aggregating stuff
avg_section = df_matched.groupby(['Section']).agg({'Page_views': ['count', 'sum', 'mean']})
# flatten the column names
avg_section.columns = ['_'.join(col).strip() for col in avg_section.columns.values]
# reset the index to turn the groupby result into a dataframe
avg_section = avg_section.reset_index()
# round the views_mean column to one decimal place
avg_section['Page_views_mean'] = avg_section['Page_views_mean'].round(1)
# sort the dataframe by views_mean
avg_section = avg_section.sort_values('Page_views_mean', ascending=False)
# write df
st.write(avg_section)

######################################################################################
st.markdown("""---""")
st.write('Above but with outliers removed using 3 standard deviations')

df_matched_outliers_removed = df_matched.copy()
df_matched_outliers_removed['z_score'] = (df_matched_outliers_removed['Page_views'] - df_matched_outliers_removed.groupby('Section')['Page_views'].transform('mean')) / df_matched_outliers_removed.groupby('Section')['Page_views'].transform('std')

# remove rows with z-score > 3 or < -3
df_matched_outliers_removed = df_matched_outliers_removed[(df_matched_outliers_removed['z_score'] <= 3) & (df_matched_outliers_removed['z_score'] >= -3)]

# calculate mean of remaining values grouped by 'position'
result = df_matched_outliers_removed.groupby('Section')['Page_views','Position'].mean().round(0)
result = result.sort_values('Position', ascending=True)

# add index
result['ranked_position'] = result['Position'].rank(method='first')
st.subheader('Outliers removed')
st.write(result)

# Section has dropped for some unknown reason
result['Section'] = result.index

######################################################################################
st.markdown("""---""")
st.subheader('Bar plot')
# sort dates
list_of_dates = df_matched['Date'].unique()

# Start and end dates
start_date = list_of_dates[0]
end_date = list_of_dates[-1]

date_range = [datetime.datetime.strptime(start_date, '%Y%m%d').date(),
                datetime.datetime.strptime(end_date, '%Y%m%d').date()]

# create visual
selected_date = st.slider("Select a date", 
                            min_value=date_range[0], 
                            max_value=date_range[1], 
                            value=date_range[0], 
                            format="YYYY-MM-DD")


selected_date_str = selected_date.strftime("%Y%m%d")

# create df by date
filtered_df = df_matched[(df_matched['Date']) == (selected_date_str)]

# normalize here
# what does it look like
#st.dataframe(filtered_df)



######################################################################################
#st.markdown("""---""")
# percentage
total_views = filtered_df['Page_views'].sum()
filtered_df['Page_views_percentage'] = df['Page_views'].div(total_views) * 100


# scale 0 to 1
filtered_df['Page_views_scaled'] = (filtered_df['Page_views'] - filtered_df['Page_views'].min()) / (filtered_df['Page_views'].max() - filtered_df['Page_views'].min())


#normalized_col = (df['Page_views'] - mean) / std
#filtered_df['normalized_Page_views'] = normalized_col

######################################################################################
#st.markdown("""---""")

# Sort by position 
filtered_df = filtered_df.sort_values(by='Position', ascending=False)

# Create the plot
fig = px.bar(filtered_df,
            x="Page_views", 
            y="Section",
            orientation='h', 
            animation_frame="Date",
            hover_name="Position", 
            #range_x=[0, sports_merged_df["Page_Views"].max()*1.1],
            height=800)



st.plotly_chart(fig)

st.subheader('Page views %')
# Create the plot
fig = px.bar(filtered_df,
            x="Page_views_percentage", 
            y="Section",
            orientation='h', 
            animation_frame="Date",
            hover_name="Position", 
            #range_x=[0, sports_merged_df["Page_Views"].max()*1.1],
            height=800)



st.plotly_chart(fig)

st.subheader('Page_views scaled')
# Create the plot
fig = px.bar(filtered_df,
            x="Page_views_scaled", 
            y="Section",
            orientation='h', 
            animation_frame="Date",
            hover_name="Position", 
            #range_x=[0, sports_merged_df["Page_Views"].max()*1.1],
            height=800)



st.plotly_chart(fig)
######################################################################################
# animated
st.subheader("Animated page views (raw data)")
# Create the plot
fig = px.bar(df_matched.sort_values(["Date", "Position"], ascending=[True, False]),
            x="Page_views", 
            y="Section",
            orientation='h', 
            animation_frame="Date",
            hover_name="Position", 
            #range_x=[0, sports_merged_df["Page_Views"].max()*1.1],
            height=800)


st.plotly_chart(fig)








