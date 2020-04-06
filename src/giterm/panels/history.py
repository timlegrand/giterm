from giterm.panels import StateLinePanel
import giterm.textutils as text
import curses

class HistoryPanel(StateLinePanel):
   def handle_event(self, event):
      data = self.rungit()
      self.content = []
      for e in data:
         (labels, msg, author, date, sha1) = e
         for i, b in enumerate(labels):
               labels[i] = '(' + b + ')'
         l2 = min(19, int(self.CW * 0.1))
         l3 = min(19, int(self.CW * 0.15))
         l4 = len(sha1) + 1
         l1 = int(self.CW - l2 - l3 - l4 - 3 * len(' | '))
         message, lm = text.shorten(''.join(labels) + msg, l1)
         author, la = text.shorten(author, l2, dots=False)
         date, ld = text.shorten(date, l3, dots=False)
         sha1, ls = text.shorten(sha1, l4, dots=False)
         line = "{:<{col1}} | {:<{col2}} | {:<{col3}} | {:<{col4}}".format(
               message,
               author,
               date,
               sha1,
               col1=l1,
               col2=l2,
               col3=l3,
               col4=l4)
         self.content.append(line)
      self.content[0] = '*' + self.content[0]
      for i, line in enumerate(self.content):
         if line.startswith('*'):
               self.decorations[i] = curses.A_BOLD
               self.content[i] = line[1:]
      self.display()