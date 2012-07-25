#!/usr/bin/python
# -*- coding: utf-8 -*-

from globals import *

from qt import *#QCursor, QMessageBox, QPopupMenu, QTextDrag, PYSIGNAL, QListViewItemIterator

from organizer import OrganizerItemView
from signalorganizer import DSignalOrganizer
from instruments import *


########################################################################
## View class
########################################################################
class DInstrumentOrganizer(OrganizerItemView):
    """
        instrument ogranizer ListView
    """
    name = 'Instrument organizer window' # needed for loadWindowPosition
    def __init__(self, parent):
        OrganizerItemView.__init__(self, parent)
        self.parent = parent
        
        self.languageChange()
    
    def contentsDropEvent( self, e ):
        if not QTextDrag.canDecode(e) :
            e.ignore()
            return
        
        dropitem = self.itemAt(self.contentsToViewport( e.pos()))
        if dropitem == None: return
        
        if dropitem.depth() > 0: 
            return
        
        if isinstance(e.source(), DSignalOrganizer):
            source = getActiveWorkspace().SignalOrg
        elif isinstance(e.source(), DInstrumentOrganizer):
            source = getActiveWorkspace().InstrumentOrg
        
        sourceItem = source.draggedItem
        
        selectable = True
        self.addItem ( dropitem, sourceItem.object, selectable )
        
        # unselect all the items
        lvii = QListViewItemIterator(self)
        while lvii.current():
            lvii.current().setSelected(False)
            lvii += 1
        
        if sourceItem:
            e.accept()
        else:
            e.ignore()
    
    def contentsMouseDoubleClickEvent(self, e):
        item = self.itemAt( self.contentsToViewport(e.pos()) )
        if not item: return
        
        sigsToProcess = []
        if item.depth() != 0:   # clicked on signal (process this signal only)
            itemProcess = item.parent()
            child = item
            sigsToProcess.append(child.object)
        else:   # clicked on instrument (process all signals)
            itemProcess = item
            child = itemProcess.firstChild()
            
            while child:
                sigsToProcess.append(child.object)
                child = child.nextSibling()
        
        try:
            osig = itemProcess.object.process(sigsToProcess)
        except anasigError, e:
            QMessageBox.information(self, self.__tr('Error'), e.message)
            return
        
        for s in osig:
            # send the signal to signal organizer
            getActiveWorkspace().SignalOrg.addProcessedItem(itemProcess, s, True)
    
    def contextMenuEvent(self, e):
        self.mousePressed = False
        contItem = self.itemAt( self.contentsToViewport(e.pos()) )
        
        contextMenu = QPopupMenu(self)
        submenu = QPopupMenu(self)
        
        if contItem == None:
            submenu.insertItem(self.__tr("FFT"), self.mnuFFT)
            submenu.insertItem(self.__tr("LTI"), self.mnuLTI)
            submenu.insertItem(self.__tr("Kalman Filter"), self.mnuKalmanFilter)
            submenu.insertItem(self.__tr("FIR filter"), self.mnuFIRfilter)
            submenu.insertItem(self.__tr("generator"), self.mnuInsertGenerator)
            contextMenu.insertItem(self.__tr("Insert"), submenu)
        else: # item menu requested
            contextMenu.insertItem(self.__tr("Rename"), contItem.rename)
            
            il = contItem.object.getMenuItemsList()
            self.addMenuItems(contextMenu, il)
                
            contextMenu.insertItem(self.__tr("Delete"), contItem.delete)
            #contextMenu.insertItem(self.__tr("Properties"), contItem.object.propertiesShow)
        
        contextMenu.exec_loop(QCursor.pos())
    
    def _createInstrument(self, inst):
        self.addItem(self, inst, True)
    
    def mnuFFT(self):
        self.addItem(self, Instrument_FFT(), True)
    
    def mnuLTI(self):
        self.addItem(self, Instrument_LTI(), True)
    
    def mnuKalmanFilter(self):
        self.addItem(self, Instrument_Kalman_Filter(), True)
    
    def mnuFIRfilter(self):
        self.addItem(self, Instrument_FIR_Filter(), True)
    
    def mnuInsertGenerator(self):
        self.addItem(self, SignalGenerator(), True)
    
    def languageChange(self):
        self.setCaption(self.__tr('Instrument organizer'))
    
    def __tr(self, s, c=None):
        return u"%s" % qApp.translate("DInstrumentOrganizer", s, c)
