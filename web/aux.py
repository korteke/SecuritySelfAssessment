#!/usr/bin/env python3

import sys
from datetime import datetime

def unixtime2date(ts):
    return datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

if __name__=='__main__':
    print(unixtime2date(int(sys.argv[1])))
