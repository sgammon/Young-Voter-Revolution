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
        Rule('/', endpoint='landing', handler='apps.yvr.handlers.LandingHandler'),
        Rule('/dev', endpoint='dev', handler='apps.yvr.handlers.DevHandler'),
        Rule('/fb', endpoint='facebook-auth', handler='apps.yvr.handlers.FacebookInit'),
        
        ## Facebook Endpoints
        Rule('/_api/canvas/', endpoint='facebook-canvas', handler='apps.yvr.handlers.FacebookCanvas'),
        Rule('/_api/canvas/tab/', endpoint='facebook-tab', handler='apps.yvr.handlers.FacebookTab'),
        Rule('/_api/deauthorize', endpoint='facebook-deauthorize', handler='apps.yvr.handlers.FacebookDeauthorize'),

        ## Form Endpoints
        Rule('/_api/data/pledge', endpoint='pledge-submit', handler='apps.yvr.handlers.PledgeSubmit'),

        ## Queue/Twilio Endpoints
        Rule('/_api/sms/send', endpoint='outbound-sms-queue', handler='apps.yvr.workers.SendSMS'),
        Rule('/_api/sms/callback', endpoint='outbound-sms-callback', handler='apps.yvr.workers.SMSCallback')

    ]

    return rules
