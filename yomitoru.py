import wx
import screenshot_app

mode = "Vocab"


class TransparentFrame(wx.Frame):
    """ Transparent Frame """

    # Optional Transparency
    DEFAULT_ALPHA = 255
    DEFAULT_SIZE = (400, 200)
    TEXTCTRL_SIZE = (200, 100)

    def __init__(self, size=DEFAULT_SIZE, *args, **kwargs):
        wx.Frame.__init__(
            self,
            None,
            size=size,
            title="yomitoru",
            style=wx.DEFAULT_FRAME_STYLE | wx.STAY_ON_TOP,
            *args,
            **kwargs
        )
        # Find HDPI scale factor
        self.screen = 0

        # This is all you need to make the window transparent.
        self.SetTransparent(self.DEFAULT_ALPHA)
        pnl = wx.Panel(self)
        self.button = wx.Button(pnl, label="Scan")
        self.button.Bind(wx.EVT_BUTTON, self.onClick)

        self.btn = wx.Button(pnl, label="Switch Display")
        self.btn.Bind(wx.EVT_BUTTON, self.switch_displays)

        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        main_sizer.AddStretchSpacer()
        main_sizer.Add(self.button, 0, wx.CENTER)
        main_sizer.AddStretchSpacer()
        pnl.SetSizer(main_sizer)

        # # self.Centre()
        # self.Show(True)

        lblList = ["Vocab", "Google", "Romaji", "DeepL"]
        self.rbox = wx.RadioBox(
            pnl,
            label="Mode",
            pos=(80, 10),
            choices=lblList,
            majorDimension=1,
            style=wx.RA_SPECIFY_ROWS,
        )
        self.rbox.Bind(wx.EVT_RADIOBOX, self.onRadioBox)
        self.Centre()
        self.Show(True)

    def switch_displays(self, event):
        combined_screen_size = wx.DisplaySize()
        for index in range(wx.Display.GetCount()):
            display = wx.Display(index)
            geo = display.GetGeometry()

        current_w, current_h = self.GetPosition()

        screen_one = wx.Display(0)
        _, _, screen_one_w, screen_one_h = screen_one.GetGeometry()
        screen_two = wx.Display(1)
        _, _, screen_two_w, screen_two_h = screen_two.GetGeometry()

        if current_w > combined_screen_size[0] / 2:
            # probably on second screen
            self.SetPosition((int(screen_one_w / 2), int(screen_one_h / 2)))
            self.screen = 0
        else:
            self.SetPosition(
                (int(screen_one_w + (screen_two_w / 2)), int(screen_two_h / 2))
            )
            self.screen = 1

    def onClick(self, event):
        screenshot_app.ocr_main(mode, self.screen)

    def onRadioBox(self, e):
        global mode
        mode = self.rbox.GetStringSelection()


if __name__ == "__main__":
    app = wx.App(False)
    frame = TransparentFrame()
    frame.Show()
    app.MainLoop()
