#!/usr/bin/env python3

import tornado.web
from tornado import escape
from base import BaseHandler
from db import db
import form
import json
import templates
import textwrap as tw

def answer_distributions(formid, company):
    questions = form.allquestions(formid)
    e = db.latest_entries(formid, company)
    foo = {}
    def counts(x):
        y={}
        for a in ['yes','no','n/a','undef']:
            y[a] = x.count(a)
        return y
    if len(e)==0:
        return {}
    for key, item in questions.items():
        try:
            if key.startswith('apprisk'):
                continue
            x = {}
            x['counts'] = counts(list(map(lambda x:x['answers'][key], e)))
            for ans in ['yes', 'no', 'undef', 'n/a']:
                x[ans] = [{'domain':y['domain'], 'project':y['project'], 'company':y['company']} for y in e \
                            if key in y['answers'] and y['answers'][key] == ans]
            x['question'] = questions[key]['text']
            x['description'] = questions[key]['description']
            try:
                x['points'] = questions[key]['points']
                x['impact'] = questions[key]['impact']
                x['effort'] = questions[key]['effort']
                x['weight'] = x['impact'] * x['points']
            except:
                x['weight'] = 0
            foo[key] = x
        except:
            pass
    return foo

def sort_answer_distribution(dist):
    counts = set()
    for a in list(dist.values()):
        counts.add(a['counts']['yes'])
        counts.add(a['counts']['no'])
        counts.add(a['counts']['undef'])
    allentries = list(dist.values())
    r = []
    for n in list(reversed(sorted(list(counts)))):
        x = [x for x in allentries if x['counts']['undef'] == n]
        tmp = []
        for n in list(reversed(sorted(list(counts)))):
            y = [y for y in x if y['counts']['no'] == n]
            tmp.append(list(sorted(y, key=lambda x:x['question'])))
        r += tmp
    return [item for sortedlist in r for item in sortedlist]



class StatisticsHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, company, path, args):
        company = escape.url_unescape(company)
        asjson = True if self.get_query_argument('format', None) == 'json' else False
        dist = answer_distributions(path, company)
        if asjson:
            self.finish(dist)
            return
        a = sort_answer_distribution(dist)
        self.write(templates.start)
        self.render_header()
        self.write('<a href="?format=json">Raw data (json)</a><br>\n')
        self.write('<pre style="font-size: 9pt">\n')
        self.write('\n\nPlanning -- %s\n\n'%path)
        self.write('%s [weight]    n/a  no  yes\n'%'Question'.ljust(60))
        self.write('%s\n'%('='*85))
        for x in a:
            q = tw.wrap(x['question'], 60)
            if len(q) > 1:
                for line in q[:-1]:
                    self.write('%s\n'%line)
            self.write('%s     [%2d] %4d %4d %4d\n\n'%(q[-1].ljust(60),
                                                       x['weight'],
                                                       #x['points'], x['impact'],
                                                       x['counts']['undef'],
                                                       x['counts']['no'],
                                                       x['counts']['yes']))
        self.write('</pre>\n')
        self.write(templates.end)

class PlanningHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, company, path, args):
        company = escape.url_unescape(company)
        asjson = True if self.get_query_argument('format', None) == 'json' else False
        dist = answer_distributions(path, company)
        if asjson:
            self.finish(dist)
            return
        a = sorted(dist.values(), key=lambda x:x['weight'], reverse=True)
        self.write(templates.start)
        self.render_header()
        self.write('<a href="?format=json">Raw data (json)</a><br>\n')
        self.write('<pre style="font-size: 9pt">\n')
        self.write('\n\nPlanning -- %s\n\n'%path)
        self.write('%s [weight]    n/a  no  yes\n'%'Question'.ljust(60))
        self.write('%s\n'%('='*85))
        for x in a:
            q = tw.wrap(x['question'], 60)
            if len(q) > 1:
                for line in q[:-1]:
                    self.write('%s\n'%line)
            self.write('%s     [%2d] %4d %4d %4d\n\n'%(q[-1].ljust(60),
                                                       x['weight'],
                                                       #x['points'], x['impact'],
                                                       x['counts']['undef'],
                                                       x['counts']['no'],
                                                       x['counts']['yes']))
        self.write('</pre>\n')
        self.write(templates.end)
        
        

if __name__=='__main__':
    print(json.dumps({'x': sort_answer_distribution(answer_distributions('ssa'))}, indent=4,sort_keys=True))
