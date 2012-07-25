#!/usr/bin/python
# -*- coding: utf-8 -*-

from globals import *
from pdebug import *

from dproperties import PropDlgBase

from dpropsignalgeneratorform import *
from dpropsignalsinform import *
from dpropsignalnoiseform import *
from dpropsignalform import *
from dpropsignalwavfileform import *

from Numeric import array
#from generator import *
import wave, struct
from os.path import join

#from qt import *

###############################################################################
##
class DSignalNoiseProperties(PropDlgBase):
    def __init__(self, signal):
        self.vw = DPropSignalNoiseForm(globalVars['GMainForm'])
        self.signal = signal
        
        self.vw.lblName.setText(u"name")
        self.vw.txtName.setText(signal.name)
        self.vw.lblFs.setText(u"sampling frequency")
        self.vw.lblFsVal.setText("%d" % signal.fs)
        self.vw.lblSamplesCount.setText(u"samples count")
        self.vw.txtSamples.setText("%d" % signal.samplescount)
        self.vw.lblUnit1.setText(u"unit")
        self.vw.txtUnit1.setText(signal.xUnit)
        self.vw.lblUnit2.setText(u"unit")
        self.vw.txtUnit2.setText(signal.yUnit)
        self.vw.lblMagnitude.setText(u"gain")
        self.vw.txtMagnitude.setText("%f" % signal.gain)

    def _CheckValues(self):
        self.unit1 = self.vw.txtUnit1.text()
        self.unit2 = self.vw.txtUnit2.text()
        
        (self.samplescount, ret) = self.vw.txtSamples.text().toInt()
        if not ret: return
        (self.gain, ret) = self.vw.txtMagnitude.text().toFloat()
        if not ret: return
        
        return True

    def _setValues(self):
        #self.signal.setData( None, Generator().generateNoise( samplescount, gain) )
        self.signal.xUnit = self.unit1
        self.signal.yUnit = self.unit2
        self.signal.gain = self.gain    

###############################################################################
##
class DSignalProperties(PropDlgBase):
    def __init__(self, signal):
        self.vw = DPropSignalForm(globalVars['GMainForm'])
        
        self.signal = signal
        
        self.vw.txtName.setText(signal.name)
        self.vw.lblFs.setText('sampling frequency' + '[' + 'Hz' + ']')
        self.vw.lblFsVal.setText("%d" % signal.fs)
        self.vw.lblSamplesCount.setText('samples count')
        self.vw.txtSamples.setText("%d" % signal.samplescount)
        self.vw.lblUnit1.setText('x unit')
        self.vw.txtUnit1.setText(signal.xUnit)
        self.vw.lblUnit2.setText('y unit')
        self.vw.txtUnit2.setText(signal.yUnit)

    def _CheckValues(self):
        self.unit1 = self.vw.txtUnit1.text()
        self.unit2 = self.vw.txtUnit2.text()
        
        (self.samplescount, ret) = self.vw.txtSamples.text().toInt()
        if not ret: return
        (self.gain, ret) = self.vw.txtMagnitude.text().toFloat()
        if not ret: return
        
        return True

    def _setValues(self):        #self.signal.setData( None, Generator().generateNoise( samplescnt, gain) )
        self.signal.xUnit = self.unit1
        self.signal.yUnit = self.unit2
        self.signal.gain = self.gain

###############################################################################
## sinus properties dialog
class DSignalSinProperties(PropDlgBase):
    def __init__(self, signal):
        self.vw = DPropSignalSinForm(globalVars['GMainForm'])
        self.signal = signal
        
        self.vw.txtName.setText(signal.name)
        self.vw.lblFs.setText('sampling frequency' + '[' + 'Hz' + ']')
        self.vw.lblFsVal.setText("%d" % signal.fs)
        self.vw.lblSamplesCount.setText('samples count')
        self.vw.txtSamples.setText("%d" % signal.samplescount)
        self.vw.lblUnit1.setText('x unit')
        self.vw.txtUnit1.setText(signal.xUnit)
        self.vw.lblPeriods.setText('periods')
        self.vw.txtPeriods.setText("%d" % signal.periods)
        self.vw.lblMagnitude.setText('magnitude')
        self.vw.txtMagnitude.setText("%d" % signal.magnitude)
        self.vw.lblUnit2.setText('y unit')
        self.vw.txtUnit2.setText(signal.yUnit)

    def _CheckValues(self):        
        self.unit1 = self.vw.txtUnit1.text()
        self.unit2 = self.vw.txtUnit2.text()
        
        (self.samplescount, ret) = self.vw.txtSamples.text().toInt()
        if not ret: return
        (self.gain, ret) = self.vw.txtMagnitude.text().toFloat()
        if not ret: return
        (self.periods, ret) = self.vw.txtPeriods.text().toFloat()
        if not ret: return
        
        return True

    def _setValues(self):
        self.signal.xUnit = self.unit1
        self.signal.yUnit = self.unit2
        self.signal.gain = self.gain
        self.signal.periods = self.periods
        self.signal.samplescount = self.samplescount

###############################################################################
## wav file properties dialog
class DSignalWavFileProperties(PropDlgBase):
    def __init__(self, signal):
        _methodName = '__init__'
        try:
            self.vw = DPropSignalWavFileForm(globalVars['GMainForm'])
        except:
            pass
        
        log("%s %s initialization" % (self.__class__, _methodName))
        log("type of signal: %s" % str(signal))
        self.signal = signal
        self._wavloadOK = False
        
        self.vw.txtName.setText(self.signal.name)
        self.vw.connect( self.vw.btnLoad, SIGNAL("clicked()"), self._btnLoadPressedSlot )

    def _btnLoadPressedSlot(self):
        fd = QFileDialog (join(ProgramVars['SIGNAL_WAV_PATH'], ProgramVars['SIGNAL_WAV_FILENAME']), "wav files (*.wav)")
        if fd.exec_loop() == QDialog.Accepted:
            filename = fd.selectedFile()
            fp = wave.open(str(filename), 'rb')
            self.signal['samplescount'] = fp.getnframes()
            self.signal['fs'] = fp.getframerate()
            self.signal['sample_size'] = fp.getsampwidth()
            self.signal['channels'] = fp.getnchannels()
            self.signal['filename'] = filename
            # TODO converting can take long time!
            #curprev = self.vw.cursor
            #self.vw.setCursor( Qt.BusyCursor )
            wavdata = fp.readframes(self.signal['samplescount']) # got string
            wavdata = array( struct.unpack("%dB"%(self.signal['samplescount']), wavdata) ) - 128.0
            self.signal.setData( None, wavdata )
            
            self.vw.txtLength.setText("%d" % self.signal['samplescount'])
            self.vw.txtSampleRate.setText("%f" % self.signal['fs'])
            self.vw.txtSampleSize.setText("%d" % self.signal['sample_size'])
            self.vw.txtChannels.setText("%d" % self.signal['channels'])
            self.vw.txtFile.setText("%s" % self.signal['filename'])
            
            ProgramVars['SIGNAL_WAV_PATH'] = fd.dirPath()
            ProgramVars['SIGNAL_WAV_FILENAME'] = filename
            
            fp.close()
            
            #self.vw.setCursor( curprev )
            
            self._wavloadOK = True

    def _CheckValues(self):
        return self._wavloadOK

###############################################################################
## signal generator properties dialog
class DSignalGeneratorProperties(PropDlgBase):
    def __init__(self, gen):
        self.vw = DPropSignalGeneratorForm(globalVars['GMainForm'])
        self.signal = gen
        
        self.vw.txtName.setText(gen.name)
        self.vw.txtFs.setText("%f" % gen.fs)
        self.vw.txtCnt.setText("%d" % gen.samplescount)

    def _CheckValues(self):
        (self.fs, ret) = self.vw.txtFs.text().toFloat()
        if not ret: return
        (self.samplescount, ret) = self.vw.txtCnt.text().toInt()
        if not ret: return
        
        return True

    def _setValues(self):
        self.signal.fs = self.fs
        self.signal.samplescount = self.samplescount
