import pathlib
import pandas as pd
import numpy as np
import psycopg2
import datetime
import math

# Load data

#APP_PATH = pathlib.Path(__file__).parent
#DATA_PATH = APP_PATH.joinpath("../data").resolve()

def querydatafromdatabase(sql, values,dbcolumns):
    db = psycopg2.connect(
        user="hychua",
        password="OiA31iCst2NPewhNhKLf2aj7PzkboXfw",
        host="dpg-csparlpu0jms73bhujs0-a.oregon-postgres.render.com",
        port=5432,
        database="kidsmart_5")
    cur = db.cursor()
    cur.execute(sql, values)
    rows = pd.DataFrame(cur.fetchall(), columns=dbcolumns)
    db.close()
    return rows

def modifydatabase(sqlcommand, values):
    db = psycopg2.connect(
            user="hychua",
            password="OiA31iCst2NPewhNhKLf2aj7PzkboXfw",
            host="dpg-csparlpu0jms73bhujs0-a.oregon-postgres.render.com",
            port=5432,
            database="kidsmart_5")
    cursor = db.cursor()
    cursor.execute(sqlcommand, values)
    db.commit()
    db.close()

#df_order = pd.read_csv(DATA_PATH.joinpath("full_data.csv"),parse_dates=True)
#df_po = pd.read_csv(DATA_PATH.joinpath("inv_data.csv"),parse_dates=True)
#df_category = pd.read_csv(DATA_PATH.joinpath("cat_text.csv"),parse_dates=True)

sql1 = 'SELECT * FROM "sale"'
sql2 = "SELECT * FROM product"
sql3 = "SELECT * FROM category"
sql4 = "SELECT * FROM po"
sql5 = "SELECT * FROM sale_product"
sql6 = "SELECT * FROM po_product"
sql7 = "SELECT * FROM city"
df_order = querydatafromdatabase(sql1,[],["Sale_ID", "Sale Date", "Store_ID", "City_ID"])
#df_product = querydatafromdatabase(sql2,[],["Product_ID", "Product Name", "Category_ID"])
#df_category = querydatafromdatabase(sql3,[],["Category_ID","Category_text"])
#df_po = querydatafromdatabase(sql4,[],["PO_ID","Release Date"])
#df_sale_product = querydatafromdatabase(sql5,[],["Sale_ID","Product_ID","Quantity","Sale Price"])
#df_po_product = querydatafromdatabase(sql6,[],["PO_ID","Product_ID","Stock","Retail Price"])
#df_city = querydatafromdatabase(sql7,[],["City_ID", "Buyer City", "Region_ID"])
        
# Create variables 
df_order['Sale Date'] = pd.to_datetime(df_order['Sale Date'])
df_order["Order Year"] = df_order["Sale Date"].dt.year
YEARS_INVENTORY = df_order['Order Year'].unique().tolist()

# Create value ranges for inventory gauge
ALL_OPTIONS = [
                {
                    "label": "Total Sales",
                    "value":"total_sales"
                },
                {
                    "label": "Count of Sales",
                    "value":"count_sales",
                },
                {
                    "label": "Average Sales per Order",
                    "value":"avg_sales",
                },
                {
                    "label": "Current Inventory",
                    "value":"curr_inventory",
                },
                {
                    "label": "Current Inventory 2",
                    "value":"curr_inventory2",
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
                    "label": "Average Net Profit",
                    "value":"avg_net_profit",
                },
                {
                    "label": "Top Avg Net Profit",
                    "value":"top_avg_net_profit",
                },
                {
                    "label": "Bottom Avg Net Profit",
                    "value":"bottom_avg_net_profit",
                },
                {
                    "label": "Average Inventory Turnover",
                    "value":"avg_inventory_turnover"
                },
                {
                    "label": "Top Inventory Turnover",
                    "value":"top_avg_inventory_turnover"
                },
                {
                    "label": "Bottom Inventory Turnover",
                    "value":"bottom_avg_inventory_turnover"
                },
                {
                    "label": "Reorder Point",
                    "value":"reorder_point"
                },
                {
                    "label": "Quantity to Reorder",
                    "value":"economic_order_quantity"
                }
            ]


# Create functions
def create_plot_metric(filters,metric_type="total_sales"):
    
    if metric_type == "total_sales":
        return get_total_sales(filters)
    
    if metric_type == "count_sales" :
        return get_count_sales(filters)
    
    if metric_type == "avg_sales":
        return get_avg_sales(filters)
    
    if metric_type == "curr_inventory":
        return get_curr_inventory(filters)
    
    if metric_type == "curr_inventory2":
        return get_curr_inventory2(filters)
                                  
    if metric_type == "top_performers":
        return get_top_performers(filters)
    
    if metric_type == "bottom_performers":
        return get_bottom_performers(filters)
    
    if metric_type == "avg_net_profit":
        return get_avg_net_profit(filters)
    
    if metric_type == "top_avg_net_profit":
        return get_top_avg_net_profit(filters)
    
    if metric_type == "bottom_avg_net_profit":
        return get_bottom_avg_net_profit(filters)
    
    if metric_type == "avg_inventory_turnover":
        return get_avg_inventory_turnover(filters)
    
    if metric_type == "top_avg_inventory_turnover":
        return get_top_avg_inventory_turnover(filters)
    
    if metric_type == "bottom_avg_inventory_turnover":
        return get_bottom_avg_inventory_turnover(filters)

    if metric_type == "sales_over_time":
        return get_sales_over_time(filters)


def get_total_sales(filters):
    df_order = querydatafromdatabase(sql1,[],["Sale_ID", "Sale Date", "Store_ID", "City_ID"])
    df_city = querydatafromdatabase(sql7,[],["City_ID", "Buyer City", "Region_ID"])
    df_sale_product = querydatafromdatabase(sql5,[],["Sale_ID","Product_ID","Quantity","Sale Price"])
    df_product = querydatafromdatabase(sql2,[],["Product_ID", "Product Name", "Category_ID"])
    
    # append order year
    df_order['Sale Date'] = pd.to_datetime(df_order['Sale Date'])
    df_order["Order Year"] = df_order["Sale Date"].dt.year
    
    # merge city
    m_city = pd.merge(df_order, df_city, on=["City_ID"])
    
    # merge product
    m_product = pd.merge(df_sale_product, df_product, on=["Product_ID"])
    
    # merge city with product
    m_order = pd.merge(m_city, m_product, on=["Sale_ID"])
    
    m_order['Subtotal Sales'] = m_order['Quantity'] * m_order["Sale Price"]
    data =  m_order.groupby(filters,as_index=False).agg({'Subtotal Sales':['sum']})
    filters.append('Total Sales')
    data.columns = filters
    data.sort_values(by=['Total Sales'],ascending=[False],inplace=True)
    return data

def get_count_sales(filters):    
    df_order = querydatafromdatabase(sql1,[],["Sale_ID", "Sale Date", "Store_ID", "City_ID"])
    df_city = querydatafromdatabase(sql7,[],["City_ID", "Buyer City", "Region_ID"])
    df_sale_product = querydatafromdatabase(sql5,[],["Sale_ID","Product_ID","Quantity","Sale Price"])
    df_product = querydatafromdatabase(sql2,[],["Product_ID", "Product Name", "Category_ID"])
    
    # append order year
    df_order['Sale Date'] = pd.to_datetime(df_order['Sale Date'])
    df_order["Order Year"] = df_order["Sale Date"].dt.year
    
    # merge city
    m_city = pd.merge(df_order, df_city, on=["City_ID"])
    
    # merge product
    m_product = pd.merge(df_sale_product, df_product, on=["Product_ID"])
    
    # merge city with product
    m_order = pd.merge(m_city, m_product, on=["Sale_ID"])
    
    data =  m_order.groupby(filters,as_index=False).agg({'Quantity':['sum']})
    filters.append('Sales Count')
    data.columns = filters
    data.sort_values(by=['Sales Count'],ascending=[False],inplace=True)
    return data

def get_avg_sales(filters):    
    df_order = querydatafromdatabase(sql1,[],["Sale_ID", "Sale Date", "Store_ID", "City_ID"])
    df_city = querydatafromdatabase(sql7,[],["City_ID", "Buyer City", "Region_ID"])
    df_sale_product = querydatafromdatabase(sql5,[],["Sale_ID","Product_ID","Quantity","Sale Price"])
    df_product = querydatafromdatabase(sql2,[],["Product_ID", "Product Name", "Category_ID"])
    
    # append order year
    df_order['Sale Date'] = pd.to_datetime(df_order['Sale Date'])
    df_order["Order Year"] = df_order["Sale Date"].dt.year
    
    # merge city
    m_city = pd.merge(df_order, df_city, on=["City_ID"])
    
    # merge product
    m_product = pd.merge(df_sale_product, df_product, on=["Product_ID"])
    
    # merge city with product
    m_order = pd.merge(m_city, m_product, on=["Sale_ID"])
    m_order['Subtotal Sales'] = m_order['Quantity'] * m_order["Sale Price"]
    data =  m_order.groupby(filters,as_index=False).agg({'Subtotal Sales':['mean']})
    filters.append('Avg Sales')
    data.columns = filters
    data.sort_values(by=['Avg Sales'],ascending=[False],inplace=True)
    return data

# sales count
def get_curr_inventory(filters):    
    df_order = querydatafromdatabase(sql1,[],["Sale_ID", "Sale Date", "Store_ID", "City_ID"])
    df_city = querydatafromdatabase(sql7,[],["City_ID", "Buyer City", "Region_ID"])
    df_sale_product = querydatafromdatabase(sql5,[],["Sale_ID","Product_ID","Quantity","Sale Price"])
    df_product = querydatafromdatabase(sql2,[],["Product_ID", "Product Name", "Category_ID"])
    
    # append order year
    df_order['Sale Date'] = pd.to_datetime(df_order['Sale Date'])
    df_order["Order Year"] = df_order["Sale Date"].dt.year
    
    # merge city
    m_city = pd.merge(df_order, df_city, on=["City_ID"])
    
    # merge product
    m_product = pd.merge(df_sale_product, df_product, on=["Product_ID"])
    
    # merge city with product
    m_order = pd.merge(m_city, m_product, on=["Sale_ID"])
    
    data =  m_order.groupby(filters,as_index=False).agg({'Quantity':['sum']})
    filters.extend(['Order Quantity'])
    data.columns = filters
    data.sort_values(by=['Order Quantity'],ascending=[True],inplace=True)
    return data

# po count
def get_curr_inventory2(filters):    
    df_po = querydatafromdatabase(sql4,[],["PO_ID","Release Date"])
    df_po_product = querydatafromdatabase(sql6,[],["PO_ID","Product_ID","Stock","Retail Price"])
    df_product = querydatafromdatabase(sql2,[],["Product_ID", "Product Name", "Category_ID"])
    
    # append order year
    df_po['Release Date'] = pd.to_datetime(df_po['Release Date'])
    df_po["Order Year"] = df_po["Release Date"].dt.year
    
    # merge product
    m_product = pd.merge(df_po_product, df_product, on=["Product_ID"])
    
    # merge po with product
    m_po = pd.merge(df_po, m_product, on=["PO_ID"])
    m_po['Stock'] = round(m_po['Stock']/10)*10
    
    data =  m_po.groupby(filters,as_index=False).agg({'Stock':['sum']})
    filters.append('Current Inventory 2')
    data.columns = filters
    data.sort_values(by=['Current Inventory 2'],ascending=[True],inplace=True)
    return data

def get_top_performers(filters):    
    df_order = querydatafromdatabase(sql1,[],["Sale_ID", "Sale Date", "Store_ID", "City_ID"])
    df_city = querydatafromdatabase(sql7,[],["City_ID", "Buyer City", "Region_ID"])
    df_sale_product = querydatafromdatabase(sql5,[],["Sale_ID","Product_ID","Quantity","Sale Price"])
    df_product = querydatafromdatabase(sql2,[],["Product_ID", "Product Name", "Category_ID"])
    
    # append order year
    df_order['Sale Date'] = pd.to_datetime(df_order['Sale Date'])
    df_order["Order Year"] = df_order["Sale Date"].dt.year
    
    # merge city
    m_city = pd.merge(df_order, df_city, on=["City_ID"])
    
    # merge product
    m_product = pd.merge(df_sale_product, df_product, on=["Product_ID"])
    
    # merge city with product
    m_order = pd.merge(m_city, m_product, on=["Sale_ID"])
    
    data =  m_order.copy()
    data['Retail Price'] = data['Sale Price']/2
    data['net_profit'] = data['Sale Price'] - data['Retail Price']
    data = data.groupby(filters,as_index=False).agg({'net_profit':['sum']})
    filters.append('Net Profit')
    data.columns = filters
    data.sort_values(by=['Net Profit'],ascending=[False],inplace=True)
    return data


def get_bottom_performers(filters):    
    df_order = querydatafromdatabase(sql1,[],["Sale_ID", "Sale Date", "Store_ID", "City_ID"])
    df_city = querydatafromdatabase(sql7,[],["City_ID", "Buyer City", "Region_ID"])
    df_sale_product = querydatafromdatabase(sql5,[],["Sale_ID","Product_ID","Quantity","Sale Price"])
    df_product = querydatafromdatabase(sql2,[],["Product_ID", "Product Name", "Category_ID"])
    
    # append order year
    df_order['Sale Date'] = pd.to_datetime(df_order['Sale Date'])
    df_order["Order Year"] = df_order["Sale Date"].dt.year
    
    # merge city
    m_city = pd.merge(df_order, df_city, on=["City_ID"])
    
    # merge product
    m_product = pd.merge(df_sale_product, df_product, on=["Product_ID"])
    
    # merge city with product
    m_order = pd.merge(m_city, m_product, on=["Sale_ID"])
    
    data =  m_order.copy()
    data['Retail Price'] = data['Sale Price']/2
    data['net_profit'] = data['Sale Price'] - data['Retail Price']
    data = data.groupby(filters,as_index=False).agg({'net_profit':['sum']})
    filters.append('Net Profit')
    data.columns = filters
    data.sort_values(by=['Net Profit'],ascending=[True],inplace=True)
    return data


def get_avg_net_profit(filters):    
    df_order = querydatafromdatabase(sql1,[],["Sale_ID", "Sale Date", "Store_ID", "City_ID"])
    df_city = querydatafromdatabase(sql7,[],["City_ID", "Buyer City", "Region_ID"])
    df_sale_product = querydatafromdatabase(sql5,[],["Sale_ID","Product_ID","Quantity","Sale Price"])
    df_product = querydatafromdatabase(sql2,[],["Product_ID", "Product Name", "Category_ID"])
    
    # append order year
    df_order['Sale Date'] = pd.to_datetime(df_order['Sale Date'])
    df_order["Order Year"] = df_order["Sale Date"].dt.year
    
    # merge city
    m_city = pd.merge(df_order, df_city, on=["City_ID"])
    
    # merge product
    m_product = pd.merge(df_sale_product, df_product, on=["Product_ID"])
    
    # merge city with product
    m_order = pd.merge(m_city, m_product, on=["Sale_ID"])
    
    data =  m_order.copy()
    data['Retail Price'] = data['Sale Price']/2
    data['net_profit'] = data['Sale Price'] - data['Retail Price']
    data = data.groupby(filters,as_index=False).agg({'net_profit':['mean']})
    filters.append('Avg Net Profit')
    data.columns = filters
    data.sort_values(by=['Avg Net Profit'],ascending=[False],inplace=True)
    return data

def get_top_avg_net_profit(filters):
    df_order = querydatafromdatabase(sql1,[],["Sale_ID", "Sale Date", "Store_ID", "City_ID"])
    df_city = querydatafromdatabase(sql7,[],["City_ID", "Buyer City", "Region_ID"])
    df_sale_product = querydatafromdatabase(sql5,[],["Sale_ID","Product_ID","Quantity","Sale Price"])
    df_product = querydatafromdatabase(sql2,[],["Product_ID", "Product Name", "Category_ID"])
    
    # append order year
    df_order['Sale Date'] = pd.to_datetime(df_order['Sale Date'])
    df_order["Order Year"] = df_order["Sale Date"].dt.year
    
    # merge city
    m_city = pd.merge(df_order, df_city, on=["City_ID"])
    
    # merge product
    m_product = pd.merge(df_sale_product, df_product, on=["Product_ID"])
    
    # merge city with product
    m_order = pd.merge(m_city, m_product, on=["Sale_ID"])
    
    data =  m_order.copy()
    data['Retail Price'] = data['Sale Price']/2
    data['net_profit'] = data['Sale Price'] - data['Retail Price']
    data = data.groupby(filters,as_index=False).agg({'net_profit':['mean']})
    filters.append('Avg Net Profit')
    data.columns = filters
    data.sort_values(by=['Avg Net Profit'],ascending=[False],inplace=True)
    return data


def get_bottom_avg_net_profit(filters):
    df_order = querydatafromdatabase(sql1,[],["Sale_ID", "Sale Date", "Store_ID", "City_ID"])
    df_city = querydatafromdatabase(sql7,[],["City_ID", "Buyer City", "Region_ID"])
    df_sale_product = querydatafromdatabase(sql5,[],["Sale_ID","Product_ID","Quantity","Sale Price"])
    df_product = querydatafromdatabase(sql2,[],["Product_ID", "Product Name", "Category_ID"])
    
    # append order year
    df_order['Sale Date'] = pd.to_datetime(df_order['Sale Date'])
    df_order["Order Year"] = df_order["Sale Date"].dt.year
    
    # merge city
    m_city = pd.merge(df_order, df_city, on=["City_ID"])
    
    # merge product
    m_product = pd.merge(df_sale_product, df_product, on=["Product_ID"])
    
    # merge city with product
    m_order = pd.merge(m_city, m_product, on=["Sale_ID"])
    
    data =  m_order.copy()
    data['Retail Price'] = data['Sale Price']/2
    data['net_profit'] = data['Sale Price'] - data['Retail Price']
    data = data.groupby(filters,as_index=False).agg({'net_profit':['mean']})
    filters.append('Avg Net Profit')
    data.columns = filters
    data.sort_values(by=['Avg Net Profit'],ascending=[True],inplace=True)
    return data



def get_avg_inventory_turnover(filters):
    df_order = querydatafromdatabase(sql1,[],["Sale_ID", "Sale Date", "Store_ID", "City_ID"])
    df_sale_product = querydatafromdatabase(sql5,[],["Sale_ID","Product_ID","Quantity","Sale Price"])
    df_po = querydatafromdatabase(sql4,[],["PO_ID","Release Date"])
    df_po_product = querydatafromdatabase(sql6,[],["PO_ID","Product_ID","Stock","Retail Price"])
    df_product = querydatafromdatabase(sql2,[],["Product_ID", "Product Name", "Category_ID"])
    
    # append order year
    df_order['Sale Date'] = pd.to_datetime(df_order['Sale Date'])
    df_order["Order Year"] = df_order["Sale Date"].dt.year
    df_po['Release Date'] = pd.to_datetime(df_po['Release Date'])
    df_po['Order Year'] = df_po["Release Date"].year
    m_order = pd.merge(df_order, df_sale_product, on=["Sale_ID"])
    m_po = pd.merge(df_po, df_po_product, on=["PO_ID"])
    
    # merge category
    m_category = pd.merge(m_order, df_product, on=["Product_ID"])
    m_category2 = pd.merge(m_po, df_product, on=["Product_ID"])
    
    m_data = pd.merge(m_category, m_category2, on=['Product_ID','Order Year'])
    #m_data['Sale Date'] = pd.to_datetime(m_data['Sale Date'])
    #m_data['Release Date'] = pd.to_datetime(m_data['Release Date'])

    m_data['days_in_inventory'] = (m_data['Sale Date'] - m_data['Release Date'])/np.timedelta64(1,'D')
    m_data = m_data.groupby(filters,as_index=False).agg({'days_in_inventory':['mean']})
    filters.append('Inventory Turnover')
    m_data.columns = filters
    m_data.sort_values(by=['Inventory Turnover'],ascending=[True],inplace=True)
    return m_data

def get_top_avg_inventory_turnover(filters):
    df_order = querydatafromdatabase(sql1,[],["Sale_ID", "Sale Date", "Store_ID", "City_ID"])
    df_sale_product = querydatafromdatabase(sql5,[],["Sale_ID","Product_ID","Quantity","Sale Price"])
    df_po = querydatafromdatabase(sql4,[],["PO_ID","Release Date"])
    df_po_product = querydatafromdatabase(sql6,[],["PO_ID","Product_ID","Stock","Retail Price"])
    df_product = querydatafromdatabase(sql2,[],["Product_ID", "Product Name", "Category_ID"])
    data =  df_sale_product.copy()
    data2 = df_po_product.copy()
    
    # append order year
    df_order['Sale Date'] = pd.to_datetime(df_order['Sale Date'])
    df_order["Order Year"] = df_order["Sale Date"].dt.year
    df_po['Release Date'] = pd.to_datetime(df_po['Release Date'])
    df_po['Order Year'] = df_po["Release Date"].year
    m_year = pd.merge(data, df_order, on=["Sale_ID"])
    m_year2 = pd.merge(data2, df_po, on=["PO_ID"])
    
    # merge category
    m_category = pd.merge(m_year, df_product, on=["Product_ID"])
    m_category2 = pd.merge(m_year2, df_product, on=["Product_ID"])
    
    m_data = pd.merge(m_category, m_category2, on=['Product_ID','Order Year','Category_ID'])
    m_data['Sale Date'] = pd.to_datetime(m_data['Sale Date'])
    m_data['Release Date'] = pd.to_datetime(m_data['Release Date'])

    m_data['days_in_inventory'] = (m_data['Sale Date'] - m_data['Release Date'])/np.timedelta64(1,'D')
    m_data = m_data.groupby(filters,as_index=False).agg({'days_in_inventory':['mean']})
    filters.append('Inventory Turnover')
    m_data.columns = filters
    m_data.sort_values(by=['Inventory Turnover'],ascending=[True],inplace=True)
    return m_data.head(10)


def get_bottom_avg_inventory_turnover(filters):
    df_order = querydatafromdatabase(sql1,[],["Sale_ID", "Sale Date", "Store_ID", "City_ID"])
    df_sale_product = querydatafromdatabase(sql5,[],["Sale_ID","Product_ID","Quantity","Sale Price"])
    df_po = querydatafromdatabase(sql4,[],["PO_ID","Release Date"])
    df_po_product = querydatafromdatabase(sql6,[],["PO_ID","Product_ID","Stock","Retail Price"])
    df_product = querydatafromdatabase(sql2,[],["Product_ID", "Product Name", "Category_ID"])
    data =  df_sale_product.copy()
    data2 = df_po_product.copy()
    
    # append order year
    df_order['Sale Date'] = pd.to_datetime(df_order['Sale Date'])
    df_order["Order Year"] = df_order["Sale Date"].dt.year
    df_po['Release Date'] = pd.to_datetime(df_po['Release Date'])
    df_po['Order Year'] = df_po["Release Date"].year
    m_year = pd.merge(data, df_order, on=["Sale_ID"])
    m_year2 = pd.merge(data2, df_po, on=["PO_ID"])
    
    # merge category
    m_category = pd.merge(m_year, df_product, on=["Product_ID"])
    m_category2 = pd.merge(m_year2, df_product, on=["Product_ID"])
    
    m_data = pd.merge(m_category, m_category2, on=['Product_ID','Order Year','Category_ID'])
    m_data['Sale Date'] = pd.to_datetime(m_data['Sale Date'])
    m_data['Release Date'] = pd.to_datetime(m_data['Release Date'])

    m_data['days_in_inventory'] = (m_data['Sale Date'] - m_data['Release Date'])/np.timedelta64(1,'D')
    m_data = m_data.groupby(filters,as_index=False).agg({'days_in_inventory':['mean']})
    filters.append('Inventory Turnover')
    m_data.columns = filters
    m_data.sort_values(by=['Inventory Turnover'],ascending=[False],inplace=True)
    m_data = m_data.dropna()
    return m_data.head(10)

def get_sales_over_time(filters):
    df_sale_product = querydatafromdatabase(sql5,[],["Sale_ID","Product_ID","Quantity","Sale Price"])
    data = df_sale_product[filters].copy()   
    return data