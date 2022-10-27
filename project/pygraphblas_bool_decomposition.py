from typing import Generic
from typing import Iterable
from typing import Iterator
from typing import Tuple
from typing import TypeVar

import pygraphblas

__all__ = ["BoolDecomposition"]

T = TypeVar("T")


class BoolDecomposition(Generic[T]):
    def __init__(
        self, shape: Tuple[int, int], content: Iterable[Tuple[int, int, T]] = None
    ):
        self.matrices = dict()
        self.shape = shape
        matrices_as_nnz_rows_cols = dict()
        if content:
            for (i, j, element) in content:
                if element not in matrices_as_nnz_rows_cols:
                    matrices_as_nnz_rows_cols[element] = ([], [])
                matrices_as_nnz_rows_cols[element][0].append(i)
                matrices_as_nnz_rows_cols[element][1].append(j)
            for (element, matrix_as_nnz_rows_cols) in matrices_as_nnz_rows_cols.items():
                self.matrices[element] = pygraphblas.Matrix.from_lists(
                    I=matrix_as_nnz_rows_cols[0],
                    J=matrix_as_nnz_rows_cols[1],
                    nrows=shape[0],
                    ncols=shape[0],
                )

    def __iter__(self) -> Iterator[Tuple[int, int, T]]:
        return (
            (i, j, element)
            for (element, matrix) in self.matrices.items()
            for (i, j, v) in matrix.__iter__()
            if v
        )

    def kron(self, other: "BoolDecomposition[T]") -> "BoolDecomposition[T]":
        result = BoolDecomposition(
            (self.shape[0] * other.shape[0], self.shape[1] * other.shape[1])
        )
        for (element, matrix) in self.matrices.items():
            if element in other.matrices:
                result.matrices[element] = matrix.kronecker(other.matrices[element])
        return result

    def transitive_closure(self) -> pygraphblas.Matrix:
        if self.shape[0] != self.shape[1]:
            raise Exception(
                "Unable to get transitive closure for non square boolean decomposition"
            )
        result: pygraphblas.Matrix = sum(
            self.matrices.values(),
            start=pygraphblas.Matrix.identity(pygraphblas.types.BOOL, self.shape[0]),
        )
        while True:
            new = result.mxm(result, mask=result, desc=pygraphblas.descriptor.C)
            if not new.reduce_bool():
                return result
            result += new
