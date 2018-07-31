import flask                                                                     
from flask import  Flask                                                         
from flask import json                                                           
from flask import jsonify                                                        
from flask import render_template
from SSOT import SSOT

app = Flask(__name__)

@app.route('/')                                                                  
def home():                                                                      
    return render_template('index.html')                                         
                                                                                 
@app.route('/ssot')                                                              
def ssot():                                                                      
    return jsonify(SSOT.transactions)                                            
                                                                                 
@app.route('/fuzzyreference')                                                    
@app.route('/fuzzyreference/<reference>')                                        
def fuzzy_reference(reference=None):                                             
    mySSOT = SSOT()
    mySSOT.fetchTransactions()
    reference = flask.request.args['reference']
    result = json.dumps(mySSOT.filterby(reference=reference), sort_keys=True, indent=4, separators=(',', ': '))
    return render_template('index.html', result=result)                          
                                                                                 
@app.route('/fuzzymatch')                                                        
def ssot_fuzzy():                                                                
    mySSOT = SSOT()
    mySSOT.fetchTransactions()
    result = json.dumps(mySSOT.fuzzygroup(), sort_keys=True, indent=4, separators=(',', ': '))
    return render_template('index.html', result=result)                          
                                                                                 
@app.route('/source')                                                            
@app.route('/source/<source>')                                                   
def source(source=None):
    mySSOT = SSOT()
    mySSOT.fetchTransactions()
    result = json.dumps(mySSOT.filterby(source_gateway=source, sort_keys=True, indent=4, separators=(',', ': ')))
    return render_template('index.html', result=result)
