
def host(text: str, address: tuple[str, int], **kwds):
    from flask import Flask
    _app = Flask(__name__)
    _app.route("/")((lambda: text))
    _app.run(address[0], address[1], **kwds)

