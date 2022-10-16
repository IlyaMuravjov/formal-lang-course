from typing import Callable
from typing import Dict
from typing import Iterator
from typing import Set
from typing import Tuple
from typing import Union

import pyformlang.finite_automaton
import scipy

from project.scipy_bool_decomposition import BoolDecomposition

__all__ = ["BoolDecomposedNFA"]


class BoolDecomposedNFA:
    def __init__(
        self,
        state_count: int,
        idx_to_state: Callable[[int], pyformlang.finite_automaton.State],
        state_to_idx: Callable[[pyformlang.finite_automaton.State], int],
        adj_bool_decomposition: BoolDecomposition[pyformlang.finite_automaton.Symbol],
        start_state_indices: Set[int],
        final_state_indices: Set[int],
    ):
        self.state_count = state_count
        self.idx_to_state = idx_to_state
        self.state_to_idx = state_to_idx
        self.adj_bool_decomposition = adj_bool_decomposition
        self.start_state_indices = start_state_indices
        self.final_state_indices = final_state_indices

    @staticmethod
    def from_nfa(
        nfa: pyformlang.finite_automaton.NondeterministicFiniteAutomaton,
    ) -> "BoolDecomposedNFA":
        idx_to_state_dict: Dict[int, pyformlang.finite_automaton.State] = dict()
        state_to_idx_dict: Dict[pyformlang.finite_automaton.State, int] = dict()
        for (idx, state) in enumerate(nfa.states):
            idx_to_state_dict[idx] = state
            state_to_idx_dict[state] = idx
        adj_bool_decomposition = BoolDecomposition(
            (len(nfa.states), len(nfa.states)),
            content=(
                (state_to_idx_dict[source], state_to_idx_dict[target], symbol)
                for (source, symbol, target) in nfa
            ),
        )
        return BoolDecomposedNFA(
            state_count=len(nfa.states),
            idx_to_state=idx_to_state_dict.__getitem__,
            state_to_idx=state_to_idx_dict.__getitem__,
            adj_bool_decomposition=adj_bool_decomposition,
            start_state_indices=set(
                state_to_idx_dict[state] for state in nfa.start_states
            ),
            final_state_indices=set(
                state_to_idx_dict[state] for state in nfa.final_states
            ),
        )

    def __iter__(
        self,
    ) -> Iterator[
        Tuple[
            pyformlang.finite_automaton.State,
            pyformlang.finite_automaton.Symbol,
            pyformlang.finite_automaton.State,
        ]
    ]:
        return (
            (self.idx_to_state(start_idx), symbol, self.idx_to_state(finish_idx))
            for (start_idx, finish_idx, symbol) in self.adj_bool_decomposition
        )

    def to_nfa(self) -> pyformlang.finite_automaton.NondeterministicFiniteAutomaton:
        nfa = pyformlang.finite_automaton.NondeterministicFiniteAutomaton()
        for idx in self.start_state_indices:
            nfa.add_start_state(self.idx_to_state(idx))
        for idx in self.final_state_indices:
            nfa.add_final_state(self.idx_to_state(idx))
        for (source, target, symbol) in self.adj_bool_decomposition:
            nfa.add_transition(
                self.idx_to_state(source), symbol, self.idx_to_state(target)
            )
        return nfa

    def intersect(self, other: "BoolDecomposedNFA") -> "BoolDecomposedNFA":
        return BoolDecomposedNFA(
            state_count=self.state_count * other.state_count,
            idx_to_state=lambda i: pyformlang.finite_automaton.State(
                (
                    self.idx_to_state(i // other.state_count),
                    (other.idx_to_state(i % other.state_count)),
                )
            ),
            state_to_idx=lambda state: self.state_to_idx(state.value[0])
            * other.state_count
            + other.state_to_idx(state.value[1]),
            adj_bool_decomposition=self.adj_bool_decomposition.kron(
                other.adj_bool_decomposition
            ),
            start_state_indices=set(
                i * other.state_count + j
                for i in self.start_state_indices
                for j in other.start_state_indices
            ),
            final_state_indices=set(
                i * other.state_count + j
                for i in self.final_state_indices
                for j in other.final_state_indices
            ),
        )

    def get_reachable(
        self,
    ) -> Set[
        Tuple[pyformlang.finite_automaton.State, pyformlang.finite_automaton.State]
    ]:
        return set(
            (self.idx_to_state(source), self.idx_to_state(target))
            for (source, target) in (
                zip(*self.adj_bool_decomposition.transitive_closure().nonzero())
            )
            if source in self.start_state_indices and target in self.final_state_indices
        )

    def sync_bfs(
        self, other: "BoolDecomposedNFA", group_by_start: bool = False
    ) -> Union[
        Set[pyformlang.finite_automaton.State],
        Dict[pyformlang.finite_automaton.State, Set[pyformlang.finite_automaton.State]],
    ]:
        def create_front(start_state_indices) -> scipy.sparse.csr_matrix:
            front_row = scipy.sparse.dok_matrix((1, self.state_count), dtype=bool)
            for i in start_state_indices:
                front_row[0, i] = True
            front = scipy.sparse.dok_matrix(
                (other.state_count, self.state_count), dtype=bool
            )
            for i in other.start_state_indices:
                front[i, :] = front_row
            return front.tocsr()

        if not self.start_state_indices:
            return dict() if group_by_start else set()

        common_labels = set(self.adj_bool_decomposition.matrices.keys()).intersection(
            other.adj_bool_decomposition.matrices.keys()
        )
        front = (
            scipy.sparse.vstack([create_front({i}) for i in self.start_state_indices])
            if group_by_start
            else create_front(self.start_state_indices)
        )
        visited = front
        while True:
            next_front = scipy.sparse.dok_matrix(front.shape, dtype=bool)
            for label in common_labels:
                next_front_part = front @ self.adj_bool_decomposition.matrices[label]
                for sub_front_idx in range(
                    len(self.start_state_indices) if group_by_start else 1
                ):
                    sub_front_offset = sub_front_idx * other.state_count
                    for (i, j) in zip(
                        *other.adj_bool_decomposition.matrices[label].nonzero()
                    ):
                        next_front[sub_front_offset + j, :] += next_front_part[
                            sub_front_offset + i, :
                        ]
            next_front = next_front.tocsr()
            front = next_front > visited
            visited += front
            if front.count_nonzero() == 0:
                break

        def get_reachable(sub_front_idx: int) -> Set[pyformlang.finite_automaton.State]:
            sub_front_offset = sub_front_idx * other.state_count
            reachable = scipy.sparse.csr_matrix((1, self.state_count), dtype=bool)
            for i in other.final_state_indices:
                reachable += visited[sub_front_offset + i, :]
            return set(
                self.idx_to_state(i)
                for i in reachable.nonzero()[1]
                if i in self.final_state_indices
            )

        return (
            {
                self.idx_to_state(start_state_idx): get_reachable(sub_front_idx)
                for sub_front_idx, start_state_idx in enumerate(
                    self.start_state_indices
                )
            }
            if group_by_start
            else get_reachable(0)
        )
