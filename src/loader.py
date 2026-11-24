"""Lexon një instancë Trigger Arc TSP (formati MESS 2024)."""
from dataclasses import dataclass, field


@dataclass
class Instance:
    n: int                       # numri i nyjeve (nyja 0 = depo)
    arcs: list                   # arcs[i] = (from, to, kosto)
    # triggers[target_arc] = {trigger_arc: kosto_e_re}
    triggers: dict = field(default_factory=dict)
    out_arcs: list = field(default_factory=list)  # out_arcs[u] = indekset e harqeve që dalin nga u
    bad_rel: int = 0             # relacione ku (from, to) nuk përputhet me indeksin e harkut


def load_instance(path):
    with open(path, encoding="utf-8") as f:
        tokens = f.read().split()

    pos = 0

    def nxt():
        nonlocal pos
        pos += 1
        return tokens[pos - 1]

    n, m, r = int(nxt()), int(nxt()), int(nxt())

    arcs = [None] * m
    for _ in range(m):
        idx, u, v, cost = int(nxt()), int(nxt()), int(nxt()), float(nxt())
        arcs[idx] = (u, v, cost)

    triggers = {}
    bad = 0
    for _ in range(r):
        nxt()                                              # indeksi i relacionit
        t_idx, t_from, t_to = int(nxt()), int(nxt()), int(nxt())   # trigger
        a_idx, a_from, a_to = int(nxt()), int(nxt()), int(nxt())   # target
        cost = float(nxt())
        if (arcs[t_idx][0], arcs[t_idx][1]) != (t_from, t_to) or \
           (arcs[a_idx][0], arcs[a_idx][1]) != (a_from, a_to):
            bad += 1
        triggers.setdefault(a_idx, {})[t_idx] = cost

    out_arcs = [[] for _ in range(n)]
    for i, (u, v, _) in enumerate(arcs):
        out_arcs[u].append(i)

    return Instance(n, arcs, triggers, out_arcs, bad)