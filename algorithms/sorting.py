# algorithms/sorting.py - Pure sorting algorithm generators for AlgoFlow
# NO pygame imports - clean separation of concerns
#
# Each algorithm is a Python generator that yields operation tuples.
# The visualizer consumes these and applies colors/swaps.
# This generator-as-coroutine pattern enables step-by-step execution
# without threads.


def bubble_sort(array):
    """
    Generator that yields sorting operations for bubble sort.

    Yields:
        ("compare", i, j)  - comparing indices i and j
        ("swap", i, j)     - swapping indices i and j
        ("sorted", i)      - index i is in final position
        ("done",)          - algorithm complete
    """
    n = len(array)
    for i in range(n):
        for j in range(0, n - i - 1):
            yield ("compare", j, j + 1)
            if array[j] > array[j + 1]:
                array[j], array[j + 1] = array[j + 1], array[j]
                yield ("swap", j, j + 1)
        yield ("sorted", n - i - 1)
    yield ("done",)


def selection_sort(array):
    """Generator that yields sorting operations for selection sort."""
    n = len(array)
    for i in range(n):
        min_idx = i
        for j in range(i + 1, n):
            yield ("compare", min_idx, j)
            if array[j] < array[min_idx]:
                min_idx = j
        if min_idx != i:
            array[i], array[min_idx] = array[min_idx], array[i]
            yield ("swap", i, min_idx)
        yield ("sorted", i)
    yield ("done",)


def insertion_sort(array):
    """Generator that yields sorting operations for insertion sort."""
    n = len(array)
    for i in range(1, n):
        j = i - 1
        while j >= 0:
            yield ("compare", j, j + 1)
            if array[j] > array[j + 1]:
                array[j], array[j + 1] = array[j + 1], array[j]
                yield ("swap", j, j + 1)
                j -= 1
            else:
                break
        yield ("sorted", i)
    # Mark all as sorted at the end
    for i in range(n):
        yield ("sorted", i)
    yield ("done",)


# Algorithm metadata - used by the visualizer and info panel
ALGORITHM_INFO = {
    "Bubble": {
        "name": "Bubble Sort",
        "time_best": "O(n)",
        "time_avg": "O(n\u00b2)",
        "time_worst": "O(n\u00b2)",
        "space": "O(1)",
        "stable": True,
        "generator": bubble_sort,
    },
    "Selection": {
        "name": "Selection Sort",
        "time_best": "O(n\u00b2)",
        "time_avg": "O(n\u00b2)",
        "time_worst": "O(n\u00b2)",
        "space": "O(1)",
        "stable": False,
        "generator": selection_sort,
    },
    "Insertion": {
        "name": "Insertion Sort",
        "time_best": "O(n)",
        "time_avg": "O(n\u00b2)",
        "time_worst": "O(n\u00b2)",
        "space": "O(1)",
        "stable": True,
        "generator": insertion_sort,
    },
}
