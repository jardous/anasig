#!/usr/bin/python
# -*- coding: utf-8 -*-

""" implements Sinus signal plugin for anasig
"""

import sys
sys.path.insert(0, '../')

#from globals import *
from signals_base import _SignalBase
from Numeric import arange, sin, pi

__plugin_name__ = 'signal sin'
__plugin_type__ = 'signal'

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
__description___ = """
"""

class SignalSin(_SignalBase):
    _subType = 'sin'
    
    # class variables
    defaults = {
    'SIGNAL_SIN_NAME'     : 'sinus',#transl.tr('sinus'),
    'SIGNAL_SIN_PERIODS'  : 1024,
    'SIGNAL_SIN_GAIN'     : 1.}
    
    def __init__(self, *args, **kwords):
        _SignalBase.__init__(self, name=self.defaults['SIGNAL_SIN_NAME'])
        self['periods']    = self.defaults['SIGNAL_SIN_PERIODS']
        self['gain']       = self.defaults['SIGNAL_SIN_GAIN']
        self.setProperties(*args, **kwords)
    
    def generate(self):
        gain, periods, samplescount = self['gain'], self['periods'], self['samplescount']
        ret = arange(0, samplescount, typecode='d')
        data = gain*sin(periods*2.0*pi*(ret/(samplescount-1.0)))
        self.setData(data, None)

    def toSave(self, s):
        _SignalBase.toSave(self, s)
        s['class'] = SignalSin
