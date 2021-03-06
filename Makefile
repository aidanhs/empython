# Enable optimisations by default
EMPYOPT?=1
COPT=$$([ $(EMPYOPT) = 1 ] && echo -Oz || echo "-O0 -g")

EMDEBUG=\
	-O0\
	-g3\
	--js-opts 0\
	--llvm-opts 0\
	--llvm-lto 0\
	-s ASSERTIONS=2\

EMOPT=\
	-O3\
	-g0\
	--js-opts 1\
	--llvm-opts 3\
	--llvm-lto 3\
	-s ASSERTIONS=0\
	#--closure 0

EMFLAGS=\
	--pre-js js/preJs.js --post-js js/postJs.js\
	--memory-init-file 0\
	-s INCLUDE_FULL_LIBRARY=0\
	-s EMULATE_FUNCTION_POINTER_CASTS=1\
	$$([ $(EMPYOPT) = 1 ] && echo $(EMOPT) || echo $(EMDEBUG))

EMEXPORTS=\
	-s EXPORTED_FUNCTIONS="['_Py_Initialize', '_PyRun_SimpleString']" -s "EXTRA_EXPORTED_RUNTIME_METHODS=['cwrap']"

empython.js: python/libpython3.5.a
	./mapfiles.py python/Lib datafilezip > js/postJs.js
	cat js/postJs.js.in >> js/postJs.js
	emcc $(EMFLAGS) $(EMEXPORTS) -o $@ $< python/Modules/zlib/libz.a

CONFFLAGS=OPT="$(COPT)" --without-threads --without-pymalloc --disable-shared --disable-ipv6
prep:
	./configure
	make python
	cp python ../python.native
	make clean
	git clean -f -x -d
em:
	cd Modules/zlib && emconfigure ./configure --static && emmake make libz.a
	(export BASECFLAGS=-m32 LDFLAGS=-m32 && emconfigure ./configure $(CONFFLAGS))
	git apply ../hacks.patch
	emmake make || true # errors on running python
	mv python python.bc # only useful if replacing the emscripten test .bc file
	cp ../python.native python && chmod +x python
	emmake make
