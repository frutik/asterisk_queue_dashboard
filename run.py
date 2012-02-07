import tornado.ioloop
import tornado.web

from tornado.options import define, options

from handlers.GetEventsHandler import GetEventsHandler

import os.path
import uuid

import ConfigParser

config = ConfigParser.ConfigParser()
config.read('config.ini')

from sqlobject import *
connection = connectionForURI(config.get('SQL', 'dsn'))
sqlhub.processConnection = connection

http_settings = dict(
    cookie_secret=str(uuid.uuid1()),
    template_path=os.path.join(os.path.dirname(__file__), "templates"),
    static_path=os.path.join(os.path.dirname(__file__), "static"),
    xsrf_cookies=False,
    autoescape="xhtml_escape",
)

define("port", default=8889, help="run on the given port", type=int)

import logging
logging.basicConfig(level=logging.INFO)

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r'/getevents/([0-9]+)', GetEventsHandler),
        ]
        tornado.web.Application.__init__(self, handlers, http_settings)

def main():
    tornado.options.parse_command_line()
    app = Application()
    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
