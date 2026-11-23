"""Llogarit koston e një ture Trigger Arc TSP dhe kontrollon vlefshmërinë."""


def build_trigger_index(inst):
    """Kthen idx[trigger_arc] = [(target_arc, kosto_e_re), ...]."""
    idx = {}
    for target, d in inst.triggers.items():
        for trig, cost in d.items():
            idx.setdefault(trig, []).append((target, cost))
    return idx


def arc_lookup(inst):
    """Kthen {(u, v): indeksi i harkut}. Supozon një hark për çift nyjesh."""
    return {(u, v): i for i, (u, v, _) in enumerate(inst.arcs)}


def is_valid(inst, arc_seq):
    """Turi është Hamiltonian: fillon e mbaron në 0, viziton çdo nyje një herë."""
    if len(arc_seq) != inst.n:
        return False
    node = 0
    seen = set()
    for a in arc_seq:
        u, v, _ = inst.arcs[a]
        if u != node or v in seen:
            if not (v == 0 and len(seen) == inst.n - 1 and u == node):
                return False
        seen.add(v)
        node = v
    return node == 0 and len(seen) == inst.n


def tour_cost(inst, arc_seq, trig_index=None):
    """Kosto totale e turit (listë indeksesh harqesh) me efektet e trigger-ave."""
    if trig_index is None:
        trig_index = build_trigger_index(inst)
    last = {}      # last[target] = kosto e vendosur nga trigger-i i fundit
    total = 0.0
    for a in arc_seq:
        total += last.get(a, inst.arcs[a][2])
        for target, new_cost in trig_index.get(a, ()):
            last[target] = new_cost
    return total


def nodes_to_arcs(inst, nodes):
    """Kthen [0, 2, 1, 4, 3] (pa 0-n e fundit) në listë indeksesh harqesh."""
    lookup = arc_lookup(inst)
    cycle = list(nodes) + [nodes[0]]
    return [lookup[(cycle[i], cycle[i + 1])] for i in range(len(nodes))]