# 10.16 adding # of files transferred according to transfer.log
# 11.20 adding a way to get each filename that didn't get copied.

import os
import os.path
import csv
import re
import datetime

# uses os and os path module to search the directory for files w/ a particular name, cd-info.log, then joins that filename w/ its path and puts that into a list

path_cd_info = []
for dirpath, dirnames, filenames in os.walk("."):
    for filename in [f for f in filenames if f.endswith("cd-info.log")]:
        path_and_file = os.path.join(dirpath, filename)
        path_cd_info.append(path_and_file)


dict = {}

# re patterns to find necessary info

mediaID_pattern = re.compile('(?=M[0-9]{5}\_[0-9]{4}\/)(M[0-9]{5}\_[0-9]{4})')
raw_pattern = re.compile('(?<=leadout\s\()[0-9]*')
formatted_pattern = re.compile('(?<=raw,\s)[0-9]*')

# this part first finds the mediaID from the path, then opens each cd-info file, looks for the raw and formatted data amounts, then puts the mediaID, raw value, and formatted value in a dictionary, using the mediaID as a key. the mediaID is a key and a value here as a workaround to not being able to output the key into a csv.

for each_item in path_cd_info:
    mediaID_find = mediaID_pattern.findall(each_item)
    if mediaID_find:
        mediaID_str = mediaID_find[0] # the 0 is necessary because findall will make a list out of subsequent matches, and we just want the 1st item
        dict[mediaID_str] = {
        "mediaID": mediaID_str
        }

        with open (each_item,'r') as log:
            for each_line in log:
                raw_find = raw_pattern.findall(each_line)
                raw_str = "".join(raw_find)
                formatted_find = formatted_pattern.findall(each_line)
                formatted_str = "".join(formatted_find)
                if raw_find:
                    if mediaID_str in dict.keys():
                        dict[mediaID_str]["raw str"] = raw_str
                        dict[mediaID_str]["formatted str"] = formatted_str

# this repeats the process done to find the cd-info.log paths, but for the bag-info.txt file.
path_bag = []
for dirpath, dirnames, filenames in os.walk("."):
    for filename in [f for f in filenames if f.endswith("bag-info.txt")]:
        path_and_file = os.path.join(dirpath, filename)
        path_bag.append(path_and_file)

# looks for the oxum, splits it into 2 parts (the bytecount and filecount; this could have been 2 sep things the regex is looking for, i realize, but this is ok too), and adds each of those to the existing mediaID key in the dictionary

oxum_pattern = re.compile('(?<=Oxum\:\s)[0-9]*\.[0-9]*')

for each_item in path_bag:
    mediaID_find = mediaID_pattern.findall(each_item)
    if mediaID_find:
        mediaID_str = mediaID_find[0] # < do this instead of join
        with open (each_item,'r') as log:
            for each_line in log:
                oxum_find = oxum_pattern.findall(each_line)
                oxum_str = "".join(oxum_find) #this could probably be moved to after the if statement?
                oxum_split = oxum_str.split(".")
                if oxum_find:
                    if mediaID_str in dict.keys():
                        dict[mediaID_str]["bytecount"] = oxum_split[0]
                        dict[mediaID_str]["filecount"] = oxum_split[1]
                    else:
                        dict[mediaID_str] = {
                        "mediaID": mediaID_str,
                        "bytecount": oxum_split[0],
                        "filecount": oxum_split[1]
                        }
# this section copies what the oxum step does, except finding the start and end times from the transfer.log file

path_xfer = []
for dirpath, dirnames, filenames in os.walk("."):
    for filename in [f for f in filenames if f.endswith("transfer.log")]:
        path_and_file = os.path.join(dirpath, filename)
        path_xfer.append(path_and_file)

start_time_pattern = re.compile("(?=\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2},\d{3} - root - INFO - ###)(\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2})")
end_time_pattern = re.compile("(?=\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2},\d{3} - root - INFO - unload command output)(\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2})")

# adding a part to help find any that have warnings. first, a known warning
not_copied_pattern = re.compile("(?<=could not be copied:\s)\[.*\]")
not_copied_each_pattern = re.compile("\.\\\\")


# 2nd, are there other warnings?
# turns out the answer is no! do not actually need this
warning_pattern = re.compile("WARNING")

# 10.16 addition—how many files xferred?
file_xfer_pattern = re.compile("(Generating manifest lines for file)")

# 11.20 addition—looking to help id what types of files didn't get xferred
not_copied_end_pattern = re.compile("(?=.{4}',).{4}")

for each_item in path_xfer:
    mediaID_find = mediaID_pattern.findall(each_item)
    if mediaID_find:
        mediaID_str = mediaID_find[0]

        with open (each_item,'r') as log:

            file_xfer_total = 0

            for each_line in log:
                start_time_find = start_time_pattern.findall(each_line)
                if start_time_find:
                    if mediaID_str in dict.keys():
                        start_time_str = "".join(start_time_find)
                        dict[mediaID_str]["start time"] = start_time_str


                end_time_find = end_time_pattern.findall(each_line)
                if end_time_find:
                    if mediaID_str in dict.keys():
                        end_time_str = "".join(end_time_find)
                        dict[mediaID_str]["end time"] = end_time_str

                # and adding the part to find the warnings here
                not_copied_find = not_copied_each_pattern.findall(each_line)
                if not_copied_find:
                    if mediaID_str in dict.keys():
                        not_copied_count = len(not_copied_find)
                        dict[mediaID_str]["not copied"] = not_copied_count
                # 11.20 addition for identifying files that didn't get xferred
                not_copied_type = not_copied_end_pattern.findall(each_line)
                if not_copied_type:
                    if mediaID_str in dict.keys():
                        dict[mediaID_str]["not copied type"] =  not_copied_type

                # getting the files xferred
                if file_xfer_pattern.findall(each_line):
                    file_xfer_total += 1
                    if mediaID_str in dict.keys():
                       dict[mediaID_str]["files xferred"] = file_xfer_total




            if "start time" in dict[mediaID_str].keys() and "end time" in dict[mediaID_str].keys():
                start = datetime.datetime.fromisoformat(dict[mediaID_str]["start time"])
                end = datetime.datetime.fromisoformat(dict[mediaID_str]["end time"])
                delta = end - start
                time_elapsed = datetime.timedelta.total_seconds(delta)
                dict[mediaID_str]["time elapsed"] =  time_elapsed



# this section puts every dumb thing in a csv

with open('specialcsv.csv','w') as csv_out:
    csv_writer = csv.DictWriter(csv_out,fieldnames=["mediaID","raw str","formatted str","bytecount","filecount","start time","end time","time elapsed","not copied","not copied type","any warning","files xferred"])
    csv_writer.writeheader() #to write out all of those field names just given
    for key,value in dict.items():
        csv_writer.writerow(value)
