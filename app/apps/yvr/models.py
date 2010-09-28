from google.appengine.ext import db
from google.appengine.ext.db import polymodel

from config import twilio


class User(polymodel.PolyModel):
    
    firstname = db.StringProperty()
    lastname = db.StringProperty()
    zipcode = db.IntegerProperty()
    email = db.EmailProperty()
    phone = db.PhoneNumberProperty()
    has_pledged = db.BooleanProperty()
    

class FacebookUser(User):
    
    uid = db.StringProperty(required=True)


class Pledge(db.Model):

    user = db.ReferenceProperty(User, collection_name='pledges')
    personal_message = db.TextProperty()
    shared_via_status = db.BooleanProperty()
    shared_via_invites = db.IntegerProperty(default=0)
    
    
class List(polymodel.PolyModel):
    name = db.StringProperty()
    description = db.TextProperty()
    show_public = db.BooleanProperty()
    question_text = db.StringProperty()
    
    
class InterestList(List):
    pass
    
    
class PhoneList(List):
    pass
    
    
class EmailList(List):
    pass
    
    
class ListMember(db.Model):
    user = db.ReferenceProperty(User, collection_name='lists')
    list = db.ReferenceProperty(List, collection_name='users')
    opted_in = db.BooleanProperty()
    double_opted_in = db.BooleanProperty()


class OutreachAction(polymodel.PolyModel):
    status = db.StringProperty(choices=['success','queued','processing','failed'],default='queued')


class OutboundSMS(OutreachAction):
    user = db.ReferenceProperty(User, collection_name='sent_sms')
    from_number = db.PhoneNumberProperty(default=twilio['from_number'])
    to_number = db.PhoneNumberProperty()
    message = db.StringProperty()
    
    
class OutboundEmail(OutreachAction):
    user = db.ReferenceProperty(User, collection_name='sent_email')
    to_email = db.EmailProperty()
    subject = db.StringProperty()
    message = db.TextProperty()