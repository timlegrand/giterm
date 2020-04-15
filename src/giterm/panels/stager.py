from giterm.panels import Panel
from giterm.postponer import Postponer
import giterm.rungit as rungit

class StagerUnstagerPanel(Panel):
   def __init__(self, *args, **kwargs):
      super(StagerUnstagerPanel, self).__init__(*args, **kwargs)
      self.default_title = self.title
      self.postponer = Postponer(timeout_in_seconds=0.3)

   def filename_from_linenum(self, linenum):
      if linenum < 0 or linenum >= len(self.content):
         return ''
      line = None
      try:
         line = self.content[linenum]
      except:
         return ''
      return line.split()[1]

   def move_cursor(self):
      super(StagerUnstagerPanel, self).move_cursor()
      if self.active:
         self.request_diff_in_diff_view()

   def handle_event(self, event=None):
      super(StagerUnstagerPanel, self).handle_event()
      self.request_diff_in_diff_view()

   def activate(self):
      this = super(StagerUnstagerPanel, self).activate()
      self.request_diff_in_diff_view()
      return this

   def request_diff_in_diff_view(self, even_not_active=False):
      if not self.active and not even_not_active:
         return
      self.hovered_content_line = self.cursor_y + self.topLineNum - self.CT
      if self.hovered_content_line < 0 or self.hovered_content_line >= len(self.content):
         return
      filepath = self.filename_from_linenum(self.hovered_content_line)
      if self.content and filepath:
         self.postponer.set(
               action=self.parent['diff'].handle_event,
               args=[filepath, (self.title == 'Staging Area')])

   def select(self):
      self.update_selection()
      if self.selected_content_line != -1:
         self.selected_file = self.filename_from_linenum(self.selected_content_line)
         self.cursor_y = max(self.cursor_y - 1, self.CT)
         self.action(self.selected_file)
         self.unselect()
      self.display()

   @property
   def has_changes(self):
      return self.content
