import streamlit as st
from streamlit_charts import get_deviation_charts
import streamlit.components.v1 as components
from gcs import GCS

gcs = GCS(streamlit=True)

st.set_page_config(page_title="Europe Weather Maps", layout='wide')

with st.sidebar:
    add_class = st.selectbox("Crop Type", ('Soft Wheat', 'Barley', 'Corn','Rye', 'Oats', 'Sunflower seed', 'Rapeseed','Soya'))


def main():
    st.markdown(f"""#### {add_class} Production in Europe""")
    values = st.slider('Select Year', 2012, 2022, 2020)
    HtmlFile = open(f"./support_files/html/{add_class}_{values}.html", 'r', encoding='utf-8')
    source_code = HtmlFile.read() 
    components.html(source_code, height=500)
    
    st.markdown("""#### Weather Summary""")
    
    
    # with ThreadPoolExecutor(max_workers=10) as executor:
    #     futures = [executor.submit(download_image, creds, filename='tp.png'),
    #                     executor.submit(download_image, creds, filename='t2m.png'),
    #                     executor.submit(download_dataframe, creds, filename=f'Europe_{add_class}_deviation.csv')]
    #     future_output = [future.result() for future in futures]
                
    col1, col2 = st.columns(2)
    # col1.image(future_output[0])
    # col2.image(future_output[1])
    # dev_charts = get_deviation_charts(future_output[2], add_class)
    df_summary = gcs.read_csv(f'global_weather/europe/Europe_{add_class}_deviation.csv')
    dev_charts = get_deviation_charts(df_summary, add_class)
    col1.plotly_chart(dev_charts[0], use_container_width=True)
    col2.plotly_chart(dev_charts[1], use_container_width=True)
    col1.plotly_chart(dev_charts[2], use_container_width=True)
    col2.plotly_chart(dev_charts[3], use_container_width=True)

    
    
if __name__ == '__main__':
    main()
