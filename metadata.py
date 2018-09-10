import fileinput
import re
import argparse
import os
import os.path
import sys
from datetime import datetime, date, time, timedelta

def command_line_arguments():
    """Create argparse object"""
    parser = argparse.ArgumentParser(description="Create a XML file from a NewsScape file input")
    parser.add_argument("-a", type=os.path.abspath, required=False, help="Directory to destination folder to process multiple files")
    parser.add_argument("FILE", type=argparse.FileType("r"), help="Newsscape capture text file")
    args = parser.parse_args()
    return args

def sentenceboundary(x):
    if x == "":
        pass
    result = re.search(r'(.*)', x)
    return('<sentenceboundary />' + result.group(1))

def commercial(x):
    result = re.sub(r'Type=Commercial', '</story><commercial>', x)
    if result != None:
        return(result)
    else:
        return(x)

def story(x):
    result = re.sub(r'Type=Story start','</commercial><story>', x)
    if result != None:
        return(result)
    else:
        return(x)

def speakerid(x):
    pattern = re.match(r'(.*>)(.*?):(.*)', x)
    if pattern != None:
        return(pattern.group(1) + '<meta type="speakeridentification" originalvalue="' + pattern.group(2) + '" />' + pattern.group(3))
    else:
        return(x)

def timeident(x):
    timeid = re.match(r'(.*)([sS]\_[0-9]+)(.*)', x)
    # timeid = re.sub(r'([sS]\_[0-9]+)', '<ccline start="' + timeid.group(1) + '" />', x)
    if timeid != None:
        return(timeid.group(1) + '<ccline start="' + timeid.group(2) + '" />' + timeid.group(3))
        # return(timeid)
    else:
        return(x)

def speakerchange(x):
    pattern = re.sub(r'&gt;&gt;', '<speakerchange value="&gt;&gt;" />', x)
    if pattern != None:
        return(pattern)
    else:
        return(x)

def brackets(x):
    pattern = re.match(r'(.*)[\[\(](.*)?[\]\[\)\(](.*)', x)
    if pattern != None:
        return(pattern.group(1) + '<meta type="bracketedinfo" originalvalue="' + pattern.group(2) + '" />' + pattern.group(3))
    else:
        return(x)

def musicnotes(x):
    pattern = re.sub(r'♪', '<musicnotes value="♪" />', x)
    if pattern != None:
        return(pattern)
    else:
        return(x)

def savefile(path, filename, xml):
    filename1 = os.path.join(path, filename[:-3])
    f = open(filename1 + 'xml', 'a+')
    f.write(xml + "\n")
    f.close()

def xmlescape(x):
    x = re.sub(r'&', '&amp;', x);
    x = re.sub(r'"', '&quot;', x);
    x = re.sub(r'\'', '&apos;', x);
    x = re.sub(r'>', '&gt;', x);
    x = re.sub(r'<', '&lt;', x);
    return x

# def parse_capture_file(file_object, abbreviations):


def parse_capture_file(file_object):
    """Parse the capture file, i.e. identify meta data, time stamps,
    etc."""
    timestamp_re = re.compile(r"^\d{14}\.\d{3}$")
	# changed one_field_metadata and two_field_metadata since that is not a sensible distinction (there may be one or two field in VID, for instance)
    file_level_metadata = set(["TOP", "COL", "UID", "PID", "ACQ", "DUR", "VID", "TTL", "URL", "TTS", "SRC", "CMT", "LAN", "TTP", "HED", "OBT", "LBT", "END"])
    text = []
    timestamps = []
    sentences = []
    # Pre-Initialization
    video_resolution = "N/A"
    collection = "Communication Studies Archive, UCLA"
    original_broadcast_date = "N/A"
    original_broadcast_time = "N/A"
    original_broadcast_timezone = "N/A"
    local_broadcast_date = "N/A"
    local_broadcast_time = "N/A"
    local_broadcast_timezone = "N/A"
    for line in file_object:
        line = line.strip()
        fields = line.split("|")
        if timestamp_re.search(fields[0]):
            if fields[2] == "SEG":
                # sentences.extend(split_into_sentences(text, timestamps, abbreviations))
                text = []
                timestamps = []
            elif fields[2] == "CC1" or fields[2] == "CCO" or fields[2] == "TR0" or fields[2] == "TR1":# Verify this is doing the right thing...
                text.extend(fields[3:])
                timestamps.append(fields[0:2])
        elif fields[0] in file_level_metadata:
            if fields[0] == "TOP":
                timestamp = fields[1]
                topfields = fields[2].split("_")
                thedate = topfields.pop(0)
                datefields = thedate.split("-")
                thetime = topfields.pop(0)
                d = date(int(datefields[0]), int(datefields[1]), int(datefields[2]))
                t = time(int(fields[1][8:10]), int(fields[1][10:12]), int(fields[1][12:14]))
                filestartdatetime = datetime.combine(d,t)
                country = topfields.pop(0)
                channel = topfields.pop(0)
                channel = re.sub(r"[^A-Za-z0-9]", "_", channel)
                channel = re.sub(r"^([0-9])", r"_\1", channel)
                title = xmlescape(" ".join(topfields))
            if fields[0] == "COL":
                collection = xmlescape(fields[1])
            if fields[0] == "UID":
                uid = fields[1].replace("-", "_")
            if fields[0] == "PID":
                program_id = xmlescape(fields[1])
            if fields[0] == "ACQ":
                pass # NO SUCH THING??? -> Would like to know the format. acquisition_time = fields[1]; But what if it is date and time?
            if fields[0] == "DUR":
                duration = xmlescape(fields[1])
            if fields[0] == "VID":
                video_resolution = xmlescape(fields[1])
                try:
                    video_resolution_original = xmlescape(fields[2])
                except IndexError:
                    pass
            if fields[0] == "TTL":
                event_title = xmlescape(fields[1])
            if fields[0] == "URL":
                url = xmlescape(fields[1])
            if fields[0] == "TTS":
                transcript_type = xmlescape(fields[1])
            if fields[0] == "SRC":
                recording_location = xmlescape(fields[1])
            if fields[0] == "CMT":
                if fields[1] != "":
                    scheduler_comment = xmlescape(fields[1])
            if fields[0] == "LAN":
                language = xmlescape(fields[1])
            if fields[0] == "TTP":
                teletext_page = xmlescape(fields[1])
            if fields[0] == "HED":
                theheader = xmlescape(fields[1])
            if fields[0] == "OBT":
                try:
                    original_broadcast_date, original_broadcast_time, original_broadcast_timezone = fields[2].split(" ")
                except ValueError:
                    pass
                except IndexError:
                    try:
                        original_broadcast_date, original_broadcast_time, original_broadcast_timezone = fields[1].split(" ")
                    except ValueError:
                        pass
                else:
                    original_broadcast_estimated = "true"
            if fields[0] == "LBT":
                try:
                    local_broadcast_date, local_broadcast_time, local_broadcast_timezone = fields[1].split(" ")
                except ValueError:
                    pass
            if fields[0] == "END":
                text = []
    sys.stdout.write("<text id=\"t__%s\" collection=\"%s\" file=\"%s\" date=\"%s\" year=\"%s\" month=\"%s\" day=\"%s\" time=\"%s\" duration=\"%s\" country=\"%s\" channel=\"%s\" title=\"%s\" video_resolution=\"%s\"" % (uid, collection, file_object.name, thedate, datefields[0], datefields[1], datefields[2], thetime, duration, country, channel, title, video_resolution))
    try:
        video_resolution_original
    except NameError:
        pass
    else:
        sys.stdout.write(" video_resolution_original=\"%s\"" % (video_resolution_original))

    try:
        scheduler_comment
    except NameError:
        pass
    else:
        sys.stdout.write(" scheduler_comment=\"%s\"" % (scheduler_comment))

    try:
        language
    except NameError:
        pass
    else:
        sys.stdout.write(" language=\"%s\"" % (language))

    try:
        url
    except NameError:
        pass
    else:
        sys.stdout.write(" url=\"%s\"" % (url))

    try:
        recording_location
    except NameError:
        pass
    else:
        sys.stdout.write(" recording_location=\"%s\"" % (recording_location))

    try:
        program_id
    except NameError:
        pass
    else:
        sys.stdout.write(" program_id=\"%s\"" % (program_id))

    try:
        transcript_type
    except NameError:
        pass
    else:
        sys.stdout.write(" transcript_type=\"%s\"" % (transcript_type))

    try:
        teletext_page
    except NameError:
        pass
    else:
        sys.stdout.write(" teletext_page=\"%s\"" % (teletext_page))

    try:
        theheader
    except NameError:
        pass
    else:
        sys.stdout.write(" header=\"%s\"" % (theheader))

    try:
        original_broadcast_date
    except NameError:
        pass
    else:
        sys.stdout.write(" original_broadcast_date=\"%s\" original_broadcast_time=\"%s\" original_broadcast_timezone=\"%s\"" % (original_broadcast_date, original_broadcast_time, original_broadcast_timezone))

    try:
        original_broadcast_estimated
    except NameError:
        pass
    else:
        sys.stdout.write(" original_broadcast_estimated=\"%s\"" % (original_broadcast_estimated))

    try:
        local_broadcast_date
    except NameError:
        pass
    else:
        sys.stdout.write(" local_broadcast_date=\"%s\" local_broadcast_time=\"%s\" local_broadcast_timezone=\"%s\"" % (local_broadcast_date, local_broadcast_time, local_broadcast_timezone))

    print("><story>" + "\n")

def main():
	"""Main function"""
	args = command_line_arguments()
	sys.stderr.write("Processing " + args.FILE.name + "\n")
	print('<?xml version="1.0" encoding="UTF-8"?>')
	parse_capture_file(args.FILE)



# if __name__ == "__main__":
    # main()

args = command_line_arguments()
file_metadata = set(["TOP", "COL", "UID", "PID", "ACQ", "DUR", "VID", "TTL", "URL", "TTS", "SRC", "CMT", "LAN", "TTP", "HED", "OBT", "LBT", "END"])
for line in args.FILE:
	if line[0:3] not in file_metadata:
		escape = xmlescape(line)
		change = speakerchange(escape)
		boundary = sentenceboundary(change)
		timeinfo = timeident(boundary)
		notes = musicnotes(timeinfo)
		cont = story(notes)
		bracket = brackets(cont)
		ads = commercial(bracket)
		speaker = speakerid(ads)
		if args.a != None:
			savefile(args.a, args.FILE.name, ads)
		else:
			print(speaker)

print("</story></text>")
