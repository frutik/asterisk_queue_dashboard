import tornado.web
import tornado
import time
import simplejson as json

#from sqlobject import *

#class QueueLog(SQLObject):
#    time = StringCol()
#
#    callid = StringCol()
#    queuename = StringCol()
#    agent = StringCol()
#    event = StringCol()
#    data = StringCol()

class GetLatestEventsHandler(tornado.web.RequestHandler):

    schedule_time = 0.2
    current_handle = None

    @tornado.web.asynchronous
    def get(self):
        self.last_event_id = int(last_event_id)
        self.schedule_execution(self.schedule_time, self.loop)

    def schedule_execution(self, schedule_time, callback):
        self.handle = tornado.ioloop.IOLoop.instance().add_timeout(time.time() + schedule_time, callback)

    def loop(self):
        tornado.ioloop.IOLoop.instance().remove_timeout(self.handle)
	
        try:
            events = QueueLog.select().orderBy('-id').limit(1)
            event_id = events[0].id

        except:
            event_id = 0
            return

        self.set_header("Content-Type", 'text/javascript')
        self.write("var last_event = '" + str(event_id) + "';")

        self.finish()

