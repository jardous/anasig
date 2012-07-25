#!/usr/bin/python
# -*- coding: utf-8 -*-

from globals import *

#from qt import *
from PyQt4 import *

from dmainform import MainForm

from signalorganizer import DSignalOrganizer
from instrumentorganizer import DInstrumentOrganizer
from properties import DProperties

appName = 'signal analyser'

import pickle

class anasigWorkspace(QWorkspace):
    def __init__(self, parent):
        QWorkspace.__init__(self, parent)
        self.InstrumentOrg = DInstrumentOrganizer(self)
        self.SignalOrg = DSignalOrganizer(self)
        self.PropestiesWnd = DProperties(self)

class MDIWindow(QMainWindow):
    def __init__(self, parent, name, wflags):
        QMainWindow.__init__(self, parent, name, wflags)
        #self.project = anasigProject()
        self.name       = tr('New project')
        self.filename   = ''
        self.ws = anasigWorkspace(self)
        self.setFocusProxy(self.ws)
        self.setCentralWidget(self.ws)
        self.is_modified = False
    
    def load(self, fn):
        self.filename  = fn
        
        f = open(self.filename, 'r')
        td = pickle.load(f)
        f.close()
        # place windows
        self.setChildWindowsPosition(td)
        # load intrument and signal organiser items
        self.ws.InstrumentOrg.fromPickle(td['InstrumentOrg'])
        self.ws.SignalOrg.fromPickle(td['SignalOrg'])
        
        self.setCaption(self.filename)
        self.emit(PYSIGNAL("message"), (QString(self.__tr("Loaded document")), 2000))
    
    def setChildWindowsPosition(self, td):
        self.name       = td['name']
        self.filename   = td['filename']
        self.ws.InstrumentOrg.setSizeFromList(td['InstrumentOrgPos'])
        self.ws.SignalOrg.setSizeFromList(td['SignalOrgPos'])
        self.ws.PropestiesWnd.setSizeFromList(td['PropestiesWndPos'])
        self.setCaption(self.__tr(self.name))
        
##        self.ws.InstrumentOrg.fromPickle(td['InstrumentOrg'])
##        self.ws.SignalOrg.fromPickle(td['SignalOrg'])
    
    def save(self):
        td = {'name':self.name,
                'filename':self.filename,
                'InstrumentOrgPos':self.ws.InstrumentOrg.getListFromSize(),
                'SignalOrgPos':self.ws.SignalOrg.getListFromSize(),
                'PropestiesWndPos':self.ws.PropestiesWnd.getListFromSize(),
                # fill the organizers
                'InstrumentOrg':self.ws.InstrumentOrg.toPickle(),
                'SignalOrg':self.ws.SignalOrg.toPickle(),
                #'PropestiesWnd':self.ws.PropestiesWnd.toPickle(),
        }
        
        if not self.filename:
            fn = QFileDialog.getSaveFileName(self.filename, QString.null, self)
            self.filename = str(fn)
        
        f = open(self.filename, 'w')
        pickle.dump(td, f)
        f.close()
        self.emit(PYSIGNAL("message"), (QString(self.__tr("Document saved")), 2000))
    
    def saveAs(self):
        fn = QFileDialog.getSaveFileName(self.filename, QString.null, self)
        if not fn.isEmpty():
            self.filename = fn
            self.save()
        else:
            self.emit(PYSIGNAL("message"), (QString(self.__tr("Saving aborted")), 2000))
    
    def closeEvent(self, e):
        if (self.is_modified):
            ret = QMessageBox.warning( self, tr("Save Changes"), tr("Save changes to "+str(self.caption())+"?"),
                tr("Yes"), tr("No"), tr("Cancel") )
            if ret==0:
                self.save()
                if not self.filename=='':
                    e.accept()
                else:
                    e.ignore()
            elif ret==1:
                e.accept()
            else:
                e.ignore()
        else:
            e.accept()
    
    def __tr(self, s, c=None):
        return u"%s" % qApp.translate("MDIWindow", s, c)






class anasigMainWindow(MainForm):
    def __init__(self):
        MainForm.__init__(self)
        
        # initialize controls
##        self.vb = QVBox(self)
##        self.vb.setFrameStyle(QFrame.StyledPanel | QFrame.Sunken)
        self.ws = QWorkspace(self)#.vb)
        self.ws.setScrollBarsEnabled(False)
        self.setCentralWidget(self.ws)#.vb)
        
        self.statusBar().message(tr("Ready"), 2000)

    def fileNew(self):
        nd = self.newDoc()
        td = {  'name':"unnamed document",
                'filename':'',
                'InstrumentOrgPos': [10, 10, 170, 250],
                'SignalOrgPos':     [190, 10, 170, 250],
                'PropestiesWndPos': [370, 10, 270, 250]
            }
        nd.setChildWindowsPosition(td)
    
    def newDoc(self):
        w = MDIWindow(self.ws, "", Qt.WDestructiveClose)
        self.connect(w, PYSIGNAL("message"), self.message)#self.statusBar(), 
            #SLOT("message(const QString&, int)"))
        #w.setCaption(self.__tr("unnamed document"))
        #w.setIcon( QPixmap("document.xpm") )
        # show the very first window in maximized mode
        if len(self.ws.windowList())==0:
            w.showMaximized()
        else:
            w.show()
        return w
    
    def message(self, m, t):
        self.statusBar().message(m, t)
    
    def fileOpen(self):
        fn = QFileDialog.getOpenFileName("", "", self)
        if not fn.isEmpty():
            w = self.newDoc()
            w.load(str(fn))
        else:
            self.statusBar().message(self.__tr("Loading aborted"), 2000)
    
    def fileSave(self):
        m = self.ws.activeWindow()
        if m:
            m.save()
    
    def fileSaveAs(self):
        m = self.ws.activeWindow()
        if m:
            m.saveAs()
    
    def closeWindow(self):
        m = self.ws.activeWindow()
        if m:
            m.close()
    
    def fileExit(self):
        windows = self.ws.windowList()
        if len(windows):
            for i in range(len(windows)):
                window = windows[i]
                if not window.close():
                    return
        self.close()
    
    def about(self):
        QMessageBox.about( self, "Qt Application Example",
                        "This example demonstrates simple use of\n "
                        "Qt's Multiple Document Interface (MDI).")
    
    def closeWindow(self):
        m = self.ws.activeWindow()
        if m:
            m.close()
    
    def windowsMenuAboutToShow(self):
        self.windows.clear()
        cascadeId = self.windows.insertItem(self.__tr("&Cascade"), self.ws, SLOT("cascade()"))
        tileId = self.windows.insertItem(self.__tr("&Tile"), self.ws, SLOT("tile()"))
        if  len(self.ws.windowList())==0 :
            self.windows.setItemEnabled( cascadeId, False )
            self.windows.setItemEnabled( tileId, False )
        self.windows.insertSeparator()
        windows = self.ws.windowList()
        cnt=0
        for i in windows:
            id =self.windows.insertItem(i.caption(),self.windowsMenuActivated )
            self.windows.setItemParameter( id, cnt )
            self.windows.setItemChecked( id, self.ws.activeWindow() == i )
            cnt=cnt+1

    def windowsMenuActivated(self, id):
        w = self.ws.windowList().at(id)
        if w:
            w.showNormal()
            w.setFocus()
    
    def closeEvent(self, e):
        """main window close event handler"""
        windows = self.ws.windowList()
        if len(windows):
            for i in range(len(windows)):
                window = windows[i]
                if not window.close():
                    e.ignore()
                    return
        e.accept()
