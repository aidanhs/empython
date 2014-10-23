EMFLAGS=\
	--pre-js js/preJs.js --post-js js/postJs.js\
	-O2\
	--memory-init-file 0\
	-s ASM_JS=0\
	-s ASSERTIONS=2\
	-s INCLUDE_FULL_LIBRARY=1\
	-s EMULATE_FUNCTION_POINTER_CASTS=1\
	#--llvm-lto 1\
	#--closure 0

EMEXPORTS=\
	-s EXPORTED_FUNCTIONS="['_Py_Initialize', '_PyRun_SimpleString']"

lp.js: libpython.a
	python mapfiles.py python/Lib > js/postJs.js
	cat js/postJs.js.in >> js/postJs.js
	emcc $(EMFLAGS) $(EMEXPORTS) -o $@ $<

CONFFLAGS="OPT=-O2 --without-threads --without-pymalloc --disable-shared --without-signal-module --disable-ipv6"
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
	(export BASECFLAGS=-m32 LDFLAGS=-m32 && emconfigure ./configure $(CONFFLAGS))
	git apply ../hacks.patch
	emmake make
	cp ../python.native python && chmod +x python
	#cp ../pgen.native Parser/pgen && chmod +x Parser/pgen
	emmake make
