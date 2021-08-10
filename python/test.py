import graphxpy, ez80, keypadpy

with graphxpy.GfxContext() as gfx:
  gfx.set_draw(graphxpy.BUFFER)
  x = 50
  y = 50
  while True:
    keys = keypadpy.get_keys()
    if keys.is_down(keypadpy.KEY_CLEAR):
      break
    if keys.is_down(keypadpy.KEY_LEFT):
      x -= 5
    if keys.is_down(keypadpy.KEY_RIGHT):
      x += 5
    if keys.is_down(keypadpy.KEY_UP):
      y -= 5
    if keys.is_down(keypadpy.KEY_DOWN):
      y += 5
    gfx.fill_screen(255)
    gfx.set_color(248)
    gfx.fill_rectangle(x,y,50,12)
    gfx.set_text_xy(x,y)
    gfx.print_string("hello python")
    gfx.blit(graphxpy.BUFFER)
