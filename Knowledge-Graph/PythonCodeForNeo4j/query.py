"""
User is provided with multiple options in performing keyword search

1. By Date: User enters the date and all the notices released on that date are returned to the user
2. By Place: User enters the place and all the notices released at that place are returned to the user
3. By OrderID: User enters the order id and matched notices are returned to the user
4. By FileName: User enters the file name and matched notices are returned to the user
5. By Abstract and Body: User enters a statement and the notices consisting similar phrases are returned to the user
"""


from neo4j import GraphDatabase

# class for Neo4j Database Management
class DatabaseManagement:

    """
    Function for connecting to the database
      user and password for authenticating the client
      uri is the server where database is hosted 
    """
    def __init__(self, uri, user, password): 
        self.driver = None
        try:
            self.driver = GraphDatabase.driver(uri, auth=(user, password)) #connecting to the Database
        except Exception as e:
            print("Failed to connect")

    #Function for closing the connection to the database
    def close(self):
        self.driver.close()

    #Function for performing keyword search using Abstarct and Body(FULLTEXT SEARCH)
    def queryByAbstractAndBody(self,message):
        session = None
        response = None
        try:
            session = self.driver.session()
            query = "CALL db.index.fulltext.queryNodes(\"BodyAndAbstract\", \""+message+"\") YIELD node, score RETURN node.ofGovtID, score LIMIT 10" #query for searching
            response = list(session.run(query)) #response obtained

            #formatting the response to return the Govt Order ID of matched records
            searchResult = []
            for record in response:
                searchResult.append(record[0])
            return searchResult
        except Exception as e:
            print("Query failed: ",e)

    
    #Function for performing keyword search using Date
    def queryByDate(self,message):
        session = None
        response = None 
        try:
            session = self.driver.session()
            query = "MATCH p = (go:GO)-[r:hasDate]->(d:Date) where d.date ='"+message+"' RETURN go.OrderID" #query for searching
            response = list(session.run(query)) #response obtained

            #formatting the response to return the Govt Order ID of matched records
            searchResult = []
            for record in response:
                searchResult.append(record[0])
            return searchResult
        except Exception as e:
            print("Query failed: ",e)
    
    #Function for performing keyword search using OrderID
    def queryByOrderID(self,message):
        session = None
        response = None 
        try:
            session = self.driver.session()
            query = "MATCH p = (go:GO)-[r:hasOrderID]->(o:OrderID) where o.value ='"+message+"' RETURN go.OrderID" #query for searching
            response = list(session.run(query))
            
            #formatting the response to return the Govt Order ID of matched records
            searchResult = []
            for record in response:
                searchResult.append(record[0])
            return searchResult
        except Exception as e:
            print("Query failed: ",e)
    

    #Function for performing keyword search using Place
    def queryByPlace(self,message):
        session = None
        response = None 
        try:
            session = self.driver.session()
            query = "MATCH p = (go:GO)-[r:hasPlace]->(pl:Place) where pl.value ='"+message+"' RETURN go.OrderID" #query for searching
            response = list(session.run(query))

            #formatting the response to return the Govt Order ID of matched records
            searchResult = []
            for record in response:
                searchResult.append(record[0])
            return searchResult
        except Exception as e:
            print("Query failed: ",e)

    
    #Function for performing keyword search using FileName
    def queryByFileName(self,message):
        session = None
        response = None 
        try:
            session = self.driver.session()
            query = "MATCH p = (go:GO) where go.file_name ='"+message+"' RETURN go.OrderID" #query for searching
            response = list(session.run(query))
            
            #formatting the response to return the Govt Order ID of matched records
            
            searchResult = []
            for record in response:
                searchResult.append(record[0])
            return searchResult
        except Exception as e:
            print("Query failed: ",e)

    
    #Function for obtain details of a file using it's OrderID
    def getDetails(self,OrderID):
        session = None
        response = None 
        try:
            session = self.driver.session()
            searchResult = dict()
            
            #Obtaining abstract of the file
            query = "MATCH p = (go:GO)-[r:hasAbstract]->(a:Abstract) where go.OrderID= '"+OrderID+"' RETURN a.value"
            response = list(session.run(query))
            searchResult['Abstract'] = dict(response[0])['a.value']

            #Obtaining place of the file
            query = "MATCH p = (go:GO)-[r:hasPlace]->(pl:Place) where go.OrderID= '"+OrderID+"' RETURN pl.value"
            response = list(session.run(query))
            searchResult['Place'] = dict(response[0])['pl.value']

            #Obtaining date of the file
            query = "MATCH p = (go:GO)-[r:hasDate]->(d:Date) where go.OrderID= '"+OrderID+"' RETURN d.date"
            response = list(session.run(query))
            searchResult['Date'] = dict(response[0])['d.date']

            #Obtaining file name of the file
            query = "MATCH (go:GO) where go.OrderID= '"+OrderID+"' RETURN go.file_name"
            response = list(session.run(query))
            searchResult['FileName'] = dict(response[0])['go.file_name']
            
            #Obtaining order id of the file
            searchResult['OrderID'] = OrderID

            return searchResult
        except Exception as e:
            print("Query failed: ",e)



# User Interface to use the class DatabaseManagement
def UserInterface(query,type):
    conn = DatabaseManagement("bolt://localhost:7687", "neo4j", "123") #establishing connection
    response = [] #stores the govt order id of matched files
    useful_response =[] #stored informartion reagrding matched files

    #Multiple ways of querying (By Date, OrderID, Place, Filename, Abstract)
    if(type=='Date'):
        response = conn.queryByDate(query)
    elif(type=='OrderID'):
        response = conn.queryByOrderID(query)
    elif(type=='Place'):
        response = conn.queryByPlace(query)
    elif(type=='FileName'):
        response = conn.queryByFileName(query)
    elif(type=='Abstract'):
        response = conn.queryByAbstractAndBody(query)
    

    for data in response:
        useful_response.append(conn.getDetails(data)) #getting details of each file
    
    conn.close() #closing the connection

    return useful_response #returning the data to the user