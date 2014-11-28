#!/usr/bin/env python2

import os
import sys
import py_compile

BASEDIR = '/usr/local/lib/python2.7'

def files_to_datafilecalls(fpaths):
    commands = []
    dpaths = set([BASEDIR])
    for fpath, targetdir in fpaths:

        assert targetdir[0] == '.'
        if not fpath.endswith('.py'):
            continue
        dpath = os.path.abspath(os.path.join(BASEDIR, targetdir))

        # We compile to save space and time in the parser
        py_compile.compile(fpath, fpath + 'c')
        fpath += 'c'
        contents = ','.join(str(ord(i)) for i in open(fpath, 'rb').read())
        commands.append('FS.createDataFile("%s", "%s", [%s], true, true);' % (
            dpath, os.path.basename(fpath), contents
        ))

        # Make sure we're adding all required directories
        while dpath not in dpaths:
            dpaths.add(dpath)
            dpath = os.path.dirname(dpath)

    dpaths.remove(BASEDIR)
    for dpath in sorted(dpaths, key=len, reverse=True):
        commands.insert(0, 'FS.createFolder("%s", "%s", true, true);' % (
            os.path.dirname(dpath), os.path.basename(dpath)
        ))
    commands.insert(0, 'FS.createPath("/", "' + BASEDIR[1:] + '", true, true);')

    return commands

def main(root):
    os.chdir(root)
    # http://bugs.python.org/issue22689
    #commands = ['ENV["PYTHONHOME"] = "%s";' % (BASEDIR,)]
    fpaths = []
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

        for filename in filenames:
            fpaths.append((os.path.join(dirpath, filename), dirpath))

    # _sysconfigdata is created by the build process
    fpaths.append(('../build/lib.linux-x86_64-2.7/_sysconfigdata.py', '.'))

    commands = files_to_datafilecalls(fpaths)

    # Start out in a writeable folder.
    commands.append('FS.createFolder(".", "sandbox", true, true);')
    commands.append('FS.currentPath = "/sandbox";')

    print '\n'.join([c for c in commands if c != ''])

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print 'Usage: %s root' % sys.argv[0]
    else:
        main(sys.argv[1])
