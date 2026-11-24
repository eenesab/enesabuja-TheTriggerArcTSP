from src.loader import load_instance
from src.evaluator import tour_cost, nodes_to_arcs, is_valid
from src.localsearch import tour_cost_fast, local_search
from src.ils import iterated_local_search

inst = load_instance("data/example.txt")

# Vlerësuesi i shpejtë duhet të japë të njëjtat vlera si ai i ngadalshëm
for nodes, expected in (([0, 2, 1, 4, 3], 71), ([0, 3, 2, 1, 4], 62)):
    arcs = nodes_to_arcs(inst, nodes)
    assert tour_cost_fast(inst, arcs) == tour_cost(inst, arcs) == expected

start = nodes_to_arcs(inst, [0, 2, 1, 4, 3])

arcs, cost, moves = local_search(inst, start)
assert is_valid(inst, arcs) and cost <= 62
print("Local search:", cost, "me", moves, "lëvizje")

arcs, cost, iters = iterated_local_search(inst, start, time_limit=0.5)
assert is_valid(inst, arcs) and tour_cost(inst, arcs) == cost <= 62
print("ILS:", cost, "me", iters, "iterime")
print("OK")