EMFLAGS=\
	--pre-js js/preJs.js --post-js js/postJs.js

EMEXPORTS=\
	-s EXPORTED_FUNCTIONS="['_Py_Initialize', '_PyRun_SimpleString']"

lp.js: lp.bc
	(cd Python-2.7.8/Lib/ && python ../../mapfiles.py .) > js/postJs.js
	cat js/postJs.js.in >> js/postJs.js
	emcc $(EMFLAGS) $(EMEXPORTS) $< -o $@

#lp.bc:
#	TODO

prep:
	cd tcl && git apply ../hacks.patch
	#TODO
	#cd tcl/unix && emconfigure ./configure --disable-threads --disable-load --disable-shared

#===================
#
#/usr/include/x86_64-linux-gnu
#============

#sudo apt-get install gcc-multilib
#
#CONFFLAGS=""
#CONFFLAGS="$CONFFLAGS --without-threads --disable-shared --without-signal-module --disable-ipv6"
#
#./configure
#make Parser/pgen python
#cp Makefile ../Makefile.native
##cp Parser/pgen ../pgen.native
#cp python ../python.native
#make clean
#git clean -f -x -d
#
#(export CFLAGS=-m32 && export LDFLAGS=-m32 && emconfigure ./configure $CONFFLAGS)
#git apply ../hacks.patch
#emmake make
##cp ../pgen.native Parser/pgen
#cp ../python.native python
##chmod +x Parser/pgen
#chmod +x python
#emmake make
#
