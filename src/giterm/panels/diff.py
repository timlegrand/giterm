from giterm.panels import Panel
from giterm.colors import colors
import giterm.textutils as text
import threading, curses

class DiffPanel(Panel):
   def __init__(self, *args, **kwargs):
      super(DiffPanel, self).__init__(*args, **kwargs)
      self.default_title = self.title
      self.running = threading.Lock()

   def setup_content(self):
      if not self.data:
         return
      self.content = []
      cut_line = '-' * (self.CW // 2 - 1) + '8<' + '-' * (self.CW // 2 - 1)
      for h in self.data:
         self.content += text.remove_superfluous_alineas(h)
         self.content.append(cut_line)

      for i, line in enumerate(self.content):
         if line.startswith('+') and not line.startswith('++'):
            self.decorations[i] = colors.diff_green
         elif line.startswith('-') and not line.startswith('--'):
            self.decorations[i] = colors.diff_red

   def handle_event(self, filepath, staged=False):
      self.running.acquire()
      if filepath is None or type(filepath) is not str:
         self.running.release()
         return

      error, output = self.rungit(filepath, staged)

      if error:
         self.parent.popup('Exception', output)
      else:
         self.decorations = {}
         self.data = output
         self.setup_content()
         self.topLineNum = 0
         self.selected_content_line = -1
         self.hovered_content_line = 0
         message = ": " + filepath if type(filepath) == str else ''
         self.title = self.default_title + message
         self.display()
      self.running.release()

   def activate(self):
      self.cursor_y = 1
      super(DiffPanel, self).activate()
      return self