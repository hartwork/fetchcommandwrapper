dist:
	rm -f MANIFEST
	python3 setup.py sdist

clean:
	find -type f -name '*.pyc' -delete

.PHONY: clean dist
