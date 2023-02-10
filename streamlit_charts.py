import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pandas as pd
pd.options.mode.chained_assignment = None


class Weather_Report:
    def __init__(self, yields: pd.DataFrame, weather: pd.DataFrame, region_name: str, grains_class: str):
        self.region_name = region_name
        self.grains_class = grains_class
        self.country_yields = yields
        self.weather = weather

    def get_weather_analytics(self, weather_variable: str, start_date: str, end_date: str):
        start_date, end_date = pd.Timestamp(start_date), pd.Timestamp(end_date)
        year_start = 2021 if start_date.month<9 else 2020
        if self.grains_class in ['Corn', 'Oats', 'Soya', 'Sunflower seed', 'Spring barley']:
            year_start = 2020
        start_date, end_date = pd.Timestamp(year_start, start_date.month, start_date.day), pd.Timestamp(end_date.year-start_date.year+year_start, end_date.month, end_date.day)


        y_df = self.country_yields.copy()
        y_df.loc[y_df.index.max()+1]=y_df.loc[y_df.index.max()]
        weather_data = self.weather.query('variable==@weather_variable')
        if weather_variable == 'vegetation-vigor-index':
            weather_data = weather_data.query('value>0')
        weather_data.rename({'value':weather_variable}, axis=1, inplace=True)
        if not self.grains_class in ['Corn', 'Oats', 'Soya', 'Sunflower seed', 'Spring barley']:
            weather_data['new_time'] = np.where(weather_data['time'].dt.month>=9, weather_data['new_time'], weather_data['new_time']+pd.DateOffset(year=2021))
            weather_data['year'] = np.where(weather_data['time'].dt.month>=9, weather_data['year']+1, weather_data['year'])        
            weather_data = weather_data[weather_data['year']>1990]
        x_df = weather_data[weather_data['year'].isin(y_df.index)]
        if weather_variable == 'vegetation-vigor-index':
            x_df = x_df.dropna(subset=weather_variable)
        last_year = x_df['year'].max()
        max_last_date = x_df.query('year==@last_year')['new_time'].max()
            
        boundary1, boundary2 = min(max_last_date, start_date), min(max_last_date, end_date)
        if boundary1 != boundary2:
            x_df = x_df.query('new_time>=@boundary1 & new_time<=@boundary2')
            if not weather_variable in ['vegetation-vigor-index', 'soil-moisture']:
                x_df = x_df.groupby(['year'], as_index=False)[weather_variable].mean()
            else:
                x_df = x_df.query('new_time==@boundary2')[['year', weather_variable]]
            x_df = x_df.merge(y_df, left_on='year', right_index=True)
            x_df[[weather_variable, 'value']] = x_df[[weather_variable, 'value']].diff()
            x_df = x_df.dropna()
 
            fig = px.scatter(x_df.query('year<@last_year'), x=weather_variable, y='value', text=x_df.query('year<@last_year')['year'],
                                trendline="ols")
            fig.update_traces(textposition='top center', marker=dict(color='#5D69B1', size=6),
                                textfont=dict(color='#E58606'))
            fig.add_trace(go.Scatter(x=[x_df.query('year==@last_year')[weather_variable].values[0]], y=[0],
                                    showlegend=False, text=str(last_year), mode='markers', marker=dict(color='#FF0000', size=8)))

            model = px.get_trendline_results(fig)
            rsq = str(round(model.iloc[0]["px_fit_results"].rsquared, 3) * 100)[:4]
            if not weather_variable in ['vegetation-vigor-index', 'soil-moisture']:
                title_text = f"<b>{self.region_name} {self.grains_class} Yield vs Avg {weather_variable.title().replace('-', ' ')}, YoY - From {boundary1.strftime('%b %d')} To {boundary2.strftime('%b %d')}</b>"
            else:
                title_text = f"<b>{self.region_name} {self.grains_class} Yield vs {weather_variable.title().replace('-', ' ')}, YoY - As of {boundary2.strftime('%b %d')}</b>"
            fig.update_layout(
                title=title_text, 
                font=dict(color='rgb(82, 82, 82)', family='Arial'),
                xaxis=dict(gridcolor='#FFFFFF', title = f"{weather_variable.title().replace('-', ' ')}, YoY",
                                                linecolor='rgb(204, 204, 204)', linewidth=1, ticks='outside',
                                                tickfont=dict(size=12)),
                                        yaxis=dict(gridcolor='#FFFFFF', title="Wheat Yield, YoY"),
                                        plot_bgcolor='white')
            return fig


    def get_weather_chart(self, weather_variable: str, start_date: str, end_date: str):
        def get_analogs(weather_variable: str, last_year: int, max_last_date):
            if not weather_variable in ['vegetation-vigor-index', 'soil-moisture']:
                boundary = min(max_last_date, end_date)
                analogs_df = pd.concat([observed_data, ecm_data])
                analogs_df = analogs_df.query('new_time == @boundary')
                analogs_df[weather_variable] = abs(analogs_df[weather_variable] -
                            analogs_df.query('year==@last_year')[weather_variable].values[0])
            else:
                analogs_df = observed_data.dropna(subset=weather_variable)
                last_date = analogs_df.query('year==@last_year')['new_time'].max()
                analogs_df = analogs_df.query('new_time==@last_date')
            analogs_df[weather_variable] = abs(analogs_df[weather_variable] -
                                                analogs_df.query('year==@last_year')[weather_variable].values[0])
            analogs_df = analogs_df[analogs_df['year'].isin(self.country_yields.index)]
            first_analog, second_analog = analogs_df.sort_values(by=weather_variable)['year'][:2].to_list()    
            return [last_year, last_year - 1] + list({first_analog, second_analog})

        start_date, end_date = pd.Timestamp(start_date), pd.Timestamp(end_date)
        year_start = 2021 if start_date.month<9 else 2020
        if self.grains_class in ['Corn', 'Oats', 'Soya', 'Sunflower seed', 'Spring barley']:
            year_start = 2020
        start_date, end_date = pd.Timestamp(year_start, start_date.month, start_date.day), pd.Timestamp(end_date.year-start_date.year+year_start, end_date.month, end_date.day)

        weather_data = self.weather.query('variable==@weather_variable')
        if not self.grains_class in ['Corn', 'Oats', 'Soya', 'Sunflower seed', 'Spring barley']:
            weather_data['new_time'] = np.where(weather_data['time'].dt.month>=9, weather_data['new_time'], weather_data['new_time']+pd.DateOffset(year=2021))
            weather_data['year'] = np.where(weather_data['time'].dt.month>=9, weather_data['year']+1, weather_data['year'])
            weather_data = weather_data[weather_data['year']>1990]
        if weather_variable == 'vegetation-vigor-index':
            weather_data = weather_data.query('value>0')
        weather_data.rename({'value':weather_variable}, axis=1, inplace=True)
        observed_data = weather_data[weather_data['time'] < pd.Timestamp.today()]
        ecm_data = weather_data[weather_data['time'] >= pd.Timestamp.today()]

        observed_data = observed_data.query('new_time>=@start_date & new_time<=@end_date')
        ecm_data = ecm_data.query('new_time>=@start_date & new_time<=@end_date')
        
        last_year = weather_data['year'].max()
        max_last_date = weather_data.query('year==@last_year')['new_time'].max()
        if weather_variable == 'daily-precipitation':
            observed_data = observed_data.groupby(['year', 'time', 'new_time']).sum().groupby(
                level=0).cumsum().reset_index()
            ecm_data = ecm_data.groupby(['year', 'time', 'new_time']).sum().groupby(
                level=0).cumsum().reset_index()           
            if len(observed_data.query('year==@last_year')):
                ecm_data[weather_variable] = ecm_data[weather_variable] + observed_data.query('year==@last_year')[weather_variable].max()
        

        excl_years = get_analogs(weather_variable, last_year, max_last_date)

        max_data = observed_data.query('year<@last_year').groupby('new_time', as_index=False)[
            ['new_time', weather_variable]].max()
        min_data = observed_data.query('year<@last_year').groupby('new_time', as_index=False)[
            ['new_time', weather_variable]].min()
        mean_data = observed_data.query('year<@last_year').groupby('new_time', as_index=False)[
            ['new_time', weather_variable]].mean()

        fig = px.line(observed_data[observed_data['year'].isin(excl_years)==False], x='new_time', y=weather_variable,
                      color_discrete_sequence=px.colors.qualitative.G10, color='year', labels={weather_variable:'', 'new_time':'', 'year':''})
        fig.update_traces(visible="legendonly")
        fig.add_trace(go.Scatter(x=max_data['new_time'], y=max_data[weather_variable], name='',
                                 fill=None, mode='lines', line_color='#D3D3D3', line=dict(width=0)))
        fig.add_trace(go.Scatter(x=min_data['new_time'], y=min_data[weather_variable], name='Max-Min',
                                 fill='tonexty', mode='lines', line_color='#D3D3D3', line=dict(width=0)))
        
        fig.add_trace(
            go.Scatter(x=mean_data['new_time'], y=mean_data[weather_variable], name='Mean', line=dict(dash='dot', width=2),
                       fill=None, mode='lines', line_color='#0047AB'))

        for year_id, year in enumerate(excl_years[::-1]):
            col_list = ['#96616B', '#52BE80', '#000000', 'firebrick']
            fig.add_trace(go.Scatter(x=observed_data.query('year==@year')['new_time'],
                                     y=observed_data.query('year==@year')[weather_variable],
                                     fill=None, name=str(year),
                                     line=dict(width=max(2 + year_id - 2, 2), color=col_list[year_id])))
        if ecm_data is not None:
            fig.add_trace(
                go.Scatter(x=ecm_data.query('new_time <@end_date')['new_time'], y=ecm_data.query('new_time <@end_date')[weather_variable],
                           name='ECMWF', line=dict(width=3, dash='dot'), fill=None, mode='lines', line_color='firebrick'))

        yield_an1 = str(round(self.country_yields.loc[excl_years[2], 'value'], 2))
        yield_an2 = str(round(self.country_yields.loc[excl_years[3], 'value'], 2))
        title_text = f"<b>{self.region_name} - {weather_variable.title().replace('-', ' ')} - Weighted by {self.grains_class}'s Production</b><br><span style='font-size: 14px';>Pattern is similar to {excl_years[2]} and {excl_years[3]} when yield was {yield_an1} and {yield_an2}</span>"
        fig.update_layout(legend={'traceorder': 'reversed'}, title=title_text, hovermode="x unified", font=dict(color='rgb(82, 82, 82)', family='Arial'),
                          xaxis=dict(gridcolor='#FFFFFF',tickformat="%b %d",
                                     linecolor='rgb(204, 204, 204)', linewidth=1, ticks='outside',
                                     tickfont=dict(size=12)),
                            yaxis=dict(gridcolor='#F8F8F8', tickfont=dict(size=12)),
                            plot_bgcolor='white')

        return fig
    
    def yields_history(self):
        fig = px.line(self.country_yields, y="value", labels={'value':'', 'year':""})
        fig.update_layout(title=f'{self.region_name} - Historical {self.grains_class} Yields', hovermode="x unified", font=dict(color='rgb(82, 82, 82)', family='Arial'),
                            xaxis=dict(gridcolor='#FFFFFF',tickformat="%b %d",
                                        linecolor='rgb(204, 204, 204)', linewidth=1, ticks='outside',
                                        tickfont=dict(size=12)),
                            yaxis=dict(gridcolor='#F8F8F8', tickfont=dict(size=12)),
                            plot_bgcolor='white')
        return fig
    
    def item_history(self, item: str):
        df_item = pd.read_csv('./support_files/eu_area.csv')
        df_item = df_item.loc[(df_item['country'] == self.region_name) & (df_item['crop'] == self.grains_class)& (df_item['variable'] == item)]
        fig = px.line(df_item, x='year', y="value", labels={'value':'', 'year':""})
        fig.update_layout(title=f'{self.region_name} - Historical {self.grains_class} {item}', hovermode="x unified", font=dict(color='rgb(82, 82, 82)', family='Arial'),
                            xaxis=dict(gridcolor='#FFFFFF',tickformat="%b %d",
                                        linecolor='rgb(204, 204, 204)', linewidth=1, ticks='outside',
                                        tickfont=dict(size=12)),
                            yaxis=dict(gridcolor='#F8F8F8', tickfont=dict(size=12)),
                            plot_bgcolor='white')
        return fig
    

def get_deviation_charts(df_div, crop):
        def plot_charts(df, col):
                variable = col.split('+')[0].replace('-',' ').title()
                period = col.split('+')[1]
                fig = px.bar(df.sort_values(by=col), x='country', y=col,
                        color_continuous_scale=['#7a004c', '#b4006e', '#da0c6f', '#f9c0cc', '#dadada', '#bfe5e2', '#00b2ac', '#007c85', '#005b65'],
                        color_continuous_midpoint=0, color=col, labels={'variable':'', col:'','country':''})

                fig.update_layout(title=f'{variable} - Last {period} Days vs Historical Average - {crop}', hovermode="x unified",
                                font=dict(color='rgb(82, 82, 82)', family='Arial'),
                                width=1300,height=400,
                                        xaxis=dict(gridcolor='#FFFFFF',tickformat="%b %d",
                                                linecolor='rgb(204, 204, 204)', linewidth=1, ticks='outside',
                                                tickfont=dict(size=12)),
                                        yaxis=dict(gridcolor='#F8F8F8', tickfont=dict(size=12), tickformat=".1%"),
                                        plot_bgcolor='white', showlegend=False)
                fig.update_coloraxes(showscale=False)

                return fig

        return plot_charts(df_div, 'daily-precipitation+7'), plot_charts(df_div, 'daily-precipitation+30'), plot_charts(df_div, 'soil-moisture+7'),plot_charts(df_div, 'vegetation-vigor-index+10')