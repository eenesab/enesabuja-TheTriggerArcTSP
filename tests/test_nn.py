from src.loader import load_instance
from src.evaluator import tour_cost, is_valid
from src.algorithms import nearest_neighbour

inst = load_instance("data/example.txt")
tour = nearest_neighbour(inst)
print("Tur (harqe):", tour)
assert tour is not None and is_valid(inst, tour)
print("Kosto:", tour_cost(inst, tour))