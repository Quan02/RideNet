""""This module validates the road network data and provide more information."""

from pathlib import Path
import pickle

import networkx as nx

from preprocessing_utils import get_logger, load_graph

logger = get_logger(__name__) 
EXTRACTED_GRAPH_FILE = Path("data/processed/road_network_processed.pkl")

def validate_graph(graph: nx.MultiDiGraph) -> None:
    """
    Validate the graph by ensure each node and edge has valid attributes.
    
    Args:
        graph (NetworkX graph): The graph to validate.
    """
    logger.info("Validate the graph by checking node and graph connectivity")
    for node_id, data in graph.nodes(data=True):
        if 'x' not in data or 'y' not in data:
            logger.warning(f"Node {node_id} is missing x and y attributes.")
    for u, v, data in graph.edges(data=True):
        if 'geometry' not in data:
            logger.warning(f"Edge {u} -> {v} is missing geometry.")
    if nx.is_weakly_connected(graph):
        logger.info("Graph is connected.")
    else:
        components = list(nx.weakly_connected_components(graph))
        logger.warning(f"Graph has {len(components)} disconnected components.")

if __name__ == "__main__":
    road_graph = load_graph(EXTRACTED_GRAPH_FILE)
    validate_graph(road_graph)