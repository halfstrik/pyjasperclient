# -*- coding: utf-8 -*-

import os
os.chdir(u'C:\\Users\\Сергей\\Projects\\pyjasperclient\\pyjasperclient')
import sys, uuid
sys.path.append(u'C:\\Users\\Сергей\\Projects\\pyjasperclient\\pyjasperclient')
from jasperclient import *
url = 'http://localhost:8080/jasperserver/services/repository'
j = JasperClient(url,'jasperadmin','jasperadmin')
##resp = j.putRaw(label="pipeslabel",
##               description="pipecdescr", 
##            name="pipec",
##	       uriString="/pipec",
##	       isNew="false",
##	       resourceProperties={"PROP_PARENT_FOLDER":"/"})

imageFile = open('imageFile.png','rb')
imageData = imageFile.read()
mimeType = 'image/png'
binaryParam = (imageData, uuid.uuid4(), mimeType)

resp = j.putWithAttachment(binaryParam,
                           label="ImAgElabel",
                           description="ImaGeDescr",
                           name="imageNameTest",
                           uriString="/pipec/imageNameTest",
                           isNew="false",
                           wsType="img",
                           resourceProperties={"PROP_PARENT_FOLDER":"/pipec",
                                               "PROP_HAS_DATA":"true"})

print resp                             
