import ez80

KEY_GRAPH = const(0)
KEY_TRACE = const(1)
KEY_ZOOM = const(2)
KEY_WINDOW = const(3)
KEY_YEQU = const(4)
KEY_2ND = const(5)
KEY_MODE = const(6)
KEY_DEL = const(7)
KEY_STO = const(9)
KEY_LN = const(10)
KEY_LOG = const(11)
KEY_SQUARE = const(12)
KEY_RECIP = const(13)
KEY_MATH = const(14)
KEY_ALPHA = const(15)
KEY_0 = const(16)
KEY_1 = const(17)
KEY_4 = const(18)
KEY_7 = const(19)
KEY_COMMA = const(20)
KEY_SIN = const(21)
KEY_APPS = const(22)
KEY_GRAPH_VAR = const(23)
KEY_DEC_PNT = const(24)
KEY_2 = const(25)
KEY_5 = const(26)
KEY_8 = const(27)
KEY_L_PAREN = const(28)
KEY_COS = const(29)
KEY_PRGM = const(30)
KEY_STAT = const(31)
KEY_CHS = const(32)
KEY_3 = const(33)
KEY_6 = const(34)
KEY_9 = const(35)
KEY_R_PAREN = const(36)
KEY_TAN = const(37)
KEY_VARS = const(38)
KEY_ENTER = const(40)
KEY_ADD = const(41)
KEY_SUB = const(42)
KEY_MUL = const(43)
KEY_DIV = const(44)
KEY_POWER = const(45)
KEY_CLEAR = const(46)
KEY_DOWN = const(48)
KEY_LEFT = const(49)
KEY_RIGHT = const(50)
KEY_UP = const(51)

class KeySet:
  def __init__(self, data):
    self.data = int.from_bytes(data, 'little') & 0b00001111011111110111111111111111111111111111111011111111

  def __int__(self):
    return self.data

  def any(self):
    return self.data != 0

  def is_down(self, key):
    return ((self.data >> key) & 1) == 1

def get_keys():
  ez80.command(11, [])
  return KeySet(ez80.b64Read(7))
