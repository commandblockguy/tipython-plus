all: site/python.js site/installer.js python/EZ80.8xv python/GRAPHXPY.8xv python/KEYPADPY.8xv python/test.8xv

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
	rm -f patches/python.js site/installer.js site/python.js python/*.8xv
	$(MAKE) -C ./installer clean

python/%.8xv: python/%.py python/%.txt
	tipycomp.py python/$*.py python/$*.txt python/$*.8xv $*

python/%.8xv: python/%.py
	printf "PYCD\x00" > /tmp/py.bin
	cat $< >> /tmp/py.bin
	convbin -i /tmp/py.bin -j bin -o $@ -k 8xv -n $*
	rm /tmp/py.bin
