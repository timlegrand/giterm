import curses

class Colors():
   def __init__(self):
      self.colors = {}

   def create(self):
      diff_green = 1
      diff_red = 2

      curses.init_color(diff_green, 50, 205, 50)
      curses.init_pair(diff_green, curses.COLOR_WHITE, diff_green)
      curses.init_color(diff_red, 205, 50, 50)
      curses.init_pair(diff_red, curses.COLOR_WHITE, diff_red)

      self.colors['diff_green'] = curses.color_pair(diff_green)
      self.colors['diff_red'] = curses.color_pair(diff_red)

   @property
   def diff_green(self):
      return self.colors['diff_green']

   @property
   def diff_red(self):
      return self.colors['diff_red']

colors = Colors()
