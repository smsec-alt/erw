import datetime
import pandas as pd
import streamlit as st
from support_files.resources import current_year, all_weather_items_pretty
from support_files.quickstart import credentials, download_dataframe
from streamlit_charts import Weather_Report
st.set_page_config(page_title="Weather per Region", layout='wide')
creds = credentials()

df_yields = pd.read_csv('./support_files/eu_yields.csv')
df_region_crop = pd.read_csv('./support_files/region_crop.csv')
yields_container, charts_container, models_container = st.container(), st.container(), st.container()

today = datetime.date.today()
min_start_winter = datetime.date(current_year-1, 9, 1) if today < datetime.date(current_year, 9, 1) else datetime.date(current_year, 9, 1)
max_start_winter = datetime.date(current_year, 9, 1) if today < datetime.date(current_year, 9, 1) else datetime.date(current_year+1, 9, 1)
min_start_spring = datetime.date(current_year, 3, 1)
max_start_spring = datetime.date(current_year, 9, 1)


def main():
    with st.sidebar:
        add_region = st.selectbox("Choose a Region", tuple(df_region_crop['country'].unique()))
        add_class = st.selectbox("Crop Type", tuple(df_region_crop.query('country == @add_region')['crop']))
        col11, col21 = st.columns(2)
        if add_class in ['Corn', 'Oats', 'Soya', 'Sunflower seed', 'Spring barley']:
            min_start = min_start_spring
            max_start = max_start_spring
        else:
            min_start = min_start_winter
            max_start = max_start_winter

        start = col11.date_input("Start Date", min_start, min_value=min_start, max_value=max_start)
        end = col21.date_input("End Date", max_start, min_value=min_start, max_value=max_start)
        weather_options = st.multiselect('Parameter ', all_weather_items_pretty, ['Daily Precipitation', 'Max Temperature', 'Vegetation Vigor Index'])
        add_historical = st.radio("Historical Chart", ('Yield', 'Production', 'Area'))

    df_yields_country = df_yields.loc[(df_yields['country']==add_region)&(df_yields['crop']==add_class)]
    df_yields_country.set_index('year', inplace=True)
    df_weather = download_dataframe(creds=creds, filename=f'{add_region}_{add_class}_weather.csv',  parse_dates=['time'])
    df_weather['new_time'] = df_weather['time'].replace({old_date: old_date + pd.DateOffset(year=2020) for old_date in df_weather['time'].unique()})
    df_weather['year'] = df_weather['time'].dt.year
    
    wr = Weather_Report(df_yields_country, df_weather, add_region, add_class)

    with yields_container:
        st.markdown("#### **Historical Data**")
        if add_historical == 'Yield':
            st.plotly_chart(wr.yields_history(), use_container_width=True)
        else:
            st.plotly_chart(wr.item_history(add_historical), use_container_width=True)


    with charts_container:
        st.markdown("#### **Weather Charts**")
        col11, col21 = st.columns(2)
        for weather in weather_options:
            weather = weather.replace(' ','-').lower()
            col11.plotly_chart(wr.get_weather_chart(weather, start, end), use_container_width=True)
            col21.plotly_chart(wr.get_weather_analytics(weather, start, end), use_container_width=True)
        
        
if __name__ == '__main__':
    main()