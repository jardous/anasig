#!/usr/bin/python
# -*- coding: utf-8 -*-

from globals import *

from qt import *#QPopupMenu, QTextDrag, QListViewItemIterator, QListView, QCursor

from organizer import OrganizerItem, OrganizerItemView
from drawing import *
from signals_base import *
from signals import *
#from plugin import *

########################################################################
## View class
########################################################################

class DSignalOrganizer(OrganizerItemView):
    """
        signal ograniser ListView
    """
    name = 'Signal organizer window' # needed for loadWindowPosition
    def __init__(self, parent):
        OrganizerItemView.__init__(self, parent)
        self.setSelectionMode(QListView.Extended)
        self.languageChange()
    
    def contextMenuEvent(self, e):
        self.mousePressed = False
        contItem = self.itemAt(self.contentsToViewport(e.pos()))
        
        contextMenu = QPopupMenu(self)
        
        if contItem == None:
            submenu = QPopupMenu(self)
            submenu.insertItem(self.__tr('Matlab file'), self.mnuInsertMatlabFile)
            submenu.insertItem(self.__tr('Picklefile'), self.mnuInsertPickleFile)
            submenu.insertItem(self.__tr('WAV file'), self.mnuInsertWavFile)
            submenu.insertItem(self.__tr('text file'), self.mnuInsertTextFile)
            submenu.insertItem(self.__tr('Load anasig signal'), self.mnuLoadSignalFromFile)
            contextMenu.insertItem(self.__tr('Insert'), submenu)
        else:
            contextMenu.insertItem(self.__tr("Rename"), contItem.rename)
            
            il = contItem.object.getMenuItemsList()
            self.addMenuItems(contextMenu, il)
            
            contextMenu.insertItem(self.__tr('Plot together'), self._dropContextPlotTogether)
            contextMenu.insertItem(self.__tr('Plot separatelly'), self._dropContextPlotSeparatelly)
            
            contextMenu.insertItem(self.__tr('Delete'), self._dropContextDelete)
        
        contextMenu.exec_loop(QCursor.pos())

    def contentsDropEvent( self, e ):
        if not QTextDrag.canDecode(e) :
            e.ignore()
            return
        
        dropItem = self.itemAt( self.contentsToViewport( e.pos()) )
        if dropItem == None: return
        if not isinstance(e.source(), DSignalOrganizer): return
        if dropItem == self.draggedItem: return     # signal dropped onto itself
        
        self.tmpDropItem = dropItem
        
        contextMenu = QPopupMenu(self)
        submenu = QPopupMenu(self)
        
        contextMenu.insertItem(self.__tr("Add"), self._dropContextAdd)
        contextMenu.insertItem(self.__tr("Insert after"), self._dropContextInsertAfter)
        contextMenu.exec_loop(QCursor.pos())
        
        del self.tmpDropItem
        e.accept()

    def _dropContextAdd(self):
        x = self.draggedItem.object
        y = self.tmpDropItem.object
        
        xx = x['name']
        yy = y['name']
        
        if x._type != 'signal' or y._type != 'signal':
            return
        if x['xUnit'] != y['xUnit']:
            return
        
        # TODO dont know why, but '+' operator does not work... :(
        newSig = x.mix(y)
        self.addItem(self, newSig, True, self.draggedItem)

    def _dropContextInsertAfter(self):
        self.draggedItem.moveItem (self.tmpDropItem)

    def _getSelectedSignalsToPlot(self):
        """ returns list of all selected signal objects """
        stp = []
        iter = QListViewItemIterator(self)
        while(iter.current()):
            if iter.current().isSelected() == True:
                if iter.current().object._type == 'signal':
                    stp.append(iter.current().object)
            iter += 1
        
        return stp
    
    def _dropContextPlotTogether(self):
        stp = self._getSelectedSignalsToPlot()
        # plot the chart
        chart = anasigPicture(getActiveWorkspace())
        chart.drawSignals(stp, True)
        chart.show()
    
    def _dropContextPlotSeparatelly(self):
        stp = self._getSelectedSignalsToPlot()
        for s in stp:
            chart = anasigPicture(getActiveWorkspace())
            chart.drawSignals([stp], False)
            chart.show()
    
    def _dropContextDelete(self):
        stp = self._getSelectedItems()
        [a.delete() for a in stp]
    
    def contentsMouseDoubleClickEvent(self, e):
        item = self.itemAt(self.contentsToViewport(e.pos()))
        if not item: return
        
        if item.object._type == 'signal':
            chart = anasigPicture(getActiveWorkspace())
            chart.drawSignals( (item.object,) )
            #chart.createWidget()
            chart.show()
    
    def addProcessedItem(self, parent, procsig, selectable):
        self.addItem(self, procsig, True)
    
    def mnuInsertWavFile(self):
        self.addItem(self, SignalWavFile(), True)
    
    def mnuInsertTextFile(self):
        self.addItem(self, SignalTextFile(), True)
    
    def mnuInsertMatlabFile(self):
        self.addItem(self, SignalMatlabFile(), True)

    def mnuInsertPickleFile(self):
        self.addItem(self, SignalPickleFile(), True)
    
    def mnuLoadSignalFromFile(self):
        from itempickling import loadItemFromFile
        s = loadItemFromFile(type='signal')
        if s:
            self.addItem(self, s, True)
    
    def languageChange(self):
        self.setCaption(self.__tr('Signal organizer'))
    
    def __tr(self, s, c=None):
        return u"%s" % qApp.translate("DSignalOrganizer", s, c)
