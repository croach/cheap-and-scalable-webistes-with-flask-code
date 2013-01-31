import os
import urlparse

from flask import Flask, render_template
from werkzeug import cached_property
import markdown
import yaml

class Post(object):
    def __init__(self, path, root='', base_url=None):
        self.urlpath = os.path.splitext(path.strip('/'))[0]
        self.filepath = os.path.join(root, path.strip('/'))
        self.base_url = base_url
        self._initialize_metadata()

    @cached_property
    def html(self):
        with open(self.filepath, 'r') as fin:
            content = fin.read().split('\n\n', 1)[1].strip()
        return markdown.markdown(content)

    @cached_property
    def url(self):
        # If a base URL was given, join the base with the urlpath
        if self.base_url:
            return urlparse.urljoin(self.base_url, self.urlpath)
        return self.urlpath

    def _initialize_metadata(self):
        content = ''
        with open(self.filepath, 'r') as fin:
            for line in fin:
                if not line.strip():
                    break
                content += line
        self.__dict__.update(yaml.load(content))


app = Flask(__name__)

# Custom Jinja Filter
@app.template_filter('date')
def format_date(value, format='%B %d, %Y'):
    return value.strftime(format)

# Routes
@app.route('/blog/<path:path>')
def post(path):
    path = os.path.join('posts', path + '.md')
    post = Post(path)
    return render_template('post.html', post=post)


if __name__ == '__main__':
    app.run(port=8000, debug=True)
