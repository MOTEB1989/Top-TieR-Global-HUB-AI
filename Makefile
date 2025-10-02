.PHONY: routes tunnel all
routes:
	python3 scripts/lexcode.py routes

tunnel:
	python3 scripts/lexcode.py tunnel 3000

all:
	python3 scripts/lexcode.py all
