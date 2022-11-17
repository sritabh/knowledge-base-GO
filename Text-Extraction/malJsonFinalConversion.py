import json
import os
import re
from datetime import datetime
c_dir = os.getcwd()
input_files_dir = c_dir + "/Text-Extraction/mal_json_phase2"
output_files_dir = c_dir +"/Text-Extraction/mal_json_phase3-final"

input_files = os.listdir(input_files_dir)

def extractAbstractSection(abstractParams:str):
    """
    Returns orderStatus,abstract and subsection
    """
    #Remove the department from end and join back the value

    abstractParamsUpdated = abstractParams.split("\n")[:-1]
    abstractParams = ""
    for element in abstractParamsUpdated:
        if element != "":
            abstractParams += element + "\n"
    abstractElem = abstractParams.split('-')
    #Remove first element
    subsection = []
    subsection.append(abstractElem[0])
    abstractElem.pop(0)
    orderStatus =abstractElem[-1].strip()
    abstractElem.pop(-1)
    abstract = ""
    #Last element is abstract
    abstract+=abstractElem[-1] + ", "+subsection[0]
    abstractElem.pop(-1)
    #Add rest of the element to abstract to allow fulltext search
    abstract.join(abstractElem)
    #Add rest value to subsection
    for ele in abstractElem:
        subsection.append(ele)
    return (abstract,orderStatus,subsection)
    
def extractDepartment(abstract:str):
    """
    Last line in abstract is probably department
    Return abbreviation too
    """
    department = abstract.split("\n")[-1]
    #If last word of department is Deptt change it to Department
    department = department.replace("Deptt", "Department")
    # department = valWithdepartment.split("-")[0]
    extraVal = department.split()
    #Take first character of all except '('
    departmentAbreviation = ''.join([i[0] for i in extraVal if i[0] != '('])+'N'
    #Find directorate, i.e. () value remove it, keep department name capital
    directorateMatch = re.search(r"\([A-Za-z\s]+\)",department)
    directorate  = ""
    if directorateMatch:
        directorate = directorateMatch.group()
        directorate = directorate.replace("(","").replace(")","")
        directorate = directorate.upper()
        #Remove directorate from department
        department = department.replace(directorateMatch.group(),"")
        #Upper case department
    department = department.upper()
    #Remove extra space
    department = department.strip()

    return (departmentAbreviation,department,directorate)
def getorderIDPlaceDate(deptAb,orderIDParams):
    """
    orderID: S.U.(Sadha) No.237/2022/4th dated Thiruvananthapuram, 29-05-2022
    Since ID doesn't have any department value, we will append the deptAb to govt ID
    govtID format = 237_2022_{deptAb}
    """
    #Extract orderID
    #Regex to extract orderID as 237/2022
    orderIDDATA = re.search(r"\d+\/\d+",orderIDParams)
    orderID = ""
    if orderIDDATA:
        orderID = orderIDDATA.group()
        intGID = orderID.split("/")
        #Append deptAb to orderID
        orderID = intGID[0]+"_"+intGID[1]+"_"+deptAb
        # print(govtID)
    else:
        print("Warning: Govt ID not Detected\n=========================================")
    
    #Extract Place, By default it is Thiruvananthapuram
    place = "Thiruvananthapuram"
    #Extract Date
    # date = re.search(r"\d{2}-\d{2}-\d{4}",orderIDParams)
    # #Try second method
    # if not date:
    #     date = re.search(r"\d{2}\/\d{2}\/\d{4}",orderIDParams)
    # #Try third method i.e. 29.05.2022

    # if not date:
    #     date = re.search(r"\d{2}\.\d{2}\.\d{4}",orderIDParams)
    # if date:
    #     date = date.group()
    #     print(date)
    # else:
    #     print("Warning: Date not Detected\n=========================================")
    #     print(orderIDParams
    #Take last element after , which is non empty
    date = orderIDParams.split(",")[-1].strip()
    date = date.replace(".","")
    #Convert date to date format and then to string to make sure it's in correct format
    #Output format as dd-mm-yyyy
    try:
        date = str(datetime.strptime(date, '%d-%m-%Y').strftime('%d-%m-%Y'))

    except ValueError as ve:
        date = str(datetime.strptime(date, '%d/%m/%Y').strftime('%d-%m-%Y'))
    # print(date)
    return (orderID,place,date)
def getOrderIssuedBy(orderIssuedByParams):
    orderIssuedBy = orderIssuedByParams.split("\n")[0]
    return orderIssuedBy

def getReferences(refText):
    # regRule = "\d+\/\d+\/[A-Z]+"
    refMatch = re.findall(r"\d+\/\d+\/[A-Z]+",refText)
    refList = []
    for ref in refMatch:
        ref = ref.replace("/","_")
        refList.append(ref)
    return refList


filename_map = {} #Map the filename to the orderID
def extractMalDataToJson():
    for file_name in input_files:
         with open(input_files_dir+"/"+file_name, "r") as f:
            print(input_files_dir+"/"+file_name)
            d = dict(json.loads(f.read()))
            (departmentAbreviation,department,directorate) =extractDepartment(d['Abstract'])
            
            (orderID,place,date) = getorderIDPlaceDate(departmentAbreviation,d['Order ID'])
            orderIssuedBy = getOrderIssuedBy(d["Order Issued By"])
            (abstract,orderStatus,subsection) = extractAbstractSection(d["Abstract"])
            referenceList = getReferences(d["References"])
            #Create json file
            data = {
                "Abstract":abstract,
                "Subsection":subsection,
                "Status":"",
                "Order Status":orderStatus,
                "Order ID":orderID,
                "Place":place,
                "Date":date,
                "Order Issued By":orderIssuedBy,
                "Body":d["Body Para"],
                "References":referenceList,
                "Department":department,
                "filename":file_name,
                "Directorate":directorate
                
            }
            #Save the json file
            with open(output_files_dir+"/"+file_name, 'w+') as outfile:
                json.dump(data, outfile)
            #Add to filename map
            filename_map[file_name] = orderID
    print("Dobe")
    #Save name mapping
    # with open(output_files_dir+"/filename_map.json", 'w+') as outfile:
    #     json.dump(filename_map, outfile)

def mergeMalJSONDAT():
    files = os.listdir(output_files_dir)
    data = {"items":[]}
    for file_name in files:
        with open(output_files_dir+"/"+file_name, "r") as f:
            d = dict(json.loads(f.read()))
            d["Language"] = "mal"
            data["items"].append(d)
    with open("Knowledge-Graph/GO_DATA_mal.json", "w") as f:
        print("Writing to file: GO_DATA_mal.json")
        f.write(json.dumps(data, indent=4))







mergeMalJSONDAT()