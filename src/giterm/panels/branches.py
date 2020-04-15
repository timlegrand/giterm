from giterm.panels import StateLinePanel
import giterm.rungit as rungit

class BranchesPanel(StateLinePanel):
   def __init__(self, *args, **kwargs):
      StateLinePanel.__init__(self, *args, **kwargs)
      self.rungit = rungit.git_branches

   def select(self):
      self.update_selection()
      if self.selected_content_line != -1:
         selected_branch = self.content[self.selected_content_line]
         self.decorations = {}
         self.action(selected_branch)
      self.display()

   def action(self, branch):
      error, output = rungit.git_checkout_branch(branch)
      if error:
         self.selected_content_line = -1
         self.parent.popup('Branch error', str(output))
      else:
         self.handle_event()