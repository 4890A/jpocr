import argparse
import MeCab
from enum import Enum
import io
import textwrap

from google.cloud import vision
from google.cloud.vision import types
from PIL import Image, ImageDraw

import pprint
pp = pprint.PrettyPrinter(depth=6)


import wx
from PIL import Image, ImageGrab

import pykakasi
kks = pykakasi.kakasi()

global selectionOffset, selectionSize, c1x, c2x, c1y, c2y
c1x = 0
c2x = 0
c1y = 0
c2y = 0

selectionOffset = ""
selectionSize = ""

class SelectableFrame(wx.Frame):

    c1 = None
    c2 = None

    def __init__(self, parent=None, id=wx.ID_ANY, title=""):
        wx.Frame.__init__(self, parent, id, title, size=wx.DisplaySize())
        self.menubar = wx.MenuBar(wx.MB_DOCKABLE)
        self.filem = wx.Menu()
        self.filem.Append(wx.ID_EXIT, '&Transparency')
        self.menubar.Append(self.filem, '&File')
        self.SetMenuBar(self.menubar)
        self.Bind(wx.EVT_MOTION, self.OnMouseMove)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnMouseDown)
        self.Bind(wx.EVT_LEFT_UP, self.OnMouseUp)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_MENU, self.OnTrans)

        self.SetCursor(wx.Cursor(wx.CURSOR_CROSS))
        self.Show()
        self.transp = False
        wx.CallLater(250, self.OnTrans, None)

    def OnTrans(self, event):
        if self.transp == False:
            self.SetTransparent(50)
            self.transp = True
        else:
            self.SetTransparent(255)
            self.transp = False

    def OnMouseMove(self, event):
        if event.Dragging() and event.LeftIsDown():
            self.c2 = event.GetPosition()
            self.Refresh()

    def OnMouseDown(self, event):
        self.c1 = event.GetPosition()

    def OnMouseUp(self, event):
        self.SetCursor(wx.Cursor(wx.CURSOR_ARROW))
        self.Destroy()

    def OnPaint(self, event):
        global selectionOffset, selectionSize
        global c1x, c2x, c1y, c2y
        if self.c1 is None or self.c2 is None: return

        dc = wx.PaintDC(self)
        dc.SetPen(wx.Pen('red', 3))
        dc.SetBrush(wx.Brush(wx.Colour(0, 0, 0), wx.TRANSPARENT))

        dc.DrawRectangle(self.c1.x, self.c1.y, self.c2.x - self.c1.x, self.c2.y - self.c1.y)

        c1x = self.c1.x
        c1y = self.c1.y
        c2x = self.c2.x
        c2y = self.c2.y
        selectionOffset = str(self.c1.x) + "x" + str(self.c1.y)
        selectionSize = str(abs(self.c2.x - self.c1.x)) + "x" + str(abs(self.c2.y - self.c1.y))

    def PrintPosition(self, pos):
        return str(pos.x) + "x" + str(pos.y)


class MyApp(wx.App):

    def OnInit(self):
        frame = SelectableFrame()

        return True


app = MyApp(redirect=False)
app.MainLoop()
im2 = ImageGrab.grab(bbox=(c1x+10, c1y+35, c2x+15, c2y+50))
im2.save('temp.png')


def get_document_bounds(image_file, feature):
    """Returns document bounds given an image."""
    client = vision.ImageAnnotatorClient()

    bounds = []

    with io.open(image_file, 'rb') as image_file:
        content = image_file.read()

    image = types.Image(content=content)

    response = client.document_text_detection(image=image)
    document = response.full_text_annotation
    texts = response.text_annotations

    s = wx.ScreenDC()
    ss_x1 = c1x + 10
    ss_x2 = c2x + 15
    ss_y1 = c1y + 35
    ss_y2 = c2y + 50

    for page in document.pages:
        for block in page.blocks:
            results = []
            results.append([])
            print('\n')
            for paragraph in block.paragraphs:
                for word in paragraph.words:
                    for symbol in word.symbols:
                        results[-1].append(symbol.text)

            bound = block.bounding_box
            start_x = bound.vertices[0].x
            start_y = bound.vertices[0].y

            width = bound.vertices[2].x - bound.vertices[0].x
            height = bound.vertices[2].y - bound.vertices[0].y

            s.Pen = wx.Pen("#FF0000")
            s.SetTextForeground((255, 0, 0))
            s.SetTextBackground((0, 0, 0))
            s.Brush = wx.Brush(wx.Colour(255,255,255))

            s.SetFont(wx.Font(10, wx.FONTFAMILY_DECORATIVE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))

            # results[-1] = ''.join(results[-1])
            ocr_results = ''.join(results[-1])
            print(ocr_results)
            items = kks.convert(ocr_results)

            for item in items:
                print(item['orig'], end = '')
            print('\n')

            for item in items:
                print("{}[{}] ".format(item['orig'], item['hepburn'].capitalize()), end='')
            print('\n')
            hepburn_block = ""
            for item in items:
                print(item['hepburn'], end =' ')
                hepburn_block = hepburn_block + " " + item['hepburn']
            print('\n')
            hepburn_block = '\n'.join(textwrap.wrap(hepburn_block, 25))
            nl_separated_block = hepburn_block.split('\n')
            max_x_bound = max([s.GetTextExtent(line)[0] for line in nl_separated_block]) + 3
            max_y_bound = s.GetTextExtent(hepburn_block)[1] * len(nl_separated_block) + 3

            w, h, = s.GetTextExtent(hepburn_block)

            s.DrawRectangle(ss_x1 + start_x - 3, ss_y1 + start_y - 3, max_x_bound, max_y_bound)
            s.DrawText(hepburn_block, ss_x1 + start_x, ss_y1 + start_y )



def render_doc_text(filein, fileout):
    image = Image.open(filein)
    get_document_bounds(filein, FeatureType.BLOCK)

render_doc_text('./temp.png', 0)



