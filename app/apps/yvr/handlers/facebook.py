import config, logging, simplejson as json

from google.appengine.ext import db
from google.appengine.api import memcache

from . import YVRRequestHandler
from tipfy import Response, abort, redirect
from tipfy.ext.jinja2 import Jinja2Mixin
from tipfy.ext.auth.facebook import FacebookMixin

from apps.yvr.models import FacebookUser, Pledge
from apps.yvr.forms import PledgeLandingNoSubmit, EmailInvites


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


#### FACEBOOK INIT
class FacebookInit(YVRRequestHandler, FacebookMixin):

    def head(self, **kwargs):
        """Facebook pings this URL when a user first authorizes your application."""
        return Response('')        

    def get(self):

        if self.request.args.get('session', None):
            logging.debug('FacebookInit: Authenticated. Passing to _on_auth.')
            return Response('<b>fb init</b>')
            #return self.get_authenticated_user(self._on_auth)
            
        logging.debug('FacebookInit: Not authenticated. Redirecting.')        
        return Response('<b>fb init</b>')
        #return self.authenticate_redirect(extended_permissions='email,sms')
        
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
                'pledge_form':PledgeLandingNoSubmit(self.request),                
                'fb_app_id':config.config['tipfy.ext.auth.facebook']['api_key'],
                'u_key':u_key_val,
                'pledgeSuccess':success_get,
                'debug':True,
                'dev':{'getvars':self.request.args.items(multi=True),'postvars':self.request.form.items(multi=True)}
            
            }
            
            return self.render('microsite.html', **page_content_vars)
        

#### FACBEOOK CANVAS
class FacebookCanvas(YVRRequestHandler, FacebookMixin):

    def get(self):
        """ Renders the Facebook app canvas. """
        return self.render('fb-canvas/main.html', fb_app_id=config.config['tipfy.ext.auth.facebook']['api_key'], debug=True, pledge_form=PledgeLandingNoSubmit(self.request))

    def post(self):
        """ Renders the Facebook app canvas. """
        return self.get()
        

#### FACEBOOK PLEDGE
class FacebookTab(YVRRequestHandler):
    
    def get(self):
        """ Renders the Facebook page tab. """
        return self.render('fb-canvas/tab.html', pledge_form=PledgeLandingNoSubmit(self.request))
        
        
    def post(self):
        """ Renders the Facebook page tab. """
        return self.get()
        
    
#### FACEBOOK DEAUTHORIZE
class FacebookDeauthorize(YVRRequestHandler):

    def get(self):
        """ Processes user deauthorizations. """
        return Response('<b>cool</b>')