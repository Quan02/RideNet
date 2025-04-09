"""This module provides utilities for preprocessing scripts."""

import logging
from pathlib import Path
import pickle
import networkx as nx

def get_logger(name=__name__):
    logger = logging.getLogger(name)
    if not logger.hasHandlers():
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger

logger = get_logger(__name__)

def load_graph(graph_file: Path) -> nx.MultiDiGraph:
    """
    Load the graph from a pickle file.

    Args:
        graph_file (Path): The path to the pickle file containing the extracted graph.
    Returns:
        NetworkX graph
    """
    try:
        logger.info(f"Loading graph from {graph_file}")
        with open(graph_file, "rb") as f:
            graph = pickle.load(f)
        logger.info(f"Graph loaded successfully with {graph.number_of_nodes()} nodes and {graph.number_of_edges()} edges")
        return graph
    except FileNotFoundError:
        logger.error(f"File not found: {graph_file}")
    except pickle.UnpicklingError:
        logger.error(f"Failed to unpickle the graph file: {graph_file}")
    except Exception as e:
        logger.exception(f"An unexpected error occurred while loading the graph: {e}")
    return None


def save_graph(graph: nx.MultiDiGraph, output_file: Path) -> None:
    """ Save the graph to a pickle file.

    Args:    
        graph (nx.MultiDiGraph): The graph to save.
        output_file (Path): Path to the output file.
    """
    try:
        logger.info(f"Saving graph to {output_file}")
        with open(output_file, "wb") as f:
            pickle.dump(graph, f)
        logger.info(f"Graph saved successfully to {output_file}")
    except Exception as e:
        logger.error(f"Failed to save graph to {output_file}: {e}")