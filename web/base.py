#!/usr/bin/env python3
import tornado.web, sys, base64
from tornado import escape
from tornadoadfsoauth2.session import sessions
from templates import *
import logging
import os

jorma_secret = os.environ.get('auth_jorma_secret', '')



# Base class providing authentication
class BaseHandler(tornado.web.RequestHandler):
    def log_request(self):
        ua = (self.request.headers['user-agent'] if 'user-agent' in self.request.headers else 'Unknown').replace('"','')
        logging.info('%s "%s"'%(str(self._request_summary()), ua))

    def on_finish(self):
        self.log_request()
    
    def get_current_user(self):
        magic = self.request.headers['X-Jorma'] if 'X-Jorma' in self.request.headers else ''
        if len(magic)==32 and magic == jorma_secret:
            logging.debug('Static apiuser authentication')
            return 'apiuser'
        
        try:
            raw = self.get_secure_cookie('session')
            if not raw:
                logging.debug("No session cookie set")
                return None
            c = raw.decode('utf-8')
            if c and sessions.check_session(c):
                return c
            else:
                logging.debug('check_session NOK for %s'%str(c))
                return None
        except:
            raise

    def get_current_username(self):
        return sessions.get_username(self.get_current_user())

    def is_user_admin(self):
        admins = ['admin', 'root']
        adminuser = os.environ.get('ADMIN_USERNAME', None)
        if adminuser:
            admins.append(adminuser)
        return self.get_current_username() in admins # todo find another way than hardcoding here
    
    def render_header(self):
        # path
        pathcomp = self.request.path.split('/')
        p = ''
        c = ''
        for x in [x for x in pathcomp if x != '']:
            c += '%s/'%x
            p += '/ <a  href="/%s">%s</a>\n'%(c, escape.url_unescape(x))
        pathcontent = '<p>[ <a href="/">home</a> %s ] ' % p

        self.write(div('', '%s You are logged in as %s. <a href="/logout/">Logout</a>\n</p><hr>\n'%(pathcontent, self.get_current_username())))
