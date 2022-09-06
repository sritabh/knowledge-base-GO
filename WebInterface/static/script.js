function showDocFile(fileUrl){
    console.log(fileUrl);
    //Display documment in doc area
    var docAreaElement = document.getElementById("docViewerArea");
    docAreaElement.style.display = "block";
    docAreaElement.innerHTML = `<iframe src="${fileUrl}" width="100%" height="900px"></iframe>`;
    console.log(filename)
}