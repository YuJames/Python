#!/usr/bin/env python

"""This module provides the required classes for representing graphs.
    
Attributes:

Classes:
    Node
    Edge
    Graph
    
Functions:
    
Todo:
    Mess with special functions (e.g. hash, etc)
    improve consistency (e.g. naming, etc)
    Document time complexities
    Improve size/efficiency
    make tests
    Support more graph types?
    
"""

from copy import deepcopy
# ^ when to use that?
# check if need special function, and time complexity

class Node:
    """A graph node.
        
    """
    
    def __init__(self, param_id, param_data = None):
        """Make a node. O(1).
        
        Args:
            param_id (int): Id of new node.
            param_data (int): Data of new node.

        """
        
        self._data = param_data
        self._id = param_id
    
    def __eq__(self, other):
        """For == comparison. O(1).
        
        Returns:
            bool: True if equal. False if otherwise.
            
        """
        
        #debug
        print "Node: __eq__"
        
        return (self._data == other._data and self._id == other._id)
        
    def __ne__(self, other):
        """For != comparison. O(1).
        
        Returns:
            bool: True if inequal. False if otherwise.
            
        """
        
        return not (self.__eq__)
            
    def get_data(self):
        """Get a node's data. O(1).
        
        Returns:
            int: Data in node.
            
        """
        
        return self._data
        
    
    def get_id(self):
        """Get a node's id. O(1).
        
        """
        
        return self._id
        
    def set_data(self, param_data):
        """Set a node's data. O(1).
        
        Args:
            param_data (int): New node data.
            
        """
        
        self._data = param_data
        
    def set_id(self, param_id):
        """Set a node's id. O(1).
        
        Args:
            param_id (int): New node id.
            
        """
        
        self._id = param_id

class Edge:
    """A graph edge.
    
    """
    
    def __init__(self, param_start, param_end, param_weight = None):
        """Make an edge. O(1).
        
        Args:
            param_start (Node): Starting node of new Edge.
            param_end (Node): Ending node of new Edge.
            param_weight (int): Edge weight of new Edge.
        
        """
        
        self._weight = param_weight
        self._nodes = (param_start, param_end)

    def __eq__(self, other):
        """For == comparison. O(1).
        
        Returns:
            bool: True if equal. False if otherwise.
            
        """
        
        #debug
        print "Edge: =="
        
        return (self._weight == other._weight and 
                self._nodes[0] == other._nodes[0] and
                self._nodes[1] == other._nodes[1])

    def __ne__(self, other):
        """For != comparison. O(1).
        
        Returns:
            bool: True if inequal. False if otherwise.
            
        """
        
        #debug
        print "Edge: !="
        
        return not self.__eq__(other)
                    
    def get_nodes(self):
        """Get an edge's nodes. O(1).
        
        """
        
        return self._nodes
    
    def get_weight(self):
        """Get an edge's weight. O(1).
        
        """
        
        return self._weight
    
    def set_edge(self, new_edge):
        """Set an edge's nodes. O(1).
        
        """
        
        self._nodes = new_edge
        
    def set_weight(self, new_weight):
        """Set an edge's weight. O(1).
        
        """
        
        self._weight = new_weight
    
    def flip(self):
        """Reverse an edge.
        
        Returns:
            Edge: Copy of reversed edge.
        """
        
        # does this work? Check special functions
        new_edge = deepcopy(self)
        new_edge.set_edge((self._nodes[1], self._nodes[0]))
        
        return new_edge
        
class Graph:
    """A graph of Nodes and Edges.
    
    """
    
    
    def __init__(self, param_directed = False):
        """Make an empty graph. O(1).
        
        Args:
            param_directed (bool): Is graph directed.

        """
        
        self._nodes = list()
        self._edges = list()
        self._directed = param_directed
        
    def add_node(self, param_node):
        """Add a node if its id is unique to the graph's current nodes. O(V).
        
        Args:
            param_node (Node): Node to add.
        
        Returns:
            bool: True if added. False if otherwise.
        """
        
        # check presence in nodes list
        for node in self._nodes:
            if node.get_id() == param_node.get_id():
                return False
        
        # add to nodes list and edges list
        # absense in nodes list implies absense in edges list
        self._nodes.append(param_node)
        self._edges.append((param_node, list()))
        return True
                        
    def add_edge(self, param_edge):
        """Add an edge if it is unique to the graph's current edges.
        
        Args:
            param_edge (Edge): Edge to add.
            
        Returns:
            bool: True if added. False if otherwise.
            
        """
        
        # all edges to add
        edges_to_add = [param_edge]
        # account for undirected graph
        if not self._directed:
            edges_to_add.append(param_edge.flip())
            
        # add nodes if not in nodes container
        self.add_node(param_edge.get_nodes()[0])
        #debug
        print "add second"
        self.add_node(param_edge.get_nodes()[1])
        
        #debug
        print "check edges"
        
        # add edge if not in edges container
        for (node, edges) in self._edges:
            for edge_to_add in edges_to_add:
                if node == edge_to_add.get_nodes()[0] and edge_to_add not in edges:
                    edges.append(edge_to_add)

        return False
       
    def get_nodes(self):
        """Get all nodes. O(1).
        
        Returns:
            list: Graph nodes.
        
        """
        
        return self._nodes
            
    def get_edges(self, param_node):
        """Get a node's edges. O(V).
        
        Args:
            param_node (Node): Node whose edges to find.
            
        Returns:
            list: Edges. None if otherwise.
            
        """
        
        for (node, edges) in self._edges:
            if node == param_node:
                return edges
        else:
            return None
                        
    def get_node(self, param_id):
        """Get a node by id. O(V).
        
        Args:
            param_id (int): Node id to search.
            
        Returns:
            Node: Node with matching id. None if otherwise.
            
        """
        
        for node in self._nodes:
            if node.get_id() == param_id:
                return node
        else:
            return None

    def is_node(self, param_node):
        """Check for a node in graph.
        
        Args:
            param_node (Node): Node to check.
        
        Returns:
            bool: True if in graph. False if otherwise.
        """
        
        for node in self._nodes:
            if node == param_node:
                return True
                
        return False
        
    def is_edge(self, param_edge):
        """Check for an edge in graph.
        
        Args:
            param_edge (Edge): Edge to check.
            
        Return:
            bool: True if edge in graph. False if otherwise.
        
        """
        
        # possible edges
        edges_to_check = self.get_edges(param_edge.get_nodes()[0])
        
        # end early
        if edges_to_check is None or len(edges_to_check) == 0:
            return False
        
        # check edges
        if param_edge in edges_to_check:
            return True
        else:
            return False
             
    def is_cyclic(self):
        """Check if the graph is cyclic. O(V + E)
        
        What technique is this?
        """
        
        # nodes where a search has started from
        starting_nodes = []
        
        def find_cycle(start, ignore = None):
            """Recursively, find a cycle in a graph starting from a node.
            
            Args:
                start (Node): Starting node.
                ignore (Node): Node neighbor to ignore in an undirected graph.
                
            """
            
            # already performed recursive search starting here
            if start in starting_nodes:
                return False
            
            starting_nodes.append(start)
            for edge in self.get_edges(start):
                neighbor_node = edge.get_nodes()[1]
                # found cycle in a directed graph
                if self._directed and (neighbor_node in starting_nodes or find_cycle(neighbor_node)):
                    return True
                elif not self._directed:
                    # found candidate for cycle in an undirected graph
                    if (neighbor_node in starting_nodes):
                        # also is not backtracking in the path so far
                        if neighbor_node is not ignore:
                            return True
                    # found cycle later down the path
                    elif find_cycle(neighbor_node, ignore = start):
                        return True
            return False
        
        return any(find_cycle(node) for node in self._nodes)
        
    def print_nodes(self):
        """Print all nodes. O(V).
        
        """
        
        print "~~~Nodes~~~"
        for node in self._nodes:
            print "Node id: {}".format(node.get_id())
            print "  data: {}".format(node.get_data())

    def print_edges(self):
        """Print all edges. O(V + E).
        
        """
        
        print "~~~Edges~~~"
        for (node, edges) in self._edges:
            print "start Node id: {}".format(node.get_id())
            for edge in edges:
                print "  end Node id: {}".format(edge.get_nodes()[1].get_id())
                
                
# test
if __name__ == "__main__":
    # make graph
    graph1 = Graph(param_directed = True)
    # add edges
    node1 = Node(1, 7)
    node2 = Node(2, 15)
    edge12_1 = Edge(node1, node2)
    edge12_2 = Edge(node1, node2)
    print id(edge12_1)
    print id(edge12_2)
    graph1.add_edge(edge12)
    print "wut"
    print graph1.is_edge(edge12_1)
    print graph1.is_edge(edge12_2)
    
    