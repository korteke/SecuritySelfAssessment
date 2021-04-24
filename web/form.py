#!/usr/bin/env python3

import tornado.web
from tornado import escape
import templates
import formrender
import sys
import scoring
import json
import time
import os
from base import BaseHandler
from db import db
import logging
import re


def filter_input(text):
    return re.sub('[^a-zA-Z0-9/\s.,()!#]', '', text) if text else ''

def allquestions(path):
    formdefinition = json.loads(open(os.path.join('forms',path+'.json'), 'r').read())
    qs = {}
    lastcategory = ''
    lastsubcategory = ''
    for l in formdefinition['lines']:
        if not 'id' in l and 'text' in l:
            if l['type'] == 'subheader':
                lastsubcategory = l['text']
            elif l['type'] == 'header':
                lastcategory = l['text']
                lastsubcategory = ''
        if 'id' in l:
            qs[l['id']] = l
            delim = ' - ' if len(lastcategory)>0 and len(lastsubcategory)>0 else ''
            qs[l['id']]['category'] = "%s%s%s"%(lastcategory, delim, lastsubcategory)
    return qs

class FormHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, company, path, args):
        company = escape.url_unescape(company)
        formid = filter_input(self.get_query_argument('id', None))
        modify = filter_input(self.get_query_argument('modify', None))
        delete = filter_input(self.get_query_argument('delete', None))
        answers = {}
        project = ''
        domain = ''
        if formid:
            a = db.get(int(formid))
            answers = a['answers']
            project = a['project']
            domain = a['domain']
            if delete and self.is_user_admin():
                db.remove_entry(int(formid))
                self.redirect('/entries/')
                return
        self.write(templates.start)
        self.render_header()
        self.write(formrender.render_formdef(company, path, project, domain, answers, modify, formid))
        self.write(templates.end)
        
    @tornado.web.authenticated
    def post(self, company, path, args):
        company = escape.url_unescape(company)
        pointsdict = scoring.getscoring(path)
        sums = pointsdict['sums']
        del pointsdict['sums']
        risk = 0
        points = 0
        answercount = 0
        unanswered = 0
        answers = {}
        project = filter_input(self.get_body_argument('projectname', default=''))
        domain = filter_input(self.get_body_argument('domain', default=''))
        formid = filter_input(self.get_body_argument('formid', default=''))
        try:
            formid = int(formid)
        except:
            formid = None

        if project == '' or domain == '' or company == '':
            self.write("Project or domain or company is empty. Please go back and provide values for all and resubmit")
            return

        # check that company is valid
        if not company in db.list_companies():
            self.write("Company %s is not known"%company)
            return
        
        d = open('debug.txt','w')
        for key, item in pointsdict.items():
            val = filter_input(self.get_body_argument(key, default='undef'))
            notekey = 'note_%s'%key
            note = self.get_body_argument(notekey, default='')
            if len(note) > 0:
                logging.debug('note_%s : %s'%(key, note))
                answers[notekey] = note
            answers[key] = val
            if val.isnumeric():
                if 'apprisk' in key:
                    risk += pointsdict[key][int(val)]
                answercount += 1
                d.write("adding %s -> %s points\n"%(key,pointsdict[key][int(val)]))
                continue
            if val == 'undef' and not key.startswith('apprisk_'):
                unanswered += 1
            if key.startswith('apprisk_') and val == 'yes':
                risk += pointsdict[key]
            elif not key.startswith('apprisk'):
                if val == 'yes':
                    points += pointsdict[key]
                    answercount += 1
                elif val == 'no':
                    answercount += 1
                elif val == 'n/a':
                    answercount += 1
            d.write("%s : %s : %s\n"%(key, str(pointsdict[key]), str(val)))
        r = {}
        r['max_risk'] = sums['max_risk'] if 'max_risk' in sums else 0
        r['max_points'] = sums['max_points']
        r['risk'] = risk
        r['score'] = points
        r['answer_count'] = answercount
        r['unanswered'] = unanswered
        try: 
            r['risk_level'] = "%d %%"%(int(100.0 * risk / sums['max_risk']))
        except: # not every form has risk at all
            pass
        r['score'] = "%d %%"%(int(100.0 * points / sums['max_points']))
        entry = {}
        entry['answers'] = answers
        entry['score'] = r
        entry['submitter'] = self.get_current_username()
        entry['formid'] = path
        open('answer.json','w').write(json.dumps(entry, sort_keys=True, indent=4))
        db.add_entry(path, self.get_current_username(), project, domain, str(time.time()), r, answers, formid, company)
        if project:
            self.redirect('/%s/%s/entries/?project=%s'%(company, path,project))
        else:
            self.redirect('/%s/%s/'%(company, path))

        
