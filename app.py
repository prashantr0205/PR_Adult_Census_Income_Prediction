from flask import Flask


app=Flask(__name__)


@app.route('/',methods=['GET','POST'])


def index():
    return "Starting PR_Adult_Income_Prediction_Project"


if __name__=="__main__":
    app.run(debug=True)





