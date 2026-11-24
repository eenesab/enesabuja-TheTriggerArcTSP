"""Algoritmet: baseline nearest neighbour me trigger-a, prerje dhe restart-e."""
import random
from src.evaluator import build_trigger_index


def _attempt(inst, trig, rev, mode, rng, max_steps):
    """Një kërkim DFS. mode: 'cost' | 'degree' | 'random'. Kthen (path ose None, hapa)."""
    n = inst.n
    arcs = inst.arcs
    out_arcs = inst.out_arcs
    visited = [False] * n
    visited[0] = True
    path = []
    state = {"steps": 0, "aborted": False}

    def reach_ok(cur, remaining):
        """Çdo nyje e pavizituar arrihet nga cur dhe arrin depon."""
        if remaining == 0:
            return True
        seen = {cur}
        stack = [cur]
        while stack:
            u = stack.pop()
            for a in out_arcs[u]:
                v = arcs[a][1]
                if not visited[v] and v not in seen:
                    seen.add(v)
                    stack.append(v)
        if len(seen) - 1 != remaining:
            return False
        seen2 = {0}
        stack = [0]
        cnt = 0
        while stack:
            v = stack.pop()
            for u in rev[v]:
                if not visited[u] and u not in seen2:
                    seen2.add(u)
                    cnt += 1
                    stack.append(u)
        return cnt == remaining

    def dfs(cur, last, depth):
        state["steps"] += 1
        if state["steps"] > max_steps:
            state["aborted"] = True
            return False
        if depth == n - 1:                       # nyja e fundit: mbyll drejt depos
            for a in out_arcs[cur]:
                if arcs[a][1] == 0:
                    path.append(a)
                    return True
            return False

        cands = []
        for a in out_arcs[cur]:
            v = arcs[a][1]
            if not visited[v]:
                c = last.get(a, arcs[a][2])
                onward = sum(1 for b in out_arcs[v] if not visited[arcs[b][1]])
                if mode == "cost":
                    key = (c, onward)
                elif mode == "degree":
                    key = (onward, c)
                else:
                    key = (onward, rng.random())
                cands.append((key, a))
        cands.sort()

        for _, a in cands:
            v = arcs[a][1]
            visited[v] = True
            path.append(a)
            if a in trig:
                new_last = dict(last)
                for target, new_cost in trig[a]:
                    new_last[target] = new_cost
            else:
                new_last = last
            if reach_ok(v, n - depth - 2) and dfs(v, new_last, depth + 1):
                return True
            visited[v] = False
            path.pop()
            if state["aborted"]:
                return False
        return False

    ok = dfs(0, {}, 0)
    return (path if ok else None), state["steps"]


def nearest_neighbour(inst, total_steps=150_000, trig=None, seed=0):
    """
    Baseline: DFS lakmitar me trigger-a aktivë, prerje dhe restart-e.
    Kthen listën e harqeve ose None. Info te nearest_neighbour.last_info
    = (hapa totalë, numri i përpjekjeve, status).
    """
    if trig is None:
        trig = build_trigger_index(inst)
    rev = [[] for _ in range(inst.n)]
    for (u, v, _) in inst.arcs:
        rev[v].append(u)

    rng = random.Random(seed)
    steps_used = 0
    attempt = 0
    result = None
    while steps_used < total_steps:
        if attempt == 0:
            mode, limit = "cost", 20_000
        elif attempt == 1:
            mode, limit = "degree", 20_000
        else:
            mode, limit = "random", 5_000
        result, steps = _attempt(inst, trig, rev, mode, rng, limit)
        steps_used += steps
        attempt += 1
        if result is not None:
            break

    status = "ok" if result is not None else "kufi hapash"
    nearest_neighbour.last_info = (steps_used, attempt, status)
    return result