all: 
	help2man -N --no-discard-stderr ./gencfs.py -o gencfs.1
	python setup.py sdist
