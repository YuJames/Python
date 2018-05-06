#!/usr/bin/env python3

"""Sorting Algorithms.

This module provides sorting functionality.
    
ToDo:
    ~~~~NOW~~~~
    ~~~~CONSIDERATION~~~~
    include average and best case
    make solution more pythonic
    ~~~~PERIODICALLY~~~~
    improve docstrings
    improve modularity (globals, fxns, variables)
    improve naming
    return vs return None vs nothing
    
"""

def bubble_sort(data):
    """Sort a list of unique numbers in ascending order using bubble sort. O(n^2).
    
    The process includes repeatedly iterating through a list and swapping adjacent elements. 
    
    Args:
        data: data to sort (list of int)
    Returns:
        sorted list
    """
    
    n = len(data)
    sorted_data = data[:]
    is_ordered = True
    
    # make up to n - 1 iterations
    for i in range(n - 1):
        # ignore the ordered, last values
        for j in range(n - 1 - i):
            # compare 2 adjacent values
            if sorted_data[j] > sorted_data[j+1]:
                sorted_data[j], sorted_data[j+1] = sorted_data[j+1], sorted_data[j]
                is_ordered = False

        # terminate early
        if is_ordered is True:
            break
        else:
            is_ordered = True
    
    return sorted_data

def quick_sort(data):
    """Sort a list of unique numbers in ascending order using quick sort. O(n^2).
    
    The process includes recursively splitting a list into a pivot, smaller side, and larger side.
    
    Args:
        data: data to sort (list of int)
    Returns:
        sorted list
    """
    
    n = len(data)
    
    # terminate early
    if n < 2:
        return data
    
    pivot = data[0]

    # organize data around pivot
    left = [value for i, value in enumerate(data[1:]) if value < pivot]
    right = [value for i, value in enumerate(data[1:]) if value > pivot]
    # make recursive calls
    sorted_left = quick_sort(left)
    sorted_right = quick_sort(right)
        
    # combine sorted data with pivot
    sorted_data = sorted_left
    sorted_data.append(pivot)
    sorted_data.extend(sorted_right)
    
    return sorted_data

def insert_sort(data):
    """Sort a list of unique numbers in ascending order using insert sort. O(n^2).
    
    The process includes iterating through a list and ordering elements as they're visited.
    
    Args:
        data: data to sort (list of int)
    Returns:
        sorted list
    """
    
    sorted_data = data[:]
    
    for i, value in enumerate(sorted_data):
        print("ITERATION: {}".format(i))
        for j in range(i):
            moving_index = i - 1 - j
            if sorted_data[moving_index] > value:
                sorted_data[moving_index + 1] = sorted_data[moving_index]
                sorted_data[moving_index] = value
    
    return sorted_data

a = [1, -1, 8, 240, -8]
b = [1, 2]
# print(a)
# b = bubble_sort(a)
# print(a)
print(insert_sort(a))