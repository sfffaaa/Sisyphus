PROJECT=pysisyphus
SRC=$(wildcard *.py) $(wildcard sisyphus/*.py)
PIP=$(PROJECT).tgz
PEP8_HOOK=.git/hooks/pre-commit

.PHONY: all $(PEP8_HOOK)

all: $(PIP) $(PEP8_HOOK)

$(PIP): $(SRC)
	tar zcvf $(PIP) $^

$(PEP8_HOOK):
	@[ -f .git/hooks/pre-commit ] || echo "git-pylint-commit-hook" >> .git/hooks/pre-commit
	@chmod +x .git/hooks/pre-commit

.PHONY: install uninstall clean

install: $(PIP) uninstall
	pip install $<

uninstall:
	@[ -z "`pip list | grep $(PROJECT)`" ] || pip uninstall -y $(PROJECT)

clean:
	rm -f $(PIP)
	find . -name '*.swp' -delete

.PHONY: test

test:
	[ "${PIPENV_ACTIVE}" != "1" ] || pytest tests
