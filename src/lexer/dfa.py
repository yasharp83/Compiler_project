"""
DFA (Deterministic Finite Automaton) for lexical analysis.
"""
from enum import Enum, auto
from typing import Dict, List, Set, Tuple, Optional, Any, Callable, Union
from dataclasses import dataclass


class StateType(Enum):
    """Types of states in the DFA."""
    START = auto()
    NORMAL = auto()
    ACCEPT = auto()
    TRAP = auto()


class TokenClass(Enum):
    """Classes of tokens recognized by the DFA."""
    UNKNOWN = auto()
    NUMBER = auto()
    ID = auto()
    KEYWORD = auto()
    SYMBOL = auto()
    WHITESPACE = auto()
    COMMENT = auto()
    ERROR = auto()


@dataclass
class DFAState:
    """
    Represents a state in the DFA.
    
    Attributes:
        id: Unique state identifier
        type: Type of state (START, NORMAL, ACCEPT, TRAP)
        token_class: Class of token recognized at this state (if ACCEPT)
        error_type: Type of error (if this is an error state)
    """
    id: int
    type: StateType
    token_class: TokenClass = TokenClass.UNKNOWN
    error_type: Optional[str] = None
    
    @property
    def is_accept(self) -> bool:
        """Check if this is an accept state."""
        return self.type == StateType.ACCEPT
    
    @property
    def is_trap(self) -> bool:
        """Check if this is a trap state."""
        return self.type == StateType.TRAP
    
    def __str__(self) -> str:
        result = f"State({self.id}, {self.type.name}"
        if self.token_class != TokenClass.UNKNOWN:
            result += f", {self.token_class.name}"
        if self.error_type:
            result += f", {self.error_type}"
        result += ")"
        return result


class DFA:
    """
    Deterministic Finite Automaton for lexical analysis.
    
    Implements a DFA that recognizes tokens in the language.
    """
    
    def __init__(self):
        """Initialize an empty DFA."""
        # All possible input characters
        self.alphabet = [chr(i) for i in range(256)]
        
        # States dictionary: id -> DFAState
        self.states: Dict[int, DFAState] = {}
        
        # Transition function: state_id -> (char -> state_id)
        self.transitions: Dict[int, Dict[str, int]] = {}
        
        # Current state
        self.current_state_id: int = 0
        
        # Basic trap state for invalid input
        self.basic_trap_id: int = 0
        
        # Initialize start and trap states
        self._initialize()
    
    def _initialize(self) -> None:
        """Initialize the DFA with start and trap states."""
        # Start state
        start_state = DFAState(
            id=0,
            type=StateType.START,
            token_class=TokenClass.UNKNOWN
        )
        self.states[0] = start_state
        self.transitions[0] = {char: 0 for char in self.alphabet}  # Loop back by default
        
        # Basic trap state
        basic_trap = DFAState(
            id=1,
            type=StateType.TRAP,
            token_class=TokenClass.ERROR,
            error_type="ERROR_INVALID_INPUT"
        )
        self.states[1] = basic_trap
        self.transitions[1] = {char: 1 for char in self.alphabet}  # Loop back in trap
        self.basic_trap_id = 1
        
        # Reset current state to start
        self.current_state_id = 0
    
    def add_state(self, 
                 is_accept: bool = False, 
                 is_trap: bool = False,
                 token_class: TokenClass = TokenClass.UNKNOWN,
                 error_type: Optional[str] = None) -> int:
        """
        Add a new state to the DFA.
        
        Args:
            is_accept: True if this is an accept state
            is_trap: True if this is a trap state
            token_class: The class of token recognized at this state
            error_type: The type of error (if this is an error state)
            
        Returns:
            The ID of the new state
        """
        state_type = StateType.NORMAL
        if is_accept:
            state_type = StateType.ACCEPT
        elif is_trap:
            state_type = StateType.TRAP
        
        state_id = len(self.states)
        new_state = DFAState(
            id=state_id,
            type=state_type,
            token_class=token_class,
            error_type=error_type
        )
        
        self.states[state_id] = new_state
        
        # Initialize all transitions to basic trap
        self.transitions[state_id] = {char: self.basic_trap_id for char in self.alphabet}
        
        return state_id
    
    def add_transition(self, from_state: int, to_state: int, chars: List[str]) -> None:
        """
        Add transitions from a state to another state for given characters.
        
        Args:
            from_state: Source state ID
            to_state: Destination state ID
            chars: List of characters for which to add the transition
        """
        for char in chars:
            self.transitions[from_state][char] = to_state
    
    def reset(self) -> None:
        """Reset the DFA to the start state."""
        self.current_state_id = 0
    
    def get_next_state(self, char: str) -> DFAState:
        """
        Get the next state for a given input character.
        
        Args:
            char: The input character
            
        Returns:
            The next state
        """
        # Handle characters outside the range
        if ord(char) > 255:
            char = chr(255)
        
        next_state_id = self.transitions[self.current_state_id][char]
        return self.states[next_state_id]
    
    def transition(self, char: str) -> DFAState:
        """
        Transition to the next state for a given input character.
        
        Args:
            char: The input character
            
        Returns:
            The new current state
        """
        # Handle characters outside the range
        if ord(char) > 255:
            char = chr(255)
        
        self.current_state_id = self.transitions[self.current_state_id][char]
        return self.states[self.current_state_id]
    
    def get_current_state(self) -> DFAState:
        """
        Get the current state.
        
        Returns:
            The current state
        """
        return self.states[self.current_state_id] 