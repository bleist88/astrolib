
package		= astrolib

all:	setup build install

setup:
	python setup.py install >> setup.log

build:
	conda-build ${package} >> build.log

install:
	conda install --use-local astrolib
