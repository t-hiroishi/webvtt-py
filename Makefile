build:
	rm -rf dist
	mkdir dist
	python setup.py sdist bdist_wheel
	twine check dist/*

release_test: build
	twine upload -r testpypi dist/*

release: build
	twine upload dist/*

.PHONY: build release_test release