#!/usr/bin/env python2

import os
import sys

BASEDIR = '/usr/local/lib/python2.7'

def main(root):
    os.chdir(root)
    # http://bugs.python.org/issue22689
    #commands = ['ENV["PYTHONHOME"] = "%s";' % (BASEDIR,)]
    commands = []
    commands.append('FS.createPath("%s", "%s", true, true);' % ('/', BASEDIR[1:]))
    for (dirpath, dirnames, filenames) in os.walk('.'):
        jsdir = os.path.abspath(os.path.join(BASEDIR, dirpath))
        for folder in dirnames:
            commands.append('FS.createFolder("%s", "%s", true, true);' % (jsdir, folder))
        for filename in filenames:
            if not filename.endswith('.py'): continue
            full_path = os.path.join(dirpath, filename)
            contents = ','.join(str(ord(i)) for i in open(full_path, 'rb').read())
            commands.append('FS.createDataFile("%s", "%s", [%s], true, true);' % (jsdir, filename, contents))

    # Start out in a writeable folder.
    commands.append('FS.createFolder(".", "sandbox", true, true);')
    commands.append('FS.currentPath = "/sandbox";')

    print '\n'.join(commands)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print 'Usage: %s root' % sys.argv[0]
    else:
        main('.')
