"""
Parse tree for representing the syntax structure of the program.
"""
import logging
from typing import List, Optional, Dict, Any


logger = logging.getLogger(__name__)


class ParseTreeNode:
    """
    Node in a parse tree.
    """
    def __init__(self, name: str, level: int = 0):
        """
        Initialize a parse tree node.
        
        Args:
            name: Name of the node
            level: Indentation level in the tree
        """
        self.name = name
        self.level = level
        self.children: List['ParseTreeNode'] = []
    
    def add_child(self, child: 'ParseTreeNode') -> None:
        """
        Add a child node.
        
        Args:
            child: Child node to add
        """
        self.children.append(child)
    
    def __str__(self) -> str:
        """String representation of the node."""
        return self.name


class ParseTree:
    """
    Parse tree for representing the syntactic structure of a program.
    """
    def __init__(self, file_path: str = "parse_tree.txt"):
        """
        Initialize a parse tree.
        
        Args:
            file_path: Path to the output file
        """
        self.file_path = file_path
        self.root: Optional[ParseTreeNode] = None
        self.nodes: List[ParseTreeNode] = []
    
    def add_node(self, node: ParseTreeNode) -> None:
        """
        Add a node to the parse tree.
        
        Args:
            node: Node to add
        """
        self.nodes.append(node)
        
        # Set as root if this is the first node
        if not self.root and node.level == 0:
            self.root = node
    
    def write_to_file(self) -> None:
        """Write the parse tree to the output file."""
        try:
            with open(self.file_path, 'w') as f:
                for node in self.nodes:
                    # Add indentation
                    indent = "  " * node.level
                    f.write(f"{indent}{node}\n")
        except IOError as e:
            logger.error(f"Error writing parse tree to file {self.file_path}: {e}")
            raise
    
    def get_nodes_at_level(self, level: int) -> List[ParseTreeNode]:
        """
        Get all nodes at a specific level.
        
        Args:
            level: The level to get nodes from
            
        Returns:
            List of nodes at the specified level
        """
        return [node for node in self.nodes if node.level == level]
    
    def get_node_by_index(self, index: int) -> Optional[ParseTreeNode]:
        """
        Get a node by its index in the node list.
        
        Args:
            index: Index of the node
            
        Returns:
            The node at the specified index, or None if out of bounds
        """
        if 0 <= index < len(self.nodes):
            return self.nodes[index]
        return None
    
    def __len__(self) -> int:
        """Get the number of nodes in the tree."""
        return len(self.nodes)
    
    def __str__(self) -> str:
        """String representation of the parse tree."""
        if not self.root:
            return "Empty parse tree"
        return f"Parse tree with root: {self.root.name}" 