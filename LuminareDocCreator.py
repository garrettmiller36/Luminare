# Luminare Doc Creator
import sys, os, requests
from markdown import markdown

# Section for asking for which document
if len(sys.argv) < 2:
    print('Usage: [account] - ')
    sys.exit()
account = sys.argv[1]
print('You have chosen to open docuement %s' % account)

account == 'test3'
Header = input("Enter the header: ")
Date = input("Please enter the paragraph: ")
Quick = input("Please enter Quick: ")

# Calling that document from github in markdown format
url = "https://raw.githubusercontent.com/garrettmiller36/Luminare/master"
fullurl = url + '/' + account +  '.txt'
rawtext = requests.get(fullurl)

# Request pulls a raw text file that is written in markdown form
# Now need to decode in order to search for the terms to change


decodedtext = []
for line in rawtext:
    decodedtext.append(line.decode("utf-8"))
# Decoded text


# Next section is searching for the terms to replace and replacing them

editedtext = []
 
for line in decodedtext:
    editedtext.append(line.replace('Header',Header).replace("paragraph",Date).replace("header",Header).replace("Quick,",Quick))
encodedtext = []

# Encoding the lines in order to convert it to markdwon format

for line in editedtext:
    encodedtext.append(str.encode(line))

# Opening a blank markdown file and writing the files to it


markdownfile = open('TestOutput.md','wb')
for i in encodedtext:
    markdownfile.write(i)
markdownfile.close()


pathtomarkdown = os.path.join(os.getcwd(),'TestOutput.md')

# Opening HTML file and converting the markdown file to html

with open(pathtomarkdown, 'r') as htmlfile:
     html_text = markdown(htmlfile.read(),output_format = 'html4')
htmlname = account + '.hthml'

htmlfile = open('htmlname','w')
htmlfile.write(html_text)
htmlfile.close()
