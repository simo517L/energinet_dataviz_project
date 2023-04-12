import math

from dash import dcc
from dash import html
import pandas as pd
import numpy as np
import datetime as dt
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from base import COLOR_HEATMAP_SCALE, COLOR_HEATMAP_LINES, GREEN_COLS, DARK_COLS,COLOR_HEATMAP_div_SCALE
from dicts_and_lists import *


def choose_plot(number):
    if number == 1:
        out = dcc.Dropdown(
            id={'type': 'plot_selector', 'index': number},
            options=[
                {'label': 'Heatmap', 'value': 'heatmap'},
                {'label': 'TimeSeries', 'value': 'timeseries'}
            ],
            placeholder="Select selector-plot chart type..."
        )

    else:
        out = dcc.Dropdown(
            id={'type': 'plot_selector', 'index': number},
            options=[
                {'label': 'Sunburst chart', 'value': 'sunburst'},
                {'label': 'Stacked/Line chart', 'value': 'stacked'},
            ],
            placeholder=f"Select chart type for child-plot {number-1}..."
        )
    return out

def build_setting_selector_for_selectorchart(value, index):
    out = []
    out.append(
        dbc.Row([
            dbc.Col(
                dcc.Dropdown(
                    id='setting_selector_chart',
                    options=[
                        {'label': 'Production', 'value': 'production'},
                        {'label': 'Consumption', 'value': 'consumption'},
                        {'label': 'CO2', 'value': 'co2'},
                        {'label': 'Mean Price', 'value': 'prices'},
                        {'label': 'Total Flows', 'value': 'exchange'},
                    ],
                    value='production'
                )
            ),
            dbc.Col(
                dcc.Dropdown('subsetting_selector_chart', options=[], value=None)
            )
        ])
    )
    row = [dbc.Col(dcc.RadioItems(
                id="pricearea_selector_chart",
                options=[
                    {'label': 'Total', 'value': 'total'},
                    {'label': 'DK1', 'value': 'DK1'},
                    {'label': 'DK2', 'value': 'DK2'}
                ],
                value='DK1',
                inputStyle={"margin-right": "5px", "margin-left": "10px"}
            ))]
    if value == "heatmap":
        row += [dbc.Col(dcc.Checklist(
                id="selector_chart_checkbox",
                options=[
                    {'label': 'Highlight chosen date (may hurt performance)', 'value': 'on'}
                ],
                value=['on'],
                inputStyle={"margin-right": "5px", "margin-left": "10px"}
            )),dbc.Col(dcc.RadioItems(
                id="selector_granularity",
                options=[
                    {'label': 'Day', 'value': 'Day'},
                ],
                value='Day',
                inputStyle={"margin-right": "5px", "margin-left": "10px"},
            style=dict(display='none')
        ))
        ]
    elif value == "timeseries":
        row += [dbc.Col(dcc.Checklist(
                id="selector_chart_checkbox",
                options=[
                    {'label': 'Share y-axis across plots', 'value': 'on'}
                ],
                value=['on'],
                inputStyle={"margin-right": "5px", "margin-left": "10px"}
            )),dbc.Col(dcc.RadioItems(
                id="selector_granularity",
                options=[
                    {'label': 'Day', 'value': 'Day'},
                    {'label': 'Hour', 'value': 'Hour'},
                ],
                value='Day',
                inputStyle={"margin-right": "5px", "margin-left": "10px"}))
                ]
    out.append(
        dbc.Row(row)
    )
    return out

def build_setting_selector_sunburst(index):
    out = [dbc.Row(dbc.Col(dcc.Dropdown(
        id={'type': "setting_sunburst", 'index': index},
        options=[{'label': 'Production', 'value': 'production'},
                 {'label': 'Imports', 'value': 'imports'},
                 {'label': 'Exports', 'value': 'exports'}],
        value="production"
    ))), dbc.Row(dcc.RadioItems(
        id={'type': "pricearea_sunburst", 'index': index},
        options=[
            {'label': 'Total', 'value': 'total'},
            {'label': 'DK1', 'value': 'DK1'},
            {'label': 'DK2', 'value': 'DK2'}
        ],
        value='DK1',
        inputStyle={"margin-right": "5px", "margin-left": "10px"}))]
    return out

def build_setting_selector_stacked(index):
    out = [dbc.Row(dbc.Col(dcc.Dropdown(
        id={'type': "setting_stacked", 'index': index},
        options=[{'label': 'Production', 'value': 'production'},
                {'label': 'Consumption', 'value': 'consumption'},
                {'label': 'CO2', 'value': 'co2'},
                {'label': 'Price', 'value': 'prices'},
                {'label': 'Imports', 'value': 'imports'},
                {'label': 'Exports', 'value': 'exports'}],
        value="production"
    ))),
        dbc.Row([dbc.Col(dcc.RadioItems(
            id={'type': "stacked_type", 'index': index},
            options=[
                {'label': 'Raw values', 'value': 'raw'},
                {'label': 'Sum to 100', 'value': 'percentage'}
            ],
            value='raw',
            inputStyle={"margin-right": "5px", "margin-left": "10px"})),
            dbc.Col(dcc.Checklist(
                id={'type': "hoverinfo_checkbox", 'index': index},
                options=[
                    {'label': 'Full Hoverinfo', 'value': 'on'}
                ],
                value=['on'],
                inputStyle={"margin-right": "5px", "margin-left": "10px"}
            ))


        ]),
        dbc.Row(dcc.RadioItems(
            id={'type': "pricearea_stacked", 'index': index},
            options=[
                {'label': 'Total', 'value': 'total'},
                {'label': 'DK1', 'value': 'DK1'},
                {'label': 'DK2', 'value': 'DK2'}
            ],
            value='total',
            inputStyle={"margin-right": "5px", "margin-left": "10px"}))]
    return out

def build_heatmap_year(df, setting,
                       fig=None,
                       row: int = None,
                       showscale: bool = False,
                       zmin=0,
                       zmax=1,
                       click=None):
    year = df.index[0].year



    # Creates empty DataFrame and inserts values
    data = pd.DataFrame()
    data['HourDK'] = pd.date_range(start=f'01-01-{year}', end=f'12-31-{year}')
    data = data.set_index('HourDK')
    data["Values"] = np.nan
    data.loc[df.index[0]:df.index[-1], "Values"] = df.values

    month_names = [dt.date(year, i, 1).strftime("%b") for i in range(1, 13)]
    month_days = [(dt.date(year=year, month=i % 12 + 1, day=1) - dt.timedelta(days=1)).day for i in range(1, 13)]
    month_positions = (np.cumsum(month_days) - 15) / 7

    weekdays_in_year = [date.weekday() for date in data.index]  # Weekday name for each date

    # Allocates each date to a weeknumber. There are some issues with some special cases which are handled in the loop.
    weeknumber_of_dates = []
    for date in data.index:
        if int(date.strftime("%V")) in [52, 53] and date.month == 1:
            weeknumber_of_dates.append(0)
        elif int(date.strftime("%V")) == 1 and date.month == 12:
            weeknumber_of_dates.append(53)
        else:
            weeknumber_of_dates.append(int(date.strftime("%V")))
    hover_text = [f'{date.strftime("%Y-%b-%d")}: {np.round(data.loc[date, "Values"],decimals=2)} {dict_units[setting]}' for date in data.index]

    # handle end of year
    if  zmin >= 0 :
        COLOR_HEATMAP = COLOR_HEATMAP_SCALE
    else:
        COLOR_HEATMAP = [[0, '#ef8a62'],[(-zmin)/(zmax-zmin),'#f7f7f7'], [1, '#67a9cf']]


    output = [
        go.Heatmap(
            x=weeknumber_of_dates,
            y=weekdays_in_year,
            z=data.Values.values,
            text=hover_text,
            hoverinfo='text',
            xgap=3, ygap=3,
            showscale=showscale,
            colorscale=COLOR_HEATMAP,
            #colorbar=go.heatmap.ColorBar(bgcolor ="aqua" , xanchor="left"),
        zmin=zmin, zmax=zmax,
        )
    ]

    output = add_month_lines(output, zip(data.index, weekdays_in_year, weeknumber_of_dates),click=click)

    layout = go.Layout(
        yaxis=dict(
            showline=False, showgrid=False, zeroline=False,
            tickmode='array',
            ticktext=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            tickvals=[0, 1, 2, 3, 4, 5, 6],
            autorange="reversed"
        ),
        xaxis=dict(
            showline=False, showgrid=False, zeroline=False,
            tickmode='array',
            ticktext=month_names,
            tickvals=month_positions
        ),
        font={'size': 10, 'color': 'black'},
        plot_bgcolor=('white'),
        margin=dict(l=0, r=0, b=0, t=20, pad=0),
        showlegend=False
    )

    if fig is None:
        fig = go.Figure(data=output, layout=layout)
    else:
        fig.add_traces(output, rows=[(row + 1)] * len(output), cols=[1] * len(output))
        fig.update_layout(layout)
        fig.update_xaxes(layout['xaxis'])
        fig.update_yaxes(layout['yaxis'])

    return fig


def build_plot_heatmap(df, header, setting, click=None):
    years = list(set(df.index.year))
    fig = make_subplots(rows=len(years), cols=1, subplot_titles=years)
    zmin = np.nanmin(df.values)
    zmax = np.nanmax(df.values)
    clickyear = 0
    if click != None:
        datestring = click["points"][0]["text"].split(": ")[0]
        date = dt.datetime.strptime(datestring, "%Y-%b-%d")
        clickyear = date.year

    for i, year in enumerate(years):
        df_year = df[df.index.year == year]
        if clickyear == year:
            clickdat = click
        else:
            clickdat = None

        fig = build_heatmap_year(df_year, setting, fig=fig, row=i, showscale=True if i == 3 else False, zmin=zmin, zmax=zmax, click=clickdat)
    fig.update_layout(clickmode='event+select',
                      title=f'Heatmap of {header}',hovermode ="closest")
    return fig

def build_timeseries_year(df, setting, zmin, zmax, fig, row, shareY):
    # TODO Look into allowing two traces per plot with each their y-axis.
    hover_text = [f'{datetime.strftime("%Y-%b-%d %H:%M:%S")}: {np.round(df.loc[datetime],decimals=2)} {dict_units[setting]}' for datetime in df.index]
    df.sort_index(inplace=True)
    output = [
        go.Scatter(
            x=df.index.map(lambda t: t.replace(year=2020)), # This looks very weird, but in the plots all data is set to be from 2020. This is so the shared x-axis works properly.
            y=df.values,
            mode='lines',
            line=dict(color="#67a9cf"),
            text=hover_text,
            hoverinfo="text"
        )
    ]
    layout = go.Layout(
        yaxis=dict(
            showgrid=False, zeroline=False,
            range=[zmin,zmax] if shareY else None,
            showline=True, linewidth=2, linecolor='black', gridcolor='white'
        ),
        xaxis=dict(
            showgrid=False, zeroline=False,
            tickformat='%B-%d', tickangle=90, dtick=604800000.0,
            showline=True, linewidth=2, linecolor='black', gridcolor='white',
        ),
        font={'size': 10, 'color': 'black'},
        plot_bgcolor=('white'),
        margin=dict(l=0, r=0, b=0, t=20, pad=0),
        showlegend=False
    )
    if fig is None:
        fig = go.Figure(data=output, layout=layout)
    else:
        fig.add_traces(output, rows=[(row + 1)] * len(output), cols=[1] * len(output))
        fig.update_layout(layout)
        fig.update_yaxes(layout['yaxis'])
        fig.update_xaxes(layout['xaxis'])

    return fig

def build_plot_timeseries(df, header, setting, shareY):
    years = list(set(df.index.year))
    fig = make_subplots(rows=len(years), cols=1, subplot_titles=years, shared_xaxes=True)
    zmin = np.nanmin(df.values)
    zmax = np.nanmax(df.values)
    for i, year in enumerate(years):
        df_year = df[df.index.year == year]
        fig = build_timeseries_year(df_year, setting, zmin, zmax, fig=fig, row=i, shareY=shareY)

    fig.update_layout(clickmode='event+select',
                      title={
                          'text': f'TimeSeries of {header}',
                          #'y': 1,
                          #'x': 0.5,
                          #'xanchor': 'center',
                          #'yanchor': 'top'
                          },
                      hovermode="closest")
    #fig.update_layout(
    #    xaxis1=dict(
    #        rangeslider_visible=False,
    #        rangeselector=dict(
    #            buttons=list([
    #                dict(count=7, label="1w", step="day", stepmode="backward"),
    #                dict(count=1, label="1m", step="month", stepmode="backward"),
    #                dict(count=3, label="3m", step="month", stepmode="backward"),
    #                dict(step="all")
    #            ])
    #        ),)
    #)
    fig.update_xaxes()
    return fig

def add_month_lines(output, date_weekday_weeknumber,click=None):
    kwargs = dict(mode='lines',
                  line=dict(color=COLOR_HEATMAP_LINES, width=1),
                  hoverinfo='skip')
    if click != None:
        datestring = click["points"][0]["text"].split(": ")[0]
        clickdate = dt.datetime.strptime(datestring, "%Y-%b-%d")
        if int(clickdate.strftime("%V")) in [52, 53] and clickdate.month == 1:
            clickweek = 0
        elif int(clickdate.strftime("%V")) == 1 and clickdate.month == 12:
            clickweek = 53
        else:
            clickweek = int(clickdate.strftime("%V"))
        clickday = clickdate.weekday()
        output += [
            go.Scatter(
                x=[clickweek - .5, clickweek  - .5],
                y=[clickday  + .5, clickday  - .5],
                **kwargs
            ),
            go.Scatter(
                x=[clickweek + .5, clickweek  + .5],
                y=[clickday  + .5, clickday  - .5],
                mode='lines',
                line=dict(color=COLOR_HEATMAP_LINES, width=1),
                hoverinfo='skip',fill='tonexty'
            ),
            go.Scatter(
                x=[clickweek - .5, clickweek  + .5],
                y=[clickday  + .5, clickday  + .5],
                **kwargs
            ),
            go.Scatter(
                x=[clickweek - .5, clickweek  + .5],
                y=[clickday  - .5, clickday  - .5],
                **kwargs
            )
        ]
    for date, dow, wkn in date_weekday_weeknumber:
        if date.day == 1:
            output += [
                go.Scatter(
                    x=[wkn - .5, wkn - .5],
                    y=[dow - .5, 6.5],
                    **kwargs
                )
            ]
            if dow:
                output += [
                    go.Scatter(
                        x=[wkn - .5, wkn + .5],
                        y=[dow - .5, dow - .5],
                        **kwargs
                    ),
                    go.Scatter(
                        x=[wkn + .5, wkn + .5],
                        y=[dow - .5, -.5],
                        **kwargs
                    )
                ]
    return output

def build_plot_sunburst(data_series, setting):
    if setting == 'production':
        data = {
            "names": ["Total", "Green", "Dark"] + GREEN_COLS + DARK_COLS,
            "parents": ["", "Total", "Total"] + ["Green" for col in GREEN_COLS] + ["Dark" for col in DARK_COLS],
            "values": data_series[["Total", "Total Green", "Total Dark"] + GREEN_COLS + DARK_COLS].values
        }
    elif setting in ["imports", "exports"]:
        ordered_names = ["Total"] + [name for name in data_series.index if "_" in name]
        names = [name.split("_")[1] if "_" in name else name for name in ordered_names]
        unique_names = list(set(names))
        if len(names) != len(unique_names):
            # When looking at e.g 'imports_total'
            values = [data_series[[name for name in data_series.index if unique_name in name.split("_")]].sum() for unique_name in unique_names]
            data = {
                "names": unique_names,
                "parents": ["Total" if name != "Total" else "" for name in unique_names],
                "values": values
            }
        else:
            values = data_series[ordered_names].values
            data = {
                "names": names,
                "parents": ["Total" if name != "Total" else "" for name in names],
                "values": values
            }
    else:
        raise ValueError(f"Sunburst plot for setting '{setting}' has not been implemented.")

    fig = go.Figure()
    unit = dict_units[setting]
    names = data['names']
    values = data['values']
    hover_text = [f'{n}: {np.round(values[names.index(n)],decimals=3)} {unit}' for n in names]
    color=[]
    for n in names:
        color.append(dict_colors[n])

    fig.add_trace(go.Sunburst(
        labels=data['names'],
        parents=data['parents'],
        values=data['values'],
        branchvalues="total",
        marker=dict(colors=color),
        hovertext = hover_text,
        hoverinfo = 'text'
        #color_discrete_map=dict_colors #, hover_data= {'names':True,'parents':False,'values':True}
    ))
    fig.update_layout(margin=dict(t=0, l=0, r=0, b=0))

    return fig

def build_plot_stackedarea(df, setting,stacked_type,pricearea,hoverfull):

    cols = None
    if setting == 'production':
        cols = ['Biomass', 'HydroPower', 'OtherRenewable', 'SolarPower', 'OnshoreWindPower', 'OffshoreWindPower', 'FossilGas', 'FossilHardCoal', 'FossilOil', 'Waste']
    elif setting == "consumption":
        cols = ["Value"]
    elif setting == 'co2':
        cols = ["CO2Emission"]
    elif setting == 'prices':
        cols = ["DE","DK1","DK2","NO2","SE4"]
    elif setting in ['imports', 'exports']:
        if pricearea == "DK1":
            cols = ["DK1_DE","DK1_NL","DK1_NO","DK1_DK2","DK1_SE","DK1_NORDIC"]
        elif  pricearea == "DK2":
            cols = [ "DK2_DE", "DK2_SE", "DK2_DK1"]
        else:
            cols= ["DK1_DE","DK1_NL","DK1_NO","DK1_SE","DK1_NORDIC", "DK2_DE", "DK2_SE"]
    else:
        raise ValueError(f"Stacked area plot for setting '{setting}' has not been implemented.")

    if stacked_type == "raw":
        df1=df[cols]

    elif stacked_type == "percentage":
        df1 = df[cols]
        df1 = df1.div(df1.sum(axis=1),axis=0)
        df1 = df1*100
    def getvar(st):return (np.var(df1[st]))

    df1.fillna(0, inplace=True)


    cols = sorted(cols,key=getvar)

    if setting in ['imports', 'exports']:
        country_cols = [col.split("_")[1] for col in cols]
        unique_cols = list(set(country_cols))
        for unique_col in unique_cols:
            df1[unique_col] = df1[[col for col in cols if unique_col in col]].sum(axis=1)
        cols = unique_cols

    fig = go.Figure()
    if cols is not None:
        for col in cols:
            if np.mean(df1[col]) != 0:

                unit = dict_units[setting] if stacked_type == 'raw' else '%'
                hover_text = [f'{date.strftime("%Y-%b-%d , %H:%M")}: {df1.loc[date, col].round(2)} {unit}, {col}' for date in df1.index]
                fig.add_trace(go.Scatter(
                    x = df1.index,
                    y = df1[col],
                    mode='lines',
                    name=col,
                    line=dict(width=0.5, color=dict_colors[col] if col in dict_colors.keys() else "#67a9cf"),
                    text=hover_text,
                    hoverinfo='text',
                    stackgroup='one' if setting != "prices" else None
            ))
    fig.update_layout(margin=dict(t=0, l=0, r=0, b=0),legend_y = 0.5, yaxis_title=f"{unit}")
    if  hoverfull == "Yes":
        fig.update_layout(hovermode='x', plot_bgcolor ="white")
    elif hoverfull == "No":
        fig.update_layout(hovermode='closest', plot_bgcolor="white")
    fig.update_xaxes(showline=True, linewidth=2, linecolor='black', gridcolor='white')
    fig.update_yaxes(showline=True, linewidth=2, linecolor='black', gridcolor='white')

    return fig
