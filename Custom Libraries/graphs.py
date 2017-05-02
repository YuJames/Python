"""This module provides the required classes for representing graphs.
    
Attributes:

Classes:
    Node
    Graph
    
Functions:
    
Todo:
    Support more graph types.
    
"""

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
        
        return (self._data == other._data and self._id == other._id)
        
    # def __hash__(self):
    #     """For hashed collections/operations.
    #     
    #     Returns:
    #         int: Hash value.
    #         
    #     """
    #     
    #     return hash(self._id)
        
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
        
        self._nodes = list()
        self._edges = list()
    
    def add_edge(self, new_edge):
        """Add an edge if it is unique to the graph's current edges.
        
        Args:
            new_edge (tuple of Node, Node): Edge to add.
            
        Returns:
            bool: True if added. False if otherwise.
            
        """

        # arg breakdown
        from_node = new_edge[0]
        to_node = new_edge[1]
        
        # add nodes if not in nodes container
        self.add_node(from_node)
        self.add_node(to_node)
        
        # add edge if not in edges container
        for (start, end) in self._edges:
            if start == from_node:
                if to_node not in end:
                    end.append(to_node)
                    return True
                    
        return False
        
    def add_node(self, new_node):
        """Add a node if its id is unique to the graph's current nodes.
        
        Args:
            new_node (Node): Node to add.
        
        Returns:
            bool: True if added. False if otherwise.
        """
        
        # check presence in nodes list
        # absense in nodes list implies absense in edges list
        if new_node not in self._nodes:
            self._nodes.append(new_node)
            self._edges.append((new_node, list()))
            return True
        else:
            return False

    def get_edges(self, node):
        """Get a node's neighbors.
        
        Args:
            node (Node): Node whose edges to find.
            
        Returns:
            list: Neighbors of node. None otherwise.
            
        """
        
        for (start, end) in self._edges:
            if start == node:
                return end
        else:
            return None
                        
    def get_node(self, id):
        """Get a node by id.
        
        Args:
            id (int): Node id to search.
            
        Returns:
            Node: Node with matching id. None otherwise
            
        """
        
        for node in self._nodes:
            if id == node._id:
                return node
        else:
            return None
                    
    def get_nodes(self):
        """Get all nodes.
        
        Returns:
            list: Graph nodes.
        
        """
        
        return self._nodes
    
    def print_nodes(self):
        """Print all nodes.
        
        """
        
        print "~~~Nodes~~~"
        for node in self._nodes:
            print "Node id: {}".format(node.get_id())
            print "  data: {}".format(node.get_data())

    def print_edges(self):
        """Print all edges.
        
        """
        
        print "~~~Edges~~~"
        for (start, end) in self._edges:
            print "start Node id: {}".format(start.get_id())
            for end_node in end:
                print "  end Node id: {}".format(end_node.get_id())