from neo4j import GraphDatabase
driver=GraphDatabase.driver(uri="bolt://localhost:7687",auth=("","neo4j"))
session=driver.session()
#search all nodes
query="MATCH (n) return (n)"
nodes=session.run(query)
for node in nodes:
    print(node)
#get specific results from graphdb
date=input()
query="MATCH (n) where n.Date=date return (n)"#date=given by user
nodes=session.run(query)
for node in nodes:
    print(node)
#create new node with label, properties Eg:
q1="CREATE (N:LABEL{Date:date})" #date=given by user
session.run(q1)
q2=" MATCH (n:LABEL) return (x)"
nodes=session.run(q2)
for node in nodes:
    print(node)
#add relationship btw nodes
query="""match(a:GO{Date:"17/02/2020"}),(b:GO{Date:date}) 
create (a)-[r1:hasdate]->(b)
"""#date=given by user
nodes=session.run(query)