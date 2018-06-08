
package		= astrolib

all:	setup conda-build conda-install

setup:
	python setup.py install --single-version-externally-managed --record=record.txt

conda-build:
	conda-build ${package} >> build.log

conda-install:
	conda install --use-local astrolib

fix:
	mkdir /anaconda3/conda-bld/noarch/;
	echo '{}' > /anaconda3/conda-bld/noarch/repodata.json;
	bzip2 -k /anaconda3/conda-bld/noarch/repodata.json;
