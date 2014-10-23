#!/usr/bin/env python2

import os
import sys
import py_compile

BASEDIR = '/usr/local/lib/python2.7'

def main(root):
    os.chdir(root)
    # http://bugs.python.org/issue22689
    #commands = ['ENV["PYTHONHOME"] = "%s";' % (BASEDIR,)]
    commands = []
    commands.append('FS.createPath("%s", "%s", true, true);' % ('/', BASEDIR[1:]))
    for (dirpath, dirnames, filenames) in os.walk('.'):
        if 'tests' in dirnames: dirnames.remove('tests')
        if 'test' in dirnames: dirnames.remove('test')
        jsdir = os.path.abspath(os.path.join(BASEDIR, dirpath))
        for folder in dirnames:
            commands.append('FS.createFolder("%s", "%s", true, true);' % (jsdir, folder))
        for filename in filenames:
            if not filename.endswith('.py'): continue
            full_path = os.path.join(dirpath, filename)
            # We compile to get rid of a strange parser error
            py_compile.compile(full_path, full_path + 'c')
            contents = ','.join(str(ord(i)) for i in open(full_path + 'c', 'rb').read())
            commands.append('FS.createDataFile("%s", "%s", [%s], true, true);' % (jsdir, filename + 'c', contents))

    # _sysconfigdata is created by the build process
    scd_dir = '../build/lib.linux-x86_64-2.7'
    scd_name = '_sysconfigdata.py'
    scd_path = os.path.join(scd_dir, scd_name)
    py_compile.compile(scd_path, scd_path + 'c')
    contents = ','.join(str(ord(i)) for i in open(scd_path + 'c', 'rb').read())
    commands.append('FS.createDataFile("%s", "%s", [%s], true, true);' % (BASEDIR, scd_name + 'c', contents))

    # Start out in a writeable folder.
    commands.append('FS.createFolder(".", "sandbox", true, true);')
    commands.append('FS.currentPath = "/sandbox";')

    print '\n'.join(commands)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print 'Usage: %s root' % sys.argv[0]
    else:
        main(sys.argv[1])
