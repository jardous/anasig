#!/usr/bin/python
# -*- coding: utf-8 -*-

#__debug__ = True

from qt import *

from types import ObjectType, IntType
from Numeric import array, transpose
from MLab import eye
import cPickle
import os
import gettext
from string import *


def tr(s, c=None):
    #return u"%s" % qApp.translate("@default", str(s), c)
    return s

PLUGIN_DIR = 'plugin'
plugins = []

globalVars = {}


class Parameter:
    """anasig data type"""
    def __init__(self, name, value, tp=None, tpl=None, callback=None):
        """ 
            tp - type of data (value)
            tpl - dictionary of selection
            callback - function to call when parameter getting changed
        """
        self.name       = name
        self.value      = value
        self.readOnly   = False
        
        if tp==None:
            self.type = type(value)
        else:
            self.type   = tp
        
        self.tuple      = tpl
        self.callback   = callback
        self.fileFilter = ''
    
    def setValue(self, val, dt=None):
        try:
            print self.name, 'set to', self.type, str(val)
            self.value = self.type(val)
        except:
            raise anasigError(self.name + ': ' + tr("Bad data type, should be") + ' ' + tr(str(self.type)))
    
    def __str__(self):
        return str(self.value)
    
    def __repr__(self):
        return self.value
    
    def copy(self):
        new = Parameter(self.name, self.value, self.type, self.tuple, self.callback)
        new.readOnly    = self.readOnly
        new.fileFilter  = self.fileFilter
        return new




class ParameterList:
    """
        anasig list of parameters
        - store for anasigDataTypes
        - has list behaviour
    """
    def __init__(self):
        self._params = [] # list of anasigDataTypes
    
    # list behaviour - setting item
    def __setitem__(self, name, value):
        for v in self._params:
            if v.name==name:
                v.setValue(value) # update if found name
                return
        adt = Parameter(name, value) # create new
        self._params.append(adt)     # append to list
    # list behaviour - getting item
    def __getitem__(self, name):
        if type(name)==IntType: # parameter at Int index requested
            try:
                return self._params[name] # return params at index
            except:
                assert('ParameterList nonexisting index: '+str(name))
        for v in self._params: # got name
            if v.name==name:
                return v
        assert('item '+str(name)+' not found')
        return None # requested index/name not found
    # len() called
    def __len__(self): 
        return len(self._params)
    
    def append(self, asp):
        """append object (Parameter) to end of the list"""
        if not isinstance(asp, Parameter):
            anasigError("not Parameter type")
        self._params.append(asp)
    
    def insert(self, index, asp):
        """insert object before index"""
        if not isinstance(asp, Parameter):
            anasigError("not Parameter type")
        self._params.insert(index, asp)
    
    def remove(self, name):
        """remove first occurrence of value"""
        for v in self._params:
            if v.name==name:
                self._params.remove(v)
                return True
        return False
    
    def index(self, name):
        """integer -- return first index of value"""
        for i,v in enumerate(self._params):
            if v.name==name:
                return i
    
    def __repr__(self):
        return 'Anasig parameter list'






def loadPlugins():
    files = os.listdir(PLUGIN_DIR)
    for f in files:
        if f in ('__init__.py', '..', '.'):
            continue
        
        fname = os.path.splitext(f)
        plugins.append(fname)# = #os.path.join([PLUGIN_DIR, f[0]])




from anasigError import *




###################################################################
## base class for all items (intrumnets, signals, graphs)
class ItemBase:
    """base class for all items"""
    def __init__(self, *args, **kwords):
        self.parameters = ParameterList()
        self.setProperties(kwords)
        self.initialized = False
    
    def setProperties(self, kwords):
        for k,v in kwords.iteritems():
            self.parameters[k] = kwords[k]
    
    def mouseReleaseEvent(self, e):
        self.mnuProperties()
    
    # wrapper - if itemname in parameters is Parameter type, return its value, otherwise 
    # return value itself (not Paramater type)
    def __getitem__(self, itemname):
        i = self.parameters[itemname]
        if i:
            return i.value
        return i
    
    def __delitem__(self, itemname):
        self.parameters.remove(itemname)
    
    def __str__(self):
        return '__str__ : item ' + self.name
    
    def __repr__(self):
        return ObjectType
    
    def __nonzero__(self):
        return True
    
    def __setitem__(self, item, value):
        try:
            self.parameters[item] = value
        except anasigError, e:
            QMessageBox.warning(None, tr("Error"), e.message)
            return
    
    def valuesChanged(self):
        """
        function called after values has been changed - used for signal generating 
        when called especially from properties.py, after new signal values has been set 
        """
        self.initialized = True

    def setName(self, txt):
        """seting the name of instrument - need length check"""
        if txt=='':
            raise anasigError(tr('Expected nonempty string'))
        self.name = txt
    
    def setReadOnly(self, name, ro):
        for i in self.parameters._params:
            if i.name==name:
                i.readOnly = ro
    
    def getParams(self):
        """returns self.parameters._params with REFERENCED anasigDataType objects"""
        return self.parameters._params
    
    def getParamsCopy(self):
        """returns COPY of self.parameters._params"""
        out = []
        for i in self.parameters._params:
            out.append(i.copy())
        return out
    
    def saveToFile(self):
        """save item to file when explicitly SAVE cmd called (saving item only - not global pikling"""
        EXT = '.asg'
        import cPickle
        fn = QFileDialog.getSaveFileName('', # startWith 
            "anasig items (*.asg)", # filter 
            None,   # parent 
            '',     # name
            tr('Save to file'), # caption
            'anasig items (*' + EXT + ')') # transl.tr('txt_Choose a filename to save under'))
        
        fn = str(fn)
        st = os.path.splitext(fn)
        
        if st[-1]!=EXT:
            if st[-1]!='':
                anasigError(tr('Bad file extension'))
            fn = fn + EXT
        
        if fn!='':
            f = open(fn, 'w')
            s = {}
            self.toPickle(s)
            
            cPickle.dump(s, f)
            f.close()
    
    def toPickle(self, s):
        """add properties to saving (pickle) object"""
        s['class']      = self.__class__.__name__
        s['type']       = self._type
        s['subType']    = self._subType
        s['name']       = self.name
        s['parameters'] = self.parameters
    
    def fromPickle(self, s):
        """loads from pickle object"""
        self._type      = s['type']
        self._subType   = s['subType']
        self.name       = s['name']
        self.parameters = s['parameters']
    
    def getMenuItemsList(self):
        """called when menu items requested
            returns dict of menu items 
            example:
            [{'name1':funcToCall},
             {'name2':funcToCall},
             {'submenuname': 
                        [ 
                            {'subname1':funcToCall},
                            {'subname2':funcToCall}
                        ]}
            ]
        """
        return []
    
##    def propertiesShow(self):
##        """show item properties in the Properties Organiser"""
##        getActiveWorkspace().PropestiesWnd.showProperties(self)




def getActiveWorkspace():
    """returns active workspace"""
    return qApp.mainWidget().ws.activeWindow().ws



class Pickleable:
    def __init__(self):
        pass
    def toPickle(self):
        pass
    def fromPickle(self):
        pass


class anasigWindow:
    def __init__(self):
        pass
    
    def getListFromSize(self):
        p = self.parentWidget().geometry()
        s = self.size()
        ll = [p.x(), p.y(), s.width(), s.height()]
        return ll
    
    def setSizeFromList(self, p):
        wnd = self.parentWidget()
        pos = QPoint()
        size = QSize()
        pos.setX(p[0])
        pos.setY(p[1])
        wnd.move(pos)
        size.setWidth(p[2])
        size.setHeight(p[3])
        wnd.resize(size)




def getAllItems(lv, type, subtype):
    """ find out items in organiser by given type and subtype """
    out = []
    iter = QListViewItemIterator(lv)
    while ( iter.current() ):
        exp1 = exp2 = False
        if type != None:
            if iter.current()._object.Type == type:
                exp1 = True
        else: exp1 = True
        
        if subtype != None:
            if iter.current()._object.subType == subtype:
                exp2 = True
        else: exp2 = True
        
        if exp1 and exp2:
            out.append ( iter.current() )
        
        iter += 1
        
    return out



def filloutComboBox(lb, items):
    """ fills out combobox by given items """
    for i in items:
        lb.insertItem(i)



##def saveWindowPosition(wnd):
##    try:
##        pos = wnd.parentWidget().geometry()
##    except:
##        pos = wnd.geometry()
##    
##    size = wnd.size()
##    settings = QSettings()
##    name = wnd.name
##    settings.writeEntry("/anasig/" + name + "/geometry/x", pos.x() )
##    settings.writeEntry("/anasig/" + name + "/geometry/y", pos.y() )
##    settings.writeEntry("/anasig/" + name + "/geometry/width", size.width() )
##    settings.writeEntry("/anasig/" + name + "/geometry/height", size.height() )
##
##
##
##def loadWindowPosition(wnd, pos):
##    settings = QSettings()
##    name = wnd.name
##    pos = QPoint()
##    size = QSize()
##    pos.setX( settings.readNumEntry("/anasig/" + name + "/geometry/x", wnd.x() )[0] )
##    pos.setY( settings.readNumEntry("/anasig/" + name + "/geometry/y", wnd.y() )[0] )
##    wnd.move(pos)
##    size.setWidth( settings.readNumEntry("/anasig/" + name + "/geometry/width", wnd.width() )[0] )
##    size.setHeight( settings.readNumEntry("/anasig/" + name + "/geometry/height", wnd.height() )[0] )
##    wnd.resize(size)



def loadProgramValue(settings, key, default):
        #print "key: " + key + ", val: ", default
        if isinstance(default, float):
            return settings.readDoubleEntry("/anasig/" + key, default )[0]
        elif isinstance(default, int):
            return settings.readNumEntry("/anasig/" + key, default )[0]
##        elif isinstance(default, list):
##            out, res = settings.readListEntry("/anasig/" + key )
##            
##            if res == False: out = default
##            else: 
##                out = [ x.toFloat() for x in out ]
            
            return out



def saveProgramValue(settings, key, val):
    settings.writeEntry("/anasig/" + key, val )
    
import os
import cPickle

def loadProgramVars():
##    settings = QSettings()
##    for key, val in ProgramVars.items():
##        if not isinstance(val, list):
##            loadProgramValue(settings, key, val)
    try:
        f = open('programvars.cfg', 'r')
        lpv = cPickle.load(f)
        f.close()
        ProgramVars.update(lpv) # can not assign directly!
    except :
        pass

def saveProgramVars():
##    settings = QSettings()
##    for key, val in ProgramVars.items():
##        if not isinstance(val, list):
##            saveProgramValue(settings, key, val)
    f = open('programvars.cfg', 'w')
    #cPickle.dump(ProgramVars, f)
    f.close()


class anasigProject:
    def load(self):
        pass
    def save(self):
        pass



# testing
if __name__ == "__main__":
    pass
