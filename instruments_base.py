#!/usr/bin/python
# -*- coding: utf-8 -*-

from globals import *

from signals_base import *
from anasigError import *

###################################################################
## virtual class Instrument
class InstrumentBase(ItemBase):
    """ base class for all instruments """
    _type = 'instrument'
    
    defaults = {
        'NAME'           : 'instrument'
    }
    
    def __init__(self, *args, **kwords):
        ItemBase.__init__(self)
        
        d = InstrumentBase.defaults
        d.update(self.__class__.defaults)
        self.__class__.defaults = d
        
        self.name = self.__class__.defaults['NAME']
        
        self.setProperties(kwords)
        
        self.appendedSignalsList = []
    
    def process(self, signals):
        """ represents method of intrument function """
        if len(signals) == 0:
            raise anasigError(tr('You must connect signal'))
    
    def addMenuItems(self, cmenu):
        """ virtual function
            this f is called when custom context menu items are requested
        """
        pass
    
    def valuesChanged(self):
        """ virtual function for instrument reinitializing """
        pass
