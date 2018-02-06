from flask import Flask, render_template
app = Flask(__name__)

@app.route("/")
def hello():
    return render_template("multi_html.html")
@app.route('/<string:page_name>/')
def render_static(page_name):
    return render_template('%s' % page_name)
if __name__ == "__main__":
    app.run()
