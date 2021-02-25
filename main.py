import datetime as dt
from os.path import dirname, join

import pandas as pd
import json

from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource,CheckboxGroup, DateRangeSlider,Select, HoverTool,DataRange1d,CustomJS
from bokeh.plotting import figure

# Chargement des données
df = pd.read_csv(join(dirname(__file__), 'data/villes_donnees.csv'))
cities_file = open(join(dirname(__file__), 'data/villes.json'), "r")
cities = json.load(cities_file)
city = 'Casablanca' # Ville par défaut
dateDefaut = (dt.date(2021, 2, 8), dt.date(2021, 2, 12)) # date par défaut

def get_dataset(src, name, mydate):
    src['date'] = pd.to_datetime(src.date)
    start_date = dt.datetime.combine(mydate[0], dt.time(0,0,0))
    end_date   = dt.datetime.combine(mydate[1], dt.time(23,0,0))

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

    temp=plot.line('date', 'temp',color='#ebbd5b', source=source , legend_label="Temperature",line_width=2, alpha=0.8)
    windspeed=plot.line('date', 'windspeed',color='#40ad5a', source=source , legend_label="Wind Speed",line_width=2, alpha=0.8)
    humidity=plot.line('date', 'humidity',color='#7f4ebf', source=source , legend_label="Humidity",line_width=2, alpha=0.8)

    
    plot.add_tools(HoverTool(
        tooltips=[
            ('La date', '@date{%d/%m/%Y, %HH%M}'),
            ('la temperature', '@temp °C'),
            ('La vitesse du vent', '@windspeed km/h'),
            ('Lhumidite', '@humidity %'),
        ],
        formatters={
            '@date': 'datetime',
        },
        mode='mouse'
    ))
    plot.axis.axis_label_text_font_style = "bold"
    plot.x_range = DataRange1d(range_padding=0.0)
    plot.toolbar.autohide = True

    return (plot,temp,windspeed,humidity)

def update_plot(attrname, old, new):
    city = city_select.value

    start_date = dt.datetime.fromtimestamp(date_select.value[0]/1000)
    end_date = dt.datetime.fromtimestamp(date_select.value[1]/1000)
    new_date = (start_date, end_date)

    plot.title.text = "Météo " + cities[city]['title']

    src = get_dataset(df, cities[city]['ville'], new_date)
    source.data.update(src.data)
    
city_select = Select(value=city, title='City', options=sorted(cities.keys()))
date_select = DateRangeSlider(value=dateDefaut, title='Date', start=dt.date(2021,2,5), end=dt.date(2021,2,19))
checkbox = CheckboxGroup(labels=["la temperature", "L'humidite" , "La vitesse du vent"], active=[0,1,0] )

source = get_dataset(df, cities[city]['ville'],dateDefaut)

plot,temp,windspeed,humidity = make_plot(source, "Météo " + cities[city]['title'])

city_select.on_change('value', update_plot)
date_select.on_change('value', update_plot)

checkbox.js_on_click( CustomJS(args=dict(line0=temp, line1=windspeed, line2=humidity), code="""
    console.log(cb_obj.active);
    line0.visible = false;
    line1.visible = false;
    line2.visible = false;
    for (let i in cb_obj.active) {
        console.log(cb_obj.active[i]);
        if (cb_obj.active[i] == 0) {
            line0.visible = true;
        } else if (cb_obj.active[i] == 1) {
            line2.visible = true;
        }else if (cb_obj.active[i] == 2) {
            line1.visible = true;
        }
    }
"""))

controls = column(city_select,date_select,checkbox)
curdoc().add_root(row(plot, controls))
curdoc().title = "La météo"