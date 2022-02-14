# -*- coding: utf-8 -*-
import dash
from dash import dcc
from dash import html
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from datetime import datetime as dt
from datetime import timedelta
import sqlite3

sqlite_ws_file = '/var/log/temperature/weatherstation.sqlite'    # name of the sqlite database file
table_ws_name = 'data'   # name of the table
index_col = 'id'
date_col = 'date' # name of the date column
time_col = 'time'# name of the time column

app = dash.Dash(__name__)
app.config.update({})
server = app.server

print(dcc.__version__)

todate = dt.now()
fromdate = dt.now()-timedelta(weeks=2)


def querywslog(fromdate,todate):
    timestamp = []
    t_ws = []
    humidity_ws = []
    subtype_ws = []
    battery_ok_ws = []
    wind_dir_deg_ws = []
    wind_avg_km_h_ws = []
    wind_max_km_h_ws = []
    rain_mm_ws = []
    conn = sqlite3.connect(sqlite_ws_file)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM {tn} WHERE {dc} BETWEEN '{fd}' AND '{td}'".\
        format(tn=table_ws_name, dc=date_col, fd=fromdate, td=todate))
    rows = c.fetchall()
    for row in rows:
        timestamp.append(row["date"] + " " + row["time"])
        t_ws.append(row["temperature_C"])
        humidity_ws.append(row["humidity"])
        subtype_ws.append(row["subtype"])
        battery_ok_ws.append(row["battery_ok"])
        wind_dir_deg_ws.append(row["wind_dir_deg"])
        wind_avg_km_h_ws.append(row["wind_avg_km_h"])
        wind_max_km_h_ws.append(row["wind_max_km_h"])
        rain_mm_ws.append(row["rain_mm"])
    conn.close()
    return {'timestamp':timestamp, 'ws_temp':t_ws, 'humidity':humidity_ws, 'subtype':subtype_ws, 'battery_ok':battery_ok_ws, 'wind_dir':wind_dir_deg_ws, 'wind_avg':wind_avg_km_h_ws, 'wind_max':wind_max_km_h_ws, 'rain':rain_mm_ws}

def calc_rain_per_day(timestamp,rain):
    i=0
    format = "%Y-%m-%d %H:%M:%S"
    startrain = rain[0]
    datestamp = []
    rain_per_day=[]
    for ts in timestamp:
        if i>0:
            dt_object_prev = dt.strptime(timestamp[i-1], format)
            dt_object = dt.strptime(ts, format)
            if dt_object.date() > dt_object_prev.date():
                #print(dt_object_prev.date(), rain[i]- startrain)
                datestamp.append(dt_object_prev.date())
                if rain[i] < startrain: # we got a reset
                    startrain = rain[i]
                rain_per_day.append(round(rain[i]- startrain,1))
                startrain = rain[i]
        i=i+1
    return{'datestamp':datestamp, 'rain_per_day':rain_per_day}

def create_figure_ws(figdatestart,figdateend):
    fromdate = dt.strptime(figdatestart[0:10], '%Y-%m-%d')
    todate = dt.strptime(figdateend[0:10], '%Y-%m-%d')
    dws = querywslog(fromdate,todate)
    rpd = calc_rain_per_day(dws['timestamp'],dws['rain'])
    fig = make_subplots(rows=3, cols=2)
    # add traces
    fig.add_trace(
        go.Scatter(x=dws['timestamp'], y=dws['ws_temp'], mode='markers+lines', name='temperature'),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=dws['timestamp'], y=dws['humidity'], mode='markers', name='humidity'),
        row=1, col=2
    )
    fig.add_trace(
        go.Scatter(x=dws['timestamp'], y=dws['wind_max'], mode='markers', name='wind_max'),
        row=2, col=1
    )
    fig.add_trace(
        go.Scatter(x=dws['timestamp'], y=dws['wind_avg'], mode='markers', name='wind_avg'),
        row=2, col=1
    )
    fig.add_trace(
        go.Scatter(x=dws['timestamp'], y=dws['wind_dir'], mode='markers', name='wind_dir'),
        row=2, col=2
    )
    fig.add_trace(
        go.Scatter(x=dws['timestamp'], y=dws['rain'], mode='markers', name='rain'),
        row=3, col=1
    )
    fig.add_trace(
        go.Bar(x=rpd['datestamp'], y=rpd['rain_per_day'], text=rpd['rain_per_day'], name='rain'),
        row=3, col=2
    )
    # Update yaxis properties
    fig.update_yaxes(title_text="Temperature (C)", row=1, col=1)
    fig.update_yaxes(title_text="humidity (%)", row=1, col=2)
    fig.update_yaxes(title_text="speed (km/h)", row=2, col=1)
    fig.update_yaxes(title_text="dir (deg)", row=2, col=2)
    fig.update_yaxes(title_text="rain (mm)", row=3, col=1)
    fig.update_yaxes(title_text="rain per day (mm)", row=3, col=2)

    fig.update_layout(height=600, 
        title_text='Weatherstation log - {:s} - {:s}'.format(fromdate.strftime("%-d %B %Y"), todate.strftime("%-d %B %Y")),
        paper_bgcolor="LightSteelBlue")
    return(fig)

def serve_layout():
    return html.Div(children=[
        dcc.Graph(id='my-graph-1'),
        html.Div([
            dcc.DatePickerRange(
            id='date-picker-range-1',
            display_format='DD MMM YYYY',
            start_date=dt.now()-timedelta(weeks=2),
            end_date=dt.now()
        ),
    ], style={'text-align': 'center', 'background-color':'LightSteelBlue'}),     
])

app.layout = serve_layout

@app.callback(
    dash.dependencies.Output('my-graph-1', 'figure'),
    [dash.dependencies.Input('date-picker-range-1', 'start_date'),
     dash.dependencies.Input('date-picker-range-1', 'end_date')])
def update_output(start_date, end_date):
    return create_figure_ws(start_date, end_date)


if __name__ == '__main__':
    app.run_server(debug=False, host='0.0.0.0')

