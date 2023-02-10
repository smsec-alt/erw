import folium
from folium import Choropleth
import pandas as pd
import geopandas as gpd


PATH = './eu_production_nuts2.xlsx'
SHAPEFILE = './mapping/NUTS_RG_20M_2021_3035.shp.zip'
MAPPING_GEO = './mapping/ESTAT_GEO_en.tsv'

tiles = ['cartodbpositron', 'openstreetmap']

nuts = gpd.read_file(SHAPEFILE)[['geometry', 'NUTS_ID', 'CNTR_CODE']]
mapping_geo_df = pd.read_csv(MAPPING_GEO, sep='\t')
table = pd.read_excel(PATH)
table = table.merge(mapping_geo_df, left_on='region', right_on='Europe')
table = table.drop('Europe', axis=1)



def get_map(production_data, geo_data, year=2020, crop='Soft Wheat'):
    def folium_del_legend(choropleth: folium.Choropleth):
        del_list = []
        for child in choropleth._children:
            if child.startswith('color_map'):
                del_list.append(child)
        for del_item in del_list:
            choropleth._children.pop(del_item)
        return choropleth

    table = production_data.loc[(production_data['year']==year) & (production_data['variable']=='Production') & (production_data['crop']==crop)]
    data = geo_data.merge(table, left_on='NUTS_ID', right_on='EUR')
    data = data.drop(['EUR', 'CNTR_CODE'], axis=1)

    loc = f'{crop} Production in {year}'
    title_html = '''<h3 align="left" style="font-size:18px"><b>&emsp;{}</b></h3>'''.format(loc) 

    eu_map = folium.Map(location=[50,25], tiles='cartodbpositron', zoom_start=4)

    for tile in tiles:
        folium.TileLayer(tile).add_to(eu_map)
        
    choropleth = Choropleth(geo_data=data,
                data=data, columns = ['NUTS_ID', 'value'],
                key_on='feature.properties.NUTS_ID',
                fill_color='Spectral_r', line_weight=0.5,legend_name='Value',
                nan_fill_color='White', fill_opacity=0.6, highlight=True,
                bins=pd.qcut(data['value'], q=[0,0.05,0.1,0.15,0.3,0.5,0.7,0.85,0.9,0.99,1], retbins=True, duplicates='drop')[1]
                ).add_to(eu_map)

    # eu_map.get_root().html.add_child(folium.Element(title_html))

    folium_del_legend(choropleth).add_to(eu_map)

    choropleth.geojson.add_child(
        folium.features.GeoJsonTooltip(fields=['country','region','value'], 
                                        aliases=['Country','Region', 'Value'],
                                        style=('background-color: white; color: black; border: 2px solid black;border-radius: 3px;box-shadow: 3px;'),
                                        localize=True))
    folium.LayerControl().add_to(eu_map)
    return eu_map



def main():
    for year in table['year'].unique():
        if year >2011:
            for crop in table['crop'].unique():
                try:
                    get_map(table, nuts, year=year, crop=crop).save(f'./html/{crop}_{year}.html')
                except:
                    print(year, crop)
                    pass
            
            
if __name__ == '__main__':
    main()
