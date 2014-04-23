PYTHON_BIN = /usr/local/bin/python3.3
PIP        = ./env/bin/pip

all : env build

# Configure virtualenv for this project.
env :
	virtualenv -p $(PYTHON_BIN) env

# Install editor tooling.
.PHONY: tooling
tooling : env
	$(PIP) install epc
	$(PIP) install pylint
	$(PIP) install rope_py3k
	$(PIP) install ropemode
	$(PIP) install ropemacs

.PHONY: build
build :
	python setup.py build

.PHONY: install
install :
	python setup.py install
