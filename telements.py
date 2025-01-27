
def div(*childs):
    return "".join(map(str, childs))

def br():
    return "\n"

def register():
    return '\r'

def span(body = ""):
    return str(body)

def heading(body):
    return div('# ', str(body).capitalize())

def script(code: str):
    exec(str(code), globals())
    return ""

