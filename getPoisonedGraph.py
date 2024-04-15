import pickle as pkl
import argparse
import torch
import numpy as np
import networkx as nx


def load_tensor_from_pickle(file_path):
    """Load a tensor object from a pickle file."""
    with open(file_path, 'rb') as file:
        tensor = pkl.load(file)
    return tensor


def tensor_to_networkx(tensor):
    """Convert adjacency matrix to a NetworkX graph."""
    # Convert tensor to numpy array
    array = tensor.numpy()
    
    # Create graph from numpy array
    return nx.from_numpy_array(array)

def perform_eda(graph):
    """exploratory data analysis on the graph"""
    # Degree Distribution
    degrees = [deg for node, deg in graph.degree()]
    print("Average Degree:", np.mean(degrees))
    print("Maximum Degree:", np.max(degrees))
    print("Minimum Degree:", np.min(degrees))
    
    # Connected Components
    connected_components = list(nx.connected_components(graph))
    print("Number of Connected Components:", len(connected_components))
    print("Sizes of Connected Components:", [len(c) for c in connected_components])
    
    # Clustering Coefficient
    print("Average Clustering Coefficient:", nx.average_clustering(graph))


def main():
    # Set up the argument parser
    parser = argparse.ArgumentParser(description="Load poisoned adjacency matrix from pickle file.")
    parser.add_argument("--method", type=str, required=True, help="Attack method")
    parser.add_argument("--rate", type=float, required=True, help="Perturbation rate")
    
    args = parser.parse_args()
    
    file_path = f'CLGA/poisoned_adj/Cora_{args.method}_{args.rate:.6f}_adj.pkl'
    
    adjacency_matrix = load_tensor_from_pickle(file_path)

    # Output the shape
    print("Loaded adjacency matrix with shape:", adjacency_matrix.shape)
    
    graph = tensor_to_networkx(adjacency_matrix)
    perform_eda(graph)


if __name__ == "__main__":
    main()