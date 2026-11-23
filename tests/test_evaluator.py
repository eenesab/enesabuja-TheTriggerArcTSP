from src.loader import load_instance
from src.evaluator import tour_cost, nodes_to_arcs, is_valid

inst = load_instance("data/example.txt")


def test_solution_1():
    arcs = nodes_to_arcs(inst, [0, 2, 1, 4, 3])
    assert is_valid(inst, arcs)
    assert tour_cost(inst, arcs) == 71


def test_solution_2():
    arcs = nodes_to_arcs(inst, [0, 3, 2, 1, 4])
    assert is_valid(inst, arcs)
    assert tour_cost(inst, arcs) == 62


if __name__ == "__main__":
    test_solution_1()
    test_solution_2()
    print("OK: 71 dhe 62")