include 'apppatch.inc'
include 'ez80.inc'

patch test

replacement 0, 0, "Test replacement - insert 32 bytes of NOP to the beginning of the main section"

repeat 32
	nop
end repeat

end replacement

end patch
