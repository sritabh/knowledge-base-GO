# Govt Order Knowledge Graph

This project leverages **Graph Databases** to store and manage government notices issued by the **Government of Kerala**. It provides a platform for **efficient retrieval** of notices based on user queries.  

### Key Features  
- **Semantic Search** – Retrieves results based on the meaning of the query rather than simple keyword matching.  
- **Knowledge-Based Search** – Utilizes structured datasets to enhance accuracy.  
- **Comprehensive Results** – Returns all relevant documents along with their corresponding hyperlinks.  

This approach ensures more **precise and contextually relevant** search results, improving access to official notices.


## Ontology
![Ontology](img/KGO_Ontology.png)

## Stage 1: Information Extraction
Stage 1 is divided into the following steps:-
- Extracting the text from scanned pdf documents.<br>
- Using the pattern in the document/textual data, writing regular expression for extracting the relevant sections from the document separately.<br>
- Severance of the extracted information into more meaningful entity.<br>
  
<div style="width:50%">

![Stage 1-1](/img/stage-1-1.png)
![Stage 1-2](/img/stage-1-2.png)

</div>

## Stage 2: Creation of knowledge graph
- Preparing the extracted json data for import.
- Mapping the data on the ontology.

### Imported Data

- Unmapped

![Unmapped](/img/Data-unmapped.png)
<br>
- Mapped to ontology

![Mapped](/img/data-mapped.png)

### Classes Defined
![Classes](/img/classes.png)

### Relations
![Relations](/img/relations.png)

## Stage 3: Web Interface for querying knowledge graph
- Connection with graph database and defining different queries on graph database.
- Using flask to create web interface and display result based on user search query. 

![Relations](/img/stage-3.png)


## Web Interface

![Interface](/img/web-interface.png)
