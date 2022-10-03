#Extracting data from text file into json file
#NOTE: regex library is used instead of default re library
import json
import os
import regex as re

"""
Regex Required
==========================

Abstract+Department = (?<=Summary)((.|\n)*?)(.*)(S\.U\..*\n)

Govt Order ID(Match 1 group 4): (?<=Summary)((.|\n)*?)(.*)(S\.U\..*\n)

Reference: (S.U..*\n*)\K(.|\n)*(?=\norder) or ((Reference))(.|\n)*(?=\norder\n)

Body para - (?<=\norder)(.|\n)*(?=\(By order of the Governor\))

Signature - (?<=\(By order of the Governor\))(.|\n)*

"""

c_dir = os.getcwd() #current directory
input_files_dir = c_dir + "/Text-Extraction/malayalam_output_eng/"
output_files_dir = c_dir + "/Text-Extraction/malayalam_json_output/"
    
input_files = os.listdir(input_files_dir) #input folder containing pdf files


def extractData(regExp:str, text:str,groupVal:int=0)->str:
    """
    Extracts and returns the clean data from the text file based on regular expression
    :param regExp: Regular expression to be used for extraction
    :param text: Text file to be used for extraction
    :param groupVal: Group to be extracted
    :return: Clean data
    """
    data = re.search(regExp, text,re.IGNORECASE)
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
                "regex": "(?<=Summary)((.|\n)*?)(.*)(S\.U\..*\n)",
                "groupVal": 1
            }],
            "Order ID": [{
                "regex": "(?<=Summary)((.|\n)*?)(.*)(S\.U\..*\n)",
                "groupVal": 4
            }],
            "References": [{
                "regex": "((Reference))(.|\n)*(?=\norder\n)",
                "groupVal": 0
            }],
            "Order Issued By": [{
                "regex": "(?<=\(By order of the Governor\))(.|\n)*",
                "groupVal": 0
            }],
            "Body Para": [{
                "regex": "(?<=\norder)(.|\n)*(?=\(By order of the Governor\))",
                "groupVal": 0
            }]

        }
    #Getter methods for data sections, getter method generates extraction log data
    def getAbstract(self)->str:
        abstractRegX = self._regex_dict["Abstract"]
        abstract = extractData(abstractRegX[0]["regex"],self.fileData,abstractRegX[0]["groupVal"])
        if abstract == "":
            self.__addLog("Abstract is not extracted!")
            #Update status code for failure
            self.statusCode +=1
        return abstract

    def getOrderID(self)->str:
        orderIDRegX = self._regex_dict["Order ID"]
        orderID = extractData(orderIDRegX[0]["regex"],self.fileData,orderIDRegX[0]["groupVal"])
        if orderID == "":
            self.statusCode +=1
            self.__addLog("Order ID is not extracted!")
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
        department = "FIX-ME" #extractData(departmentRegX[0]["regex"],self.fileData,1)
        if department == "":
            pass
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
    eData = DataExtractor(input_files_dir+file) #Data extractor
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




print("Processing....")
for file in input_files:
    # print(file.open())
    extractToJson(file,output_files_dir)
print("Done!")


