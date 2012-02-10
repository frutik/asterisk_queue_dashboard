import tornado.web
import tornado
import time
import simplejson as json
import logging

class GetEventsHandler(tornado.web.RequestHandler):

    schedule_time = 0.2
    delimiter = '|'

    def initialize(self, **kwargs):
        super(GetEventsHandler, self).initialize()
        self.QueueLog = kwargs['QueueLog']
        self.current_handle = None

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

    def _parsed_data(self, keys, data):
        t = data.split(self.delimiter)
        r = {}
        for i,n in enumerate(keys):
            r[n] = t[i]

        return r

    def _abandon_data(self, data):
        return self._parsed_data(['position', 'origposition', 'waittime'], data)

    def _agentlogin_data(self, data):
        return self._parsed_data(['channel',], data)

    def _agentcallbacklogin_data(self, data):
        return self._parsed_data(['exten@context',], data)

    def _agentlogoff_data(self, data):
        return self._parsed_data(['channel', 'logintime',], data)

    def _agentcallbacklogoff_data(self, data):
        return self._parsed_data(['exten@context', 'logintime', 'reason',], data)

    def _completeagent_data(self, data):
        return self._parsed_data(['holdtime', 'calltime', 'origposition',], data)

    def _completecaller_data(self, data):
        return self._parsed_data(['holdtime', 'calltime', 'origposition',], data)

    def _connect_data(self, data):
        return self._parsed_data(['holdtime', 'bridgedchanneluniqueid',], data)

    def _enterqueue_data(self, data):
        return self._parsed_data(['url', 'callerid',], data)

    def _exitempty_data(self, data):
        return self._parsed_data(['position', 'origposition', 'waittime',], data)

    def _exitwithkey_data(self, data):
        return self._parsed_data(['key', 'position',], data)

    def _exitwithtimeout_data(self, data):
        return self._parsed_data(['position',], data)

    def _ringnoanswer_data(self, data):
        return self._parsed_data(['ringtime',], data)

    def _transfer_data(self, data):
        return self._parsed_data(['extension', 'context', 'holdtime', 'calltime',], data)

    def on_connection_close(self):
        #TODO: Check if call to parent class needed.
        tornado.ioloop.IOLoop.instance().remove_timeout(self.handle)
