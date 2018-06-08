
package		= astrolib

all:  setup conda-build conda-install

setup:
	python setup.py install --single-version-externally-managed --record=record.txt

conda-build:
	conda-build .

conda-install:
	conda install --use-local astrolib

clean:
	rm -r astrolib.egg-info;
	rm -r build;
	rm record.txt;
