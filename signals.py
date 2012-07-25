#!/usr/bin/python
# -*- coding: utf-8 -*-

from signals_base import *#SignalBase, Signal
#from Numeric import arange, array, sin, pi, Float
from numpy import arange, array, sin, pi#, Float
from types import *#IntType, StringType
from random import gauss


###################################################################
## white noise signal
class SignalNoise(SignalBase):
    _subType = 'noise'
    
    
    defaults = {
        'NAME'   : u'noise',
        'GAIN'   : 1.
    }
    
    def __init__(self, *args, **kwords):
        SignalBase.__init__(self)
        
        sc = self.__class__
        name = sc.defaults['NAME']
        
        self['gain'] = sc.defaults['GAIN']
        
        self.setProperties(kwords)
    
    def valuesChanged(self):
        gain, samplescount = self['gain'], self['samplescount']
        data = arange(samplescount, typecode='d')
        x=0
        while x<samplescount:
            data[x] = gauss(0, .5)
            x = x + 1
        data = data * gain
        self.set_dataY(data)



###################################################################
## sinus signal
class SignalSin(SignalBase):
    _subType = 'sin'
    
    # class variables
    defaults = {
        'NAME'     : u'sinus',#transl.tr('sinus'),
        'PERIODS'  : 1.,
        'GAIN'     : 1.
    }
    
    def __init__(self, *args, **kwords):
        SignalBase.__init__(self)
        
        sc = self.__class__
        name = sc.defaults['NAME']
        
        self.parameters['periods']    = sc.defaults['PERIODS']
        self.parameters['gain']       = sc.defaults['GAIN']
        self.setProperties(kwords)
    
    def valuesChanged(self):
        gain, periods, samplescount = self['gain'], self['periods'], self['samplescount']
        ret = arange(0, samplescount, typecode='d')
        data = gain * sin(periods*2.0*pi*(ret/(samplescount-1.0)))
        self.set_dataY(data)

##    def toSave(self, s):
##        _SignalBase.toSave(self, s)



###################################################################
## constant value
class SignalConstant(SignalBase):
    _subType = 'constant'
    
    defaults = {
        'NAME'  : u'constant',
        'GAIN'  : 1.
    }
    
    def __init__(self, *args, **kwords):
        SignalBase.__init__(self)
        
        name = self.__class__.defaults['NAME']
        
        self['gain'] = self.__class__.defaults['GAIN']
        self.setProperties(kwords)
    
    def valuesChanged(self):
        gain, samplescount = self['gain'], self['samplescount']
        data = gain * ones(samplescount, Float)
        self.set_data(data, None)



###################################################################
## spectrum
class SignalSpectrum(SignalBase):
    _subType = 'spectrum'
    
    defaults = {
        'NAME'  : u'spectrum',
        'FS'        : 1024.,
        'SAMPLES'   : 0,
        'GAIN'      : 1.
    }
    
    def __init__(self, *args, **kwords):
        SignalBase.__init__(self)
        name = self.__class__.defaults['NAME']
        #- del self['fs'] # spectrum has no sampling frequency
        self.setProperties(kwords)



###################################################################
## signal from wav file
class SignalWavFile(SignalBase):
    _subType = 'wavfile'
    
    defaults = {
        'NAME'      : u'wav',
        'FS'        : 1024.,
        'SAMPLES'   : 0,
        'FILENAME'  : '',
        'GAIN'      : 1.,
        'FILEFILTER': 'wav files (*.wav)'
    }
    
    def __init__(self, *args, **kwords):
        SignalBase.__init__(self)
        
        ai = self.parameters.insert
        sc = self.__class__
        
        self.name = sc.defaults['NAME']
        
        f = Parameter('file', sc.defaults['FILENAME'], StringType)
        f.fileFilter = sc.defaults['FILEFILTER']
        ai(0, f)
        self['samplesize']      = 16
        self['channels']        = 2
        self['xAxisLabel']      = tr('samples')
        self['yAxisLabel']      = tr('magnitude')
        self['xUnit']           = u'Hz'
        self['yUnit']           = u''
        
        self.setReadOnly('fs', True)
        self.setReadOnly('samplescount', True)
        self.setReadOnly('samplesize', True)
        self.setReadOnly('channels', True)
        
        # TODO: mix signals
        self.setProperties(kwords)
    
    def valuesChanged(self):
        import wave, struct
        fn = self['file']
        fp = wave.open(fn, 'rb')
        
        self['samplescount']    = fp.getnframes()
        self['fs']              = fp.getframerate()
        self['samplesize']      = fp.getsampwidth()
        self['channels']        = fp.getnchannels()
        # TODO converting can take long time!
        #curprev = self.vw.cursor
        #self.vw.setCursor( Qt.BusyCursor )
        
        wavdata = fp.readframes(self['samplescount']) # got string
        wavdata = array( struct.unpack("%dB"%(self['samplescount']), wavdata) ) - 128.0
        self.set_data( wavdata, None )
    
    def __play( self ):
        _methodName = 'play'
    
##    def selectFile(self):
##        fd = QFileDialog(
##                join(ProgramVars['SIGNAL_PICKLE_PATH'], ProgramVars['SIGNAL_WAV_FILENAME']), 
##                "wav files (*.wav)")
##        if fd.exec_loop() == QDialog.Accepted:
##            filename = fd.selectedFile()
##    
##    def __setitem__(self, item, value):
##        # floats
##        if item in ('channels', 'samplesize'):
##            if value!=None: # not for initialization
##                raise anasigError(transl.tr('err_Noneditable_property'))
##        _SignalBase.__setitem__(self, item, value)



###################################################################
## signal from Pickle file
class SignalPickleFile(SignalBase):
    _subType = 'signal'
    
    defaults = {
        'NAME'      : u'pickle',
        'FS'        : 1024.,
        'SAMPLES'   : 0,
        'FILENAME'  : '',
        'GAIN'      : 1.,
        'FILEFILTER': ''
    }
    
    def __init__(self, *args, **kwords):
        SignalBase.__init__(self)
        
        ai = self.parameters.insert
        sc = self.__class__
        
        self.name = sc.defaults['NAME']
        
        f = Parameter('file', sc.defaults['FILENAME'], StringType)
        f.fileFilter = sc.defaults['FILEFILTER']
        ai(0, f)
        self['xAxisLabel']      = tr('samples')
        self['yAxisLabel']      = tr('magnitude')
        self['xUnit']           = u'Hz'
        self['yUnit']           = u''
        
        self.setReadOnly('fs', True)
        self.setReadOnly('samplescount', True)
        
        self.setProperties(kwords)
    
    def valuesChanged(self):
        import cPickle
        fn = self['filename']
        try:
            f = open(fn, 'r')
            data = cPickle.load(f)
        except:
            f.close()
            raise anasigError(tr('Not a pickle file'))
        
        f.close()
        
        self.set_data( data, None )




class SignalFile:
    """baseclass for signals loaed from file
       Must be initialized after SignalBase"""
    def __init__(self):
        # need to remove fs a samplescount variabled - added in SignalBase by default
        #del self['fs']; del self['samplescount']
        pass


###################################################################
## signal from text file
class SignalTextFile(SignalBase, SignalFile):
    """ loading file of format:
        0,00\t478\n
    """
    _subType = 'signal'
    """
    param order:
        file, [fs], [samplescount], ...
    """
    
    defaults = {
        'NAME'      : u'text file',
        'FS'        : 1024.,
        'SAMPLES'   : 0,
        'FILENAME'  : '',
        #'GAIN'      : 1.,
        'FILEFILTER': ''
    }
    
    def __init__(self, *args, **kwords):
        SignalBase.__init__(self)
        SignalFile.__init__(self)
        
        ai = self.parameters.insert
        sc = self.__class__
        
        self.name = sc.defaults['NAME']
        
        f = Parameter('file', sc.defaults['FILENAME'], StringType)
        f.fileFilter = sc.defaults['FILEFILTER']
        self.parameters.insert(0, f)
        self['xAxisLabel']      = tr('samples')
        self['yAxisLabel']      = tr('magnitude')
        self['xUnit']           = u''
        self['yUnit']           = u''
        
        self.setReadOnly('fs', True)
        self.setReadOnly('samplescount', True)
        
        self.setProperties(kwords)
    
    def valuesChanged(self):
        import fileinput
        fn = str(self['file'])
        time = []
        vals = []
        try:
            for line in fileinput.input(fn):
                line = line.replace(',', '.')
                t,v = line.split()
                time.append(eval(t))
                vals.append(eval(v))
        except:
            raise anasigError(tr('Do not understand the file format'))
        
        #TODO: insert time values
        self['samplescount'] = len(vals)
        bn = os.path.basename(self['file'])
        self.setName(os.path.splitext(bn)[0])
        self.set_data( array(vals), None )
        SignalBase.valuesChanged(self)


###################################################################
## signal from Pickle file
class SignalMatlabFile(SignalBase, SignalFile):
    _subType = 'signal'
    """
    param order:
        file, [fs], [samplescount], ...
    """
    
    defaults = {
        'NAME'      : u'matlab',
        'FS'        : 1024.,
        'SAMPLES'   : 0,
        'FILENAME'  : '',
        #'GAIN'      : 1.,
        'FILEFILTER': ''
    }
    
    def __init__(self, *args, **kwords):
        SignalBase.__init__(self)
        SignalFile.__init__(self)
        
        ai = self.parameters.insert
        sc = self.__class__
        
        self.name = sc.defaults['NAME']
        
        f = Parameter('file', sc.defaults['FILENAME'], StringType)
        f.fileFilter = sc.defaults['FILEFILTER']
        self.parameters.insert(0, f)
        self['xAxisLabel']      = tr('samples')
        self['yAxisLabel']      = tr('magnitude')
        self['xUnit']           = u''
        self['yUnit']           = u''
        
        self.setReadOnly('fs', True)
        self.setReadOnly('samplescount', True)
        
        self.setProperties(kwords)
    
    def valuesChanged(self):
        #import wave, struct
        from pylab import load
        
        fn = str(self['file'])
        try:
            data = load(fn)
        except:
        #if data==None:
            raise anasigError(tr('Not a matlab file'))
        
        self['samplescount'] = len(data)
        bn = os.path.basename(self['file'])
        self.setName(os.path.splitext(bn)[0])
        self.set_data( data, None )
        SignalBase.valuesChanged(self)

