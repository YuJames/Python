import graphs

def breadth_first_search(graph, start):
    """Traverse a graph using BFS.
    
    Args:
        graph (Graph): Graph to traverse. 
        start (int): Starting node's index.
    
    """
    
    # stuff to track
    visited = []
    queue = []
    
    # by default, start is part of visited and queue
    visited.append(start)
    queue.append(start)
    
    # do BFS
    while(True):
        if len(queue) > 0:
            next_node = queue.pop(0)
            edges = 
        else:
            break
        
    # print results
    
# test
