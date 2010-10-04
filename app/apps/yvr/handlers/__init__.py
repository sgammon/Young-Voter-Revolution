import logging, os, config, urllib2, base64, simplejson as json

from google.appengine.ext import db
from google.appengine.api import memcache, mail
from google.appengine.api.labs import taskqueue

from tipfy import RequestHandler, Response, abort, redirect, Tipfy, url_for
from tipfy.ext.jinja2 import render_response as jrender, Environment, ModuleLoader, FileSystemLoader
from wtforms.validators import ValidationError

from apps.yvr.models import FacebookUser, Pledge, MicrositeUser, ListMember
from apps.yvr.forms import PledgeLanding, EmailInvites


try:
    from tipfy.ext import i18n
except (ImportError, AttributeError), e:
    i18n = None

try:
    t_data
except NameError:
    t_data = {}

# Superfast In-Memory Cache
def get_tdata_from_fastcache(name, do_log):

    if name in t_data:
        if do_log: logging.debug('Found bytecode in fastcache memory under key \''+str(base64.b64encode(name))+'\'.')
        return t_data[name]
    else: return None
    

# Memcache API loader
def get_tdata_from_memcache(name, do_log):
    
    data = memcache.get('tdata-'+name)
    if data is not None:
        if do_log: logging.debug('Found bytecode in memcache under key \'tdata-'+str(name)+'\'.')
        return data
    else: return None
    

# Loader class
class YVRLoader(FileSystemLoader):
    
    def load(self, environment, name, globals=None):
        
        if globals is None:
            globals = {}

        # Load config
        app = Tipfy.app
        y_cfg = app.get_config('yvr.out.template_factory')
        
        # Encode in Base64
        b64_name = base64.b64encode(name)

        # Debug logging
        if y_cfg.get('enable_logging'): do_log = True;
        if do_log: logging.debug('YVR Loader received request for name \''+str(name)+'\'.')
        
        # Try the in-memory supercache
        if y_cfg.get('use_memory_cache'): bytecode = get_tdata_from_fastcache(b64_name, do_log)
        
        if bytecode is None: # Not found in fastcache
        
            if do_log: logging.debug('Template not found in fastcache.')
            
            # Fallback to memcache
            if y_cfg.get('use_memcache'): bytecode = get_tdata_from_memcache(b64_name, do_log)

            # Fallback to regular loader, then cache
            if bytecode is None: # Not found in memcache
                
                if do_log: logging.debug('Template not found in memcache.')
                
                source, filename, uptodate = self.get_source(environment, name)
                template = file(filename).read().decode('ascii').decode('utf-8')
                bytecode = environment.compile(template, raw=True)
                
                if do_log: logging.debug('Loaded, decoded, and compiled template code manually.')
                
                if y_cfg.get('use_memcache'):
                    memcache.set('tdata-'+b64_name, bytecode)
                    if do_log: logging.debug('Stored in memcache with key \'tdata-'+b64_name+'\'.')
                
            bytecode = compile(bytecode, name, 'exec')
            
            if y_cfg.get('use_memory_cache'):
                t_data[b64_name] = bytecode
                if do_log: logging.debug('Stored in fastcache with key \''+b64_name+'\'')
            
        # Return compiled template code
        return environment.template_class.from_code(environment, bytecode, globals)
        
# Template Factory
def yvr_template_factory():
    """Returns the Jinja2 environment.

    :return:
        A ``jinja2.Environment`` instance.
    """
    app = Tipfy.app
    cfg = app.get_config('tipfy.ext.jinja2')
    templates_compiled_target = cfg.get('templates_compiled_target')
    use_compiled = not app.dev or cfg.get( 'force_use_compiled')

    if templates_compiled_target is not None and use_compiled:
        # Use precompiled templates loaded from a module or zip.
        loader = ModuleLoader(templates_compiled_target)
    else:
        # Parse templates for every new environment instances.
        loader = YVRLoader(cfg.get( 'templates_dir'))

    if i18n:
        extensions = ['jinja2.ext.i18n']
    else:
        extensions = []

    # Initialize the environment.
    env = Environment(loader=loader, extensions=extensions)

    # Add url_for() by default.
    env.globals['url_for'] = url_for

    if i18n:
        # Install i18n.
        trans = i18n.get_translations
        env.install_gettext_callables(
            lambda s: trans().ugettext(s),
            lambda s, p, n: trans().ungettext(s, p, n),
            newstyle=True)
        env.globals.update({
            'format_date':     i18n.format_date,
            'format_time':     i18n.format_time,
            'format_datetime': i18n.format_datetime,
        })

    return env

## Jinja Request Handler Parent
class YVRRequestHandler(RequestHandler):
    
    def render(self, template, vars={}, **kwargs):
        
        sys = {
            
            'env':os.environ,
            'request':self.request,
            'config':config.config,
            'fb_app_id':config.config['tipfy.ext.auth.facebook']['api_key'],
            'dev':
                {
                    'getvars':self.request.args.items(multi=True),
                    'postvars':self.request.form.items(multi=True)
                }
        }
        
        
        if str(os.environ['SERVER_SOFTWARE'][0:3]).lower() == 'dev':
            sys['dev']['is_dev'] = True
        
        return jrender(template, sys=sys, **kwargs)



#### DEV HANDLER
class DevHandler(YVRRequestHandler):
    def get(self):

        """ Basic dev handler for debugging. """
        return self.render('dev.html', title='Dev Handler', ev=os.environ)


#### ENDPOINT FOR SUBMITTING PLEDGES
class PledgeSubmit(YVRRequestHandler):

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
                u_next_action = str(form.u_nextAction.data)
                u_lists = form.u_lists.data
                u_prev_action = str(form.u_prevAction.data)
                firstname = str(form.firstname.data)
                lastname = str(form.lastname.data)
                email = str(form.email.data)
                phone = str(form.phone.data)
                zipcode = str(form.zipcode.data)
                message = str(form.message.data)
                
                logging.info('Submitted form POST data follows...')
                
                logging.info('next = '+u_next_action)
                logging.info('lists = '+str(u_lists))
                logging.info('prev = '+u_prev_action)
                logging.info('key = '+u_key)
                logging.info('firstname = '+firstname)
                logging.info('lastname = '+lastname)
                logging.info('email = '+email)
                logging.info('phone = '+phone)
                logging.info('zipcode = '+zipcode)                
                logging.info('message = '+message)                                                                                
        
        
                logging.debug('Action valid.')
                    
                ## Use Key or FBID, whichever exists
                if u_key == '' or u_key is None:
                    if u_fbid == '' or u_key is None:
                        logging.info('Creating anonymous microsite user.')
                        u = MicrositeUser()
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
                u.zipcode = int(zipcode)
                u.has_pledged = True
                
                if not u.is_saved():
                    u.put()
                    
                memberships = []
                if isinstance(u_lists, list) and len(u_lists) > 0:
                    for list_item in u_lists:
                        memberships.append(ListMember(user=u, list=db.Key(list_item), opted_in=True))

                p = Pledge(u, user=u, personal_message=message)
                        
                db.put([u, p]+memberships)
                
                logging.debug('Put pledge, updated user, and list memberships.')
        
                if u_next_action is not False:
                    
                    logging.debug('Redirecting to next action...')
                    return redirect(u_next_action)


        except ValidationError, e:
            logging.error('Form validation failed. Redirecting with error text.')
            self.redirect(self.request.headers.get('referrer')+'&validationError=true&error='+urllib2.urlencode(str(e.message)))
        
        
#### SENDS EMAIL INVITES
class EmailInvites(YVRRequestHandler):

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