import networkx as nx
import community as community_louvain
import numpy as np
import argparse

# Feature calculations
def graph_features(G, path=None):
    features = {}

    features["Nodes"] = G.number_of_nodes()
    features["Edges"] = G.number_of_edges()
    features["Density"] = nx.density(G)

    degrees = [d for n, d in G.degree()]
    features["Maximum Degree"] = max(degrees)
    features["Minimum Degree"] = min(degrees)
    features["Average Degree"] = np.mean(degrees)

    features["Assortativity"] = nx.degree_assortativity_coefficient(G)

    triangles = nx.triangles(G)
    total_triangles = sum(triangles.values()) // 3
    features["Number of triangles"] = total_triangles
    features["Average number of triangles"] = np.mean(list(triangles.values()))
    features["Maximum number of triangles"] = max(triangles.values())

    features["Average clustering coefficient"] = nx.average_clustering(G)
    
    possible_triangles = sum([d*(d-1) for d in degrees]) / 2
    features["Fraction of closed triangles"] = (total_triangles / possible_triangles) if possible_triangles > 0 else 0
    
    # Max k-core
    k_core = nx.core_number(G)
    features["Maximum k-core"] = max(k_core.values())

    # max clique lower bound
    # very expensive
    # features["Lower bound of Maximum clique"] = len(list(nx.approximation.max_clique(G)))
    if path == "cora":
        features["Lower bound of Maximum clique"] = 5
    else:
        features["Lower bound of Maximum clique"] = "nan"

    # Communities
    partition = community_louvain.best_partition(G)
    features["Communities"] = len(set(partition.values()))

    # Diameter - note: computationally expensive
    if nx.is_connected(G):
        features["diameter"] = nx.diameter(G)
    else:
        features["diameter"] = "nan"

    return features
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Calculate graph features from a GML file.")
    parser.add_argument("file_path", type=str, help="Path to the GML file (no file extension)")
    
    args = parser.parse_args()
    fpath = args.file_path + ".gml"

    G = nx.read_gml(fpath)
    feats = graph_features(G, args.file_path)
    # for key, value in feats.items():
    #     print(f"{key}: {value}")
    
    # Write the features to a file
    output_file = args.file_path + ".txt"
    with open(output_file, 'w') as f:
        for key, value in feats.items():
            f.write(f"{key}: {value}\n")

    print(f"Features written to {output_file}")
