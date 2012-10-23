ENV = env
ORGVIZ_OPTS =

.PHONY : run requirements env clean-env clean jslib clean-tmp


run: requirements
	$(ENV)/bin/python -m orgviz.web $(ORGVIZ_OPTS)


### Virtual Environment

requirements: env
	# Installing NumPy need to be done before installing matplotlib
	pip install --environment $(ENV) numpy
	pip install --environment $(ENV) --requirement requirements.txt

env: $(ENV)/bin/activate
$(ENV)/bin/activate:
	virtualenv $(ENV)

clean-env:
	rm -rf $(ENV)


### JS libraries

jslib:
	./setup-jslib.sh

clean-tmp:
	rm -rf tmp


### Coffee

coffee:
	coffee -c orgviz/static/


### Clean

clean: clean-env
