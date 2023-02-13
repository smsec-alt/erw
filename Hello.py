from gcs import GCS
import streamlit as st
import streamlit.components.v1 as components
from streamlit_charts import get_deviation_charts
from support_files.resources import crops_list

gcs = GCS(streamlit=True)

st.set_page_config(page_title="Europe Weather Maps", layout='wide')

with st.sidebar:
    add_class = st.selectbox("Crop Type", tuple(crops_list))


def main():
    st.markdown(f"""#### {add_class} Production in Europe""")
    values = st.slider('Select Year', 2012, 2022, 2021)
    HtmlFile = open(f"./support_files/html/{add_class}_{values}.html", 'r', encoding='utf-8')
    source_code = HtmlFile.read() 
    components.html(source_code, height=500)
    
    st.markdown("""#### Weather Summary""")
    
    img1 = gcs.read_file(f'global_weather/forecasts/europe_tp.png')
    img2 = gcs.read_file(f'global_weather/forecasts/europe_t2m.png')
    col1, col2 = st.columns(2)
    col1.image(img1)
    col2.image(img2)
    df_summary = gcs.read_csv(f'global_weather/europe/Europe_{add_class}_deviation.csv')
    dev_charts = get_deviation_charts(df_summary, add_class)
    col1.plotly_chart(dev_charts[0], use_container_width=True)
    col2.plotly_chart(dev_charts[1], use_container_width=True)
    col1.plotly_chart(dev_charts[2], use_container_width=True)
    col2.plotly_chart(dev_charts[3], use_container_width=True)

    
    
if __name__ == '__main__':
    main()
