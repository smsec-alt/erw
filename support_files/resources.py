import pandas as pd

today = pd.to_datetime("today").strftime('%Y-%m-%d')
current_year = pd.to_datetime("today").year
all_weather_items = ['daily-precipitation', 'max-temperature', 'min-temperature', 'average-temperature', 'vegetation-vigor-index', 'soil-moisture']
all_weather_items_pretty = ['Daily Precipitation', 'Max Temperature', 'Min Temperature', 'Average Temperature', 'Vegetation Vigor Index', 'Soil Moisture']

crops_list = ['Soft Wheat', 'Barley', 'Corn', 'Sunflower seed', 'Rapeseed', 'Oats']

def function_name(function):
    def wrapper(*args, **kwargs):
        print(f"Running function -- {function.__name__}{args}")
        return function(*args, **kwargs)
    return wrapper