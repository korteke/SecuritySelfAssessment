#!/usr/bin/env python3

import tornado.ioloop
import tornado.web
from tornadoadfsoauth2.auth import AuthHandler
import sys, json
from base import BaseHandler
import templates
from db import db
import aux
import logging

class AdminHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        if not self.is_user_admin():
            logging.info('user is not admin')
            self.finish('%s is not admin'%self.get_current_username())
            return
        self.write(templates.start)
        self.render_header()

        addcompanyform = """
<p>Existing companies: %s\n</p>
<form method="post">Add company: 
<input type="text" class="focus:outline-none focus:shadow-outline border border-gray-300 rounded-lg ml-2 py-1 px-2 appearance-none leading-normal" name="company">
<input type="hidden" name="op" value="add_company">
<input type="submit" class="m-1 p-1"></form>""" % ', '.join(db.list_companies())

        options = []
        for c in db.list_companies():
            options.append('<option value="%s">%s</option>'%(c,c))
        removecompanyform = """
<form method="post"> 
<label for="company">remove company: </label>
<select class="focus:outline-none focus:shadow-outline border border-gray-300 rounded-lg ml-2 py-1 px-2 appearance-none leading-normal" name="company" id="company">
<option value=""></option>
%s
</select>
<input type="hidden" name="op" value="remove_company">
<input type="submit" class="m-1 p-1"></form>"""%('\n'.join(options))

        # fuck. https://docs.python.org/3/library/logging.html#levels
        levels = {10: 'DEBUG', 20: 'INFO', 30: 'WARNING', 40: 'ERROR', 50: 'CRITICAL', 0: 'NOTSET'}
        loglevelform = """
<p>Current log level: %s</p>
<form method="post"> 
<label for="loglevel">set log level: </label>
<select class="focus:outline-none focus:shadow-outline border border-gray-300 rounded-lg ml-2 py-1 px-2 appearance-none leading-normal" name="loglevel" id="loglevel">
<option value=""></option>
<option value="DEBUG">DEBUG</option>
<option value="INFO">INFO</option>
<option value="WARNING">WARNING</option>
<option value="ERROR">ERROR</option>
<option value="CRITICAL">CRITICAL</option>
</select>
<input type="hidden" name="op" value="set_loglevel">
<input type="submit" class="m-1 p-1"></form>""" % str(levels[logging.getLogger().getEffectiveLevel()])
        
        self.write(templates.div('bg-blue-300 m-1 p-1', addcompanyform + removecompanyform))
        self.write(templates.div('bg-blue-300 m-1 p-1', loglevelform))

        self.write(templates.end)

    def post(self):
        self.redirect('/admin/')
        op = self.get_body_argument('op', 'nop')
        if op == 'add_company':
            company = self.get_body_argument('company', '')
            db.add_company(company)
        if op == 'remove_company':
            company = self.get_body_argument('company', '')
            db.remove_company(company)
        elif op == 'set_loglevel':
            loglevel = self.get_body_argument('loglevel', '')
            logger = logging.getLogger()
            if loglevel == 'INFO':
                logger.setLevel(logging.INFO)
            elif loglevel == 'DEBUG':
                logger.setLevel(logging.DEBUG)
            elif loglevel == 'WARNING':
                logger.setLevel(logging.WARNING)
            elif loglevel == 'ERROR':
                logger.setLevel(logging.ERROR)
            elif loglevel == 'CRITICAL':
                logger.setLevel(logging.CRITICAL)
                
