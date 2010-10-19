from google.appengine.ext import db
from google.appengine.ext.db import polymodel

from config import twilio


class User(polymodel.PolyModel):
    
    firstname = db.StringProperty(verbose_name='First Name')
    lastname = db.StringProperty(verbose_name='Last Name')
    zipcode = db.IntegerProperty(verbose_name='Zip Code')
    email = db.EmailProperty(verbose_name='Email')
    phone = db.PhoneNumberProperty(verbose_name='Mobile Phone')
    has_pledged = db.BooleanProperty(verbose_name='Pledged?')

    modifiedAt = db.DateTimeProperty(auto_now=True, verbose_name='Modified At')
    createdAt = db.DateTimeProperty(auto_now_add=True, verbose_name='Created At')
    

class FacebookUser(User):
    
    uid = db.StringProperty(required=True, verbose_name='Facebook UID')
    
    
class MicrositeUser(User):
    
    FORM_EXCLUDE=['ip_addr']
    
    ip_addr = db.StringProperty(verbose_name='IP Address')


class Pledge(db.Model):

    user = db.ReferenceProperty(User, collection_name='pledges', verbose_name='User')
    personal_message = db.TextProperty(verbose_name='Personal Message')
    shared_via_status = db.BooleanProperty(verbose_name='Shared via Status')
    shared_via_invites = db.IntegerProperty(default=0, verbose_name='Shared via Email')
    
    
class List(polymodel.PolyModel):
    name = db.StringProperty(verbose_name='Name')
    weight = db.IntegerProperty(verbose_name='Ordering Weight')
    description = db.TextProperty(verbose_name='Description')
    form_question = db.StringProperty(verbose_name='Form Question')
    show_public = db.BooleanProperty(verbose_name='Show Public')
    uses_email = db.BooleanProperty(verbose_name='Uses User Email')
    uses_sms = db.BooleanProperty(verbose_name='Uses User Phone')
    
    
class InterestList(List):
    pass
    
    
class PhoneList(List):
    pass
    
    
class EmailList(List):
    pass
    
    
class ListMember(db.Model):
    user = db.ReferenceProperty(User, collection_name='lists', verbose_name='User')
    list = db.ReferenceProperty(List, collection_name='users', verbose_name='List')
    opted_in = db.BooleanProperty(default=False, verbose_name='Opted In')
    double_opted_in = db.BooleanProperty(default=False, verbose_name='Double Opted In')


class OutreachAction(polymodel.PolyModel):
    status = db.StringProperty(choices=['success','queued','processing','failed'],default='queued', verbose_name='Status')


class OutboundSMS(OutreachAction):
    user = db.ReferenceProperty(User, collection_name='sent_sms', verbose_name='User')
    from_number = db.PhoneNumberProperty(default=twilio['from_number'], verbose_name='From Number')
    to_number = db.PhoneNumberProperty(verbose_name='To Number')
    message = db.StringProperty(verbose_name='Message')
    
    
class OutboundEmail(OutreachAction):
    user = db.ReferenceProperty(User, collection_name='sent_email', verbose_name='User')
    to_email = db.EmailProperty(verbose_name='To Email')
    subject = db.StringProperty(verbose_name='Subject')
    message = db.TextProperty(verbose_name='Body')
    
    
models_list = [User, FacebookUser, MicrositeUser, Pledge, List, InterestList, PhoneList, EmailList, ListMember, OutreachAction, OutboundSMS, OutboundEmail]