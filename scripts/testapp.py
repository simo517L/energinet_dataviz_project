import dash
import pandas as pd

from dicts_and_lists import *
from dash_helper_functions import *
from dash.dependencies import Output, Input, State, MATCH, ALL


# TODO For timeseries make secondary plots update on selection
# TODO Figure out if possible for new plots to plot the already selected data (VIGTIG)
def build_app(data_handler):
    external_stylesheets = [dbc.themes.BOOTSTRAP]

    app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

    app.layout = dbc.Container([
        html.Div(id='selected-dates', children=[]),
        dcc.Store(id='data-storage-hourly'),
        dcc.Store(id='data-storage-daily'),

        dbc.Card([
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        choose_plot(1)
                    ], width=8),
                    dbc.Col([
                        choose_plot(2)
                    ], width=2),
                    dbc.Col([
                        choose_plot(3)
                    ], width=2)
                ])
            ])
        ]),

        dbc.Card([
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                dcc.Loading(
                                    html.Div(id={'type': 'plot', 'index': 1}, children=[],  style={'height': '90vh'}),
                                    type="circle",
                                    style={'height': '90vh'}
                                )
                            ], style={'height': '90vh'})
                        ])
                    ], width=8),
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                dcc.Loading(
                                    html.Div(id={'type': 'plot', 'index': 2}, children=[],  style={'height': '45vh'}),
                                    type="circle",
                                    style={'height': '45vh'}
                                )
                            ], style={'height': '45vh'})
                        ]),
                        dbc.Card([
                            dbc.CardBody([
                                dcc.Loading(
                                    html.Div(id={'type': 'plot', 'index': 3}, children=[],  style={'height': '45vh'}),
                                    type="circle",
                                    style={'height': '45vh'}
                                )
                            ], style={'height': '45vh'})
                        ]),
                    ], width=4),
                ]),
            ])
        ])
    ], style={'width': '95vw', 'height': '100vh'}, fluid=True)

    @app.callback(
        Output(component_id={'type': 'plot', 'index': MATCH}, component_property='children'),
        Input(component_id={'type': 'plot_selector', 'index': MATCH}, component_property='value'),
        State(component_id={'type': 'plot_selector', 'index': MATCH}, component_property='id')
    )
    def update_plot(value, id):
        index = id['index']
        height = '90%' if index == 1 else '85%'
        if value in ["heatmap", "timeseries"]:
            return [*build_setting_selector_for_selectorchart(value, index), dcc.Graph(id="selector_chart", figure=go.Figure(), style={'height': height})]

        elif value == "sunburst":
            return [*build_setting_selector_sunburst(index), dcc.Graph(id={'type': "sunburst", 'index': index}, figure=go.Figure(), style={'height': height})]

        elif value == "stacked":
            return [*build_setting_selector_stacked(index), dcc.Graph(id={'type': "stacked-area", 'index': index}, figure=go.Figure(), style={'height': height})]


    @app.callback(
        Output(component_id='subsetting_selector_chart', component_property='options'),
        Output(component_id='subsetting_selector_chart', component_property='value'),
        Input(component_id='setting_selector_chart', component_property='value'),
        Input(component_id="pricearea_selector_chart", component_property="value"),
        State(component_id={'type': 'plot_selector', 'index': 1}, component_property='value')
    )
    def update_selector_chart_subsetting_options(setting, pricearea, plottype):
        if plottype == "heatmap":
            df = data_handler.dataframes[f"{setting}_daily"].copy()
        elif plottype == "timeseries":
            df = data_handler.dataframes[f"{setting}"].copy()
        else:
            df = pd.DataFrame()

        if setting == "exchange" and pricearea != 'total':
            df = df[[col for col in df.columns if (pricearea in col) or col in ["HourDK"]]]
        cols = df.columns
        cols = [col for col in cols if col not in ['HourDK', 'PriceArea']]

        options = [{'label': col, 'value': col} for col in cols]
        if setting == "production":
            value = "Total"
        elif setting == 'exchange':
            value = f'Total {pricearea}' if pricearea != 'total' else 'Total'
        elif setting == "consumption":
            value = "Value"
        elif setting == 'co2':
            value = "CO2Emission"
        elif setting == "prices":
            value = "DK1"
        else:
            raise ValueError(f"Selector plot setting, {setting}, not implemented yet")
        return options, value

    @app.callback(
        Output(component_id="pricearea_selector_chart", component_property="options"),
        Output(component_id="pricearea_selector_chart", component_property="value"),
        Input(component_id="setting_selector_chart", component_property="value"),
        prevent_initial_call=True
    )
    def update_heatmap_pricearea(setting):
        options = [{'label': 'Total', 'value': 'total'},
                   {'label': 'DK1', 'value': 'DK1'},
                   {'label': 'DK2', 'value': 'DK2'}]
        value = "DK1"

        if setting == "co2":
            options = [{'label': 'Total', 'value': 'total','disabled':True}],
            value = "total"
        elif setting == "prices":
            options = [{'label': 'DK1', 'value': 'DK1', 'disabled':True}]
            value = "DK1"

        return options, value

    @app.callback(
        Output(component_id="selector_chart", component_property="figure"),
        Input(component_id="pricearea_selector_chart", component_property="value"),
        Input(component_id="setting_selector_chart", component_property="value"),
        Input(component_id='subsetting_selector_chart', component_property='value'),
        Input(component_id='selector_chart', component_property='clickData'),
        Input(component_id="selector_chart_checkbox", component_property="value"),
        State(component_id="selector_chart", component_property="figure"),
        State(component_id={'type': 'plot_selector', 'index': 1}, component_property='value'),
        Input(component_id="selector_granularity", component_property="value"),
        prevent_initial_call=True
    )
    def update_selector_chart(pricearea, setting, subsetting, click, checkbox, fig, plottype,gran_setting):
        trigger = dash.callback_context.triggered[0]['prop_id'].split('.')[0]
        if plottype == "heatmap":
            dataframe = f"{setting}_daily"
            granularity = "D"
        elif plottype == "timeseries":
            dataframe = setting
            if gran_setting == "Day":
                granularity = "D"
            elif gran_setting == "Hour":
                granularity = "H"
        else:
            return go.Figure()

        df = data_handler.dataframes[dataframe].copy()
        if "PriceArea" in df.columns:
            if pricearea != "total":
                df = df[df["PriceArea"].isin([pricearea])]
            else:
                df.drop("PriceArea", inplace=True, axis=1)

        elif setting == "exchange":
            if "DK" in pricearea:
                df = df[[col for col in df.columns if (pricearea in col) or col in ["HourDK"]]]
        elif setting == "prices":
            df = df[["HourDK", subsetting]]
        df.set_index("HourDK", inplace=True)
        if setting == "prices":
            df = df.groupby([pd.Grouper(level='HourDK', freq=granularity)]).mean()
        else:
            df = df.groupby([pd.Grouper(level='HourDK', freq=granularity)]).sum()
        df.index = pd.to_datetime(df.index)

        data = df[subsetting]
        if plottype == "heatmap":
            if len(checkbox) > 0 and checkbox[0] == "on":
                fig = build_plot_heatmap(data, header=f"{subsetting} {setting} ({dict_units[setting]})", setting=setting, click=click)
            elif trigger == "selector_chart_checkbox":
                fig = build_plot_heatmap(data, header=f"{subsetting} {setting} ({dict_units[setting]})", setting=setting, click=None)
        elif plottype == "timeseries" and trigger != "selector_chart": #Shoudn't redraw if just triggered by clicking a date.
            fig = build_plot_timeseries(data, header=f"{subsetting} {setting} ({dict_units[setting]})", setting=setting, shareY=True if len(checkbox) > 0 else False)
        return fig

    @app.callback(
        Output(component_id={'type': "sunburst", 'index': MATCH}, component_property='figure'),
        Input(component_id="selector_chart", component_property='clickData'),
        Input(component_id={'type': "setting_sunburst", 'index': MATCH}, component_property="value"),
        Input(component_id={'type': "pricearea_sunburst", 'index': MATCH}, component_property="value"),
        State(component_id={'type': 'plot_selector', 'index': 1}, component_property='value'),
        prevent_initial_call=True
    )
    def update_sunburst_plot(selection, setting, pricearea, plottype):
        datestring = selection["points"][0]["text"].split(": ")[0]
        if plottype == "heatmap":
            date = dt.datetime.strptime(datestring, "%Y-%b-%d")
        elif plottype == "timeseries":
            date = dt.datetime.strptime(datestring, "%Y-%b-%d %H:%M:%S").date()
            date = dt.datetime(date.year, date.month, date.day)

        df = data_handler.dataframes[f"{setting}_daily"].copy()
        df = df.set_index('HourDK')
        if setting == "production":
            if pricearea != "total":
                df = df[df["PriceArea"].isin([pricearea])]
            else:
                df.drop("PriceArea", inplace=True, axis=1)
                df = df.groupby([pd.Grouper(level='HourDK', freq='D')]).sum()
        elif setting in ["imports", "exports"]:
            if pricearea != "total":
                cols = [col for col in df.columns if col.split("_")[0] == pricearea]
            else:
                cols = [col for col in df.columns if col not in ["DK1_DK2", "DK2_DK1"]]
            df = df[cols]
            df["Total"] = df.sum(axis=1)
        df.index = pd.to_datetime(df.index)

        data = df.loc[date]

        fig = build_plot_sunburst(data, setting=setting)
        return fig


    @app.callback(
        Output(component_id={'type': "pricearea_stacked", 'index': MATCH}, component_property="options"),
        Output(component_id={'type': "pricearea_stacked", 'index': MATCH}, component_property="value"),
        Output(component_id={'type': "stacked_type", 'index': MATCH}, component_property="options"),
        Output(component_id={'type': "stacked_type", 'index': MATCH}, component_property="value"),
        Input(component_id={'type': "setting_stacked", 'index': MATCH}, component_property="value"),
        State(component_id={'type': "pricearea_stacked", 'index': MATCH}, component_property="value"),
        State(component_id={'type': "stacked_type", 'index': MATCH}, component_property="value"),
        prevent_initial_call=True
    )
    def update_stackedarea_pricearea(setting, value, value2):
        value = "DK1"
        value2 = "raw"
        options = [{'label': 'Total', 'value': 'total'},
                   {'label': 'DK1', 'value': 'DK1'},
                   {'label': 'DK2', 'value': 'DK2'}]
        options2 = [
                {'label': 'Raw values', 'value': 'raw'},
                {'label': 'Sum to 100', 'value': 'percentage'}
            ]

        if setting == "co2":
            options = [{'label': 'Total', 'value': 'total','disabled':True}]
            value = "total"
            options2 = [{'label': 'Raw values', 'value': 'raw','disabled':True}]
            value2 = "raw"
        elif setting == "prices":
            options = [
                       {'label': 'DK', 'value': 'DK', 'disabled':True}]
            value = "DK"
            options2 = [{'label': 'Raw values', 'value': 'raw','disabled':True}]
            value2 = "raw"

        return options, value, options2, value2



    @app.callback(
        Output(component_id={'type': "stacked-area", 'index': MATCH}, component_property='figure'),
        Input(component_id="selector_chart", component_property='clickData'),
        Input(component_id={'type': "pricearea_stacked", 'index': MATCH}, component_property="value"),
        Input(component_id={'type': "setting_stacked", 'index': MATCH}, component_property="value"),
        Input(component_id={'type': "stacked_type", 'index': MATCH}, component_property="value"),
        Input(component_id={'type': "hoverinfo_checkbox", 'index': MATCH}, component_property="value"),
        State(component_id={'type': 'plot_selector', 'index': 1}, component_property='value'),
        prevent_initial_call=True
    )
    def update_stackedarea_plot(selection, pricearea, setting, stacked_type, hoverfull,plottype):
        datestring = selection["points"][0]["text"].split(": ")[0]
        if plottype == "heatmap":
            date = dt.datetime.strptime(datestring, "%Y-%b-%d")
        elif plottype == "timeseries":
            date = dt.datetime.strptime(datestring, "%Y-%b-%d %H:%M:%S").date()
            date = dt.datetime(date.year, date.month, date.day)

        df = data_handler.dataframes[f"{setting}"]  # pd.read_json(df, orient='split')

        if pricearea == "total":
            if "PriceArea" in df.columns:
                df1 = df[df["PriceArea"].isin(["DK1"])]
                df2 = df[df["PriceArea"].isin(["DK2"])]
                df1 = df1.set_index('HourDK')
                df2 = df2.set_index('HourDK')
                df1 = df1.drop("PriceArea", axis=1)
                df2 = df2.drop("PriceArea", axis=1)
                df = df1.add(df2,fill_value=0)
            else:
                df = df.set_index('HourDK')
        elif "PriceArea" in df.columns:
            df = df[df["PriceArea"].isin([pricearea])]
            df = df.set_index('HourDK')
        else:
            df = df.set_index('HourDK')
        df.index = pd.to_datetime(df.index)

        data = df[df.index.date == date.date()]

        if len( hoverfull) > 0 and  hoverfull[0] == "on":
            fig = build_plot_stackedarea(data, setting=setting, stacked_type=stacked_type , pricearea=pricearea,hoverfull="Yes")
        else:
            fig = build_plot_stackedarea(data, setting=setting, stacked_type=stacked_type, pricearea=pricearea,
                                         hoverfull="No")
        return fig


    return app
