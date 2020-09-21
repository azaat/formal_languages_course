from pygraphblas import Matrix, BOOL, lib
from itertools import product
from src.graph import LabelGraph


def perform_rpq(graph, regex_automaton, start_lst, end_lst):
    query_dict = regex_automaton.to_GrB_matrix()
    graph_dict = graph.graph_dict
    tmp_graph_dict = {}
    num_vert = 0

    # Getting intersection with kronecker product
    for label in query_dict:
        tmp_graph_dict[label] = graph_dict[label].kronecker(query_dict[label])
        if num_vert == 0:
            num_vert = tmp_graph_dict[label].ncols

    # To GrB matrix

    tmp = LabelGraph()
    tmp.graph_dict = tmp_graph_dict
    tmp.num_vert = num_vert
    result = tmp.to_GrB_matrix()

    # Transform double index to single value
    def coord_to_index(coord):
        v_graph, v_regex = coord
        return v_graph * regex_automaton.num_vert + v_regex

    start_states = set(map(
        coord_to_index,
        product(range(graph.num_vert), regex_automaton.start_states)
    ))
    final_states = set(map(
        coord_to_index,
        product(range(graph.num_vert), regex_automaton.final_states)
    ))

    # result_dfa = MatrixAutomaton(
    #     result, start_states, final_states
    # ).to_dfa()

    # Computing reachability
    print("Transitive closure\n")
    reachability_matrix_ = get_transitive_closure(result).select(lib.GxB_NONZERO)
    print("Finished transitive closure\n")
    reachability_matrix = Matrix.sparse(BOOL, graph.num_vert, graph.num_vert)
    print("Started r_m\n")

    for v_i, v_j, _ in zip(*reachability_matrix_.select(lib.GxB_NONZERO).to_lists()):
        if (v_i in start_states) and (v_j in final_states):
            # Getting initial graph vertex from index in result matrix
            v_from = v_i // regex_automaton.num_vert
            v_to = v_j // regex_automaton.num_vert
            # Debug output
            reachability_matrix[v_from, v_to] = True
    return reachability_matrix

    #checksums = {}
    #for label in tmp.graph_dict:
    #    checksums[label] = tmp.graph_dict[label].nvals
    #    print(f'{label} {tmp.graph_dict[label].nvals}')
    #return checksums


def get_transitive_closure(matrix):
    for i in range(matrix.ncols):
        old_nvals = matrix.nvals
        matrix += matrix @ matrix
        if (matrix.nvals == old_nvals):
            break
    return matrix
