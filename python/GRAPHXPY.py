from ez80 import *
from ti_system import disp_cursor

SCREEN = 0
BUFFER = 1

class GfxContext:
  def __init__(self):
    self.lib = Library("GRAPHX",11,100)
  
  def __enter__(self):
    disp_cursor(0)
    run_indic(0)
    self.lib.call(0,RETURN_NONE) # gfx_begin
    return self
    
  def __exit__(self,t,v,tb):
    self.lib.call(1,RETURN_NONE) #gfx_end
    run_indic(1)
    print(t,v,tb)

  def set_color(self,color):
    self.lib.call(2,RETURN_NOBLOCK,color)
  def set_default_palette(self):
    self.lib.call(3,RETURN_NOBLOCK,27)
  def set_palette(self,buf,offset):
    self.lib.call(4,RETURN_NOBLOCK,buf,len(buf),offset)
  def fill_screen(self,color):
    self.lib.call(5,RETURN_NONE,color)
  def set_pixel(self,x,y):
    self.lib.call(6,RETURN_NOBLOCK,x,y)
  def get_pixel(self,x,y):
    return self.lib.call(7,RETURN_8,x,y)
  def get_draw(self):
    return self.lib.call(8,RETURN_8)
  def set_draw(self,loc):
    self.lib.call(9,RETURN_NOBLOCK,loc)
  def swap_draw(self):
    self.lib.call(10,RETURN_NOBLOCK)
  def blit(self,loc):
    self.lib.call(11,RETURN_NONE,loc)
  def blit_lines(self,src,y_loc,num_lines):
    self.lib.call(12,RETURN_NONE,src,y_loc,num_lines)
  def blit_rectangle(self,src,x,y,width,height):
    self.lib.call(13,RETURN_NONE,src,x,y,width,height)
  def print_char(self,char):
    self.lib.call(14,RETURN_NOBLOCK,char)
  def print_int(self,n,digits):
    if n < 0:
      self.lib.call(15,RETURN_NOBLOCK,n,digits)
    else:
      self.lib.call(16,RETURN_NOBLOCK,n,digits)
  def print_string(self,string):
    with DynBuf(string) as buf:
      self.lib.call(17,RETURN_NOBLOCK,buf)
  def print_string_xy(self,string,x,y):
    with DynBuf(string) as buf:
      self.lib.call(18,RETURN_NOBLOCK,buf)
  def set_text_xy(self,x,y):
    self.lib.call(19,RETURN_NOBLOCK,x,y)
  def set_text_bg_color(self,color):
    self.lib.call(20,RETURN_NOBLOCK,color)
  def set_text_fg_color(self,color):
    self.lib.call(21,RETURN_NOBLOCK,color)
  def set_text_transparent_color(self,color):
    self.lib.call(22,RETURN_NOBLOCK,color)
  def set_font_data(self,buf):
    self.lib.call(23,RETURN_NOBLOCK,buf)
  def set_font_spacing(self,buf):
    self.lib.call(24,RETURN_NOBLOCK,buf)
  def set_monospace_font(self,spacing):
    self.lib.call(25,RETURN_NOBLOCK,spacing)
  def get_string_width(self,string):
    with DynBuf(string) as buf:
      return self.lib.call(26,RETURN_24,buf)
  def get_char_width(self,char):
    self.lib.call(27,RETURN_24,ord(char))
  def get_text_x(self):
    return self.lib.call(28,RETURN_24)
  def get_text_y(self):
    return self.lib.call(29,RETURN_8)
  def line(self,x0,y0,x1,y1):
    self.lib.call(30,RETURN_NOBLOCK,x0,y0,x1,y1)
  def horiz_line(self,x,y,length):
    self.lib.call(31,RETURN_NOBLOCK,x,y,length)
  def vert_line(self,x,y,height):
    self.lib.call(32,RETURN_NOBLOCK,x,y,height)
  def circle(self,x,y,radius):
    self.lib.call(33,RETURN_NOBLOCK,x,y,radius)
  def fill_circle(self,x,y,radius):
    self.lib.call(34,RETURN_NOBLOCK,x,y,radius)
  def rectangle(self,x,y,width,height):
    self.lib.call(35,RETURN_NOBLOCK,x,y,width,height)
  def fill_rectangle(self,x,y,width,height):
    self.lib.call(36,RETURN_NOBLOCK,x,y,width,height)
# not including these for the moment since clipping is probably negligible compared to the amount of time it takes to send a command
#  def line_no_clip(self):
#    self.lib.call(37,RETURN_)
#  def horiz_line_no_clip(self):
#    self.lib.call(38,RETURN_)
#  def vert_line_no_clip(self):
#    self.lib.call(39,RETURN_)
#  def fill_circle_no_clip(self):
#    self.lib.call(40,RETURN_)
#  def rectangle_no_clip(self):
#    self.lib.call(41,RETURN_)
#  def fill_rectangle_no_clip(self):
#    self.lib.call(42,RETURN_)
  def set_clip_region(self,xmin,ymin,xmax,ymax):
    self.lib.call(43,RETURN_NOBLOCK,xmin,ymin,xmax,ymax)
#  def get_clip_region(self):
#    self.lib.call(44,RETURN_)
  def shift_down(self,pixels):
    self.lib.call(45,RETURN_NOBLOCK,pixels)
  def shift_up(self,pixels):
    self.lib.call(46,RETURN_NOBLOCK,pixels)
  def shift_left(self,pixels):
    self.lib.call(47,RETURN_NOBLOCK,pixels)
  def shift_right(self,pixels):
    self.lib.call(48,RETURN_NOBLOCK,pixels)
# sprite stuff will use classes
#  def tilemap(self):
#    self.lib.call(49,RETURN_)
#  def tilemap_no_clip(self):
#    self.lib.call(50,RETURN_)
#  def transparent_tilemap(self):
#    self.lib.call(51,RETURN_)
#  def transparent_tilemap_no_clip(self):
#    self.lib.call(52,RETURN_)
#  def tile_ptr(self):
#    self.lib.call(53,RETURN_)
#  def tile_ptr_mapped(self):
#    self.lib.call(54,RETURN_)
#  def sprite(self):
#    self.lib.call(57,RETURN_)
#  def transparent_sprite(self):
#    self.lib.call(58,RETURN_)
#  def sprite_no_clip(self):
#    self.lib.call(59,RETURN_)
#  def transparent_sprite_no_clip(self):
#    self.lib.call(60,RETURN_)
#  def get_sprite(self):
#    self.lib.call(61,RETURN_)
#  def scaled_sprite_no_clip(self):
#    self.lib.call(62,RETURN_)
#  def scaled_transparent_sprite_no_clip(self):
#    self.lib.call(63,RETURN_)
#  def flip_sprite_y(self):
#    self.lib.call(64,RETURN_)
#  def flip_sprite_x(self):
#    self.lib.call(65,RETURN_)
#  def rotate_sprite_c(self):
#    self.lib.call(66,RETURN_)
#  def rotate_sprite_c_c(self):
#    self.lib.call(67,RETURN_)
#  def rotate_sprite_half(self):
#    self.lib.call(68,RETURN_)
  def polygon(self,points):
    self.lib.call(69,RETURN_NOBLOCK,points,len(points)/6)
#  def polygon_no_clip(self):
#    self.lib.call(70,RETURN_)
  def fill_triangle(self,x0,y0,x1,y1,x2,y2):
    self.lib.call(71,RETURN_NOBLOCK,x0,y0,x1,y1,x2,y2)
#  def fill_triangle_no_clip(self):
#    self.lib.call(72,RETURN_)
  def set_text_scale(self,xscale,yscale):
    self.lib.call(74,RETURN_NOBLOCK,xscale,yscale)
  def set_transparent_color(self,color):
    self.lib.call(75,RETURN_NOBLOCK,color)
  def zero_screen(self):
    self.lib.call(76,RETURN_NOBLOCK)
#  def set_text_config(self):
#    self.lib.call(77,RETURN_)
#  def get_sprite_char(self):
#    self.lib.call(78,RETURN_)
# kinda useless to ask the main processor to do basic math
#  def lighten(self):
#    self.lib.call(79,RETURN_)
#  def darken(self):
#    self.lib.call(80,RETURN_)
  def set_font_height(self,height):
    self.lib.call(81,RETURN_NOBLOCK,height)
#  def scale_sprite(self):
#    self.lib.call(82,RETURN_)
  def flood_fill(self,x,y,color):
    self.lib.call(83,RETURN_NOBLOCK,x,y,color)
#  def rlet_sprite(self):
#    self.lib.call(84,RETURN_)
#  def rlet_sprite_no_clip(self):
#    self.lib.call(85,RETURN_)
#  def convert_from_rlet_sprite(self):
#    self.lib.call(86,RETURN_)
#  def convert_to_rlet_sprite(self):
#    self.lib.call(87,RETURN_)
#  def convert_to_new_rlet_sprite(self):
#    self.lib.call(88,RETURN_)
#  def rotate_scale_sprite(self):
#    self.lib.call(89,RETURN_)
#  def rotated_scaled_transparent_sprite_no_clip(self):
#    self.lib.call(90,RETURN_)
#  def rotated_scaled_sprite_no_clip(self):
#    self.lib.call(91,RETURN_)
  def set_char_data(self,index,buf):
    self.lib.call(92,RETURN_NOBLOCK,index,buf)
# we're doing enough of this already
#  def wait(self):
#    self.lib.call(93,RETURN_)
  def copy_rectangle(self,src,dest,src_x,src_y,dst_x,dst_y,width,height):
    self.lib.call(94,RETURN_NOBLOCK,src,dest,src_x,src_y,dst_x,dst_y,width,height)
