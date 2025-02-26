from .multiobjective.constrained import Srinivas, Tanaka
from .multiobjective.dtlz import DTLZ1, DTLZ2, DTLZ3, DTLZ4, DTLZ5, DTLZ6, DTLZ7
from .multiobjective.lz09 import LZ09_F2
from .multiobjective.unconstrained import Kursawe, Fonseca, Schaffer, Viennet2
from .multiobjective.zdt import ZDT1, ZDT2, ZDT3, ZDT4, ZDT6
from .multiobjective.wfg import WFG1, WFG2, WFG3, WFG4, WFG5, WFG6, WFG7, WFG8, WFG9
from .singleobjective.unconstrained import OneMax, Sphere

__all__ = [
    'Srinivas', 'Tanaka',
    'Kursawe', 'Fonseca', 'Schaffer', 'Viennet2',
    'DTLZ1', 'DTLZ2', 'DTLZ3', 'DLTZ4', 'DTLZ5', 'DTLZ6', 'DTLZ7',
    'ZDT1', 'ZDT2', 'ZDT3', 'ZDT4', 'ZDT6',
    'WFG1', 'WFG2', 'WFG3','WFG4', 'WFG5','WFG6', 'WFG7', 'WFG8', 'WFG9',
    'LZ09_F2',
    'OneMax', 'Sphere'
]
