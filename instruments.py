#!/usr/bin/python
# -*- coding: utf-8 -*-

from globals import *

from scipy.signal.ltisys import lti#, lsim
from kalmanfilter import KalmanFilter
#from pnumeric import kf_process, Matrix

from signals_base import *
from signals import *

from string import split, lower
from scipy.signal.signaltools import get_window
from Numeric import array, arange, Float, transpose, resize, Float
from matplotlib.numerix.mlab import zeros, eye, ones
from scipy.signal import signaltools
from anasigError import *
from instruments_base import *
from types import *


FFT_OVERLAY = ('0', '1/3', '2/3')
FFT_WINDOW = ('Rectangular', 'Bartlett', 'Blackman', 'Hamming', 'Hanning', 'Gaussian')
FFT_LINENUMBER = (400, 800)


###################################################################
## Fast fourier transform (spectrum)
class Instrument_FFT(InstrumentBase):
    """ Fast Fourier Transform instrument object """
    _subType = 'FFT'
    
    defaults = {
        'NAME'       : u'FFT',
        'OVERLAY'    : 0,   # FFT_OVERLAY[0]
        'AVERAGES'   : 1,
        'WINDOW'     : 0,   # FFT_WINDOW[0]
        'LINENUMBER' : 0    # FFT_LINENUMBER[0]
    }
    
    def __init__ ( self, *args, **kwords ):
        InstrumentBase.__init__(self)
        
        af = self.parameters.append
        sc = self.__class__
        # set the name attribute
        self.name = sc.defaults['NAME']
        
        af(Parameter('linenumber', sc.defaults['LINENUMBER'], IntType, FFT_LINENUMBER))
        self['averages']        = sc.defaults['AVERAGES']
        af(Parameter('overlay', sc.defaults['OVERLAY'], IntType, FFT_OVERLAY))
        af(Parameter('window', sc.defaults['WINDOW'], IntType, FFT_WINDOW))
        self['xAxisLabel']      = tr('frequency')
        self['yAxisLabel']      = tr('magnitude')
        self['xUnit']           = u'Hz'
        self['yUnit']           = u''
        self.setProperties(kwords)
    
    def process(self, signals):
        InstrumentBase.process(self, signals)
        from scipy.fftpack import fft
        from scipy.signal import signaltools
        from Numeric import convolve
        
        dOverlay    = self['overlay']
        dAverages   = self['averages']
        dLinenumber = FFT_LINENUMBER[self['linenumber']]
        dWindow     = self['window']
        # get float from overlay string etc. "2/3" = float(2./3.)
        overlay = [float(a) for a in split(FFT_OVERLAY[dOverlay], '/')]
        if len(overlay)==1: fOverlay = float(overlay[0])
        else: fOverlay = overlay[0]/overlay[1]
        
        length      = dLinenumber
        fft_length  = dLinenumber
        
        dIncrement = int(length * (1-fOverlay))
        
        sout = []
        for s in signals:   # process for every signal
            data = s.get_dataY()
            datalength = s.get_size()
            
            if datalength < length:
                data = resize(data, (length,))
                datalength = length
            
            av_from = 0
            
            if dWindow!=0: # rectangular
                wfunc = getWindowFunction(dWindow, length)
            
            for i in range(dAverages):
                av_to = av_from+length
                if av_to>datalength: 
                    break # end of data
                
                dt = data[av_from:av_to]
                l = len(dt)
                if dWindow!=0: # rectangular
                    dt = signaltools.convolve(dt, wfunc) # weighting by window function
                
                spectrum = fft(dt)
                spectrum_real = abs(spectrum[:fft_length/2].real)
                # recursive average
                if i>1:
                    out = 0.5*(out + spectrum_real) # averaging
                else:
                    out = spectrum_real # initial or single
                
                av_from += dIncrement
            
            #sig = abs(fft(data)[1:len(s.dataY)/2+1].real)
            outSig = SignalSpectrum()
            outSig.name = self.name + ': ' + s.name
            df = 1.#TODO: s['fs']/float(dLinenumber)
            outSig.set_data(out, None)#, df*arange(df, dLinenumber+df))
            outSig['xAxisLabel']    = self['xAxisLabel']
            outSig['yAxisLabel']    = self['yAxisLabel']
            outSig['xUnit']         = self['xUnit']
            sout.append(outSig)
        
        return sout





def getWindowFunction(name, length):
    return get_window(lower(FFT_WINDOW[name]), length)




LTI_DESCRIPTION_TYPE = ('transfer function', 'state space')

###################################################################
## Linear Time Invariant system
class _LTI_BASE(InstrumentBase):
    _subType = 'LTI'
    
    defaults = {
        'NAME'               : u'LTI',
        'DESCRIPTION_TYPE'   : 1, # LTI_DESCRIPTION_TYPE[0]
        'STATES'             : 2, #2,
        #'NUM'                : [1.],
        #'DEN'                : [1.,6.,25.],
        'A'                  : [[-6., -25.], [1., 0.]],
        'B'                  : [[1.], [0.]],
        'C'                  : [[0., 1.]],
        'D'                  : [[0.]],
        'GENERATE_STATES'    : True
    }
    
    def __init__ ( self, *args, **kwords ):
        InstrumentBase.__init__(self)
        
        af = self.parameters.append
        sc = self.__class__
        # set the name attribute
        self.name = sc.defaults['NAME']
        d = sc.defaults
        
        af(Parameter('states', sc.defaults['STATES']))#, IntType, None, self.valuesChanged))#sc.defaults['STATES']
        #self['states'] = sc.defaults['STATES']
        #self._lti = lti(sc.defaults['NUM'], sc.defaults['DEN'])
        self._lti = lti(d['A'], d['B'], d['C'], d['D'])
        af(Parameter('description type', sc.defaults['DESCRIPTION_TYPE'], IntType,
                      LTI_DESCRIPTION_TYPE, self._changeDescriptionType))
        self._changeDescriptionType(1)
        af(Parameter('generate states', sc.defaults['GENERATE_STATES'], BooleanType))
        
        self.setProperties(kwords)
    
    def valuesChanged(self):
        states = self['states'] # new number of states
        dt = self['description type']
        m = self._lti
        ps = m.A.shape[0] # previous number of states
        
        dch = False # description changed indicator
        if (self['A'] and dt==0) or (self['num'] and dt==1):
            dch = True
        
        if ps != states: # Number of states changed - resize matrixes
            A, B, C, D = m.A, m.B, m.C, m.D
            if A.shape != (states, states):
                A = eye(states)
            p = B.shape[1] # number ouf inputs
            if B.shape != (states, p):
                B = eye(states, p)
            q = C.shape[0] # number ouf outputs
            if C.shape != (q, states):
                C = eye(q, states)
            if D.shape != (q, p):
                D = zeros((q, p))
            self._lti = lti(A, B, C, D)
            
            m = self._lti
            
            if dt==0: # 'transfer function'
                # TODO: why m.num.tolist() returns (1,2)? - should be vector
                self['num'], self['den'] = m.num.tolist()[0], m.den.tolist()
            elif dt==1: # 'state space'
                self['A'], self['B'], self['C'], self['D'] = m.A.tolist(), m.B.tolist(), m.C.tolist(), m.D.tolist()
        
        elif dch: # number of states doesn't changed - change descr. type
            if dt==0: # 'transfer function'
                n, d = self['num'], self['den']
                self._lti = lti(n, d)
                del self['A']; del self['B']; del self['C']; del self['D']
            elif dt==1: # 'state space'
                A, B, C, D = self['A'], self['B'], self['C'], self['D']
                if A.shape != (states, states):
                    A = eye(states)
                p = len(B[1]) # number ouf inputs
                if B.shape != (states, p):
                    B = eye(states, p)
                q = len(C[0]) # number ouf outputs
                if C.shape != (q, states):
                    C = eye(q, states)
                if D.shape != (q, p):
                    D = zeros(q, p)
                self._lti = lti(A, B, C, D)
                del self['num']; del self['den']
    
    def process(self, signals):
        InstrumentBase.process(self, signals) # checks connected signals
        sout = [] # output signals list
        for sig in signals:
            U = sig.get_dataY()
            t = sig.get_dataX()
            
            T, yout, xout = self._lti.output( U, t )
            # create states signals if desired
            if self['generate states']:
                xout = transpose(xout)
                i=1
                # take all system state variables
                states = xout.shape[0]
                for x in xout:
                    out = Signal()
                    out.set_data( transpose(x), T )
                    out.name = self.name + u': ' + tr('State') + u' ' + str(i)
                    i += 1
                    sout.append(out)
            
            # system output
            out = Signal()
            out.set_data( yout, T )
            out.name = self.name + u': ' + tr('Output')
            sout.append(out)
        
        return sout
    
    def __clear_desc(self):
        pr = self.parameters.remove
        pr('num'), pr('den'), pr('A'), pr('B'), pr('C'), pr('D')
    
    def _changeDescriptionType(self, idx):
        prev_type = self['description type']
        self['description type'] = idx
        # get the index of description type - parameters should be appended just after it
        i = self.parameters.index('description type') + 1
        self.__clear_desc()
        ins = self.parameters.insert
        m = self._lti
        
        if idx==1: #'ss'
            ins(i, Parameter('D', m.D.tolist(), ListType))
            ins(i, Parameter('C', m.C.tolist(), ListType))
            ins(i, Parameter('B', m.B.tolist(), ListType))
            ins(i, Parameter('A', m.A.tolist(), ListType))
        elif idx==0:#'tf':
            ins(i, Parameter('den', m.den.tolist(), ListType))
            ins(i, Parameter('num', m.num.tolist(), ListType))
        return True
    
##    def __setitem__(self, key, val):
##        status, val = checkType(key, val)
##        if not status: return
##        
##        if key=='generate_states':
##            self.__class__.defaults['GENERATE_STATES'] = val
##        elif key=='lti_states': # also initializes the lti object
##            prev_states = self['lti_states']
##            if val != prev_states:
##                self.__holdMatrixUpdate = True
##                A=eye(val, val, 1, Float);
##                A[val-1]=-ones((1, val), Float)[0]
##                B=zeros((val, 1), Float); B[val-1][0]=1.
##                C=zeros((1, val)); C[0][0]=1.
##                D=zeros((1,1))
##                self._lti = lti(A, B, C, D)
##        elif key=='lti_description_type':
##            self._changeDescriptionType(val)
##        elif key in ('A', 'B', 'C', 'D', 'num', 'den', 'x0', 'P0'):
##            if self.__holdMatrixUpdate:
##                return
##        
##        InstrumentBase.__setitem__(self, key, val)
    
    def getMenuItemsList(self):
        return [{tr('impulse response'):self.ImpulseResponse},
                {tr('step response'):self.StepResponse}]
    
    def ImpulseResponse(self):
        t, g = self._lti.impulse()
        fs = 1./(t[1]-t[0])
        samplescount = len(t)
        sig = Signal(fs=fs, yAxisLabel=self['yAxisLabel'], yUnit=self['yUnit'])
        sig.set_data( g, t )
        sig.name = self.name + u': ' + tr('impulse response')
        # send new signal to signal organiser
        ws = qApp.activeWindow().ws.activeWindow().ws
        ws.SignalOrg.addProcessedItem(None, sig, True)
    
    def StepResponse(self):
        t, s = self._lti.step()
        fs = 1./(t[1]-t[0])
        samplescount = len(t)
        sig = Signal(fs=fs, yAxisLabel=self['yAxisLabel'], yUnit=self['yUnit'])
        sig.set_data( s, t )
        sig.name = self.name + ': ' + tr('step response')
        # send new signal to signal organiser
        ws = qApp.activeWindow().ws.activeWindow().ws
        ws.SignalOrg.addProcessedItem(None, sig, True)




###################################################################
## Linear Time Invariant system
class Instrument_LTI(_LTI_BASE):
    _subType = 'LTI'
    def __init__ ( self, *args, **kwords ):
        _LTI_BASE.__init__(self)
        
        self['xAxisLabel']      = tr('frequency')
        self['yAxisLabel']      = tr('magnitude')
        self['xUnit']           = u'Hz'
        self['yUnit']           = u''
        
        self.setProperties(kwords)
    def process(self, signals):
        sout = _LTI_BASE.process(self, signals)
##        return sout
##    
##    def __setitem__(self, item, value):
##        if item=='b_generate_states':
##            self.__class__.defaults['GENERATE_STATES'] = value
##        _LTI_BASE.__setitem__(self, item, value)



KF_STATES  = 2
KF_INPUTS  = 1
KF_OUTPUTS = 1

###################################################################
## Kalman filter
class Instrument_Kalman_Filter(_LTI_BASE):#, KalmanFilter):
    _subType = 'KalmanFilter'
    
    defaults = {
        'NAME'              : u'Kalman filter',
        'DESCRIPTION_TYPE'  : 1,#'tf',
        'STATES'            : 1,#2,
        #'NUM'               : [1.],
        #'DEN'               : [1., 6., 25.],
        'A'                  : [[1.]],#[[-6., -25.], [1., 0.]],
        'B'                  : [[0.]], #[[1.], [0.]],
        'C'                  : [[1.]], #[[0., 1.]],
        'D'                  : [[0.]],
        'GENERATE_STATES'   : False,
        'x0'                : [[1.]],#[[0.], [0.]], #[[0]]*KF_STATES,#array([[0.]]*2),       # Nx1
        'P0'                : [[1.]], #*eye(2, typecode='d'),           # NxN
        'Q'                 : [[1.]], # * eye(KF_STATES),         # NxN
        'R'                 : [[1.]]} # * eye(KF_OUTPUTS),        # qxq
    
    def __init__(self, *args, **kwords):
        self.__kf = None
        _LTI_BASE.__init__(self)#- , name=self.__class__.defaults['NAME'])
        
        af = self.parameters.append
        sc = self.__class__
        # set the name attribute
        self.name = sc.defaults['NAME']
        
        self['x0']          = sc.defaults['x0']
        self['P0']          = sc.defaults['P0']
        self['Q']           = sc.defaults['Q']
        self['R']           = sc.defaults['R']
        af(Parameter(name='signal_yv', value=0, tp=IntType))
        af(Parameter(name='signal_u', value=1, tp=IntType))
        # override some defaults
        self['states']              = sc.defaults['STATES']
        #self._lti                   = lti(sc.defaults['NUM'], sc.defaults['DEN'])
        af(Parameter(name='description type', value=sc.defaults['DESCRIPTION_TYPE'], tp=IntType))
        af(Parameter(name='generate states', value=sc.defaults['GENERATE_STATES'], tp=BooleanType))
##        self['description type']    = sc.defaults['DESCRIPTION_TYPE']
##        self['generate states']     = sc.defaults['GENERATE_STATES']
##        self._changeDescriptionType(sc.defaults['DESCRIPTION_TYPE'])
        
##        self['xAxisLabel']      = tr('frequency')
##        self['yAxisLabel']      = tr('magnitude')
##        self['xUnit']           = u'Hz'
##        self['yUnit']           = u''
        
        self.setProperties(kwords)
    
    def valuesChanged(self):
        states = self['states']
        _LTI_BASE.valuesChanged(self) # removes hold
        if len(self['x0']) != states:
            self['x0'] = [[0]]*states
        if len(self['P0']) != states:
            self['P0'] = eye(states).tolist()
        if len(self['Q']) != states:
            self['Q'] = eye(states, states).tolist()
        if len(self['R']) != 1:
            self['R'] = eye(1).tolist() #TODO: change it to qxq
        
        Q, R        = self['Q'], self['R']
        x0, P0      = array(self['x0']), self['P0']
        A, B, C, D  = self._lti.A, self._lti.B, self._lti.C, self._lti.D
        self.__kf = KalmanFilter(A, B, C, D, Q, R, x0, P0)
    
    def process(self, signals):
        if self.__kf==None:
            self.valuesChanged()
        
        if signals[self['signal_yv']]==None:
            if len(self.appendedSignalsList)==1:
                self['signal_yv']=self.appendedSignalsList[0]
            else:
                raise anasigError(tr('Connect signals first!') + ' ('
                        + tr('signal_yv') + ' not set)')
        
        s_yv = signals[self['signal_yv']]
        dyv = s_yv.get_dataY()
        
        #self['signal_u']
        if not len(signals) or len(signals)<(self['signal_u']+1):# or signals[self['signal_u']]==None:
            s_u = None
            du = None
        else:
            s_u = signals[self['signal_u']]
            du = s_u.get_dataY()
        
        # KalmanFilter.py
        yout, xout, K, P = self.__kf.process(dyv, du)
        # pNumeric version
#        Q, R        = Matrix(self['Q']), Matrix(self['R'])
#        x0, P0      = Matrix(self['x0']), Matrix(self['P0'])
#        A, B, C, D  = Matrix(self._lti.A.tolist()), Matrix(self._lti.B.tolist()), \
#                        Matrix(self._lti.C.tolist()), Matrix(self._lti.D.tolist())
#        x_est, y_est, P_est = kf_process(A, B, C, D, dyv, du, x0, P0, Q, R)
        
        sout = [] # output signals list
        if self['generate states']=='yes':
            xout = transpose(xout)
            i=1
            # take all system state variables
            for x in xout:
                out = Signal(fs=s_yv['fs'])
                out.set_data( x, None )
                out.name = self.name + u': ' + tr('state') + u' ' + str(i)
                i += 1
                sout.append(out)
        
        # output values
        out = Signal(fs=s_yv['fs'])
        out.set_data(transpose(yout)[0], None)
        out.name = self.name  + u': ' + tr('output')
        sout.append(out)
        
#        # kalman gain
#        Kout = transpose(K)
#        i=1
#        # take all system state variables
#        for k in Kout:
#            out = Signal(fs=s_yv['fs'])
#            out.set_data( k, None )
#            out.name = self.name + u': ' + tr('txt_gain') + u' ' + str(i)
#            i += 1
#            sout.append(out)
#        
        return sout

#####################################################################
#### resample
##class Instrument_Resample(InstrumentBase):
##    _subType = 'Resample'
##    def __init__ ( self, *args, **kwords ):
##        InstrumentBase.__init__( self, name='Resample')
##        self['number']       = 1024
##        self.setProperties(*args, **kwords)
##    
##    def process(self, signals):
##        InstrumentBase.process(self, signals)
##        sout = []
##        for sig in signals:
##            outSig = Signal()
##            outSig['name'] = 'Resampled (' + sig['name'] + ')'
##            
##            out = signaltools.resample(sig.dataY, self['number'])
##            outSig.set_data(out, None)
##            sout.append(outSig)
##        
##        return sout




FILTER_IIR_ALGORITHM = ('Butterworth', )




###################################################################
## FIR filter
class Instrument_FIR_Filter(InstrumentBase):
    _subType = 'FIRFilter'
    
    FILTER_FIR_ALGORITHM = ('Remez', 'windowing')
    FILTER_TYPE = ('lowpass', 'highpass')#'bandpass',  'bandstop')
    
    defaults = {
        'NAME'       : u'FIR',
        'TYPE'       : 0,   # FILTER_TYPE[0]
        'ORDER'      : 20,
        'F1'         : 0.2,
        'F2'         : 0.4,
        'DEN'        : [1.,6.,25.],
        'ALGORITHM'  : 0    # FILTER_FIR_ALGORITHM[0]
    }
    
    def __init__ ( self, *args, **kwords ):
        InstrumentBase.__init__( self, name=self.__class__.defaults['NAME'])
        
        af = self.parameters.append
        sc = self.__class__
        
        af(Parameter('type', sc.defaults['TYPE'], IntType, sc.FILTER_TYPE))
        self['filter_order']= sc.defaults['ORDER']
        self['f1']          = sc.defaults['F1'] # Hz
        self['f2']          = sc.defaults['F2'] # Hz
        af(Parameter('algorithm', sc.defaults['ALGORITHM'], IntType, sc.FILTER_FIR_ALGORITHM))
        self['xAxisLabel']  = tr('frequency')
        self['yAxisLabel']  = tr('magnitude')
        self['xUnit']       = 'Hz'
        self['yUnit']       = ''
        
        # nonsetable parameters
        self.__num            = 1. # FIR filter has always num=1!
        self.__den            = sc.defaults['DEN']
        self.setProperties(kwords)
##        self.generate()
    
    def __design(self):
        order = self['filter_order']
        ft = self['type']
        
        if self['algorithm']==0:    # remez
            if ft == 0:#'lowpass':
                dg = [1., 0.]
            if ft == 1:#'highpass':
                dg = [0., 1.]
            fq = [0., self['f1'], self['f2'], .5]
            out = signaltools.remez(order, fq, dg)
        elif self['algorithm']==1:  # windowing
            from scipy.signal.filter_design import firwin
            # N      -- order of filter (number of taps)
            # cutoff -- cutoff frequency of filter (normalized so that 1 corresponds 
            #           to Nyquist or pi radians / sample)
            out = firwin(order, self['f1'])
        self.__den = out
    
    def valuesChanged(self):
        self.__design()
    
    def process(self, signals):
        InstrumentBase.process(self, signals)
        sout = []
        for sig in signals:
            outSig = Signal()
            outSig.name = u'FIR (' + sig.name + u')'
            
            #new = signaltools.lfilter(self.num, self.den, sig.dataY)
            new = signaltools.convolve(sig.get_dataY(), self.__den)
            outSig.set_data(new, None)
            
            sout.append(outSig)
        
        self['xAxisLabel'] = sig['xAxisLabel']
        self['yAxisLabel'] = sig['yAxisLabel']
        
        return sout
    
    def getMenuItemsList(self):
        menu = [ {tr('impulse response') : self.ImpulseResponse} ]
        return menu
    
    def ImpulseResponse(self):
        sig = Signal()
        g = self.__den
        sig.set_data( g, range(0, len(self.__den)))
        sig.name = self.name + u': ' + tr('Impulse response')
        # send new signal to signal organiser
        getActiveWorkspace().SignalOrg.addProcessedItem(None, sig, True)




###################################################################
## Signal Generator
class SignalGenerator(InstrumentBase):
    """ signal generator class """
    _type = 'signalgenerator'    # object type
    
    defaults = {
        'NAME'     : u'generator',
        'FS'       : 1024.,
        'SAMPLES'  : 1024
    }
    
    def __init__(self, *args, **kwords):
        InstrumentBase.__init__(self)
        
        af = self.parameters.append
        sc = self.__class__
        
        self.name = sc.defaults['NAME']
        
        self['fs']              = sc.defaults['FS']      # sampling frequency
        self['samplescount']    = sc.defaults['SAMPLES'] # total samples count
        self.setProperties(kwords)
    
    def process(self, signals):
        return []
    
    def getMenuItemsList(self):
        menu = [ {tr("Generate") : [
            {tr('Constant') : self.mnuGenerateConstant},
            {tr('Sin') : self.mnuGenerateSin},
            {tr('Noise') : self.mnuGenerateNoise}
            ]}
        ]
        return menu
    
    def mnuGenerateSin(self):
        newsig = SignalSin(samplescount=self['samplescount'], fs=self['fs'])
        newsig.valuesChanged()
        newsig.name = self.name + u': ' + tr('Sin')
        getActiveWorkspace().SignalOrg.addProcessedItem(None, newsig, True)
    
    def mnuGenerateNoise(self):
        newsig = SignalNoise(samplescount=self['samplescount'], fs=self['fs'])
        newsig.valuesChanged()
        newsig.name = self.name + u': ' + tr('Noise')
        getActiveWorkspace().SignalOrg.addProcessedItem(None, newsig, True)
    
    def mnuGenerateConstant(self):
        newsig = SignalConstant(samplescount=self['samplescount'], fs=self['fs'])
        newsig.valuesChanged()
        newsig.name = self.name + u': ' + tr('Constant')
        getActiveWorkspace().SignalOrg.addProcessedItem(None, newsig, True)
