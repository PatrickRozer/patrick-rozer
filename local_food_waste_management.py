%%writefile local_food_waste_management.py
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
import psycopg2
from psycopg2.extras import RealDictCursor

# Database connection string - use your credentials/environment variables
DB_USER = 'postgres'
DB_PASS = '142789'
DB_HOST = 'localhost'
DB_PORT = '5432'
DB_NAME = 'food_waste_management_db'

@st.cache_resource
def get_engine():
    return create_engine(f'postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}')

engine = get_engine()

st.sidebar.title("Local Food Wastage Management System")
page = st.sidebar.selectbox("Choose a page", ["Home", "Food Listings", "Claims", "Providers", "Receivers", "Analytics", "Add Food", "Add Claim"])

if page == "Home":
    st.title("Welcome to the Local Food Wastage Management System")
    st.write("""This app helps connect surplus food providers to those in need, reducing local food waste. Use the menu to explore listings, claims, analytics, and more.""")

if page == "Food Listings":
    st.header("Available Food Listings")

    # Get filter options from DB
    cities = pd.read_sql('SELECT DISTINCT "Location" FROM "Food_Listing_db" ORDER BY "Location"', engine)["Location"].tolist()
    providers = pd.read_sql('SELECT DISTINCT "Name" FROM "Providers_db" ORDER BY "Name"', engine)["Name"].tolist()
    food_types = pd.read_sql('SELECT DISTINCT "Food_Type" FROM "Food_Listing_db" ORDER BY "Food_Type"', engine)["Food_Type"].tolist()
    meal_types = pd.read_sql('SELECT DISTINCT "Meal_Type" FROM "Food_Listing_db" ORDER BY "Meal_Type"', engine)["Meal_Type"].tolist()

    # Filter widgets
    city_filter = st.multiselect("Filter by City", options=cities)
    provider_filter = st.multiselect("Filter by Provider", options=providers)
    food_type_filter = st.multiselect("Filter by Food Type", options=food_types)
    meal_type_filter = st.multiselect("Filter by Meal Type", options=meal_types)

    # Build where clause dynamically
    where_clauses = []
    params = {}

    if city_filter:
        where_clauses.append("Location IN :city_filter")
        params["city_filter"] = tuple(city_filter)
    if provider_filter:
        where_clauses.append('"Provider_ID" IN (SELECT "Provider_ID" FROM "Providers_db" WHERE "Name" IN :provider_filter)')
        params["provider_filter"] = tuple(provider_filter)
    if food_type_filter:
        where_clauses.append('"Food_Type" IN :food_type_filter')
        params["food_type_filter"] = tuple(food_type_filter)
    if meal_type_filter:
        where_clauses.append('"Meal_Type" IN :meal_type_filter')
        params["meal_type_filter"] = tuple(meal_type_filter)

    where_sql = " AND ".join(where_clauses)
    if where_sql:
        query = text(f'SELECT * FROM "Food_Listing_db" WHERE {where_sql} ORDER BY "Expiry_Date" ASC')
    else:
        query = text('SELECT * FROM "Food_Listing_db" ORDER BY "Expiry_Date" ASC')

    df_food = pd.read_sql(query, engine, params=params)
    st.dataframe(df_food)

    if not df_food.empty:
        # Show contact info of providers
        st.subheader("Provider Contacts")
        selected_provider_ids = df_food["Provider_ID"].unique().tolist()
        provider_contacts = pd.read_sql(
            text('SELECT "Name", "City", "Contact" FROM "Providers_db" WHERE "Provider_ID" IN :ids'),
            engine,
            params={"ids": tuple(selected_provider_ids)}
        )
        st.dataframe(provider_contacts)

if page == "Claim_db":
    st.header("Food Claims")

    # Show all claims with food and receiver info
    claims_query = '''
    SELECT c."Claim_ID", f."Food_Name", r."Name" AS "Receiver_Name", c."Status", c."Timestamp"
    FROM "Claim_db" c
    JOIN "Food_Listing_db" f ON c."Food_ID" = f."Food_ID"
    JOIN "Receiver_db" r ON c."Receiver_ID" = r."Receiver_ID"
    ORDER BY c."Timestamp" DESC
    '''
    df_claims = pd.read_sql(claims_query, engine)
    st.dataframe(df_claims)

    st.subheader("Add New Claim")
    food_options = pd.read_sql('SELECT "Food_ID", "Food_Name" FROM "Food_Listing_db" WHERE "Expiry_Date" >= CURRENT_DATE', engine)
    receiver_options = pd.read_sql('SELECT "Receiver_ID", "Name" FROM "Receiver_db"', engine)

    selected_food = st.selectbox("Select Food Item", options=food_options["Food_ID"], format_func=lambda x: food_options[food_options["Food_ID"] == x]["Food_Name"].values[0])
    selected_receiver = st.selectbox("Select Receiver", options=receiver_options["Receiver_ID"], format_func=lambda x: receiver_options[receiver_options["Receiver_ID"] == x]["Name"].values[0])
    status = st.selectbox("Claim Status", options=['Pending', 'Completed', 'Cancelled'])

    if st.button("Add Claim"):
        from datetime import datetime
        insert_query = text('''
            INSERT INTO "Claim_db" ("Claim_ID", "Food_ID", "Receiver_ID", "Status", "Timestamp)
            VALUES (DEFAULT, :"Food_ID", :"Receiver_ID", :status, :"Timestamp")
        ''')
        with engine.begin() as conn:
            conn.execute(insert_query, {
                "Food_ID": selected_food,
                "Receiver_ID": selected_receiver,
                "Status": status,
                "Timestamp": datetime.now()
            })
        st.success("Claim added successfully!")

if page == "Providers":
    st.header("Food Providers")
    providers_df = pd.read_sql('SELECT * FROM "Providers_db" ORDER BY "City", "Name"', engine)
    st.dataframe(providers_df)

if page == "Receivers":
    st.header("Food Receivers")
    receivers_df = pd.read_sql('SELECT * FROM "Receiver_db" ORDER BY "City", "Name"', engine)
    st.dataframe(receivers_df)


if page == "Analytics":
    st.header("Food Wastage Analytics")

    st.subheader("Total Food Available by Provider Type")
    query = '''
        SELECT "Provider_Type", SUM("Quantity")AS total_quantity
        FROM "Food_Listing_db"
        GROUP BY "Provider_Type"
        ORDER BY total_quantity DESC
    '''
    df = pd.read_sql(query, engine)
    st.bar_chart(df.set_index("Provider_Type"))

    # Additional Analytics queries for demands, claims etc.
    st.subheader("Food Claims Status Distribution")
    query2 = '''
        SELECT "Status", COUNT(*) AS count
        FROM "Claim_db"
        GROUP BY "Status"
    '''
    df2 = pd.read_sql(query2, engine)
    st.bar_chart(df2.set_index("Status"))

    st.subheader("Top 5 Cities With Most Food Listings")
    query3 = '''
        SELECT "Location" AS "City", COUNT(*) AS food_listing_count
        FROM "Food_Listing_db"
        GROUP BY "Location"
        ORDER BY food_listing_count DESC
        LIMIT 5
    '''
    df3 = pd.read_sql(query3, engine)
    st.bar_chart(df3.set_index("City"))



if page == "Add Food":
    st.header("Add New Food Listing")

    food_name = st.text_input("Food_Name")
    quantity = st.number_input("Quantity", min_value=1)
    expiry_date = st.date_input("Expiry_Date")
    providers_df = pd.read_sql('SELECT "Provider_ID", "Name" FROM "Providers_db"', engine)
    selected_provider = st.selectbox("Select Provider", providers_df["Provider_ID"], format_func=lambda x: providers_df[providers_df["Provider_ID"] == x]["Name"].values[0])
    provider_type = pd.read_sql('SELECT type FROM "Providers_db" WHERE "Provider_ID" = pid', engine, params={"pid": selected_provider}).iloc[0,0]
    location = pd.read_sql('SELECT city FROM "Providers_db" WHERE "Provider_ID" =  pid', engine, params={"pid": selected_provider}).iloc[0,0]

    food_type = st.selectbox("Food_Type", ['Vegetarian', 'Non-Vegetarian', 'Vegan'])
    meal_type = st.selectbox("Meal_Type", ['Breakfast', 'Lunch', 'Dinner', 'Snacks'])

    if st.button("Add Food Listing"):
        insert_food_query = text('''
            INSERT INTO "Food_listings" ("Food_ID", "Food_Name", "Quanity", "Expiry_Date", "Provider_ID", "Provider_Type", "Location", "food_Type", "Meal_Type")
            VALUES (DEFAULT, :"Food_Name", :"quantity", :"Expiry_Date", :"Provider_ID", :"Provider_Type", :"Location", :"Food_Type, :"Meal_Type")
        ''')
        with engine.begin() as conn:
            conn.execute(insert_food_query, {
                "food_name": food_name,
                "quantity": quantity,
                "expiry_date": expiry_date,
                "provider_id": selected_provider,
                "provider_type": provider_type,
                "location": location,
                "food_type": food_type,
                "meal_type": meal_type
            })
        st.success(f"Food listing '{food_name}' added!")




