%%writefile food_wastemanagement.py
import streamlit as st
import pandas as pd
import sqlite3
import psycopg2
from psycopg2.extras import RealDictCursor


conn = psycopg2.connect(
host="localhost",
database="food_data",
user="postgres",
password="142789"
)
cursor = conn.cursor(cursor_factory=RealDictCursor)
st.title("🍱 Local Food Wastage Management System (PostgreSQL)")

tab1, tab2, tab3, tab4 = st.tabs(["Dashboard", "Food Listings", "Make a Claim", "Admin Panel"])

with tab1:
    st.header("📊 Dashboard & SQL Analysis")
    cursor.execute("SELECT city, COUNT(*) AS total_providers FROM providers_data GROUP BY city")
    data = cursor.fetchall()
    df = pd.DataFrame(data)
    st.dataframe(df)

with tab2:
    st.header("📦 Available Food Listings")
    cursor.execute('SELECT * FROM food_listing_data WHERE "Quantity " > 0')
    listings = cursor.fetchall()
    df_listings = pd.DataFrame(listings)
    st.dataframe(df_listings)

with tab3:
    st.header("🤝 Claim Food")
    food_id = st.number_input("Enter Food ID", min_value=1)
    receiver_id = st.number_input("Enter Receiver ID", min_value=1)
if st.button("Submit Claim"):
    cursor.execute("""INSERT INTO claim_data(food_id, recivier_id , Status)VALUES (%s, %s, 'Pending')""", (food_id, receiver_id))
    conn.commit()
    st.success("Claim submitted successfully!")

with tab4:
    st.header(⚙️ Admin Panel (CRUD)")

with st.form("add_food"):
    food_name = st.text_input("Food Name")
    quantity = st.number_input("Quantity", min_value=1)
    expiry = st.date_input("Expiry Date")
    provider_id = st.number_input("Provider ID", min_value=1)
    provider_type = st.selectbox("Provider Type", ["Restaurant", "Grocery Store", "Supermarket"])
    location = st.text_input("City")
    food_type = st.selectbox("Food Type", ["Vegetarian", "Non-Vegetarian", "Vegan"])
    meal_type = st.selectbox("Meal Type", ["Breakfast", "Lunch", "Dinner", "Snacks"])

    submit = st.form_submit_button("Add Food")
    if submit:
        cursor.execute("""
            INSERT INTO Food_Listings
            (Food_Name, Quantity, Expiry_Date, Provider_ID, Provider_Type, Location, Food_Type, Meal_Type)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (food_name, quantity, expiry, provider_id, provider_type, location, food_type, meal_type))
        conn.commit()
        st.success("Food item added!")

import psycopg2

try:
    conn = psycopg2.connect("food_data")  # your DB credentials
    cursor = conn.cursor()

    # your query
    cursor.execute("SELECT * FROM your_table")
    results = cursor.fetchall()

    # do something with results

except Exception as e:
    print(f"Error: {e}")

finally:
    if cursor and not cursor.closed:
        cursor.close()
    if conn:
        conn.close()
