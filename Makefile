.PHONY : test build clean-tox clean cog jslib update-jslib clean-tmp


## Test
test: build
	tox

clean-tox:
	rm -rf .tox


## Bulid
build: jslib coffee favicons


### cog
cog: orgviz/__init__.py
orgviz/__init__.py: README.rst
	cd orgviz && cog.py -r __init__.py


### JS libraries
jslib:
	tools/setup-jslib.sh

update-jslib: clean-tmp jslib

clean-tmp:
	rm -rf tmp


### Coffee
coffee:
	coffee -c orgviz/static/


## Favicons
NUVOLA_DIR = orgviz/static/favicons/nuvola

favicons: \
	$(NUVOLA_DIR)/date.ico \
	$(NUVOLA_DIR)/kmplot.ico \
	$(NUVOLA_DIR)/korganizer.ico

$(NUVOLA_DIR)/%.ico: $(NUVOLA_DIR)/%.png
	convert $< $@

clean-favicons:
	rm $(NUVOLA_DIR)/*.ico


### Clean
clean: clean-tox
