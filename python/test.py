import graphxpy, ez80

with graphxpy.GfxContext() as gfx:
  gfx.set_draw(1)
  for i in range(20):
    gfx.fill_screen(i)
    gfx.set_color(255 - i)
    gfx.fill_rectangle(25,i,50,12)
    gfx.set_text_xy(26,i+1)
    gfx.print_string("hello world")
    gfx.blit(1)
