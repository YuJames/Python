"""This module provides the required classes for representing graphs.
    
Attributes:

Classes:
    Node
    Edge
    Graph
    
Functions:
    
Todo:
    Support more graph types.
    Improve size/efficiency.
    Mess with special functions (e.g. hash).
    
"""

from copy import deepcopy
# ^ when to use that?

class Node:
    """A graph node.
        
    """
    
    def __init__(self, id, data = None):
        """Make a node.
        
        Args:
            id (int): Id held by node.
            data (int): Data held by node.

        """
        
        self._data = data
        self._id = id
    
    def __eq__(self, other):
        """For == comparison.
        
        Returns:
            bool: True if equal. False if otherwise.
            
        """
        
        return (self._data == other._data and self._id == other._id)
        
    def get_data(self):
        """Get a node's data.
        
        Returns:
            int: Data in node.
            
        """
        
        return self._data
        
    
    def get_id(self):
        """Get a node's id.
        
        """
        
        return self._id
        
    def set_data(self, new_data):
        """Set a node's data.
        
        Args:
            new_data (int): New node data.
            
        """
        
        self._data = new_data
        
    def set_id(self, new_id):
        """Set a node's id.
        
        Args:
            new_id (int): New node id.
            
        """
        
        self._id = new_id

class Edge:
    """A graph edge.
    
    """
    
    def init(self, start, end, weight = None):
        self._weight = weight
        self._edge = (start, end)

    def __eq__(self, other):
        """For == comparison.
        
        Returns:
            bool: True if equal. False if otherwise.
            
        """
        
        return (self._weight == other._weight and 
                self._edge[0] == other._edge[0] and
                self._edge[1] == other._edge[1])
            
    def get_edge(self):
        """Get an edge's edge.
        
        """
        
        return self._edge
    
    def get_weight(self):
        """Get an edge's weight.
        
        """
        
        return self._weight
    
    def set_edge(self, new_edge):
        """Set an edge's edge.
        
        """
        
        self._edge = new_edge
        
    def set_weight(self, new_weight):
        """Set an edge's weight.
        
        """
        
        self._weight = new_weight
    
    def flip(self):
        """Reverse an edge.
        
        Returns:
            Edge: Reversed edge.
        """
        
        #v does this work? Check special functions
        new_edge = copy.deepcopy(self)
        new_edge.set_edge((self._edge[1], self._edge[0]))
        
        return new_edge
        
class Graph:
    """A basic graph.
    
    """
    
    
    def __init__(self, directed = False, cyclic = False):
        """Make an empty graph.
        
        Args:
            directed (bool): Is graph directed.
            cyclic (bool): Is graph cyclic.

        """
        
        self._nodes = list()
        self._edges = list()
        self._directed = directed
        self._cyclic = cyclic
    
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

    def is_edge(self, edge):
        """Check for an edge in graph.
        
        Args:
            edge (tuple of (Node, Node)): Edge to check.
            
        Return:
            bool
        
        """
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