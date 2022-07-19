from flask import Flask
import sys
from census.logger import logging
from census.exception import CensusException

app = Flask(__name__)

@app.route('/',methods=['GET','POST'])

def index():
    try:
        raise Exception("We are testing custom exception")
    except Exception as e:
        census=CensusException(e,sys) from e
    logging.info("We are testing logging module")
    return"CICD pipeline has been created"
if __name__=="__main__":
    app.run(debug=True)