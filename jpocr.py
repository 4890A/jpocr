import wx
import screenshot_app

mode = 'EOP'

class TransparentFrame(wx.Frame):
    ''' Transparent Frame '''
    DEFAULT_ALPHA = 255
    DEFAULT_SIZE = (400, 200)
    TEXTCTRL_SIZE = (200, 100)
    def __init__(self, size=DEFAULT_SIZE, *args, **kwargs):
        wx.Frame.__init__(self, None, size=size, title='jpocr', *args, **kwargs)
        # This is all you need to make the window transparent.
        self.SetTransparent(self.DEFAULT_ALPHA)

        pnl = wx.Panel(self)
        self.button = wx.Button(pnl, label='Scan')
        self.button.Bind(wx.EVT_BUTTON, self.onClick)
        self.Centre()
        self.Show(True)


        lblList = ['EOP', 'Vocab', 'Romaji']

        self.rbox = wx.RadioBox(pnl, label='RadioBox', pos=(80, 10), choices=lblList,
                                majorDimension=1, style=wx.RA_SPECIFY_ROWS)
        self.rbox.Bind(wx.EVT_RADIOBOX, self.onRadioBox)
        self.Centre()
        self.Show(True)

        # sizer = wx.BoxSizer(wx.VERTICAL)
        # button = wx.Button(self, label='Scan')
        # button.Bind(wx.EVT_BUTTON, self.onClick)
        # sizer.Add(button, 0, wx.ALL, 10)
        # sizer.Add(pnl, 30, wx.ALL, 30)

        # self.SetSizer(sizer)
        self.Centre()
        self.Show(True)




    def onClick(self, event):
        btn = event.GetEventObject().GetLabel()
        screenshot_app.ocr_main(mode)

    def onRadioBox(self, e):
        global mode
        mode = self.rbox.GetStringSelection()
        print(mode)



if __name__ == '__main__':
    app = wx.App(False)
    frame = TransparentFrame()
    # frame.SetIcon()
    frame.Show()
    app.MainLoop()