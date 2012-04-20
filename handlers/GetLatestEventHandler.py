import tornado.web
import tornado
import time
import simplejson as json

class GetLatestEventHandler(tornado.web.RequestHandler):

    schedule_time = 0.2
    current_handle = None

    def initialize(self, **kwargs):
        super(GetLatestEventHandler, self).initialize()
        self.QueueLog = kwargs['QueueLog']

#    @tornado.web.asynchronous
    def get(self):
#        self.schedule_execution(self.schedule_time, self.loop)
#        try:

	import datetime, time
	
	today = int(time.mktime(datetime.date.today().timetuple()))
	
        events = self.QueueLog.select(self.QueueLog.q.time2 > today).orderBy('id')

	total_answered = 0
	finished_by_agent = 0
	finished_by_caller = 0	
	transfered = 0
	unanswered = 0
	abandoned = 0
	timeouted = 0

	lates_event = 0

	for e in events:
	    if e.event == 'CONNECT': total_answered += 1
	    if e.event in ('ABANDON', 'TIMEOUT'): unanswered += 1
	    if e.event == 'COMPLETEAGENT': finished_by_agent += 1
	    if e.event == 'COMPLETECALLER': finished_by_caller += 1
	    if e.event == 'TRANSFER': transfered += 1
	    if e.event == 'ABANDON': abandoned += 1
	    if e.event == 'TIMEOUT': timeouted += 1

	    lates_event = e.id


        #first_event = self.QueueLog.select(self.QueueLog.q.time2 > today).orderBy('id').limit(1)
        #first_event_id = first_event[0].id
	
	#catchup_event = self.QueueLog.select().orderBy('-id').limit(1)
        #catchup_event_id = catchup_event[0].id
#        except:
#            event_id = 0

        self.set_header("Content-Type", 'text/javascript')
        self.write("var last_event = '" + str(lates_event) + "';\n")
#        self.write("var catchup_event = '" + str(catchup_event_id) + "';\n")

	self.write("var total_answered = '" + str(total_answered) + "';\n")
	self.write("var finished_by_agent = '" + str(finished_by_agent) + "';\n") 
	self.write("var finished_by_caller = '" + str(finished_by_caller) + "';\n") 	
	self.write("var transfered = '" + str(transfered) + "';\n") 
	self.write("var unanswered = '" + str(unanswered) + "';\n") 
	self.write("var abandoned = '" + str(abandoned) + "';\n") 
	self.write("var timeouted = '" + str(timeouted) + "';\n") 


#        self.finish()

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

