all: patches/python.js installer.js

patches/python.js: patches/python.asm
	cd patches && fasmg python.asm python.js

installer.js: installer/bin/PYINST.bin
	xxd -i installer/bin/PYINST.bin | sed -e 's/.*{/const installer = [/' -e 's/}.*/];/' -e 's/unsigned.*//' > installer.js

installer/bin/PYINST.bin: installer/src/*
	$(MAKE) -C ./installer

clean:
	rm -f patches/python.js installer.js
	$(MAKE) -C ./installer clean
