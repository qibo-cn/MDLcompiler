"""
dlex is short for darlang lexical analyze.
It's named tokenizer as well. A tokenizer will
split source program into tokens.
"""

import ply.lex as lex

reserved_word = {
    '"projectName"': 'PROJECT_NAME',
    '"version"': 'VERSION',
    '"target"': 'TARGET',
    '"netDepth"': 'NET_DEPTH',
    '"delayType"': 'DELAY_TYPE',
    '"leakSign"': 'LEAK_SIGN',

    '"neuronGroups"': 'NEURON_GROUPS',
    '"layerName"': 'LAYER_NAME',
    '"neuronSize"': 'NEURON_SIZE',
    '"neuronType"': 'NEURON_TYPE',
    '"leakMode"': 'LEAK_MODE',
    '"leakValue"': 'LEAK_VALUE',
    '"resetMode"': 'RESET_MODE',
    '"vThreshold"': 'V_THRESHOLD',

    '"connectConfig"': 'CONNECT_CONFIG',
    '"name"': 'NAME',
    '"src"': 'SRC',
    '"dst"': 'DST',
    '"synapses"': 'SYNAPSES'
}

tokens = [
             'NUMBER', 'STRING',
             'COLON', 'COMMA',
             'OPEN_SQUARE_BRACKET', 'CLOSE_SQUARE_BRACKET',
             'OPEN_CURLY_BRACKET', 'CLOSE_CURLY_BRACKET',
         ] + list(reserved_word.values())


def t_NUMBER(t):
    r'[-+]?\d+'
    t.value = int(t.value)
    return t


def t_STRING(t):
    r'"([^\\"\n]|\\.)*"'
    if t.value in reserved_word:
        t.type = reserved_word[t.value]
    else:
        t.value = t.value[1:len(t.value) - 1]
    return t


def t_COLON(t):
    r':'
    return t


def t_COMMA(t):
    r','
    return t


def t_OPEN_SQUARE_BRACKET(t):
    r'\['
    return t


def t_CLOSE_SQUARE_BRACKET(t):
    r']'
    return t


def t_OPEN_CURLY_BRACKET(t):
    r'{'
    return t


def t_CLOSE_CURLY_BRACKET(t):
    r'}'
    return t


t_ignore = ' \t\n\r\v\f'


class DarLexer:
    def __init__(self):
        self.lexer = lex.lex()

    def __del__(self):
        del self.lexer
