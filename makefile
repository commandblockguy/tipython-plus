all: patches/python.js installer.js test.8xv

patches/python.js: patches/python.asm
	cd patches && fasmg python.asm python.js

installer.js: installer/bin/PYINST.bin
	xxd -i installer/bin/PYINST.bin | sed -e 's/.*{/const installer = [/' -e 's/}.*/];/' -e 's/unsigned.*//' > installer.js

installer/bin/PYINST.bin: installer/src/*
	$(MAKE) -C ./installer debug

clean:
	rm -f patches/python.js installer.js
	$(MAKE) -C ./installer clean

test.8xv: test.py
	printf "PYCD\x00" > test.bin
	cat test.py >> test.bin
	convbin -i test.bin -j bin -o test.8xv -k 8xv -n TEST
	rm test.bin
