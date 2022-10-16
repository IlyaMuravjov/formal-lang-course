from collections import defaultdict
from typing import Generic
from typing import Iterable
from typing import Iterator
from typing import Tuple
from typing import TypeVar

import scipy

__all__ = ["BoolDecomposition"]

T = TypeVar("T")


class BoolDecomposition(Generic[T]):
    def __init__(
        self, shape: Tuple[int, int], content: Iterable[Tuple[int, int, T]] = None
    ):
        self.matrices = defaultdict(lambda: scipy.sparse.csr_matrix(shape))
        self.shape = shape
        dok_matrices = dict()
        if content:
            for (i, j, element) in content:
                if element not in dok_matrices:
                    dok_matrices[element] = scipy.sparse.dok_matrix(
                        self.shape, dtype=bool
                    )
                dok_matrices[element][i, j] = True
            for (element, matrix) in dok_matrices.items():
                self.matrices[element] = matrix.tocsr()

    def __iter__(self) -> Iterator[Tuple[int, int, T]]:
        return (
            (i, j, element)
            for (element, matrix) in self.matrices.items()
            for (i, j) in (zip(*matrix.nonzero()))
        )

    def __getitem__(self, element: T) -> scipy.sparse.csr_matrix:
        return self.matrices[element]

    def __setitem__(self, element: T, matrix: scipy.sparse.csr_matrix):
        self.matrices[element] = matrix

    def count_nonzero(self) -> int:
        return sum(matrix.count_nonzero() for matrix in self.matrices.values())

    def kron(self, other: "BoolDecomposition[T]") -> "BoolDecomposition[T]":
        result = BoolDecomposition(
            (self.shape[0] * other.shape[0], self.shape[1] * other.shape[1])
        )
        for (element, matrix) in self.matrices.items():
            if element in other.matrices:
                result.matrices[element] = scipy.sparse.kron(
                    matrix, other.matrices[element], format="csr"
                )
        return result

    def transitive_closure(self) -> scipy.sparse.csr_matrix:
        if self.shape[0] != self.shape[1]:
            raise Exception(
                "Unable to get transitive closure for non square boolean decomposition"
            )
        result: scipy.sparse.csr_matrix = sum(
            self.matrices.values(),
            start=scipy.sparse.identity(self.shape[0], dtype=bool, format="csr"),
        )
        prev_non_zeros = 0
        non_zeros = result.count_nonzero()
        while prev_non_zeros != non_zeros:
            result += result @ result
            prev_non_zeros = non_zeros
            non_zeros = result.count_nonzero()
        return result
