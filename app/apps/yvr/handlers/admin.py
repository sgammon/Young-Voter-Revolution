from apps.yvr.models import *

from google.appengine.ext import db

from apps.yvr import models

from tipfy import RequestHandler, Response, abort, redirect
from tipfy.ext.jinja2 import render_response, Jinja2Mixin

from tipfy.ext.wtforms import fields
from wtforms.ext.appengine.db import model_form


class Index(RequestHandler):
    pass


class View(RequestHandler):

    def get(self, key):
        
        _m = db.get(db.Key(key))
        if _m is not None:
            form = model_form(_m,exclude=_m.FORM_EXCLUDE)
            form.submit = fields.SubmitField()
            if self.request.args.get('edit', False):
                editform = True
            else:
                editform = False
        
        return render_response('admin/crud-view.html', object=_m, form=form(self.request.form, obj=_m), editform=editform)
        
    def post(self):
        pass
    

class List(RequestHandler):
    
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
                    n_offset = len(type_r)+self.request.arge.get('offset')
                else:
                    n_offset = len(type_r)
            else:
                n_link = False
                n_offset = 0

            return render_response('admin/crud-list.html', type=type, records=type_r, previous_link=p_link, previous_offset=p_offset, next_link=n_link, next_offset=n_offset)
                
            
        except ImportError, e:
            return abort(404)
            
        
    def post(self):
        pass
        
        
class Create(RequestHandler):
    
    def get(self, type):
        pass
        
    def post(self):
        pass
        
        
class Delete(RequestHandler):
    
    def get(self, key):
        pass
        
    def post(self):
        pass