from bottle import hook, response, route, run, static_file, request, template, get
from Bio import SeqIO, SwissProt
import urllib
import re
import json
import socket
import os

#These lines are needed for avoiding the "Access-Control-Allow-Origin" errors
@hook('after_request')
def enable_cors():
    response.headers['Access-Control-Allow-Origin'] = '*'

@route('/<filename:path>')
def send_static(filename):
    return static_file(filename, root='static/')
#Note that the text on the route decorator is the name of the resource
# and the name of the function which answers the request could have any name
@route('/')
def index():
    return template("index.html")

@route('/about')
def about():
    return template("about.html")

@route('/guide')
def guide():
    return template("guide.html")

#If you have to send parameters, the right sintax is as calling the resoure
# with a kind of path, with the parameters separed with slash ( / ) and they 
# MUST to be written inside the lesser/greater than signs  ( <parameter_name> ) 
@route('/getData', method="POST")
def getData():
    keyword = request.params.get('keyword')
    result = {}
    motif = []
    #---------- if identifier is inputed, then get the sequance from UniProt with it -------

    if keyword:
        url = "http://www.uniprot.org/uniprot/" + keyword + ".xml"
        try:
            handle = urllib.request.urlopen(url)
            record = SeqIO.read(handle, "uniprot-xml")
            data = record
            error = None

        #--------- search motifs according to the pattern (reqular expression) -------
            seqSource = str(record.seq)
            motifSre = re.findall(r'[ILV]Q...[RK]...[RK]', seqSource)
            
        #---------- find the position of motifs in the sequance ------------
            for mtf in motifSre:
                motifPosition = seqSource.find(mtf)
                start = motifPosition + 1
                end = motifPosition + len(mtf)
                motif.append({'name': mtf, 'start': start, 'end': end})
            
        #-------- if identifier is invalid, then show warning to the user ----------

        except Exception as e:
            data = []
            error = "Please try again with a valid identifier"
            result = {}
            seqSource = ""

        #--------- when all the process finished, then show the result to the user ---------

        context = {'data': seqSource, "keyword" : keyword, "result": result, "motif": motif, "error": error}
    else:
        context = {'data': "", "error": "Please input your identifiers"}
    # context = {'data': seqSource}
    return json.dumps(context)

#To send a favicon to a webpage use this below
@route('/favicon.ico')
def favicon():
    return static_file('windowIcon.ico', root="C:/folder/images", mimetype="image/ico")


if os.environ.get('APP_LOCATION') == 'heroku':
    run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
else:
    run(host='localhost', port=8000, debug=True)