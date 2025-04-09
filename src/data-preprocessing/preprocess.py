"""
Preprocess the road network graph by extracting largest connected subgraph.
"""

from pathlib import Path
import pickle
import networkx as nx

from preprocessing_utils import get_logger, load_graph, save_graph

logger = get_logger(__name__) 
INPUT_GRAPH_FILE = Path("data/processed/road_network.pkl")
OUTPUT_GRAPH_FILE = Path("data/processed/road_network_processed.pkl")

def extract_largest_subgraph(graph: nx.MultiDiGraph) -> nx.MultiDiGraph:
    """
    Extract the largest connected subgraph from the original graph.

    Args:
        graph (NetworkX graph): The original graph.
    Returns:
        NetworkX graph: The largest connected subgraph.
    """
    logger.info(f"Extract largest subgraph from file.")
    largest_component = max(nx.weakly_connected_components(graph), key=len)
    largest_subgraph = graph.subgraph(largest_component).copy()
    logger.info(f"Largest subgraph has {largest_subgraph.number_of_nodes()} nodes and {largest_subgraph.number_of_edges()} edges.")
    return largest_subgraph

if __name__ == "__main__":
    road_graph = load_graph(INPUT_GRAPH_FILE)
    largest_subgraph = extract_largest_subgraph(road_graph)
    save_graph(largest_subgraph, OUTPUT_GRAPH_FILE)