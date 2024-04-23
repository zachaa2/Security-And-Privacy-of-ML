import torch
from netgan.train import train
from netgan.model import Generator, Discriminator
from netgan import utils

import numpy as np
import matplotlib.pyplot as plt

import networkx as nx

import argparse
from scipy.sparse import csr_matrix, lil_matrix
import pickle as pkl
import networkx as nx


def load_matrix_from_pickle(file_path):
    """Load a csr SparseMatrix object from a pickle file."""
    # binary file is of a tensor
    with open(file_path, 'rb') as file:
        tensor = pkl.load(file)
    # convert tensor to csr SparseMatrix format
    arr = tensor.numpy()
    matr = csr_matrix(arr)
    return matr

def reintegrate_synthetic_lcc(orig, lcc, synth):
    '''
        Function to create the full synthetic graph by adding back the LCC to the original graph.
        NetGAN considers only the LCC, so we need to combine the returned lcc with the non-lcc indices
        from the original graph.
        Params:
            orig - original graph in csr form.
            lcc - list of the lcc indices.
            synth - a numpy array matrix which is the synthetic LCC.
        Returns: 
            new_adj_matrix - new full SparseMatrix in csr form. 
    '''
    # Convert original adj matrix to a LIL matrix for easier assignment
    new_adj_matrix = orig.tolil()
    
    # Add the synthetic adjacency matrix from the LCC indices
    for i, row in enumerate(lcc):
        for j, col in enumerate(lcc):
            new_adj_matrix[row, col] = synth[i, j]
    
    return new_adj_matrix.tocsr()

def write_graph(adj, method, rate):
    '''
    Function to convert the SparceMatrix to a tensor object and write it to a pickle file.
    Params: 
        adj - CSR adjacency matrix of the full graph. 
        method - attack method used to poison graph.
        rate - poison rate used on the graph.
    '''
   # Convert CSR to dense numpy array
    dense_array = adj.toarray()
    # convert numpy to tensor
    tensor = torch.tensor(dense_array, dtype=torch.float)
    # save to pickle file
    with open(f'data/Cora_{method}_{rate:.6f}_synthetic.pkl', 'wb') as f:
        pkl.dump(tensor, f)

def write_logs(logs, method, rate):
    '''
    Function to write the logs (the output of the train function) to a binary
    Params:
        logs - dictionary which contains the logged data.
        method - attack method used to poison graph.
        rate - poison rate used on the graph.
    '''
    file_path = f'data/Cora_{method}_{rate:.6f}_logs.pkl'
    with open(file_path, 'wb') as f:
        pkl.dump(logs, f)

def csr_matrices_equal(mat1, mat2):
    # Check if both matrices have the same shape
    if mat1.shape != mat2.shape:
        return False
    
    # Check if both matrices have the same number of non-zero entries
    if mat1.nnz != mat2.nnz:
        return False
    
    # Check if both matrices have the same data in the same positions
    if not (mat1 != mat2).nnz == 0:
        return False
    
    return True

if __name__ == '__main__':
    # get args
    parser = argparse.ArgumentParser(description="Load poisoned adjacency matrix from pickle file.")
    parser.add_argument("--method", type=str, required=True, help="Attack method")
    parser.add_argument("--rate", type=float, required=True, help="Perturbation rate")
    
    args = parser.parse_args()

    '''
    NOTE: Requires that the poisoned adj matrix exists in the filepath ../CLGA/poisoned_adj/ as a pickle file with the following name convention
    Cora_{args.method}_{args.rate:.6f}_adj.pkl
    If the poisoned adj is not there you must first run the script to poison the graph
    '''

    # get the filepath of the poisoned adj matrix from the given attack method and rate
    file_path = f'../CLGA/poisoned_adj/Cora_{args.method}_{args.rate:.6f}_adj.pkl' 

    ### load the data
    _A_orig = load_matrix_from_pickle(file_path=file_path) # This is for the experiments
    # _A_obs, _X_obs, _z_obs = utils.load_npz("data/cora_ml.npz") This is from the NetGAN paper 

    _A_orig = _A_orig + _A_orig.T
    _A_orig[_A_orig > 1] = 1

    '''largest weakly connected component'''
    G = nx.from_scipy_sparse_array(_A_orig, create_using=nx.DiGraph)
    wcc = max(nx.weakly_connected_components(G), key=len)
    orig_indices = np.array(list(wcc))
    G_lcc = G.subgraph(wcc).copy()
    # Convert the subgraph back to a CSR matrix
    numpy_array = nx.to_numpy_array(G_lcc)
    _A_obs = csr_matrix(numpy_array)
    
    _N = _A_obs.shape[0]
    # get splits 
    val_share = 0.1
    test_share = 0.05
    seed = 481516234

    train_graph = _A_obs
    assert (train_graph.toarray() == train_graph.toarray().T).all()

    train_ones, val_ones, val_zeros, test_ones, test_zeros = utils.train_val_test_split_adjacency(_A_obs, val_share,
                                                                                                  test_share, seed,
                                                                                                  undirected=True,
                                                                                                  connected=True,
                                                                                                  asserts=True)

    ### Parameter
    rw_len = 16
    batch_size = 128
    temperature = 5.0
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    print('Using device:', device)
    print('Device Name:', torch.cuda.get_device_name(torch.cuda.current_device()))

    walk = utils.RandomWalker(train_graph, rw_len, p=1, q=1, batch_size=batch_size)

    ### build generator and discriminator
    netG = Generator(_N, rw_len, tau=temperature, device=device).to(device)
    netD = Discriminator(_N, rw_len).to(device)

    ### define the stopping criterion
    stopping_criterion = "eo"
    assert stopping_criterion in ["val", "eo"], "Please set the desired stopping criterion."

    if stopping_criterion == "val":
        stopping = None
    if stopping_criterion == "eo":
        stopping = 0.5

    ### train model
    eval_every = 1000
    # eval_every = 2

    log_dict = train(netG, netD, _N, rw_len, val_ones, val_zeros, batch_size, walk.walk, _A_obs,
                    device=device, stopping=stopping, eval_every=eval_every, max_patience=20, max_iters=25000)
    # log_dict = train(netG, netD, _N, rw_len, val_ones, val_zeros, batch_size, walk.walk, _A_obs,
    #                 device=device, stopping=stopping, eval_every=eval_every, max_patience=20, max_iters=10)
    print(log_dict.keys())
    
    # get last generated graph from the validation logs
    synthetic_lcc = log_dict['generated_graphs'][-1]
    # print(type(synthetic_lcc))

    # get the new full graph by adding back the synthetic generated lcc into the original graph
    '''reintegrate the lcc adj matrix'''
    # reintegrate the lcc back into the full graph
    new_full_csr = csr_matrix(_A_orig.shape, dtype=np.int8)
    full_lil = new_full_csr.tolil()

    # copy original edges that are not in lcc
    for i, j in zip(*_A_orig.nonzero()):
        if i not in orig_indices or j not in orig_indices:
            full_lil[i, j] = 1
    
    # copy edges from new lcc back into the full graph
    for i, j in zip(*synthetic_lcc.nonzero()):
        orig_i, orig_j = orig_indices[i], orig_indices[j]
        full_lil[orig_i, orig_j] = synthetic_lcc[i, j]

    final_csr = full_lil.tocsr()
    
    '''write to file'''
    # write new synthetic graph to binary
    write_graph(final_csr, args.method, args.rate)
    # write_logs(log_dict, args.method, args.rate)

    # convert generated and original adj matrices to networkx graphs
    G = nx.from_scipy_sparse_array(final_csr)
    OG = nx.from_scipy_sparse_array(_A_orig)

    # EDA
    print("Original graph nodes:", OG.order())
    print("Original graph edges:", OG.size())
    
    print("Generated graph nodes:", G.order())
    print("Generated graph edges:", G.size())
    

    '''plotting validation performance'''
    # plt.plot(np.arange(len(log_dict['val_performances'])) * eval_every,
    #          np.array(log_dict['val_performances'])[:, 0], label='ROC-AUC')
    # plt.plot(np.arange(len(log_dict['val_performances'])) * eval_every,
    #          np.array(log_dict['val_performances'])[:, 1], label='Avg.Perc')
    # plt.title('Validation')
    # plt.legend()
    # plt.show()