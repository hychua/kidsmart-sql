import dash
from dash import dcc
from dash import html
import dash_split_pane
from dash.dependencies import Input, Output, State
from dash import dash_table
import plotly.express as px
import dash_daq as daq
import pandas as pd
import numpy as np
import math
from apps.analytics import( create_plot_metric, 
                                    YEARS_INVENTORY,
                                    querydatafromdatabase,
                                    modifydatabase
                                    )
import base64
import psycopg2
from dash.exceptions import PreventUpdate
import datetime
import io
from app import app
from sqlalchemy import create_engine


engine = create_engine('postgresql://kidsmart_6_user:xKtAHODVAHVwDJRYh04S4Xu8p7n6Sd0l@dpg-ctn13a9opnds73fjd03g-a.oregon-postgres.render.com:5432/kidsmart_6')

# Create layout

# start from dashboard.py

# will be dcc.Dropdown multi = True or checkbox
FILTERS = ['Order Year','Region_ID','Category_ID','Product_ID','Store_ID','City_ID']

# will be dcc.Dropdown multi = False
METRIC_TYPES = [
    'total_sales',
    'count_sales',
    'avg_sales',
    'curr_inventory',
    'curr_inventory2',
    'top_performers',
    'bottom_performers',
    'avg_net_profit',
    'top_avg_net_profit',
    'bottom_avg_net_profit',
    'avg_inventory_turnover',
    'top_avg_inventory_turnover',
    'bottom_avg_inventory_turnover',
    'sales_over_time',
    'reorder_point',
    'economic_order_quantity'
]

METRIC_DICT = {
    'total_sales': 'Total Sales',
    'count_sales':'Sales Count',
    'avg_sales':'Avg Sales',
    'curr_inventory':'Order Quantity',
    'curr_inventory2':'Current Inventory 2',
    'top_performers':'Net Profit',
    'bottom_performers':'Net Profit',
    'avg_net_profit':'Avg Net Profit',
    'top_avg_net_profit':'Avg Net Profit',
    'bottom_avg_net_profit':'Avg Net Profit',
    'avg_inventory_turnover':'Inventory Turnover',
    'top_avg_inventory_turnover':'Inventory Turnover',
    'bottom_avg_inventory_turnover':'Inventory Turnover',
    'sales_over_time': 'Sales Over Time',
    'reorder_point': 'Reorder Point',
    'economic_order_quantity': 'Quantity to Reorder'
}

layout1 = html.Div([
    
            dash_split_pane.DashSplitPane(
                children=[# start sliders
                            html.Div(
                                
                                children=[
                                    
                                    html.Div(
                                        id="slider-container",
                                        children=[
                                            html.P(
                                                id="slider-text",
                                                children="Drag the slider to change the year:",
                                            ),
                                            dcc.Slider(
                                                id="years-slider",
                                                min=min(YEARS_INVENTORY),
                                                max=max(YEARS_INVENTORY),
                                                value=max(YEARS_INVENTORY)-1,
                                                marks={
                                                    str(year): {
                                                        "label": str(year),
                                                        #"style": {"color": "#7fafdf"},
                                                    }
                                                    for year in YEARS_INVENTORY
                                                },
                                            ),
                                        ],
                                    ),
                                    html.Br(),
                                    html.Br(),
                                    html.Br(),
                                    html.P(id="chart-selector",children="Select Chart:"),
                                    dcc.Dropdown(
                                        options = [
                                            {
                                                "label": "Total Sales",
                                                "value":"total_sales"
                                            },
             
                                            {
                                                "label": "Average Sales per Order",
                                                "value":"avg_sales",
                                            },

                                            {
                                                "label": "Top Performers",
                                                "value":"top_performers",
                                            },
                                            {
                                                "label": "Bottom Performers",
                                                "value":"bottom_performers",
                                            },

                                            {
                                                "label": "Top Avg Net Profit",
                                                "value":"top_avg_net_profit",
                                            },
                                            {
                                                "label": "Bottom Avg Net Profit",
                                                "value":"bottom_avg_net_profit",
                                            },
                                            

                                        ],
                                        value = "total_sales",
                                        id="chart-dropdown",
                                        multi = False
                                    ), # End Dropdown
                                    
                                    html.P(id="variable-selector",children="Select Variable:"),
                                    dcc.Dropdown(
                                        options = [
                                            {
                                                "label": "Buyer Region",
                                                "value":"buyer_region"
                                            },
             
                                            {
                                                "label": "Buyer City",
                                                "value":"buyer_city",
                                            },

                                            {
                                                "label": "Product Category",
                                                "value":"category",
                                            },
                                                                                 
                                        ],
                                        value = "buyer_city",
                                        id="variable-dropdown",
                                        multi = False
                                    ),
                                    
                                    html.Div(
                                    children=[
                                        html.P(id="site-dropdown-text",
                                        children="Choose Site: "),
                                        dcc.Dropdown(
                                            id="site-dropdown",
                                            options = [
                                            {
                                                "label": "Store A",
                                                "value":"A"
                                            },
             
                                            {
                                                "label": "Store B",
                                                "value":"B",
                                            },

                                            {
                                                "label": "Online",
                                                "value":"Online",
                                            },
                                                                                 
                                        ],
                                            #value = [],
                                            multi= False ,                           
                                        ),

                                    ]
                                )
                                    
                                    # End Dropdown
                                    ]),
                            #end sliders
              
                
                #start second graphs                                    
                            html.Div(id="sales-app-container",
                                className="row",
                                )
                            # end second graphs
                ],
    id="splitter",
    split="vertical",
    size='25%'
)

])

layout2 = html.Div([
    
                dash_split_pane.DashSplitPane(
                        children=[html.Div([html.Div(
                                            id="slider-container",
                                            children=[
                                                html.P(
                                                    id="slider-text",
                                                    children="Drag the slider to change the year:",
                                                ),
                                                dcc.Slider(
                                                    id="years-slider",
                                                    min=min(YEARS_INVENTORY),
                                                    max=max(YEARS_INVENTORY),
                                                    value=max(YEARS_INVENTORY)-1,
                                                    marks={
                                                        str(year): {
                                                            "label": str(year),
                                                            #"style": {"color": "#7fafdf"},
                                                        }
                                                        for year in YEARS_INVENTORY
                                                    },
                                                ),
                                            ],
                                        ),
                        html.Br(),
                        html.Br(),
                        # START BOTTOM DIV 1 
                        html.Br(),
                                    html.P(id="metric-selector",children="Select Metric:"),
                                    dcc.Dropdown(
                                        options = [
                                            {
                                                "label": "Inventory Gauge with Reorder Point",
                                                "value":"inventory_metrics",
                                            },
                                            
                                            {
                                                "label": "Highest Turnover",
                                                "value":"top_turnover"
                                            },
             
                                            {
                                                "label": "Lowest Tunrover",
                                                "value":"bottom_turnover",
                                            },
                               
                                        ],
                                        value = "inventory_metrics",
                                        id="metric-dropdown",
                                        multi = False
                                    ), # End Dropdown
                        html.Div(
                            id="app-container-2",
                            children=[
                                html.Div(
                                    children=[
                                        html.P(id="category-dropdown-text",
                                        children="Choose Category: "),
                                        dcc.Dropdown(
                                            id="category-dropdown",
                                            options = [],   
                                            value=[],
                                            multi= True ,                           
                                        ),

                                    ]
                                ),
                                html.Div(
                                    children=[
                                        html.P(id="product-dropdown-text",
                                        children="Choose Product: "),
                                        dcc.Dropdown(
                                            id="product-dropdown",
                                            options = [],   
                                            value=[],
                                            multi= True ,                           
                                        ),

                                    ]
                                ),
                                html.Div(
                                    children=[
                                        html.P(id="regions-dropdown-text",
                                        children="Choose Region: "),
                                        dcc.Dropdown(
                                            id="region-dropdown",
                                            #options=[{'label': k, 'value':k} for k in ALL_REGIONS],
                                            value=[],
                                            multi= True ,                           
                                        ),

                                    ]
                                ),
                                html.Div(
                                    children=[
                                        html.P(id="shoe-sizes-dropdown-text",
                                        children="Choose Site: "),
                                        dcc.Dropdown(
                                            id="shoe-size-dropdown",
                                            options = [
                                            {
                                                "label": "Store A",
                                                "value":"A"
                                            },
             
                                            {
                                                "label": "Store B",
                                                "value":"B",
                                            },

                                            {
                                                "label": "Online",
                                                "value":"Online",
                                            },
                                                                                 
                                        ],
                                            value=[],
                                            multi= True ,                           
                                        ),

                                    ]
                                )
                                ])
                            
                ]),
                
                html.Div([
                    
                        html.Div(id="app-container-3",
                                 className="row")

                ])
                ],
    id="splitter",
    split="vertical",
    size='25%'
)

])

sale_page = html.Div([html.Hr(),
                                    
                    html.A('Upload Order.completed.xlsx or sale.csv File'),
                
                    html.Hr(),
                
                    dcc.Upload(
                        id='upload-data',
                        children=html.Div([
                            'Drag and Drop or ',
                            html.A('Select Files')
                        ]),
                        style={
                            'width': '75%',
                            'height': '60px',
                            'lineHeight': '60px',
                            'borderWidth': '1px',
                            'borderStyle': 'dashed',
                            'borderRadius': '5px',
                            'textAlign': 'center',
                            'margin': '10px'
                        },
                        # Allow multiple files to be uploaded
                        multiple=True
                    ),
                    html.Div([
                        
                          html.Br(),
                          html.Button(
                            id='sale-save-button',
                            n_clicks=0,
                            children='Save Sales',
                            style={'fontsize':14,
                           'color':'rgb(255,255,255)',
                           'backgroundColor':'#1f2630',
                           'borderRadius':5,
                           'height':38}),
                          html.Br(),
                          ],
                                 ),
                    
                    html.Div(id='output-data-upload'),
                    html.Br(),
                    
                    html.P(id='sale-notif'),
                    ])

sale_product_page = html.Div([html.Hr(),
                
                    html.A('Upload sale_product.csv File'),
                
                    html.Hr(),
                
                    dcc.Upload(
                        id='upload-data8',
                        children=html.Div([
                            'Drag and Drop or ',
                            html.A('Select Files')
                        ]),
                        style={
                            'width': '75%',
                            'height': '60px',
                            'lineHeight': '60px',
                            'borderWidth': '1px',
                            'borderStyle': 'dashed',
                            'borderRadius': '5px',
                            'textAlign': 'center',
                            'margin': '10px'
                        },
                        # Allow multiple files to be uploaded
                        multiple=True
                    ),
                    html.Div([
                        
                          html.Br(),
                          html.Button(
                            id='sale-product-save-button',
                            n_clicks=0,
                            children='Save Sale Items',
                            style={'fontsize':14,
                           'color':'rgb(255,255,255)',
                           'backgroundColor':'#1f2630',
                           'borderRadius':5,
                           'height':38}),
                          html.Br(),
                          ],
                                 ),
                    html.Div(id='output-data-upload8'),
                        
                    html.P(id='sale-product-notif'),
                    ])

po_page = html.Div([html.Hr(),
                
                    html.A('Upload po.csv File'),
                
                    html.Hr(),
                
                    dcc.Upload(
                        id='upload-data2',
                        children=html.Div([
                            'Drag and Drop or ',
                            html.A('Select Files')
                        ]),
                        style={
                            'width': '75%',
                            'height': '60px',
                            'lineHeight': '60px',
                            'borderWidth': '1px',
                            'borderStyle': 'dashed',
                            'borderRadius': '5px',
                            'textAlign': 'center',
                            'margin': '10px'
                        },
                        # Allow multiple files to be uploaded
                        multiple=True
                    ),
                    html.Div([
                        
                          html.Br(),
                          html.Button(
                            id='po-save-button',
                            n_clicks=0,
                            children='Save PO',
                            style={'fontsize':14,
                           'color':'rgb(255,255,255)',
                           'backgroundColor':'#1f2630',
                           'borderRadius':5,
                           'height':38}),
                          html.Br(),
                          ],
                                 ),
                    html.Div(id='output-data-upload2'),
                        
                    html.P(id='po-notif'),
                    ])

po_product_page = html.Div([html.Hr(),
                
                    html.A('Upload po_product.csv File'),
                
                    html.Hr(),
                
                    dcc.Upload(
                        id='upload-data9',
                        children=html.Div([
                            'Drag and Drop or ',
                            html.A('Select Files')
                        ]),
                        style={
                            'width': '75%',
                            'height': '60px',
                            'lineHeight': '60px',
                            'borderWidth': '1px',
                            'borderStyle': 'dashed',
                            'borderRadius': '5px',
                            'textAlign': 'center',
                            'margin': '10px'
                        },
                        # Allow multiple files to be uploaded
                        multiple=True
                    ),
                    html.Div([
                        
                          html.Br(),
                          html.Button(
                            id='po-product-save-button',
                            n_clicks=0,
                            children='Save PO Items',
                            style={'fontsize':14,
                           'color':'rgb(255,255,255)',
                           'backgroundColor':'#1f2630',
                           'borderRadius':5,
                           'height':38}),
                          html.Br(),
                          ],
                                 ),
                    html.Div(id='output-data-upload9'),
                        
                    html.P(id='po-product-notif'),
                    ])

category_page = html.Div([html.Hr(),
                
                    html.A('Upload category.csv File'),
                
                    html.Hr(),
                
                    dcc.Upload(
                        id='upload-data3',
                        children=html.Div([
                            'Drag and Drop or ',
                            html.A('Select Files')
                        ]),
                        style={
                            'width': '75%',
                            'height': '60px',
                            'lineHeight': '60px',
                            'borderWidth': '1px',
                            'borderStyle': 'dashed',
                            'borderRadius': '5px',
                            'textAlign': 'center',
                            'margin': '10px'
                        },
                        # Allow multiple files to be uploaded
                        multiple=True
                    ),
                    html.Div([
                        
                          html.Br(),
                          html.Button(
                            id='cat-save-button',
                            n_clicks=0,
                            children='Save Category',
                            style={'fontsize':14,
                           'color':'rgb(255,255,255)',
                           'backgroundColor':'#1f2630',
                           'borderRadius':5,
                           'height':38}),
                          html.Br(),
                          ],
                                 ),
                    html.Div(id='output-data-upload3'),
                    
                    html.P(id='cat-notif'),
                    ])

store_page = html.Div([html.Hr(),
                
                    html.A('Upload store.csv File'),
                
                    html.Hr(),
                
                    dcc.Upload(
                        id='upload-data4',
                        children=html.Div([
                            'Drag and Drop or ',
                            html.A('Select Files')
                        ]),
                        style={
                            'width': '75%',
                            'height': '60px',
                            'lineHeight': '60px',
                            'borderWidth': '1px',
                            'borderStyle': 'dashed',
                            'borderRadius': '5px',
                            'textAlign': 'center',
                            'margin': '10px'
                        },
                        # Allow multiple files to be uploaded
                        multiple=True
                    ),
                    html.Div([
                        
                          html.Br(),
                          html.Button(
                            id='store-save-button',
                            n_clicks=0,
                            children='Save Store',
                            style={'fontsize':14,
                           'color':'rgb(255,255,255)',
                           'backgroundColor':'#1f2630',
                           'borderRadius':5,
                           'height':38}),
                          html.Br(),
                          ],
                                 ),
                    html.Div(id='output-data-upload4'),
                    
                    html.P(id='store-notif'),
                    ])

region_page = html.Div([html.Hr(),
                
                    html.A('Upload region.csv File'),
                
                    html.Hr(),
                
                    dcc.Upload(
                        id='upload-data5',
                        children=html.Div([
                            'Drag and Drop or ',
                            html.A('Select Files')
                        ]),
                        style={
                            'width': '75%',
                            'height': '60px',
                            'lineHeight': '60px',
                            'borderWidth': '1px',
                            'borderStyle': 'dashed',
                            'borderRadius': '5px',
                            'textAlign': 'center',
                            'margin': '10px'
                        },
                        # Allow multiple files to be uploaded
                        multiple=True
                    ),
                    html.Div([
                        
                          html.Br(),
                          html.Button(
                            id='region-save-button',
                            n_clicks=0,
                            children='Save Region',
                            style={'fontsize':14,
                           'color':'rgb(255,255,255)',
                           'backgroundColor':'#1f2630',
                           'borderRadius':5,
                           'height':38}),
                          html.Br(),
                          ],
                                 ),
                    html.Div(id='output-data-upload5'),
                    
                    html.P(id='region-notif'),
                    ])

city_page = html.Div([html.Hr(),
                
                    html.A('Upload city.csv File'),
                
                    html.Hr(),
                
                    dcc.Upload(
                        id='upload-data6',
                        children=html.Div([
                            'Drag and Drop or ',
                            html.A('Select Files')
                        ]),
                        style={
                            'width': '75%',
                            'height': '60px',
                            'lineHeight': '60px',
                            'borderWidth': '1px',
                            'borderStyle': 'dashed',
                            'borderRadius': '5px',
                            'textAlign': 'center',
                            'margin': '10px'
                        },
                        # Allow multiple files to be uploaded
                        multiple=True
                    ),
                    html.Div([
                        
                          html.Br(),
                          html.Button(
                            id='city-save-button',
                            n_clicks=0,
                            children='Save City',
                            style={'fontsize':14,
                           'color':'rgb(255,255,255)',
                           'backgroundColor':'#1f2630',
                           'borderRadius':5,
                           'height':38}),
                          html.Br(),
                          ],
                                 ),
                    html.Div(id='output-data-upload6'),
                    
                    html.P(id='city-notif'),
                    ])

product_page = html.Div([html.Hr(),
                
                    html.A('Upload product.csv File'),
                
                    html.Hr(),
                
                    dcc.Upload(
                        id='upload-data7',
                        children=html.Div([
                            'Drag and Drop or ',
                            html.A('Select Files')
                        ]),
                        style={
                            'width': '75%',
                            'height': '60px',
                            'lineHeight': '60px',
                            'borderWidth': '1px',
                            'borderStyle': 'dashed',
                            'borderRadius': '5px',
                            'textAlign': 'center',
                            'margin': '10px'
                        },
                        # Allow multiple files to be uploaded
                        multiple=True
                    ),
                    html.Div([
                        
                          html.Br(),
                          html.Button(
                            id='product-save-button',
                            n_clicks=0,
                            children='Save Product',
                            style={'fontsize':14,
                           'color':'rgb(255,255,255)',
                           'backgroundColor':'#1f2630',
                           'borderRadius':5,
                           'height':38}),
                          html.Br(),
                          ],
                                 ),
                    html.Div(id='output-data-upload7'),
                        
                    html.P(id='product-notif'),
                    ])

online_page = html.Div([html.Hr(),
                
                    html.A('Upload Order.completed.YYYYMMDD.csv File'),
                
                    html.Hr(),
                
                    dcc.Upload(
                        id='upload-data10',
                        children=html.Div([
                            'Drag and Drop or ',
                            html.A('Select Files')
                        ]),
                        style={
                            'width': '75%',
                            'height': '60px',
                            'lineHeight': '60px',
                            'borderWidth': '1px',
                            'borderStyle': 'dashed',
                            'borderRadius': '5px',
                            'textAlign': 'center',
                            'margin': '10px'
                        },
                        # Allow multiple files to be uploaded
                        multiple=True
                    ),
                    html.Div([
                        
                          html.Br(),
                          html.Button(
                            id='online-save-button',
                            n_clicks=0,
                            children='Save Online Sales',
                            style={'fontsize':14,
                           'color':'rgb(255,255,255)',
                           'backgroundColor':'#1f2630',
                           'borderRadius':5,
                           'height':38}),
                          html.Br(),
                          ],
                                 ),
                    html.Div(id='output-data-online'),
                        
                    html.P(id='online-notif'),
                    ])


# Create call back functions

# sales graphs
@app.callback(
    Output("selected-data", "figure"),
    [
        Input("chart-dropdown", "value"),
        Input("years-slider", "value"),
        Input("site-dropdown", "value")
    ],
)
def display_selected_data(selected_data, year, Store_ID):

    filters = ['Order Year','Region_ID','Store_ID']
    metric_type = selected_data
    curr_metric_col = METRIC_DICT[metric_type]
    curr_year = year

    df = create_plot_metric(filters,metric_type)
    dff = df[df['Order Year'] == curr_year]
    if Store_ID == None:
        filters = ['Order Year', 'Region_ID']
        metric_type = selected_data
        df = create_plot_metric(filters,metric_type)
        dff = df[df['Order Year'] == curr_year]
    elif (len(Store_ID) == 1):
        dff = dff[dff['Store_ID'] == Store_ID]
    else:
        filters = ['Order Year', 'Region_ID']
        metric_type = selected_data
        df = create_plot_metric(filters,metric_type)
        dff = df[df['Order Year'] == curr_year]


    #dff = dff.sort_values(by=[curr_metric_col],ascending=[False])

    if selected_data == "total_sales":

        dff['Store_ID'] = np.sqrt(dff[curr_metric_col])
        dff['Store_ID'] = np.sqrt(dff['Store_ID']).round(0)
        

        fig = px.scatter(dff, x="Region_ID", y=curr_metric_col, color="Region_ID",
                          size = 'Store_ID', hover_data=[curr_metric_col])



        fig.update_layout(
            title = f'Regional Retail: {curr_metric_col} {curr_year}',
            #paper_bgcolor="#1f2630",
            plot_bgcolor="#D3D3D3",
            #margin=dict(t=75, r=50, b=100, l=50),
            font=dict(color="#000000")

        )
        return fig


    if selected_data == "count_sales":
        pass

    if selected_data == "avg_sales":

        fig = px.histogram(dff, x='Region_ID', y=curr_metric_col,
                    #title='Histogram of bills',
                    labels={'x':'Region_ID', 'y':curr_metric_col }, # can specify one label per df column
                    opacity=.8,
                    log_y=True, # represent bars with log scale
                    color_discrete_sequence=['deepskyblue'] # color of histogram bars
                    )


        fig.update_layout(
            title = f'Regional Retail: {curr_metric_col}',
            #paper_bgcolor="#1f2630",
            plot_bgcolor="#D3D3D3",
            #margin=dict(t=75, r=50, b=100, l=50),
            font=dict(color="#000000")

        )
        return fig

    # will be a table and gauge
    if selected_data == "curr_inventory":
        pass


    if selected_data == "top_performers":
        values = dff[curr_metric_col]
        names = dff['Region_ID'].unique()
  
        fig = px.pie(dff, values=values, names=names, color=names,)




        fig.update_layout(
            title = f'Regional Retail: Top {curr_metric_col}',
            #paper_bgcolor="#1f2630",
            plot_bgcolor="#D3D3D3",
            #margin=dict(t=75, r=50, b=100, l=50),
            font=dict(color="#000000")

        )
        return fig


    if selected_data == "bottom_performers":
        values = dff[curr_metric_col]
        names = dff['Region_ID'].unique()
  
        fig = px.pie(dff, values=values, names=names, color=names,)




        fig.update_layout(
            title = f'Regional Retail: Bottom {curr_metric_col}',
            #paper_bgcolor="#1f2630",
            plot_bgcolor="#D3D3D3",
            #margin=dict(t=75, r=50, b=100, l=50),
            font=dict(color="#000000")

        )
        return fig



    if selected_data == "avg_net_profit":
        pass


    if selected_data == "top_avg_net_profit":
        fig = px.bar(dff, x='Region_ID', y =curr_metric_col , color=curr_metric_col,
                     hover_data = ['Region_ID']
        
        )




        fig.update_layout(
            title = f'Regional Retail: Top {curr_metric_col}',
            #paper_bgcolor="#1f2630",
            plot_bgcolor="#D3D3D3",
            #margin=dict(t=75, r=50, b=100, l=50),
            font=dict(color="#000000")

        )
        return fig


    if selected_data == "bottom_avg_net_profit":
        fig = px.bar(dff, x='Region_ID', y =curr_metric_col , color=curr_metric_col,
                     hover_data = ['Region_ID']
        
        )




        fig.update_layout(
            title = f'Regional Retail: Bottom {curr_metric_col}',
            #paper_bgcolor="#1f2630",
            plot_bgcolor="#D3D3D3",
            #margin=dict(t=75, r=50, b=100, l=50),
            font=dict(color="#000000")

        )
        return fig





    if selected_data == "avg_inventory_turnover":
        pass


    if selected_data == "top_avg_inventory_turnover":
        pass

    if selected_data == "bottom_avg_inventory_turnover":
        pass



# sales graph 2
@app.callback(
    Output("selected-data2", "figure"),
    [
        Input("chart-dropdown", "value"),
        Input("years-slider", "value"),
        Input("site-dropdown", "value")
    ],
)
def display_selected_data2(selected_data, year, Store_ID):

    filters = ['Order Year','Category_ID','Store_ID']
    metric_type = selected_data
    curr_metric_col = METRIC_DICT[metric_type]
    curr_year = year

    df = create_plot_metric(filters,metric_type)
    dff = df[df['Order Year'] == curr_year]
    if Store_ID == None:
        filters = ['Order Year', 'Category_ID']
        metric_type = selected_data
        df = create_plot_metric(filters,metric_type)
        dff = df[df['Order Year'] == curr_year]
    elif (len(Store_ID) == 1):
        dff = dff[dff['Store_ID'] == Store_ID]
    else:
        filters = ['Order Year', 'Category_ID']
        metric_type = selected_data
        df = create_plot_metric(filters,metric_type)
        dff = df[df['Order Year'] == curr_year]

    
    #dff = dff.sort_values(by=[curr_metric_col],ascending=[False])
    
    # define categories
    sql3 = "SELECT * FROM category"
    df_category = querydatafromdatabase(sql3,[],["Category_ID","Category_text"])

    if selected_data == "total_sales":
        dff = dff.head(8)
        dff['Store_ID'] = np.sqrt(dff[curr_metric_col])
        dff['Store_ID'] = np.sqrt(dff['Store_ID']).round(0)
                
        merged_df = pd.merge(dff,df_category, on='Category_ID')        

        fig2 = px.scatter(merged_df, x='Category_text', y=curr_metric_col, color='Category_text',
                           size = 'Store_ID', hover_data=[curr_metric_col])

        fig2.update_layout(
            title = f'Product Category: {curr_metric_col} {curr_year}',
            #paper_bgcolor="#1f2630",
            plot_bgcolor="#D3D3D3",
            #margin=dict(t=75, r=50, b=100, l=50),
            font=dict(color="#000000")

        )
        return fig2


    if selected_data == "count_sales":
        pass

    if selected_data == "avg_sales":
        dff = dff.head(8)
        merged_df = pd.merge(dff,df_category, on='Category_ID')

        fig = px.histogram(merged_df, x='Category_text', y=curr_metric_col,
                    #title='Histogram of bills',
                    labels={'x':'Category_text', 'y':curr_metric_col }, # can specify one label per df column
                    opacity=.8,
                    log_y=True, # represent bars with log scale
                    color_discrete_sequence=['deepskyblue'] # color of histogram bars
                    )


        fig.update_layout(
            title = f'Product Category: {curr_metric_col}',
            #paper_bgcolor="#1f2630",
            plot_bgcolor="#D3D3D3",
            #margin=dict(t=75, r=50, b=100, l=50),
            font=dict(color="#000000")

        )
        return fig

    # will be a table and gauge
    if selected_data == "curr_inventory":
        pass


    if selected_data == "top_performers":
        dff = dff.head(9)
        merged_df = pd.merge(dff,df_category, on='Category_ID')
        values = merged_df[curr_metric_col]
        names = merged_df['Category_text'].unique()
  
        fig = px.pie(dff, values=values, names=names, color=names,)




        fig.update_layout(
            title = f'Product Category: Top {curr_metric_col}',
            #paper_bgcolor="#1f2630",
            plot_bgcolor="#D3D3D3",
            #margin=dict(t=75, r=50, b=100, l=50),
            font=dict(color="#000000")

        )
        return fig


    if selected_data == "bottom_performers":
        dff = dff.head(15)
        merged_df = pd.merge(dff,df_category, on='Category_ID')
        values = merged_df[curr_metric_col]
        names = merged_df['Category_text'].unique()
  
        fig = px.pie(dff, values=values, names=names, color=names,)




        fig.update_layout(
            title = f'Product Category: Bottom {curr_metric_col}',
            #paper_bgcolor="#1f2630",
            plot_bgcolor="#D3D3D3",
            #margin=dict(t=75, r=50, b=100, l=50),
            font=dict(color="#000000")

        )
        return fig



    if selected_data == "avg_net_profit":
        pass


    if selected_data == "top_avg_net_profit":
        dff = dff.head(8)
        merged_df = pd.merge(dff,df_category, on='Category_ID')
        fig = px.bar(merged_df, x='Category_text', y =curr_metric_col , color=curr_metric_col,
                     hover_data = ['Category_text']
        
        )




        fig.update_layout(
            title = f'Product Category: Top {curr_metric_col}',
            #paper_bgcolor="#1f2630",
            plot_bgcolor="#D3D3D3",
            #margin=dict(t=75, r=50, b=100, l=50),
            font=dict(color="#000000")

        )
        return fig


    if selected_data == "bottom_avg_net_profit":
        dff = dff.head(8)
        merged_df = pd.merge(dff,df_category, on='Category_ID')
        fig = px.bar(merged_df, x='Category_text', y =curr_metric_col , color=curr_metric_col,
                     hover_data = ['Category_text']
        
        )




        fig.update_layout(
            title = f'Product Category: Bottom {curr_metric_col}',
            #paper_bgcolor="#1f2630",
            plot_bgcolor="#D3D3D3",
            #margin=dict(t=75, r=50, b=100, l=50),
            font=dict(color="#000000")

        )
        return fig





    if selected_data == "avg_inventory_turnover":
        pass


    if selected_data == "top_avg_inventory_turnover":
        pass

    if selected_data == "bottom_avg_inventory_turnover":
        pass

# sales graph 3
@app.callback(
    Output("selected-data3", "figure"),
    [
        Input("chart-dropdown", "value"),
        Input("years-slider", "value"),
        Input("site-dropdown", "value")
    ],
)
def display_selected_data3(selected_data, year, Store_ID):

    filters = ['Order Year','City_ID','Store_ID']
    metric_type = selected_data
    curr_metric_col = METRIC_DICT[metric_type]
    curr_year = year

    df = create_plot_metric(filters,metric_type)
    dff = df[df['Order Year'] == curr_year]
    if Store_ID == None:
        filters = ['Order Year', 'City_ID']
        metric_type = selected_data
        df = create_plot_metric(filters,metric_type)
        dff = df[df['Order Year'] == curr_year]
    elif (len(Store_ID) == 1):
        dff = dff[dff['Store_ID'] == Store_ID]
    else:
        filters = ['Order Year', 'City_ID']
        metric_type = selected_data
        df = create_plot_metric(filters,metric_type)
        dff = df[df['Order Year'] == curr_year]
        
    #dff = dff.sort_values(by=[curr_metric_col],ascending=[False])

    if selected_data == "total_sales":

        dff['Store_ID'] = np.sqrt(dff[curr_metric_col])
        dff['Store_ID'] = np.sqrt(dff['Store_ID']).round(0)
        
        dff = dff.head(n=10)

        fig3 = px.scatter(dff, x='City_ID', y=curr_metric_col, color='City_ID',
                          size = 'Store_ID', hover_data=[curr_metric_col])



        fig3.update_layout(
            title = f'Sales by City: {curr_metric_col} {curr_year}',
            #paper_bgcolor="#1f2630",
            plot_bgcolor="#D3D3D3",
            #margin=dict(t=75, r=50, b=100, l=50),
            font=dict(color="#000000")

        )
        return fig3


    if selected_data == "count_sales":
        pass

    if selected_data == "avg_sales":
        dff = dff.head(n=10)
        fig = px.histogram(dff, x='City_ID', y=curr_metric_col,
                    #title='Histogram of bills',
                    labels={'x':'City_ID', 'y':curr_metric_col }, # can specify one label per df column
                    opacity=.8,
                    log_y=True, # represent bars with log scale
                    color_discrete_sequence=['deepskyblue'] # color of histogram bars
                    )


        fig.update_layout(
            title = f'Sales by City: {curr_metric_col}',
            #paper_bgcolor="#1f2630",
            plot_bgcolor="#D3D3D3",
            #margin=dict(t=75, r=50, b=100, l=50),
            font=dict(color="#000000")

        )
        return fig

    # will be a table and gauge
    if selected_data == "curr_inventory":
        pass


    if selected_data == "top_performers":
        dff = dff.head(8)
        values = dff[curr_metric_col]
        names = dff['City_ID'].unique()
  
        fig = px.pie(dff, values=values, names=names, color=names,)




        fig.update_layout(
            title = f'Sales by City: Top {curr_metric_col}',
            #paper_bgcolor="#1f2630",
            plot_bgcolor="#D3D3D3",
            #margin=dict(t=75, r=50, b=100, l=50),
            font=dict(color="#000000")

        )
        return fig


    if selected_data == "bottom_performers":
        dff = dff.head(8)
        values = dff[curr_metric_col]
        names = dff['City_ID'].unique()
  
        fig = px.pie(dff, values=values, names=names, color=names,)




        fig.update_layout(
            title = f'Sales by City: Bottom {curr_metric_col}',
            #paper_bgcolor="#1f2630",
            plot_bgcolor="#D3D3D3",
            #margin=dict(t=75, r=50, b=100, l=50),
            font=dict(color="#000000")

        )
        return fig


    if selected_data == "avg_net_profit":
        pass


    if selected_data == "top_avg_net_profit":
        dff = dff.head(8)
        fig = px.bar(dff, x='City_ID', y =curr_metric_col , color=curr_metric_col,
                     hover_data = ['City_ID']
        
        )




        fig.update_layout(
            title = f'Sales by City: Top {curr_metric_col}',
            #paper_bgcolor="#1f2630",
            plot_bgcolor="#D3D3D3",
            #margin=dict(t=75, r=50, b=100, l=50),
            font=dict(color="#000000")

        )
        return fig


    if selected_data == "bottom_avg_net_profit":
        dff = dff.head(8)
        fig = px.bar(dff, x='City_ID', y =curr_metric_col , color=curr_metric_col,
                     hover_data = ['City_ID']
        
        )




        fig.update_layout(
            title = f'Sales by City: Bottom {curr_metric_col}',
            #paper_bgcolor="#1f2630",
            plot_bgcolor="#D3D3D3",
            #margin=dict(t=75, r=50, b=100, l=50),
            font=dict(color="#000000")

        )
        return fig





    if selected_data == "avg_inventory_turnover":
        pass


    if selected_data == "top_avg_inventory_turnover":
        pass

    if selected_data == "bottom_avg_inventory_turnover":
        pass

# sales graphs-variable selector
@app.callback(
    Output("sales-app-container", "children"),
    Input("variable-dropdown", "value")
)
def sales_variable_selector(variable):
    if variable == "buyer_region":
        children = [# Start changing graph
                    dcc.Graph(className="six columns",
                        id="selected-data",
                        figure = dict(
                        data=[dict(x=0, y=0)],
                        layout=dict(
                        #paper_bgcolor="#1f2630",
                        #plot_bgcolor="#1f2630",
                        autofill=True,
                        #margin=dict(t=75, r=50, b=100, l=50),
                        )
                                        ), style={"display":"block"}

                                    ), # end changing graph
                    ]
        return children
    
    elif variable == "category":
        children = [# Start changing graph 2                      
                    dcc.Graph(className="six columns",
                        id="selected-data2",
                        figure = dict(
                        data=[dict(x=0, y=0)],
                        layout=dict(
                        #paper_bgcolor="#1f2630",
                        #plot_bgcolor="#1f2630",
                        autofill=True,
                        #margin=dict(t=75, r=50, b=100, l=50),
                                            )
                                        ), style={"display":"block"}

                                    ), # end changing graph2
                    ]
        return children
    elif variable == "buyer_city":
        children = [# Start changing graph3
                    dcc.Graph(className="six columns",
                        id="selected-data3",
                        figure = dict(
                        data=[dict(x=0, y=0)],
                        layout=dict(
                        #paper_bgcolor="#1f2630",
                        #plot_bgcolor="#1f2630",
                        autofill=True,
                        #margin=dict(t=75, r=50, b=100, l=50),
                                            )
                                        ), style={"display":"block"}

                                    ), # end changing graph3
                    ]
        return children
    else:
        return [html.H1("404: Not found", className="text-danger")]

# Load options for Categories
@app.callback(
    Output("category-dropdown", "options"),
    [
        Input("years-slider", "value"),
    ],
)


def set_category_options(year):
    # load category list
    sql3 = "SELECT * FROM category"
    df_category = querydatafromdatabase(sql3,[],["Category_ID","Category_text"])

    categories = df_category['Category_ID'].unique().tolist()
    text = df_category['Category_text'].unique().tolist()

    return [{'label':i, 'value':j} for i, j in zip(text, categories)]

# Product and Brand
@app.callback(
    Output("product-dropdown", "options"),
    [
        Input("category-dropdown", "value"),
    ],
)


def set_products_options(selected_category):
    # load product list
    sql2 = "SELECT * FROM product"
    df_product = querydatafromdatabase(sql2,[],["Product_ID","Product Name","Category_ID"])

    curr_category = [category for category in selected_category]

    if (len(curr_category)>=1):
        dff = df_product[df_product['Category_ID'].isin(curr_category)]
    else:
        dff = df_product.copy()

    products = dff['Product_ID'].unique().tolist()
    text = dff['Product Name'].unique().tolist()

    return [{'label':i, 'value':j} for i, j in zip(text, products)]

# Load Regions
@app.callback(
    Output("region-dropdown", "options"),
    [
        Input("years-slider", "value"),
    ],
)


def set_region_options(year):
    # load region list
    sql8 = "SELECT * FROM region"
    df_region = querydatafromdatabase(sql8,[],["Region_ID","Buyer Region"])

    regions = df_region['Region_ID'].unique().tolist()
    text = df_region['Buyer Region'].unique().tolist()

    return [{'label':i, 'value':j} for i, j in zip(text, regions)]


# Get Led Display
@app.callback(
    Output("inventory-turnover-led", "value"),
    [
        Input("years-slider", "value"),
        Input("region-dropdown", "value"),
        Input("category-dropdown", "value"),
        Input("product-dropdown", "value"),
    ],
)
def set_led_display(year,selected_region,selected_brand,selected_product):

    metric_type = 'avg_inventory_turnover'
  
    sql1 = 'SELECT * FROM "sale"'
    sql2 = "SELECT * FROM product"
    sql3 = "SELECT * FROM category"
    sql4 = "SELECT * FROM po"
    sql5 = "SELECT * FROM sale_product"
    sql6 = "SELECT * FROM po_product"
    sql7 = "SELECT * FROM city"
    df_order = querydatafromdatabase(sql1,[],["Sale_ID", "Sale Date", "Store_ID", "City_ID"])
    df_product = querydatafromdatabase(sql2,[],["Product_ID", "Product Name", "Category_ID"])
    df_category = querydatafromdatabase(sql3,[],["Category_ID","Category_text"])
    df_po = querydatafromdatabase(sql4,[],["PO_ID","Release Date"])
    df_sale_product = querydatafromdatabase(sql5,[],["Sale_ID","Product_ID","Quantity","Sale Price"])
    df_po_product = querydatafromdatabase(sql6,[],["PO_ID","Product_ID","Stock","Retail Price"])
    df_city = querydatafromdatabase(sql7,[],["City_ID", "Buyer City", "Region_ID"])
    
    # append order year
    df_order['Sale Date'] = pd.to_datetime(df_order['Sale Date'])
    df_order["Order Year"] = df_order["Sale Date"].dt.year
    
    # merge city
    m_city = pd.merge(df_order, df_city, on=["City_ID"])
    
    # merge product
    m_product = pd.merge(df_sale_product, df_product, on=["Product_ID"])
    
    # merge city with product
    m_order = pd.merge(m_city, m_product, on=["Sale_ID"])
    
    # append order year
    df_po['Release Date'] = pd.to_datetime(df_po['Release Date'])
    df_po["Order Year"] = df_po["Release Date"].dt.year
    
    # merge product
    m_product = pd.merge(df_po_product, df_product, on=["Product_ID"])
    
    # merge po with product
    m_po = pd.merge(df_po, m_product, on=["PO_ID"])
    
    df = m_order.copy()
    df2 = m_po.copy()
   
    curr_metric_col = METRIC_DICT[metric_type]
    curr_year = year
    pyear = year - 1
    curr_brand = selected_brand
    curr_regions = [region for region in selected_region]
    curr_products = [product for product in selected_product]

    # If Brand is All, region is blank, and product is blank
    if (len(curr_brand)>=1) and (len(curr_regions)==0) and (len(curr_products)==0):
        dff = df[(df['Order Year']==curr_year) & (df['Category_ID']==str(curr_brand[0]))]
        dff2 = df2[(df2['Order Year']==curr_year) & (df2['Category_ID']==str(curr_brand[0]))]
        pdff = df[(df['Order Year']==pyear) & (df['Category_ID']==str(curr_brand[0]))]
        pdff2 = df2[(df2['Order Year']==pyear) & (df2['Category_ID']==str(curr_brand[0]))]
 
    elif (len(curr_brand)>=1) and (len(curr_regions)==0) and (len(curr_products)>=1):
        dff = df[(df['Order Year']==curr_year) & (df['Category_ID']==str(curr_brand[0])) &(df['Product_ID'].isin(curr_products))]
        dff2 = df2[(df2['Order Year']==curr_year) & (df2['Category_ID']==str(curr_brand[0])) &(df2['Product_ID'].isin(curr_products))]
        pdff = df[(df['Order Year']==pyear) & (df['Category_ID']==str(curr_brand[0])) &(df['Product_ID'].isin(curr_products))]
        pdff2 = df2[(df2['Order Year']==pyear) & (df2['Category_ID']==str(curr_brand[0])) &(df2['Product_ID'].isin(curr_products))]

    elif (len(curr_brand)==0) and (len(curr_regions)==0) and (len(curr_products)==0):
        dff = df[(df['Order Year']==curr_year)]
        dff2 = df2[(df2['Order Year']==curr_year)]
        pdff = df[(df['Order Year']==pyear)]
        pdff2 = df2[(df2['Order Year']==pyear)]
      
    elif (len(curr_brand)==0) and (len(curr_regions)==0) and (len(curr_products)>=1):
        dff = df[(df['Order Year']==curr_year) &  (df['Product_ID'].isin(curr_products))]
        dff2 = df2[(df2['Order Year']==curr_year) &  (df2['Product_ID'].isin(curr_products))]
        pdff = df[(df['Order Year']==pyear) &  (df['Product_ID'].isin(curr_products))]
        pdff2 = df2[(df2['Order Year']==pyear) &  (df2['Product_ID'].isin(curr_products))]
      
    elif (len(curr_brand)==0) and (len(curr_regions)>=1) and (len(curr_products)==0):
        dff = df[(df['Order Year']==curr_year) & (df['Region_ID'].isin(curr_regions))]
        dff2 = df2[(df2['Order Year']==curr_year)]
        pdff = df[(df['Order Year']==pyear) & (df['Region_ID'].isin(curr_regions))]
        pdff2 = df2[(df2['Order Year']==pyear)]
      
    else:
        dff = df[(df['Order Year']==curr_year) & (df['Category_ID']==str(curr_brand[0])) & (df['Region_ID'].isin(curr_regions)) & (df['Product_ID'].isin(curr_products))]
        dff2 = df2[(df2['Order Year']==curr_year) & (df2['Category_ID']==str(curr_brand[0])) & (df2['Product_ID'].isin(curr_products))]  
        pdff = df[(df['Order Year']==pyear) & (df['Category_ID']==str(curr_brand[0])) & (df['Region_ID'].isin(curr_regions)) & (df['Product_ID'].isin(curr_products))]
        pdff2 = df2[(df2['Order Year']==pyear) & (df2['Category_ID']==str(curr_brand[0])) & (df2['Product_ID'].isin(curr_products))]

    #​Inventory Turnover=COGS/(( beginning inventory + ending inventory) / 2)
    #Ending Inventory = beginning inventory + restock - sales
    
    curr_price = dff2.groupby(["Product_ID"]).agg({'Retail Price' : 'mean'})
    curr_qty = dff.groupby(["Product_ID"]).agg({'Quantity' : 'sum'})
    curr_qty['Retail Price'] = curr_price['Retail Price']
    curr_stock = dff2.groupby(["Product_ID"]).agg({'Stock' : 'sum'})
    
    past_price = pdff2.groupby(["Product_ID"]).agg({'Retail Price' : 'mean'})
    past_qty = pdff.groupby(["Product_ID"]).agg({'Quantity' : 'sum'})
    past_qty['Retail Price'] = past_price['Retail Price']
    past_stock = pdff2.groupby(["Product_ID"]).agg({'Stock' : 'sum'})
    
    curr_data = pd.merge(curr_qty, curr_stock, on=['Product_ID'])
    past_data = pd.merge(past_qty, past_stock, on=['Product_ID'])
    
    curr_data['beg_inv'] = (past_data['Retail Price'] * past_data['Stock']) - (past_data['Retail Price'] * past_data['Quantity'])
    beg_inventory = curr_data['beg_inv'].sum()
    past_data['end_inv'] = curr_data['beg_inv'] + (curr_data['Retail Price'] * curr_data['Stock']) - (curr_data['Retail Price'] * curr_data['Quantity'])
    end_inventory = past_data['end_inv'].sum()

    cogs = (curr_data['Retail Price'] * curr_data['Stock']).sum()
    
    turnover = cogs / ((beg_inventory + end_inventory)/2)
    #days in inventory = 365/turnover
    dii = 365 / turnover

    return round(dii,2)


@app.callback(
    Output("inventory-current-led", "value"),
    [
        Input("years-slider", "value"),
        Input("category-dropdown", "value"),
        Input("product-dropdown", "value"),
        Input("region-dropdown", "value"),
        Input("shoe-size-dropdown", "value"),
    ],
)


def set_current_inventory_led(year, selected_brand, selected_product, selected_region, selected_shoe_size):

    filters = ['Order Year','Region_ID','Category_ID','Product_ID','Store_ID']
    filters2 = ['Order Year','Category_ID','Product_ID']
    metric_type = 'curr_inventory'
    metric_type2 = 'curr_inventory2'
    curr_metric_col = METRIC_DICT[metric_type]
    curr_metric_col2 = METRIC_DICT[metric_type2]
    curr_year = year
    curr_brand = selected_brand
    curr_regions = [region for region in selected_region]
    curr_products = [product for product in selected_product]
    curr_shoe_sizes = [shoe for shoe in selected_shoe_size]

    df = create_plot_metric(filters,metric_type)
    df2 = create_plot_metric(filters2,metric_type2)
  
    # If Brand is All

    if (len(curr_brand)==0) and (len(curr_products)==0) and (len(curr_regions)==0) and (len(curr_shoe_sizes)==0):
        dff = df[(df['Order Year']==curr_year)]

    elif (len(curr_brand)==0) and (len(curr_products)>=1) and (len(curr_regions)==0) and (len(curr_shoe_sizes)==0):
        dff = df[(df['Order Year']==curr_year) & (df['Product_ID'].isin(curr_products))]

    elif (len(curr_brand)==0) and (len(curr_products)>=1) and (len(curr_regions)>=1) and (len(curr_shoe_sizes)==0):
        dff = df[(df['Order Year']==curr_year) & (df['Product_ID'].isin(curr_products)) & (df['Region_ID'].isin(curr_regions))]

    elif (len(curr_brand)==0) and (len(curr_products)>=1) and (len(curr_regions)>=1) and (len(curr_shoe_sizes)>=1):
        dff = df[(df['Order Year']==curr_year) & (df['Product_ID'].isin(curr_products)) & (df['Region_ID'].isin(curr_regions)) & (df['Store_ID'].isin(curr_shoe_sizes))]
        

    elif (len(curr_brand)>=1) and (len(curr_products)==0) and (len(curr_regions)==0) and (len(curr_shoe_sizes)==0):
        dff = df[(df['Order Year']==curr_year) & (df['Category_ID']==str(curr_brand[0]))]


    elif (len(curr_brand)>=1) and (len(curr_products)>=1) and (len(curr_regions)==0) and (len(curr_shoe_sizes)==0):
        dff = df[(df['Order Year']==curr_year) & (df['Category_ID']==str(curr_brand[0])) & (df['Product_ID'].isin(curr_products))]


    elif (len(curr_brand)>=1) and (len(curr_products)>=1) and (len(curr_regions)>=1) and (len(curr_shoe_sizes)==0):
        dff = df[(df['Order Year']==curr_year) & (df['Category_ID']==str(curr_brand[0])) & (df['Product_ID'].isin(curr_products)) & (df['Region_ID'].isin(curr_regions))]

    else:
        dff = df[(df['Order Year']==curr_year) & (df['Product_ID'].isin(curr_products)) & (df['Region_ID'].isin(curr_regions)) & (df['Store_ID'].isin(curr_shoe_sizes))]

    # if statements for curr_inventory2
    if (len(curr_brand)==0) and (len(curr_products)==0):
        dff2 = df2[(df2['Order Year']==curr_year)]
    
    elif (len(curr_brand)==0) and (len(curr_products)>=1):
        dff2 = df2[(df2['Order Year']==curr_year) & (df2['Product_ID'].isin(curr_products))]
          
    elif (len(curr_brand)>=1) and (len(curr_products)==0):
        dff2 = df2[(df2['Order Year']==curr_year) & (df2['Category_ID']==str(curr_brand[0]))]
    
    elif (len(curr_brand)>=1) and (len(curr_products)>=1):
        dff2 = df2[(df2['Order Year']==curr_year) & (df2['Category_ID']==str(curr_brand[0])) & (df2['Product_ID'].isin(curr_products))]
    else:
        dff2 = df2[(df2['Order Year']==curr_year) & (df2['Category_ID']==str(curr_brand[0])) & (df2['Product_ID'].isin(curr_products))]
    
    
    curr_inventory = dff2[curr_metric_col2].sum() - dff[curr_metric_col].sum()


    return curr_inventory

# Get Reorder Point Led Display
@app.callback(
    Output("rop-led", "value"),
    [
        Input("years-slider", "value"),
        Input("region-dropdown", "value"),
        Input("category-dropdown", "value"),
        Input("product-dropdown", "value"),
        Input("shoe-size-dropdown", "value")
    ],
)
def set_rop_display(year,selected_region,selected_brand,selected_product,selected_site):

    filters = ['Sale Date','Order Year','Region_ID','Store_ID','Category_ID','Product_ID']
    metric_type = 'count_sales'
    curr_year = year
    curr_brand = selected_brand
    curr_regions = [region for region in selected_region]
    curr_products = [product for product in selected_product]
    curr_shoe_sizes = [shoe for shoe in selected_site]
    
    df = create_plot_metric(filters,metric_type)
    
    if (len(curr_brand)==0) and (len(curr_products)==0) and (len(curr_regions)==0) and (len(curr_shoe_sizes)==0):
        dff = df[(df['Order Year']==curr_year)]

    elif (len(curr_brand)==0) and (len(curr_products)>=1) and (len(curr_regions)==0) and (len(curr_shoe_sizes)==0):
        dff = df[(df['Order Year']==curr_year) & (df['Product_ID'].isin(curr_products))]

    elif (len(curr_brand)==0) and (len(curr_products)>=1) and (len(curr_regions)>=1) and (len(curr_shoe_sizes)==0):
        dff = df[(df['Order Year']==curr_year) & (df['Product_ID'].isin(curr_products)) & (df['Region_ID'].isin(curr_regions))]

    elif (len(curr_brand)==0) and (len(curr_products)>=1) and (len(curr_regions)>=1) and (len(curr_shoe_sizes)>=1):
        dff = df[(df['Order Year']==curr_year) & (df['Product_ID'].isin(curr_products)) & (df['Region_ID'].isin(curr_regions)) & (df['Store_ID'].isin(curr_shoe_sizes))]
        

    elif (len(curr_brand)>=1) and (len(curr_products)==0) and (len(curr_regions)==0) and (len(curr_shoe_sizes)==0):
        dff = df[(df['Order Year']==curr_year) & (df['Category_ID']==str(curr_brand[0]))]


    elif (len(curr_brand)>=1) and (len(curr_products)>=1) and (len(curr_regions)==0) and (len(curr_shoe_sizes)==0):
        dff = df[(df['Order Year']==curr_year) & (df['Category_ID']==str(curr_brand[0])) & (df['Product_ID'].isin(curr_products))]


    elif (len(curr_brand)>=1) and (len(curr_products)>=1) and (len(curr_regions)>=1) and (len(curr_shoe_sizes)==0):
        dff = df[(df['Order Year']==curr_year) & (df['Category_ID']==str(curr_brand[0])) & (df['Product_ID'].isin(curr_products)) & (df['Region_ID'].isin(curr_regions))]

    else:
        dff = df[(df['Order Year']==curr_year) & (df['Product_ID'].isin(curr_products)) & (df['Region_ID'].isin(curr_regions)) & (df['Store_ID'].isin(curr_shoe_sizes))]

    #Lead time demand = avg. daily sales x avg. lead time
    data =  dff.groupby(['Sale Date']).agg({'Sales Count':['sum']})
    mean_qty = data.mean()
    #ltd = mean_qty * 3
    #Safety stock = (max. daily sales x max. lead time) – Lead time demand
    #ss = (data.max() * 3) - ltd
    #Reorder point = lead time demand + safety stock
    rop = round(data.max() * 3)
    
    return rop

# Get Economic Order Quantity Led Display
@app.callback(
    Output("eoq-led", "value"),
    [
        Input("years-slider", "value"),
        Input("region-dropdown", "value"),
        Input("category-dropdown", "value"),
        Input("product-dropdown", "value"),
        Input("shoe-size-dropdown", "value")
    ],
)
def set_eoq_display(year,selected_region,selected_brand,selected_product,selected_site):
    #filters = ['Order Year','Region_ID','Category_ID','Product_ID','Store_ID']
    filters2 = ['Order Year','Category_ID','Product_ID']
    #metric_type = 'curr_inventory'
    metric_type2 = 'curr_inventory2'
    #curr_metric_col = METRIC_DICT[metric_type]
    curr_metric_col2 = METRIC_DICT[metric_type2]
    curr_year = year
    curr_brand = selected_brand
    curr_regions = [region for region in selected_region]
    curr_products = [product for product in selected_product]
    curr_shoe_sizes = [shoe for shoe in selected_site]
    
    sql1 = 'SELECT * FROM "sale"'
    sql2 = "SELECT * FROM product"
    #sql4 = "SELECT * FROM po"
    sql5 = "SELECT * FROM sale_product"
    #sql6 = "SELECT * FROM po_product"
    sql7 = "SELECT * FROM city"
    df_order = querydatafromdatabase(sql1,[],["Sale_ID", "Sale Date", "Store_ID", "City_ID"])
    df_product = querydatafromdatabase(sql2,[],["Product_ID", "Product Name", "Category_ID"])
    #df_po = querydatafromdatabase(sql4,[],["PO_ID","Release Date"])
    df_sale_product = querydatafromdatabase(sql5,[],["Sale_ID","Product_ID","Quantity","Sale Price"])
    #df_po_product = querydatafromdatabase(sql6,[],["PO_ID","Product_ID","Stock","Retail Price"])
    df_city = querydatafromdatabase(sql7,[],["City_ID", "Buyer City", "Region_ID"])
    
    # append order year
    df_order['Sale Date'] = pd.to_datetime(df_order['Sale Date'])
    df_order["Order Year"] = df_order["Sale Date"].dt.year
    
    # merge city
    m_city = pd.merge(df_order, df_city, on=["City_ID"])
    
    # merge product
    m_product = pd.merge(df_sale_product, df_product, on=["Product_ID"])
    
    # merge city with product
    m_order = pd.merge(m_city, m_product, on=["Sale_ID"])
    
    # append order year
    #df_po['Release Date'] = pd.to_datetime(df_po['Release Date'])
    #df_po["Order Year"] = df_po["Release Date"].dt.year
    
    # merge product
    #m_product = pd.merge(df_po_product, df_product, on=["Product_ID"])
    
    # merge po with product
    #m_po = pd.merge(df_po, m_product, on=["PO_ID"])
    
    df = m_order.copy()
    df2 = create_plot_metric(filters2,metric_type2)
    
    if (len(curr_brand)==0) and (len(curr_products)==0) and (len(curr_regions)==0) and (len(curr_shoe_sizes)==0):
        dff = df[(df['Order Year']==curr_year)]
        dff2 = df2[(df2['Order Year']==curr_year)]

    elif (len(curr_brand)==0) and (len(curr_products)>=1) and (len(curr_regions)==0) and (len(curr_shoe_sizes)==0):
        dff = df[(df['Order Year']==curr_year) & (df['Product_ID'].isin(curr_products))]
        dff2 = df2[(df2['Order Year']==curr_year) & (df2['Product_ID'].isin(curr_products))]

    elif (len(curr_brand)==0) and (len(curr_products)>=1) and (len(curr_regions)>=1) and (len(curr_shoe_sizes)==0):
        dff = df[(df['Order Year']==curr_year) & (df['Product_ID'].isin(curr_products)) & (df['Region_ID'].isin(curr_regions))]
        dff2 = df2[(df2['Order Year']==curr_year) & (df2['Product_ID'].isin(curr_products))]

    elif (len(curr_brand)==0) and (len(curr_products)>=1) and (len(curr_regions)>=1) and (len(curr_shoe_sizes)>=1):
        dff = df[(df['Order Year']==curr_year) & (df['Product_ID'].isin(curr_products)) & (df['Region_ID'].isin(curr_regions)) & (df['Store_ID'].isin(curr_shoe_sizes))]
        dff2 = df2[(df2['Order Year']==curr_year) & (df2['Product_ID'].isin(curr_products))]

    elif (len(curr_brand)>=1) and (len(curr_products)==0) and (len(curr_regions)==0) and (len(curr_shoe_sizes)==0):
        dff = df[(df['Order Year']==curr_year) & (df['Category_ID']==str(curr_brand[0]))]
        dff2 = df2[(df2['Order Year']==curr_year) & (df2['Category_ID'].isin(curr_products))]

    elif (len(curr_brand)>=1) and (len(curr_products)>=1) and (len(curr_regions)==0) and (len(curr_shoe_sizes)==0):
        dff = df[(df['Order Year']==curr_year) & (df['Category_ID']==str(curr_brand[0])) & (df['Product_ID'].isin(curr_products))]
        dff2 = df2[(df2['Order Year']==curr_year) & (df2['Product_ID'].isin(curr_products)) & (df2['Category_ID'].isin(curr_products))]

    elif (len(curr_brand)>=1) and (len(curr_products)>=1) and (len(curr_regions)>=1) and (len(curr_shoe_sizes)==0):
        dff = df[(df['Order Year']==curr_year) & (df['Category_ID']==str(curr_brand[0])) & (df['Product_ID'].isin(curr_products)) & (df['Region_ID'].isin(curr_regions))]
        dff2 = df2[(df2['Order Year']==curr_year) & (df2['Product_ID'].isin(curr_products)) & (df2['Category_ID'].isin(curr_products))]

    else:
        dff = df[(df['Order Year']==curr_year) & (df['Product_ID'].isin(curr_products)) & (df['Region_ID'].isin(curr_regions)) & (df['Store_ID'].isin(curr_shoe_sizes))]
        dff2 = df2[(df2['Order Year']==curr_year) & (df2['Product_ID'].isin(curr_products)) & (df2['Category_ID'].isin(curr_products))]

    #EOQ Method = √ (2DS/H)
    #where : 
    #m_product = pd.merge(dff, dff2, on=["Product_ID"])
    #D : annual demand for material inventory 
    #S : costs required per order
    ds = (dff['Quantity']*dff['Sale Price']).sum()
    #m_product['cogs'] = m_product['Quantity'] * m_product['Retail Price']
    #H : holding cost per unit annually
    h = ((dff['Sale Price']/2) * 0.2748).sum() / dff['Quantity'].sum()
    #EOQ : number of items in each order 
    eoq = round(math.sqrt(2*ds/h))
    
    curr_inventory = dff2[curr_metric_col2].sum() - dff['Quantity'].sum()
    
    if curr_inventory < eoq:
        reorder = eoq - curr_inventory
    else:
        reorder = 0
    
    return reorder

# Get Shoe Site from Selected Region
@app.callback(
    Output("curr-inventory-gauage", "value"),
    [
        Input("years-slider", "value"),
        Input("category-dropdown", "value"),
        Input("product-dropdown", "value"),
        Input("region-dropdown", "value"),
        Input("shoe-size-dropdown", "value"),
    ],
)


def set_gauge_value(year, selected_brand, selected_product, selected_region, selected_shoe_size):
    filters = ['Order Year','Region_ID','Category_ID','Product_ID','Store_ID']
    filters2 = ['Order Year','Category_ID','Product_ID']
    metric_type = 'curr_inventory'
    metric_type2 = 'curr_inventory2'
    curr_metric_col = METRIC_DICT[metric_type]
    curr_metric_col2 = METRIC_DICT[metric_type2]
    curr_year = year
    curr_brand = selected_brand
    curr_regions = [region for region in selected_region]
    curr_products = [product for product in selected_product]
    curr_shoe_sizes = [shoe for shoe in selected_shoe_size]

    df = create_plot_metric(filters,metric_type)
    df2 = create_plot_metric(filters2,metric_type2)
    # If Brand is All

    if (len(curr_brand)==0) and (len(curr_products)==0) and (len(curr_regions)==0) and (len(curr_shoe_sizes)==0):
        dff = df[(df['Order Year']==curr_year)]

    elif (len(curr_brand)==0) and (len(curr_products)>=1) and (len(curr_regions)==0) and (len(curr_shoe_sizes)==0):
        dff = df[(df['Order Year']==curr_year) & (df['Product_ID'].isin(curr_products))]

    elif (len(curr_brand)==0) and (len(curr_products)>=1) and (len(curr_regions)>=1) and (len(curr_shoe_sizes)==0):
        dff = df[(df['Order Year']==curr_year) & (df['Product_ID'].isin(curr_products)) & (df['Region_ID'].isin(curr_regions))]

    elif (len(curr_brand)==0) and (len(curr_products)>=1) and (len(curr_regions)>=1) and (len(curr_shoe_sizes)>=1):
        dff = df[(df['Order Year']==curr_year) & (df['Product_ID'].isin(curr_products)) & (df['Region_ID'].isin(curr_regions)) & (df['Store_ID'].isin(curr_shoe_sizes))]
        

    elif (len(curr_brand)>=1) and (len(curr_products)==0) and (len(curr_regions)==0) and (len(curr_shoe_sizes)==0):
        dff = df[(df['Order Year']==curr_year) & (df['Category_ID']==str(curr_brand[0]))]


    elif (len(curr_brand)>=1) and (len(curr_products)>=1) and (len(curr_regions)==0) and (len(curr_shoe_sizes)==0):
        dff = df[(df['Order Year']==curr_year) & (df['Category_ID']==str(curr_brand[0])) & (df['Product_ID'].isin(curr_products))]


    elif (len(curr_brand)>=1) and (len(curr_products)>=1) and (len(curr_regions)>=1) and (len(curr_shoe_sizes)==0):
        dff = df[(df['Order Year']==curr_year) & (df['Category_ID']==str(curr_brand[0])) & (df['Product_ID'].isin(curr_products)) & (df['Region_ID'].isin(curr_regions))]

    else:
        dff = df[(df['Order Year']==curr_year) & (df['Product_ID'].isin(curr_products)) & (df['Region_ID'].isin(curr_regions)) & (df['Store_ID'].isin(curr_shoe_sizes))]

    # if statements for curr_inventory2
    if (len(curr_brand)==0) and (len(curr_products)==0):
        dff2 = df2[(df2['Order Year']==curr_year)]

    elif (len(curr_brand)==0) and (len(curr_products)>=1):
        dff2 = df2[(df2['Order Year']==curr_year) & (df2['Product_ID'].isin(curr_products))]

    elif (len(curr_brand)==0) and (len(curr_products)>=1) and len(curr_shoe_sizes)==0:
        dff2 = df2[(df2['Order Year']==curr_year) & (df2['Product_ID'].isin(curr_products))]

    elif (len(curr_brand)==0) and (len(curr_products)>=1) and (len(curr_regions)>=1) and (len(curr_shoe_sizes)>=1):
        dff2 = df2[(df2['Order Year']==curr_year) & (df2['Product_ID'].isin(curr_products))]
        

    elif (len(curr_brand)>=1) and (len(curr_products)==0):
        dff2 = df2[(df2['Order Year']==curr_year) & (df2['Category_ID']==str(curr_brand[0]))]


    elif (len(curr_brand)>=1) and (len(curr_products)>=1):
        dff2 = df2[(df2['Order Year']==curr_year) & (df2['Category_ID']==str(curr_brand[0])) & (df2['Product_ID'].isin(curr_products))]


    elif (len(curr_brand)>=1) and (len(curr_products)>=1):
        dff2 = df2[(df2['Order Year']==curr_year) & (df2['Category_ID']==str(curr_brand[0])) & (df2['Product_ID'].isin(curr_products))]

    else:
        dff2 = df2[(df2['Order Year']==curr_year) & (df2['Product_ID'].isin(curr_products))]

    curr_inventory = dff2[curr_metric_col2].sum() - dff[curr_metric_col].sum()
    max_inventory = dff2[curr_metric_col2].sum()
    scaled_inventory = (50 * curr_inventory) / max_inventory

    return scaled_inventory

# Get Shoe Site from Selected Region
@app.callback(
    Output("curr-inventory-gauage-2", "value"),
    [
        Input("years-slider", "value"),
        Input("category-dropdown", "value"),
        Input("product-dropdown", "value"),
        Input("region-dropdown", "value"),
        Input("shoe-size-dropdown", "value"),
    ],
)


def set_gauge_2_value(year, selected_brand, selected_product, selected_region, selected_shoe_size):
    

    filters = ['Sale Date','Order Year','Region_ID','Category_ID','Product_ID','Store_ID']
    filters2 = ['Order Year','Category_ID','Product_ID']
    metric_type = 'curr_inventory'
    metric_type2 = 'curr_inventory2'
    curr_metric_col = METRIC_DICT[metric_type]
    curr_metric_col2 = METRIC_DICT[metric_type2]
    curr_year = year
    curr_brand = selected_brand
    curr_regions = [region for region in selected_region]
    curr_products = [product for product in selected_product]
    curr_shoe_sizes = [shoe for shoe in selected_shoe_size]

    df = create_plot_metric(filters,metric_type)
    df2 = create_plot_metric(filters2,metric_type2)
    # If Brand is All

    if (len(curr_brand)==0) and (len(curr_products)==0) and (len(curr_regions)==0) and (len(curr_shoe_sizes)==0):
        dff = df[(df['Order Year']==curr_year)]

    elif (len(curr_brand)==0) and (len(curr_products)>=1) and (len(curr_regions)==0) and (len(curr_shoe_sizes)==0):
        dff = df[(df['Order Year']==curr_year) & (df['Product_ID'].isin(curr_products))]

    elif (len(curr_brand)==0) and (len(curr_products)>=1) and (len(curr_regions)>=1) and (len(curr_shoe_sizes)==0):
        dff = df[(df['Order Year']==curr_year) & (df['Product_ID'].isin(curr_products)) & (df['Region_ID'].isin(curr_regions))]

    elif (len(curr_brand)==0) and (len(curr_products)>=1) and (len(curr_regions)>=1) and (len(curr_shoe_sizes)>=1):
        dff = df[(df['Order Year']==curr_year) & (df['Product_ID'].isin(curr_products)) & (df['Region_ID'].isin(curr_regions)) & (df['Store_ID'].isin(curr_shoe_sizes))]
        

    elif (len(curr_brand)>=1) and (len(curr_products)==0) and (len(curr_regions)==0) and (len(curr_shoe_sizes)==0):
        dff = df[(df['Order Year']==curr_year) & (df['Category_ID']==str(curr_brand[0]))]


    elif (len(curr_brand)>=1) and (len(curr_products)>=1) and (len(curr_regions)==0) and (len(curr_shoe_sizes)==0):
        dff = df[(df['Order Year']==curr_year) & (df['Category_ID']==str(curr_brand[0])) & (df['Product_ID'].isin(curr_products))]


    elif (len(curr_brand)>=1) and (len(curr_products)>=1) and (len(curr_regions)>=1) and (len(curr_shoe_sizes)==0):
        dff = df[(df['Order Year']==curr_year) & (df['Category_ID']==str(curr_brand[0])) & (df['Product_ID'].isin(curr_products)) & (df['Region_ID'].isin(curr_regions))]

    else:
        dff = df[(df['Order Year']==curr_year) & (df['Product_ID'].isin(curr_products)) & (df['Region_ID'].isin(curr_regions)) & (df['Store_ID'].isin(curr_shoe_sizes))]
    
    # if statements for curr_inventory2
    if (len(curr_brand)==0) and (len(curr_products)==0):
        dff2 = df2[(df2['Order Year']==curr_year)]

    elif (len(curr_brand)==0) and (len(curr_products)>=1):
        dff2 = df2[(df2['Order Year']==curr_year) & (df2['Product_ID'].isin(curr_products))]

    elif (len(curr_brand)==0) and (len(curr_products)>=1) and len(curr_shoe_sizes)==0:
        dff2 = df2[(df2['Order Year']==curr_year) & (df2['Product_ID'].isin(curr_products))]

    elif (len(curr_brand)==0) and (len(curr_products)>=1) and (len(curr_regions)>=1) and (len(curr_shoe_sizes)>=1):
        dff2 = df2[(df2['Order Year']==curr_year) & (df2['Product_ID'].isin(curr_products))]
        

    elif (len(curr_brand)>=1) and (len(curr_products)==0):
        dff2 = df2[(df2['Order Year']==curr_year) & (df2['Category_ID']==str(curr_brand[0]))]


    elif (len(curr_brand)>=1) and (len(curr_products)>=1):
        dff2 = df2[(df2['Order Year']==curr_year) & (df2['Category_ID']==str(curr_brand[0])) & (df2['Product_ID'].isin(curr_products))]


    elif (len(curr_brand)>=1) and (len(curr_products)>=1):
        dff2 = df2[(df2['Order Year']==curr_year) & (df2['Category_ID']==str(curr_brand[0])) & (df2['Product_ID'].isin(curr_products))]

    else:
        dff2 = df2[(df2['Order Year']==curr_year) & (df2['Product_ID'].isin(curr_products))]

    #Lead time demand = avg. daily sales x avg. lead time
    data =  dff.groupby(['Sale Date']).agg({'Order Quantity':['sum']})
    mean_qty = data.mean()
    #ltd = mean_qty * 3
    #Safety stock = (max. daily sales x max. lead time) – Lead time demand
    #ss = (data.max() * 3) - ltd
    #Reorder point = lead time demand + safety stock = (max. daily sales x max. lead time)
    rop = round((data.max() * 3))

    # convert values to scale 50
    curr_rop = int(rop)
    max_inventory = dff2[curr_metric_col2].sum()
    scaled_rop = (50 * curr_rop) / max_inventory

    return scaled_rop


# Get Shoe Store_ID from Selected Region
@app.callback(
    Output("best-turnover-graph", "figure"),
    [
        Input("years-slider", "value"),
        Input("category-dropdown", "value"),
        Input("region-dropdown", "value"),
  
    ],
)


def set_best_turnover_graph(year, selected_brand, selected_region):
    metric_type = 'avg_inventory_turnover'
    curr_metric_col = METRIC_DICT[metric_type]
    curr_year = year
    pyear = year - 1
    curr_brand = selected_brand
    curr_regions = [region for region in selected_region]

    sql1 = 'SELECT * FROM "sale"'
    sql2 = "SELECT * FROM product"
    sql3 = "SELECT * FROM category"
    sql4 = "SELECT * FROM po"
    sql5 = "SELECT * FROM sale_product"
    sql6 = "SELECT * FROM po_product"
    sql7 = "SELECT * FROM city"
    df_order = querydatafromdatabase(sql1,[],["Sale_ID", "Sale Date", "Store_ID", "City_ID"])
    df_product = querydatafromdatabase(sql2,[],["Product_ID", "Product Name", "Category_ID"])
    df_po = querydatafromdatabase(sql4,[],["PO_ID","Release Date"])
    df_sale_product = querydatafromdatabase(sql5,[],["Sale_ID","Product_ID","Quantity","Sale Price"])
    df_po_product = querydatafromdatabase(sql6,[],["PO_ID","Product_ID","Stock","Retail Price"])
    df_city = querydatafromdatabase(sql7,[],["City_ID", "Buyer City", "Region_ID"])
    
    # append order year
    df_order['Sale Date'] = pd.to_datetime(df_order['Sale Date'])
    df_order["Order Year"] = df_order["Sale Date"].dt.year
    
    # merge city
    m_city = pd.merge(df_order, df_city, on=["City_ID"])
    
    # merge product
    m_product = pd.merge(df_sale_product, df_product, on=["Product_ID"])
    
    # merge city with product
    m_order = pd.merge(m_city, m_product, on=["Sale_ID"])
    
    # append order year
    df_po['Release Date'] = pd.to_datetime(df_po['Release Date'])
    df_po["Order Year"] = df_po["Release Date"].dt.year
    
    # merge product
    m_product = pd.merge(df_po_product, df_product, on=["Product_ID"])
    
    # merge po with product
    m_po = pd.merge(df_po, m_product, on=["PO_ID"])
    
    df = m_order.copy()
    df2 = m_po.copy()
   
    if (len(curr_brand)==0) and (len(curr_regions)==0):
        dff = df[(df['Order Year']==curr_year)]
        dff2 = df2[(df2['Order Year']==curr_year)]
        pdff = df[(df['Order Year']==pyear)]
        pdff2 = df2[(df2['Order Year']==pyear)]

    elif (len(curr_brand)==0) and (len(curr_regions)>=1):
        dff = df[(df['Order Year']==curr_year) & (df['Region_ID'].isin(curr_regions))]
        dff2 = df2[(df2['Order Year']==curr_year)]
        pdff = df[(df['Order Year']==pyear) & (df['Region_ID'].isin(curr_regions))]
        pdff2 = df2[(df2['Order Year']==pyear)]

    elif (len(curr_brand)>=1) and (len(curr_regions)==0):
        dff = df[(df['Order Year']==curr_year) & (df['Category_ID']==str(curr_brand[0]))]
        dff2 = df2[(df2['Order Year']==curr_year) & (df2['Category_ID']==str(curr_brand[0]))]
        pdff = df[(df['Order Year']==pyear) & (df['Category_ID']==str(curr_brand[0]))]
        pdff2 = df2[(df2['Order Year']==pyear) & (df2['Category_ID']==str(curr_brand[0]))]


    elif (len(curr_brand)>=1) and (len(curr_regions)>=1):
        dff = df[(df['Order Year']==curr_year) & (df['Category_ID']==str(curr_brand[0])) & (df['Region_ID'].isin(curr_regions))]
        dff2 = df2[(df2['Order Year']==curr_year) & (df2['Category_ID']==str(curr_brand[0]))]
        pdff = df[(df['Order Year']==pyear) & (df['Category_ID']==str(curr_brand[0])) & (df['Region_ID'].isin(curr_regions))]
        pdff2 = df2[(df2['Order Year']==pyear) & (df2['Category_ID']==str(curr_brand[0]))]
        
    else:
        dff = df[(df['Order Year']==curr_year)]
        dff2 = df2[(df2['Order Year']==curr_year)]
        pdff = df[(df['Order Year']==pyear)]
        pdff2 = df2[(df2['Order Year']==pyear)]

    #​Inventory Turnover=COGS/(( beginning inventory + ending inventory) / 2)
    #Ending Inventory = beginning inventory + restock - sales
    
    curr_price = dff2.groupby(["Product_ID"]).agg({'Retail Price' : 'mean'})
    curr_qty = dff.groupby(["Product_ID"]).agg({'Quantity' : 'sum'})
    curr_qty['Retail Price'] = curr_price['Retail Price']
    curr_stock = dff2.groupby(["Product_ID"]).agg({'Stock' : 'sum'})
    
    past_price = pdff2.groupby(["Product_ID"]).agg({'Retail Price' : 'mean'})
    past_qty = pdff.groupby(["Product_ID"]).agg({'Quantity' : 'sum'})
    past_qty['Retail Price'] = past_price['Retail Price']
    past_stock = pdff2.groupby(["Product_ID"]).agg({'Stock' : 'sum'})
    
    curr_data = pd.merge(curr_qty, curr_stock, on=['Product_ID'])
    past_data = pd.merge(past_qty, past_stock, on=['Product_ID'])
    
    curr_data['beg_inv'] = (past_data['Retail Price'] * past_data['Stock']) - (past_data['Retail Price'] * past_data['Quantity'])
    #beg_inventory = curr_data['beg_inv'].sum()
    past_data['end_inv'] = curr_data['beg_inv'] + (curr_data['Retail Price'] * curr_data['Stock']) - (curr_data['Retail Price'] * curr_data['Quantity'])
    #end_inventory = past_data['end_inv'].sum()

    curr_data['COGS'] = curr_data['Retail Price'] * curr_data['Quantity']
    # days of sales inventory
    dff = 365 / (curr_data['COGS'] / ((past_data['end_inv'] + curr_data['beg_inv'])/2))
    df_dii = dff.to_frame(name=curr_metric_col)
    df_dii = df_dii.reset_index()
    df_dii.sort_values(by=[curr_metric_col],ascending=[True],inplace=True)

    df_dii = df_dii.head()


    fig = px.bar(df_dii, x='Product_ID', y =curr_metric_col , color=curr_metric_col,
                    hover_data = ['Product_ID']
    
    )




    fig.update_layout(
        title = f'Best Days in Inventory (DSI)',
        #paper_bgcolor="#1f2630",
        plot_bgcolor="#D3D3D3",
        margin=dict(t=75, r=50, b=100, l=50),
        font=dict(color="#000000")

    )
    return fig





    
# Get Shoe Store_ID from Selected Region
@app.callback(
    Output("worse-turnover-graph", "figure"),
    [
        Input("years-slider", "value"),
        Input("category-dropdown", "value"),
        Input("region-dropdown", "value"),
  
    ],
)


def set_worse_turnover_graph(year, selected_brand, selected_region):
    metric_type = 'avg_inventory_turnover'
    curr_metric_col = METRIC_DICT[metric_type]
    curr_year = year
    pyear = year - 1
    curr_brand = selected_brand
    curr_regions = [region for region in selected_region]
    
    sql1 = 'SELECT * FROM "sale"'
    sql2 = "SELECT * FROM product"
    sql3 = "SELECT * FROM category"
    sql4 = "SELECT * FROM po"
    sql5 = "SELECT * FROM sale_product"
    sql6 = "SELECT * FROM po_product"
    sql7 = "SELECT * FROM city"
    df_order = querydatafromdatabase(sql1,[],["Sale_ID", "Sale Date", "Store_ID", "City_ID"])
    df_product = querydatafromdatabase(sql2,[],["Product_ID", "Product Name", "Category_ID"])
    df_po = querydatafromdatabase(sql4,[],["PO_ID","Release Date"])
    df_sale_product = querydatafromdatabase(sql5,[],["Sale_ID","Product_ID","Quantity","Sale Price"])
    df_po_product = querydatafromdatabase(sql6,[],["PO_ID","Product_ID","Stock","Retail Price"])
    df_city = querydatafromdatabase(sql7,[],["City_ID", "Buyer City", "Region_ID"])
    
    # append order year
    df_order['Sale Date'] = pd.to_datetime(df_order['Sale Date'])
    df_order["Order Year"] = df_order["Sale Date"].dt.year
    
    # merge city
    m_city = pd.merge(df_order, df_city, on=["City_ID"])
    
    # merge product
    m_product = pd.merge(df_sale_product, df_product, on=["Product_ID"])
    
    # merge city with product
    m_order = pd.merge(m_city, m_product, on=["Sale_ID"])
    
    # append order year
    df_po['Release Date'] = pd.to_datetime(df_po['Release Date'])
    df_po["Order Year"] = df_po["Release Date"].dt.year
    
    # merge product
    m_product = pd.merge(df_po_product, df_product, on=["Product_ID"])
    
    # merge po with product
    m_po = pd.merge(df_po, m_product, on=["PO_ID"])
    
    df = m_order.copy()
    df2 = m_po.copy()
   
    if (len(curr_brand)==0) and (len(curr_regions)==0):
        dff = df[(df['Order Year']==curr_year)]
        dff2 = df2[(df2['Order Year']==curr_year)]
        pdff = df[(df['Order Year']==pyear)]
        pdff2 = df2[(df2['Order Year']==pyear)]

    elif (len(curr_brand)==0) and (len(curr_regions)>=1):
        dff = df[(df['Order Year']==curr_year) & (df['Region_ID'].isin(curr_regions))]
        dff2 = df2[(df2['Order Year']==curr_year)]
        pdff = df[(df['Order Year']==pyear) & (df['Region_ID'].isin(curr_regions))]
        pdff2 = df2[(df2['Order Year']==pyear)]

    elif (len(curr_brand)>=1) and (len(curr_regions)==0):
        dff = df[(df['Order Year']==curr_year) & (df['Category_ID']==str(curr_brand[0]))]
        dff2 = df2[(df2['Order Year']==curr_year) & (df2['Category_ID']==str(curr_brand[0]))]
        pdff = df[(df['Order Year']==pyear) & (df['Category_ID']==str(curr_brand[0]))]
        pdff2 = df2[(df2['Order Year']==pyear) & (df2['Category_ID']==str(curr_brand[0]))]


    elif (len(curr_brand)>=1) and (len(curr_regions)>=1):
        dff = df[(df['Order Year']==curr_year) & (df['Category_ID']==str(curr_brand[0])) & (df['Region_ID'].isin(curr_regions))]
        dff2 = df2[(df2['Order Year']==curr_year) & (df2['Category_ID']==str(curr_brand[0]))]
        pdff = df[(df['Order Year']==pyear) & (df['Category_ID']==str(curr_brand[0])) & (df['Region_ID'].isin(curr_regions))]
        pdff2 = df2[(df2['Order Year']==pyear) & (df2['Category_ID']==str(curr_brand[0]))]
        
    else:
        dff = df[(df['Order Year']==curr_year)]
        dff2 = df2[(df2['Order Year']==curr_year)]
        pdff = df[(df['Order Year']==pyear)]
        pdff2 = df2[(df2['Order Year']==pyear)]

    #​Inventory Turnover=COGS/(( beginning inventory + ending inventory) / 2)
    #Ending Inventory = beginning inventory + restock - sales
    
    curr_price = dff2.groupby(["Product_ID"]).agg({'Retail Price' : 'mean'})
    curr_qty = dff.groupby(["Product_ID"]).agg({'Quantity' : 'sum'})
    curr_qty['Retail Price'] = curr_price['Retail Price']
    curr_stock = dff2.groupby(["Product_ID"]).agg({'Stock' : 'sum'})
    
    past_price = pdff2.groupby(["Product_ID"]).agg({'Retail Price' : 'mean'})
    past_qty = pdff.groupby(["Product_ID"]).agg({'Quantity' : 'sum'})
    past_qty['Retail Price'] = past_price['Retail Price']
    past_stock = pdff2.groupby(["Product_ID"]).agg({'Stock' : 'sum'})
    
    curr_data = pd.merge(curr_qty, curr_stock, on=['Product_ID'])
    past_data = pd.merge(past_qty, past_stock, on=['Product_ID'])
    
    curr_data['beg_inv'] = (past_data['Retail Price'] * past_data['Stock']) - (past_data['Retail Price'] * past_data['Quantity'])
    #beg_inventory = curr_data['beg_inv'].sum()
    past_data['end_inv'] = curr_data['beg_inv'] + (curr_data['Retail Price'] * curr_data['Stock']) - (curr_data['Retail Price'] * curr_data['Quantity'])
    #end_inventory = past_data['end_inv'].sum()

    curr_data['COGS'] = curr_data['Retail Price'] * curr_data['Quantity']
    
    dff = 365 / (curr_data['COGS'] / ((past_data['end_inv'] + curr_data['beg_inv'])/2))
    df_dii = dff.to_frame(name=curr_metric_col)
    df_dii = df_dii.reset_index()
    df_dii.sort_values(by=[curr_metric_col],ascending=[False],inplace=True)

    df_dii = df_dii.head()


    fig = px.bar(df_dii, x='Product_ID', y =curr_metric_col , color=curr_metric_col,
                    hover_data = ['Product_ID']
    
    )




    fig.update_layout(
        title = f'Worse Days in Inventory (DSI)',
        #paper_bgcolor="#1f2630",
        plot_bgcolor="#D3D3D3",
        margin=dict(t=75, r=50, b=100, l=50),
        font=dict(color="#000000")

    )
    return fig         

# product inventory graphs-metric selector
@app.callback([
     Output("app-container-3", "children"),
     ],

    Input("metric-dropdown", "value")
    
)
def inventory_metric_selector(metric):
    if metric == "inventory_metrics":
        return [
            
            html.Div([html.Div([
                        html.Div([
                            html.Div(
                                id='current-inventory-led-container',
                                children=[
                                    html.H6(
                                        #id='inventory-current-led-header',
                                        children=["Total Inventory Available"]
                                    ),

                                ],
                            ),
                            daq.LEDDisplay(
                                id="inventory-current-led",
                                label="Total Stock - Total Sales",
                                #value=5,
                                backgroundColor="#D3D3D3",
                                color="#000000",
                                size=70,
                            ), 
                            ],className="five columns"),
                        
                        html.Div([
                            html.Div(
                                id='turnover-led-container',
                                children=[
                                    html.H6(
                                        #id='inventory-turnover-led-header',
                                        children=["Days Sales of Inventory (DSI)"]
                                    ),

                                ],
                            ),

                            daq.LEDDisplay(
                                id="inventory-turnover-led",
                                label="Average Inventory/COGS * 365",
                                #value=5,
                                backgroundColor="#FF5E5E",
                                size=70,
                            ), 
                            ],className="five columns"),

                        ],className="row"),
                html.Div([
                    html.Br(),
                    html.Br(),
                    html.H3(id="inventory-gauage-title",
                    children=["Current Inventory with Reorder Point"],
                    ),
                    html.Div(
                        id='curr-inventory-gauage-container',
                        children=[
                            daq.GraduatedBar(
                                id="curr-inventory-gauage",
                                color={
                                    "gradient":True,
                                    "ranges":{"green":[20,50],"yellow":[5,19],"red":[0,4]}
                                    },
                                min = 0,
                                max=50,
                                step=1,
                                labelPosition= 'bottom',
                                showCurrentValue=False,
                                size=800,
                                value=15,
                                vertical=False,
                                theme={
                                    'dark': True,
                                },
                                
                            ), 
    
                        ],className='row'
    
                        
                    ),
                    html.Div(
                        id='curr-inventory-gauage-2-container',
                        children=[
                            daq.GraduatedBar(
                                id ='curr-inventory-gauage-2',
                                color={
                                    "ranges":{"orange":[0,50]}
                                    },
                                min=0,
                                max=50,
                                step=1,
                                labelPosition= 'bottom',
                                showCurrentValue=False,
                                size=800,
                                #value=15,
                                vertical=False,
                                theme={
                                    'dark': True,
                                },
                                
                            ), 
    
                        ],className='row'
          
                    ),
            
            html.Div([
                html.Div([
                    html.H6("Reorder Point (ROP)"),
                    daq.LEDDisplay(
                    id="rop-led",
                    label="lead time demand * safety stock",
                    #value=5,
                    backgroundColor="#FF5E5E",
                    color="#000000",
                    size=70,
                ), 
                    ],className="five columns"),
                
                html.Div([
                    html.H6("Quantity to Reorder"),
                    daq.LEDDisplay(
                    id="eoq-led",
                    label="EOQ - Total Inventory Available",
                    #value=5,
                    backgroundColor="#D3D3D3",
                    color="#000000",
                    size=70,
                ), 
                    ],className="five columns")
                
                ],className="row")])
                ])
                                      
                ]

    elif metric == "top_turnover":
        return [
            
                dcc.Graph(className="six columns",
                    id="best-turnover-graph",
                    figure = dict(
                        data=[dict(x=0, y=0)],
                        layout=dict(
                            #paper_bgcolor="#1f2630",
                            #plot_bgcolor="#1f2630",
                            autofill=True,
                            margin=dict(t=75, r=50, b=100, l=50),
                        ),
                    ), style={"display":"block"}
                ), # end area graph
           
            ]
    elif metric == "bottom_turnover":
        return [        
           
                dcc.Graph(className="six columns",
                    id="worse-turnover-graph",
                    figure = dict(
                        data=[dict(x=0, y=0)],
                        layout=dict(
                            #paper_bgcolor="#1f2630",
                            #plot_bgcolor="#1f2630",
                            autofill=True,
                            margin=dict(t=75, r=50, b=100, l=50),
                        ),
                    ), style={"display":"block"}
                ), # end area graph    
                                     
            
            ]
    else:
        return [html.H1("404: Not found", className="text-danger")]


# end from dashboard.py
# for loading data on screen
def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            if 'sale' in filename:
                if 'sale_product' in filename:
                    df_raw = pd.read_csv(io.BytesIO(decoded))
                    sql = 'SELECT max("Sale_ID") as max_order FROM "sale_product"'
                    df_order = querydatafromdatabase(sql,[],["max_order"])
                    input_id = int(df_order["max_order"][0])+1
                    df_raw['Sale_ID'] = list(range(input_id,input_id+len(df_raw.index)))
                    df = df_raw
                else:
                    df_raw = pd.read_csv(io.BytesIO(decoded))
                    sql = 'SELECT max("Sale_ID") as max_order FROM "sale"'
                    df_order = querydatafromdatabase(sql,[],["max_order"])
                    input_id = int(df_order["max_order"][0])+1
                    df_raw['Sale_ID'] = list(range(input_id,input_id+len(df_raw.index)))
                    df = df_raw   
            elif 'po' in filename:
                if 'po_product' in filename:
                    df_raw = pd.read_csv(io.BytesIO(decoded))
                    sql = 'SELECT max("PO_ID") as max_po FROM "po_product"'
                    df_inv = querydatafromdatabase(sql,[],["max_po"])
                    input_id = int(df_inv["max_po"][0])+1
                    df_raw['PO_ID'] = list(range(input_id,input_id+len(df_raw.index)))
                    df = df_raw
                else:
                    df_raw = pd.read_csv(io.BytesIO(decoded))
                    sql = 'SELECT max("PO_ID") as max_po FROM "po"'
                    df_inv = querydatafromdatabase(sql,[],["max_po"])
                    input_id = int(df_inv["max_po"][0])+1
                    df_raw['PO_ID'] = list(range(input_id,input_id+len(df_raw.index)))
                    df = df_raw
            else:
                df = pd.read_csv(io.BytesIO(decoded))

        elif 'xlsx' in filename:
            # Assume that the user uploaded an excel file
            if 'Order.completed.' in filename:
                # Assume data is from Online and requires column conversion
                df_raw = pd.read_excel(io.BytesIO(decoded))
                sql = 'SELECT max("Sale_ID") as "Sale_ID" FROM "sale"'
                df_sale = querydatafromdatabase(sql,[],["Sale_ID"])
                input_id = int(df_sale['Sale_ID'][0])+1
                #PO_ID = list(range(1,len(df_raw.index)+1))
                data = {
                    "Sale_ID": list(range(input_id,input_id+len(df_raw.index))),
                    "Sale Date": [x[:10] for x in df_raw["Order Creation Date"]], 
                    #"Category": df_raw["Parent SKU Reference No."].tolist(), 
                    #"Product_ID": df_raw["Product_ID"].tolist(), 
                    #"PO_ID": [str(x) for x in PO_ID], 
                    #"Sale Price": df_raw["Products' Price Paid by Buyer (PHP)"].tolist(), 
                    "Store_ID": ["Online"] * len(df_raw.index), 
                    #"Region_ID": df_raw["Province"].tolist(), 
                    #"Order Year": [x[:4] for x in df_raw["Order Creation Date"]], 
                    "City_ID": df_raw["City"].tolist(), 
                    #"Quantity": df_raw["Quantity"].tolist()
                #    }
                #data2 = {
                    #"Sale_ID": list(range(input_id,input_id+len(df_raw.index))),
                    #"Sale Date": [x[:10] for x in df_raw["Order Creation Date"]], 
                    #"Category": df_raw["Parent SKU Reference No."].tolist(), 
                    "Product_ID": df_raw["Product Name"].tolist(), 
                    #"PO_ID": [str(x) for x in PO_ID], 
                    "Sale Price": df_raw["Products' Price Paid by Buyer (PHP)"].tolist(), 
                    #"Store_ID": ["Online"] * len(df_raw.index), 
                    #"Region_ID": df_raw["Province"].tolist(), 
                    #"Order Year": [x[:4] for x in df_raw["Order Creation Date"]], 
                    #"City_ID": df_raw["City"].tolist(), 
                    "Quantity": df_raw["Quantity"].tolist()
                    }
                df = pd.DataFrame(data)
                #df2 = pd.DataFrame(data2)
            else:
                #data2 = []
                df = pd.read_csv(io.BytesIO(decoded))
                #df2 = pd.DataFrame(data2)
                
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

    return html.Div([
        html.Div([
                html.H5(filename),
                html.H6(datetime.datetime.fromtimestamp(date)),
                html.P("Displaying first 5 records."),
                dash_table.DataTable(
                    df[0:5].to_dict('records'),
                    [{'name': i, 'id': i} for i in df.columns]
                )
            ]),
      
       # html.Hr(),  # horizontal line

        # For debugging, display the raw contents provided by the web browser
       # html.Div('Raw Content'),
       # html.Pre(contents[0:200] + '...', style={
       #     'whiteSpace': 'pre-wrap',
       #     'wordBreak': 'break-all'
       # })
    ])

# for updating data in postgresql
def parse_contents2(contents, filename):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            if 'sale' in filename:
                if 'sale_product' in filename:
                    df_raw = pd.read_csv(io.BytesIO(decoded))
                    sql = 'SELECT max("Sale_ID") as max_order FROM "sale_product"'
                    df_order = querydatafromdatabase(sql,[],["max_order"])
                    input_id = int(df_order["max_order"][0])+1
                    df_raw['Sale_ID'] = list(range(input_id,input_id+len(df_raw.index)))
                    df = df_raw
                else:
                    df_raw = pd.read_csv(io.BytesIO(decoded))
                    sql = 'SELECT max("Sale_ID") as max_order FROM "sale"'
                    df_order = querydatafromdatabase(sql,[],["max_order"])
                    input_id = int(df_order["max_order"][0])+1
                    df_raw['Sale_ID'] = list(range(input_id,input_id+len(df_raw.index)))
                    df = df_raw   
            elif 'po' in filename:
                if 'po_product' in filename:
                    df_raw = pd.read_csv(io.BytesIO(decoded))
                    sql = 'SELECT max("PO_ID") as max_po FROM "po_product"'
                    df_inv = querydatafromdatabase(sql,[],["max_po"])
                    input_id = int(df_inv["max_po"][0])+1
                    df_raw['PO_ID'] = list(range(input_id,input_id+len(df_raw.index)))
                    df = df_raw
                else:
                    df_raw = pd.read_csv(io.BytesIO(decoded))
                    sql = 'SELECT max("PO_ID") as max_po FROM "po"'
                    df_inv = querydatafromdatabase(sql,[],["max_po"])
                    input_id = int(df_inv["max_po"][0])+1
                    df_raw['PO_ID'] = list(range(input_id,input_id+len(df_raw.index)))
                    df = df_raw
            else:
                df = pd.read_csv(io.BytesIO(decoded))

        elif 'xlsx' in filename:
            # Assume that the user uploaded an excel file
            if 'Order.completed.' in filename:
                # Assume data is from Online and requires column conversion
                df_raw = pd.read_excel(io.BytesIO(decoded))
                sql = 'SELECT max("Sale_ID") as "Sale_ID" FROM "sale"'
                df_order = querydatafromdatabase(sql,[],["Sale_ID"])
                input_id = int(df_order['Sale_ID'][0])+1
                data = {
                    "Sale_ID": list(range(input_id,input_id+len(df_raw.index))),
                    "Sale Date": [x[:10] for x in df_raw["Order Creation Date"]], 
                    "Store_ID": ["O"] * len(df_raw.index), 
                    "City_ID": df_raw["City"].tolist(), 
                    }
                #data2 = {
                #    "Sale_ID": list(range(input_id,input_id+len(df_raw.index))),
                #    "Product_ID": df_raw["Product Name"].tolist(), 
                #    "Sale Price": df_raw["Products' Price Paid by Buyer (PHP)"].tolist(), 
                #    "Quantity": df_raw["Quantity"].tolist()
                #    }
                df = pd.DataFrame(data)
                #df2 = pd.DataFrame(data2)
            else:
                df = pd.read_csv(io.BytesIO(decoded))

    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
            ])

    return  df
            
# for updating data in postgresql
def parse_contents3(contents, filename):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'xlsx' in filename:
            # Assume that the user uploaded an excel file
            if 'Order.completed.' in filename:
                # Assume data is from Online and requires column conversion
                df_raw = pd.read_excel(io.BytesIO(decoded))
                sql = 'SELECT max("Sale_ID") as "Sale_ID" FROM "sale"'
                df_order = querydatafromdatabase(sql,[],["Sale_ID"])
                input_id = int(df_order['Sale_ID'][0])+1
                data = {
                #    "Sale_ID": list(range(input_id,input_id+len(df_raw.index))),
                #    "Sale Date": [x[:10] for x in df_raw["Order Creation Date"]], 
                #    "Store_ID": ["O"] * len(df_raw.index), 
                #    "City_ID": df_raw["City"].tolist(), 
                #    }
                #data2 = {
                    "Sale_ID": list(range(input_id,input_id+len(df_raw.index))),
                    "Product_ID": df_raw["Product Name"].tolist(), 
                    "Sale Price": df_raw["Products' Price Paid by Buyer (PHP)"].tolist(), 
                    "Quantity": df_raw["Quantity"].tolist()
                    }
                df = pd.DataFrame(data)
                #df2 = pd.DataFrame(data2)
            else:
                df = pd.read_csv(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
            ])

    return  df
  
# start update callbacks
@app.callback(Output('output-data-upload', 'children'),
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'),
              State('upload-data', 'last_modified'))
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in zip(list_of_contents, list_of_names, list_of_dates)]
        return children
    
@app.callback(Output('output-data-upload2', 'children'),
              Input('upload-data2', 'contents'),
              State('upload-data2', 'filename'),
              State('upload-data2', 'last_modified'))
def update_output2(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in zip(list_of_contents, list_of_names, list_of_dates)]
        return children
    
@app.callback(Output('output-data-upload3', 'children'),
              Input('upload-data3', 'contents'),
              State('upload-data3', 'filename'),
              State('upload-data3', 'last_modified'))
def update_output3(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in zip(list_of_contents, list_of_names, list_of_dates)]
        return children
    
@app.callback(Output('output-data-upload4', 'children'),
              Input('upload-data4', 'contents'),
              State('upload-data4', 'filename'),
              State('upload-data4', 'last_modified'))
def update_output4(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in zip(list_of_contents, list_of_names, list_of_dates)]
        return children
    
@app.callback(Output('output-data-upload5', 'children'),
              Input('upload-data5', 'contents'),
              State('upload-data5', 'filename'),
              State('upload-data5', 'last_modified'))
def update_output5(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in zip(list_of_contents, list_of_names, list_of_dates)]
        return children
    
@app.callback(Output('output-data-upload6', 'children'),
              Input('upload-data6', 'contents'),
              State('upload-data6', 'filename'),
              State('upload-data6', 'last_modified'))
def update_output6(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in zip(list_of_contents, list_of_names, list_of_dates)]
        return children
    
@app.callback(Output('output-data-upload7', 'children'),
              Input('upload-data7', 'contents'),
              State('upload-data7', 'filename'),
              State('upload-data7', 'last_modified'))
def update_output7(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in zip(list_of_contents, list_of_names, list_of_dates)]
        return children
    
@app.callback(Output('output-data-upload8', 'children'),
              Input('upload-data8', 'contents'),
              State('upload-data8', 'filename'),
              State('upload-data8', 'last_modified'))
def update_output8(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in zip(list_of_contents, list_of_names, list_of_dates)]
        return children
    
@app.callback(Output('output-data-upload9', 'children'),
              Input('upload-data9', 'contents'),
              State('upload-data9', 'filename'),
              State('upload-data9', 'last_modified'))
def update_output9(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in zip(list_of_contents, list_of_names, list_of_dates)]
        return children

@app.callback(Output('output-data-online', 'children'),
              Input('upload-data10', 'contents'),
              State('upload-data10', 'filename'),
              State('upload-data10', 'last_modified'))
def update_output10(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in zip(list_of_contents, list_of_names, list_of_dates)]
        return children
# end update callbacks

## start upload callbacks
# order callbacks
@app.callback(
    Output('sale-notif', 'children'),

    [Input('sale-save-button', 'n_clicks'),
     Input('upload-data', 'contents')
     ],
    [
     State('upload-data', 'filename')
     ])
def sale_output(sale_save_button, list_of_contents, file_name):
   ctx = dash.callback_context
   if ctx.triggered:
       eventid = ctx.triggered[0]['prop_id'].split('.')[0]
       if eventid =="sale-save-button":
           if list_of_contents is not None:
               for c, n in zip(list_of_contents, file_name):
                   df = parse_contents2(c, n)
                   df_parsed = df[["Sale_ID","Sale Date","Store_ID","City_ID"]]
                   df_parsed.to_sql(name='sale',con=engine, if_exists='append', index=False)
               return ['Posting Sales was Successful!']
           else:
               return ['Error encountered.']
   else:
       return ['']

# inventory callbacks
@app.callback(
    Output('po-notif', 'children'),

    [Input('po-save-button', 'n_clicks'),
     Input('upload-data2', 'contents')
     ],
    [
     State('upload-data2', 'filename')
     ])
def inventory_output(po_save_button, list_of_contents, file_name):
   ctx = dash.callback_context
   if ctx.triggered:
       eventid = ctx.triggered[0]['prop_id'].split('.')[0]
       if eventid =="po-save-button":
           if list_of_contents is not None:
               for c, n in zip(list_of_contents, file_name):
                   df_parsed = parse_contents2(c, n)
                   df_parsed.to_sql(name='po',con=engine, if_exists='append', index=False)
               return ['Posting PO was Successful!']
           else:
               return ['Error encountered.']
   else:
       return ['']
   
# category callbacks
@app.callback(
    Output('cat-notif', 'children'),

    [Input('cat-save-button', 'n_clicks'),
     Input('upload-data3', 'contents')
     ],
    [
     State('upload-data3', 'filename')
     ])
def category_output(cat_save_button, list_of_contents, file_name):
   ctx = dash.callback_context
   if ctx.triggered:
       eventid = ctx.triggered[0]['prop_id'].split('.')[0]
       if eventid =="cat-save-button":
           if list_of_contents is not None:
               for c, n in zip(list_of_contents, file_name):
                   df_parsed = parse_contents2(c, n)
                   df_parsed.to_sql(name='category', con=engine, if_exists='append', index=False)
               return ['Posting Category was Successful!']
           else:
               return ['Error encountered.']
   else:
       return ['']
      
# store callbacks
@app.callback(
    Output('store-notif', 'children'),

    [Input('store-save-button', 'n_clicks'),
     Input('upload-data4', 'contents')
     ],
    [
     State('upload-data4', 'filename')
     ])
def store_output(store_save_button, list_of_contents, file_name):
   ctx = dash.callback_context
   if ctx.triggered:
       eventid = ctx.triggered[0]['prop_id'].split('.')[0]
       if eventid =="store-save-button":
           if list_of_contents is not None:
               for c, n in zip(list_of_contents, file_name):
                   df_parsed = parse_contents2(c, n)
                   df_parsed.to_sql(name='store', con=engine, if_exists='append', index=False)
               return ['Posting Store was Successful!']
           else:
               return ['Error encountered.']
   else:
       return ['']
      
# region callbacks
@app.callback(
    Output('region-notif', 'children'),

    [Input('region-save-button', 'n_clicks'),
     Input('upload-data5', 'contents')
     ],
    [
     State('upload-data5', 'filename')
     ])
def region_output(region_save_button, list_of_contents, file_name):
   ctx = dash.callback_context
   if ctx.triggered:
       eventid = ctx.triggered[0]['prop_id'].split('.')[0]
       if eventid =="region-save-button":
           if list_of_contents is not None:
               for c, n in zip(list_of_contents, file_name):
                   df_parsed = parse_contents2(c, n)
                   df_parsed.to_sql(name='region', con=engine, if_exists='append', index=False)
               return ['Posting Region was Successful!']
           else:
               return ['Error encountered.']
   else:
       return ['']
      
# city callbacks
@app.callback(
    Output('city-notif', 'children'),
    [Input('city-save-button', 'n_clicks'),
     Input('upload-data6', 'contents')
     ],
    [
     State('upload-data6', 'filename')
     ])
def city_output(city_save_button, list_of_contents, file_name):
   ctx = dash.callback_context
   if ctx.triggered:
       eventid = ctx.triggered[0]['prop_id'].split('.')[0]
       if eventid =="city-save-button":
           if list_of_contents is not None:
               for c, n in zip(list_of_contents, file_name):
                   df_parsed = parse_contents2(c, n)
                   df_parsed.to_sql(name='city', con=engine, if_exists='append', index=False)
               return ['Posting City was Successful!']
           else:
               return ['Error encountered.']
   else:
       return ['']
   
# product callbacks
@app.callback(
    Output('product-notif', 'children'),
    [Input('product-save-button', 'n_clicks'),
     Input('upload-data7', 'contents')
     ],
    [
     State('upload-data7', 'filename')
     ])
def product_output(product_save_button, list_of_contents, file_name):
   ctx = dash.callback_context
   if ctx.triggered:
       eventid = ctx.triggered[0]['prop_id'].split('.')[0]
       if eventid =="product-save-button":
           if list_of_contents is not None:
               for c, n in zip(list_of_contents, file_name):
                   df_parsed = parse_contents2(c, n)
                   #sqlinsert = "INSERT INTO category(Category, Category_text) VALUES(%s, %s)"
                   df_parsed.to_sql(name='product', con=engine, if_exists='append', index=False)
               return ['Posting Product was Successful!']
           else:
               return ['Error encountered.']
   else:
       return ['']
   
# product callbacks
@app.callback(
    Output('sale-product-notif', 'children'),
    [Input('sale-product-save-button', 'n_clicks'),
     Input('upload-data8', 'contents')
     ],
    [
     State('upload-data8', 'filename')
     ])
def sale_product_output(sale_product_save_button, list_of_contents, file_name):
   ctx = dash.callback_context
   if ctx.triggered:
       eventid = ctx.triggered[0]['prop_id'].split('.')[0]
       if eventid =="sale-product-save-button":
           if list_of_contents is not None:
               for c, n in zip(list_of_contents, file_name):
                   df = parse_contents2(c, n)
                   df_parsed = df[["Sale_ID","Product_ID","Sale Price","Quantity"]]
                   df_parsed.to_sql(name='sale_product', con=engine, if_exists='append', index=False)
               return ['Posting Sale Items was Successful!']
           else:
               return ['Error encountered.']
   else:
       return ['']
   
# product callbacks
@app.callback(
    Output('po-product-notif', 'children'),
    [Input('po-product-save-button', 'n_clicks'),
     Input('upload-data9', 'contents')
     ],
    [
     State('upload-data9', 'filename')
     ])
def po_product_output(po_product_save_button, list_of_contents, file_name):
   ctx = dash.callback_context
   if ctx.triggered:
       eventid = ctx.triggered[0]['prop_id'].split('.')[0]
       if eventid =="po-product-save-button":
           if list_of_contents is not None:
               for c, n in zip(list_of_contents, file_name):
                   df_parsed = parse_contents2(c, n)
                   df_parsed.to_sql(name='po_product', con=engine, if_exists='append', index=False)
               return ['Posting PO Items was Successful!']
           else:
               return ['Error encountered.']
   else:
       return ['']

# online sales callbacks
@app.callback(
    Output('online-notif', 'children'),
    [Input('online-save-button', 'n_clicks'),
     Input('upload-data10', 'contents')
     ],
    [
     State('upload-data10', 'filename')
     ])
def online_output(online_save_button, list_of_contents, file_name):
   ctx = dash.callback_context
   if ctx.triggered:
       eventid = ctx.triggered[0]['prop_id'].split('.')[0]
       if eventid =="online-save-button":
           if list_of_contents is not None:
               for c, n in zip(list_of_contents, file_name):
                   df_parsed2 = parse_contents2(c, n)
                   df_parsed3 = parse_contents3(c, n)
                   df_parsed2.to_sql(name='sale', con=engine, if_exists='append', index=False)
                   df_parsed3.to_sql(name='sale_product', con=engine, if_exists='append', index=False)
               return ['Posting Online Sales was Successful!']
           else:
               return ['Error encountered.']
   else:
       return ['']
# end upload callbacks



