
from dash import dcc
from dash import html
from dash.dependencies import Input, Output

# from dashboard.py
from apps import dashboard

# Connect to main app.py file
from app import app
import os

# define tab styles
tab_style = {
    'borderBottom': '2px solid #d6d6d6',
    'padding': '6px',
    'fontWeight': 'bold'
}

tab_selected_style = {
    'borderTop': '2px solid #d6d6d6',
    'borderBottom': '2px solid #d6d6d6',
    'backgroundColor': '#000000',
    'color': 'white',
    'padding': '6px'
}

# live updates
def serve_layout():
    return layout_index

# Create Pages      
layout_index = html.Div([
    
                html.Div([
                    
                #html.Img(id="logo", src=app.get_asset_url("logo.png")),
                
                    #html.Div([ html.H2('Kidsmart Dashboard'),
       
                    #],style={'display':'inline-block','margin-left':50}),
                            
                        ],
                        style={}),

    html.Div([
        dcc.Tabs(id='tabs', value='inventory-dash', children=[
            dcc.Tab(label='', value='home', style={background: app.get_asset_url("logo.png")}, selected_style={background: app.get_asset_url("logo.png")}),
            dcc.Tab(label='Sales Dashboard', value='sales-dash',style=tab_style, selected_style=tab_selected_style),
            dcc.Tab(label='Inventory Dashboard', value='inventory-dash',style=tab_style, selected_style=tab_selected_style),
            dcc.Tab(label='Upload Data', value='upload-data',style=tab_style, selected_style=tab_selected_style),

        ]),
    
    ], style={}),
    html.Div(id='tabs-content', style={}),

])
# end create pages

app.layout = serve_layout


# Tab callbacks
@app.callback(Output('tabs-content', 'children'),
              Input('tabs', 'value'))
def render_content(tab):
    if tab == 'sales-dash':
        return dashboard.layout1
    elif tab == 'inventory-dash':
        return dashboard.layout2
    elif tab == 'upload-data':   
        return dashboard.layout3


app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

if __name__ == '__main__':
    app.run_server(debug=False)
