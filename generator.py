import os
import urlparse

from flask import Flask, render_template, url_for
from werkzeug import cached_property
import markdown
import yaml

class Post(object):
    def __init__(self, path, root=''):
        self.urlpath = os.path.splitext(path.strip('/'))[0]
        self.filepath = os.path.join(root, path.strip('/'))
        self._initialize_metadata()

    @cached_property
    def html(self):
        with open(self.filepath, 'r') as fin:
            content = fin.read().split('\n\n', 1)[1].strip()
        return markdown.markdown(content)

    @cached_property
    def url(self):
        return url_for('post', path=self.urlpath)

    def _initialize_metadata(self):
        content = ''
        with open(self.filepath, 'r') as fin:
            for line in fin:
                if not line.strip():
                    break
                content += line
        self.__dict__.update(yaml.load(content))


app = Flask(__name__)

@app.template_filter('date')
def format_date(value, format='%B %d, %Y'):
    return value.strftime(format)

@app.route('/blog/<path:path>')
def post(path):
    path = os.path.join('posts', path + '.md')
    post = Post(path)
    return render_template('post.html', post=post)


if __name__ == '__main__':
    app.run(port=8000, debug=True)
