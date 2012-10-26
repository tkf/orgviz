.PHONY : test clean-tox clean jslib clean-tmp


## Test
test: jslib coffee
	tox

clean-tox:
	rm -rf .tox


### JS libraries

jslib:
	./setup-jslib.sh

clean-tmp:
	rm -rf tmp


### Coffee

coffee:
	coffee -c orgviz/static/


### Clean

clean: clean-tox
