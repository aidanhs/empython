EMFLAGS=\
	--pre-js js/preJs.js --post-js js/postJs.js\
	-s ASSERTIONS=1 -s INCLUDE_FULL_LIBRARY=1\
	-O0 -s ASM_JS=0 -s NAMED_GLOBALS=1 \
	#--llvm-lto 1 #--minify 0 #-g --closure 0 --llvm-lto 0

EMEXPORTS=\
	-s EXPORTED_FUNCTIONS="['_Py_Initialize', '_PyRun_SimpleString']"

lp.js: lp.bc
	(cd python/Lib/ && python ../../mapfiles.py .) > js/postJs.js
	cat js/postJs.js.in >> js/postJs.js
	EMCC_FAST_COMPILER=0 emcc $(EMFLAGS) $(EMEXPORTS) -o $@ $< \
		python/Modules/_weakref.o

#lp.bc:
#	TODO

CONFFLAGS="OPT=-O0 --without-threads --without-pymalloc --disable-shared --without-signal-module --disable-ipv6"
prep:
	#sudo apt-get install gcc-multilib
	./configure
	make Parser/pgen python
	#cp Makefile ../Makefile.native
	#cp Parser/pgen ../pgen.native
	cp python ../python.native
	make clean
	git clean -f -x -d
	#
	(export BASECFLAGS=-m32 && export LDFLAGS=-m32 && emconfigure ./configure $(CONFFLAGS))
	git apply ../hacks.patch
	(export EMCC_FAST_COMPILER=0 && emmake make)
	cp ../python.native python && chmod +x python
	#cp ../pgen.native Parser/pgen && chmod +x Parser/pgen
	(export EMCC_FAST_COMPILER=0 && emmake make)
