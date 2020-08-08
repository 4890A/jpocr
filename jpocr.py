import wx
import screenshot_app
mode = 'Vocab'
scale = 1


class TransparentFrame(wx.Frame):
    ''' Transparent Frame '''
    # Optional Transparency
    DEFAULT_ALPHA = 255
    DEFAULT_SIZE = (400, 200)
    TEXTCTRL_SIZE = (200, 100)
    def __init__(self, size=DEFAULT_SIZE, *args, **kwargs):
        wx.Frame.__init__(self, None, size=size, title='yomitoru', style=wx.DEFAULT_FRAME_STYLE | wx.STAY_ON_TOP, *args, **kwargs)
        # Find HDPI scale factor
        global scale
        scale = wx.GetApp().GetTopWindow().GetContentScaleFactor()

        # This is all you need to make the window transparent.
        self.SetTransparent(self.DEFAULT_ALPHA)
        pnl = wx.Panel(self)
        self.button = wx.Button(pnl, label='Scan')
        self.button.Bind(wx.EVT_BUTTON, self.onClick)
        self.Centre()
        self.Show(True)

        lblList = ['Vocab', 'Google', 'Romaji', 'DeepL']
        self.rbox = wx.RadioBox(pnl, label='Mode', pos=(80, 10), choices=lblList,
                                majorDimension=1, style=wx.RA_SPECIFY_ROWS)
        self.rbox.Bind(wx.EVT_RADIOBOX, self.onRadioBox)
        self.Centre()
        self.Show(True)

        self.Centre()
        self.Show(True)

    def onClick(self, event):
        screenshot_app.ocr_main(mode)

    def onRadioBox(self, e):
        global mode
        mode = self.rbox.GetStringSelection()

if __name__ == '__main__':
    app = wx.App(False)
    frame = TransparentFrame()
    frame.Show()
    app.MainLoop()
