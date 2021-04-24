#!/usr/bin/env python3

from singleton import Singleton
import mysql.connector, json, os, time
from hashlib import sha256
import logging
import sys
import subprocess

def dump(x):
    return json.dumps(x, indent=2, sort_keys = True)

def reads(x):
    return json.loads(x)

def sha(x):
    return sha256(str(x).encode('ascii')).hexdigest()

#TODO hardcoded variables should be removed
def getconnection():
    host=os.environ.get('DBHOST', 'db')
    database=os.environ.get('MYSQL_DATABASE', 'ssa')
    user=os.environ.get('MYSQL_USER', 'ssa')
    password=os.environ.get('MYSQL_PASS','ssapass1!!!1one')
    return mysql.connector.connect(host=host,database=database,user=user,password=password)


@Singleton
class Db:
    def __init__(self):
        self.host = 'db'
        self.update_schema()
        self.last_cleanup = 0

    def update_schema(self):
        # Update schema by creating a procedure that ignores an error
        # as we are not accessing the information_schema database
        queries=["""
DROP PROCEDURE IF EXISTS `pieru`;""","""
CREATE PROCEDURE `pieru`()
BEGIN
  DECLARE CONTINUE HANDLER FOR SQLEXCEPTION BEGIN END;
  ALTER TABLE `entries` ADD COLUMN `yourcustomcolumn` TEXT DEFAULT '';
END"""]
        
        conn = getconnection()
        c = conn.cursor()
        for q in queries:
            try:
                logging.info(q)
                c.execute(q)
            except:
                logging.warning("failed query: %s"%q)
        conn.commit()
        conn.close()
        

            
    def _row2result(self, row, full=False):
        r = {}
        r['formid'] = row[0]
        r['id'] = row[1]
        r['submitter'] = row[2]
        r['project'] = row[3]
        r['domain'] = row[4]
        r['date'] = row[5]
        r['score'] = json.loads(row[6])
        try:
            r['entries'] = json.loads(row[7])
        except:
            pass
        if full: # wtf
            r['answers'] = json.loads(row[7])
        r['company'] = row[8]
        return r
    
    def list_all(self, formid, company):
        conn = getconnection()
        c = conn.cursor()
        rows = []
        c.execute('select formid, id, submitter, project, business_unit, date, score, company from entries where formid = %s and company = %s', (formid,company))
        for row in c.fetchall():
            rows.append(self._row2result(row))
        conn.close()
        return rows

    def list_domains(self, formid, company):
        conn = getconnection()
        c = conn.cursor()
        rows = []
        c.execute('select distinct business_unit, project from entries where formid = %s and company = %s order by project', (formid,company))
        for row in c.fetchall():
            rows.append(row[0])
        conn.close()
        return rows

    def list_projects(self, formid, company, domain=None):
        conn = getconnection()
        c = conn.cursor()
        rows = []
        if domain==None:
            c.execute('select distinct project, business_unit from entries where formid = %s and company = %s order by project', (formid,company))
        else:
            c.execute('select distinct project, business_unit from entries where business_unit=%s and formid = %s and company = %s order by project',
                      (domain, formid, company))
        for row in c.fetchall():
            rows.append((row[0], row[1]))
        conn.close()
        return rows

    def entries_by_project(self, formid, company, project):
        conn = getconnection()
        c = conn.cursor()
        rows = []
        logging.debug("project=%s"%str(project))
        if project != 'None':
            c.execute('select formid, id, submitter, project, business_unit, date, score, entries, company from entries where formid = %s and project = %s and company = %s order by date desc',
            (formid, project, company))
        else:
            c.execute('select formid, id, submitter, project, business_unit, date, score, entries, company from entries where formid = %s and project = null and company = %s order by date desc', (formid,company))
        for row in c.fetchall():
            rows.append(self._row2result(row))
        conn.close()
        return rows

    def latest_entries(self, formid, company):
        projects = db.list_projects(formid, company)
        entries = []
        conn = getconnection()
        c = conn.cursor()
        ids = []
        for p in projects:
            sql = 'select id from entries where project = %s and business_unit = %s and formid = %s and company = %s order by date desc limit 1'
            c.execute(sql, (p[0], p[1], formid, company))
            for row in c.fetchall():
                ids.append(row[0])
        conn.close()
        for i in ids:
            entries.append(self.get(i))
        return entries

    def add_entry(self, formid, submitter, project, business_unit, date, score, answers, submission_id, company):
        conn = getconnection()
        c = conn.cursor()
        if submission_id == None:
            logging.debug("Inserting")
            sql = 'insert into entries (formid, submitter, project, business_unit, date, score, entries, company) values (%s,%s,%s,%s,%s,%s,%s,%s)'
            c.execute(sql, (formid, submitter, project, business_unit, date, dump(score), dump(answers), company))
        else:
            logging.debug("Updating submission_id=%s"%str(submission_id))
            sql = 'update entries set submitter=%s, project=%s, business_unit=%s, date=%s, score=%s, entries=%s where id = %s'
            c.execute(sql, (submitter, project, business_unit, date, dump(score), dump(answers), submission_id))
        conn.commit()
        conn.close()

    def remove_entry(self, submission_id):
        conn = getconnection()
        c = conn.cursor()
        c.execute('delete from entries where id = %s', (submission_id, ))
        conn.commit()
        conn.close()
        
    def get(self, submission_id):
        conn = getconnection()
        c = conn.cursor()
        sql = 'select formid, id, submitter, project, business_unit, date, score, entries, company from entries where id = %s'
        r = None
        c.execute(sql, (submission_id, ))
        for row in c.fetchall():
            r = self._row2result(row, True)
        conn.close()
        return r

    # create table if not exists selectedcompanies (winaccountname nvarchar(256) primary key, selectedcompany text not null);
    def get_selected_company(self, winaccountname):
        sql = "select selectedcompany from usermeta where winaccountname = %s"
        conn = getconnection()
        c = conn.cursor()
        c.execute(sql, (winaccountname,))
        company = ""
        for row in c.fetchall():
            company = row[0]
        conn.close()
        return company

    def set_selected_company(self, key, company):
        sql = "update usermeta set selectedcompany = %s where winaccountname = %s"
        conn = getconnection()
        c = conn.cursor()
        c.execute(sql, (winaccountname,))
        conn.commit()
        conn.close()
        
    def list_companies(self):
        sql = "select company from companies"
        conn = getconnection()
        c = conn.cursor()
        c.execute(sql)
        companies = []
        for row in c.fetchall():
            companies.append(row[0])
        conn.close()
        return companies

    def add_company(self, company):
        sql = "insert into companies (company) values (%s)"
        conn = getconnection()
        c = conn.cursor()
        c.execute(sql, (company,))
        conn.commit()
        conn.close()
 
    def remove_company(self, company):
        sql = "delete from companies where company = %s"
        conn = getconnection()
        c = conn.cursor()
        c.execute(sql, (company,))
        conn.commit()
        conn.close()

    def companies_for_user(self, username):
        sql = "select company where username = %s"
        conn = getconnection()
        c = conn.cursor()
        c.execute(sql, (company,))
        companies = []
        for row in c.fetchall():
            companies.add(row[0])
        conn.close()
        return companies

db = Db.Instance()

if __name__=='__main__':
    d = Db.Instance()
    d.host = 'localhost'
    print(db.list_all('ssa'))
    print('')
    print(json.dumps(db.get(int(sys.argv[1])), sort_keys=True,indent=4))
