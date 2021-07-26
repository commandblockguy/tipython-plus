all: site/python.js site/installer.js test.8xv

site/python.js: patches/python.asm patches/fasmg-ez80/ti84pce.inc
	cd patches && fasmg python.asm ../site/python.js

patches/fasmg-ez80/ti84pce.inc:
	cd patches/fasmg-ez80 && ./bin/fetch_ti84pce
	cd patches/fasmg-ez80 && ./ti84pce.sed ti84pce.inc > ti84pceg.inc

site/installer.js: installer/bin/PYINST.bin
	xxd -i installer/bin/PYINST.bin | sed -e 's/.*{/const installer = [/' -e 's/}.*/];/' -e 's/unsigned.*//' > site/installer.js

installer/bin/PYINST.bin: installer/src/*
	$(MAKE) -C ./installer debug

clean:
	rm -f patches/python.js site/installer.js site/python.js test.8xv
	$(MAKE) -C ./installer clean

test.8xv: test.py
	printf "PYCD\x00" > test.bin
	cat test.py >> test.bin
	convbin -i test.bin -j bin -o test.8xv -k 8xv -n TEST
	rm test.bin
