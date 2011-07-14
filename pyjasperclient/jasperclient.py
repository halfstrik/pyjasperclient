"""
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
try:
    from xml.etree import ElementTree as ET
except ImportError, e:
    from elementtree import ElementTree as ET
from suds.client import Client
import email,re

class JasperClient:
    def __init__(self,url,username,password):
        self.client = Client(url,username=username,password=password)

    def listReportsRaw(self,dir=""):
        ''' perform "list" request to JasperServer WS
            and return xml result as is '''
        req = createRequest(
            uriString=dir, 
            wsType="folder", 
            operationName="list")
        return self.client.service.list(req)
    
    def listReports(self,dir=""):
        """ get a list containing report URIs on JasperServer
        optional dir param shows the directory to list in JasperServer
        """
        res = listReportsRaw(dir)
        reports = []
        for rd in ET.fromstring(res).findall('resourceDescriptor'):
            if rd.get('wsType') == 'reportUnit':
                report = {}
                report['id'] = rd.get('uriString')
                for infotag in ['label','description']:
                    try:
                        report[infotag] = rd.find(infotag).text
                    except AttributeError, e:
                        report[infotag] = None
                reports.append(report)
        return reports

    def putRaw(self):
        pass
    
    def runReport(self,uri,output="PDF",params={}):
        """ uri should be report URI on JasperServer
            output may be PDF, JRPRINT, HTML, XLS, XML, CSV and RTF; default PDF
                but JRPRINT is useless, so don't use it
            params may contain parameters as a simple dict for passing to the report
            this method will return a dict containing 'content-type' and 'data'.
        """
        self.client.set_options(retxml=True) # suds does not parse MIME encoded so we cancel it
        req = createRequest(
            arguments={"RUN_OUTPUT_FORMAT" : output},
            uriString = uri,
            wsType = "reportUnit",
            operationName="runReport",
            params=params)
        res = self.client.service.runReport(req)
        self.client.set_options(retxml=False) # temporarily of course
        res = parseMultipart(res)
        return res

def createRequest(**kwargs):
    r = ET.Element("request")
    r.set("operationName",kwargs.get("operationName", "list"))
    r.set("locale",fwargs.get("locale","en"))
    for argName,argValue in kwargs.get("arguments",{}).items():
        ar = ET.SubElement(r,"argument")
        ar.set("name",argName)
        ar.text = argValue
    rd = ET.SubElement(r,"resourceDescriptor")
    rd.set("name",kwargs.get("name",""))
    rd.set("wsType",kwargs.get("wsType","folder"))
    rd.set("uriString",kwargs.get("uriString",""))
    rd.set("isNew",kwargs.get("isNew","false"))
    l = ET.SubElement(rd,"label")
    l.text = kwargs.get("label","null")
    d = ET.SubElement(rd,"description")
    d.text = kwargs.get("description","null")
    for propname,propval in kwargs.get("resourceProperties",{}).items():
        prop = ET.SubElement(rd,"resourceProperty")
        prop.set("name",propname)
        prop.set("value",propval)
    for pname,pval in kwargs.get("params",{}).items():
        if type(pval) in (list,tuple):
            for aval in pval:
                p = ET.SubElement(rd,"parameter")
                p.set("name",pname)
                p.set("isListItem","true")
                p.text = aval
        else:
            p = ET.SubElement(rd,"parameter")
            p.set("name",pname)
            p.text = pval
    return ET.tostring(r)

def parseMultipart(res):
    boundary = re.search(r'----=[^\r\n]*',res).group()
    res = " \n"+res
    res = "Content-Type: multipart/alternative; boundary=%s\n%s" % (boundary, res)
    message = email.message_from_string(res)
    attachment = message.get_payload()[1]
    return {'content-type': attachment.get_content_type(), 'data': attachment.get_payload()}

if __name__ == "__main__":
    url = 'http://localhost:8080/jasperserver/services/repository?wsdl'
    j = JasperClient(url,'jasperadmin','jasperadmin')
    a = j.runReport('/reports/samples/AllAccounts',"PDF")
    f = file('AllAccounts.pdf','w')
    f.write(a['data'])
    f.close()
