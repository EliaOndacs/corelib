
def host(text: str, address: tuple[str, int], **kwds):
    from flask import Flask
    _app = Flask("easyhost")
    @_app.get("/")
    def home():
        return text
    _app.run(host=address[0], port=address[1], **kwds)

