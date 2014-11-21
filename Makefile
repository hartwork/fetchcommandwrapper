dist:
	rm -f MANIFEST
	python setup.py sdist

clean:
	find -type f -name '*.pyc' -delete

.PHONY: clean dist
