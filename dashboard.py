import streamlit as st 
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


#helper function untuk grafik
def create_monthly_orders_df(df):
    monthly_orders_df = df.resample(rule='M', on='order_purchase_timestamp').agg({
        "order_id": "nunique",
        "price": "sum"
    })
    monthly_orders_df.index = monthly_orders_df.index.strftime('%m-%Y')
    monthly_orders_df = monthly_orders_df.reset_index()
    monthly_orders_df.rename(columns={
        "order_id": "order_count",
        "price": "total_revenue"
    }, inplace=True)
    return monthly_orders_df


def create_sum_order_item(df):
    sum_order_items_df = df.groupby("product_category_name").order_item_id.sum().sort_values(ascending=False).reset_index()
    return sum_order_items_df

def cust_by_city(df):
    cust_by_city_df = df.groupby(by="customer_city").customer_id.nunique().reset_index()
    cust_by_city_df.rename(columns={
        "customer_id": "customer_count"
    }, inplace=True)
    return cust_by_city_df

def cust_by_state(df):
    cust_by_state_df = df.groupby(by="customer_state").customer_id.nunique().reset_index()
    cust_by_state_df.rename(columns={
        "customer_id": "customer_count"
    }, inplace=True)
    return cust_by_state_df

def seller_by_city(df):
    seller_by_city_df = order_df.groupby(by="seller_city").seller_id.nunique().reset_index()
    seller_by_city_df.rename(columns={
        "seller_id": "seller_count"
    }, inplace=True)
    return seller_by_city_df

def seller_by_state(df):
    seller_by_state_df = order_df.groupby(by="seller_state").seller_id.nunique().reset_index()
    seller_by_state_df.rename(columns={
        "seller_id": "seller_count"
    }, inplace=True)
    return seller_by_state_df

def rfm_analysis(df):
    rfm_df = order_df.groupby(by="customer_id", as_index=False).agg({
    "order_purchase_timestamp": "max", #mengambil tanggal order terakhir
    "order_id": "nunique",
    "price": "sum"
    })
    rfm_df.columns = ["customer_id", "max_order_timestamp", "frequency", "monetary"]
    
    # menghitung kapan terakhir pelanggan melakukan transaksi (hari)
    rfm_df["max_order_timestamp"] = rfm_df["max_order_timestamp"].dt.date
    recent_date = df["order_purchase_timestamp"].dt.date.max()
    rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(lambda x: (recent_date - x).days)
    rfm_df.drop("max_order_timestamp", axis=1, inplace=True)

    return rfm_df

#import data
order_df = pd.read_csv("order_data.csv")
datetime_columns = ["order_approved_at", "order_delivered_carrier_date", "order_delivered_customer_date", "order_estimated_delivery_date", "order_purchase_timestamp", "shipping_limit_date"]
order_df.sort_values(by="order_purchase_timestamp", inplace=True)
order_df.reset_index(inplace=True)

for column in datetime_columns:
    order_df[column] = pd.to_datetime(order_df[column])


#untuk filter
min_date = order_df["order_purchase_timestamp"].min()
max_date = order_df["order_purchase_timestamp"].max()

with st.sidebar:
    # Menambahkan logo perusahaan
    st.image("https://upload.wikimedia.org/wikipedia/commons/a/a9/Amazon_logo.svg")
    
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Range Time',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = order_df[(order_df['order_purchase_timestamp'] >= str(start_date)) & (order_df['order_purchase_timestamp'] <= str(end_date))]

#st.dataframe(main_df)

#Menyiapkan dataframe
monthly_orders_df = create_monthly_orders_df(main_df)
sum_order_items_df = create_sum_order_item(main_df)
cust_by_city_df = cust_by_city(main_df)
cust_by_state_df = cust_by_state(main_df)
seller_by_city_df = seller_by_city(main_df)
seller_by_state_df = seller_by_state(main_df)
rfm_df = rfm_analysis(main_df)


# Layout website

# Membuat header
st.header('E-Commerce Orders Dahsboard')

#membuat grafik revenue
st.subheader('Company Revenue')
col1, col2 = st.columns(2)

with col1:
    total_orders = monthly_orders_df.order_count.sum()
    st.metric("Total orders", value=total_orders)

# with col2:
total_revenue = monthly_orders_df.total_revenue.sum()
st.metric("Total Revenue (in R$)", value=total_revenue)

fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    monthly_orders_df["order_purchase_timestamp"],
    monthly_orders_df["order_count"],
    marker='o', 
    linewidth=2,
    color="#72BCD4"
)
# ax.xticks(rotation=45, ha='right')
ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right") 
ax.tick_params(axis='y', labelsize=25)
ax.tick_params(axis='x', labelsize=20)

st.pyplot(fig)


#Membuat grafik penjualan produk

st.subheader("Best and Worst Selling Products")
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(48, 12))

colors = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

sns.barplot(x="order_item_id", y="product_category_name", data=sum_order_items_df.head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("Best Performing Product", loc="center", fontsize=18)
ax[0].tick_params(axis ='y', labelsize=30)

sns.barplot(x="order_item_id", y="product_category_name", data=sum_order_items_df.sort_values(by="order_item_id", ascending=True).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Worst Performing Product", loc="center", fontsize=18)
ax[1].tick_params(axis='y', labelsize=30)

st.pyplot(fig)

# Membuat grafik persebaran pelanggan

st.subheader("Customer Distribution by City and States")

col1, col2 = st.columns(2)

with col1:
    fig, ax = plt.subplots(figsize=(30, 15))
    colors_ = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
    sns.barplot(
        x="customer_count", 
        y="customer_city",
        data=cust_by_city_df.sort_values(by="customer_count", ascending=False).head(5),
        palette=colors_
    )
    ax.set_title("Number of Customer by City", loc="center", fontsize=15)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.tick_params(axis='x', labelsize=35)
    ax.tick_params(axis='y', labelsize=35)
    st.pyplot(fig)

with col2:
    fig, ax = plt.subplots(figsize=(30, 15))
    colors_ = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
     
    sns.barplot(
        x="customer_count", 
        y="customer_state",
        data=cust_by_state_df.sort_values(by="customer_count", ascending=False).head(5),
        palette=colors_
    )
    ax.set_title("Number of Customer by Seller", loc="center", fontsize=15)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.tick_params(axis='x', labelsize=35)
    ax.tick_params(axis='y', labelsize=35)
    st.pyplot(fig)

# Membuat grafik persebaran penjual

st.subheader("Seller Distribution by City and States")

col1, col2 = st.columns(2)

with col1:
    fig, ax = plt.subplots(figsize=(30, 15))
    colors_ = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
    sns.barplot(
        x="seller_count", 
        y="seller_city",
        data=seller_by_city_df.sort_values(by="seller_count", ascending=False).head(5),
        palette=colors_
    )
    ax.set_title("Number of Seller by City", loc="center", fontsize=15)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.tick_params(axis='x', labelsize=35)
    ax.tick_params(axis='y', labelsize=35)
    st.pyplot(fig)

with col2:
    fig, ax = plt.subplots(figsize=(30, 15))
    colors_ = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
    sns.barplot(
        x="seller_count", 
        y="seller_state",
        data=seller_by_state_df.sort_values(by="seller_count", ascending=False).head(5),
        palette=colors_
    )
    ax.set_title("Number of Seller by State", loc="center", fontsize=15)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.tick_params(axis='y', labelsize=35)
    st.pyplot(fig)

# Membuat grafik persebaran penjual

st.subheader("Customer RFM (Recency Frequency Monetary) Analysis")
col1, col2, col3 = st.columns(3)

with col1:
    avg_recency = round(rfm_df.recency.mean(), 1)
    st.metric("Average Recency (days)", value=avg_recency)

with col2:
    avg_frequency = round(rfm_df.frequency.mean(), 2)
    st.metric("Average Frequency", value=avg_frequency)

with col3:
    avg_frequency = rfm_df.monetary.mean()
    st.metric("Average Monetary (in R$)", value=avg_frequency)


st.caption('Created by: Annisa Mufidatun')