"""Algoritmet: baseline nearest neighbour me backtracking."""
from src.evaluator import build_trigger_index, tour_cost


def nearest_neighbour(inst, max_steps=1_000_000):
    """
    Nearest neighbour me trigger-a dhe backtracking.
    Kthen listën e indekseve të harqeve (tur i plotë) ose None.
    """
    trig = build_trigger_index(inst)
    n = inst.n
    steps = 0

    visited = [False] * n
    visited[0] = True
    path = []        # harqet e zgjedhura deri tani
    states = []      # states[k] = (last, total) para hapit k, për backtracking
    # Për çdo nivel mbajmë listën e kandidatëve të renditur dhe pozicionin
    cand_stack = []

    def candidates(node, last):
        """Harqet dalëse drejt nyjeve të pavizituara, renditur sipas kostos aktuale."""
        out = []
        for a in inst.out_arcs[node]:
            v = inst.arcs[a][1]
            if not visited[v] or (v == 0 and len(path) == n - 1):
                c = last.get(a, inst.arcs[a][2])
                out.append((c, a))
        out.sort()
        return out

    last = {}
    cand_stack.append([candidates(0, last), 0])
    states.append(dict(last))
    node = 0

    while cand_stack:
        steps += 1
        if steps > max_steps:
            return None
        cands, pos = cand_stack[-1]
        if pos >= len(cands):
            # Backtrack: hiq nivelin e fundit
            cand_stack.pop()
            states.pop()
            if path:
                a = path.pop()
                v = inst.arcs[a][1]
                if v != 0:
                    visited[v] = False
                node = inst.arcs[a][0]
            continue
        cand_stack[-1][1] += 1
        c, a = cands[pos]
        v = inst.arcs[a][1]

        # Aplikojmë harkun a
        last = dict(states[-1])
        for target, new_cost in trig.get(a, ()):
            last[target] = new_cost
        path.append(a)
        if v != 0:
            visited[v] = True
        node = v

        if len(path) == n:
            return path          # tur i plotë, mbyllur në 0

        cand_stack.append([candidates(node, last), 0])
        states.append(last)

    return None