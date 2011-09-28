#!/usr/bin/env python
# coding: utf-8

import wx


class MyFrame(wx.Frame):
  def __init__(self, parent, id, title, pos=wx.DefaultPosition,
               size=wx.DefaultSize, style=wx.DEFAULT_FRAME_STYLE):
    wx.Frame.__init__(self, parent, id, title, pos, size, style)
    panel = wx.Panel(self)


class MyApp(wx.App):
  def OnInit(self):
    frame = MyFrame(None, -1, "PCounter")
    self.SetTopWindow(frame)
    frame.Show()
    return True

if __name__ == '__main__':
  app = MyApp(redirect=True)
  app.MainLoop() 

