import requests
from bs4 import BeautifulSoup
import networkx as nx
import matplotlib.pyplot as plt
import math
import csv

G = nx.Graph()

url_mapping = {}  # Dictionary to store the mapping between numbers and href links
current_index = 1  # Starting index for numbering

visited = set()  # Set to store visited URLs

def extract_url(url, depth=0, max_depth=3):
    global current_index

    try:
        if url not in url_mapping:
            url_mapping[url] = current_index
            current_index += 1

        G.add_node(url_mapping[url])  # Add the initial URL to the graph
        html = requests.get(url).text
        soup = BeautifulSoup(html, "html.parser")
        links = soup.find_all('a')

        visited.add(url)  # Mark the current URL as visited

        for link in links:
            href = link.get('href')
            if href:
                if href not in url_mapping:
                    url_mapping[href] = current_index
                    current_index += 1
                G.add_edge(url_mapping[url], url_mapping[href])  # Add edge between initial URL and linked URL
                if depth < max_depth - 1 and href not in visited:  
                    G.add_node(url_mapping[href])  # Add node only if it's connected to something
                    extract_url(href, depth + 1, max_depth)

    except Exception as e:
        # print(f"Error extracting links from {url}: {e}")
        pass

# Dijkstra's algorithm to compute shortest paths
def dijkstra(graph, source):
    # Initialize distances to all nodes as infinity except for the source node
    distances = {node: math.inf for node in graph.nodes}
    distances[source] = 0

    # Initialize a set of visited nodes
    visited = set()

    while len(visited) < len(graph.nodes):
        # Find the node with the minimum distance
        min_node = min((node for node in graph.nodes if node not in visited), key=lambda x: distances[x])

        # Mark the node as visited
        visited.add(min_node)

        # Update distances to its neighbors
        for neighbor in graph.neighbors(min_node):
            new_distance = distances[min_node] + 1  # Assuming all edges have weight 1
            if new_distance < distances[neighbor]:
                distances[neighbor] = new_distance

    return distances

# Prompt user to input the max depth
max_depth = int(input("Enter the maximum depth: "))

# Read URLs from a text file
file_path = input("Enter the path to the text file containing URLs: ")
with open(file_path, 'r') as file:
    Web_Crawl_Urls = file.readlines()

# Remove trailing newline characters
Web_Crawl_Urls = [url.strip() for url in Web_Crawl_Urls]


#parse lists of URLS
for url in Web_Crawl_Urls:
    extract_url(url, max_depth=max_depth)  # set max_depth


# Compute shortest paths from a source node
source_node = 1  # Assuming the source node is the first node
shortest_paths = dijkstra(G, source_node)

# Printing and saving closeness of each node to a CSV file
with open('node_closeness.csv', 'w', newline='') as csvfile:
    fieldnames = ['Node', 'Closeness']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for node, distance in shortest_paths.items():
        if distance != 0:  # Exclude nodes with distance 0
            closeness = 1 / distance  # Calculate closeness
            writer.writerow({'Node': node, 'Closeness': closeness})
            print(f"Node {node} closeness: {closeness}")

        
# Printing and saving the URL mapping to a CSV file
with open('url_mapping.csv', 'w', newline='') as csvfile:
    fieldnames = ['Number', 'URL']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for url, number in url_mapping.items():
        writer.writerow({'Number': number, 'URL': url})

# Find the most central node
most_central_node = max(shortest_paths, key=lambda x: shortest_paths[x])

# Print the most central node
print(f"The most central node is: {most_central_node}")

# Plotting the graph
nx.draw(G, with_labels=True, node_color="red", node_size=100, font_weight="bold", font_size=5)

plt.show()