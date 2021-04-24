#!/usr/bin/env python

start="""<html>
<head>
<link rel="stylesheet" type="text/css" href="/assets/css/app.css">
<title>SSA</title>
</head>

<body>
<div id="app" class="font-sans p-4">

"""

end="""
</div>
</body></html>
"""

def div(cls, content):
    return '<div class="%s">\n%s\n</div>'%(cls, content)

def select(name, values, default):
    r = '<select id="%s" name="%s">\n'%(name,name)
    for v in values:
        r += '  <option value="%s"%s>%s</option>\n'%(v, " selected" if v == default else "", v)
    r += '</select>\n'
    return r
