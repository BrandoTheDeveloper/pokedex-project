import requests
import mysql.connector
import time

# -------------------------------
# Connect to MySQL
# -------------------------------
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="password",
    database="pokedex"
)
mycursor = mydb.cursor()

# -------------------------------
# Get total number of Pokémon dynamically
# -------------------------------
response = requests.get("https://pokeapi.co/api/v2/pokemon?limit=1")
total_pokemon = response.json()['count']  # currently 1025
print(f"Total Pokémon available: {total_pokemon}")

# -------------------------------
# Loop through all Pokémon IDs
# -------------------------------
for id in range(1, total_pokemon + 1):

    # --- Build API URLs ---
    url = f"https://pokeapi.co/api/v2/pokemon/{id}/"
    url2 = f"https://pokeapi.co/api/v2/pokemon-species/{id}/"

    # --- Fetch Pokémon base data (stats, types, sprites) ---
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"Skipping Pokémon {id} due to error fetching base data: {e}")
        continue

    # --- Fetch species data (genus, description) ---
    try:
        response2 = requests.get(url2, timeout=10)
        response2.raise_for_status()
        data2 = response2.json()
    except Exception as e:
        print(f"Skipping Pokémon {id} due to error fetching species data: {e}")
        continue

    # -------------------------------
    # Extract fields
    # -------------------------------
    pokemon_id = data['id']
    pokemon_name = data['name']

    # Genus (species field) — filter for English entry
    pokemon_species = next(
        (entry['genus'] for entry in data2['genera'] if entry['language']['name'] == 'en'),
        "Unknown"
    )

    # Types (handle single-type Pokémon safely)
    types_list = data['types']
    pokemon_type1 = types_list[0]['type']['name']
    pokemon_type2 = types_list[1]['type']['name'] if len(types_list) >= 2 else "N/A"

    # Stats
    pokemon_hp = data['stats'][0]['base_stat']
    pokemon_attack = data['stats'][1]['base_stat']
    pokemon_defense = data['stats'][2]['base_stat']
    pokemon_speed = data['stats'][5]['base_stat']

    # Description (first English flavor text)
    pokemon_description = next(
        (entry['flavor_text'].replace("\n", " ").replace("\f", " ")
         for entry in data2['flavor_text_entries']
         if entry['language']['name'] == 'en'),
        "No description available"
    )

    # Sprite (official artwork URL)
    pokemon_sprite = data['sprites']['other']['official-artwork']['front_default']

    # -------------------------------
    # Insert or update row in MySQL
    # -------------------------------
    sql = """INSERT INTO pokemon 
                (id, name, species, type1, type2, hp, attack, defense, speed, description, sprite) 
             VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
             ON DUPLICATE KEY UPDATE 
                species = VALUES(species),
                name = VALUES(name),
                type1 = VALUES(type1),
                type2 = VALUES(type2),
                hp = VALUES(hp),
                attack = VALUES(attack),
                defense = VALUES(defense),
                speed = VALUES(speed),
                description = VALUES(description),
                sprite = VALUES(sprite);"""

    val = (pokemon_id, pokemon_name, pokemon_species, pokemon_type1, pokemon_type2,
           pokemon_hp, pokemon_attack, pokemon_defense, pokemon_speed, pokemon_description, pokemon_sprite)

    try:
        mycursor.execute(sql, val)
        print(f"Inserted/Updated {pokemon_name} (ID: {pokemon_id}) successfully! ({id}/{total_pokemon})")
    except Exception as e:
        print(f"Failed to insert {pokemon_name} (ID: {pokemon_id}): {e}")

    # Optional: sleep to avoid hammering the API too fast
    time.sleep(0.2)

# -------------------------------
# Commit all changes once at the end
# -------------------------------
mydb.commit()

# -------------------------------
# Close connection
# -------------------------------
mycursor.close()
mydb.close()