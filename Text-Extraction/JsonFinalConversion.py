import json
import os
import re

count=0
c_dir = os.getcwd()
print(c_dir)
input_files_dir = c_dir + "/Text-Extraction/json_phase2"
output_files_dir = c_dir +"/Text-Extraction/json_phase3-final"

input_files = os.listdir(input_files_dir)

result_data = {
            "Abstract": "",
            "Subsection": [],
            "Status": "",
            "Order Status": "",
            "Order ID": "",
            "Place": "",
            "Date": "",
            "Order Issued By": "",
            "Body": "",
            "References": [],
            "Department": ""  
        }

def extractAbstract(section):
    section = section.replace("\n"," ")
    section = section.replace("~","-")
    split_data = re.split(r'(?<=\D)-\s*|\s*-(?=\D)',section)
    split_data = list(map(str.strip, split_data))
    abs = max(split_data, key = len).strip()
    result_data["Abstract"] = abs
    
    index = split_data.index(abs)
    subs=[]
    for i in range(0,index):
        subs.append(split_data[i])
    result_data["Subsection"] = subs
    result_data["Status"] = split_data[-2]
    if(result_data["Status"]==abs):
        result_data["Status"]=""
    result_data["Order Status"] = split_data[-1].split(".")[0]


def extractOrderID(section):
    section = section.replace(",",", ")
    split_data = section.split(",")
    split_data[0] = split_data[0].replace("Dated","")
    split_data = list(map(str.strip, split_data))
    split_data[2] = split_data[2].replace("-","/")
    split_data[2] = split_data[2].replace(".","/")
    split_data[2] = split_data[2].replace(" ","")
    split_data[0] = split_data[0][re.search(r"\d", split_data[0]).start():]
    split_data[0] = split_data[0].replace("/","_")
    split_data[0] = split_data[0].replace((split_data[0][(split_data[0].rfind("_")+1):]),"HEDN")
    split_data[0] = split_data[0][(split_data[0].rfind(".")+1):]
    result_data["Order ID"]=split_data[0]
    result_data["Place"]=split_data[1]
    result_data["Date"]=split_data[2]

def extractOrderIssuedBy(section):
    s = "(By order of the Governor)"
    ord = section.replace(s,"")
    ord = ord.replace("\n"," ")
    ord = ord.strip()
    result_data["Order Issued By"]=ord

def extractReferences(section):
    split_data = section.split("\n")
    for i in range(len(split_data)):
        split_data[i] = split_data[i].replace(str(i+1)+".","")
        split_data[i] = split_data[i].replace("("+str(i+1)+")","")
        split_data[i] = split_data[i].replace(str(i+1)+" ","")
        split_data[i] = split_data[i].replace("GO.","G.O.")
        split_data[i] = split_data[i].replace("GO","G.O.")
        split_data[i] = split_data[i].replace("G.O","G.O.")
        split_data[i] = split_data[i].replace("G.0","G.O.")
        split_data[i] = split_data[i].replace("G. O","G.O.")
        split_data[i] = split_data[i].replace("dated","Dated")
        split_data[i] = split_data[i].replace("dates","Dated")
        split_data[i] = split_data[i].replace("No","No.")
        split_data[i] = split_data[i].replace("no","No.")
        split_data[i] = split_data[i].replace(":",".")
    split_data=[x for x in split_data if 'G.O.' in x]
    split_data=[x for x in split_data if 'Letter' not in x]
    split_data=[x for x in split_data if '/' in x]
    for i in range(len(split_data)):  
        if("No." in split_data[i]):
            split_data[i] = split_data[i].split("No.")[1]
            split_data[i] = split_data[i].split("Dated")[0]
        else:
            split_data[i] = split_data[i].split("Dated")[0]
    split_data = [s.replace(".","") for s in split_data]
    if(len(split_data)>0):
        for i in range(len(split_data)):
            val = split_data[i].split("/")
            val = list(map(str.strip, val))
            val[2] = val[2].upper()
            val[0] = re.sub('[\D_]+', '', val[0])
            split_data[i]= val[0]+"_"+val[1]+"_"+val[2]

    split_data = list(map(str.strip, split_data))
    result_data["References"] = split_data

def extractSegments(data):

    for field in data:
        section = data[field]
        if (field == "Abstract"):
            extractAbstract(section)
        elif (field == "Order ID"):
            extractOrderID(section)
        elif (field == "Order Issued By"):
            extractOrderIssuedBy(section)
        elif (field == "Body Para"):
            section = section.replace("\n\n"," ")
            result_data["Body"] = section.strip()
        elif (field == "References"):
            extractReferences(section)
        else:
            result_data["Department"] = section.strip()


def extractToSeperateJson():
    for file in input_files:
        file_name = file.split(".")[0]+ ".json"
        d = open(input_files_dir+"/"+file_name, 'r').read()
        data = json.loads(d)
        extractSegments(data)
        count = 0
        with open(output_files_dir+"/"+file_name, "w") as f:
            print("Writing to file: " + file_name)
            f.write(json.dumps(result_data, indent=4))
            count+=1
        
        print("Count: "+str(count))



#Once extraction to seperate json is done, merge all the json files into one json file for Knoweldge Graph
def mergeJsonFiles():
    files = os.listdir(output_files_dir)
    data = {"items":[]}
    for file_name in files:
        with open(output_files_dir+"/"+file_name, "r") as f:
            d = dict(json.loads(f.read()))
            d["Date"] = d["Date"].replace("/","-")#Change date format to match with the date format in the graph database
            d["file_name"] = file_name.split(".")[0] #adding filename
            #Add directorate field
            #Directorate is J for department = "HIGHER EDUCATION (J) DEPARTMENT"
            try:
                d["Directorate"] = re.findall(r'\((.*?)\)', d["Department"])[0]
            except IndexError:
                d["Directorate"] = "J" #Default directorate is J NOTE: adding it just for the sake of not keeping the field blank
            data["items"].append(d)
    with open("Knowledge-Graph/GO_DATA.json", "w") as f:
        print("Writing to file: GO_DATA.json")
        f.write(json.dumps(data, indent=4))

if __name__ == "__main__":
    #extractToSeperateJson() #Already done
    #NOTE(to self) : If you want to extract to seperate json files, comment the below line and uncomment the above line, remember that the data in phase 2 is not at its best(not cleaned)
    mergeJsonFiles()