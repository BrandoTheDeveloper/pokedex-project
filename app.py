import streamlit as st
import mysql.connector
import os
from dotenv import load_dotenv

# -------------------------------
# Load environment variables
# -------------------------------
load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")


# -------------------------------
# Connect to MySQL
# -------------------------------
def get_pokemon():
    mydb = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
    cursor = mydb.cursor(dictionary=True)
    cursor.execute("SELECT * FROM pokemon ORDER BY id")
    results = cursor.fetchall()
    cursor.close()
    mydb.close()
    return results

# -------------------------------
# Streamlit UI
# -------------------------------
st.set_page_config(page_title="Pokédex", layout="wide")
st.title("Pokédex Viewer")

# Fetch Pokémon data
pokemons = get_pokemon()

# Sidebar filter
search_name = st.sidebar.text_input("Search Pokémon by name")
type_filter = st.sidebar.selectbox("Filter by Type", ["All"] + sorted(set([p["type1"] for p in pokemons])))

# Apply filters
filtered = [
    p for p in pokemons
    if (search_name.lower() in p["name"].lower()) and
       (type_filter == "All" or p["type1"] == type_filter or p["type2"] == type_filter)
]

# Display Pokémon cards
cols = st.columns(4)  # 4 Pokémon per row
for i, p in enumerate(filtered):
    with cols[i % 4]:
        st.image(p["sprite"], width=120)
        st.subheader(p["name"].title())
        st.caption(p["species"])
        st.text(f"Types: {p['type1']} / {p['type2']}")
        st.text(f"HP: {p['hp']} | ATK: {p['attack']} | DEF: {p['defense']} | SPD: {p['speed']}")