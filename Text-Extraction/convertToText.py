"""
Input file contains scanned pdf documents
Output file contains extracted text

Input files at location: {pwd}/input/{input_file}
Output files at location: {pwd}/output/{output_file}
"""

import pytesseract
from PIL import Image
from pdf2image import convert_from_path
import os
#malayalam to english
# from googletrans import Translator
import translators as ts

input_files = os.listdir('Text-Extraction/malayalam_files') #input folder containing pdf files

for file in input_files:
    file_name = file.split('.')[0] #Name of the file without extension i.e. splitting about '.'
    f = open('Text-Extraction/malayalam_output/'+file_name+'.txt', 'a') #Open(Create) the output file in append mode(If the pdf file has more than one page, text would be appended to the single file)

    print("Converting File: ",file_name) #Print the name of the file being converted

    pages = convert_from_path('Text-Extraction/malayalam_files/'+file, 500)
    for page in pages:
        page.save('temp.png', 'PNG') #Saving the file as png
        text = pytesseract.image_to_string(Image.open('temp.png'),lang='mal') #Extracting text from the image

        f.write(text) #Writing the text to the file
    
    print("Converted File: ",file_name)
    #Print output location
    print("Output Location: output/"+file_name+"_mal.txt")
    f.close()
    print("--------------------------------------------------------------------------------")


# f = open('Text-Extraction/malyalam_output/file_mal.txt','r') #Open(Create) the output file in append mode(If the pdf file has more than one page, text would be appended to the single file)
# text = pytesseract.image_to_string(Image.open('temp.png'),lang='mal') #Extracting text from the image
# print("Done!")
# f.write(text) #Writing the text to the file
# f.seek(0)




"""# print("Translating to English")
# #Translation Process

content = f.read()
result = ts.google(content,reset_host_url="https://translate.google.co.in") #translator.translate(content, src='ml', dest='en')
#Save the file with name file_eng.txt
f_eng = open('Text-Extraction/malyalam_output/file_eng.txt','w')

#Join the result list as string
print(result)
f_eng.write("".join(result))
f_eng.close()

print("Translated text saved!")"""
