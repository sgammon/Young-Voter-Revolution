# -*- coding: utf-8 -*-
"""
    handlers
    ~~~~~~~~

    Hello, World!: the simplest tipfy app.

    :copyright: 2009 by tipfy.org.
    :license: BSD, see LICENSE for more details.
"""
import logging, os, config, urllib2
from google.appengine.ext import db
from google.appengine.api import memcache
from apps.yvr.models import FacebookUser, Pledge
from apps.yvr.forms import PledgeLanding
from wtforms.validators import ValidationError

import simplejson as json
from tipfy import RequestHandler, Response, abort
from tipfy.ext.jinja2 import render_response, Jinja2Mixin
from tipfy.ext.auth.facebook import FacebookMixin


def get_pledge_form():
    pass


def get_fb_session(request):
    
    session = request.args.get('session', None)

    if session is not None:
        session_obj = json.loads(session)
                
        u = memcache.get(str(session_obj['session_key']))

        if u is None:
            u = FacebookUser.get_by_key_name(str(session_obj['uid']))

            if u is None:
                u = FacebookUser(key_name=str(session_obj['uid']), uid=str(session_obj['uid']), app_installed=installed).put()
            
            memcache.set(str(session_obj['uid']), u, time=3600)
        
        return session_obj, u

    else:
        abort(403)
        

#### MAIN LANDING
class LandingHandler(RequestHandler):
    def get(self):
        """Simply returns a Response object with an enigmatic salutation."""
        return render_response('landing.html', title='2010 Young Voter Revolution')


#### DEV HANDLER
class DevHandler(RequestHandler):
    def get(self):

        """ Basic dev handler for debugging. """
        return render_response('dev.html', title='Dev Handler', ev=os.environ)
        

#### FACEBOOK INIT
class FacebookInit(RequestHandler, FacebookMixin):

    def head(self, **kwargs):
        """Facebook pings this URL when a user first authorizes your application."""
        return Response('')        

    def get(self):

        if self.request.args.get('session', None):
            logging.debug('FacebookInit: Authenticated. Passing to _on_auth.')
            return self.get_authenticated_user(self._on_auth)
            
        logging.debug('FacebookInit: Not authenticated. Redirecting.')        
        return self.authenticate_redirect(extended_permissions='email,sms')
        
    def _on_auth(self, user):

        if not user:
            abort(403)
            
        logging.debug('OnAuth: Beginning.')
            
        session = self.request.args.get('session', False)
        
        logging.debug('OnAuth: Session = '+str(session))
        
        if session is False:
            abort(403)
        
        else:
            session_obj = json.loads(session)
            
            logging.debug('OnAuth: Decoded session object follows...')
            logging.debug('OnAuth: '+str(session_obj))
            
            u = memcache.get(str(session_obj['session_key']))

            if u is None:
                u = FacebookUser.get_by_key_name(str(session_obj['uid']))
                logging.debug('OnAuth: u 1st round = '+str(u))

            if u is None:
                u = FacebookUser(key_name=str(session_obj['uid']), uid=str(session_obj['uid'])).put()
                logging.debug('OnAuth: u 2nd round = '+str(u))
                
                
            logging.debug('OnAuth: u 3rd round = '+str(u))
            
            logging.debug('OnAuth: UID = '+str(session_obj['uid']))
            logging.debug('OnAuth: KEY = '+str(session_obj['session_key']))
                
            memcache.set(str(session_obj['uid']), u, time=3600)
            
            success_get = self.request.args.get('pledgeSuccess', False)
            
            return render_response('microsite.html', fb_app_id=config.config['tipfy.ext.auth.facebook']['api_key'], pledgeSuccess=success_get, debug=True, pledge_form=PledgeLanding(self.request), dev={'getvars':self.request.args.items(multi=True),'postvars':self.request.form.items(multi=True)})
        

#### FACBEOOK CANVAS
class FacebookCanvas(RequestHandler, FacebookMixin):

    def get(self):

        """ Renders the Facebook app canvas. """

        return render_response('fb-canvas/main.html', fb_app_id=config.config['tipfy.ext.auth.facebook']['api_key'], debug=True, pledge_form=PledgeLanding(self.request), dev={'getvars':self.request.args.items(multi=True),'postvars':self.request.form.items(multi=True)})


    def post(self):
        """ Renders the Facebook app canvas. """
        return self.get()
        

#### FACEBOOK PLEDGE
class FacebookTab(RequestHandler):
    
    def get(self):
        """ Renders the Facebook page tab. """
        s, u = get_fb_session(self.request)
        return render_response('fb-canvas/tab.html', fb_app_id=config.config['tipfy.ext.auth.facebook']['api_key'], debug=True, dev={'getvars':self.request.args.items(multi=True),'postvars':self.request.form.items(multi=True)})
        
    def post(self):
        """ Renders the Facebook page tab. """
        return self.get()
        
    
#### FACEBOOK DEAUTHORIZE
class FacebookDeauthorize(RequestHandler):

    def get(self):
        """ Processes user deauthorizations. """
        return Response('<b>cool</b>')
        

#### ENDPOINT FOR SUBMITTING PLEDGES
class PledgeSubmit(RequestHandler):

    def post(self):
        
        """ Submit and process submitted pledges. """
        form = PledgeLanding(self.request)
        try:
            if form.validate():
                action = str(form.u_action.data)
                u_next_action = str(form.u_nextAction.data)
                u_prev_action = str(form.u_prevAction.data)
                u_key = str(form.u_key.data).strip('=')
                firstname = str(form.firstname.data)
                lastname = str(form.lastname.data)
                email = str(form.email.data)
                phone = str(form.phone.data)
                message = str(form.message.data)
        
        
                if action is not False:
            
                    if u_key is not False:

                        u = db.get(db.Key(u_key))
                        u.firstname = firstname
                        u.lastname = lastname
                        u.email = email
                        u.phone = phone
                        u.has_pledged = True
        
                        p = Pledge(u, user=u, personal_message=message)
                                
                        db.put([u, p])
                
                        if u_next_action is not False:
                            self.redirect(u_next_action)

                    else:
                        abort(404)
                       
                else:
                    abort(400)

        except ValidationError, e:
            self.redirect(self.request.headers.get('referrer')+'&validationError=true&error='+urllib2.urlencode(str(e.message)))
        