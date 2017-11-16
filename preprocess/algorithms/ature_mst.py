import itertools as itr
from heapq import heappop, heappush
from itertools import count
from multiprocessing import Process

import networkx as nx

from commons.timer import check_time

"""
  A minimum spanning tree is a sub-graph of the graph (a tree)
  with the minimum sum of edge weights.  A spanning forest is a
  union of the spanning trees for each connected component of the graph.
  """


@check_time
def _prim_mst_edges(lattice=None, img_lattice=None, threshold=None, weight=None, seed=None):
    c = itr.count()
    if lattice.is_directed():
        raise nx.NetworkXError(
            "Minimum spanning tree not defined for directed graphs.")

    push = heappush
    pop = heappop

    nodes = lattice.nodes()
    c = count()

    while nodes:
        u = seed.pop(0)
        frontier = []
        visited = [u]
        for u, v in lattice.edges(u):
            push(frontier, (lattice[u][v].get(weight, 1), next(c), u, v))

        while frontier:
            _, _, u, v = pop(frontier)
            if v in visited:
                continue
            visited.append(v)
            nodes.remove(v)
            for v, w in lattice.edges(v):
                if w not in visited:
                    push(frontier, (lattice[v][w].get(weight, 1), next(c), v, w))

            if 0 == threshold:
                return

            lattice.accumulator[u, v] = 255
            threshold = threshold - 1


def _prim_mst(lattice=None, lattice_object=None, threshold=None, weight=None, seed=None):
    """
     If the graph is not connected a spanning forest is constructed.  A
     spanning forest is a union of the spanning trees for each
     connected component of the graph.
    """
    _prim_mst_edges(lattice=lattice, lattice_object=lattice_object, threshold=threshold, weight=weight, seed=seed)


def run_mst(lattice_object=None, threshold=50000, weight='cost', seed=[], test_index=-1):
    all_p = []
    if test_index >= 0:
        p = Process(
            target=_prim_mst(lattice=lattice_object.k_lattices[test_index], lattice_object=lattice_object,
                             threshold=threshold, weight=weight,
                             seed=seed))
        all_p.append(p)

    else:
        for a_lattice in lattice_object.k_lattices:
            p = Process(
                target=_prim_mst(lattice=a_lattice, lattice_object=lattice_object, threshold=threshold, weight=weight,
                                 seed=seed))
        all_p.append(p)

    for p in all_p:
        p.run()
    for p in all_p:
        p.join()
