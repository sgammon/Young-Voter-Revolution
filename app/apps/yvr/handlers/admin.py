from apps.yvr.models import *

from google.appengine.ext import db
from google.appengine.ext import deferred
from google.appengine.api import memcache
from google.appengine.api.labs import taskqueue

from apps.yvr import models
from apps.yvr.forms import SendTextForm

from . import YVRRequestHandler

from tipfy import RequestHandler, Response, abort, redirect
from tipfy.ext.jinja2 import render_response, Jinja2Mixin

from tipfy.ext.wtforms import fields
from wtforms.ext.appengine.db import model_form

import twilio


ACCOUNT_SID = 'AC8cb910ac2bc06ed184232be22bca8cf2'
ACCOUNT_TOKEN = 'e3eddb2fcb7ba2f9c63f7390f6751626'
CALLER_ID = '+14155992671'
API_VERSION = '2010-04-01'


class Index(YVRRequestHandler):
    
    def get(self):
        
        model_groups = {}
        for model in models.models_list:
            
            q = model.all()
            c = q.count()
            
            if c > 5:
                fold_model_list = True
            else:
                fold_model_list = False
                
            data = q.fetch(5)
            
            model_groups[model.kind()] = {'fold':fold_model_list, 'data':data, 'count':c}
            
        
        return self.render('admin/crud-admin.html', model_groups=model_groups)


class View(YVRRequestHandler):

    def get(self, key):
        
        _m = db.get(db.Key(key))
        if _m is not None:
            form = model_form(_m,exclude=_m.FORM_EXCLUDE)
            form.submit = fields.SubmitField()
            if self.request.args.get('edit', False):
                editform = True
            else:
                editform = False
        
        return self.render('admin/crud-view.html', object=_m, form=form(self.request.form, obj=_m), editform=editform)
        
    def post(self):
        pass
    

class List(YVRRequestHandler):
    
    def get(self, type):

        try:
            type_o = getattr(models, type)

            type_q = type_o().all()
            if self.request.args.get('offset', False):
                p_link = True
                if int(self.request.args.get('offset')) < 26:
                    p_offset = 0
                else:
                    p_offset = int(self.request.args.get('offset')) - 25
                    
                type_q.offset(int(self.request.args.get('offset')))
            else:
                p_link = False
                p_offset = 0
            
            type_r = type_q.fetch(26)
            if len(type_r) > 25:
                n_link = True
                if self.request.args.get('offset', False):
                    n_offset = len(type_r)+self.request.args.get('offset')
                else:
                    n_offset = len(type_r)
            else:
                n_link = False
                n_offset = 0

            return self.render('admin/crud-list.html', type=type, records=type_r, previous_link=p_link, previous_offset=p_offset, next_link=n_link, next_offset=n_offset)
                
            
        except ImportError, e:
            return abort(404)
            
        
    def post(self):
        pass
        
        
class Create(YVRRequestHandler):
    
    def get(self, type):
        pass
        
    def post(self):
        pass
        
        
class Delete(YVRRequestHandler):
    
    def get(self, key):
        pass
        
    def post(self):
        pass
        
        
def split_and_add_sms_tasks(d_list_key, message):

    d_list = memcache.get('sms-send-list')
    if d_list is None:
        d_list = db.get(db.Key(d_list_key))
    
    tasks = []
    
    for item in d_list.users:
        
        p = {'number': item.user.phone, 'message': message, 'action': 'send'}
        t = taskqueue.Task(url='/manage/send', params=p)
        tasks.append(t)
        
    logging.info('Splitting tasks to tasks list: '+str(tasks))
    
    q = taskqueue.Queue(name='outbound-sms')
    q.add(tasks)
    
    logging.info('Added tasks. Deferred library success.')
    
    return True
        
        
class SendText(YVRRequestHandler):
    
    def get(self):
        
        form = SendTextForm(self.request)

        return self.render('admin/sendtext.html', form=form)
        
        
    def post(self):

        action = self.request.form.get('action', False)
        if action  == False:
            abort(400)
            return Response('<b>No form action specified</b>')
            
        else:
            
            if action == 'submit':

                form = SendTextForm(self.request)

                ## Grab form values
                dest_list = form.dest_list.data
                message = form.message.data

                dest_list = db.Key(dest_list)
                
                memcache.delete('sms-send-list')
                memcache.set('sms-send-list', db.get(dest_list))

                deferred.defer(split_and_add_sms_tasks, dest_list, message)

            elif action == 'send':
                
                dest_number = self.request.form.get('number', False)
                message = self.request.form.get('message', False)
            
                account = twilio.Account(ACCOUNT_SID, ACCOUNT_TOKEN)
        
                d = {
                    'From' : CALLER_ID,
                    'To' : dest_number,
                    'Body' : message,
                }
                try:
                    response = account.request('/%s/Accounts/%s/SMS/Messages.json' % \
                                              (API_VERSION, ACCOUNT_SID), 'POST', d)
                                  
                    response_obj = json.loads(response)
        
                    logging.info('TW Response: '+str(response))
                    logging.info('SMS send successful.')
        
                    return Response('<b>A-OK (Send Successful)</b>')
                except Exception, e:
                    logging.error('Exception encountered.')
                    raise e                