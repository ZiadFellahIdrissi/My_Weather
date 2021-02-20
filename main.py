import datetime as dt
from datetime import date,time
from os.path import dirname, join

import pandas as pd
import json

from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, Select, BoxSelectTool, DateRangeSlider, HoverTool
from bokeh.plotting import figure

# Chargement des données
df = pd.read_csv(join(dirname(__file__), 'data/villes_donnees.csv'))
cities_file = open(join(dirname(__file__), 'data/villes.json'), "r")
cities = json.load(cities_file)
city = 'Casablanca' # Ville par défaut
dateDefaut = (date(2021, 2, 8), date(2021, 2, 12)) # Ville par défaut

def get_dataset(src, name, mydate):
    src['date'] = pd.to_datetime(src.date)
    start_date = dt.datetime.combine(mydate[0], time(0,0,0))
    end_date   = dt.datetime.combine(mydate[1], time(23,0,0))

    after_start_date = src['date'] >= start_date
    before_end_date = src['date'] <= end_date
    between_two_dates = after_start_date & before_end_date
    filtered_dates = src.loc[between_two_dates]

    df = filtered_dates[filtered_dates.ville==name].copy()
    del df['ville']
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

    start_date = dt.datetime.fromtimestamp(date_select.value[0]/1000)
    end_date = dt.datetime.fromtimestamp(date_select.value[1]/1000)
    new_date = (start_date, end_date)

    plot.title.text = "Météo " + cities[city]['title']

    src = get_dataset(df, cities[city]['ville'], new_date)
    source.data.update(src.data)
    
city_select = Select(value=city, title='City', options=sorted(cities.keys()))
date_select = DateRangeSlider(value=dateDefaut, title='Date', start=date(2021,2,5), end=date(2021,2,19))

source = get_dataset(df, cities[city]['ville'],dateDefaut)

plot = make_plot(source, "Météo " + cities[city]['title'])

city_select.on_change('value', update_plot)
date_select.on_change('value', update_plot)

controls = column(city_select,date_select)
curdoc().add_root(row(plot, controls))
curdoc().title = "La météo"