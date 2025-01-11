install:
		pip3 install -e .[dev]

lint:
		flake8 getoutline_cli

build:
		python setup.py sdist bdist_wheel

publish:
		twine upload dist/*

clean:
		rm -rf build dist *.egg-info getoutline_cli/__pycache__
