#!/usr/bin/env python2

import os
import sys
import py_compile

BASEDIR = '/usr/local/lib/python2.7'

def mk_file(dname, fname, target):
    fpath = os.path.join(dname, fname)
    if fname.endswith('.py'):
        # We compile to save space and time in the parser
        py_compile.compile(fpath, fpath + 'c')
        fpath += 'c'
        fname += 'c'
    else:
        return ''
    contents = ','.join(str(ord(i)) for i in open(fpath, 'rb').read())
    return 'FS.createDataFile("%s", "%s", [%s], true, true);' % (target, fname, contents)

def main(root):
    os.chdir(root)
    # http://bugs.python.org/issue22689
    #commands = ['ENV["PYTHONHOME"] = "%s";' % (BASEDIR,)]
    commands = []
    commands.append('FS.createPath("%s", "%s", true, true);' % ('/', BASEDIR[1:]))
    for (dirpath, dirnames, filenames) in os.walk('.'):
        for dirname in dirnames[:]:
            should_remove = any([
                dirname in ['tests', 'test'], # python 3 tests will error!
                dirname == 'unittest', # gets crippled by the above
                dirname.startswith('plat-') and dirname != 'plat-linux2', # emscripten is ~linux
                dirname == 'lib2to3', # we don't package the necessary grammar files
                dirname in ['idlelib', 'lib-tk'], # Tk doesn't even compile yet
                dirname == 'ctypes', # we obviously can't call C functions
                dirname == 'distutils', # not going to be running pip any time soon
                dirname == 'bsddb', # needs compiling, deprecated anyway
                dirname == 'multiprocessing', # doesn't really make sense in JS
                dirname == 'curses', # we don't have the terminal interface (yet)
                dirname == 'sqlite3', # doesn't get compiled yet
                dirname == 'msilib', # doesn't get compiled and who cares anyway
                dirname == 'hotshot', # doesn't get compiled, unmaintained
                dirname == 'wsgiref', # not going to be building any web servers
            ])
            if should_remove:
                dirnames.remove(dirname)

        target = os.path.abspath(os.path.join(BASEDIR, dirpath))
        for dname in dirnames:
            commands.append('FS.createFolder("%s", "%s", true, true);' % (target, dname))
        for filename in filenames:
            commands.append(mk_file(dirpath, filename, target))

    # _sysconfigdata is created by the build process
    commands.append(mk_file('../build/lib.linux-x86_64-2.7', '_sysconfigdata.py', BASEDIR))

    # Start out in a writeable folder.
    commands.append('FS.createFolder(".", "sandbox", true, true);')
    commands.append('FS.currentPath = "/sandbox";')

    print '\n'.join([c for c in commands if c != ''])

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print 'Usage: %s root' % sys.argv[0]
    else:
        main(sys.argv[1])
