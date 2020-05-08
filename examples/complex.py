from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

from zoo import api

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)

api.init_app(app)

app.run(debug=True)
