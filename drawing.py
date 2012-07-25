#!/usr/bin/python
# -*- coding: utf-8 -*-

from globals import *
from pdebug import *

##import matplotlib
##matplotlib.use('QtAgg') # need to set before importing pylab
from backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from qt import *

from Numeric import arange, sin, pi

import os
import sys
from sys import argv, exit
from pylab import *
from types import *

class anasigMPLcanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        #FigureCanvas.__init__(self, gcf())
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        # We want the axes cleared every time plot() is called
        self.axes.hold(False)
        
        FigureCanvas.__init__(self, self.fig)
        self.reparent(parent, QPoint(0, 0))
        FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
    def minimumSizeHint(self):
        return QSize(510, 307)
    def sizeHint(self):
        w, h = self.get_width_height()
        return QSize(w, h)
    def minimumSizeHint(self):
        return QSize(10, 10)



class anasigPicture(ItemBase, anasigWindow, QMainWindow):
    def __init__(self, parent=None, **kwords):
        QMainWindow.__init__(self, parent, "", Qt.WDestructiveClose)
        self.object = Chart()
        anasigWindow.__init__(self)
        self.sc = anasigMPLcanvas(self, width=5, height=4, dpi=80)
        self.sc.setFocus()
        self.setCentralWidget(self.sc)

    def contextMenuEvent(self, e):
        menu = QPopupMenu(self)
        menu.insertItem(tr('Save to file'), self.mnuSave)
        menu.insertItem(tr('Properties'), self.mnuProperties)
        menu.exec_loop(QCursor.pos())
    
    def mnuSave(self):
        dlg = QFileDialog(self)
        dlg.setCaption(tr('Save figure as'))
        dlg.setMode(QFileDialog.AnyFile)
        dlg.setDir(self.object.__class__.defaults['PLOT_DPI_LAST_DIR'])
        dlg.setSelection(self.object.__class__.defaults['PLOT_DPI_LAST_FILENAME'])
        
        if dlg.exec_loop()==QDialog.Accepted:
            file = dlg.selectedFile()
            file = str(file)
            path, filename = os.path.split(file)
        
        savefig(file, dpi=int(self['export dpi']))
        self.object.__class__.defaults['PLOT_DPI_LAST_DIR']       = path
        self.object.__class__.defaults['PLOT_DPI_LAST_FILENAME']  = file
    
    def drawSignals(self, signals, phold=False):
        if signals==None:
            raise anasigError(tr('No signals to plot'))
        
        self.__signals = signals
        self.__hold    = phold
       
        s1 = signals[0]
        
        xmin = s1.get_minX()#dx[0]
        xmax = s1.get_maxX()#max(dx)#[self.__signals[0].size-1]
        ymin = 1.1 * s1.get_minY()#min(dy)q
        ymax = 1.1 * s1.get_maxY()#max(dy)
        
        # get max and min axis values
        for sig in self.__signals:
            # TODO: get_dataX called twice - possible speed problem
            xmi = sig.get_minX()
            if xmi<xmin: xmin=xmi
            xma = sig.get_maxX()
            if xma>xmax: xmax=xma
            
            ymi = sig.get_minY()
            if ymi<ymin: ymin=ymi
            yma = sig.get_maxY()
            if yma>ymax: ymax=yma
        
        if len(signals)==1:
            sig = signals[0]
            if sig.get_size():
                self._subplot(sig.get_dataX(), sig.get_dataY(), label=sig.name)
            # print xaxis name (of first signal)
            xlbl = sig['xAxisLabel'] + u' [' + sig['xUnit'] + u']'
            ylbl = sig['yAxisLabel'] + u' [' + sig['yUnit'] + u']'
            self.sc.axes.set_xlabel(xlbl)#, font)
            self.sc.axes.set_ylabel(ylbl)#, font)
            self.sc.axes.set_title(sig.name)
            self.setCaption(sig.name)
        if len(signals) > 1: # print in one chart
            self.sc.axes.hold(True)
            # plot the signals
            for sig in self.__signals:
                self._subplot(sig.get_dataX(), sig.get_dataY(), label=sig.name)
            
        
    
    def _subplot(self, dx, dy, label=''):
        if self.object['charttype']==1:    # 'stem'
            self.sc.axes.stem(dx, dy)
        else:
            self.sc.axes.plot(dx, dy, label=label)
    
    def mnuProperties(self):
        getActiveWorkspace().PropestiesWnd.showProperties(self)



class Chart(ItemBase):
    _type = 'chart'
    
    CHART_TYPE  = ('line', 'stem')
    
    defaults = {
        'PLOT_NAME'             : u'chart',
        'PLOT_CHARTTYPE'        : 0,    # CHART_TYPE[0]
        'PLOT_GEOMETRY'         : [10, 10, 400, 300],
        'PLOT_LINEWIDTH'        : 1.2,
        'PLOT_DPI_SHOW'         : 80,
        'PLOT_DPI_SAVE'         : 80,
        'PLOT_DPI_LAST_DIR'     : '~',
        'PLOT_DPI_LAST_FILENAME': '',
        'PLOT_SHOW_LEGEND'      : False
    }
    
    def __init__(self, **kwords):
        ItemBase.__init__(self)
        
        af = self.parameters.append
        sc = self.__class__
        
        self.name = self.__class__.defaults['PLOT_NAME']
        af(Parameter('charttype', sc.defaults['PLOT_CHARTTYPE'], IntType, sc.CHART_TYPE))
        self['linewidth']     = sc.defaults['PLOT_LINEWIDTH']
        self['show legend']   = sc.defaults['PLOT_SHOW_LEGEND']
        self['display dpi']   = sc.defaults['PLOT_DPI_SHOW']
        self['export dpi']    = sc.defaults['PLOT_DPI_SAVE']
        self.setProperties(kwords)
    




# testing
if __name__ == "__main__":
    from signals import SignalSin
    s1 = SignalSin(samplescount=100, periods=1.5, gain=1.3)
    s1.name = 'aaa'
    s1.valuesChanged()
    s2 = SignalSin(samplescount=100, periods=3, gain=1.1)
    s2.name = 'bbb'
    s2.valuesChanged()
    
    a = QApplication(argv)
    
    aw = anasigPicture()
    #aw.setCaption("asdfsadfsadfsad")
    a.setMainWidget(aw)
    aw.setSignals((s1, s2))
##    aw.createWidget()
    aw.show()
    sys.exit(a.exec_loop())
