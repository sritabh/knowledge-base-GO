import os
import json

c_dir = os.getcwd()
print(c_dir)
files_1_dir = c_dir + "/Text-Extraction/json_phase3-final"
files_2_dir = c_dir +"/Text-Extraction/input"

files_list_1 = os.listdir(files_1_dir)
files_list_2 = os.listdir(files_2_dir)
for file in files_list_1:
    file_name = file.split(".")[0]
    with open(files_1_dir+"/"+file, "r") as f:
        d = dict(json.loads(f.read()))
        new_file_name = d["Order ID"]
        for f in files_list_2:
            f_name = f.split(".")[0]
            if(f_name==file_name):
                os.rename((files_2_dir+"/"+f),(files_2_dir+"/"+new_file_name+".pdf"))
                print("Renamed: "+f)
                break
    os.rename((files_1_dir+"/"+file),(files_1_dir+"/"+new_file_name+".json"))
    print("Renamed: "+file)
