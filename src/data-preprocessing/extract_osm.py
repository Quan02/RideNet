"""
This script extracts OpenStreetMap (OSM) data within a bounding box covering Kuala Lumpur and Selangor.
It uses Osmium to process the raw PBF data and OSMnx to fetch geographic boundaries.
"""
from pathlib import Path

import osmium            # For parsing and filtering needed data from OSM PBF files.
import osmium.osm
import osmnx as ox       # For retrieving region boundaries from OSM.
import networkx as nx    # For generate directed graph.
from typing import Tuple, List
from preprocessing_utils import get_logger, save_graph

logger = get_logger(__name__) 
REGIONS = ["Selangor, Malaysia", "Kuala Lumpur, Malaysia"]
OSM_FILE = Path("data/raw/malaysia-singapore-brunei-latest.osm.pbf")
OUTPUT_GRAPH_FILE = Path("data/processed/road_network.pkl")
  
class RoadGraphExtractor(osmium.SimpleHandler):
    """
    Extract nodes and roads to build a graph, focusing on car-accessible roads.
    """
    ROAD_TYPE_FILE = Path("data/processed/road_types.txt")

    def __init__(self, bbox: Tuple[float, float, float, float]):
        """
        Initialize the graph with a bounding box.

        Parameters:
            bbox (tuple): (min_lon, min_lat, max_lon, max_lat)
        """
        super().__init__()
        self.min_lon, self.min_lat, self.max_lon, self.max_lat = bbox
        self.nodes = {}  # {node_id: (longitude, latitude)}
        self.edges = []  # [(source_node, target_node, attributes)]
        self.valid_road_types = self._load_valid_road_types(self.ROAD_TYPE_FILE)

    def _load_valid_road_types(self, filename: str) -> set:
        """
        Load valid road types from a file.
        Each line in the file should contain one road type.
        """
        with open(filename, 'r') as f:
            return set(line.strip() for line in f if line.strip())
    
    def node(self, node: osmium.osm.Node) -> None:
        """
        Process OSM nodes and store their coordinates within the boundary area.
        """
        if self.min_lon <= node.lon <= self.max_lon and self.min_lat <= node.lat <= self.max_lat:
            self.nodes[node.id] = (node.lon, node.lat)  # Store longitude and latitude
    
    def way(self, way: osmium.osm.Way) -> None:
        """
        Process OSM ways (roads) and create edges with attributes.
        """
        if 'highway' in way.tags:  # Only extract car roads.
            road_type = way.tags['highway']
            if road_type not in self.valid_road_types:
                return  # Skip non-car roads
            oneway = way.tags.get('oneway', 'no').lower() in ['yes', 'true', '1']
            nodes = list(way.nodes)
            for start, end in zip(nodes[:-1], nodes[1:]):
                if start.ref in self.nodes and end.ref in self.nodes:
                    segment_geometry = [(self.nodes[start.ref][0], self.nodes[start.ref][1]),
                                    (self.nodes[end.ref][0], self.nodes[end.ref][1])]
                    edge_attrs = {"highway": road_type, "geometry": segment_geometry}
                    edge = (start.ref, end.ref, edge_attrs)
                    self.edges.append(edge)
                    # If not oneway, add a reverse edge.
                    if not oneway:
                        self.edges.append((end.ref, start.ref, edge_attrs))

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

def generate_road_graph(osm_file: Path, regions: List[str], output_file: Path) -> None:
    """
    Build a road network graph and save it to a file.

    Args:
        osm_file (str): Path to the raw OSM file.
        regions (Tuple): Contain the region that needed to be extracted.
        output_file (str): Path to save the graph as a pickle file.
    """
    bbox = retrieve_boundary(regions)
    extractor = RoadGraphExtractor(bbox)
    extractor.apply_file(osm_file)
    
    # Create directed graph
    graph = nx.MultiDiGraph()
    for node_id, coords in extractor.nodes.items():
        graph.add_node(node_id, x=coords[0], y=coords[1])
    for source, target, attr in extractor.edges:
        graph.add_edge(source, target, **attr)

    graph.graph["crs"] = "epsg:4326" # Illustrate for longitude and latitude
    graph = extract_largest_subgraph(graph)
    # Save the graph as pickle file for future use.
    save_graph(graph, output_file)
    

def retrieve_boundary(regions: List[str])-> Tuple[float, float, float, float]:
    """
    Fetch the combined bounding box for multiple regions.
    Args:
        regions (List[str]): List of region names.
    Returns:
        Tuple[float, float, float, float]: Combined bounding box. 
    """
    min_lon, min_lat, max_lon, max_lat = float('inf'), float('inf'), float('-inf'), float('-inf')
    for region in regions:
        gdf = ox.geocode_to_gdf(region)
        region_min_lon, region_min_lat, region_max_lon, region_max_lat = gdf.total_bounds
        min_lon = min(min_lon, region_min_lon)
        min_lat = min(min_lat, region_min_lat)
        max_lon = max(max_lon, region_max_lon)
        max_lat = max(max_lat, region_max_lat)
    return (min_lon, min_lat, max_lon, max_lat)

if __name__ == "__main__":
    generate_road_graph(OSM_FILE, REGIONS, OUTPUT_GRAPH_FILE)