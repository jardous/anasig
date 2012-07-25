#!/usr/bin/python
# -*- coding: utf-8 -*-

""" implements Noise signal plugin for anasig
"""

import sys
sys.path.insert(0, '../')

#from globals import *
from signals_base import _SignalBase
from scipy import rand

__plugin_name__ = 'noise signal'
__plugin_type__ = 'signal'
__plugin_main_class__ = SignalNoise

__version__ = '07-2002'
__author__ = ['Jiří Popek (jiri.popek@gmail.com)',]
__thanks_to__ = []
__copyright__ = """
    This file is released to the public domain. I would
    appreciate it if you choose to keep derived works under terms
    that promote freedom, but obviously am giving up any rights
    to compel such.
"""
__history__ = """
    01-07-2005  initial version
"""
__description___ = """"
"""

class SignalNoise(_SignalBase):
    _subType = 'noise'
    
    defaults = {
    'SIGNAL_NOISE_NAME'   : 'noise',#transl.tr('noise'),
    'SIGNAL_NOISE_GAIN'   : 1.}
    
    def __init__(self, *args, **kwords):
        _SignalBase.__init__(self, name=self.defaults['SIGNAL_NOISE_NAME'])
        self['gain'] = self.defaults['SIGNAL_NOISE_GAIN']
        self.setProperties(*args, **kwords)
    
    def generate(self):
        from scipy import rand
        gain, samplescount = self['gain'], self['samplescount']
        data = gain * (rand(samplescount) - 0.5)
        self.setData(data, None)
