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


def merge_sort(array):
    """
    Generator for merge sort using yield from for recursive delegation.

    Merge sort is out-of-place: it copies sub-arrays into a temp buffer,
    then writes elements back one at a time via ("set", index, value).
    The visualizer handles the actual array[index] = value assignment.
    """
    yield from _merge_sort(array, 0, len(array) - 1)
    for i in range(len(array)):
        yield ("sorted", i)
    yield ("done",)


def _merge_sort(array, left, right):
    if left >= right:
        return
    mid = (left + right) // 2
    yield from _merge_sort(array, left, mid)
    yield from _merge_sort(array, mid + 1, right)
    yield from _merge(array, left, mid, right)


def _merge(array, left, mid, right):
    """Merge two sorted sub-arrays array[left..mid] and array[mid+1..right]."""
    left_copy = array[left:mid + 1]
    right_copy = array[mid + 1:right + 1]
    i = j = 0
    k = left

    while i < len(left_copy) and j < len(right_copy):
        # Highlight the two elements being compared from each sub-array
        yield ("compare", left + i, mid + 1 + j)
        if left_copy[i] <= right_copy[j]:
            yield ("set", k, left_copy[i])
            i += 1
        else:
            yield ("set", k, right_copy[j])
            j += 1
        k += 1

    # Remaining elements from left sub-array
    while i < len(left_copy):
        yield ("set", k, left_copy[i])
        i += 1
        k += 1

    # Remaining elements from right sub-array
    while j < len(right_copy):
        yield ("set", k, right_copy[j])
        j += 1
        k += 1


def quick_sort(array):
    """
    Generator for quick sort using yield from for recursive delegation.

    Highlights the pivot element with ("pivot", index) and marks each
    partition's final pivot position with ("sorted", index).
    """
    yield from _quick_sort(array, 0, len(array) - 1)
    for i in range(len(array)):
        yield ("sorted", i)
    yield ("done",)


def _quick_sort(array, low, high):
    if low < high:
        pivot_idx = yield from _partition(array, low, high)
        yield ("sorted", pivot_idx)
        yield from _quick_sort(array, low, pivot_idx - 1)
        yield from _quick_sort(array, pivot_idx + 1, high)


def _partition(array, low, high):
    """Lomuto partition scheme — pivot is the last element."""
    pivot = array[high]
    yield ("pivot", high)
    i = low - 1
    for j in range(low, high):
        yield ("compare", j, high)
        if array[j] <= pivot:
            i += 1
            if i != j:
                array[i], array[j] = array[j], array[i]
                yield ("swap", i, j)
    array[i + 1], array[high] = array[high], array[i + 1]
    if i + 1 != high:
        yield ("swap", i + 1, high)
    return i + 1


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
    "Merge": {
        "name": "Merge Sort",
        "time_best": "O(n log n)",
        "time_avg": "O(n log n)",
        "time_worst": "O(n log n)",
        "space": "O(n)",
        "stable": True,
        "generator": merge_sort,
    },
    "Quick": {
        "name": "Quick Sort",
        "time_best": "O(n log n)",
        "time_avg": "O(n log n)",
        "time_worst": "O(n²)",
        "space": "O(log n)",
        "stable": False,
        "generator": quick_sort,
    },
}
