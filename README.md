# COMP3610_Assignment-1
Big Data Analytics Assignment one deliverables
Student: Shania Siew - 816039282

Project Overview

This project analyzes the NYC Yellow Taxi January 2024 dataset to discover patterns in taxi usage, passenger behavior, and trip characteristics.
The workflow is as follows:

1.Data loading, cleaning and validation
2. SQL analytical queries
3.Exploratory visualizations
4. Interactive dashboard deployment using Streamlit

Dataset: NYC TLC Trip Record Data (January 2024 Yellow Taxi)

Analytical Questions:
Which pickup zones are busiest
How fares vary throughout the day
Typical taxi trip distances
Payment behavior of passengers
Weekly travel demand patterns

The Streamlit dashboard includes:

Filters:
Date range selector
Hour range slider (0–23)
Payment type selector

Key Metrics: 
Total Trips
Average Fare
Total Revenue
Average Distance
Average Duration

Visualizations:
Top pickup zones by trip count
Average fare by hour of day
Distribution of trip distances
Payment type breakdown
Weekly demand heatmap (day vs hour)

Technologies Used:
Python
Pandas
DuckDB
SQL
Plotly
Streamlit

How to Run the Project
1. Clone the Repository
git clone <repo link>
cd <repo folder>
2. Install Dependencies
pip install -r requirements.txt
3. Run Dashboard
streamlit run app.py

The dashboard will open automatically in your browser.
