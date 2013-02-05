import os
import sys
import urlparse
import collections
import datetime

from flask import Flask, render_template, url_for, abort
from flask_frozen import Freezer
from werkzeug import cached_property
from werkzeug.contrib.atom import AtomFeed
import markdown
import yaml


class SortedDict(collections.MutableMapping):
    def __init__(self, items=[], key=None, reverse=False):
        self._items = {}
        self._keys = []
        if key:
            self._key_fn = lambda k: key(self._items[k])
        else:
            self._key_fn = lambda k: self._items[k]
        self._reverse = reverse

        self.update(items)

    def __getitem__(self, key):
        return self._items[key]

    def __setitem__(self, key, value):
        self._items[key] = value
        self._keys.append(key)
        self._keys.sort(key=self._key_fn, reverse=self._reverse)

    def __delitem__(self, key):
        self._items.pop(key)
        self._keys.remove(key)

    def __len__(self):
        return len(self._keys)

    def __iter__(self):
        for key in self._keys:
            yield key

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, self._items)


class Blog(object):
    def __init__(self, app, root_dir=None, file_ext='.md'):
        self.root_dir = root_dir or app.root_path
        self.file_ext = file_ext
        self._app = app
        self._cache = SortedDict(key=lambda p: p.date, reverse=True)
        self._initialize_cache()

    @property
    def posts(self):
        return self._cache.values()

    def get_post_or_404(self, path):
        """
        Returns the Post object at path or raises a NotFound error
        """
        # Grab the post from the cache
        post = self._cache.get(path, None)

        # If the post isn't cached (or DEBUG), create a new Post object
        if not post:
            filepath = os.path.join(self.root_dir, path + self.file_ext)
            if not os.path.isfile(filepath):
                abort(404)
            post = Post(filepath, root_dir=self.root_dir)
            self._cache[post.urlpath] = post

        return post

    def _initialize_cache(self):
        """
        Walks the root directory and adds all posts to the cache dict
        """
        for (root, dirpaths, filepaths) in os.walk(self.root_dir):
            for filepath in filepaths:
                filename, ext = os.path.splitext(filepath)
                if ext == self.file_ext:
                    path = os.path.join(root, filepath).replace(self.root_dir, '')
                    post = Post(path, root_dir=self.root_dir)
                    self._cache[post.urlpath] = post


class Post(object):
    def __init__(self, path, root_dir=''):
        self.urlpath = os.path.splitext(path.strip('/'))[0]
        self.filepath = os.path.join(root_dir, path.strip('/'))
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

DOMAIN = 'myawesomeblog.com'

app = Flask(__name__)
freezer = Freezer(app)
blog = Blog(app, root_dir='posts')


# Custom Jinja Filter
@app.template_filter('date')
def format_date(value, format='%B %d, %Y'):
    return value.strftime(format)


# Routes
@app.route('/')
def index():
    return render_template('index.html', posts=blog.posts)


@app.route('/blog/<path:path>/')
def post(path):
    post = blog.get_post_or_404(path)
    return render_template('post.html', post=post)

@app.route('/feed.atom')
def feed():
    feed = AtomFeed('My Awesome Blog',
        feed_url='http://%s/%s/' % (DOMAIN, 'feed.atom'),
        url='http://%s' % DOMAIN,
        updated=datetime.datetime.now())
    for post in blog.posts[:10]: # Just show the last 10 posts
        try:
            post_title = '%s: %s' % (post.title, post.subtitle)
        except AttributeError:
            post_title = post.title
        post_url = 'http://%s/%s/%s' % (DOMAIN, 'blog', post.url)

        feed.add(
            title=post_title,
            content=unicode(post.html),  # this could be a summary for the post
            content_type='html',
            author='Christopher Roach',
            url=post_url,
            updated=post.date,  # published is optional, updated is not
            published=post.date)
    return feed.get_response()


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'build':
        freezer.freeze()
    else:
        app.run(port=8000, debug=True)
