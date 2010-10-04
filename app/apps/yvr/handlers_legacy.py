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

        



        


        

