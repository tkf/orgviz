ENV = env

.PHONY : run requirements env clean-env clean

run: requirements
	$(ENV)/bin/python -m orgviz.web

requirements: env
	# Installing NumPy need to be done before installing matplotlib
	pip install --environment $(ENV) numpy
	pip install --environment $(ENV) --requirement requirements.txt

env: $(ENV)/bin/activate
$(ENV)/bin/activate:
	virtualenv $(ENV)

clean-env:
	rm -rf $(ENV)

clean: clean-env
