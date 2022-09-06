#Extracting data from text file into json file
#NOTE: regex library is used instead of default re library
import json
import os
import regex as re

"""
Regex Required
==========================

Abstract
--------------------------
Between "Abstract" and line containing EDUCATION(Group 1)
(?<=Abstract)((.|\n)*)(?=(\n.*EDUCATION.*\n))

Everything Above line containing EDUCATION(Group 2)
^(((.|\n)*)(\n.*EDUCATION.*\n))


(Order ID)
--------------------------
Group 2(Includes Department aswell in Group 1)
(.*EDUCATION.*)[\r\n]+([^\r\n]+)

Line of the format {}/{}/{}
Group 0
\n.*(\d|\W)*\/(\d|\W)*\/(\d|(\W&^\n))*\n

References
--------------------------
Group 0
Between Order ID line and line containing ORDER
(.*EDUCATION.*)[\r\n]+([^\r\n]+)\K(.|\n)*(?=\nORDER)

Body Para
--------------------------
Group 0
Full content of the order i.e. all paragraphs
(?<=\nORDER)(.|\n)*(?=\(By order of the Governor\))

OrderIssuedBy
--------------------------
Group 0
Contains 2 lines
C AJAYAN
ADDITIONAL SECRETARY

(\(By order of the Governor\)).*\n.*\n.*\n

"""

c_dir = os.getcwd() #current directory
input_files_dir = c_dir + "/Text-Extraction/output/"
output_files_dir = c_dir + "/Text-Extraction/json_output/"
    
input_files = os.listdir(input_files_dir) #input folder containing pdf files


def extractData(regExp:str, text:str,groupVal:int=0)->str:
    """
    Extracts and returns the clean data from the text file based on regular expression
    :param regExp: Regular expression to be used for extraction
    :param text: Text file to be used for extraction
    :param groupVal: Group to be extracted
    :return: Clean data
    """
    data = re.search(regExp, text)
    if data:
        dataVal = data.group(groupVal) #Value of the group
        dataVal = dataVal.strip() #Removing leading and trailing spaces and newline characters
        return dataVal
    else:
        return "" #Return empty string if no data is found




class DataExtractor:
    """
    Class to extract data from text file in formatted manner
    """
    def __init__(self,filename:str) -> None:
        self.filename = filename
        self.fileData = open(filename,"r").read()
        self.statusLog = "" #Maintain status of the extraction
        self.statusCode = 0 #Maintain status code of the extraction, 0 means success, anything more than that means there's a problem
        self._regex_dict = {
            "Abstract": [{
                "regex": "(?<=Abstract)((.|\n)*)(?=(\n.*EDUCATION.*\n))",
                "groupVal": 1
            },{
                "regex": "^(((.|\n)*)(\n.*EDUCATION.*\n))",
                "groupVal": 2
            }],
            "Order ID": [{
                "regex": "(.*EDUCATION.*)[\r\n]+([^\r\n]+)",
                "groupVal": 2
            },{
                "regex": "\n.*(\d|\W)*\/(\d|\W)*\/(\d|(\W&^\n))*\n",
                "groupVal": 0
            }],
            "References": [{
                "regex": "(.*EDUCATION.*)[\r\n]+([^\r\n]+)\K(.|\n)*(?=\nORDER)",
                "groupVal": 0
            }],
            "Order Issued By": [{
                "regex": "(\(By order of the Governor\)).*\n.*\n.*\n",
                "groupVal": 0
            }],
            "Body Para": [{
                "regex": "(?<=\nORDER)(.|\n)*(?=\(By order of the Governor\))",
                "groupVal": 0
            }]

        }
    #Getter methods for data sections, getter method generates extraction log data
    def getAbstract(self)->str:
        abstractRegX = self._regex_dict["Abstract"]
        abstract = extractData(abstractRegX[0]["regex"],self.fileData,abstractRegX[0]["groupVal"])
        if abstract == "":
            abstract = extractData(abstractRegX[1]["regex"],self.fileData,abstractRegX[1]["groupVal"])
            self.__addLog("Abstract is extracted using 2nd regex, Cleaning Required!")
            #Update status code
            self.statusCode +=1
        else:
            self.__addLog("Abstract Extracted!")
        return abstract

    def getOrderID(self)->str:
        orderIDRegX = self._regex_dict["Order ID"]
        orderID = extractData(orderIDRegX[0]["regex"],self.fileData,orderIDRegX[0]["groupVal"])
        if orderID == "":
            orderID = extractData(orderIDRegX[1]["regex"],self.fileData,orderIDRegX[1]["groupVal"])
            self.__addLog("Order ID is extracted using 2nd regex, Success!")
        else:
            self.__addLog("Order ID Extracted!")
        return orderID

    def getOrderIssuedBy(self)->str:
        orderIssuedByRegX = self._regex_dict["Order Issued By"]
        orderIssuedBy = extractData(orderIssuedByRegX[0]["regex"],self.fileData,orderIssuedByRegX[0]["groupVal"])
        if orderIssuedBy == "":
            self.__addLog("Order Issued By is not extracted!")
            #Update status code for failure
            self.statusCode +=1
        else:
            self.__addLog("Order Issued By Extracted!")
        return orderIssuedBy

    def getBodyPara(self)->str:
        bodyParaRegX = self._regex_dict["Body Para"]
        bodyPara = extractData(bodyParaRegX[0]["regex"],self.fileData,bodyParaRegX[0]["groupVal"])
        if bodyPara == "":
            self.__addLog("Body Para is not extracted!")
            #Update status code for failure
            self.statusCode +=1
        else:
            self.__addLog("Body Para Extracted!")
        return bodyPara

    def getReferences(self)->str:
        referencesRegX = self._regex_dict["References"]
        references = extractData(referencesRegX[0]["regex"],self.fileData,referencesRegX[0]["groupVal"])
        if references == "":
            self.__addLog("References is not extracted!")
            #Update status code for failure
            self.statusCode +=1
        else:
            self.__addLog("References Extracted!")
        return references

    def getDepartment(self)->str:
        departmentRegX = self._regex_dict["Order ID"]
        department = extractData(departmentRegX[0]["regex"],self.fileData,1)
        if department == "":
            department = "HIGHER EDUCATION ( ) DEPARTMENT"
            self.__addLog("Department is not extracted!\n Default: HIGHER EDUCATION ( ) DEPARTMENT is added as value")
            #Update status code for failure
            self.statusCode +=1
        else:
            self.__addLog("Department Extracted!")
        return department

    def getStatusLog(self)->str:
        self.__addLog("Status Code: "+str(self.statusCode))
        return self.filename + "\n=====================================\n"+self.statusLog + "-------------------------------------------------\n\n"

    def __addLog(self,log:str)->None:
        self.statusLog += log + "\n"
    def to_dict(self)->dict:
        """
        Returns a dictionary of all the extracted data
        """
        data_dict = {
            "Abstract": "",
            "Order ID": "",
            "Order Issued By": "",
            "Body Para": "",
            "References": "",
            "Department": ""
        }
        data_dict["Abstract"] = self.getAbstract()
        data_dict["Department"] = self.getDepartment()
        data_dict["Order ID"] = self.getOrderID()
        data_dict["References"] = self.getReferences()
        data_dict["Body Para"] = self.getBodyPara()
        data_dict["Order Issued By"] = self.getOrderIssuedBy()
        return data_dict




def extractToJson(file,dest_dir = ""):
    file_name = file.split('.')[0] + ".json" #output file name
    print("Processing file: " + file)
    eData = DataExtractor(dest_dir+file) #Data extractor
    data_dict = eData.to_dict() #Extracted data in dictionary format
    try:
        with open(dest_dir + file_name, "w") as f:
            print("Writing to file: " + file_name)
            f.write(json.dumps(data_dict, indent=4))
    except FileNotFoundError:
        #Create dir
        os.mkdir(dest_dir)
        with open(dest_dir + file_name, "w") as f:
            print("Writing to file: " + file_name)
            f.write(json.dumps(data_dict, indent=4))
    #Generate log in the file
    print("Writing Logs!")
    with open(dest_dir + "extraction.log", "a") as f:
        f.write(eData.getStatusLog())
    print(eData.getStatusLog())




# print("Processing....")
# for file in input_files:
#     file_name = file.split('.')[0] + ".json" #output file name
#     print("Processing file: " + file)
#     eData = DataExtractor(file) #Data extractor
#     data_dict = eData.to_dict() #Extracted data in dictionary format
#     try:
#         with open(output_files_dir + file_name, "w") as f:
#             print("Writing to file: " + file_name)
#             f.write(json.dumps(data_dict, indent=4))
#     except FileNotFoundError:
#         #Create dir
#         os.mkdir(output_files_dir)
#         with open(output_files_dir + file_name, "w") as f:
#             print("Writing to file: " + file_name)
#             f.write(json.dumps(data_dict, indent=4))
#     #Generate log in the file
#     print("Writing Logs!")
#     with open(output_files_dir + "extraction.log", "a") as f:
#         f.write(eData.getStatusLog())
#     print(eData.getStatusLog())

# print("Done!")

dest_dir = c_dir + "/Text-Extraction/malyalam_output/"
input_file = "file_eng.txt"
extractToJson(input_file,dest_dir)
