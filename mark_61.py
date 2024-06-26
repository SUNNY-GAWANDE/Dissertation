#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import numpy as np

import dash
from dash import dcc
from dash import html
import plotly.graph_objects as go
import plotly.express as px

from dash.dependencies import Input, Output

import io
import base64


# In[2]:


pd.set_option('display.max_columns', 500)


# In[3]:


df_month_location = pd.read_csv('df_month_location1.csv')


# In[4]:


df_season_location = pd.read_csv('df_season_location1.csv')



df_year_location = pd.read_csv('df_year_location1.csv')


# In[6]:


# In[8]:


# List of available x columns
x_columns = ['DTR (Diurnal Temperature Range)', 'FD (Frost Days)', 'PRCPTOT (Total Precipitation)',
             'R10mm (Days with ≥ 10mm rain)', 'R20mm (Days with ≥ 20mm rain)', 'R5mm (Days with ≥ 5mm rain)',
             'Rx1day (Wettest day)', 'Rx5day (Wettest 5-Day Period)', 'SDII (Average Daily Rainfall Intensity)',
             'SU (Summer Days)', 'TN10p (Cold Nights)', 'TN90p (Warm Nights)', 'TNn (Coldest Night)',
             'TNx (Warmest Night)', 'TR (Tropical Nights)', 'TX10p (Cold Days)', 'TX90p (Warm Days)',
             'TXn (Coldest Day)', 'TXx (Warmest Day)', 'n_maxdy', 'n_mindy', 'n_rain','GSL','CSDI','WSDI','ID (Icing Days)',
             'R95pTOT','R99pTOT']

# Dictionary containing descriptions of x-columns
x_column_descriptions = {
    'DTR (Diurnal Temperature Range)': 'Avg difference between the max and min temperature during period of interest',
    'FD (Frost Days)': 'Counting the number of days when the min temperature was less than 0°C',
    'ID (Icing Days)': 'Counting the number of times the maximum temperature was less than 0°C',
    'PRCPTOT (Total Precipitation)': 'Annual total precipitation from days ≥1 mm',
    'R10mm (Days with ≥ 10mm rain)': 'Annual count when precipitation ≥10 mm',
    'R20mm (Days with ≥ 20mm rain)': 'Annual count when precipitation ≥20 mm',
    'R5mm (Days with ≥ 5mm rain)': 'Annual count when precipitation ≥5 mm',
    'Rx1day (Wettest day)': 'Annual maximum 1-day precipitation',
    'Rx5day (Wettest 5-Day Period)': 'Annual maximum consecutive 5-day precipitation',
    'SDII (Average Daily Rainfall Intensity)': 'Ratio of annual total precipitation to number of wet days (≥1 mm)',
    'SU (Summer Days)': 'Annual count when the max temperature >25 C',
    'TN10p (Cold Nights)': 'xyz',
    'TN90p (Warm Nights)': 'xyz1',
    'TNn (Coldest Night)': 'Min value of daily min temperature during period of interest',
    'TNx (Warmest Night)': 'Max value of daily min temperature during period of interest',
    'TR (Tropical Nights)': 'Counting no. of times when daily min temperature > 20 C',
    'TX10p (Cold Days)': 'abc',
    'TX90p (Warm Days)': 'abc1',
    'TXn (Coldest Day)': 'The min value of daily max temperature (TX) during the period of interest',
    'TXx (Warmest Day)': 'The maximum value of daily maximum temperature',
    'n_maxdy': 'abcde',
    'n_mindy': 'abcd',
    'n_rain': 'abcde',
    'GSL':'xyz',
    'CSDI':'xyz1',
    'WSDI':'The Warm Spell Duration Index (WSDI) represents the annual count of days contributing to warm spells, when the maximum temperature (TX) remains above its climatological 90th percentile.',
    'ID (Icing Days)': 'the number of times the maximum temperature (TX) was less than 0°C',
    'R95pTOT':'the accumulated rainfall (in mm) on very wet days',
    'R99pTOT':'Where an extremely wet day is defined as being greater than the 99th percentile of wet days'
}

# Create Dash app
app = dash.Dash(__name__)

# Define app layout
app.layout = html.Div([
    html.H1("Visualising Irish Climate Extremes"),

    # Radio buttons for selecting data source
    html.Div([
        html.Label("Select Data Source:"),
        dcc.RadioItems(
            id='data-source-radio',
            options=[
                {'label': 'Year', 'value': 'year'},
                {'label': 'Season', 'value': 'season'},
                {'label': 'Month', 'value': 'month'}
            ],
            value='year',
            labelStyle={'display': 'inline-block'}
        ),
    ]),

    # Dropdown for selecting station
    html.Div([
        html.Label("Select Station:"),
        dcc.Dropdown(
            id='station-dropdown',
            options=[{'label': str(station), 'value': station} for station in df_year_location['station_id'].unique()],
            multi=True
        ),
    ]),

    # Dropdown for selecting x column
    html.Div([
        html.Label("Select Indices:"),
        dcc.Dropdown(
            id='x-column-dropdown',
            options=[{'label': col, 'value': col} for col in x_columns],
            value=x_columns[0]
        ),
    ]),

    # Dropdown for selecting month
    html.Div([
        html.Label("Select Month:"),
        dcc.Dropdown(
            id='month-dropdown',
            options=[{'label': str(month), 'value': month} for month in df_month_location['month'].unique()],
            value=df_month_location['month'].unique()[0],
            style={'display': 'none'}
        ),
    ]),

    # Dropdown for selecting season
    html.Div([
        html.Label("Select Season:"),
        dcc.Dropdown(
            id='season-dropdown',
            options=[{'label': str(season), 'value': season} for season in df_season_location['season'].unique()],
            value=df_season_location['season'].unique()[0],
            style={'display': 'none'}
        ),
    ]),
    
    # Dropdown for selecting year for the map
    html.Div([
        html.Label("Select Year for Map:"),
        dcc.Dropdown(
            id='year-dropdown-map',
            options=[{'label': 'All Years', 'value': None}] + [{'label': str(year), 'value': year} for year in sorted(df_year_location['year'].unique())],
            value=None,  # Default to 'All Years'
            style={'display': 'block'}  # Always show this dropdown
        ),
    ]),

    # Container for graphs
    html.Div([
        # Line graph
        html.Div(dcc.Graph(id='line-plot'), style={'flex': '7', 'padding': '10px', 'height': '600px'}),
        
        # Map graph
        html.Div(dcc.Graph(id='map-plot'), style={'flex': '3', 'padding': '10px', 'height': '400px'})
    ], style={'display': 'flex', 'flex-direction': 'row', 'margin-bottom': '-170px'}),

    # Description of selected x-column
    html.Div(id='x-column-description', style={'padding': '10px', 'margin-top': '-160px'}),
])

# Callback to show/hide month and season dropdowns based on the selected data source
@app.callback(
    Output('month-dropdown', 'style'),
    Output('season-dropdown', 'style'),
    [Input('data-source-radio', 'value')]
)
def update_dropdown_visibility(data_source):
    if data_source == 'month':
        return {'display': 'block'}, {'display': 'none'}
    elif data_source == 'season':
        return {'display': 'none'}, {'display': 'block'}
    else:
        return {'display': 'none'}, {'display': 'none'}

# Callback to update line plot based on dropdown selections
@app.callback(
    Output('line-plot', 'figure'),
    [Input('data-source-radio', 'value'),
     Input('station-dropdown', 'value'),
     Input('x-column-dropdown', 'value'),
     Input('month-dropdown', 'value'),
     Input('season-dropdown', 'value')]
)
def update_line_plot(data_source, station_ids, selected_x, selected_month, selected_season):
    if data_source == 'year':
        df = df_year_location.copy()
    elif data_source == 'season':
        df = df_season_location.copy()
    elif data_source == 'month':
        df = df_month_location.copy()
    else:
        df = pd.DataFrame()

    if data_source == 'month':
        df = df[df['month'] == selected_month]
    elif data_source == 'season':
        df = df[df['season'] == selected_season]

    traces = []
    
    if not station_ids:  # No station selected, show average across all stations
        # Calculate mean for selected x column grouped by year
        avg_values = df.groupby('year')[selected_x].mean().reset_index()

        # Create trace for line plot
        trace = go.Scatter(
            x=avg_values['year'],
            y=avg_values[selected_x],
            mode='lines+markers',
            name='Average'
        )

        traces.append(trace)
    else:  # Specific stations selected
        for station_id in station_ids:
            df_filtered = df[df['station_id'] == station_id]

            if not df_filtered.empty:
                # Calculate mean for selected x column grouped by year
                avg_values = df_filtered.groupby('year')[selected_x].mean().reset_index()

                # Create trace for line plot
                trace = go.Scatter(
                    x=avg_values['year'],
                    y=avg_values[selected_x],
                    mode='lines+markers',
                    name=f"Station {station_id}"
                )

                traces.append(trace)

    # Layout for line plot
    layout = go.Layout(
        title=f"{selected_x} Analysis",
        xaxis={'title': 'Year'},
        yaxis={'title': selected_x},
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5
        )
    )
    return {'data': traces, 'layout': layout}

# Callback to update map plot based on dropdown selections
@app.callback(
    Output('map-plot', 'figure'),
    [Input('data-source-radio', 'value'),
     Input('station-dropdown', 'value'),
     Input('x-column-dropdown', 'value'),
     Input('month-dropdown', 'value'),
     Input('season-dropdown', 'value'),
     Input('year-dropdown-map', 'value')]  # Add input for the new year dropdown
)
def update_map_plot(data_source, station_ids, selected_x, selected_month, selected_season, selected_year):
    if data_source == 'year':
        df = df_year_location.copy()
    elif data_source == 'season':
        df = df_season_location.copy()
    elif data_source == 'month':
        df = df_month_location.copy()
    else:
        df = pd.DataFrame()

    if station_ids:
        df = df[df['station_id'].isin(station_ids)]

    # Handle filtering by selected year or average across all years
    if selected_year is not None:
        df = df[df['year'] == selected_year]
    else:
        df = df.groupby(['station_id', 'Latitude', 'Longitude']).agg({selected_x: 'mean'}).reset_index()

    if not df.empty:
        fig = px.scatter_mapbox(df,
                                lat="Latitude",
                                lon="Longitude",
                                size_max=15,
                                color=selected_x,
                                hover_data={selected_x: True, 'station_id': True},
                                zoom=4.5,
                                height=400,
                                center={"lat": 53.1424, "lon": -7.6921})

        fig.update_traces(marker=dict(size=12, symbol='circle'))
        fig.update_layout(mapbox_style="open-street-map")
        fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
        fig.update_layout(coloraxis_colorbar=dict(title=''))

        return fig
    else:
        return go.Figure()

# Callback to update description of selected x-column
@app.callback(
    Output('x-column-description', 'children'),
    [Input('x-column-dropdown', 'value')]
)
def update_x_column_description(selected_x):
    if selected_x in x_column_descriptions:
        return html.Div([
            html.Label("Description:"),
            html.P(x_column_descriptions[selected_x])
        ])
    else:
        return html.Div()

# Run the app
if __name__ == '__main__':
    app.run_server(port=8501)
