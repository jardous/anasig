#!/usr/bin/python
# -*- coding: utf-8 -*-

from globals import *
from pdebug import *

from dproperties import PropDlgBase
##from dpropinstrumentltiform import *
##from dpropinstrumentkalmanfilterform import *
from Numeric import array, identity, resize, Float
from scipy.signal.ltisys import ss2tf

from qt import SIGNAL, QWidget, QDialog, QTabDialog

TXT_STATESPACE = 'state space'
TXT_TRANSFERFUNC = 'transfer function'


class PropDlgBase:
    def __init__(self):
        pass

##################################################################
## function to get string from array
def getString(arr):
    ret = ''
    if len (arr.shape) == 2:
        arr = arr[0]
    
    for t in arr:
        ret = ret + str(t) + '  '
    
    ret = string.rstrip(ret)
    return ret

def setupMatrix(wg, mtr, rows, cols, default=None):
    """ sets values into QLineEdit arrays """
    ain = mtr.copy()
    if ain.shape != (rows, cols):
        if rows == cols:
            if default == None:
                ain = identity(rows)
            else: #TODO
                ain = array([[default]*rows]*cols)
        else:
            ain = resize(mtr, (rows, cols))        
    
    wg.vbox = QVBoxLayout( wg )
    wg.btn = []
    wg.boxLE = [] * rows
    
    for y in range(rows):
        wg.boxLE.append (QHBoxLayout( wg.vbox ))
        wg.btn.append([])
        for x in range(cols):
            tmp = QLineEdit( wg )
            tmp.setText("%f" % ain[y, x])
            wg.btn[y].append( tmp )
            wg.boxLE[y].addWidget(wg.btn[y][x])

def getMatrix(wg, matrixName):
    """ reread the values from array of QLineEdit """
    rows, cols = array(wg.btn).shape
    
    out = array([[0]*cols]*rows, Float)
    for y in range(rows):
        for x in range(cols):
            val, res = wg.btn[y][x].text().toFloat()
            if res == False:
                QMessageBox.information(wg, "Bad value", "Enter right " + matrixName + " matrix value, please, at pos: [" + str(y) + ", " + str(x) + "]")
                self.allOK = False
                return
            out[y,x] = val
    
    return out.tolist()

class setupMatrixDlg(QDialog):
    def __init__(self, matrix, rows, cols, name):
        QDialog.__init__(self)
        self.name = name
        self.setCaption(self.name)
        setupMatrix(self, matrix, rows, cols)
        self.bb = QHBoxLayout( self.vbox )
        self.btnCancel = QPushButton("&Cancel", self)
        self.bb.addWidget(self.btnCancel)
        self.connect( self.btnCancel, SIGNAL("pressed()"), self.btnCancelPressed)
        self.btnOk = QPushButton("O&K", self)
        self.bb.addWidget(self.btnOk)
        self.connect( self.btnOk, SIGNAL("pressed()"), self.btnOKPressed)

    def btnOKPressed(self):
        self.matrix = getMatrix(self, self.name)
        self.accept()#self.setResult(QDialog.Accepted)
    
    def btnCancelPressed(self):
        self.reject()
        #self.setResult(QDialog.Rejected)

class setupMatrixesDlg(QTabDialog):
    """ the state matrixes set values dialog """
    def __init__(self, parent, object, statesCount, inputsCount, outputsCount):
        self._object = object
        self._statesCount, self._inputsCount, self._outputsCount = statesCount, inputsCount, outputsCount
        QTabDialog.__init__(self, parent, TXT_STATESPACE + " matrixes", True)
        self.setCaption(TXT_STATESPACE + " matrixes")
        # setup widget A
        self.tabwgA = QWidget()
        setupMatrix (self.tabwgA, self._object.A, self._statesCount, self._statesCount)        
        self.addTab (self.tabwgA, "A")
        # setup widget B
        self.tabwgB = QWidget()
        setupMatrix (self.tabwgB, self._object.B, self._statesCount, self._inputsCount)
        self.addTab (self.tabwgB, "B")
        # setup widget C
        self.tabwgC = QWidget()
        setupMatrix (self.tabwgC, self._object.C, self._outputsCount, self._statesCount)
        self.addTab (self.tabwgC, "C")
        # setup widget D
        self.tabwgD = QWidget()
        setupMatrix (self.tabwgD, self._object.D, self._outputsCount, self._inputsCount, 0)
        self.addTab (self.tabwgD, "D")        

    def accept(self):
        self.allOK = True
        self.A = getMatrix(self.tabwgA, 'A')
        self.B = getMatrix(self.tabwgB, 'B')
        self.C = getMatrix(self.tabwgC, 'C')
        self.D = getMatrix(self.tabwgD, 'D')
        
        if self.allOK == True:
            QTabDialog.accept(self)

#################################################################################
class setupTFdlg(QTabDialog):
    def __init__(self, parent, ltss, inputs):
        QTabDialog.__init__(self, parent)
        self.setCaption(TXT_TRANSFERFUNC)
        self.setModal(True)
        
        self.widgets = []
        for i in range(inputs):
            try:
                num, den = ss2tf(ltss.A, ltss.B, ltss.C, ltss.D, i-1)
            except:
                num, den = ss2tf(ltss.A, ltss.B, ltss.C, ltss.D)
            
            wg = QWidget(self)
            wg.vbox = QVBoxLayout( wg )
            
            wg.hbox11 = QHBoxLayout( wg.vbox )
            wg.lblnum = QLabel( "numerator coeffs", wg)
            wg.hbox11.addWidget( wg.lblnum )
            
            wg.hbox1 = QHBoxLayout( wg.vbox )
            wg.txtnum = QLineEdit( wg )
            wg.txtnum.setText(getString(num))
            wg.hbox1.addWidget( wg.txtnum )
            
            wg.hbox21 = QHBoxLayout( wg.vbox )
            wg.lblden = QLabel( "denominator coeffs", wg )
            wg.hbox21.addWidget( wg.lblden )
            
            wg.hbox2 = QHBoxLayout( wg.vbox )
            wg.txtden = QLineEdit( wg )
            wg.txtden.setText(getString(den))
            wg.hbox2.addWidget( wg.txtden )        
            
            self.widgets.append(wg)
            self.addTab (wg, "input " + str(i+1))
        
        self.setCancelButton("&Cancel")

    def _getPoly(self, wg):
        out = []
        tmp = "%s" % wg.text()
        tmp = string.split(tmp)
        for str in tmp:
            try:
                out.append(eval(str))
            except:
                pass
        return out

    def accept(self):
        self.num = []
        self.den = []
        
        for wg in self.widgets:
            num = self._getPoly(wg.txtnum)
            den = self._getPoly(wg.txtden)
            
            if len(num) < 1 or len(den) < 1:
                return
            
            self.num.append ( array(num) )
            self.den.append ( array(den) )
        
        QDialog.accept(self)

###############################################################################
class DInstrumentLTIProperties(PropDlgBase):
    def __init__(self, inst):
        self.vw = DPropInstrumentLTIForm(globalVars['GMainForm'])
        self.vw.connect( self.vw.btnSetParams, SIGNAL("clicked()"), self.changeParamsSlot )
        self._object = inst
        self._fillByValues()
    
    def _fillByValues(self):
        self.vw.txtName.setText(self._object.name)
        self.vw.cmbSystemDescrType.insertItem(TXT_TRANSFERFUNC)
        self.vw.cmbSystemDescrType.insertItem(TXT_STATESPACE)
        self.vw.txtInputsCnt.setText("%d" % self._object.inputsCount)
        self.vw.txtOutputsCnt.setText("%d" % self._object.outputsCount)
        self.vw.txtStatesCnt.setText("%d" % self._object.statesCount)

    def changeParamsSlot(self):
        """ slot handles change params button click """
        if not self._CheckValues(): return
        
        if self.vw.cmbSystemDescrType.currentText() == TXT_STATESPACE:
            dlg = setupMatrixesDlg(self.vw, self._object, self.states, self.inputs, self.outputs)
            dlg.exec_loop()
            
            if dlg.result() == QDialog.Accepted:
                self._object.reinitialize(dlg.A, dlg.B, dlg.C, dlg.D)
            
        elif self.vw.cmbSystemDescrType.currentText() == TXT_TRANSFERFUNC:
            dlg = setupTFdlg(self.vw, self._object, self.inputs)
            dlg.exec_loop()
            if dlg.result() == QDialog.Accepted:
                self._object.reinitialize(dlg.num[0], dlg.den[0]) # TODO how to init MISO system?

    def _CheckValues(self):
        (self.states, ret) = self.vw.txtStatesCnt.text().toInt()
        if not ret or self.states <= 0: return False
        
        (self.inputs, ret) = self.vw.txtInputsCnt.text().toInt()
        if not ret or self.inputs <= 0: return False
        (self.outputs, ret) = self.vw.txtOutputsCnt.text().toInt()
        if not ret or self.outputs <= 0: return False
        
        return True

    def _setValues(self):
        self._object._statesCount = self.states
        self._object._inputsCount = self.inputs
        self._object._outputsCount = self.outputs

###############################################################################
class DInstrumentKalmanFilterProperties(PropDlgBase):
    def __init__(self, inst):
        self.vw = DPropInstrumentKalmanFilterForm(globalVars['GMainForm'])
        self.vw.connect( self.vw.btnSetParams, SIGNAL("clicked()"), self.changeParamsSlot )
        self.vw.connect( self.vw.btnSetx0, SIGNAL("clicked()"), self.changeMatrixx0 )
        self.vw.connect( self.vw.btnSetP0, SIGNAL("clicked()"), self.changeMatrixP0 )
        
        self._object = inst
        self._fillByValues()
##        # fill the ComboBox by LTI systems
##        plants = getAllItems(globalVars['GMainForm'].InstrumentOrg.medit, type='instrument', subtype='LTI')
##        plants = [p._object.name for p in plants]   # get names of items
##        filloutComboBox( self.vw.cbPlants, plants )
    
    def _fillByValues(self):
        self.vw.txtName.setText(self._object.name)
        self.vw.txtQ.setText("%f" % self._object.Q)
        self.vw.txtR.setText("%f" % self._object.R)
        self.vw.txtStatesCnt.setText("%d" % self._object.NSTATES)      
        self.vw.cmbSystemDescrType.insertItem(TXT_TRANSFERFUNC)
        self.vw.cmbSystemDescrType.insertItem(TXT_STATESPACE)
        self._x0 = self._object.x
        self._P0 = self._object.P

    def changeParamsSlot(self):
        """ slot handles change params button click """
        if not self._CheckValues(): return
        
        if self.vw.cmbSystemDescrType.currentText() == TXT_STATESPACE:
            dlg = setupMatrixesDlg(self.vw, self._object, self.states, 1, 1)
            
##            # setup widget C
##            dlg.tabwgx0 = QWidget()
##            setupMatrix (dlg.tabwgx0, self._object.x, self._outputsCount, 1)
##            dlg.addTab (dlg.tabwgx0, "x0")
##            # setup widget D
##            dlg.tabwgP0 = QWidget()
##            setupMatrix (dlg.tabwgP0, self._object.P, self._outputsCount, self._outputsCount, 0)
##            dlg.addTab (dlg.tabwgP0, "P0") 
            
            dlg.exec_loop()
            
        elif self.vw.cmbSystemDescrType.currentText() == TXT_TRANSFERFUNC:
            dlg = setupTFdlg(self.vw, self._object, 1)
            dlg.exec_loop()
            if dlg.result() == QDialog.Accepted:
                dlg.A, dlg.B, dlg.C, dlg.D = tf2ss(dlg.num[0], dlg.den[0]) # TODO how to init MISO system?
        
        if dlg.result() == QDialog.Accepted:
            self._object.reinitialize(dlg.A, dlg.B, dlg.C, dlg.D, self.Q, self.R, self._x0, self._P0)

    def changeMatrixx0(self):
        if self._CheckValues() == False: return
        dlg = setupMatrixDlg(self._object.x, self.states, 1, 'x0')
        dlg.exec_loop()
        if dlg.result() == QDialog.Accepted:
            self._object.x0 = dlg.matrix

    def changeMatrixP0(self):
        if self._CheckValues() == False: return
        dlg = setupMatrixDlg(self._object.P, self.states, self.states, 'P0')
        dlg.exec_loop()
        if dlg.result() == QDialog.Accepted:
            self._object.P0 = dlg.matrix
    
    def _CheckValues(self):
        (self.Q, ret) = self.vw.txtQ.text().toFloat()
        if not ret: return False
        
        (self.R, ret) = self.vw.txtR.text().toFloat()
        if not ret: return False
        
        (self.states, ret) = self.vw.txtStatesCnt.text().toInt()
        if not ret: return False
        
        return True

    def _setValues(self):
        self._object._Q = self.Q
        self._object._R = self.R
        self._object._statesCount = self.states
##        self._object.x0 = self._x0
##        self._object.P0 = self._P0    
