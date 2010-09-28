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
from google.appengine.api import memcache, mail
from google.appengine.api.labs import taskqueue
from apps.yvr.models import FacebookUser, Pledge
from apps.yvr.forms import PledgeLanding, EmailInvites
from wtforms.validators import ValidationError

import simplejson as json
from tipfy import RequestHandler, Response, abort, redirect
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
        
    def _on_auth(self, user=None):
        
        logging.info('User == '+str(user))
        
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
            
            if isinstance(u, db.Key):
                u_key_val = str(u)
            elif isinstance(u, db.Model):
                u_key_val = str(u.key())
            
            
            page_content_vars = {
            
                #'invites_form':EmailInvites(self.request),
                'pledge_form':PledgeLanding(self.request),                
                'fb_app_id':config.config['tipfy.ext.auth.facebook']['api_key'],
                'u_key':u_key_val,
                'pledgeSuccess':success_get,
                'debug':True,
                'dev':{'getvars':self.request.args.items(multi=True),'postvars':self.request.form.items(multi=True)}
            
            }
            
            return render_response('microsite.html', **page_content_vars)
        

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
        return render_response('fb-canvas/tab.html', fb_app_id=config.config['tipfy.ext.auth.facebook']['api_key'], debug=True, pledge_form=PledgeLanding(self.request), dev={'getvars':self.request.args.items(multi=True),'postvars':self.request.form.items(multi=True)})
        
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
        
        logging.info('Beginning new Pledge POST...')
        
        """ Submit and process submitted pledges. """
        form = PledgeLanding(self.request)
        try:
            logging.debug('Beginning validation...')


            if form.validate():

                logging.debug('Validation passed.')

                u_key = str(form.u_key.data).strip('=')
                u_fbid = str(form.u_fbid.data).strip('=')
                action = str(form.u_action.data)
                u_next_action = str(form.u_nextAction.data)
                u_prev_action = str(form.u_prevAction.data)
                firstname = str(form.firstname.data)
                lastname = str(form.lastname.data)
                email = str(form.email.data)
                phone = str(form.phone.data)
                message = str(form.message.data)
                
                logging.info('Submitted form POST data follows...')
                
                logging.info('action = '+action)
                logging.info('next = '+u_next_action)
                logging.info('prev = '+u_prev_action)
                logging.info('key = '+u_key)
                logging.info('firstname = '+firstname)
                logging.info('lastname = '+lastname)
                logging.info('email = '+email)
                logging.info('phone = '+phone)
                logging.info('message = '+message)                                                                                
        
        
                if action is not False:
                    
                    logging.debug('Action valid.')
            
                    if u_key is not False:
                        
                        ## Use Key or FBID, whichever exists
                        if u_key == '' or u_key is None:
                            if u_fbid == '' or u_key is None:
                                abort(400)
                                logging.error('Request failed because both fbid and key are missing.')
                                return Response('<b>Must provide FBID or U_KEY.')
                            else:
                                logging.info('Using FBID to identify user.')
                                u = FacebookUser.get_by_key_name(u_fbid)
                        else:
                            logging.info('Using KEY to identify user.')
                            u = db.get(db.Key(u_key))
                        
                        logging.info('User record: '+str(u))
                        
                        u.firstname = firstname
                        u.lastname = lastname
                        u.email = email
                        u.phone = phone
                        u.has_pledged = True
        
                        p = Pledge(u, user=u, personal_message=message)
                                
                        db.put([u, p])
                        
                        logging.debug('Put pledge and updated user.')
                
                        if u_next_action is not False:
                            
                            logging.debug('Redirecting to next action...')
                            return redirect(u_next_action)

                    else:
                        logging.error('Couldn\'t retrieve key. Exiting 404.')
                        abort(404)
                       
                else:
                    logging.error('Missing action. Exiting 400.')
                    abort(400)

        except ValidationError, e:
            logging.error('Form validation failed. Redirecting with error text.')
            self.redirect(self.request.headers.get('referrer')+'&validationError=true&error='+urllib2.urlencode(str(e.message)))
        
        
#### SENDS EMAIL INVITES
class EmailInvites(RequestHandler):

    def post(self):
        
        logging.info('Beginning new outgoing email POST...')
        
        form = EmailInvites(self.request)
        try:
            logging.debug('Beginning validation...')


            if form.validate():

                logging.debug('Validation passed.')

                u_key = str(form.u_key.data).strip('=')
                u_fbid = str(form.u_fbid.data).strip('=')
                message = str(form.message.data)
                email_1 = str(form.email_1.data)
                email_2 = str(form.email_2.data)
                email_3 = str(form.email_3.data)
                email_4 = str(form.email_4.data)
                email_5 = str(form.email_5.data)
                
                logging.info('Submitted form POST data follows...')
                
                logging.info('key = '+u_key)
                logging.info('email 1 = '+email_1)
                logging.info('email 2 = '+email_2)
                logging.info('email 3 = '+email_3)
                logging.info('email 4 = '+email_4)
                logging.info('email 5 = '+email_5)
                logging.info('message = '+message)
                
                emails = [email_1, email_2, email_3, email_4, email_5]
            
                if u_key is not False:
                    
                    ## Use Key or FBID, whichever exists
                    if u_key == '' or u_key is None:
                        if u_fbid == '' or u_key is None:
                            abort(400)
                            logging.error('Request failed because both fbid and key are missing.')
                            return Response('<b>Must provide FBID or U_KEY.')
                        else:
                            logging.info('Using FBID to identify user.')
                            u = FacebookUser.get_by_key_name(u_fbid)
                    else:
                        logging.info('Using KEY to identify user.')
                        u = db.get(db.Key(u_key))
                    
                    logging.info('User record: '+str(u))

                    if message == '' or message is None:
                        message = 'Sign up for YVR today! (DEVTEST)'
                    
                    tickets = []

                    for email in emails:
                        if mail.is_email_valid(email):
                            tickets.append(OutboundEmail(user=u, to_email=email, subject='(DEV) YV Outbound Email', message=message))
                            

                    keys = db.put(tickets)

                    tasks = []
                    for item in keys:
                        t = taskqueue.Task(url='/_api/mail/send', params={'ticket':str(item)}).add(queue_name='outbound-mail')
            
                
                else:
                    logging.error('Couldn\'t retrieve key. Exiting 404.')
                    abort(404)
                   

        except ValidationError, e:
            logging.error('Form validation failed. Redirecting with error text.')
            self.redirect(self.request.headers.get('referrer')+'&validationError=true&error='+urllib2.urlencode(str(e.message)))