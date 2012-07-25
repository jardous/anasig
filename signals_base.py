#!/usr/bin/python
# -*- coding: utf-8 -*-

from globals import *
#from Numeric import arange, sin, pi, array, ones
from numpy import arange, sin, pi, array, ones

import os

###################################################################
## base signal
class SignalBase(ItemBase):
    """ base class for all signals """
    _type = 'signal'
    
    # class variables
    defaults = {
        'NAME'           : u'signal',
        'FS'             : 1024.,    # sampling frequency
        'SAMPLES'        : 1024      # total number of samples
    }
    
    def __init__(self, **kwords):
        ItemBase.__init__(self)
        sc = self.__class__
        # update the dafaults
        d = SignalBase.defaults
        d.update(sc.defaults)
        sc.defaults = d
        
        self.name = sc.defaults['NAME']
        
        self.parameters['fs']           = d['FS']
        self.parameters['samplescount'] = d['SAMPLES']
        self.parameters['xAxisLabel']   = tr('time')
        self.parameters['yAxisLabel']   = tr('magnitude')
        self.parameters['xUnit']        = 'samples'
        self.parameters['yUnit']        = ''
        self.setProperties(kwords)
        self.__kwords = kwords
        
        # data is stored as (dependent data - Y, and independet - x axis labels)
        self._dataX = None
        self._dataY = None
    
    def toPickle(self, s):
        ItemBase.toPickle(self, s)
        s['yData'] = self._dataY.tolist()
        s['xData'] = None
        if self._dataX:
            s['xData'] = self._dataX.tolist()
    
    def fromPickle(self, s):
        ItemBase.fromPickle(self, s)
        self.set_data(s['yData'], s['xData'])
    
    def set_dataY(self, data):
        """set the Y-axis data"""
        self._dataY = data
        # do not add by default self['samplescount'] = len(data)
    
    def set_dataX(self, data):
        """set the X-axis data"""
        self._dataX = data
    
    def set_data(self, dataY, dataX): # Y, x-axis vals
        # TODO: data length check
        #if (dataX == None) or (dataX.shape == dataY.shape):
        self.set_dataY(dataY)
        self.set_dataX(dataX)
        #    raise ValueError
    
##    def __add__(self, right): # overloaded operator for sum operation
    def mix(self, right): # overloaded operator for sum operation
        # it is only possible to add two signals of the same fs
        if (self['fs'] != right['fs']):
            raise anasigError(tr('Signals must have the same sampling frequency'))
        
        if (self.get_size() >= right.get_size()):
            newDataX = self.get_dataX()
        else:
            newDataX = right.get_dataX()
        
        newSig = Signal()
        newSig.set_data(self.get_dataY() + right.get_dataY(), newDataX)
        newSig.name = self.name + '+' + right.name
        #newSig['fs'] = self['fs'] # TODO: really?
        return newSig
    
    def get_minX(self):
        """returns the minimum value of dataX"""
        if self._dataX != None:
            return min(self._dataX)
        return 0
    def get_minY(self):
        """returns the minimum value of dataY"""
        if self._dataY != None:
            return min(self._dataY)
        return 0
    def get_maxX(self):
        """returns the maximum value of dataX"""
        if self._dataX != None:
            return max(self._dataX)
        return self.get_size()#self['samplescount']#-1 TODO:?
    def get_maxY(self):
        """returns the maximum value of dataX"""
        if self._dataY != None:
            return max(self._dataY)
        return 0
    
    def get_dataY(self):
        ret = self._dataY
        if ret==None:
            ret = zeros(self['samplescount'], typecode='d')
        return ret
    
    def get_dataX(self):   # return x axis values
        if self._dataX == None:# or len(self._data[1])==0:
            # need time or samples?
            return arange(0, self.get_size(), 1)
##            fs = float(self['fs'])
##            up = self.get_size()/fs
##            out = arange(0, up, 1/fs)
##            o = len(out)
##            s = self.get_size()
##            assert(len(out) == self.get_size())
##            return out
        else:
            return self._dataX
    
    def get_size(self):
        if self._dataY != None:
            return len(self._dataY)#self['samplescount']
        return 0
    
    def __eq__(self, right):
        return self.__class__==right.__class__
    
    def getMenuItemsList(self):
        return [{tr('Save to file'):self.saveToFile},
##                {tr('Properties'):self.propertiesShow}
                ]
    
    def valuesChanged(self):
        getActiveWorkspace().SignalOrg.updateContents()
        getActiveWorkspace().InstrumentOrg.updateContents()



###################################################################
## generic type of signal
class Signal(SignalBase):
    _subType = 'generic'
    
    defaults = {
        'NAME' : u'generic signal'
    }
    
    def __init__(self, **kwords):
        SignalBase.__init__(self)
        self.name = self.__class__.defaults['NAME']
        self.setProperties(kwords)

