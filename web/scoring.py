#!/usr/bin/env python3

import json, sys

def getscoring(formname):
    fields = json.loads(open('forms/%s.json'%formname).read())['lines']
    scoring = {}
    maxpoints = 0
    maxrisk = 0
    for l in fields:
        t = l['type']
        if t in ['radio', 'yesno']:
            scoring[l['id']] = l['points']
            s = sum(l['points']) if type(l['points']) == list else l['points']
            if l['id'].startswith('apprisk'):
                maxrisk += s
            else:
                maxpoints += s
        elif t == 'multiple':
            for i in range(len(l['points'])):
                scoring['%s_%i'%(l['id'], i)] = l['points'][i]
                if l['id'].startswith('apprisk'):
                    maxrisk += l['points'][i]
                else:
                    maxpoints += l['points'][i]
    sums = {}
    sums['max_points'] = maxpoints
    sums['max_risk'] = maxrisk
    scoring['sums'] = sums
    return scoring

if __name__=='__main__':
    print(json.dumps(getscoring(sys.argv[1]), indent=True, sort_keys = True))
