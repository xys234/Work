"""

List all files


"""

import os
import csv
import datetime

# search_directory = r'I:\NVTA\Needs_Assess_Model\2016_Base_MID_Cap_v3'
# search_directory = r'L:\DCS\Projects\_Legacy\60563434_SWIFT\400_Technical'
search_directory = r'I:'
search_extensions = ('zip', '7z')
search_results = r'C:\Projects\compressed_archives_vdot.csv'

matches = []

for root, dirnames, filenames in os.walk(search_directory):
    for filename in filenames:
        if '.' in filename:
            extension = filename.lower().split('.')[1]
            if extension in search_extensions:
                fullpath = os.path.join(root, filename)
                modified_time = os.path.getmtime(fullpath)
                modified_time = datetime.datetime.fromtimestamp(modified_time).strftime('%Y-%m-%d  %H:%M:%S')
                matches.append((fullpath, modified_time))


with open(search_results, mode='w', newline='') as f:
    writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
    writer.writerow(("File", "Last_Modified"))
    for match in matches:
        writer.writerow(match)




