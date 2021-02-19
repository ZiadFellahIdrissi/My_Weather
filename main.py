import datetime
from os.path import dirname, join

import pandas as pd
import json

from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, Select, BoxSelectTool, HoverTool
from bokeh.plotting import figure

# Chargement des données
df = pd.read_csv(join(dirname(__file__), 'data/villes_donnees.csv'))
cities_file = open(join(dirname(__file__), 'data/villes.json'), "r")
cities = json.load(cities_file)
city = 'Casablanca' # Ville par défaut

def get_dataset(src, name):
    df = src[src.ville == name].copy()
    del df['ville']
    df['date'] = pd.to_datetime(df.date)
    data = dict(
                temp=df.temperature,
                windspeed=df['vitessevent'],
                humidity=df.humidite,
                date=df.date
            )
    return ColumnDataSource(data)

def make_plot(source, title):
    plot = figure(title=title, x_axis_type="datetime", plot_width=800,
                    x_axis_label=None, y_axis_label=None)

    plot.line('date', 'temp',color='#ebbd5b', source=source , legend_label="Temperature",line_width=2, alpha=0.8)
    plot.line('date', 'windspeed',color='#40ad5a', source=source , legend_label="Wind Speed",line_width=2, alpha=0.8)
    plot.line('date', 'humidity',color='#7f4ebf', source=source , legend_label="Humidity",line_width=2, alpha=0.8)

    plot.add_tools(HoverTool(
        tooltips=[
            ('Date', '@date{%d/%m/%Y, %HH%M}'),
            ('Temperature', '@temp °C'),
            ('Wind Speed', '@windspeed km/h'),
            ('Humidity', '@humidity %'),
        ],
        formatters={
            '@date': 'datetime',
        },
        mode='mouse'
    ))

    return plot

def update_plot(attrname, old, new):
    city = city_select.value
    plot.title.text = "Données météo pour " + cities[city]['title']

    src = get_dataset(df, cities[city]['ville'])
    source.data.update(src.data)
    
city_select = Select(value=city, title='City', options=sorted(cities.keys()))

source = get_dataset(df, cities[city]['ville'])

plot = make_plot(source, "Météo " + cities[city]['title'])

city_select.on_change('value', update_plot)

controls = column(city_select)
curdoc().add_root(row(plot, controls))
curdoc().title = "La météo"