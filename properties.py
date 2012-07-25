#!/usr/bin/python
# -*- coding: utf-8 -*-

from globals import *
from logging import *

from qt import *

from qttable import *
import os
from types import *
from anasigError import anasigError

from dinstrumentproperties import *
from drawing import anasigPicture

##_tr_properties = {
QT_TR_NOOP("fs")
QT_TR_NOOP("linenumber")
QT_TR_NOOP("samplescount")
QT_TR_NOOP("file")
QT_TR_NOOP("averages")
QT_TR_NOOP("overlay")
QT_TR_NOOP("window")
QT_TR_NOOP("xAxisLabel")
QT_TR_NOOP("yAxisLabel")
QT_TR_NOOP("xUnit")
QT_TR_NOOP("yUnit")
QT_TR_NOOP("states")
QT_TR_NOOP("num")
QT_TR_NOOP("den")
QT_TR_NOOP("transfer function")
QT_TR_NOOP("state space")
QT_TR_NOOP("description type")
QT_TR_NOOP("generate states")
QT_TR_NOOP("channels")
QT_TR_NOOP("samplesize")
QT_TR_NOOP("state space")
##    
##    }

###############################################################################
## Main class (properties window without any widget)
class DProperties(QTable, anasigWindow):
    """instrument ograniser window"""
    name = 'Properties window' # needed for loadWindowPosition
    def __init__(self, parent):
        QTable.__init__(self, parent)
        anasigWindow.__init__(self)
        #Pickleable.__init__(self)
        self.setLeftMargin(0)
        #self.setTopMargin(0)
        self.setNumCols(2)
        self.setSelectionMode(QTable.SingleRow)
        self.setColumnReadOnly(0, True)
        self.setColumnStretchable(1, True)
        #self.hide()
        self.item = None
        
        self.languageChange()
    
    def closeEvent(self, e):
        self.emit(PYSIGNAL("closed()"), ())
    
    def showProperties(self, item=None):
        """
            fill Table in properties window by given item 
            item - Instrument, Signal or Chart object
        """
        # remove old table entries
        self.removeRows(range(self.numRows()))
        
        if isinstance(item, anasigPicture):
            pass#print 'props anasigPicture object'
        elif isinstance(item, QListViewItem):
            pass#print 'props QListViewItem object'
        
        if item:
            del self.item
            self.item = item # new item to show
        if not self.item:
            return # first call or unset
        
        self.propstochange = self.item.object.getParamsCopy()
        self.setNumRows(len(self.propstochange)+1) # extra line for ok/cancel buttons
        for i,p in enumerate(self.propstochange):
            self._insertProp(i, p, self.item)
        
        # Ok-Cancel button
        self._ocb = OkCancelButtonTableItem(self, self.OnOk, self.OnCancel)
        self.setItem(i+1, 1, self._ocb)
        self._ocb.setButtonsEnabled(False) # disable buttons by default
        self.myresize()
    
    def myresize(self):
        # resize to fit contents
        self.adjustColumn(0)
        self.adjustColumn(1)
        self.adjustSize()
        s = self.size()
        #print 'size', s.width(), s.height()
        s.setWidth(s.width()-1)
        #s.setHeight(s.height()-
        self.resize(s)
        #print 'end resizing'
    
    def _insertProp(self, idx, adt, qlistviewitem=None):
        """
            inserts value stored in adt (Parameter)
            idx - index (position in table)
            adt - Parameter object
        """
        # set name col
        tik = QTableItem(self, QTableItem.Never, self.__tr(adt.name))
        tik.key = adt.name
        self.setItem(idx, 0, tik)
        
        if adt.name in ('signal_yv', 'signal_u'):
            tiv = SignalsListTableItem(self, qlistviewitem, adt)
        elif adt.name=='file':
            tiv = FileButtonTableItem(self, '...', adt)
        elif adt.tuple!=None:
            tiv = ComboBoxTableItem(self, adt, self.emitChange)
        elif adt.type==BooleanType:
            tiv = CheckTableItem(self, adt)
        elif adt.type==ListType:  # in ('A', 'B', 'C', 'D', 'x0', 'P0', 'Q', 'R'):
            tiv = LineEditButtonTableItem(self, tr('set'), adt, _setupMatrixDlgShow)
        else:
            tiv = TextTableItem(self, adt)
        
        self.setItem(idx, 1, tiv)
    
    def emitChange(self):
        """ called when combobox item is changed """
        from instruments import Instrument_LTI, Instrument_Kalman_Filter
        o = self.item.object
        if isinstance(o, Instrument_Kalman_Filter) or isinstance(o, Instrument_LTI):
            pt = o['description type']
            # 0 - tf, 1 - ss
            if pt==0:
                self.hideRow(4)
                self.hideRow(5)
            elif pt==1:
                self.showRow(4)
                self.showRow(5)
            o._changeDescriptionType(pt)
            
            t = o['description type']
            i = o.parameters.index('description type') + 1
            if t==1:
                props = ('A', 'B', 'C', 'D')
            elif t==0:
                props = ('num', 'den')
            for v in range(len(props)):
                self._insertProp(v+2, o.parameters[i+v])
            self.myresize()
##        getActiveWorkspace().PropestiesWnd.showProperties(self.item)
##        io = getActiveWorkspace().InstrumentOrg
##        #find the item in instrument organiser
##        lvii = QListViewItemIterator(io)
##        while lvii.current():
##            if lvii.current().object == self.item.object:
##                item = lvii.current()
##                break
##            lvii += 1
        
    def OnOk(self):
        props = self.item.object.parameters
        for p in self.propstochange:
            if p.value != props[p.name].value:
                #print 'changing', p.name, p.value, props[p.name], 'X'
                props[p.name].setValue(p.value)
        # update item
        self.item.object.valuesChanged()
        self.showProperties() # update table
    
    def OnCancel(self):
        self.showProperties() # update table - redraw with original values
    
    def languageChange(self):
        self.setCaption(self.__tr('Properties'))
        self.horizontalHeader().setLabel(0, self.__tr('property'))
        self.horizontalHeader().setLabel(1, self.__tr('value'))
        # redraw all properties
        #self.showProperties()
    
    def __tr(self, s, c=None):
        return u"%s" % qApp.translate("DProperties", s, c)
    
    def toPickle(self):
        s = self.size()
        data = {'windowPosition':self.getListFromSize()}
        return data
    
    def fromPickle(self, p):
        self.setSizeFromList(p['windowPosition'])





class TableItem(QObject):
    """base class for all TableItems"""
    def __init__(self, adt=None):
        self._adt = adt
        if adt and adt.readOnly:
            self.setEnabled(False)
    
    def setText(self, txt):
        txt = QString(u'%s' % txt)
        QTableItem.setText(self, txt)
    
    def setContentFromEditor(self, w):
        self.table()._ocb.setButtonsEnabled(True)





###############################################################################
## text table item
class TextTableItem(QTableItem, TableItem):
    def __init__(self, table, adt, edittype=QTableItem.OnTyping):
        QTableItem.__init__(self, table, edittype)
        TableItem.__init__(self, adt)
        self.setText(self._adt.value)
    
    def setContentFromEditor(self, w):
        b = u'%s' % w.text()    # convert from QString to unicode string
        if self._adt.type(b)==self._adt.value:
            return              # value was not changed
        
        try:
            self._adt.setValue(b)
        except anasigError, e:
            QMessageBox.warning(None, tr("Bad value"), e.message)
            return
        self.setText(self._adt.value)
        
        TableItem.setContentFromEditor(self, w)




###############################################################################
## checkbox table item
class CheckTableItem(QCheckTableItem, TableItem):
    def __init__(self, table, adt, edittype=QTableItem.OnTyping):
        QCheckTableItem.__init__(self, table, '')
        TableItem.__init__(self, adt)
        #self.setText(self._adt.value)



###############################################################################
## LineEdit-Button table item
class LineEditButtonTableItem(QTableItem, TableItem):
    def __init__(self, table, btn_text, adt, fnc=None, edittype=QTableItem.OnTyping):
        QTableItem.__init__(self, table, edittype)
        TableItem.__init__(self, adt)
        self._btn_text = btn_text
        self._fnc      = fnc
        self.setText(self._adt.value)
    
    def createEditor(self):
        hbox = QHBox(self.table().viewport())
        self._edt = QLineEdit(hbox)
        self._btn = QPushButton(hbox)
        hbox.setFocusProxy(self._btn)
        self._btn.setText(tr(self._btn_text))
        s = QString(str(self._adt.value))
        self._edt.setText(s)
        self._btn.connect(self._btn, SIGNAL('clicked()'), self._btnClickedSLOT)
        return hbox
    
    def _btnClickedSLOT(self):
        if self._fnc:
            self._fnc(self._adt)
        self._edt.setText(str(self._adt.value))
    
    def setContentFromEditor(self, w):
        TableItem.setContentFromEditor(self, w)
        es = u"%s" % self._edt.text()
        try:
            es = eval(es)
        except SyntaxError:
            #return
            pass
        self._adt.setValue(es)
        self.setText(self._adt.value)





###############################################################################
## fileinput table item
class FileButtonTableItem(LineEditButtonTableItem):
    def __init__(self, table, btn_text, adt):
        LineEditButtonTableItem.__init__(self, table, btn_text, adt, self._btnClickedSLOT, QTableItem.OnTyping)
    
    def _btnClickedSLOT(self):
        dlg = QFileDialog(self._edt.text(), self._adt.fileFilter)
        if dlg.exec_loop()==QDialog.Accepted:
            filename = dlg.selectedFile()
            self._edt.setText(filename)
            self.setContentFromEditor(None)




###############################################################################
## combobox table item
class ComboBoxTableItem(QTableItem, TableItem):
    def __init__(self, table, adt, fnc=None):
        """
            @params:
                table - QTable object
                adt - Parameter object
                fnc - function to call when item changed
        """
        QTableItem.__init__(self, table, QTableItem.Always)
        TableItem.__init__(self, adt)
        self._fnc = fnc
    
    def createEditor(self):
        hbox = QHBox(self.table().viewport())
        self._cmb = QComboBox(False, hbox)
        hbox.setFocusProxy(self._cmb)
        # fill out the combo box
        for i in self._adt.tuple:
            iu = QString(tr(str(i)))
            self._cmb.insertItem(iu)
        
        # set current item
        if self._adt.value:
            curr = str(self._adt.tuple[self._adt.value])
            self._cmb.setCurrentText(QString(tr(curr)))
        
        self._cmb.connect(self._cmb, SIGNAL('activated(int)'), self._OnComboBoxChanged)
        return hbox
    
    def _OnComboBoxChanged(self, idx):
        """ called wheh combo item changed
            idx - index of new selected item
        """
        if not self._adt.callback:
            TableItem.setContentFromEditor(self, idx)
            self._adt.setValue(idx)
        else:
            self._adt.callback(idx)
        # item changed - call function
        if self._fnc:
            self._fnc()
    
    def setContentFromEditor(self, w):
        """do not call default TableItem.setContentFromEditor!"""
        pass




###############################################################################
## combobox table item
class SignalsListTableItem(QTableItem, TableItem):
    def __init__(self, table, lvitem, adt):
        """
            @params:
                table (QTable)
                lvitem - QListViewItem
                adt - anasig data type
        """
        QTableItem.__init__(self, table, QTableItem.Always)
        TableItem.__init__(self, adt)
        
        self._default = adt.value
        # get appended signals
        self._signals = []
        if lvitem.childCount():
            it = lvitem.firstChild()
            while it:
                self._signals.append(it)
                it = it.nextSibling()
    
    def createEditor(self):
        hbox = QHBox(self.table().viewport())
        self._cmb = QComboBox(False, hbox)
        hbox.setFocusProxy(self._cmb)
        # fill out the combo box
        self._cmb.insertItem('Please select')
        for lvsignal in self._signals:
            iu = lvsignal.object.name
            self._cmb.insertItem(QString(iu))
        
        # set current item
        df = self._default
        t = ''#tr('Please select')
        if df>=0:
            try:
                curr = self._signals[df]
                t = curr.object.name
            except:
                pass
            self._cmb.setCurrentText(QString(t))
        
        self._cmb.connect(self._cmb, SIGNAL('activated(int)'), self._OnComboBoxChanged)
        return hbox
    
    def _OnComboBoxChanged(self, idx):
        print '_OnComboBoxChanged'
        if idx==0:
            key = None # first position is ''!
        else:
            key = idx-1
        self._adt.setValue(key)




###############################################################################
## button table item
class ButtonTableItem(QTableItem, TableItem):
    def __init__(self, table, adt, call_function, btn_text):
        """
            @params
                call_function - fuction to call when button pressed
        """
        QTableItem.__init__(self, table, QTableItem.Always)
        TableItem.__init__(self, adt)
        self._btn_text = btn_text
        self._call_function = call_function
    
    def createEditor(self):
        hbox = QHBox(self.table().viewport())
        self._btn = QPushButton(hbox)
        hbox.setFocusProxy(self._btn)
        self._btn.setText(self.__tr(self._btn_text))
        self._btn.connect(self._btn, SIGNAL('clicked()'), self._action)
        return hbox
    
    def _action(self):
        """when button is pressed"""
        self.table().setCurrentCell(self.row(), self.col())
        ret = self._call_function()




###############################################################################
## Ok-Cancel button table item
class OkCancelButtonTableItem(QTableItem, TableItem):
    def __init__(self, table, fncOk, fncCancel):
        """
            @params
                call_function - fuction to call when button pressed
        """
        QTableItem.__init__(self, table, QTableItem.Always)
        TableItem.__init__(self)
        self._fncOk        = fncOk
        self._fncCancel    = fncCancel
    
    def createEditor(self):
        hbox = QHBox(self.table().viewport())
        self._btnOk = QPushButton( hbox )
        self._btnCancel = QPushButton( hbox )
        hbox.setFocusProxy(self._btnOk)
        hbox.setFocusProxy(self._btnCancel)
        self._btnOk.connect(self._btnOk, SIGNAL('clicked()'), self._OkAction)
        self._btnCancel.connect(self._btnCancel, SIGNAL('clicked()'), self._CancelAction)
        self.languageChange()
        return hbox
    
    def setButtonsEnabled(self, enabled):
        self._btnOk.setEnabled(enabled)
        self._btnCancel.setEnabled(enabled)
    
    def _OkAction(self):
        """when button is pressed"""
        self.table().setCurrentCell(self.row(), self.col())
        ret = self._fncOk()
    
    def _CancelAction(self):
        """when button is pressed"""
        self.table().setCurrentCell(self.row(), self.col())
        ret = self._fncCancel()
    
    def setContentFromEditor(self, w):
        """do not call default TableItem.setContentFromEditor!"""
        pass
    
    def languageChange(self):
        self._btnOk.setText(self.__tr("Use"))
        self._btnCancel.setText(self.__tr("Cancel"))
    
    def __tr(self, s, c=None):
        return u"%s" % qApp.translate("OkCancelButtonTableItem", s, c)




def _setupMatrixDlgShow(adt):
    parent = getActiveWorkspace()
    md = setupMatrixDlg(parent, adt.name)
    
    v = adt.value
    val = md.getValue(adt.value)
    
    if val!=None:
        adt.setValue(val)
        return val



def _setupTFDlgShow(adt):
    parent = getActiveWorkspace()
    md = setupPolyDlg(parent, tr(name))
    val = md.getValue(item)
    if val:
        return val
