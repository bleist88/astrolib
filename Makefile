
package_name	= astrolib

##	============================================================================
##	Installation.

install:  setup conda_install

setup:
	python3 setup.py install --single-version-externally-managed --record=record.txt

conda_install:
	conda build .;
	conda install --use-local astrolib;

##	============================================================================
##	Updating.

update_all:
	update_git;
	update_conda;

update_git:
	git add -A;
	git commit -m "updating";
	git push;

update_conda:
	conda update --use-local ${package_name};

##	============================================================================
##	Housekeeping.

clean:
	rm -r astrolib.egg-info;
	rm -r build;
	rm record.txt;
