PROJECT=pysisyphus
SRC=$(wildcard *.py) $(wildcard sisyphus/*.py)
PIP=$(PROJECT).tgz

.PHONY: all

all: $(PIP)

$(PIP): $(SRC)
	tar zcvf $(PIP) $^


.PHONY: install uninstall clean

install: $(PIP) uninstall
	pip install $<

uninstall:
	@[ -z "`pip list | grep $(PROJECT)`" ] || pip uninstall -y $(PROJECT)

clean:
	rm -f $(PIP)
	find . -name '*.swp' -delete

