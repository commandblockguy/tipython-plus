from sys import stdin, stdout

def csi(c, args):
  return "\x1B[" + ';'.join([str(x) for x in args]) + c

def command(id, args):
  stdout.write(csi('p', [id] + args))

def bytesToInt(s):
  return ord(s[0]) | (ord(s[1]) << 8) | (ord(s[2]) << 16)

def intToBytes(i):
  return chr(i & 0xff) + chr((i >> 8) & 0xff) + chr((i >> 16) & 0xff)

def b64Read(size):
  num_chunks = (size + 2) // 3
  r = ''
  for _ in range(num_chunks):
    n = b64ToInt(stdin.read(4))
    r += ''.join([chr((n >> (8*i)) & 0xff) for i in range(3)])
  return r[:size]

def b64Write(s):
  num_chunks = (len(s) + 2) // 3
  for x in range(num_chunks):
    c = s[3*x:3*x+3]
    n = bytesToInt(c + '\0' * (3 - len(c)))
    r = ''.join([chr(((n >> (6*i)) & 0x3f) + 32) for i in range(4)])
    stdout.write(r)

def b64ToInt(s):
  return sum([(ord(s[i]) - 32) << (6*i) for i in range(4)])

def version():
  command(0, [])
  stdout.write("\x03")
  s = stdin.read(1)
  if s == '\x06':
    return None
  else:
    s += stdin.read(3)
    return b64ToInt(s)

def loadlib(name, version, funcs):
  data = name + '\0' * (8 - len(name)) + chr(version)
  args = [data[x*3:x*3+3] for x in range(3)]
  args = [bytesToInt(args[x]) for x in range(3)] + [funcs]
  command(1, args)
  return b64ToInt(stdin.read(4))

def call(addr, args):
  command(2, [addr, 3 * len(args)])
  b64Write(''.join([intToBytes(x) for x in args]))
  return [b64ToInt(stdin.read(4)), b64ToInt(stdin.read(4))]

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
  return b64ToInt(stdin.read(4))

def free(addr):
  command(8, [addr])
  stdin.read(1)

def free_all():
  command(9, [])
  stdin.read(1)

free_all()