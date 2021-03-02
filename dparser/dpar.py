"""
dpar is short for darlang dparser. A dparser will
convert token sequence into an abstract syntax tree.
"""

import ply.yacc as yacc

from dparser.dlex import tokens, DarLexer
from dparser.ast import NeuronGroup, ConnectConfig, SNN


def p_program(p):
    "program : OPEN_CURLY_BRACKET PROJECT_NAME COLON STRING COMMA VERSION COLON STRING COMMA TARGET COLON STRING COMMA NET_DEPTH COLON NUMBER COMMA DELAY_TYPE COLON number_list COMMA LEAK_SIGN COLON NUMBER COMMA NEURON_GROUPS COLON neuron_group_list COMMA CONNECT_CONFIG COLON connect_config_list CLOSE_CURLY_BRACKET"
    p[0] = SNN(p[4], p[8], p[12], p[16], p[20], p[24], p[28], p[32])


def p_number_list(p):
    """
    number_list : OPEN_SQUARE_BRACKET number_rec CLOSE_SQUARE_BRACKET
    """
    p[0] = p[2]


def p_number_rec(p):
    """
    number_rec : NUMBER COMMA number_rec
               | NUMBER
    """
    if len(p) == 4:
        p[0] = [p[1]] + p[3]
    else:
        p[0] = [p[1]]


def p_neuron_group_list(p):
    """
    neuron_group_list : OPEN_SQUARE_BRACKET neuron_group_rec CLOSE_SQUARE_BRACKET
    """
    p[0] = p[2]


def p_neuron_group_rec(p):
    """
    neuron_group_rec : neuron_group COMMA neuron_group_rec
                     | neuron_group
    """
    if len(p) == 4:
        p[0] = [p[1]] + p[3]
    else:
        p[0] = [p[1]]


def p_neuron_group(p):
    """
    neuron_group : input_neuron_group
                 | normal_neuron_group
    """
    p[0] = p[1]


def p_input_neuron_group(p):
    """
    input_neuron_group : OPEN_CURLY_BRACKET LAYER_NAME COLON STRING COMMA NEURON_SIZE COLON NUMBER CLOSE_CURLY_BRACKET
    """
    p[0] = NeuronGroup(p[4], p[8])


def p_normal_neuron_group(p):
    """
    normal_neuron_group : OPEN_CURLY_BRACKET LAYER_NAME COLON STRING COMMA NEURON_SIZE COLON NUMBER COMMA NEURON_TYPE COLON STRING COMMA LEAK_MODE COLON NUMBER COMMA LEAK_VALUE COLON NUMBER COMMA RESET_MODE COLON NUMBER COMMA V_THRESHOLD COLON NUMBER CLOSE_CURLY_BRACKET"""
    p[0] = NeuronGroup(p[4], p[8], p[12], p[16], p[20], p[24], p[28])


def p_connect_config_list(p):
    """
    connect_config_list : OPEN_SQUARE_BRACKET connect_config_rec CLOSE_SQUARE_BRACKET
    """
    p[0] = p[2]


def p_connect_config_rec(p):
    """
    connect_config_rec : connect_config COMMA connect_config_rec
                       | connect_config
    """
    if len(p) == 4:
        p[0] = [p[1]] + p[3]
    else:
        p[0] = [p[1]]


def p_connect_config(p):
    """
    connect_config : OPEN_CURLY_BRACKET NAME COLON STRING COMMA SRC COLON STRING COMMA DST COLON STRING COMMA SYNAPSES COLON STRING CLOSE_CURLY_BRACKET
    """
    p[0] = ConnectConfig(p[4], p[8], p[12], p[16])


class DarParser:
    def __init__(self):
        self.lexer = DarLexer()
        self.parser = yacc.yacc()

    def __del__(self):
        del self.lexer
        del self.parser

    def parse(self, program):
        return self.parser.parse(program)


def parse(program):
    d = DarParser()
    return d.parse(program)
