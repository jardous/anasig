#!/usr/bin/python
# -*- coding: utf-8 -*-
import cPickle
from qt import QDialog, QFileDialog

def loadItemFromFile(type, ext='asg'):
    dlg = QFileDialog('', 'anasig items (*.' + ext + ')')
    if dlg.exec_loop()==QDialog.Accepted:
        fn = dlg.selectedFile()
        fn = str(fn)
        f = open(fn, 'r')
        
        try:
            s = cPickle.load(f)
        except:
            anasigError(tr('Can not load item from file'))
            return None
        
        if s['type'] != type:
            return None # bad type - requested different
        if s['type']=='signal':
            from signals import *
            item = eval('%s()' % s['class'])
            item.parameters = s['parameters']
        # let item to update itself
        item.fromPickle(s)
        
        return item
