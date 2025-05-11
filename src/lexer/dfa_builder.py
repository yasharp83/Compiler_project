"""
DFA builder for constructing the lexical analyzer DFA.
"""
from typing import List, Set

from src.common.language_specs import (
    KEYWORDS, SYMBOLS, WHITESPACE, DIGITS, LETTERS, ILLEGAL, SIGMA
)
from src.lexer.dfa import DFA, TokenClass


def get_except(list1: List[str], list2: List[str]) -> List[str]:
    """
    Get elements in list1 that are not in list2.
    
    Args:
        list1: First list
        list2: Second list
        
    Returns:
        List of elements in list1 that are not in list2
    """
    return [i for i in list1 if i not in list2]


def build_dfa() -> DFA:
    """
    Build and initialize the DFA for lexical analysis.
    
    Returns:
        An initialized DFA
    """
    dfa = DFA()
    
    # Create states for NUMBER tokens
    number_state = dfa.add_state(is_accept=True, token_class=TokenClass.NUMBER)
    error_invalid_number = dfa.add_state(is_trap=True, token_class=TokenClass.ERROR, 
                                       error_type="ERROR_INVALID_NUMBER")
    error_invalid_input = dfa.add_state(is_trap=True, token_class=TokenClass.ERROR,
                                       error_type="ERROR_INVALID_INPUT")
    
    # Transitions for numbers
    dfa.add_transition(dfa.current_state_id, number_state, list(DIGITS))
    dfa.add_transition(number_state, number_state, list(DIGITS))
    dfa.add_transition(number_state, dfa.basic_trap_id, list(WHITESPACE) + list(SYMBOLS))
    dfa.add_transition(number_state, error_invalid_number, list(LETTERS))
    dfa.add_transition(number_state, error_invalid_input, list(ILLEGAL))
    
    # Create states for SYMBOL tokens (except *, /, =)
    symbol_chars = get_except(list(SYMBOLS), ['*', '/', '='])
    for symbol in symbol_chars:
        symbol_state = dfa.add_state(is_accept=True, token_class=TokenClass.SYMBOL)
        dfa.add_transition(0, symbol_state, [symbol])
        # All transitions from symbol state go to trap (single-char symbols)
        
    # Handle * specially (for comments)
    star_state = dfa.add_state(is_accept=True, token_class=TokenClass.SYMBOL)
    dfa.add_transition(0, star_state, ['*'])
    dfa.add_transition(star_state, dfa.basic_trap_id, 
                      list(WHITESPACE) + list(LETTERS) + list(DIGITS) + 
                      get_except(list(SYMBOLS), ['/']))
    dfa.add_transition(star_state, error_invalid_input, list(ILLEGAL))
    
    error_unmatched_comment = dfa.add_state(is_trap=True, token_class=TokenClass.ERROR,
                                          error_type="ERROR_UNMATCHED_COMMENT")
    dfa.add_transition(star_state, error_unmatched_comment, ['/'])
    
    # Handle = and == operators
    eq_state = dfa.add_state(is_accept=True, token_class=TokenClass.SYMBOL)
    eq_eq_state = dfa.add_state(is_accept=True, token_class=TokenClass.SYMBOL)
    dfa.add_transition(0, eq_state, ['='])
    dfa.add_transition(eq_state, eq_eq_state, ['='])
    dfa.add_transition(eq_state, dfa.basic_trap_id, 
                      get_except(list(SIGMA), ['='] + list(ILLEGAL)))
    dfa.add_transition(eq_state, error_invalid_input, list(ILLEGAL))
    
    # Handle / and /* for comments
    div_state = dfa.add_state(is_accept=True, token_class=TokenClass.SYMBOL)
    dfa.add_transition(0, div_state, ['/'])
    dfa.add_transition(div_state, dfa.basic_trap_id,
                      list(WHITESPACE) + list(LETTERS) + list(DIGITS) +
                      get_except(list(SYMBOLS), ['*']))
    dfa.add_transition(div_state, error_invalid_input, list(ILLEGAL))
    
    # Comment states
    comment_state_1 = dfa.add_state(is_accept=False, token_class=TokenClass.COMMENT,
                                   error_type="ERROR_UNCLOSED_COMMENT")
    comment_state_2 = dfa.add_state(is_accept=False, token_class=TokenClass.COMMENT,
                                   error_type="ERROR_UNCLOSED_COMMENT")
    comment_state_3 = dfa.add_state(is_accept=True, token_class=TokenClass.COMMENT)
    
    dfa.add_transition(div_state, comment_state_1, ['*'])
    dfa.add_transition(comment_state_1, comment_state_1, 
                      get_except(list(SIGMA), ['*']))
    dfa.add_transition(comment_state_1, comment_state_2, ['*'])
    dfa.add_transition(comment_state_2, comment_state_1, 
                      get_except(list(SIGMA), ['/']))
    dfa.add_transition(comment_state_2, comment_state_3, ['/'])
    
    # Handle whitespace
    for ws in WHITESPACE:
        ws_state = dfa.add_state(is_accept=True, token_class=TokenClass.WHITESPACE)
        dfa.add_transition(0, ws_state, [ws])
    
    # Handle identifiers and keywords
    id_state = dfa.add_state(is_accept=True, token_class=TokenClass.ID)
    dfa.add_transition(0, id_state, list(LETTERS))
    dfa.add_transition(id_state, id_state, list(LETTERS) + list(DIGITS))
    dfa.add_transition(id_state, dfa.basic_trap_id, list(WHITESPACE) + list(SYMBOLS))
    dfa.add_transition(id_state, error_invalid_input, list(ILLEGAL))
    
    # Handle illegal characters in start state
    for char in ILLEGAL:
        dfa.add_transition(0, error_invalid_input, [char])
    
    # Reset the DFA to the start state
    dfa.reset()
    
    return dfa 