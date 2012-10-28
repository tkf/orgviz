.PHONY : test clean-tox clean jslib update-jslib clean-jslib clean-tmp


## Test
test: jslib coffee
	tox

clean-tox:
	rm -rf .tox


### JS libraries

jslib:
	tools/setup-jslib.sh

update-jslib: clean-jslib clean-tmp jslib

clean-jslib:
	rm -rf orgviz/static/lib

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
