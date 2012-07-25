#!/usr/bin/env python
# -*- coding: utf-8 -*-

from globals import *

from sys import exit, argv
from qt import *

from dmain import anasigMainWindow



###################################################################
## main application class
class anasigApp(QApplication):
    """main application class"""
##    def __init__(self, argv):
##        QApplication.__init__(self, argv)
##    
    def start(self):
        #loadProgramVars()
        #loadPlugins()
        
##        # set language
##        lang = QTextCodec.locale()[:2]
##        language =  "anasig_" + lang + ".qm"
##        
##        translator = QTranslator()
##        translator.load(language, ".")
##        qApp.installTranslator(translator)
        
        self.main = anasigMainWindow()
        self.setMainWidget(self.main)
        
        self.main.show()
        ret = self.exec_loop()
        
        #saveProgramVars()
        
        return ret




if __name__ == "__main__":
    """main function - here everything begins (and ends...)"""
    
    a = anasigApp(argv)
    ret = a.start()
    exit(ret)
