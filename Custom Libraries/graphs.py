from copy import deepcopy

class Node:
    """A graph node.
        
    """
    
    def __init__(self, data):
        """Make a node.
        
        Args:
            data (int): Data in node.
            
        """
        
        self._data = data
    
    def get_data(self):
        """Get a node's data.
        
        Returns:
            int: Data in node.
            
        """
        
        return self._data
        
    def set_data(self, data):
        """Set a node's data.
        
        Args:
            data (int): New node data.
            
        """
        
        self._data = data
        
class Graph:
    """A basic graph.
    
    """
    
    
    def __init__(self, nodes_and_edges = []):
        """Make a graph.
        
        Args:
            nodes (list of tuple of (Node, list of Node), optional): Initial graph nodes and edges.
            
        """
        
        self._nodes_and_edges = nodes_and_edges
        
    def get_nodes(self):
        """Get all nodes.
        
        Returns:
            list: Graph nodes.
        
        """
        
        return [node for (node, edges) in nodes_and_edges]
    
    # def set_nodes(self, nodes):
    #     """Set all nodes.
    #     
    #     Args:
    #         nodes (:obj:'list' of :obj:'Node'): New graph nodes.
    #         
    #     """
    #     
    #     self._nodes = deepcopy(nodes)
    #     
    def get_node(self, index):
        """Get a node.
        
        Args:
            index (int): Index to __nodes.
            
        Returns:
            Node: Node at __nodes[index].
            
        """
        
        return self.__nodes[index][0]

   ##   def set_node(self, index, node):
    #     """Set a node.
    #     
    #     Args:
    #         index (int): Index to __nodes.
    #         node (:obj: node): New graph node.
    #         
    #     """
    #     
    #     self._nodes[index] = deepcopy(node)
        
    def get_edges(self, node):
        """Get a node's neighbors.
        
        Args:
            node (:obj:'Node'): Node whose edges to find.
            
        Returns:
            list: Neighbors of node. None otherwise.
            
        """
        
        for (graph_node, edges) in self._nodes_and_edges:
            if node is graph_node:
                return edges
        else:
            return None