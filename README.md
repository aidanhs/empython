= empython

== Get it

First, clone and initialise submodules:

```
$ git clone git@github.com:aidanhs/empython.git
$ cd empython
$ git submodule update --init
```

== Build it

If you have emscripten 2.0.7 installed (other versions may or may not work):

```
$ cd python
$ make -f ../Makefile prep
$ make -f ../Makefile em
$ cd ..
$ make empython.js
```

If you have docker or podman (below I'll use podman, I think you'll need to add `-u $(id -u):$(id -g)` for Docker):

```
$ podman pull emscripten/emsdk:2.0.7
$ podman run -it --rm -v $(pwd):/src emscripten/emsdk:2.0.7 bash -c "cd python && make -f ../Makefile prep && make -f ../Makefile em && cd .. && make empython.js"
$ ls -l empython.{js,wasm}
.rw-r--r-- 2.9M aidanhs 25 Oct 14:52 empython.js
.rwxr-xr-x 1.9M aidanhs 25 Oct 14:52 empython.wasm
```
