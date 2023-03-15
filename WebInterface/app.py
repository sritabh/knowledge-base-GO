from socket import fromfd
from flask import Flask, render_template,request
from flask import *
from query import *
import re

app = Flask(__name__)


@app.route("/") 
def home():
    return render_template("index.html")
    
@app.route("/search",methods= ["GET"])
def show_result():
    query = request.args.get("query")
    page = int(request.args.get("page") if request.args.get("page") != None else 1)
    print("PAGE",page)

    #Replace non alphanumeric from query with space
    # clean_query = re.sub(r"[^A-Za-z0-9]", " ", query)
    option = request.args.get("type")
    #Advanced options
    fromDate = request.args.get("FromDate") if request.args.get("FromDate") !="" else None
    toDate = request.args.get("ToDate") if request.args.get("ToDate") !="" else None

    # response = UserInterface(query,option,fromDate,toDate) 
    response = SearchInterface(query,page)
    if response is not None and len(response) == 0:
        response = None
    
    if response != None:
        for res in response:
            filename = res['GOID'] #ID of the file
            res['GOID'] = goid_formatter(filename)
            res['Filename'] = filename
            res["Body"] = getBody(filename)[:270] + "..."
            res["Department"] = res['Department']
            res["Date"] = res['Date']
            #res['Abstract'] = res['Abstract'][:160] + "..."

    #Add extra parameters
    data = {}
    data["query"] = query
    data["queryType"] = option
    data["resultAvailable"] = True
    data["nextPageAvailable"] = True if response != None and len(response) == 10 else False
    data["prevPageAvailable"] = True if page > 1 else False
    data["nextPage"] = page+1
    data["prevPage"] = page-1
    data["fromDate"] = fromDate
    data["toDate"] = toDate
    if response == None:
        data["resultAvailable"] = False
    data["result"] = response
    # print(data)
    return render_template("result.html", data = data)



@app.route("/viewDoc/<filename>")
def viewDoc(filename):
    docType = request.args.get("docType")
    data = {}
    lang = getLanguage(filename)
    # print(filename)
    # print("Language: ",lang)
    data["filename"] = filename #ID of the file
    if lang=="mal":
        data["filename"] = "mal/"+filename
    data["GOID"] = goid_formatter(filename)
    data["isRefDoc"] = False
    if docType == "refDoc":
        data["isRefDoc"] = True
    #References to the file
    #NOTE: filename is simply GOID
    references = getReferences(filename)
    data["references"] = []
    data["hasReference"] = False
    for ref in references:
        refData = {}
        refData["filename"] = ref
        refData["GOID"] = goid_formatter(ref)
        data["references"].append(refData)

    if data["references"] != []:
        data["hasReference"] = True
    #If the type is reference Doc, then show the base Govt Orders which is refering to this GO
    data["baseGOs"] = []
    if data["isRefDoc"]:
        baseGOs = getReferencedGO(filename)
        go_dict = {}
        for go in baseGOs:
            go_dict["GOID"] = goid_formatter(go)
            go_dict["filename"] = go
            data["baseGOs"].append(go_dict)
    # print(data)
    return render_template("pdf.html",data=data)

 

#Utility function
def goid_formatter(goid:str)->str:
    """
    Given goid in format 1149_2020_HEDN
    returns G.O.(Rt)No.1149/2020/HEDN
    """
    goid = goid.split("_")
    
    return "G.O.(Rt)No.{}/{}/{}".format(goid[0],goid[1],goid[2])
    

if __name__== "__main__":
    app.run(debug=True, port=8000)
