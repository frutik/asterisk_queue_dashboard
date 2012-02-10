import tornado.web
import tornado
import time
import simplejson as json
import logging

class GetEventsHandler(tornado.web.RequestHandler):

    schedule_time = 0.2
    current_handle = None

    def initialize(self, **kwargs):
        super(GetEventsHandler, self).initialize()
        self.QueueLog = kwargs['QueueLog']

    @tornado.web.asynchronous
    def get(self, last_event_id):
        self.last_event_id = int(last_event_id)
        self.schedule_execution(self.schedule_time, self.loop)

    def schedule_execution(self, schedule_time, callback):
        self.handle = tornado.ioloop.IOLoop.instance().add_timeout(time.time() + schedule_time, callback)

    def loop(self):
        tornado.ioloop.IOLoop.instance().remove_timeout(self.handle)

        logging.info('long poll tick')

        try:
            events = self.QueueLog.select(self.QueueLog.q.id > self.last_event_id).orderBy('id').limit(1)
    	    event = events[0]

        except IndexError:
            self.schedule_execution(self.schedule_time, self.loop)
            return

        e = {
            'id': event.id,
            'time': event.time,
            'callid': event.callid.replace('.', ''),
            'queuename': event.queuename,
            'agent': event.agent.replace('SIP/', ''),
            'event': event.event
            }

        try:
            de = getattr(self, '_' + event.event.lower() + '_data')(event.data)

        except:
            pass

        else:
            e.update(de)

        ev = json.dumps(e)
        
        print ev

    	self.set_header("Content-Type", 'application/json')
        self.write(ev)

        self.finish()

    def _completeagent_data(self, data):
        return {}

    def _completecaller_data(self, data):
        return {}

    def _abandon_data(self, data):
        return {
            'test':'test'
        }

    def on_connection_close(self):
        #TODO: Check if call to parent class needed.
        tornado.ioloop.IOLoop.instance().remove_timeout(self.handle)
