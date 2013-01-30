import os

from flask import Flask, render_template
from werkzeug import cached_property
import markdown


class Post(object):
    def __init__(self, path):
        self.path = path

    @cached_property
    def html(self):
        with open(self.path, 'r') as fin:
            content = fin.read().strip()
        return markdown.markdown(content)

app = Flask(__name__)

@app.route('/blog/<path:path>')
def post(path):
    path = os.path.join('posts', path + '.md')
    post = Post(path)
    return render_template('post.html', post=post)


if __name__ == '__main__':
    app.run(port=8000, debug=True)
