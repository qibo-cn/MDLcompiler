"""
ast is short for abstract syntax tree.
"""
from typing import List


class NeuronGroup:
    def __init__(self,
                 layer_name: str,
                 neuron_size: int,
                 neuron_type: str = '',
                 leak_mode: int = 0,
                 leak_value: int = 0,
                 reset_mode: int = 0,
                 v_threshold: int = 0):
        self.layer_name = layer_name
        self.neuron_size = neuron_size
        self.neuron_type = neuron_type
        self.leak_mode = leak_mode
        self.leak_value = leak_value
        self.reset_mode = reset_mode
        self.v_threshold = v_threshold


class ConnectConfig:
    def __init__(self,
                 name: str,
                 src: str,
                 dst: str,
                 synapses: str):
        self.name = name
        self.src = src
        self.dst = dst
        self.synapses = synapses


class SNN:
    def __init__(self,
                 project_name: str,
                 version: str,
                 target: str,
                 net_depth: int,
                 delay_type: List[int],
                 leak_sign: int,
                 neuron_groups: List[NeuronGroup],
                 connect_config: List[ConnectConfig]):
        self.project_name = project_name
        self.version = version
        self.target = target
        self.net_depth = net_depth
        self.delay_type = delay_type
        self.leak_sign = leak_sign
        self.neuron_groups = neuron_groups
        self.connect_config = connect_config
