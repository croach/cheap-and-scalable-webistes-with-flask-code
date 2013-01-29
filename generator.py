from flask import Flask, render_template
app = Flask(__name__)

@app.route('/blog')
def post():
    return render_template('post.html')


if __name__ == '__main__':
    app.run(port=8000)
