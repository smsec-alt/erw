import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'

CROPS = ['Common wheat and spelt', 'Rye and winter cereal mixtures (maslin)', 'Barley', 'Winter barley', 'Spring barley',
       'Oats', 'Grain maize and corn-cob-mix', 'Rape and turnip rape seeds', 'Sunflower seed', 'Soya']
dict_replace = {
    'p': '',
    ': c': '',
    ' e': '',
    ':': '',
    ' ': '',
    'b': '',
    'd': '',
    'n': '',
    'u': '',
    'z': '',
    'f': '',
    'r': '',
}
country_mapping = pd.read_csv('country_mapping.csv', index_col='country').to_dict()['region']
url_crop_production = 'https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/APRO_CPSH1/?format=TSV'
url_crop_production_old = 'https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/APRO_CPNH1_H/?format=TSV'
url_crop_production_nuts2 = 'https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/APRO_CPSHR/?format=TSV'


def eu_production(url: str, title: str):
    df = pd.read_csv(url, header=0, sep='\t', quotechar='"')
    item = df.columns[0]
    new_cols = df[item].str.split(',', expand=True)
    item_names = item.split('\\')[0].split(',')
    new_cols.columns = item_names

    df = pd.concat([df, new_cols], axis=1)
    df.drop(item, axis=1, inplace=True)

    df.columns = list(map(lambda x: x.replace(' ', ''), list(df.columns)))
    df = df.replace(dict_replace, regex=True)

    df = df.melt(id_vars=item_names, var_name='year', value_name='value')
    df = df[df['value'] != '']
    df['value'] = pd.to_numeric(df['value'])

    df.reset_index(drop=True, inplace=True)
    crops_mapping = pd.read_csv('./mapping/ESTAT_CROPS_en.tsv', sep='\t', index_col='CRP')
    geo_mapping = pd.read_csv('./mapping/ESTAT_GEO_en.tsv', sep='\t', index_col='EUR')
    struc_mapping = pd.read_csv('./mapping/ESTAT_STRUCPRO_en.tsv', sep='\t', index_col='HU')

    df = df.merge(crops_mapping, left_on='crops', right_index=True)
    df = df.merge(geo_mapping, left_on='geo', right_index=True)
    df = df.merge(struc_mapping, left_on='strucpro', right_index=True)
    df = df.drop(['crops', 'strucpro', 'freq'], axis=1)
    df['geo'] = df['geo'].str[:2]
    df.columns = ['country', 'year', 'value', 'crop', 'region', 'variable']
    df = df[['country', 'region', 'crop', 'variable', 'year', 'value']]
    df = df.query('variable != "EU standard humidity (%)"')
    df = df[df['crop'].isin(CROPS)]
    df['variable'] = df['variable'].replace({'Harvested production in EU standard humidity (1000 t)': 'Production',
                                             'Area (cultivation/harvested/production) (1000 ha)':'Area', 'Yield in EU standard humidity (tonne/ha)':'Yield'})
    df['crop'] = df['crop'].replace({'Common wheat and spelt':'Soft Wheat',
                                     'Grain maize and corn-cob-mix':'Corn',
                                     'Rye and winter cereal mixtures (maslin)':'Rye',
                                     'Rape and turnip rape seeds':'Rapeseed',
                                     'Linseed (oilflax)': 'Linseed'})
    df['country'] = df['country'].replace(country_mapping)
    df = df.groupby(['country', 'region', 'crop', 'variable', 'year'], as_index=False)['value'].mean()
    df = df.query('value>0')
    df.to_excel(f'{title}.xlsx', index=None)


def get_processed_data(variable='Yield'):
    df_production_new = pd.read_excel('eu_production.xlsx')
    df_production_old = pd.read_excel('eu_production_old.xlsx')
    countries_list = pd.read_csv('region_crop.csv')
    df_production = pd.concat([df_production_new, df_production_old])
    df_production['variable'] = df_production['variable'].replace({'Harvested production (1000 t)': 'Production', 'Yield (tonne/ha)':'Yield'})
    df_production = df_production.pivot(index=['region', 'crop', 'year'], columns='variable', values='value')
    df_production['Yield'] = df_production['Production'] / df_production['Area']
    df_production = df_production.reset_index()
    df_production = df_production.dropna()
    df_production['region'] = df_production['region'].replace({'Germany (until 1990 former territory of the FRG)':'Germany'})
    df_production['country'] = df_production['region']
    if variable=='Yield':
        df_production = df_production[['region', 'crop', 'year', variable, 'country']]
        df_production.rename({variable:'value'}, axis=1, inplace=True)
        df_production['variable'] = variable
        df_production = df_production[['country', 'region', 'crop', 'variable', 'year', 'value']]
    elif variable=='Area':
        df_production = df_production[['region', 'crop', 'year', 'Production', 'Area', 'country']]
        df_production = df_production.melt(id_vars=['country', 'region', 'crop', 'year'])
        df_production = df_production[['country', 'region', 'crop', 'variable', 'year', 'value']]
    df_production = df_production[df_production['country'].isin(countries_list['country'].unique())]
    variable = 'Yields' if variable == 'Yield' else variable
    df_production.to_csv(f'eu_{variable.lower()}.csv', index=None)


def main():
    # eu_production(url_crop_production, 'eu_production')
    # eu_production(url_crop_production_old, 'eu_production_old')
    # eu_production(url_crop_production_nuts2, 'eu_production_nuts2')
    get_processed_data('Yield')
    get_processed_data('Area')


if __name__ == '__main__':
    main()
