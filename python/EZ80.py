from sys import stdin, stdout

RETURN_NOBLOCK = const(0)
RETURN_NONE = const(1)
RETURN_8 = const(2)
RETURN_24 = const(3)

def csi(c, args):
  return "\x1B[" + ';'.join(str(x) for x in args) + c

def command(id, args):
  stdout.write(csi('p', [id] + args))

def bytesToInt(s):
  return ord(s[0]) | (ord(s[1]) << 8) | (ord(s[2]) << 16)

def b64Read(size):
  num_chunks = (size + 2) // 3
  r = b''
  for _ in range(num_chunks):
    n = b64ToInt(stdin.read(4))
    r += bytes((n >> (8*i)) & 0xff for i in range(3))
  return r[:size]

def b64WriteInt(n):
  b = (n & 0x3f) + ((n << 2) & 0x3f00) + ((n << 4) & 0x3f0000) + ((n << 6) & 0x3f000000) + 0x20202020
  stdout.write(b.to_bytes(4, 'little'))

def b64Write(s):
  v = memoryview(s)
  num_chunks = (len(v) + 2) // 3
  for x in range(num_chunks):
    c = v[3*x:3*x+3]
    n = int.from_bytes(c, 'little')
    b64WriteInt(n)
    

def b64ToInt(s):
  return sum((ord(s[i]) - 32) << (6*i) for i in range(4))

def version():
  command(0, [])
  stdout.write("\x03")
  s = stdin.read(1)
  if s == '\x06':
    return None
  else:
    s += stdin.read(3)
    return b64ToInt(s)


class Library:
  def __init__(self, name, version, numFuncs):
    data = name + '\0' * (8 - len(name)) + chr(version)
    args = [data[x*3:x*3+3] for x in range(3)]
    args = [bytesToInt(args[x]) for x in range(3)] + [numFuncs]
    command(1, args)
    self.addr = b64ToInt(stdin.read(4))
    if self.addr == 0:
      raise OSError("Library appvar " + name + " not found")
    self.numFuncs = numFuncs
    self.funcs = self.addr + len(name) + 3

  # todo: fix this not actually getting called
  def __del__(self):
    free(self.addr)

  def call(self, f, retType, *args):
    call(self.funcs + f * 4, retType, args)

def call(addr, retType, args):
  command(2, [addr, retType, 3 * len(args)])
  for x in args:
    b64WriteInt(x)
  if retType == RETURN_NONE:
    stdin.read(1)
  elif retType == RETURN_8:
    return b64ToInt(stdin.read(4)) & 0xff
  elif retType == RETURN_24:
    return b64ToInt(stdin.read(4))

def write(addr, data):
  command(3, [addr, len(data)])
  b64Write(data)
  stdin.read(1)

def read(addr, size):
  command(4, [addr, size])
  return b64Read(size)

def copy(dest, addr, size):
  command(5, [dest, addr, size])
  stdin.read(1)

def set(addr, byte, size):
  command(6, [addr, byte, size])
  stdin.read(1)

def malloc(size):
  command(7, [size])
  result = b64ToInt(stdin.read(4))
  if result == 0:
    raise MemoryError('ez80 heap full')
  return result

def free(addr):
  command(8, [addr])
  stdin.read(1)

def free_all():
  command(9, [])
  stdin.read(1)

def run_indic(enabled):
  command(10, [enabled])
  stdin.read(1)

free_all()
