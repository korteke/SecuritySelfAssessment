#!/usr/bin/env python3

import tornado.ioloop
import tornado.web
from tornado.escape import json_decode
from form import FormHandler
from tornadoadfsoauth2.auth import AuthHandler
#from main import MainHandler
from tornadoadfsoauth2.session import sessions
import sys, os, json
from base import BaseHandler
from entries import EntriesHandler
from stats import StatisticsHandler, PlanningHandler
from admin import AdminHandler
import templates
from db import db
import logging
from collections import defaultdict

class CompaniesHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        companies = db.list_companies()
        asjson = True if self.get_query_argument('format', None) == 'json' else False
        if asjson:
            self.finish({'companies':companies})
            return
        
        self.write(templates.start)
        self.write('<p>Available companies</p>\n')
        for c in companies:
            self.write('<p><a href="/%s/">%s</a></p>\n'%(c,c))
        self.write(templates.end)

class FrontpageHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, company):
        jsons = list(filter(lambda x:x.endswith('.json'), os.listdir('forms')))
        allforms = defaultdict(list) # indexed by sortkey
        for j in jsons:
            meta = json.loads(open('forms/%s'%j).read())['meta']
            allforms[meta['sortkey']].append(meta)

        asjson = True if self.get_query_argument('format', None) == 'json' else False
        if asjson:
            self.finish({'forms':allforms})
            return

        self.write(templates.start)
        self.write('<h1>Available forms</h1>\n')
        for sortkey in sorted(list(allforms.keys())):
            forms = sorted(allforms[sortkey], key=lambda x:x['title'])
            if len(forms) == 0:
                continue
            self.write('<h2>%s</h2>\n'%forms[0]['category'])
            for f in forms:
                self.write('<p><a href="/%s/%s/">%s</a></p>\n'%(company, f['path'],f['title']))
        self.write(templates.end)


class MainHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, company, path):
        self.write(templates.start)
        self.render_header()
        self.write('<a href="/%s/%s/form/">New submission</a><br>\n' % (company, path))
        self.write('<a href="/%s/%s/entries/">Past entries</a><br>\n' % (company, path))
        self.write('<a href="/%s/%s/stats/">Statistics</a><br>\n' % (company, path))
        self.write(templates.end)

class LogoutHandler(BaseHandler):
    def get(self):
        sessions.remove_session(self.get_current_user())
        self.clear_all_cookies()
        self.redirect(os.environ.get('adfs_logout_uri', 'http://127.0.0.1/'))

def make_app():
    return tornado.web.Application([
        (r"/", CompaniesHandler),
        (r"/logout/", LogoutHandler),
        (r"/admin/", AdminHandler),
        (r"/auth/(.*)", AuthHandler),
        (r"/([^/]*)/", FrontpageHandler),
        (r"/([^/]*)/([^/]*)/", MainHandler),
        (r"/([^/]*)/([^/]*)/entries/(.*)", EntriesHandler),
        (r"/([^/]*)/([^/]*)/form/(.*)", FormHandler),
        (r"/([^/]*)/([^/]*)/stats/(.*)", StatisticsHandler),
        (r"/([^/]*)/([^/]*)/planning/(.*)", PlanningHandler),
        (r"/(.*)", tornado.web.StaticFileHandler, {"path": "static/",\
                                                   "default_filename": 'index.html'}),
    ], cookie_secret='339a5da7f364d10c7d64a40e90982e4756572cdb',
                                   login_url='/auth/')

def main():
    logging.basicConfig(format='%(asctime)s %(message)s')
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    port = 8888
    if len(sys.argv) >= 2:
        port = int(sys.argv[1])
    #if len(sys.argv) == 3:
        
    app = make_app()
    logging.info("Application starting up")
    app.listen(port, address='0.0.0.0')
#    tornado.log.enable_pretty_logging()
    tornado.ioloop.IOLoop.current().start()

if __name__ == "__main__":
    main()
