"""
Preprocess the road network graph by extracting largest connected subgraph.
"""

from pathlib import Path
import networkx as nx
from geopy.distance import geodesic # For calculating distances between nodes.

from preprocessing_utils import get_logger, load_graph, save_graph

logger = get_logger(__name__) 
INPUT_GRAPH_FILE = Path("data/processed/road_network_processed.pkl")
OUTPUT_GRAPH_FILE = Path("data/processed/road_network_distance.pkl")

def add_edge_distances(graph: nx.MultiDiGraph) -> nx.MultiDiGraph:
    """
    Add geographic distances to the edges of the graph.

    Args:
        graph (nx.MultiDiGraph): The graph to process.

    Returns:
        nx.MultiDiGraph: The graph with distance attribute on edges.
    """
    for u, v, data in graph.edges(data=True):
        if 'geometry' in data  and len(data['geometry']) == 2:
            start_coords = (data['geometry'][0][1], data['geometry'][0][0]) # (lat,lon)
            end_coords = (data['geometry'][1][1], data['geometry'][1][0])
            distance = geodesic(start_coords, end_coords).meters
            data['distance'] = distance
    return graph

if __name__ == "__main__":
    road_graph = load_graph(INPUT_GRAPH_FILE)
    road_graph = add_edge_distances(road_graph)
    save_graph(road_graph, OUTPUT_GRAPH_FILE)