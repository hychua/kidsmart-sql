import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
import dash-bootstrap-components as dbc

# from dashboard.py
from apps import dashboard

# Connect to main app.py file
from app import app
import os


# define tab styles
tab_style = {
    'borderTop': '1px solid #d6d6d6',
    'borderBottom': '1px solid #d6d6d6',
    'height': '10rem',
    'padding': '3.5rem',
    'font-size': '1.7rem'
}

tab_selected_style = {
    'borderTop': '1px solid #d6d6d6',
    'borderBottom': '1px solid #d6d6d6',
    'backgroundColor': '#000000',
    'color': 'white',
    'height': '10rem',
    'padding': '3.5rem',
    'font-size': '1.7rem'
}

# make a reuseable navitem for the different examples
inv_item = dbc.NavItem(dbc.NavLink("Inventory |", href="/inventory"))
sale_item = dbc.NavItem(dbc.NavLink("Sales |", href="/sales"))

# make a reuseable dropdown for the different examples
dropdown = dbc.DropdownMenu(
    children=[
        dbc.DropdownMenuItem("SALE", href="/order", style = {"font-size": "1.5rem"}),
        dbc.DropdownMenuItem("SALE ITEMS", href="/sale_product", style = {"font-size": "1.5rem"}),
        dbc.DropdownMenuItem("PO", href="/po", style = {"font-size": "1.5rem"}),
        dbc.DropdownMenuItem("PO ITEMS", href="/po_product", style = {"font-size": "1.5rem"}),
        dbc.DropdownMenuItem("PRODUCT", href="/product", style = {"font-size": "1.5rem"}),
        dbc.DropdownMenuItem("CATEGORY", href="/category", style = {"font-size": "1.5rem"}),
        dbc.DropdownMenuItem("STORE", href="/store", style = {"font-size": "1.5rem"}),
        dbc.DropdownMenuItem("REGION", href="/region", style = {"font-size": "1.5rem"}),
        dbc.DropdownMenuItem("CITY", href="/city", style = {"font-size": "1.5rem"}),
    ],
    nav=True,
    in_navbar=True,
    label="Upload",
    
)

# this example that adds a logo to the navbar brand
navbar = dbc.Navbar(
    dbc.Container(
        [
            html.A(
                # Use row and col to control vertical alignment of logo / brand
                dbc.Row(
                    [
                        dbc.Col(html.Img(id="logo", src=app.get_asset_url("logo.png"))),
                        dbc.Col(dbc.NavbarBrand("Kidsmart Dashboard", style = {"font-size": "2rem","padding-left":"1rem"})),
                    ],
                align="center",
                className="g-0",
                ),
                href = "https://shopee.ph/megaluck",
                style={"textDecoration": "none"},
            ),
            dbc.NavbarToggler(id="navbar-toggler", n_clicks=0),
            dbc.Collapse(
                dbc.Nav(
                    [inv_item, sale_item, dropdown],
                    className="ms-auto",
                    navbar=True,
                ),
                id="navbar-collapse",
                navbar=True,
            ),
        ],
    ),
    color="dark",
    dark=True,
    className="mb-5",
    style = {"font-size": "2rem"}
)

app.layout = html.Div(
    [
        dcc.Location(id="url", refresh=False, pathname="/inventory"),
        navbar,
        dbc.Container(id="page-content", fluid=True),
    ]
)


@app.callback(Output("page-content", "children"), Input("url", "pathname"))
def display_page(pathname):
    if pathname == "/inventory":
        return dashboard.layout2
    elif pathname == "/sales":
        return dashboard.layout1
    elif pathname == "/order":
        return dashboard.sale_page
    elif pathname == "/sale_product":
        return dashboard.sale_product_page
    elif pathname == "/po":
        return dashboard.po_page
    elif pathname == "/po_product":
        return dashboard.po_product_page
    elif pathname == "/product":
        return dashboard.product_page
    elif pathname == "/category":
        return dashboard.category_page
    elif pathname == "/store":
        return dashboard.store_page
    elif pathname == "/region":
        return dashboard.region_page
    elif pathname == "/city":
        return dashboard.city_page
    else:
        return dbc.Jumbotron(
            [
                html.H1("404: Not found", className="text-danger"),
                html.Hr(),
                html.P(f"The pathname {pathname} was not recognized..."),
            ]
        )


# we use a callback to toggle the collapse on small screens
def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


# the same function (toggle_navbar_collapse) is used in all three callbacks
for i in [1, 2, 3]:
    app.callback(
        Output(f"navbar-collapse{i}", "is_open"),
        [Input(f"navbar-toggler{i}", "n_clicks")],
        [State(f"navbar-collapse{i}", "is_open")],
    )(toggle_navbar_collapse)


#app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

if __name__ == '__main__':
    app.run_server(debug=False)
