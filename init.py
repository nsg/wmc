#!/usr/bin/env python

import commands
import re
import wx

class Windows():
    def __init__(self):
        self.raw = commands.getoutput("wmctrl -lGp").split("\n")
        self._curdesk = self.curdesk()

    def curdesk(self):
        return [ l.split()[0] for l in commands.getoutput("wmctrl -d").split("\n") if l.split()[1] == "*"][0]

    def filter(self):
        return [l for l in self.raw if l.split()[1] == self._curdesk and not re.search("Window Mark", l)]

    def find_self(self):
        return [l for l in self.raw if re.search("Window Mark", l)][0].split()

    def w_id_self(self):
        return self.find_self()[0]

    def search(self, w_id):
        n = 0
        for l in self.filter():
            if re.search(w_id, l.split()[0]):
                return n
            n += 1
        return -1

    def size(self):
        return len(self.filter())

    def window(self, n):
        return self.filter()[n].split()

    def w_id(self, n):
        return self.window(n)[0]

    def pid(self, n):
        return int(self.window(n)[2])

    def abs_x(self, n):
        return int(self.window(n)[3])

    def abs_y(self, n):
        return int(self.window(n)[4])

    def width(self, n):
        return int(self.window(n)[5])

    def height(self, n):
        return int(self.window(n)[6])

    def focus(self, w_id):
        commands.getoutput("wmctrl -i -R {}".format(w_id))

class CurrentWindow():
    def __init__(self):
        self.raw = commands.getoutput("xwininfo -id $(xdotool getactivewindow)").split("\n")

    def w_id(self):
        return [l.split()[3].split("x")[1] for l in self.raw if re.search("Window id:", l)][0]

class MarkWindow(wx.Frame):
    selwin = -1
    tagMode = 0

    def __init__(self):
        style = ( wx.CLIP_CHILDREN | wx.STAY_ON_TOP | wx.FRAME_NO_TASKBAR | wx.NO_BORDER | wx.FRAME_SHAPED  )
        wx.Frame.__init__(self, None, title='Window Mark', style = style)

        w = Windows()
        self.SetSize((100, 100))
        self.SetPosition((
            w.abs_x(MarkWindow.selwin) + w.width(MarkWindow.selwin) / 2 - 25,
            w.abs_y(MarkWindow.selwin) + w.height(MarkWindow.selwin) / 2 - 25
        ))

        self.panel = wx.Panel(self)
        self.panel.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.panel.SetFocus()
        self.panel.SetBackgroundColour('#a70000')

        self.text("    WMC")

        if wx.Platform == '__WXGTK__':
            self.Bind(wx.EVT_WINDOW_CREATE, self.SetRoundShape)
        else:
            self.SetRoundShape()
        self.Show(True)

    def text(self, s):
        self.panel.DestroyChildren()
        text = wx.StaticText(self.panel, pos=(5,30), label=s)
        text.SetForegroundColour((255,255,255))

    def SetRoundShape(self, event=None):
        w, h = self.GetSizeTuple()
        self.SetShape(self.GetRoundShape(w,h,80))

    def GetRoundShape(self, w, h, r):
        return wx.RegionFromBitmap(self.GetRoundBitmap(w,h,r))

    def GetRoundBitmap(self, w, h, r):
        maskColor = wx.Color(0,0,0)
        shownColor = wx.Color(5,5,5)
        b = wx.EmptyBitmap(w,h)
        dc = wx.MemoryDC(b)
        dc.SetBrush(wx.Brush(maskColor))
        dc.DrawRectangle(0,0,w,h)
        dc.SetBrush(wx.Brush(shownColor))
        dc.SetPen(wx.Pen(shownColor))
        dc.DrawRoundedRectangle(0,0,80,80,r)
        dc.SelectObject(wx.NullBitmap)
        b.SetMaskColour(maskColor)
        return b

    def OnKeyDown(self, event):
        keycode = event.GetKeyCode()

        if MarkWindow.tagMode == 1:
            w = Windows()
            w_id = w.w_id(MarkWindow.selwin)
            f = open("/tmp/wmc-tagfile.dat", "a")
            f.write("{} {}\n".format(w_id,keycode))
            f.close()
        elif MarkWindow.tagMode == 2:
            w = Windows()
            with open('/tmp/wmc-tagfile.dat', 'r') as cfile:
                content = cfile.read()
            for line in content.strip().split("\n"):
                (w_id, kc) = line.split()
                if keycode == int(kc):
                    MarkWindow.selwin = w.search(w_id)
                    self.SetPosition((
                        w.abs_x(MarkWindow.selwin) + w.width(MarkWindow.selwin) / 2 - 25,
                        w.abs_y(MarkWindow.selwin) + w.height(MarkWindow.selwin) / 2 - 25
                    ))
                    w.focus(w_id)
                    w.focus(w.w_id_self())
        if MarkWindow.tagMode > 0:
            self.panel.SetBackgroundColour('#a70000')
            MarkWindow.tagMode = 0
            return

        if keycode == ord('Q'):
            self.Close(force=True)
        if keycode == 32:
            w = Windows()
            if MarkWindow.selwin >= w.size() - 1:
                MarkWindow.selwin = 0
            else:
                MarkWindow.selwin += 1
            self.SetPosition((
                w.abs_x(MarkWindow.selwin) + w.width(MarkWindow.selwin) / 2 - 25,
                w.abs_y(MarkWindow.selwin) + w.height(MarkWindow.selwin) / 2 - 25
            ))
            self.text("pid: " + str(w.pid(MarkWindow.selwin)))
            print w.window(MarkWindow.selwin)
        if keycode == ord('V'):
            w = Windows()
            w_id = w.w_id(MarkWindow.selwin)
            w.focus(w_id)
            w.focus(w.w_id_self())
        if keycode == ord('F'):
            w = Windows()
            w_id = w.w_id(MarkWindow.selwin)
            w.focus(w_id)
            self.Close(force=True)
        if keycode == ord('T'):
            self.panel.SetBackgroundColour('#395ee8')
            MarkWindow.tagMode = 1
        if keycode == ord('S'):
            self.panel.SetBackgroundColour('#f9c423')
            MarkWindow.tagMode = 2
            
        event.Skip()

cw = CurrentWindow()
w = Windows()
MarkWindow.selwin = w.search(cw.w_id())
app = wx.App()

MarkWindow()

app.MainLoop()

