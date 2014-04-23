PYTHON_BIN = /usr/local/bin/python3.3
PIP        = ./env/bin/pip

all : env

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
