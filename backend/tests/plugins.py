import sys
import os
from pathlib import Path


root_dir = Path(__file__).parent.parent.parent 
sys.path.insert(0, str(root_dir))

from backend.core.primitives.Plugin import PortPlugin, PortPluginParamMeta

class PL(PortPlugin):
    def __init__(self):
        super().__init__('test', 'fff', 'dsdds', 'sds')

    @PortPlugin.init_func(medium=PortPluginParamMeta(description= 'Среда', choices=['гелий', 'натрий'],
                                             type= 'str', default='гелий'),
                      density={'description': 'Плотность', 'min': 10., 'max': 20., 'type': 'float', 'default': 15})
    def _init_1(self, medium, density):
        self._medium = medium
        self._density = density

    @PortPlugin.calc_func(p=PortPluginParamMeta(description='давление', type='float'),
                      t=PortPluginParamMeta(description='температура', type='float'))
    def calc_1(self, p, t):
        return p + t
    
    @PortPlugin.calc_func(p=PortPluginParamMeta(description='давление', type='float'),
                      h=PortPluginParamMeta(description='энтальпия', type='float'))
    def calc_2(self, p, h):
        return p - h

t = PL()
init_sc = PL.get_init_schema()
cals_sc = t.get_calc_schema()
t.init(medium='натрий', density=11.0)
z = t.calculate(p=1., h=3.)
print(z)
