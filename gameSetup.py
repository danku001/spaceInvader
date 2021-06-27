"""
code is to compile spaceInvadersGame into single
Executable

"""

from distutils.core import setup
import os, sys
import py2exe



#datafile
##first element in the tuple is the name of the file to be copied
##second is the file path
dataFile = [ ]
fileDir = os.path.join( os.path.dirname( os.path.abspath(sys.argv[0]) ), "assets")
#print('fileDir: ', fileDir)
for files in os.listdir(fileDir):
    f1 = os.path.join(fileDir, files)
    #moving the files into the datafile list
    if os.path.isfile(f1):
        #above checks if that is a file
        f2 = 'assets', [f1]
        dataFile.append(f2)

#calling the function
##keep bundle_files:1
setup( windows=['spaceInvGame.py'],
       data_files=dataFile,
       options={
               "py2exe": { "unbuffered": False,
                                  "optimize" : 2,
                                  "excludes": ["email","numpy"],
                                  "includes": ['pygame', 'random','time', 'os'],
                                  "bundle_files": 1,
                                  }
                      }
       )
