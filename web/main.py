#!/usr/bin/env python3

import tornado.web
from tornadoadfsoauth2.session import sessions
from server import BaseHandler

h="""
<html><head><title>SSA</title></head>
<body>
%s
</body></html>
"""


