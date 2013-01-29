from flask import Flask
app = Flask(__name__)
# The creation of the app object does things like:
#   - sets up path information (root, templates, static, etc.)
#   - sets the config
#       - Two ways to do this:
#           1) Through a config file - app.config.from_pyfile('settings.cfg')
#               - You can also use app.config.from_envar('SETTINGS_FILE')
#                 to point to a file containing your config settings
#           2) Through a python module - app.config.from_object(__name__)
#       - In either case, only upper case attributes are added to the config

@app.route('/')
def hello():
    return 'Hello, World!'


if __name__ == '__main__':
    app.run(port=8000)
    # Runs the app
    # Important options:
    #   - host: set to '0.0.0.0' to make it available externally, default to '127.0.0.1'
    #   - port: defaults to 5000
    #   - debug: Set to true to auto restart after a change
