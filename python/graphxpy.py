from ez80 import *

class GfxContext:
  def __init__(self):
    self.lib=loadlib("GRAPHX",11,100)
    if self.lib==0:
      raise "Failed to load lib"
    self.funcs=self.lib+9
  
  def __enter__(self):
    call(self.funcs,RETURN_NONE,[]) # gfx_begin
    return self
    
  def __exit__(self,t,v,tb):
    call(self.funcs+4,RETURN_NONE,[]) #gfx_end
    print(t,v,tb)

  def set_color(self,color):
    call(self.funcs+8,RETURN_NOBLOCK,[color])
  def set_default_palette(self):
    call(self.funcs+12,RETURN_NOBLOCK,[27])
#  def set_palette(self):
#    call(self.funcs+16,[])
  def fill_screen(self,color):
    call(self.funcs+20,RETURN_NONE,[color])
  def set_pixel(self,x,y):
    call(self.funcs+24,RETURN_NOBLOCK,[x,y])
#  def get_pixel(self):
#    call(self.funcs+28,[])
#  def get_draw(self):
#    call(self.funcs+32,[])
  def set_draw(self,loc):
    call(self.funcs+36,RETURN_NOBLOCK,[loc])
  def swap_draw(self):
    call(self.funcs+40,RETURN_NOBLOCK,[])
  def blit(self,loc):
    call(self.funcs+44,RETURN_NONE,[loc])
  def blit_lines(self,src,y_loc,num_lines):
    call(self.funcs+48,RETURN_NONE,[src,y_loc,num_lines])
  def blit_rectangle(self,src,x,y,width,height):
    call(self.funcs+52,RETURN_NONE,[src,x,y,width,height])
  def print_char(self,char):
    call(self.funcs+56,RETURN_NOBLOCK,[char])
  def print_int(self,n,digits):
    call(self.funcs+60,RETURN_NOBLOCK,[n, digits])
  # todo: merge with above?
  def print_uint(self,n,digits):
    call(self.funcs+64,RETURN_NOBLOCK,[n, digits])
  def print_string(self,string):
    addr = malloc(len(string))
    write(addr,bytes(string,0))
    call(self.funcs+68,RETURN_NOBLOCK,[addr])
    free(addr)
  def print_string_xy(self,string,x,y):
    addr = malloc(len(string))
    write(addr,bytes(string,0))
    call(self.funcs+72,RETURN_NOBLOCK,[addr,x,y])
    free(addr)
  def set_text_xy(self,x,y):
    call(self.funcs+76,RETURN_NOBLOCK,[x,y])
  def set_text_bg_color(self,color):
    call(self.funcs+80,RETURN_NOBLOCK,[color])
  def set_text_fg_color(self,color):
    call(self.funcs+84,RETURN_NOBLOCK,[color])
  def set_text_transparent_color(self,color):
    call(self.funcs+88,RETURN_NOBLOCK,[color])
#  def set_font_data(self):
#    call(self.funcs+92,[])
#  def set_font_spacing(self):
#    call(self.funcs+96,[])
#  def set_monospace_font(self):
#    call(self.funcs+100,[])
#  def get_string_width(self):
#    call(self.funcs+104,[])
#  def get_char_width(self):
#    call(self.funcs+108,[])
#  def get_text_x(self):
#    call(self.funcs+112,[])
#  def get_text_y(self):
#    call(self.funcs+116,[])
#  def line(self):
#    call(self.funcs+120,[])
#  def horiz_line(self):
#    call(self.funcs+124,[])
#  def vert_line(self):
#    call(self.funcs+128,[])
#  def circle(self):
#    call(self.funcs+132,[])
#  def fill_circle(self):
#    call(self.funcs+136,[])
  def rectangle(self,x,y,width,height):
    call(self.funcs+140,RETURN_NOBLOCK,[x,y,width,height])
  def fill_rectangle(self,x,y,width,height):
    call(self.funcs+144,RETURN_NOBLOCK,[x,y,width,height])
#  def line_no_clip(self):
#    call(self.funcs+148,[])
#  def horiz_line_no_clip(self):
#    call(self.funcs+152,[])
#  def vert_line_no_clip(self):
#    call(self.funcs+156,[])
#  def fill_circle_no_clip(self):
#    call(self.funcs+160,[])
#  def rectangle_no_clip(self):
#    call(self.funcs+172,[])
#  def fill_rectangle_no_clip(self):
#    call(self.funcs+176,[])
#  def set_clip_region(self):
#    call(self.funcs+180,[])
#  def get_clip_region(self):
#    call(self.funcs+184,[])
#  def shift_down(self):
#    call(self.funcs+188,[])
#  def shift_up(self):
#    call(self.funcs+192,[])
#  def shift_left(self):
#    call(self.funcs+196,[])
#  def shift_right(self):
#    call(self.funcs+200,[])
#  def tilemap(self):
#    call(self.funcs+204,[])
#  def tilemap_no_clip(self):
#    call(self.funcs+208,[])
#  def transparent_tilemap(self):
#    call(self.funcs+212,[])
#  def transparent_tilemap_no_clip(self):
#    call(self.funcs+216,[])
#  def tile_ptr(self):
#    call(self.funcs+220,[])
#  def tile_ptr_mapped(self):
#    call(self.funcs+224,[])
#  def reserved(self):
#    call(self.funcs+228,[])
#  def alloc_sprite(self):
#    call(self.funcs+232,[])
#  def sprite(self):
#    call(self.funcs+236,[])
#  def transparent_sprite(self):
#    call(self.funcs+240,[])
#  def sprite_no_clip(self):
#    call(self.funcs+244,[])
#  def transparent_sprite_no_clip(self):
#    call(self.funcs+248,[])
#  def get_sprite(self):
#    call(self.funcs+252,[])
#  def scaled_sprite_no_clip(self):
#    call(self.funcs+256,[])
#  def scaled_transparent_sprite_no_clip(self):
#    call(self.funcs+260,[])
#  def flip_sprite_y(self):
#    call(self.funcs+272,[])
#  def flip_sprite_x(self):
#    call(self.funcs+276,[])
#  def rotate_sprite_c(self):
#    call(self.funcs+280,[])
#  def rotate_sprite_c_c(self):
#    call(self.funcs+284,[])
#  def rotate_sprite_half(self):
#    call(self.funcs+288,[])
#  def polygon(self):
#    call(self.funcs+292,[])
#  def polygon_no_clip(self):
#    call(self.funcs+296,[])
#  def fill_triangle(self):
#    call(self.funcs+300,[])
#  def fill_triangle_no_clip(self):
#    call(self.funcs+304,[])
#  def deprecated(self):
#    call(self.funcs+308,[])
#  def set_text_scale(self):
#    call(self.funcs+312,[])
#  def set_transparent_color(self):
#    call(self.funcs+316,[])
#  def zero_screen(self):
#    call(self.funcs+320,[])
#  def set_text_config(self):
#    call(self.funcs+324,[])
#  def get_sprite_char(self):
#    call(self.funcs+328,[])
#  def lighten(self):
#    call(self.funcs+332,[])
#  def darken(self):
#    call(self.funcs+336,[])
#  def set_font_height(self):
#    call(self.funcs+340,[])
#  def scale_sprite(self):
#    call(self.funcs+344,[])
#  def flood_fill(self):
#    call(self.funcs+348,[])
#  def rlet_sprite(self):
#    call(self.funcs+352,[])
#  def rlet_sprite_no_clip(self):
#    call(self.funcs+356,[])
#  def convert_from_rlet_sprite(self):
#    call(self.funcs+360,[])
#  def convert_to_rlet_sprite(self):
#    call(self.funcs+372,[])
#  def convert_to_new_rlet_sprite(self):
#    call(self.funcs+376,[])
#  def rotate_scale_sprite(self):
#    call(self.funcs+380,[])
#  def rotated_scaled_transparent_sprite_no_clip(self):
#    call(self.funcs+384,[])
#  def rotated_scaled_sprite_no_clip(self):
#    call(self.funcs+388,[])
#  def set_char_data(self):
#    call(self.funcs+392,[])
#  def wait(self):
#    call(self.funcs+396,[])
#  def copy_rectangle(self):
#    call(self.funcs+400,[])
