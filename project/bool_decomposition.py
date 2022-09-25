from typing import Dict
from typing import Generic
from typing import Iterable
from typing import Iterator
from typing import Tuple
from typing import TypeVar

from scipy.sparse import csr_matrix
from scipy.sparse import dok_matrix
from scipy.sparse import identity
from scipy.sparse import kron

__all__ = ["BoolDecomposition"]

T = TypeVar("T")


class BoolDecomposition(Generic[T]):
    matrices: Dict[T, csr_matrix]
    size: int

    def __init__(self, size: int, content: Iterable[Tuple[int, int, T]] = None):
        self.matrices = dict()
        self.size = size
        dok_matrices = dict()
        if content:
            for (i, j, elm) in content:
                if elm not in dok_matrices:
                    dok_matrices[elm] = dok_matrix((self.size, self.size), dtype=bool)
                dok_matrices[elm][i, j] = True
            for (elm, matrix) in dok_matrices.items():
                self.matrices[elm] = matrix.tocsr()

    def __iter__(self) -> Iterator[Tuple[int, int, T]]:
        return (
            (i, j, elm)
            for (elm, matrix) in self.matrices.items()
            for (i, j) in (zip(*matrix.nonzero()))
        )

    def kron(self, other: "BoolDecomposition[T]") -> "BoolDecomposition[T]":
        result = BoolDecomposition(self.size * other.size)
        for (elm, matrix) in self.matrices.items():
            if elm in other.matrices:
                result.matrices[elm] = kron(matrix, other.matrices[elm], format="csr")
        return result

    def transitive_closure(self) -> csr_matrix:
        result: csr_matrix = sum(
            self.matrices.values(),
            start=identity(self.size, dtype=bool, format="csr"),
        )
        prev_non_zeros = 0
        non_zeros = result.count_nonzero()
        while prev_non_zeros != non_zeros:
            result += result @ result
            prev_non_zeros = non_zeros
            non_zeros = result.count_nonzero()
        return result
