"""
User is provided with multiple options in performing keyword search

BASIC FUNCTIONALITY
1. By Date: User enters the date and all the notices released on that date are returned to the user
2. By Place: User enters the place and all the notices released at that place are returned to the user
3. By OrderID: User enters the order id and matched notices are returned to the user
4. By FileName: User enters the file name and matched notices are returned to the user
5. By Abstract and Body: User enters a statement and the notices consisting similar phrases are returned to the user

ADVANCED FUNCTIONALITY
1. Search By Order ID on a given set of dates: User enters the range of date and order id and matched documents within the range are returned to the user
2. Search By Place on a given set of dates: User enters the range of date and place and matched documents within the range are returned to the user
3. Search By Keyword on a given set of dates: User enters the range of date and keywords and matched documents within the range are returned to the user

"""

from neo4j import GraphDatabase #importing libraries

try:
    driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "123")) #establishing connection to database
    print("Connection established")
except Exception as e:
    print("Connection Error:",e)



def queryByDate(date:str):
    """
    Function for performing keyword search using DATE
    Paramters: date (string) - stores DATE in the format "YYYY-MM-DD"
    Returns searchResult - a LIST of dictionaries - each dictionary containing key GOID - the GOIDs belong to the notices released on the given date
    """
    query = "MATCH (d:Date)-[r:hasDate]-(go:GO) where d.date = date('"+date+"') RETURN go.GOID" #query for searching
    session = None
    response = None 
    try:
        session = driver.session()
        response = list(session.run(query)) #response obtained
        #formatting the response to return the Govt Order ID of matched records
        searchResult = []
        for record in response:
            d=dict()
            d["GOID"] = record[0]
            searchResult.append(d)
        return searchResult
    except Exception as e:
        print("Date Query failed: ",e) #prints error if one occurs



def queryByOrderID(orderID:str,fromDate:str=None,toDate:str=None):
    """
    Function for performing keyword search using ORDER ID
    Paramters:  1. orderID (string) - stores ORDER ID in the form "####/####/####"
                2. fromDate (string) - storing the starting date of the range in the format "YYYY-MM-DD" - initial value NULL when Basic Search is performed
                3. toDate (string) - storing the end date of the range in the format "YYYY-MM-DD" - initial value NULL when Basic Search is performed
    Returns searchResult - a LIST of dictionaries - each dictionary containing key GOID - the GOIDs belong to the notices released with the given orderID
    """
    #Formatting of the ORDER ID to convert it from "####/####/####" to "####_####_####"
    m = orderID.split("/")
    m[-1] = m[-1].upper()
    m_modified = [s.strip() for s in m]
    orderID = '_'.join(m_modified) 
    
    query=""
    #If fromDate is not null then searching is performed within the range of dates
    if fromDate is None:
        query = "MATCH (go:GO) where go.GOID = '"+orderID+"' return go" #query for searching
    else:
        query="MATCH (d:Date)-[r:hasDate]-(go:GO) where d.date>=date('"+fromDate+"') and d.date<=date('"+toDate+"') and go.GOID='"+orderID+"' return go" #query for searching
    session = None
    response = None 
    try:
        session = driver.session()           
        response = list(session.run(query))
        #formatting the response to return the Govt Order ID of matched records
        searchResult = []
        for record in response:
            searchResult.append(dict(record[0]))
        return searchResult #return the list of GOIDs
    except Exception as e:
        print("OrderID Query failed: ",e) #prints error if one occurs



def queryByPlace(place:str,fromDate:str=None, toDate:str=None):
    """
    Function for performing keyword search using PLACE
    Paramters:  1. place (string),
                2. fromDate (string) - storing the starting date of the range in the format "YYYY-MM-DD" - initial value NULL when Basic Search is performed
                3. toDate (string) - storing the end date of the range in the format "YYYY-MM-DD" - initial value NULL when Basic Search is performed
    Returns searchResult - a LIST of dictionaries - each dictionary containing keys GOID - the GOIDs belong to the notices released at the given place
    """
    query=""
    #If fromDate is not null then searching is performed within the range of dates
    if(fromDate is None):
        query = "MATCH p = (pl:Place)-[r:hasPlace]-(go:GO) where pl.value ='"+place+"' RETURN go.GOID LIMIT 10" #query for searching
    else:
        query = "MATCH (d:Date)-[r:hasDate]-(go:GO) where d.date>=date('"+fromDate+"') and d.date<=date('"+toDate+"') with go MATCH (p:Place)-[r:hasPlace]-(go) where p.value='"+place+"' return go.GOID LIMIT 10" #query for searching

    session = None
    response = None
    
    try:
        session = driver.session()
        response = list(session.run(query))
        print(response)
        #formatting the response to return the Govt Order ID of matched records
        searchResult = []
        for record in response:
            d=dict()
            d["GOID"] = record[0]
            searchResult.append(d)
        return searchResult
    except Exception as e:
        print("Place Query failed: ",e) #print error if one occurs



def fulltextQuery(query:str,page:int=1):
    """
    Function for performing fulltext search
    NOTE: Fulltext in neo4j is implemented using Lucene
    NOTE: At a time only 10 results are returned, if there are more, then request for next page
    page: skips the first 10*(page-1) results and returns the next 10 results
    """
    query = "CALL db.index.fulltext.queryNodes('BodyAndAbstract', '"+query+"') YIELD node, score MATCH (go:GO)-[]-(node) RETURN go.GOID,go.lang,collect(score)[0] SKIP "+ str((page-1)*10)+" LIMIT 10"
    print("Query: ",query)
    session = None
    response = None
    try:
        session = driver.session()
        
        response = list(session.run(query)) #response obtained

        #formatting the response to return the Govt Order ID of matched records
        searchResult = []
        for record in response:
            d =dict()
            d["GOID"] = dict(record)["go.GOID"] #the GOIDs of matched notices
            d["SCORE"] = dict(record)["collect(score)[0]"] #corresponding SCOREs of each GOID
            d["LANG"] = dict(record)["go.lang"] #corresponding LANGs of each GOID
            searchResult.append(d)
        return searchResult
    except Exception as e:
        print("FULLTEXT Query failed: ",e)


def queryByAbstractAndBody(keyword:str,fromDate:str=None,toDate:str=None):
    """
    Function for performing keyword search using ABSTRACT and BODY (FULLTEXT SEARCh)
    Paramters:  1. keyword (string) - stores the keywords to be matched
                2. fromDate (string) - storing the starting date of the range in the format "YYYY-MM-DD" - initial value NULL when Basic Search is performed
                3. toDate (string) - storing the end date of the range in the format "YYYY-MM-DD" - initial value NULL when Basic Search is performed
    Returns searchResult - a LIST of dictionaries - each dictionary containing keys GOID and SCORE - the GOIDs belong to the notices with the matching keywords and the SCOREs determine the percentage of match found in the GOID
    """
    query=""
    #If fromDate is not null then searching is performed within the range of dates
    if(fromDate is None):
        query = "CALL db.index.fulltext.queryNodes('BodyAndAbstract', '"+keyword+"') YIELD node, score MATCH (go:GO)-[]-(node) RETURN go.GOID, collect(score)[0] LIMIT 10" #query for searching
    else:
        query="CALL db.index.fulltext.queryNodes('BodyAndAbstract', '"+keyword+"') YIELD node, score MATCH (node)-[]-(go:GO)-[r:hasDate]-(d:Date) where d.date>=date('"+fromDate+"') and d.date<=date('"+toDate+"') RETURN go.GOID, collect(score)[0]" #query for searching
    print("Query: ",query)
    session = None
    response = None
    try:
        session = driver.session()
        
        response = list(session.run(query)) #response obtained

        #formatting the response to return the Govt Order ID of matched records
        searchResult = []
        for record in response:
            d =dict()
            d["GOID"] = dict(record)["go.GOID"] #the GOIDs of matched notices
            d["SCORE"] = dict(record)["collect(score)[0]"] #corresponding SCOREs of each GOID
            searchResult.append(d)
        return searchResult
    except Exception as e:
        print("Index Query failed: ",e)



def getAbstract(goid:str):
    """
    Function to extract Abstract of the given order
    Parameter: goid (string): containing the Govt Order Id of the notice
    Return the Abstract (string) of the goid
    """
    query = "MATCH (go:GO)-[r:hasAbstract]-(a:Abstract) where go.GOID = '"+goid+"' RETURN a.value"
    try:
        session = driver.session()
        response = list(session.run(query))
        return response[0]["a.value"] #return the abstract
    except Exception as e:
        print("Abstract Query failed: ",e)



def getDate(goid:str):
    """
    Function to extract Date of the given order
    Parameter: goid (string): containing the Govt Order Id of the notice
    Return the Date (string) of the goid
    """
    query = "MATCH (go:GO)-[r:hasDate]-(d:Date) where go.GOID = '"+goid+"' RETURN d.date"
    try:
        session = driver.session()
        response = list(session.run(query))
        return response[0]["d.date"]  #return the abstract
    except Exception as e:
        print("Date Query failed: ",e)
def getLanguage(goid:str):
    """
    Function to extract Date of the given order
    Parameter: goid (string): containing the Govt Order Id of the notice
    Return the language of the document
    """
    query = "MATCH (go:GO) where go.GOID = '"+goid+"' return go.lang"
    try:
        session = driver.session()
        response = list(session.run(query))
        return response[0]["go.lang"] if len(response)>0 else None  #return the language
    except Exception as e:
        print("Language Query failed: ",e)



def getPlace(goid:str):
    """
    Function to extract Place of the given order
    Parameter: goid (string): containing the Govt Order Id of the notice
    Return the Place (string) of the goid
    """
    query = "MATCH (go:GO)-[r:hasPlace]-(p:Place) where go.GOID = '"+goid+"' RETURN p.value"
    try:
        session = driver.session()
        response = list(session.run(query))
        return response[0]["p.value"]
    except Exception as e:
        print("Query failed: ",e)

def getDepartment(goid:str):
    """
    Function to extract Department of the given order
    Parameter: goid (string): containing the Govt Order Id of the notice
    Return the Place (string) of the goid
    """
    query = "MATCH (go:GO)-[r:hasDepartment]-(p:Department) where go.GOID = '"+goid+"' RETURN p.value"
    try:
        session = driver.session()
        response = list(session.run(query))
        return response[0]["p.value"]
    except Exception as e:
        print("Query failed: ",e)


def getReferences(goid:str):
    """
    Function to extract References of the given order
    Parameter: goid (string): containing the Govt Order Id of the notice
    Return the LIST of References of the goid
    """
    query = "MATCH (go:GO)-[r:hasReference]-(ref:Reference) where go.GOID = '"+goid+"' RETURN ref.value"
    try:
        session = driver.session()
        response = list(session.run(query))
        searchResult = []
        for record in response:
            searchResult.append(record[0])
        return searchResult #return the list of references
    except Exception as e:
        print("Query failed: ",e)



def getDetails(response:list):
    """
    Function to extract Details of the given order (Date, Place, OrderId, References, Abstract)
    Parameter: response (list): containing the list of multiple Govt Order Ids whose details are needed to be displayed
    Return the LIST of Dictionaries - each dictionary consists of details of one Govt Order
    Each response has
    Abstract: Abstract of the GO
    Date: Date of the GO
    Place: Place of the GO
    References: List of References of the GO
    GOID: Govt Order ID of the GO
    Language: Language of the GO
    Department: Department of the GO
    SCORE: Score of the GO
    """
    details = []
    try:
        for record in response:
            d = dict()
            d["Abstract"] = getAbstract(record["GOID"])
            d["Date"] = getDate(record["GOID"])
            d["Place"] = getPlace(record["GOID"])
            d["References"] = getReferences(record["GOID"])
            d["GOID"] = record["GOID"]
            d["Language"] = getLanguage(record["GOID"]) #Adding language to the details
            d["Department"] = getDepartment(record["GOID"])
            if "SCORE" in record.keys():
                d["SCORE"] = record["SCORE"]
            details.append(d)
        return details #return the details of all the files to the user
    except Exception as e:
        print("Query failed: ",e)


#Function to get the body of the given orderid
def getBody(goid:str):
    query = "MATCH (go:GO)-[r:hasBody]-(b:Body) where go.GOID = '"+goid+"' RETURN b.value"
    try:
        session = driver.session()
        response = list(session.run(query))
        return response[0]["b.value"]
    except Exception as e:
        print("Query failed: ",e)



def getReferencedGO(ReferenceID:str):
    """
    Function to extract all the Govt Order IDs which take reference from one common order
    Parameter: ReferenceID (string): containing the Order ID of the reference order
    Returns the LIST of Govt Order IDs which take reference from one common order
    """
    query="MATCH (ref:Reference)-[r:hasReference]-(go:GO) where ref.value = '"+ReferenceID+"' RETURN go.GOID"
    session = None
    response = None
    try:
        session = driver.session()
        response = list(session.run(query))
        searchResult = []
        for record in response:
            searchResult.append(record[0])
        return searchResult #return the list of references
    except Exception as e:
        print("Query failed: ",e)



def UserInterface(query:str,type:str,fromDate:str=None,toDate:str=None):
    """
    Function to provide an interface to user in order to perform queries and obtain results"
    Paramters:  1. query (string) - the element on which the search is based
                2. type (string) - tells the category (or relationship) to which the query paramter belongs to
                3. fromDate (string) - storing the starting date of the range in the format "YYYY-MM-DD" - initial value NULL when Basic Search is performed
                4. toDate (string) - storing the end date of the range in the format "YYYY-MM-DD" - initial value NULL when Basic Search is performed

    Returns a LIST of Dictionatries - each Dictionary contains details of one matched Govt Order
    """
    response = [] #stores the govt order id of matched files
    useful_response = [] #stored informartion regarding matched files

    #Multiple ways of querying (By Date, OrderID, Place, Filename, Abstract)
    if(type=='Date'):
        response = queryByDate(query)
    elif(type=='OrderID'):
        response = queryByOrderID(query,fromDate,toDate)
    elif(type=='Place'):
        response = queryByPlace(query,fromDate,toDate)    
    elif(type=='Keyword'):
        response = queryByAbstractAndBody(query,fromDate,toDate)
    else:
        response = queryByAbstractAndBody(query,fromDate,toDate)
    try:
        useful_response = getDetails(response) #getting useful details of each file
        return useful_response #returning the data to the user
    except:
        print("Error: No results found")
        return None #NoneType error

def SearchInterface(query:str,page:int=1):
    """
    Extended fulltext search interface to user
    Returns the data which would be useful for user's search result
    NOTE: At a time only 10 results are returned, if there are more, then request for next page
    page: skips the first 10*(page-1) results and returns the next 10 results
    Each response has
    Abstract: Abstract of the GO
    Date: Date of the GO
    Place: Place of the GO
    References: List of References of the GO
    GOID: Govt Order ID of the GO
    Language: Language of the GO
    Department: Department of the GO
    SCORE: Score of the GO
    """
    response = fulltextQuery(query,page)
    
    try:
        useful_response = getDetails(response) #getting useful details of each file
        return useful_response #returning the data to the user
    except:
        print("Error: No results found")
        return None #NoneType error


"""
testing paramters
print(UserInterface("2020-11-24","Date"))
print("\n\n")
print(UserInterface("1444/2020/HEDN","OrderID"))
print("\n\n")
print(UserInterface("Dr.Jayasankar Prasad continued to hold full additional", "Keyword"))
print("\n\n")
print(UserInterface("Thiruvananthapuram","Place"))
print("\n\n")
print(UserInterface("1444/2020/HEDN","OrderID","2020-11-01","2020-12-01"))
print("\n\n")
print(UserInterface("Thiruvananthapuram","Place","2020-11-01","2020-12-01"))
print("\n\n")
print(UserInterface("Dr.Jayasankar Prasad continued to hold full additional","Keyword","2020-11-01","2020-12-01"))
print("\n\n")
print(getReferencedGO("4279_2020_FIN"))
"""