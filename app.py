import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")

@st.cache_data
def load_data():

    taxi_url = "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-01.parquet"
    zone_url = "https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv"

    df = pd.read_parquet(
        taxi_url,
        engine="pyarrow",
        columns=[
            "tpep_pickup_datetime",
            "tpep_dropoff_datetime",
            "trip_distance",
            "fare_amount",
            "total_amount",
            "payment_type",
            "PULocationID"
        ]
    )


    df = df.sample(150000, random_state=42)

    zones = pd.read_csv(zone_url)

    # Data cleaning
    df = df[df["trip_distance"] > 0]
    df = df[df["fare_amount"] > 0]

    df["tpep_pickup_datetime"] = pd.to_datetime(df["tpep_pickup_datetime"])
    df["tpep_dropoff_datetime"] = pd.to_datetime(df["tpep_dropoff_datetime"])

    df["pickup_hour"] = df["tpep_pickup_datetime"].dt.hour
    df["pickup_day_of_week"] = df["tpep_pickup_datetime"].dt.day_name()

    df["trip_duration_minutes"] = (
        df["tpep_dropoff_datetime"] - df["tpep_pickup_datetime"]
    ).dt.total_seconds() / 60

    df = df.merge(zones, left_on="PULocationID", right_on="LocationID", how="left")

    payment_map = {
        1: "Credit Card",
        2: "Cash",
        3: "No Charge",
        4: "Dispute"
    }
    df["payment_type"] = df["payment_type"].map(payment_map)

    return df


df = load_data()


st.title("NYC Taxi Trip Analytics Dashboard")
st.markdown("""
This dashboard explores patterns in NYC Yellow Taxi trips including high demand locations,fare patterns, and payment trends. 
The filters can be used to explore how time and payment method affect taxi trips. 
The insights can inform transportation planning, pricing strategies, and service improvements. 
""")


# Sidebar Filters
st.sidebar.header("Filters")

min_date = df["tpep_pickup_datetime"].dt.date.min()
max_date = df["tpep_pickup_datetime"].dt.date.max()

date_range = st.sidebar.date_input(
    "Date Range",
    [min_date, max_date],
    min_value=min_date,
    max_value=max_date
)

hour_range = st.sidebar.slider("Pickup Hour", 0, 23, (0, 23))

payment_types = st.sidebar.multiselect(
    "Payment Type",
    options=df["payment_type"].unique(),
    default=df["payment_type"].unique()
)

#Filter data
filtered_df = df[
    (df["tpep_pickup_datetime"].dt.date >= date_range[0]) &
    (df["tpep_pickup_datetime"].dt.date <= date_range[1]) &
    (df["pickup_hour"] >= hour_range[0]) &
    (df["pickup_hour"] <= hour_range[1]) &
    (df["payment_type"].isin(payment_types))
]


# Metrics

st.header("Key Metrics")

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("Total Trips", f"{len(filtered_df):,}")
col2.metric("Avg Fare", f"${filtered_df['fare_amount'].mean():.2f}")
col3.metric("Revenue", f"${filtered_df['total_amount'].sum():,.0f}")
col4.metric("Avg Distance", f"{filtered_df['trip_distance'].mean():.2f} mi")
col5.metric("Avg Duration", f"{filtered_df['trip_duration_minutes'].mean():.1f} min")


# Tabs for different analyses
tab1, tab2, tab3 = st.tabs(["Demand Patterns", "Fare Patterns", "Payments & Behavior"])


#Demand tab

with tab1:

    st.subheader("Top 10 Pickup Zones")

    zone_counts = (
        filtered_df.groupby("Zone")
        .size()
        .reset_index(name="trips")
        .sort_values("trips", ascending=False)
        .head(10)
    )

    fig1 = px.bar(zone_counts, x="trips", y="Zone", orientation="h")
    st.plotly_chart(fig1,  width="stretch")

    st.markdown("""
The majority of trips originate from high activity and urban areas such as Midtown, Upper East Side, and Financial District.
This indicates taxis are heavily relied upon for short travel rather than for long commuting routes. 
These demands are predictable based on the economic activity of these zones.
""")

    st.subheader("Trips by Day & Hour")

    heatmap_data = filtered_df.groupby(
        ["pickup_day_of_week", "pickup_hour"]
    ).size().reset_index(name="trips")

    fig5 = px.density_heatmap(
        heatmap_data,
        x="pickup_hour",
        y="pickup_day_of_week",
        z="trips",
        color_continuous_scale="blues"
    )

    st.plotly_chart(fig5,  width="stretch")

    st.markdown("""
Taxi demand peaks during evenings or on weekdays, reflecting typical commuting patterns and nightlife activity.
Demand is lowest in the early morning hours when fewer people are traveling, and roads are less congested. 
This pattern is consistent with taxis being used primarily for work commutes and social outings rather than late night transportation.
""")
    
    st.subheader("Trip Distance Distribution")

    distance_view = filtered_df[
    (filtered_df["trip_distance"] > 0.1) & 
    (filtered_df["trip_distance"] <= 30)]

    fig3 = px.histogram(
    distance_view,
    x="trip_distance",
    nbins=60,
    title="Distribution of Trip Distances (0.1–30 miles)")

    st.plotly_chart(fig3,  width="stretch")

    st.markdown("""
Most taxi rides are short distance trips, showing taxis are primarily used for local
transportation within neighborhoods rather than long distance and odd location travel. 
Long trips exist but represent a small minority of total rides.
""")

# Fare tab

with tab2:

    st.subheader("Average Fare by Hour")

    fare_hour = filtered_df.groupby("pickup_hour")["fare_amount"].mean().reset_index()

    fig2 = px.line(fare_hour, x="pickup_hour", y="fare_amount", markers=True)
    st.plotly_chart(fig2,  width="stretch")

    st.markdown("""
Higher fares appear during peak traffic periods when trips take longer due to congestion.
Late night fares stabilize because roads are clearer, allowing trips to complete faster
even over similar distances.
""")

    

# Payment tab

with tab3:

    st.subheader("Payment Type Breakdown")

    payment_counts = filtered_df["payment_type"].value_counts().reset_index()
    payment_counts.columns = ["payment_type", "count"]
    payment_counts = payment_counts.sort_values(by="count", ascending=False)

    fig4 = px.bar(payment_counts, x="payment_type", y="count")
    st.plotly_chart(fig4,  width="stretch")

    st.markdown("""
Electronic payments dominate taxi usage, indicating riders prefer speed and convenience
over handling cash. This trend also reflects broader societal shifts towards digital payments or how wide acceptance of credit cards to accomodate the large number of tourists and business travelers in NYC.
""")


