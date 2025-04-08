"""
This script visualizes the road network graph using Folium.
"""

from pathlib import Path
import logging

import pickle
import folium

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
GRAPH_FILE = Path("data/processed/road_network.pkl")
OUTPUT_HTML_MAP = Path("data/processed/interactive_road_network_map.html")
MAX_EDGE_NUM = 150000    # Maximum number of edges to visualize

def visualize_interactive_graph(graph_file: Path, output_html_map: Path):
    """
    Create an interactive map using Folium directly.
    Args:
        graph_file (Path): Path to the pickled graph file.
        output_html_map (Path): Path to save the interactive map.
    """
    with open(graph_file, "rb") as f:
        graph = pickle.load(f)
    center_malaysia = (3.139, 101.686)  # Latitude and Longitude for Kuala Lumpur
    folium_map = folium.Map(location=center_malaysia, zoom_start=11)

    for edge_num, (u, v, data) in enumerate(graph.edges(data=True)):
        if edge_num >= MAX_EDGE_NUM:
            break
        if 'geometry' in data:
            coords = [(y, x) for x, y in data['geometry']]
            folium.PolyLine(coords, color="blue", weight=2).add_to(folium_map)

    # Save the map as an HTML file
    folium_map.save(output_html_map)
    logging.info(f"Interactive map saved to {output_html_map}")

if __name__ == "__main__":
    visualize_interactive_graph(GRAPH_FILE, OUTPUT_HTML_MAP)
