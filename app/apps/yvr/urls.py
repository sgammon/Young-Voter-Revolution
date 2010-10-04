# -*- coding: utf-8 -*-
"""
    urls
    ~~~~

    URL definitions.

    :copyright: 2009 by tipfy.org.
    :license: BSD, see LICENSE.txt for more details.
"""
from tipfy import Rule


def get_rules(app):
    """Returns a list of URL rules for the Hello, World! application.

    :param app:
        The WSGI application instance.
    :return:
        A list of class:`tipfy.Rule` instances.
    """
    rules = [

        ## Main Endpoints
        Rule('/', endpoint='landing', handler='apps.yvr.handlers.microsite.LandingHandler'), ## index is entrypoint to the microsite
        Rule('/dev', endpoint='dev', handler='apps.yvr.handlers.DevHandler'), ## dev handler for system use
        
        ## Facebook Endpoints
        Rule('/fb', endpoint='facebook-auth', handler='apps.yvr.handlers.facebook.FacebookInit'), ## facebook auth initiation
        Rule('/_api/canvas/', endpoint='facebook-canvas', handler='apps.yvr.handlers.facebook.FacebookCanvas'), ## facebook canvas (application main page)
        Rule('/_api/canvas/tab/', endpoint='facebook-tab', handler='apps.yvr.handlers.facebook.FacebookTab'), ## facebook canvas for profile tabs
        Rule('/_api/deauthorize', endpoint='facebook-deauthorize', handler='apps.yvr.handlers.facebook.FacebookDeauthorize'), ## deauthorize endpoint for app removal

        ## Form Endpoints
        Rule('/_api/data/pledge', endpoint='pledge-submit', handler='apps.yvr.handlers.PledgeSubmit'), ## POST endpoint for submitted pledges
        Rule('/_api/data/invite', endpoint='invites-send', handler='apps.yvr.handlers.EmailInvites'), ## POST endpoint for queued email invites

        ## Queue/Twilio/Email Endpoints
        Rule('/_api/sms/send', endpoint='outbound-sms-queue', handler='apps.yvr.workers.SendSMS'), ## queue worker for outgoing twilio SMS
        Rule('/_api/sms/callback', endpoint='outbound-sms-callback', handler='apps.yvr.workers.SMSCallback'), ## callback for outgoing twilio SMS
        Rule('/_api/mail/send', endpoint='outbound-mail-queue', handler='apps.yvr.workers.SendMail'), ## queue worker for outgoing mail
        
        ## Admin Panel Stuff
        Rule('/manage/data', endpoint='admin-data-index', handler='apps.yvr.handlers.admin.Index'), ## admin panel index page
        Rule('/manage/data/key/<string:key>', endpoint='admin-data-view', handler='apps.yvr.handlers.admin.View'), ## generates a view/edit for a record        
        Rule('/manage/data/list/<string:type>', endpoint='admin-data-list', handler='apps.yvr.handlers.admin.List'), ## lists records for a kind
        Rule('/manage/data/create/<string:type>', endpoint='admin-data-create', handler='apps.yvr.handlers.admin.Create'), ## generate create form for data item
        Rule('/manage/data/delete/<string:key>', endpoint='admin-data-delete', handler='apps.yvr.handlers.admin.Delete') ## delete a given key

    ]

    return rules
