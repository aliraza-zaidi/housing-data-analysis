import streamlit as st
import pandas as pd
import plotly.express as px 
import plotly.graph_objects as go

def load_data():
    data = pd.read_csv('cleaned.csv')    
    return data

months = {"January":1, "February":2, "March":3, "April":4, "May":5, "June":6, "July":7, "August":8, "September":9, "October":10, "November":11, "December":12}

st.set_page_config(
    page_title="Pakistan Housing Data Analysis",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title('Pakistan Housing Data Analysis 🏠')
st.write("Delve into the Pakistan Real Estate Market Trends with data-driven analysis")

st.sidebar.header("Explore Analysis")
options = [
    "Overview",
    "Listings by Month",
    "Listings by Purpose",
    "Listings by City",
    "Top Locations",
    "Price by Purpose",
    "Price by City",
    "Hot Locations",
    "Price Trend Over Time"
]
selected_option = st.sidebar.radio("Choose an analysis:", options)

data = load_data()

sale = data.loc[data['purpose']=='For Sale', :]
location_counts = sale['location'].value_counts()
locations_to_keep = location_counts[location_counts > 1].index
sale = sale[sale['location'].isin(locations_to_keep)]

if selected_option == "Overview":
    st.header = "Overview: "
    a, b = st.columns(2)
    c, d = st.columns(2)

    a.metric("Total Listings 📋", data.size, delta=None, border=True)
    b.metric("Total Property Types 🏘️", len(data['property_type'].unique()),border=True)

    c.metric("Total Cities 🏙️", len(data['city'].unique()), border=True)
    d.metric("Total Locations 📍", len(data['location'].unique()), border=True)

    lat_min, lat_max = 23.42, 37.06
    long_min, long_max = 60.50, 77.50

    filtered_locs = data[
            (data['latitude'] >= lat_min) & (data['latitude'] <= lat_max) &
            (data['longitude'] >= long_min) & (data['longitude'] <= long_max)
        ]
    fig = px.scatter_geo(filtered_locs.sample(frac=0.0001), lat='latitude', lon='longitude', hover_name='city', title='Locations Across Pakistan',center={'lat': 30, 'lon': 70}, template='ggplot2')
    fig.update_layout(geo_scope='asia',height=600,width=800)
    st.plotly_chart(fig)

elif selected_option=="Listings by Month":
    st.header = "Listings by Month of the Year"
    selected_month = st.selectbox("Select a month:", options=["All"] + list(months.keys()))

    if selected_month != "All":        
        listings_by_month = data.loc[data["listing_month"]==months[selected_month],:].groupby('property_type').size().reset_index(name='listings')   
        fig = px.pie(listings_by_month, values='listings', names='property_type', title=f'Listings in {selected_month}', template='ggplot2')
        st.plotly_chart(fig)
    else:
        listings_by_month = data.groupby('listing_month').size().reset_index(name='listings')
        fig = px.line(listings_by_month, x='listing_month', y="listings", template='ggplot2')
        fig.update_layout(title='Trends of Listings Across Months', xaxis_title='Month', yaxis_title='Listings',xaxis=dict(tickmode='array',tickvals=listings_by_month['listing_month'],ticktext=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']  # Custom labels
    ))
        st.plotly_chart(fig)

elif selected_option == "Listings by Purpose":
    st.header = "Listings by Purpose (Sale/Rental)"
    selected_purpose = st.radio("Select a purpose:", options=["Both", "Sale", "Rent"], horizontal=True)
    
    if selected_purpose == "Both":        
        listings_by_purpose = data.groupby('purpose').size().reset_index(name='listings')
        fig = px.bar(listings_by_purpose, x='purpose', y='listings', template='ggplot2')
        fig.update_layout(title='Listings by Purpose', width=700, height=600, bargap=0.4)
        st.plotly_chart(fig)
    else:
        listings_by_purpose = data.loc[data['purpose']=="For "+ selected_purpose,:].groupby('property_type').size().reset_index(name='listings')        
        fig = px.pie(listings_by_purpose, values='listings', names='property_type', title=f'Listings for {selected_purpose}',template='ggplot2')        
        st.plotly_chart(fig)

elif selected_option == "Listings by City":
    st.header = "Listings by City"
    on = st.toggle("See Trend")

    if on:
        property_type_by_city = data.groupby(['city','property_type']).size().unstack()
        fig = px.imshow(property_type_by_city, template='ggplot2')
        fig.update_layout(title='Trend of Property Type Across Cities',height=600, width=700, xaxis_title=None, yaxis_title=None, template='seaborn')
        st.plotly_chart(fig)

    else:
        listings_by_city = data['city'].value_counts().reset_index(name='listings')
        fig = px.bar(listings_by_city, x='city', y='listings', template='ggplot2')
        fig.update_layout(title='Listings by City', xaxis_title='City',yaxis_title='Listings',width=700, height=600, bargap=0.3)
        st.plotly_chart(fig)

elif selected_option == "Top Locations":
    st.header = "Top Locations in Pakistan (By Number of Listings)"
    selected_city = st.selectbox("Select a city:", options=["All"] + sorted(data['city'].unique().tolist()))

    if selected_city != "All":
        city_sub = data.loc[data['city']==selected_city, :].groupby(['location']).size().reset_index(name='listings')
        top_10 = city_sub.sort_values(by='listings', ascending=False).head(10)
            
        fig = go.Figure()
        fig.add_trace(go.Scatter(y=top_10['location'], x=top_10['listings'],
                            mode='markers', name='Value'))
        fig.add_trace(go.Bar(y=top_10['location'], x=top_10['listings'],
                        orientation='h', name='Bar', marker=dict(opacity=0.6),width=0.3))
        fig.update_layout(title=f'Top 10 Most Popular Locations in {selected_city}', xaxis_title='Listings', yaxis_title='Locations', height=500)
        st.plotly_chart(fig)
    else:
        top_10_pak = data.groupby('location').size().reset_index(name='listings').sort_values(by='listings', ascending=False).head(10)
        fig = go.Figure()
        fig.add_trace(go.Scatter(y=top_10_pak['location'], x=top_10_pak['listings'],
                            mode='markers', name='Value'))
        fig.add_trace(go.Bar(y=top_10_pak['location'], x=top_10_pak['listings'],
                        orientation='h', name='Bar', marker=dict(opacity=0.6),width=0.3))
        fig.update_layout(title='Top 10 Most Popular Locations Across Pakistan', xaxis_title='Listings', yaxis_title='Locations', height=500)
        st.plotly_chart(fig)

        

elif selected_option == "Price by Purpose":
    st.header = "Price Analysis by Purpose (Sale/Rental)"
    selected_purpose = st.radio("Select a purpose:", options=["Sale", "Rent"], horizontal=True)

    data_sub = data.loc[data['purpose'] == "For "+ selected_purpose, :]
    price_vs_beds = data_sub.groupby(['property_type', 'bedrooms'])['price'].mean().reset_index()
    fig = px.scatter(
            price_vs_beds,
            x='bedrooms',
            y='price',
            color='property_type',        
            title=f'Average Property Price ({selected_purpose}) by Number of Beds and Property Type',
            labels={'beds': 'Number of Beds', 'price': 'Average Price'}
            , template='ggplot2'
        )
    fig.update_layout(
            xaxis_title='Number of Beds',
            yaxis_title='Average Price',
            legend_title='Property Type', 
            height = 700,
            width = 800
        )
    st.plotly_chart(fig)

elif selected_option == "Price by City":
    st.header = "Price Analysis by City"
    
    purpose = st.selectbox("Choose Purpose: ", options=['For Sale', 'For Rent'])
    type = st.selectbox("Choose Property Type: ", options=data['property_type'].unique().tolist())

    filtered = data.loc[(data['purpose']==purpose) & (data['property_type']==type), :]

    city_wise = filtered.groupby(['bedrooms', 'city'])['price'].mean().reset_index(name='average_price')

    fig = px.line(
            city_wise,
            x='bedrooms',
            y='average_price',
            color='city',
            markers=True,
            title=f'Average {type} {purpose} Price by City',
            labels={'beds': 'Number of Beds', 'price': 'Average Price'}
            , template='ggplot2'
        )
    fig.update_layout(
            xaxis_title='Number of Beds',
            yaxis_title='Average Price',
            legend_title='City', 
            height = 700,
            width = 800
        )
    st.plotly_chart(fig)

elif selected_option == "Hot Locations":
    st.header = "Hot Locations in Pakistan (By Average Property Sale Price)"

    on = st.toggle("View Top 10")


    avg = sale.groupby(['location', 'city'])['price'].mean().reset_index(name='average_price')    

    if on:
        city = st.selectbox("Choose a city: ", options=avg['city'].unique())
        city_sub = avg.loc[avg['city']==city, :]
        top_10 = city_sub.sort_values(by='average_price', ascending=False).head(10)
        fig = go.Figure()
        fig.add_trace(go.Scatter(y=top_10['location'], x=top_10['average_price'],
                                mode='markers', name='Value'))
        fig.add_trace(go.Bar(y=top_10['location'], x=top_10['average_price'],
                            orientation='h', name='Bar', marker=dict(opacity=0.6),width=0.3))
        fig.update_layout(title=f'Top 10 Most Expensive Locations in {city}', xaxis_title='Average', yaxis_title='Locations', height=500)
        st.plotly_chart(fig)
    else:
        fig = px.treemap(avg, 
        path=['city', 'location'], 
        values='average_price',
        color='average_price', 
        title='Average Property Price by Location and City'
        , template='ggplot2'
        )
        fig.update_layout(            
                height = 900,
                width = 1200
            )
        
        st.plotly_chart(fig)
    
elif selected_option == "Price Trend Over Time":
    st.header = "Trend in Property Prices Across Months"

    purpose = st.selectbox("Choose Purpose: ", options=['For Sale', 'For Rent'])
    type = st.selectbox("Choose Property Type: ", options=data['property_type'].unique().tolist())

    filtered = data.loc[(data['purpose']==purpose) & (data['property_type']==type), :]
    beds = st.selectbox("Choose Number of Beds: ", options=sorted(filtered['bedrooms'].unique().tolist()))
    filtered = data.loc[(data['bedrooms']==beds), :]
    month_wise = filtered.groupby('listing_month')['price'].mean().reset_index(name='average_price')

    fig = px.line(month_wise, x='listing_month', y="average_price", template='ggplot2')
    fig.update_layout(
        xaxis_title='Month',
        yaxis_title='Average Price',
        xaxis=dict(
            tickmode='array',
            tickvals=month_wise['listing_month'],
            ticktext=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        )
    )
    st.plotly_chart(fig)