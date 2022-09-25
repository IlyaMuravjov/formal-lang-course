from typing import Callable
from typing import Dict
from typing import Set
from typing import Tuple

from pyformlang.finite_automaton import NondeterministicFiniteAutomaton as NFA
from pyformlang.finite_automaton import State
from pyformlang.finite_automaton import Symbol

from project.bool_decomposition import BoolDecomposition

__all__ = ["BoolDecomposedNFA"]


class BoolDecomposedNFA:
    state_count: int
    idx_to_state: Callable[[int], State]
    adj_bool_decomposition: BoolDecomposition[Symbol]
    start_state_indices: Set[int]
    final_state_indices: Set[int]

    def __init__(
        self,
        state_count: int,
        idx_to_state: Callable[[int], State],
        adj_bool_decomposition: BoolDecomposition[Symbol],
        start_state_indices: Set[int],
        final_state_indices: Set[int],
    ):
        self.state_count = state_count
        self.idx_to_state = idx_to_state
        self.adj_bool_decomposition = adj_bool_decomposition
        self.start_state_indices = start_state_indices
        self.final_state_indices = final_state_indices

    @staticmethod
    def from_nfa(nfa: NFA) -> "BoolDecomposedNFA":
        idx_to_state_dict: Dict[int, State] = dict()
        state_to_idx_dict: Dict[State, int] = dict()
        for (idx, state) in enumerate(nfa.states):
            idx_to_state_dict[idx] = state
            state_to_idx_dict[state] = idx
        adj_bool_decomposition = BoolDecomposition(
            len(nfa.states),
            content=(
                (state_to_idx_dict[source], state_to_idx_dict[target], symbol)
                for (source, symbol, target) in nfa
            ),
        )
        return BoolDecomposedNFA(
            state_count=len(nfa.states),
            idx_to_state=idx_to_state_dict.__getitem__,
            adj_bool_decomposition=adj_bool_decomposition,
            start_state_indices=set(
                state_to_idx_dict[state] for state in nfa.start_states
            ),
            final_state_indices=set(
                state_to_idx_dict[state] for state in nfa.final_states
            ),
        )

    def to_nfa(self) -> NFA:
        nfa = NFA()
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
            idx_to_state=lambda i: State(
                (
                    self.idx_to_state(i // other.state_count),
                    (other.idx_to_state(i % other.state_count)),
                )
            ),
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

    def get_reachable(self) -> Set[Tuple[State, State]]:
        return set(
            (self.idx_to_state(source), self.idx_to_state(target))
            for (source, target) in (
                zip(*self.adj_bool_decomposition.transitive_closure().nonzero())
            )
            if source in self.start_state_indices and target in self.final_state_indices
        )
