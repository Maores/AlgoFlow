# algorithms/sorting.py - Pure sorting algorithm generators for AlgoFlow
# NO pygame imports - clean separation of concerns
#
# Each algorithm is a Python generator that yields 4-tuple operation records:
#   (op_type, indices_tuple, status_msg, pointers_dict)
#
# - op_type: "compare", "swap", "set", "pivot", "sorted", "done"
# - indices_tuple: tuple of relevant indices/values
# - status_msg: human-readable play-by-play string
# - pointers_dict: variable names → array indices (positional),
#                  _-prefixed keys → raw values (non-positional)


def bubble_sort(array):
    """Generator for bubble sort with play-by-play status and pointer tracking."""
    n = len(array)
    for i in range(n):
        for j in range(0, n - i - 1):
            yield ("compare", (j, j + 1),
                   f"Comparing arr[{j}]={array[j]} and arr[{j+1}]={array[j+1]}",
                   {"j": j, "j+1": j + 1})
            if array[j] > array[j + 1]:
                yield ("swap", (j, j + 1),
                       f"Swapping {array[j]} and {array[j+1]}",
                       {"j": j, "j+1": j + 1})
                array[j], array[j + 1] = array[j + 1], array[j]
        yield ("sorted", (n - i - 1,),
               f"Position {n-i-1} is now in final place", {})
    yield ("done", (), "Sorting complete!", {})


def selection_sort(array):
    """Generator for selection sort with play-by-play status and pointer tracking."""
    n = len(array)
    for i in range(n):
        min_idx = i
        for j in range(i + 1, n):
            yield ("compare", (min_idx, j),
                   f"Checking if arr[{j}]={array[j]} < current min arr[{min_idx}]={array[min_idx]}",
                   {"i": i, "j": j, "min": min_idx})
            if array[j] < array[min_idx]:
                min_idx = j
                yield ("compare", (min_idx, j),
                       f"New minimum found: arr[{j}]={array[j]}",
                       {"i": i, "j": j, "min": min_idx})
        if min_idx != i:
            yield ("swap", (i, min_idx),
                   f"Placing minimum {array[min_idx]} at position {i}",
                   {"i": i, "min": min_idx})
            array[i], array[min_idx] = array[min_idx], array[i]
        yield ("sorted", (i,),
               f"Position {i} is now in final place", {})
    yield ("done", (), "Sorting complete!", {})


def insertion_sort(array):
    """Generator for insertion sort with play-by-play status and pointer tracking."""
    n = len(array)
    for i in range(1, n):
        key = array[i]
        j = i - 1
        while j >= 0:
            yield ("compare", (j, j + 1),
                   f"Comparing arr[{j}]={array[j]} with arr[{j+1}]={array[j+1]}",
                   {"i": i, "j": j, "_key": key})
            if array[j] > array[j + 1]:
                yield ("swap", (j, j + 1),
                       f"Shifting {array[j]} right because {array[j]} > key ({key})",
                       {"i": i, "j": j, "_key": key})
                array[j], array[j + 1] = array[j + 1], array[j]
                j -= 1
            else:
                break
        yield ("sorted", (i,),
               f"Key inserted \u2014 sorted prefix now has {i+1} elements", {})
    # Mark all as sorted at the end
    for i in range(n):
        yield ("sorted", (i,), "", {})
    yield ("done", (), "Sorting complete!", {})


def merge_sort(array):
    """
    Generator for merge sort using yield from for recursive delegation.

    Merge sort is out-of-place: it copies sub-arrays into a temp buffer,
    then writes elements back one at a time via ("set", ...).
    The visualizer handles the actual array[index] = value assignment.
    """
    yield from _merge_sort(array, 0, len(array) - 1)
    for i in range(len(array)):
        yield ("sorted", (i,), "", {})
    yield ("done", (), "Sorting complete!", {})


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
        yield ("compare", (left + i, mid + 1 + j),
               f"Comparing left[{i}]={left_copy[i]} with right[{j}]={right_copy[j]}",
               {"L": left + i, "R": mid + 1 + j, "k": k})
        if left_copy[i] <= right_copy[j]:
            yield ("set", (k, left_copy[i]),
                   f"Writing {left_copy[i]} to position {k} from left subarray",
                   {"L": left + i, "k": k})
            i += 1
        else:
            yield ("set", (k, right_copy[j]),
                   f"Writing {right_copy[j]} to position {k} from right subarray",
                   {"R": mid + 1 + j, "k": k})
            j += 1
        k += 1

    # Remaining elements from left sub-array
    while i < len(left_copy):
        yield ("set", (k, left_copy[i]),
               f"Writing {left_copy[i]} to position {k} from left subarray",
               {"L": left + i, "k": k})
        i += 1
        k += 1

    # Remaining elements from right sub-array
    while j < len(right_copy):
        yield ("set", (k, right_copy[j]),
               f"Writing {right_copy[j]} to position {k} from right subarray",
               {"R": mid + 1 + j, "k": k})
        j += 1
        k += 1


def quick_sort(array):
    """
    Generator for quick sort using yield from for recursive delegation.

    Highlights the pivot element with ("pivot", ...) and marks each
    partition's final pivot position with ("sorted", ...).
    """
    yield from _quick_sort(array, 0, len(array) - 1)
    for i in range(len(array)):
        yield ("sorted", (i,), "", {})
    yield ("done", (), "Sorting complete!", {})


def _quick_sort(array, low, high):
    if low < high:
        pivot_idx = yield from _partition(array, low, high)
        yield ("sorted", (pivot_idx,),
               f"Pivot {pivot_idx} in final position", {})
        yield from _quick_sort(array, low, pivot_idx - 1)
        yield from _quick_sort(array, pivot_idx + 1, high)


def _partition(array, low, high):
    """Lomuto partition scheme \u2014 pivot is the last element."""
    pivot = array[high]
    yield ("pivot", (high,),
           f"Pivot = arr[{high}] = {pivot}",
           {"pivot": high})
    i = low - 1
    for j in range(low, high):
        yield ("compare", (j, high),
               f"Comparing arr[{j}]={array[j]} with pivot {pivot}",
               {"pivot": high, "i": i + 1, "j": j})
        if array[j] <= pivot:
            i += 1
            if i != j:
                yield ("swap", (i, j),
                       f"Swapping arr[{i}] and arr[{j}], extending partition",
                       {"pivot": high, "i": i, "j": j})
                array[i], array[j] = array[j], array[i]
    yield ("swap", (i + 1, high),
           f"Placing pivot at position {i+1}",
           {"pivot": i + 1})
    array[i + 1], array[high] = array[high], array[i + 1]
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
        "time_worst": "O(n\u00b2)",
        "space": "O(log n)",
        "stable": False,
        "generator": quick_sort,
    },
}
