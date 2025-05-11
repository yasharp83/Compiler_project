"""
Symbol table for tracking identifiers and their attributes.
"""
import logging
from typing import Dict, List, Optional, Set, Any

from src.common.language_specs import KEYWORDS


logger = logging.getLogger(__name__)


class SymbolTableError(Exception):
    """Exception raised for symbol table errors."""
    pass


class Symbol:
    """
    Represents a symbol in the symbol table.
    
    Attributes:
        name: The name of the symbol
        kind: The kind of symbol (variable, function, etc.)
        type: The data type of the symbol (int, void, etc.)
        scope: The scope where the symbol is defined
        address: Memory address or offset (optional)
        is_array: Whether the symbol is an array
        array_size: Size of the array if is_array is True
    """
    def __init__(
        self, 
        name: str, 
        kind: str = "variable", 
        type_name: str = "int",
        scope: str = "global",
        address: Optional[int] = None,
        is_array: bool = False,
        array_size: Optional[int] = None
    ):
        self.name = name
        self.kind = kind
        self.type = type_name
        self.scope = scope
        self.address = address
        self.is_array = is_array
        self.array_size = array_size
    
    def __str__(self) -> str:
        """String representation of the symbol."""
        result = self.name
        if self.is_array and self.array_size is not None:
            result += f"[{self.array_size}]"
        return result
    
    def __repr__(self) -> str:
        """Detailed representation of the symbol."""
        array_info = f", array_size={self.array_size}" if self.is_array else ""
        return (f"Symbol(name='{self.name}', kind='{self.kind}', "
                f"type='{self.type}', scope='{self.scope}'{array_info})")


class SymbolTable:
    """
    Symbol table for tracking identifiers.
    Manages both keywords and user-defined identifiers.
    """
    
    def __init__(self, file_path: str = "symbol_table.txt"):
        """
        Initialize a symbol table.
        
        Args:
            file_path: Path to the symbol table file
        """
        self.file_path = file_path
        self.symbols: List[Symbol] = []
        self.symbol_index: Dict[str, int] = {}  # Maps symbol names to their index
        
        # Initialize with keywords
        for keyword in KEYWORDS:
            self._add_symbol(Symbol(name=keyword, kind="keyword"))
        
        self._ensure_file_exists()
    
    def _ensure_file_exists(self) -> None:
        """Ensure the symbol table file exists."""
        try:
            with open(self.file_path, 'a'):
                pass
        except IOError as e:
            logger.error(f"Error creating symbol table file {self.file_path}: {e}")
            raise SymbolTableError(f"Could not create symbol table file: {e}")
    
    def _add_symbol(self, symbol: Symbol) -> bool:
        """
        Add a symbol to the table. Private method for internal use.
        
        Args:
            symbol: The symbol to add
            
        Returns:
            True if the symbol was added, False if it already exists
        """
        if symbol.name in self.symbol_index:
            return False
        
        self.symbol_index[symbol.name] = len(self.symbols)
        self.symbols.append(symbol)
        return True
    
    def add(self, name: str, **kwargs) -> bool:
        """
        Add a symbol to the table.
        
        Args:
            name: The name of the symbol
            **kwargs: Additional symbol attributes
            
        Returns:
            True if the symbol was added, False if it already exists
        """
        if name in self.symbol_index:
            return False
        
        symbol = Symbol(name=name, **kwargs)
        return self._add_symbol(symbol)
    
    def lookup(self, name: str) -> Optional[Symbol]:
        """
        Look up a symbol by name.
        
        Args:
            name: The name to look up
            
        Returns:
            The Symbol object if found, None otherwise
        """
        if name in self.symbol_index:
            return self.symbols[self.symbol_index[name]]
        return None
    
    def write_to_file(self) -> None:
        """Write the symbol table to the file."""
        try:
            with open(self.file_path, 'w') as f:
                for idx, symbol in enumerate(self.symbols):
                    f.write(f"{idx+1}.\t{symbol}\n")
        except IOError as e:
            logger.error(f"Error writing to symbol table file {self.file_path}: {e}")
            raise SymbolTableError(f"Could not write to symbol table file: {e}")
    
    def read_from_file(self, file_path: Optional[str] = None) -> None:
        """
        Read the symbol table from a file.
        
        Args:
            file_path: The file to read from, defaults to self.file_path
        """
        if file_path is None:
            file_path = self.file_path
        
        # Keep keywords but reset other symbols
        self.symbols = [symbol for symbol in self.symbols if symbol.kind == "keyword"]
        self.symbol_index = {symbol.name: idx for idx, symbol in enumerate(self.symbols)}
        
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    if not line.strip():
                        continue
                    
                    parts = line.strip().split('\t')
                    if len(parts) < 2:
                        continue
                    
                    # Extract symbol name (simple for now)
                    symbol_name = parts[1].strip()
                    
                    # Skip if it's a keyword or already exists
                    if symbol_name in KEYWORDS or symbol_name in self.symbol_index:
                        continue
                    
                    # Parse array notation if present
                    is_array = False
                    array_size = None
                    
                    if '[' in symbol_name and ']' in symbol_name:
                        name_parts = symbol_name.split('[')
                        symbol_name = name_parts[0].strip()
                        size_str = name_parts[1].split(']')[0].strip()
                        try:
                            array_size = int(size_str)
                            is_array = True
                        except ValueError:
                            pass
                    
                    self.add(
                        name=symbol_name,
                        is_array=is_array,
                        array_size=array_size
                    )
        except IOError as e:
            logger.error(f"Error reading symbol table file {file_path}: {e}")
            raise SymbolTableError(f"Could not read symbol table file: {e}")
    
    def __iter__(self):
        """Iterator for symbols."""
        return iter(self.symbols)
    
    def __len__(self) -> int:
        """Number of symbols in the table."""
        return len(self.symbols) 