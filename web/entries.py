#!/usr/bin/env python

import tornado.ioloop
import tornado.web
from tornado.escape import json_decode, url_unescape
from form import FormHandler, allquestions
from tornadoadfsoauth2.auth import AuthHandler
from tornadoadfsoauth2.session import sessions
import sys, json
from base import BaseHandler
import templates
from db import db
import aux
import logging

class EntriesHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, company, path, args):
        company = url_unescape(company)
        project = self.get_query_argument('project', None)
        asjson = True if self.get_query_argument('format', None) == 'json' else False
        modify = True if self.get_query_argument('modify', None) == 'true' else False
        domain = self.get_query_argument('domain', None)
        if self.is_user_admin():
            modify = True
        # no args - list projects
        if not project and not asjson:
            self.write(templates.start)
            self.render_header()
            if not domain:
                self.write("<h3>Business units</h3>\n")
                self.write('<p>')
                for x in db.list_domains(path, company):
                    self.write('<a href="/%s/%s/entries/?domain=%s">%s</a>\n'%(company,path,x,x))
                self.write('</p>\n')
                self.write("<h3>Projects</h3>\n")
            else:
                self.write("<h3>Projects for %s</h3>\n"%domain)
            for x in db.list_projects(path, company, domain):
                self.write('<p><a href="?project=%s">%s (%s)</a></p>\n'%(x[0],x[0], x[1]))
            self.write('<hr><p><a href="?format=json">Raw data</a>\n')
            statspath = '/%s/'%company + path.split('/')[0] + '/stats/'
            self.write('-- <a href="%s">Statistics</a>\n' % (statspath))
            planningpath = '/' + path.split('/')[0] + '/planning/'
            self.write('-- <a href="%s">Planning</a></p>\n' % (planningpath))
            self.write(templates.end)
        elif asjson:
            if project:   # all scores for a project
                self.write({'scores':db.entries_by_project(path, company, project),
                            'questions': allquestions(path)})
            else:  # latest scores for each project
                d = []
                for p in db.list_projects(path, company):
                    d.append(db.entries_by_project(path, company, p[0]))  # db orders by date desc
                self.write({'latest_scores':d, 'questions': allquestions(path)})
        else:
            r = ''
            self.write(templates.start)
            self.render_header()
            r = ''
            r += '<h3>Entries for project %s</h3>\n'%project
            r += '<table class="table"><tr>\n'
            columns = ['Date','Answered', 'Risk level', 'Score', 'Submitted by']
            if modify:
                columns = ['Date','Answered','Risk level','Score', 'Submitted by' ,'', '']
            # kludge to only show risk level for ssa
            if not path in ['ssa', 'satsi'] and 'Risk level' in columns:
                columns.remove('Risk level')
            for x in columns:
                r += '<td>%s</td>\n'%x
            r += '</tr>\n'
            for e in db.entries_by_project(path, company, project):
                r += '<tr>\n'
                r += '<td><a href="/%s/%s/form/?id=%d">%s</a>\n'%(company, path, e['id'], aux.unixtime2date(e['date']))
                r += '<td>%d / %d</td>\n'%(e['score']['answer_count'], e['score']['answer_count'] + e['score']['unanswered'])
                if 'Risk level' in columns:
                    try:
                        r += '<td>%s</td>\n'%(e['score']['risk_level'])
                    except:
                        r += '<td>n/a</td>\n'
                        logging.debug(str(e['score']))
                        logging.debug(json.dumps(e['score'], indent=4))
                r += '<td>%s</td>\n'%(e['score']['score'])
                r += '<td>%s</td>\n'%(e['submitter'])
                if modify:
                    r += '<td><a href="/%s/%s/form/?id=%d&modify=true">Modify</a>\n'%(company, path, e['id'])
                    r += '<td><a href="/%s/%s/form/?id=%d&delete=true">Delete</a>\n'%(company, path, e['id'])
                r += '</tr>\n'
            r += '</table>\n'
            r += '<p><a href="?project=%s&format=json">Raw data</a></p>\n'%(project)
            self.write(r)
            self.write(templates.end)
                
