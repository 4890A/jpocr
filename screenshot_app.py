import io
import textwrap
import requests
import wx
import pyperclip
from PIL import Image, ImageGrab

from googletrans import Translator
from google.cloud import vision
from google.cloud.vision import types
from secrets import deepL_auth

from jamdict import Jamdict
jmd = Jamdict()
from fugashi import Tagger
import cutlet

from rich import print
from rich.console import Console
from rich.progress import track
from rich.table import Column, Table
console = Console()
from rich import box



global mode
mode = 'EOP'


global selectionOffset, selectionSize, c1x, c2x, c1y, c2y, c1x_delta, c2x_delta, c1y_delta, c2y_delta
c1x = 0
c2x = 0
c1y = 0
c2y = 0

# offsets to account for selection window decorations
c1x_delta = 0
c2x_delta = 0
c1y_delta = 28
c2y_delta = 15


selectionOffset = ""
selectionSize = ""

clipboard_buffer = ""

class SelectableFrame(wx.Frame):

    c1 = None
    c2 = None

    def __init__(self, parent=None, id=wx.ID_ANY, title=""):
        wx.Frame.__init__(self, parent, id, title, size=wx.DisplaySize())
        self.ShowFullScreen(True)
        self.menubar = wx.MenuBar(wx.MB_DOCKABLE)
        self.filem = wx.Menu()
        self.filem.Append(wx.ID_EXIT, "&Transparency")
        self.menubar.Append(self.filem, "&File")
        self.SetMenuBar(self.menubar)
        self.Bind(wx.EVT_MOTION, self.OnMouseMove)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnMouseDown)
        self.Bind(wx.EVT_LEFT_UP, self.OnMouseUp)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_MENU, self.OnTrans)
        self.Bind(wx.EVT_KEY_DOWN, self.onKey)

        self.SetCursor(wx.Cursor(wx.CURSOR_CROSS))
        self.Show()
        self.transp = False
        self.scale = wx.GetApp().GetTopWindow().GetContentScaleFactor()
        wx.CallLater(250, self.OnTrans, None)

    def OnTrans(self, event):
        if self.transp == False:
            self.SetTransparent(50)
            self.transp = True
        else:
            self.SetTransparent(255)
            self.transp = False

    def onKey(self, event):
        """
        Check for ESC key press and exit is ESC is pressed
        """
        key_code = event.GetKeyCode()
        if key_code == wx.WXK_ESCAPE:
            self.Close()
        else:
            event.Skip()

    def OnMouseMove(self, event):
        if event.Dragging() and event.LeftIsDown():
            self.c2 = event.GetPosition()
            self.Refresh()

    def OnMouseDown(self, event):
        self.c1 = event.GetPosition()

    def OnMouseUp(self, event):
        self.SetCursor(wx.Cursor(wx.CURSOR_ARROW))
        self.Destroy()
        bbox = [c1x + c1x_delta, c1y + c1y_delta, c2x + c2x_delta, c2y + c2y_delta]
        for i in range(len(bbox)):
            bbox[i] = bbox[i] * self.scale
        bbox = tuple(bbox)
        img = ImageGrab.grab(bbox=bbox)
        img.save("temp.png")
        clipboard_buffer = ""
        clipboard_buffer = render_doc_text("./temp.png", 0, clipboard_buffer)
        pyperclip.copy(clipboard_buffer)


    def OnPaint(self, event):
        global selectionOffset, selectionSize
        global c1x, c2x, c1y, c2y
        if self.c1 is None or self.c2 is None:
            return

        dc = wx.PaintDC(self)
        dc.SetPen(wx.Pen("red", 3))
        dc.SetBrush(wx.Brush(wx.Colour(0, 0, 0), wx.TRANSPARENT))

        dc.DrawRectangle(
            self.c1.x, self.c1.y, self.c2.x - self.c1.x, self.c2.y - self.c1.y
        )

        c1x = self.c1.x
        c1y = self.c1.y
        c2x = self.c2.x
        c2y = self.c2.y
        selectionOffset = str(self.c1.x) + "x" + str(self.c1.y)
        selectionSize = (
            str(abs(self.c2.x - self.c1.x)) + "x" + str(abs(self.c2.y - self.c1.y))
        )


    def PrintPosition(self, pos):
        return str(pos.x) + "x" + str(pos.y)



def recognize_image(image_file, clipboard_buffer):
    """Returns document bounds given an image."""
    client = vision.ImageAnnotatorClient()


    with io.open(image_file, "rb") as image_file:
        content = image_file.read()

    image = types.Image(content=content)

    response = client.document_text_detection(image=image)
    document = response.full_text_annotation
    texts = response.text_annotations

    s = wx.ScreenDC()
    ss_x1 = c1x + c1x_delta
    ss_x2 = c2x + c2x_delta
    ss_y1 = c1y + c1y_delta
    ss_y2 = c2y + c2y_delta
    global mode

    console_output = ""
    table = Table(show_header=True, header_style='bold magenta', box=box.MINIMAL_DOUBLE_HEAD)
    table.add_column("日本語", style='dim')
    table.add_column(mode)
    if mode == 'Vocab':
        table.add_column('読み方')
        table.add_column('意味')
    for page in document.pages:
        for block in track(page.blocks):
            results = []
            results.append([])
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
            s.Brush = wx.Brush(wx.Colour(255, 255, 255))

            s.SetFont(
                wx.Font(
                    12,
                    wx.FONTFAMILY_DECORATIVE,
                    wx.FONTSTYLE_NORMAL,
                    wx.FONTWEIGHT_BOLD,
                )
            )

            ocr_results = "".join(results[-1])

            clipboard_buffer = clipboard_buffer + ocr_results
            clipboard_buffer = clipboard_buffer + "\n"
            if mode == 'Romaji':
                katsu = cutlet.Cutlet()
                hepburn_block =  katsu.romaji(ocr_results)
                table.add_row(ocr_results, hepburn_block)
                hepburn_block = "\n".join(textwrap.wrap(hepburn_block, 25))

            if mode == 'Vocab':
                tagger = Tagger('-Owakati')

                nl_separated_block = []
                for word in tagger(ocr_results):
                    if word.char_type == 2:
                        results = jmd.lookup(str(word.feature.lemma))
                        meaning = ' '
                        for k in range(len(results.entries)):
                            result = results.entries[k]
                            if k > 0:
                                meaning =  meaning + '\n '
                            meaning = meaning +  str(k + 1) + '.' + ' \\ '.join([str(sense.gloss[0]) for sense in result.senses])
                        console_output = console_output + '\t'.join([str(word), '『' + word.feature.kana + '』', meaning, '\n'])
                        nl_separated_block.append('\t'.join([str(word), '『' + word.feature.kana + '』', meaning]))
                        table.add_row(str(word), str(word.feature.lemma), '『' + word.feature.kana + '』', meaning )
                hepburn_block = '\n'.join(nl_separated_block)
                # table.add_row(ocr_results, hepburn_block)

            if mode == 'Google':
                translator = Translator()
                translated = translator.translate(ocr_results).text
                table.add_row('\n'.join(textwrap.wrap(ocr_results, 25)), translated)
                hepburn_block = "\n".join(textwrap.wrap(translated, 25))

            if mode == 'DeepL':
                url = 'https://api.deepl.com/v2/translate'
                response = requests.get(url, params={"auth_key": deepL_auth, "text": ocr_results, "target_lang": "EN"})
                result = response.json()
                translated = result['translations'][0]['text']
                table.add_row('\n'.join(textwrap.wrap(ocr_results, 25)) + '\n', translated)
                hepburn_block = "\n".join(textwrap.wrap(translated, 40))

            nl_separated_block = hepburn_block.split("\n")
            max_x_bound = (
                max([s.GetTextExtent(line)[0] for line in nl_separated_block]) + 3
            )
            max_y_bound = (
                s.GetTextExtent(hepburn_block)[1] * len(nl_separated_block) + 3
            )
            w, h, = s.GetTextExtent(hepburn_block)

            # modify this with dpi scale when screen device context is fixed
            s.DrawRectangle(
                ss_x1 + start_x - 3, ss_y1 + start_y - 3, max_x_bound, max_y_bound
            )
            s.DrawText(hepburn_block, ss_x1 + start_x, ss_y1 + start_y)
    console.print(table)
    return clipboard_buffer

class screenshotApp(wx.App):
    def OnInit(self):
        frame = SelectableFrame()
        return True

def render_doc_text(filein, fileout, clipboard_buffer):
    image = Image.open(filein)
    return recognize_image(filein, clipboard_buffer)


def ocr_main(window_mode):
    global mode
    mode = window_mode
    ssframe = SelectableFrame()
