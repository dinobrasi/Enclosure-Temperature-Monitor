from flask import Flask, render_template

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

@app.route('/')
def index():
    f = open("/home/tim/Documents/www/templates/index.html", "r")
    return f.read()
    #return render_template("index.html")

if __name__ == '__main__':
    app.run(debug=False, host='192.168.1.241', port=80)