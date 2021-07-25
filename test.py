from sys import stdin, stdout

def u24(x):
	return chr(x & 0xff) + chr((x >> 8) & 0xff) + chr((x >> 16) & 0xff)

def u24ToInt(x):
	return ord(x[0]) | (ord(x[1]) << 8) | (ord(x[2]) << 16)

def version():
	stdout.write("\x10\x00\x03")
	v = ord(stdin.read(1))
	if v != 6:
		stdin.read(1)
	return v

def loadlib(name, version, funcs):
	stdout.write("\x10\x01" + name + "\0" * (8 - len(name)) + chr(version) + u24(funcs))
	return u24ToInt(stdin.read(3))

def call(addr, args):
	stdout.write("\x10\x02" + u24(addr) + u24(3 * len(args)))
	for arg in args:
		stdout.write(u24(arg))
	return stdin.read(5)

def write(addr, data):
	stdout.write("\x10\x03" + u24(addr) + u24(len(data)) + data)
	stdin.read(1)

def read(addr, size):
	stdout.write("\x10\x04" + u24(addr) + u24(size))
	return stdin.read(size)

def copy(dest, addr, size):
	stdout.write("\x10\x05" + u24(dest) + u24(addr) + u24(size))
	stdin.read(1)

def set(addr, byte, size):
	stdout.write("\x10\x06" + u24(addr) + chr(byte) + u24(size))
	stdin.read(1)

def malloc(size):
	stdout.write("\x10\x07" + u24(size))
	return u24ToInt(stdin.read(3))

def free(addr):
	stdout.write("\x10\x08" + u24(addr))
	stdin.read(1)
