from collections import deque
from copy import deepcopy

class Node:
    """A graph node.
        
    """
    
    def __init__(self, data, id):
        """Make a node.
        
        Args:
            data (int): Data held by node.
            id (int): Id held by node.
        """
        
        self._data = data
        self._id = id
    
    def __eq__(self, other):
        """For == comparison.
        
        Returns:
            bool: True if equal. False if otherwise.
            
        """
        
        return (self._data == other._data && self._id == other._id)
        
    def __hash__(self):
        """For hashed collections/operations.
        
        Returns:
            int: Hash value.
            
        """
        
        return hash(self._id)
        
    def get_data(self):
        """Get a node's data.
        
        Returns:
            int: Data in node.
            
        """
        
        return self._data
        
    def set_data(self, new_data):
        """Set a node's data.
        
        Args:
            new_data (int): New node data.
            
        """
        
        self._data = new_data
    
    def get_id(self):
        """Get a node's id.
        
        """
        
        return self._id
        
    def set_id(self, new_id):
        """Set a node's id.
        
        Args:
            new_id (int): New node id.
            
        """
        
        self._id = new_id
        
class Graph:
    """A basic graph.
    
    """
    
    
    def __init__(self):
        """Make an empty graph.

        """
        
        self._nodes = set()
        self._edges = list()
    
    def add_edge(self, new_edge):
        """Add an edge if it is unique to the graph's current edges.
        
        Args:
            new_edge (tuple of Node, Node): Edge to add.
            
        Returns:
            bool: True if added. False if otherwise.
            
        """
        
        None
        
    def add_node(self, new_node):
        """Add a node if its id is unique to the graph's current nodes.
        
        Args:
            new_node (Node): Node to add.
        
        Returns:
            bool: True if added. False if otherwise.
        """
        
        for node in self._nodes:
            if new_node._id == node._id:
                return False
        else:
            self._nodes.add(new_node)
            return True

    # def get_edges(self, node):
    #     """Get a node's neighbors.
    #     
    #     Args:
    #         node (Node): Node whose edges to find.
    #         
    #     Returns:
    #         list: Neighbors of node. None otherwise.
    #         
    #     """
    #     
    #     for (graph_node, edges) in self._nodes_and_edges:
    #         if node is graph_node:
    #             return edges
    #     else:
    #         return None
    #                     
    def get_node(self, id):
        """Get a node by id.
        
        Args:
            id (int): Node id to search.
            
        Returns:
            Node: Node with matching id. None otherwise
            
        """
        
        for node in self._nodes:
            if id == node.id:
                return node
        else:
            return None
                    
    def get_nodes(self):
        """Get all nodes.
        
        Returns:
            list: Graph nodes.
        
        """
        
        return self._nodes
    
