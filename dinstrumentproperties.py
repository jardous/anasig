#!/usr/bin/python
# -*- coding: utf-8 -*-

from globals import *
from qt import *

from Numeric import Float

def getShape(mx):
    """return shape (rows, cols) of list/array object
           c  o  l  s
        r |a11 a12 a13|
        o |a21 a22 a23|
        w |a31 a32 a33|
    """
    rows = len(mx)
    try:
        cols = len(mx[0])
    except TypeError: # not 2D object
        cols = 0
    
    return (rows, cols)




def normalize(mx):
    """return copy of matrix or matrix from scalar, list, ... (makes 2D object from non 2D)"""
    out = []
    try:
        cols = len(mx[0])
        out = mx[:] # make copy of list array
    except TypeError: # not 2D object
        out.append(mx)
    
    return out




def _setupMatrix(wg, mtr, rows, cols, default=None):
    """fill out the QLineEdit arrays by values"""
    wg.vbox = QVBoxLayout(wg)
    wg.btn = []
    wg.boxLE = []*rows
    
    n = normalize(mtr)
    rows, cols = getShape(n)
    
    for y in range(rows):
        wg.boxLE.append(QHBoxLayout(wg.vbox))
        wg.btn.append([])
        for x in range(cols):
            tmp = QLineEdit(wg)
            
            li = n[y][x]
            
            tmp.setText(str(li))
            tmp.setValidator(QDoubleValidator(tmp))
            wg.btn[y].append(tmp)
            wg.boxLE[y].addWidget(wg.btn[y][x])




def _getMatrix(wg, rows, cols):
    """reread the values from array of QLineEdit"""
    out = array([[0]*cols]*rows, Float)
    for y in range(rows):
        for x in range(cols):
            val, res = wg.btn[y][x].text().toFloat()
            if res == False:
                QMessageBox.information(wg, 
                            tr('Bad value'),
                            tr('You entered bad value')+' '+tr('at pos')+': [' + str(y)
                            + ', ' + str(x) + ']' + '!')
                return
            out[y,x] = val
    
    if rows==0:
        return out[0].tolist()
    
    return out.tolist()




class setupMatrixDlg:
    """dialog for matrix/poly input"""
    def __init__(self, parent, name=''):
        self.__parent = parent
        self.__name = name
    
    def getValue(self, default):
        """returns the new value entered"""
        mx = normalize(default)
        rows, cols = getShape(mx)
        
        while(1): # repeat until correct values has been set
            succ_code = self.__showDlg(default, rows, cols)
            succ_code = bool(succ_code)
            if succ_code==True: # pressed OK
                matrix = _getMatrix(self.wg, rows, cols)
                if matrix:
                    return matrix
            else: # Cancel button pressed
                return None
    
    def __showDlg(self, default, rows, cols):
        self.dl = QDialog(self.__parent)
        self.dl.setCaption(self.__name)
        
        self.vbox = QVBoxLayout( self.dl )
        self.bb1 = QHBoxLayout( self.vbox )
        self.wg = QWidget( self.dl )
        _setupMatrix(self.wg, default, rows, cols)
        self.bb1.addWidget(self.wg)
        
        self.bb2 = QHBoxLayout( self.vbox )
        self.btnCancel = QPushButton("&Cancel", self.dl)
        self.bb2.addWidget(self.btnCancel)
        self.dl.connect( self.btnCancel, SIGNAL("pressed()"), self.btnCancelPressed)
        self.btnOk = QPushButton("O&K", self.dl)
        self.bb2.addWidget(self.btnOk)
        self.dl.connect( self.btnOk, SIGNAL("pressed()"), self.btnOKPressed)
        
        self.dl.exec_loop()
        return self.__succ_code
    
    def btnOKPressed(self):
        self.dl.hide()
        self.__succ_code = 1
    
    def btnCancelPressed(self):
        self.dl.hide()
        self.__succ_code = 0

