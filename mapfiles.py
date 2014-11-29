#!/usr/bin/env python2

import os
import sys
import py_compile
from zipfile import ZipFile, ZIP_DEFLATED
from StringIO import StringIO
from subprocess import check_call

def mk_contents(data):
    return '[' + ','.join(str(ord(i)) for i in data) + ']'

def files_to_datafilecalls(fpaths):
    basedir = '/usr/local/lib/python2.7'
    commands = []
    dpaths = set([basedir])
    for fpath, targetdir in fpaths:

        dpath = os.path.abspath(os.path.join(basedir, targetdir))

        commands.append('FS.createDataFile("%s", "%s", %s, true, true);' % (
            dpath, os.path.basename(fpath), mk_contents(open(fpath, 'rb').read())
        ))

        # Make sure we're adding all required directories
        while dpath not in dpaths:
            dpaths.add(dpath)
            dpath = os.path.dirname(dpath)

    dpaths.remove(basedir)
    for dpath in sorted(dpaths, key=len, reverse=True):
        commands.insert(0, 'FS.createFolder("%s", "%s", true, true);' % (
            os.path.dirname(dpath), os.path.basename(dpath)
        ))
    commands.insert(0, 'FS.createPath("/", "' + basedir[1:] + '", true, true);')

    return commands

def files_to_datafilezipcall(fpaths):
    zf = StringIO()
    zipfile = ZipFile(zf, 'w', ZIP_DEFLATED)
    for fpath, targetdir in fpaths:
        zipfile.write(fpath, os.path.join(targetdir, os.path.basename(fpath)))
    zipfile.close()

    target = '/usr/local/lib/python27.zip'
    commands = []
    commands.insert(0, 'FS.createPath("/", "' + os.path.dirname(target)[1:] + '", true, true);')
    commands.append('FS.createDataFile("%s", "%s", %s, true, true);' % (
        os.path.dirname(target), os.path.basename(target), mk_contents(zf.getvalue())
    ))
    return commands

def main(root):
    os.chdir(root)
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
                dirname == 'pydoc_data', # don't bundle documentation
            ])
            if should_remove:
                dirnames.remove(dirname)

        for filename in filenames:
            fpaths.append((os.path.join(dirpath, filename), dirpath))

    # _sysconfigdata is created by the build process
    fpaths.append(('../build/lib.linux-x86_64-2.7/_sysconfigdata.py', '.'))

    # Some checks and assertions
    assert all([targetdir[0] == '.' for fpath, targetdir in fpaths])
    fpaths = [
        (fpath, targetdir) for fpath, targetdir in fpaths
        if os.path.splitext(fpath)[1] == '.py'
    ]
    # Compile to save space and time in the parser
    check_call(['python', '-OO', '-m', 'py_compile'] + [fpath for fpath, _ in fpaths])
    fpaths = [(fpath + 'o', targetdir) for fpath, targetdir in fpaths]

    if sys.argv[2] == 'datafiles':
        commands = files_to_datafilecalls(fpaths)
    elif sys.argv[2] == 'datafilezip':
        commands = files_to_datafilezipcall(fpaths)
    else:
        assert False

    # Start out in a writeable folder.
    commands.append('FS.createFolder(".", "sandbox", true, true);')
    commands.append('FS.currentPath = "/sandbox";')

    # http://bugs.python.org/issue22689
    #commands = ['ENV["PYTHONHOME"] = "%s";' % (pyhomedir,)]

    print '\n'.join([c for c in commands if c != ''])

if __name__ == '__main__':
    if len(sys.argv) != 3 or sys.argv[2] not in ['datafiles', 'datafilezip']:
        print 'Usage: %s root datafiles|datafilezip' % sys.argv[0]
        sys.exit(1)
    else:
        main(sys.argv[1])
