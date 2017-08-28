import os

def createTXTfilefromPDF(_txt_file ,_pdf_file):
    file = open(_txt_file, 'wb')
    for line in open(_pdf_file, 'rb').readlines():
        file.write(line)
    file.close()


def createPDFfilefromTXT(_pdf_file, _txt_file):
    file = open(_pdf_file, 'wb')
    for line in open(_txt_file, 'rb').readlines():
        file.write(line)
    file.close()

os.remove('test-pdf.txt')
os.remove('prueba.pdf')

createTXTfilefromPDF('test-pdf.txt','/Users/aitorcalero/Documents/Luciad-White-Paper-GIS-Databases.pdf')

createPDFfilefromTXT('prueba.pdf','test-pdf.txt')
