import wx
from wx.html2 import WebView


def launcher(manifest: dict):

    app = wx.App(False)
    window = wx.Frame(None, wx.ID_ANY, manifest.get("name", "untitled"))
    if "icon" in manifest:
        window.SetIcon(wx.Icon(manifest["icon"], wx.BITMAP_TYPE_ICO))

    view: WebView = WebView.New(window, wx.ID_ANY)
    # Create a sizer to manage the layout
    sizer = wx.BoxSizer(wx.VERTICAL)
    sizer.Add(view, 1, wx.EXPAND | wx.ALL, 0)  # Add the web view to the sizer

    if not manifest.get("border", False):
        window.SetWindowStyleFlag(wx.BORDER_NONE | wx.RESIZE_BORDER)

    # Set the sizer for the frame
    window.SetSizer(sizer)
    window.Layout()  # Layout the frame
    if "index" in manifest:
        url = manifest.get("index", None)
        if os.path.exists(url):
            url = open(url).read()
        view.SetPage(url, manifest.get("url", "http://localhost"))

    view.Show()
    window.Show()
    app.MainLoop()
    app.Destroy()

    return


import json, os

if __name__ == "__main__":
    print("starting the XWLauncher")
    base = os.path.dirname(os.path.abspath(__file__))
    launcher(json.load(open(os.path.join(base, "setup.json"))))
# end main
