from itertools import combinations

TARGET = 24
EPS = 1e-6


class ClassicalDFSSolver:
    def __init__(self):
        self.nodes_expanded = 0
        self.visited = set()

    def solve(self, numbers):
        self.nodes_expanded = 0
        self.visited = set()

        state = [(float(n), str(n)) for n in numbers]
        solution = self._dfs(state)

        return {
            "success": solution is not None,
            "solution": solution,
            "nodes_expanded": self.nodes_expanded,
            "api_calls": 0,
            "pruned": len(self.visited)
        }

    @staticmethod
    def _key(state):
        return tuple(sorted(round(v, 6) for v, _ in state))

    def _dfs(self, state):
        self.nodes_expanded += 1

        if len(state) == 1:
            value, expr = state[0]
            return expr if abs(value - TARGET) < EPS else None

        key = self._key(state)
        if key in self.visited:
            return None
        self.visited.add(key)

        for i, j in combinations(range(len(state)), 2):
            a, expr_a = state[i]
            b, expr_b = state[j]

            remaining = [
                state[k] for k in range(len(state))
                if k not in (i, j)
            ]

            candidates = [
                (a + b, f"({expr_a} + {expr_b})"),
                (a - b, f"({expr_a} - {expr_b})"),
                (b - a, f"({expr_b} - {expr_a})"),
                (a * b, f"({expr_a} * {expr_b})"),
            ]

            if abs(b) > EPS:
                candidates.append((a / b, f"({expr_a} / {expr_b})"))

            if abs(a) > EPS:
                candidates.append((b / a, f"({expr_b} / {expr_a})"))

            for value, expr in candidates:
                result = self._dfs(remaining + [(value, expr)])
                if result is not None:
                    return result

        return None