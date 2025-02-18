import requests
import base64
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np

# 
CLIENT_ID = "d6439164eb6746c8ac5bb20a2f708fe4"
CLIENT_SECRET = "6c209eabbd824444aed24feec03b7766"
ARTIST_NAME = "Taylor Swift"

# Function to get a Spotify API token
def get_access_token():
    auth_url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode(),
    }
    data = {"grant_type": "client_credentials"}
    
    response = requests.post(auth_url, headers=headers, data=data)
    token = response.json().get("access_token")
    
    return token

ACCESS_TOKEN = get_access_token()

# Function to get an artist's Spotify ID
def get_artist_id(artist_name):
    url = "https://api.spotify.com/v1/search"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    params = {"q": artist_name, "type": "artist", "limit": 1}
    
    response = requests.get(url, headers=headers, params=params)
    data = response.json()
    
    try:
        artist_id = data["artists"]["items"][0]["id"]
        return artist_id
    except (IndexError, KeyError):
        return None

# Function to get an artist's featured collaborators, with track popularity
def get_featured_artists(artist_id):
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    params = {"market": "US"}
    
    response = requests.get(url, headers=headers, params=params)
    data = response.json()

    collaborations = {}
    for track in data.get("tracks", []):
        for artist in track["artists"]:
            if artist["id"] != artist_id:  
                collab_name = artist["name"]
                popularity = track["popularity"]  
                current_count, current_popularity = collaborations.get(collab_name, (0, 0))  # Get current values or defaults

                # Update the collaboration count and store the maximum popularity
                collaborations[collab_name] = (current_count + 1, max(current_popularity, popularity))

    return collaborations  

from collections import deque

G = nx.Graph()

def bfs_collaboration_network(start_artist_name, depth):
    queue = deque([(start_artist_name, 0)])  
    visited = set()

    while queue:
        artist_name, level = queue.popleft()
        if artist_name in visited or level > depth:
            continue

        artist_id = get_artist_id(artist_name)
        if not artist_id:
            continue

        G.add_node(artist_name)  
        collaborators = get_featured_artists(artist_id)

        for collab_name, (collab_count, popularity) in collaborators.items():
            if collab_name not in visited:
                queue.append((collab_name, level + 1))

            # Add edge with weight (number of collaborations) and track popularity
            if G.has_edge(artist_name, collab_name):
                # Update edge weight and popularity if it already exists
                G[artist_name][collab_name]["weight"] += collab_count
                G[artist_name][collab_name]["popularity"] = max(G[artist_name][collab_name].get("popularity", 0), popularity)
            else:
                G.add_edge(artist_name, collab_name, weight=collab_count, popularity=popularity)

        visited.add(artist_name)

bfs_collaboration_network(ARTIST_NAME, depth=3)


edge_popularity = [G[u][v]["popularity"] for u, v in G.edges()]

# Normalize edge popularity for color mapping
max_popularity = max(edge_popularity) if edge_popularity else 1  # Prevent division by zero
edge_colors = [plt.cm.Greys(pop / max_popularity) for pop in edge_popularity]  # Use a color map (viridis for popularity)

for artist_name in G.nodes():
    print(f"Artist: {artist_name}")
    
    # Get the collaborators for the current artist
    for neighbor in G.neighbors(artist_name):
        # Get the popularity of the collaboration (edge attribute)
        edge_data = G[artist_name][neighbor]
        collaboration_popularity = edge_data.get("popularity", "No popularity data")
        
        # Print the collaborator and the popularity of their collaboration
        print(f"  Collaboration with: {neighbor}, Popularity: {collaboration_popularity}")
    
    print("\n")  
# Plot the graph
plt.figure(figsize=(12, 8))

pos = nx.spring_layout(G, seed=42)  # Positioning algorithm for layout

# Plot with edge color adjusted for popularity
nx.draw(G, 
        pos,
        with_labels=True, 
        node_size=450,  
        font_size=5, 
        font_color="white", 
        edge_color=edge_colors,  # Use the color map based on popularity
        node_color="blue",
        width=[w["weight"] / max_popularity * 7 for u, v, w in G.edges(data=True)]  # Scale edge width by weight (collaborations)
       )

plt.title("Spotify Collaboration Network with Track Popularity")
plt.show()

