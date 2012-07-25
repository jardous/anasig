# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'dforms/dorganiserform.ui'
#
# Created: Mon Oct 25 20:31:45 2004
#      by: The PyQt User Interface Compiler (pyuic) 3.13
#
# WARNING! All changes made in this file will be lost!


from qt import *


class DOrganiserForm(QDialog):
    def __init__(self,parent = None,name = None,modal = 0,fl = 0):
        QDialog.__init__(self,parent,name,modal,fl)

        if not name:
            self.setName("DOrganiserForm")
        
        self.listItems = QListView(self,"listItems")
        self.listItems.addColumn(self.__tr("Column 1"))
        self.listItems.setGeometry(QRect(0,10,160,301))
        self.listItems.setBackgroundOrigin(QListView.WidgetOrigin)
        self.listItems.setAcceptDrops(0)
        self.listItems.setFrameShape(QListView.WinPanel)
        self.listItems.setFrameShadow(QListView.Sunken)
        self.listItems.setResizePolicy(QListView.AutoOneFit)
        self.listItems.setVScrollBarMode(QListView.Auto)
        self.listItems.setSelectionMode(QListView.Extended)
        self.listItems.setShowSortIndicator(0)
        self.listItems.setRootIsDecorated(1)
        self.listItems.setResizeMode(QListView.AllColumns)
        self.listItems.setTreeStepSize(6)
        
        self.languageChange()
        
        self.resize(QSize(172,325).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

    def languageChange(self):
        self.setCaption(self.__tr("organiser"))
        self.listItems.header().setLabel(0,self.__tr("Column 1"))
        self.listItems.clear()
        item = QListViewItem(self.listItems,None)
        item.setText(0,self.__tr("New Item"))



    def __tr(self,s,c = None):
        return qApp.translate("DOrganiserForm",s,c)
