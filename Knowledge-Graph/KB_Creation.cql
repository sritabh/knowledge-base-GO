//========Labels============
// GoK
// Document
// 	GO
// Department
// Subsection
// Directorate
// OrderStatus
// Status
// Abstract
// Body
// Reference
// Date
// Place

//=========Relations==========
// hasDocument
// hasDepartment
// SubsectionOf
// hasDepartmentField
// hasGOID
// hasDate
// hasReference
// hasBody
// hasAbstract
// hasStatus
// hasOrderStatus
// hasPlace

//Using Ontology as a reference to create the knowledge graph, creating the label and the relations on the run

WITH "file:///GO_DATA.json" AS url
CALL apoc.load.json(url) YIELD value
UNWIND value.items AS item
MERGE (go:GO {GOID: item["Order ID"],lang:item["Language"],subsection:item.Subsection})
MERGE (abstract:Abstract {value:item.Abstract})

MERGE (body:Body {value:item["Body"],goID:replace(item["Order ID"],"_","/") +" "})
MERGE (place:Place {value:item["Place"]})
MERGE(orderStatus:OrderStatus{value:item["Order Status"]})
MERGE (status:Status {value:item["Status"]})
MERGE(department:Department{value:item["Department"]})
MERGE(directorate:Directorate{value:item["Directorate"]})

with item
FOREACH (ref IN item.References |
MERGE (reference:Reference {value:ref})
)
FOREACH (sub IN item.Subsection |
MERGE (subsection:Subsection {value:sub})
)

MERGE (date:Date {date:date(datetime({epochmillis: apoc.date.parse(item["Date"], "ms", "dd-MM-yyyy")})), value: replace(item["Date"],"-"," ")})

WITH item
MATCH (go:GO),
(d:Date)
WHERE go.GOID = item["Order ID"] and d.date = date(datetime({epochmillis: apoc.date.parse(item["Date"], "ms", "dd-MM-yyyy")}))
MERGE (go)-[:hasDate]-(d)
WITH item
MATCH (go:GO),
(abstract:Abstract)
WHERE go.GOID = item["Order ID"] and abstract.value = item.Abstract
MERGE (go)-[:hasAbstract]-(abstract)
WITH item
MATCH (go:GO),
(body:Body)
WHERE go.GOID = item["Order ID"] and body.value = item["Body"]
MERGE (go)-[:hasBody]-(body)
WITH item
MATCH (go:GO),
(place:Place)
WHERE go.GOID = item["Order ID"] and place.value = item["Place"]
MERGE (go)-[:hasPlace]-(place)
WITH item
MATCH (go:GO),
(status:Status)
WHERE go.GOID = item["Order ID"] and status.value = item["Status"]
MERGE (go)-[:hasStatus]-(status)
WITH item
MATCH (go:GO),
(orderStatus:OrderStatus)
WHERE go.GOID = item["Order ID"] and orderStatus.value = item["Order Status"]
MERGE (go)-[:hasOrderStatus]-(orderStatus)
WITH item
MATCH (go:GO),
(department:Department)
WHERE go.GOID = item["Order ID"] and department.value = item["Department"]
MERGE (go)-[:hasDepartment]-(department)
WITH item
MATCH (go:GO),
(directorate:Directorate)
WHERE go.GOID = item["Order ID"] and directorate.value = item["Directorate"]
MERGE (go)-[:hasDirectorate]-(directorate)

WITH item
UNWIND (CASE item.References WHEN [] then ["None"] else item.References end) as refVal
MATCH (go:GO),(ref:Reference)
WHERE go.GOID = item["Order ID"] and ref.value = refVal
MERGE (go)-[:hasReference]-(ref)

//Subsection Relation with GO
MATCH (go:GO),(sub:Subsection)
WHERE sub.value in go.subsection
MERGE (go)-[:hasSubsection]-(sub)


//Remove subsection as it is not required
MATCH (go:GO)
REMOVE go.subsection



//Step2 - Importing the ontology(Not required)

call n10s.graphconfig.init({ handleVocabUris: "IGNORE", classLabel: "Concept"});
CALL n10s.onto.import.fetch("https://raw.githubusercontent.com/SobyDamn/knowledge-base-GO/main/Knowledge-Graph/KGO_Ontology.owl?token=GHSAT0AAAAAABRDCGC5KKMM3T3R545EBZV2YRYZX6A","RDF/XML");



//NOTE: REMOVE THE OLD INDEX

DROP INDEX BodyAndAbstract
//Creating fulltext search
//Fulltext allows to do distance searching of keywords or phrases with the help of the fulltext index and also provides scores

CREATE FULLTEXT INDEX BodyAndAbstract FOR (n:Body|Abstract) ON EACH [n.value]

CREATE FULLTEXT INDEX BodyAndAbstract FOR (n:Abstract|Department|Body|Place|Date|Reference|Subsection) ON EACH [n.value,n.goID]

CREATE FULLTEXT INDEX AllAttributes FOR (n:Abstract|Department|Body|Place|Date|Reference|Subsection) ON EACH [n.value,n.goID]
//Once fulltext search is created, perform text based search easily
//Search Query - "Dr.Jayasankar Prasad continued to hold full additional"
//From DOC - G.O(Rt)No.11/2021U/HEDN
//NOTE: Result must contain above GovID with highest score
//NOTE_TO_SELF: Find better way of querying nodes
CALL db.index.fulltext.queryNodes("BodyAndAbstract", "Dr.Jayasankar Prasad continued to hold full additional") YIELD node, score
MATCH p = (go:GO)-[]-(node)
with go,score
MATCH (go)-[]-(a:Abstract)
RETURN go.GOID,a.value,score
