#!/usr/bin/env python3

import sys, json, templates
import logging

def header(text):
    return "<h2 class=\"mt-4\" >%s</h2>\n"%text

def subheader(text):
    return "<h3 class=\"mt-2\">%s</h3>\n"%text

def paragraph(text):
    return "<p class=\"mt-2\">%s</p>\n"%text

def cell(text, colspan=1):
    if colspan==1:
        return "<td>%s</td>\n"%text
    else:
        return "<td colspan=\"%d\">%s</td>\n"%(text, colspan)
def tag(text, t):
    return '<%s>%s</%s>'%(t, text, t)

def tableheader(columns):
    return '<tr>%s</tr>\n'%(''.join(list(map(lambda x:cell(tag(x, 'b')), columns))))

def render_formdef(company, formname, project='', domain='', answers={}, modify=False, formid=None):
    formdefinition = json.loads(open('forms/%s.json'%formname,'r').read())
    lines = formdefinition['lines']
    intable = False
    r = ""
    lineindex = 0

    def checked(field):
        logging.debug("field: %s"%str(field))
        if field in answers.keys() and answers[field] == 'yes':
            return 'checked'
        else:
            return ''

    def selected(field, val):
        if field in answers.keys() and str(answers[field]) == str(val):
            return 'checked'
        else:
            return ''

    r += '<h1>%s</h1><br>\n'%formdefinition['meta']['title']

    r += '<h3>Instructions</h3>\n'
    r += '<p>Fill the form below. It\'s ok to not fill every field: you can always come back and re-fill the form by selecting the most recent entry. Yes/no questions left unanswered count as no.</p>\n'
    
    r += "<form action=\"/%s/%s/form/1\" method=\"post\">\n"%(company, formname)

    if modify and formid:
        r += '<input type=hidden id="formid" name="formid" value="%s"/>'%(str(formid))

    # project name
    r += '<p>Project/service: <input type="text" class="bg-white focus:outline-none focus:shadow-outline border border-gray-300 rounded-lg ml-2 py-1 px-2 appearance-none leading-normal" name="projectname" id="projectname" value="%s"></p>\n'%project
    # business unit
    r += '<p>Business unit: <input type="text" class="bg-white focus:outline-none focus:shadow-outline border border-gray-300 rounded-lg ml-2 py-1 px-2 appearance-none leading-normal" name="domain" id="domain" value="%s"></p><br><br>\n'%domain

    for line in lines:
        #if len(fields) <= 1:
        #    continue
        if line['type'] == 'header':
            if intable:
                r += "</table>\n\n"
                intable = False
            r += header(line['text'])
            continue
        if line['type'] == 'subheader':
            if intable:
                r += "</table>\n"
                intable = False
            r += subheader(line['text'])
            continue
        if line['type'] == 'paragraph':
            if intable:
                r += "</table>\n"
                intable = False
            r += paragraph(line['text'])
            continue
        if not intable:
            #r += "<table class=\"table pb-4\"><col width=\"400px\"><col width=\"150px\"><col width=\"50px\"><col width=\"500px\">\n"
            r += "<table class=\"table pb-4\"><col width=\"400px\"><col width=\"150px\"><col width=\"400px\"><col width=\"200px\">\n"
            r += tableheader(['Item','Value', 'Description', 'Notes'])
            intable = True
        if line['type'] == 'subsubheader':
            r += '<tr><td colspan="3"><b>%s</b></td></tr>\n'%line['text']
        def maybedescription(line):
            if 'description' in line:
                return "<td valign=\"top\">%s</td>\n"%line['description']
            else:
                return cell('')
        def maybenote(line):
            if 'points' in line and 'type' in line and line['type'] != 'multiple':
                notekey = 'note_%s' % line['id']
                note = str(answers[notekey] if notekey in answers else "")
                return '<td><textarea type="text" class="bg-white focus:outline-none focus:shadow-outline border border-gray-300 rounded-lg ml-2 py-1 px-2 appearance-none leading-normal" name="%s" value="">%s</textarea></td>' % (notekey, note)
            else:
                return '<td></td>'
        def points(line):
            if 'points' in line and type(line['points']) and 'impact' in line and type(line['impact']) == int:
                return cell(str(line['points'] * line['impact']))
            else:
                return cell('')
        def pointsanddescription(line):
            return maybedescription(line) + maybenote(line)
            #return points(line) + maybedescription(line)
            
        if line['type'] == 'multiple':
            r += "<tr>\n  <td valign=\"top\">%s</td>\n"%line['text']
            r += "  <td>\n"
            i = 0
            for label in line['values']:
                id = "%s_%d"%(line['id'], i)
                i += 1
                r += '    <input type="checkbox" id="%s" name="%s" value="yes" %s>\n<label for="%s">%s</label><br>\n'%(id,id,checked(id), id,label)
            r += "</td>\n"
            r += pointsanddescription(line)
            r += "</tr>\n"
        elif line['type'] == 'radio':
            r += "<tr>\n  <td valign=\"top\">%s</td>\n"%line['text']
            r += "  <td>\n"
            i = 0
            for label in line['values']:
                id = "%s_%d"%(line['id'], i)
                name = line['id']
                r += '    <input type="radio" id="%s" name="%s" value="%d" %s>\n<label for="%s">%s</label><br>\n'%(name,name,i,selected(name, i),id,label)
                i += 1
            r += "</td>\n"
            r += pointsanddescription(line)
            r += "</tr>\n"
        elif line['type'] == 'yesno':
            r += "<tr>\n  <td valign=\"top\">%s</td>\n"%line['text']
            r += "  <td valign=\"top\">\n"
            for label in ['yes', 'no', 'n/a']:
                id = "%s"%(line['id'])
                r += '    <input type="radio" id="%s" name="%s" value="%s" %s>\n<label>%s</label><br>\n'%(id,id,label, selected(id,label),label)
            r += "</td>\n"
            r += pointsanddescription(line)
            r += "</tr>\n"
        elif line['type'] == 'number':
            r += "<tr>\n  <td valign=\"top\">%s</td>\n"%line['text']
            r += "  <td>\n"
            r += "    <input type=\"text\" id=\"%s\">"%line['id']
            r += "  </td>\n"
            r += pointsanddescription(line)
            r += "</tr>\n"
        elif line['type'] == 'text':
            r += "<tr>\n  <td valign=\"top\">%s</td>\n"%line['text']
            r += "  <td>\n"
            r += "    <input type=\"text\" id=\"%s\">"%line['id']
            r += "  </td>\n"
            r += pointsanddescription(line)
            r += "</tr>\n"
            
            
        lineindex += 1
    if intable:
        r += "</table>\n"
    r += "<br><input type=\"submit\" class=\"bg-gray border p-2\"></input>\n"
    r += "</form>\n"
    return r

if __name__=='__main__':
    print(render_formdef(sys.argv[1]))
        
    
