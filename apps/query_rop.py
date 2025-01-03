import pandas as pd
import numpy as np
import psycopg2

def querydatafromdatabase(sql, values,dbcolumns):
    db = psycopg2.connect(
        user="kidsmart_6_user",
        password="xKtAHODVAHVwDJRYh04S4Xu8p7n6Sd0l",
        host="dpg-ctn13a9opnds73fjd03g-a.oregon-postgres.render.com",
        port=5432,
        database="kidsmart_6")
    cur = db.cursor()
    cur.execute(sql, values)
    rows = pd.DataFrame(cur.fetchall(), columns=dbcolumns)
    db.close()
    return rows

curr_year = 2023

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

df_sale = df.groupby(["Product_ID"]).agg({'Quantity' : 'sum'}).reset_index()
df_po = df2.groupby(["Product_ID"]).agg({'Stock' : 'sum'}).reset_index()
# inventory = po - sales
df_inv = pd.merge(df_sale, df_po, on=['Product_ID']).set_axis(df_sale.index)
df_inv['Inventory'] = df_po['Stock'] - df_sale['Quantity']
df_inv = df_inv.drop(columns=['Quantity', 'Stock'])
#ROP = max. daily sales x max. lead time
df_sale_date = df.groupby(["Product_ID","Sale Date"]).agg({'Quantity' : 'sum'}).reset_index()
df_sale_max = df_sale_date.groupby(["Product_ID"]).agg({'Quantity':'max'}).reset_index()
df_sale_max['ROP'] = df_sale_max['Quantity'] * 3
df_rop = pd.merge(df_inv, df_sale_max, on=['Product_ID']).set_axis(df_inv.index)
df_eoq = pd.merge(df_rop,df[["Product_ID","Sale Price"]],on=["Product_ID"])
df_unique = df_eoq.drop_duplicates()
#EOQ Method = √ (2DS/H)
#where : 
#D : annual demand for material inventory 
#S : costs required per order
#H : holding cost per unit annually
holding = 18220.91 / df_unique["Inventory"].sum()
#EOQ = sqrt(2*Qty*Price/Holding Cost)
df_unique['EOQ'] = np.sqrt(2*df_unique['Quantity']*df_unique['Sale Price']/holding)
#print(df_unique)

# saving the DataFrame as a CSV file 
csv_data = df_unique.to_csv('EOQ.csv', index = True) 
print('\nCSV String:\n', csv_data) 