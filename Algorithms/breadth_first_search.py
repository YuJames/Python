"""This module provides breadth first search functionality.
    
Attributes:

Classes:
    
Functions:
    breadth_first_search
    
Todo:
    track depth
    track other stuff?
    
"""

from graphs import Graph, Node

def breadth_first_search(graph, start):
    """Traverse a graph using BFS.
    
    Args:
        graph (Graph): Graph to traverse. 
        start (Node): Starting node.
    
    Returns:
        A dictionary mapping strings to search results.
        
        {"depth": int,
         "reachable_nodes": Node list"}
         
    """
    
    # stuff to track
    visited = []
    queue = []
    
    # by default, start is part of visited and queue
    visited.append(start)
    queue.append(start)
    
    # do BFS
    while(len(queue) > 0):
        next_node = queue.pop(0)
        
        for neighbor in graph.get_edges(next_node):
            if neighbor not in visited:
                queue.append(neighbor)
        
        visited.append(next_node)
        
    # print results
    return {"reachable_nodes": visited}
    
# test
if __name__ == "__main__":
    my_graph = Graph()
    
    node1 = Node(10, 1)
    node2 = Node(13, 2)
    node3 = Node(20, 3)
    
    my_graph.add_node(node1)
    my_graph.add_edge((node2, node3))
    my_graph.add_edge((node3, node1))
    
    my_graph.print_nodes()
    my_graph.print_edges()
    
    print breadth_first_search(my_graph, node2)