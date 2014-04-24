.PHONY: build
build :
	python setup.py build

.PHONY: install
install :
	python setup.py install

# Install editor tooling.
.PHONY: tooling
tooling :
	pip install epc
	pip install pylint
	pip install rope_py3k
	pip install ropemode
	pip install ropemacs
