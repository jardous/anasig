#!/usr/bin/python
# -*- coding: utf-8 -*-

from globals import *
from pdebug import *

from qt import *
from types import ListType, DictType

from signals import *
from instruments import *

########################################################################
## ListView widget
########################################################################
class OrganizerItemView(QListView, anasigWindow):
    """ base class for organizer views """
    draggedItem = None
    
    def __init__( self, parent=None):
        QListBox.__init__(self, parent)
        anasigWindow.__init__(self)
        self.dropItem = 0
        self.presspos = QPoint(0,0)
        self.mousePressed = False
        
        self.setAcceptDrops( True )
        self.viewport().setAcceptDrops(True)
        self.setResizeMode(QListView.AllColumns)
        self.setSelectionMode(QListView.Single)
        self.addColumn('items')
        self.setColumnWidthMode(0, QListView.Maximum)
        self.header().hide()
        self.setAllColumnsShowFocus( True )
        #self.setTreeStepSize( 20 )
        self.setUpdatesEnabled( True )
        self.setSorting(-1, True)   # do not sort
##        self.connect(self, SIGNAL("clicked(QListViewItem*)"),
##                     self.clicked)
    
##    def clicked(self, i):
##        getActiveWorkspace().PropestiesWnd.showProperties(i)
    def contentsMousePressEvent(self, e):
        QListView.contentsMousePressEvent(self, e)
        
        p = QPoint(self.contentsToViewport(e.pos()))
        i = self.itemAt( p )
        
        if i == None: return # nothing to do in not clicked to item
        
        if self.rootIsDecorated(): isdecorated = 1
        else : isdecorated = 0
        if p.x() > self.header().sectionPos( self.header().mapToIndex( 0 )) + self.treeStepSize() * ( i.depth() + isdecorated + self.itemMargin() or
           p.x() < self.header().sectionPos( self.header().mapToIndex( 0 ) ) ) :
           self.presspos.setX(e.pos().x())
           self.presspos.setY(e.pos().y())
           self.mousePressed = True
    
    def contentsMouseReleaseEvent(self, e):
        p = QPoint(self.contentsToViewport(e.pos()))
        i = self.itemAt(p)
        
        if i:
            getActiveWorkspace().PropestiesWnd.showProperties(i)
##            i.object.propertiesShow()
        
        self.mousePressed = False
    
    def contentsMouseMoveEvent(self, e):
        offset = QPoint( self.presspos.x() - e.pos().x(), self.presspos.y() - e.pos().y() )    
        if self.mousePressed and (offset).manhattanLength() > qApp.startDragDistance():
            self.mousePressed = False
            i = self.itemAt( self.contentsToViewport(self.presspos) )
            # only signals can be dragged
            if i.object._type!='signal': return
            
            if i == None: return
            i.setSelected(False)
            self.draggedItem = i
            d = QTextDrag(i.object.name, self) # keep a reference to d
            d.drag()
    
    def contentsDragLeaveEvent(self, QDragLeaveEvent):
        self.dropItem = 0
    
    def addItem(self, parent, item, selectable, after=None):
        """ add item to organizer 
            @params:
                parent - parent item
        """
        self.contItem = None
        if isinstance(parent, QListViewItem):
            parent.setOpen(True)
        
        # insert item as last child
        if after == None:
            myChild = parent.firstChild()
            while( myChild ):
                after = myChild
                myChild = myChild.nextSibling();
        
        it = OrganizerItem(parent, item, after)
        it.setSelectable(selectable)
        
##        it.object.propertiesShow()
        getActiveWorkspace().PropestiesWnd.showProperties(it)
    
    def _getSelectedItems(self):
        """ find out and return selected items in organizer """
        out = []
        iter = QListViewItemIterator(self)
        while(iter.current()):
            if iter.current().isSelected()==True:
                out.append(iter.current())
            iter += 1
            
        return out
    
    def closeEvent(self, e):
        self.emit(PYSIGNAL("closed()"), ())
    
    def addMenuItems(self, menu, itemlist):
        """create menu from given itemlist structure"""
        for i in itemlist:
            items = i.items()[0]
            if type(items[1])==ListType:
                submenu = QPopupMenu(menu)
                p = menu.parentWidget()
                self.addMenuItems(submenu, items[1])
                menu.insertItem(tr("Insert"), submenu)
            else:
                menu.insertItem(items[0], items[1])
    
    def __tr(self, s, c=None):
        return u"%s" % qApp.translate("Organizer", s, c)
    
    def toPickle(self):
        childs = []
        iter = QListViewItemIterator(self)
        p = {}
        while(iter.current()):
            o = iter.current().object
            childs.append(o)#.toPickle(p))
            iter += 1
        
        #s = self.size()
        data = {#'windowPosition':self.getListFromSize(),
                'childs':childs
            }
        
        return data
    
    def fromPickle(self, p):
        childs = p['childs']
        for ch in childs:
##            ni = eval(ch['classname'])
            self.addItem(self, ch, True)




########################################################################
## Organizer item - represents items in organizer
########################################################################
class OrganizerItem(QListViewItem):
    """organizer item class"""
    def __init__( self, parent, item, after=None):
        QListViewItem.__init__( self, parent, after)
        self.setText(0, item.name)
        
        self.object = item
        self.__parent = parent
        
        lv = parent
        if isinstance(parent, OrganizerItem):
            lv = parent.listView()
            parent.object.appendedSignalsList.append(item)
    
    def clicked(self):
        print 'clicked'
    
    def contentsMouseReleaseEvent(self, QMouseEvent):
        self.mousePressed = False
    
    def text(self, col=0):
        if hasattr(self, 'object'):
            return self.object.name
        return QListViewItem.text(self, col)
    
    def rename(self):
        self.setRenameEnabled(0, True)
        self.startRename(0)
        #self.setRenameEnabled(0, False)
    
    def okRename(self, col):
        try:
            QListViewItem.okRename(self, col)
            txt = u'%s' % self.text(1)
            #print 'changing name to', txt
            self.object.setName(txt)
        except:
            #self.setText(0, self.object.name)
            pass
    
    def delete(self):
        lv = self.listView()
        parent = self.parent()
        
        if parent ==  None:
            parent = lv
        
##        ret = QMessageBox.question(lv, "Delete signal", 
##                    "Do you really want to delete selected signals?",
##                    "&Yes", "&No", "",  0, 1)
        ret = 0
        if ret == 0:
            # delete ref from properties window
            pd = getActiveWorkspace().PropestiesWnd
            
            if pd.item == self.object:
##                pd.object = None
                del pd.item
                getActiveWorkspace().PropestiesWnd.showProperties(None) # show none properties
            
            try:
                pr = self.__parent.object
                # delete itself from instrument appended signals
                for child in pr.appendedSignalsList:
                    if child == self.object:
                        del child
                # delete itself from possible instrument signal
                #TODO: put this into instrument class
                if pr['signal_in'] == self.object: pr['signal_in']=None
                if pr['signal_mu'] == self.object: pr['signal_mu']=None
                if pr['signal_process_noise'] == self.object: pr['signal_in']=None
                if pr['signal_measure_noise'] == self.object: pr['signal_in']=None
            except:
                pass
            
            if lv.contItem == self:
                lv.contItem = None
            
            #del self.object
            item = parent.takeItem(self)     # delete from ListView
            del item
