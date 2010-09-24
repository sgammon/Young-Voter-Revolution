from tipfy.ext.wtforms import Form, fields, validators


class PledgeLanding(Form):
    firstname = fields.HiddenField(id='firstname_input')
    lastname = fields.HiddenField(id='lastname_input')
    
    zipcode = fields.TextField(id='zipcode_input')
    email = fields.TextField(id='email_input')
    phone = fields.TextField(id='phone_input')
    message = fields.TextAreaField(id='message_input')
    do_pledge = fields.BooleanField(id='do_pledge_input')

    u_action = fields.HiddenField(id='action_control', default='pledgeCreate')
    u_nextAction = fields.HiddenField(id='u_next_action_control')
    u_prevAction = fields.HiddenField(id='u_prev_action_control')
    u_key = fields.HiddenField(id='u_key_control')
    submit = fields.SubmitField()