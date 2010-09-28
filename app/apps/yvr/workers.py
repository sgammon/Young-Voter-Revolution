import urllib, logging, simplejson

from google.appengine.ext import db
from google.appengine.api import urlfetch, mail

from tipfy import RequestHandler, Response
from tipfy.ext.jinja2 import render_response

from config import twilio
from apps.yvr.models import OutboundSMS, OutboundEmail

_twilio_api_scheme = 'https'
_twilio_api_username = twilio['account_sid']
_twilio_api_password = twilio['auth_token']
_twilio_api_endpoint = 'api.twilio.com:80/2010-04-01'
_twilio_rest_action = '/Accounts/'+twilio['account_sid']+'/SMS/Messages'

class SendSMS(RequestHandler):
    
    """ Queues SMS messages for sending notifications through Twilio. """
    
    def post(self):
        
        logging.info('Beginning outbound SMS request.')
        
        ## Pull ticket and prepare REST payload
        ticket_key = self.request.form.get('ticket', False)
        
        logging.debug('Ticket key: '+str(ticket_key)+'.')
                    
        if ticket_key is False:
            logging.error('Ticket key defaulted to False.')
            self.error(400)
            return Response('<b>A valid outbound SMS ticket must be provided.</b>')
            
        else:
            ticket = db.get(db.Key(ticket_key))
            
            if ticket is None:
                logging.error('Ticket key could not be pulled from datastore.')
                self.error(400)
                return Response('<b>A valid outbound SMS ticket must be provided.</b>')
                
            else:
                
                ## Ticket sanity check
                if ticket.class_name() != 'OutboundSMS':
                    logging.error('Ticket could be pulled from datastore but is not of OutboundSMS type.')
                    self.error(400)
                    return Response('<b>A valid OutboundSMS ticket must be provided. A key was given, but was not an OutboundSMS. Key: '+str(ticket_key)+'</b>')

                else:
                    
                    logging.info('Ticket pulled successfully. Starting job...')
                    
                    ## Set ticket status
                    ticket.status = 'processing'
                    ticket.put()
                    
                    logging.debug('Marked ticket as processing.')
                    
                    ## Prepare callback
                    callback_url = 'https://yvrevolution.appspot.com/_api/sms/callback?ticket='+str(ticket_key)
                
                    ## Prepare and submit form
                    form_fields = {
                      "From": twilio['from_number'],
                      "To": ticket.to_number,
                      "Body": ticket.message,
                      "StatusCallback": callback_url
                    }

                    ## Prepare form data and URL
                    form_data = urllib.urlencode(form_fields)
                    url = _twilio_api_scheme+'://'+_twilio_api_username+':'+_twilio_api_password
                    url = url+'@'+_twilio_api_endpoint+_twilio_rest_action+'.json'
                    
                    ## Put in some logging messages
                    logging.debug('From #: '+twilio['from_number'])
                    logging.debug('To #: '+ticket.to_number)
                    logging.debug('Callback: '+callback_url)
                    logging.debug('Final POST URL: "'+str(url)+'".')
                    
                    ## Build the POST request
                    result = urlfetch.fetch(url=url,
                    
                    
                                            payload=form_data,
                                            method=urlfetch.POST,
                                            headers={'Content-Type': 'application/x-www-form-urlencoded'})
                    
                    ## Error out or live happily ever after
                    if result.status_code != 200:
                        logging.error('Twilio request failed with HTTP status code '+str(result.status_code)+'.')
                        self.error(500)
                        return Response('<b>Twilio request failed. Check logs.</b>')
                    else:
                        logging.info('Message successfully queued for delivery.')
            
            
class SMSCallback(RequestHandler):
    
    """ Handles a callback once Twilio is ready to update the status of our queued messages. """

    def post(self):
        
        logging.info('SMS Callback request received.')
        
        ## Pull status from twilio and given Ticket
        status = self.request.form.get('SmsStatus', False)
        ticket_key = self.request.form.get('ticket', False)
        
        ## Debug msgs
        logging.debug('Status: "'+str(status)+'".')
        logging.debug('Ticket: "'+str(ticket_key)+'".')    
        
        ## Sanity checks
        if status is False:
            logging.error('SmsStatus parameter could not be parsed.')
            self.error(404)
            return Response('<b>SmsStatus parameter could not be parsed.')
            
        elif ticket_key is False:
            logging.error('Ticket parameter could not be parsed.')
            self.error(400)
            return Response('<b>Valid ticket parameter must be specified.</b>')
            
        else:
            ## Pull ticket
            ticket = db.get(db.Key(ticket_key))
            
            if ticket is not None and isinstance(ticket, db.Model):
                logging.info('Ticket is valid and ready for processing.')
                
                ## Update status
                if status == 'sent':
                    ticket.status = 'success'
                    
                elif status == 'failure':
                    ticket.status = 'faliure'
                
                ## Update ticket
                ticket.put()
                
                logging.info('Ticket processed and updated with key "'+str(ticket.key())+'".')
                
                
class SendMail(RequestHandler):
    
    def post(self):
        
        ticket_key = self.request.form.get('ticket', False)
        
        logging.debug('Beginning new queued mail request.')
        logging.debug('Ticket key = '+str(ticket_key))
        
        if ticket_key is not False:
            
            ticket = db.get(db.Key(str(ticket_key)))
            logging.debug('Pulled ticket = '+str(ticket))
            
            if ticket is not None:
                
                if not mail.is_email_valid(ticket.to_email):
                    
                    logging.error('Given recipient address is invalid as reported by the GAE Mail API. Failing.')
                    abort(400)
                    
                else:
                    mail.send_mail( sender="Pledge to Vote 2010! <pledge@yvrevolution.com>",
                                    to=ticket.to_email,
                                    subject=ticket.subject,
                                    body=ticket.message)
            
        else:
            logging.critical('Ticket key not provided. Failing.')
            abort(400)