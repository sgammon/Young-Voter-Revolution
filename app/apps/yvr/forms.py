import logging
from google.appengine.api import memcache
from apps.yvr.models import List, InterestList, PhoneList, EmailList
from tipfy.ext.wtforms import Form, fields, validators
from wtforms import widgets
        

class MultiCheckboxField(fields.SelectMultipleField):
    """
    A multiple-select, except displays a list of checkboxes.

    Iterating the field will produce subfields, allowing custom rendering of
    the enclosed checkbox fields.
    """
    
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()
    

def get_list_choices():

    choices_cached = memcache.get('list-choices')

    if choices_cached is None:

        q = List.all().filter('show_public =', True).fetch(20)
        choices = []
            
        if len(q) > 0:
            for choice in q:
                choices.append((str(choice.key()), choice.form_question))

        
            memcache.set('list-choices', choices)
            return choices
        else:
            return []
    else:
        return choices_cached


class PledgeLanding(Form):
    firstname = fields.TextField(id='firstname_input', label='First Name')
    lastname = fields.TextField(id='lastname_input', label='Last Name')
    
    email = fields.TextField(id='email_input', label='Email Address')
    zipcode = fields.TextField(id='zipcode_input', label='Zip Code')
    phone = fields.TextField(id='phone_input', label='Mobile Phone')
    message = fields.TextAreaField(id='message_input', label='Personal Message')

    u_lists = MultiCheckboxField(choices=get_list_choices())
    u_nextAction = fields.HiddenField(id='u_next_action_control')
    u_prevAction = fields.HiddenField(id='u_prev_action_control')
    u_key = fields.HiddenField(id='u_key_control')
    u_fbid = fields.HiddenField(id='u_fbid_control')
    submit = fields.SubmitField()
    

class PledgeLandingNoSubmit(Form):
    firstname = fields.TextField(id='firstname_input', label='First Name')
    lastname = fields.TextField(id='lastname_input', label='Last Name')
    
    email = fields.TextField(id='email_input', label='Email Address')
    zipcode = fields.TextField(id='zipcode_input', label='Zip Code')
    phone = fields.TextField(id='phone_input', label='Mobile Phone')
    message = fields.TextAreaField(id='message_input', label='Personal Message')

    u_lists = MultiCheckboxField(choices=get_list_choices())
    u_nextAction = fields.HiddenField(id='u_next_action_control')
    u_prevAction = fields.HiddenField(id='u_prev_action_control')
    u_key = fields.HiddenField(id='u_key_control')
    u_fbid = fields.HiddenField(id='u_fbid_control')

    
class EmailInvites(Form):
    message = fields.TextAreaField(id='message_input')
    email_1 = fields.TextField(id='email_input_1')
    email_2 = fields.TextField(id='email_input_2')
    email_3 = fields.TextField(id='email_input_3')
    #email_4 = fields.TextField(id='email_input_4')
    #email_5 = fields.TextField(id='email_input_5')
    u_key = fields.HiddenField('u_key_control')
    u_fbid = fields.HiddenField(id='u_fbid_control')
    submit = fields.SubmitField()
    
    
class ShareStatus(Form):
    personal_message = fields.TextAreaField(id='share_message_input')