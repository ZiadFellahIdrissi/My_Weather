import datetime
from os.path import dirname, join

import pandas as pd
from scipy.signal import savgol_filter

from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, DataRange1d, Select, BoxSelectTool, HoverTool
from bokeh.palettes import Blues4
from bokeh.plotting import figure


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

    plot.line('date', 'temp',color=Blues4[1], source=source , legend_label="Temperature",line_width=3, alpha=0.7)
    plot.line('date', 'windspeed',color=Blues4[2], source=source , legend_label="Wind Speed",line_width=2, alpha=0.7)
    plot.line('date', 'humidity',color=Blues4[3], source=source , legend_label="Humidity",line_width=2, alpha=0.7)

    plot.add_tools(HoverTool(
        tooltips=[
            ('Date', '@date{%Y-%m-%d}'),
            ('Temperature', '@temp °C'),
            ('Wind Speed', '@windspeed km/h'),
            ('Humidity', '@humidity %'),
        ],
        formatters={
            'date'      : 'datetime',
        },
        mode='mouse'
    ))

    return plot

def update_plot(attrname, old, new):
    city = city_select.value
    plot.title.text = "Weather data for " + cities[city]['title']

    src = get_dataset(df, cities[city]['ville'])
    source.data.update(src.data)
    
city = 'Casablanca'
cities = {
    'Casablanca': {
        'ville': 'CASA',
        'title': 'Casablanca, MA',
    },
    'Fes': {
        'ville': 'FES',
        'title': 'Fès, MA',
    }
}

city_select = Select(value=city, title='City', options=sorted(cities.keys()))

df = pd.read_csv(join(dirname(__file__), 'data/bestone.csv'))
source = get_dataset(df, cities[city]['ville'])

plot = make_plot(source, "Weather data for " + cities[city]['title'])

city_select.on_change('value', update_plot)

controls = column(city_select)
curdoc().add_root(row(plot, controls))
curdoc().title = "Weather"