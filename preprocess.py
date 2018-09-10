# -*- coding: utf-8 -*-
'''
This script takes the input NewsScape file and extracts the relevant text from it.
'''
from datetime import datetime
import argparse
import re
import sys

parser = argparse.ArgumentParser()
parser.add_argument("FILE", type=str, default=sys.stdin, help="Name of input file")
# parser.add_argument("-inf", "--input_file", type=str, required=True, help="Name of\
#                     input file")
parser.add_argument("-t", "--timing", default=0, type=int, help="Option to decide whether\
                    to include timing info in output")
args = parser.parse_args()

with open(args.FILE) as f:
	content = f.readlines()
content = [x.strip() for x in content]

date_format = "%Y%m%d%H%M%S.%f"
fields = set(["TOP", "COL", "UID", "PID", "ACQ", "DUR", "VID", "TTL", "URL", "TTS", "SRC", "CMT", "LAN", "TTP", "HED", "OBT", "LBT", "END", "CC1"])
text = ''
for line in content:
	l = line.split('|')
	if l[0]=="TOP":
		start = datetime.strptime(l[1]+'.0', date_format)
		y = '|'.join(l)
		text+= str(y + "\n")
	elif l[0] in fields:
		f = '|'.join(l)
		text+= str(f + "\n")
	elif l[0]=="END":
		break
	elif l[0] not in fields:
		t = datetime.strptime(l[0], date_format)
		s = l[-1]
		#print s
		if args.timing:
			text+=' '.join(['S_'+str(int((t-start).total_seconds())),s,''])
		else:
			text+=' '.join([s,''])


end = re.search(r'(END\|.*)', text)
text = re.sub(r'(END\|.*)', '', text)
text+=end.group(1)

print(text)
