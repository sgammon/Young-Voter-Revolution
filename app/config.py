# -*- coding: utf-8 -*-
"""
    config
    ~~~~~~

    Configuration settings.

    :copyright: 2009 by tipfy.org.
    :license: BSD, see LICENSE for more details.
"""
config = {}

# Configurations for the 'tipfy' module.
config['tipfy'] = {
    # Enable debugger. It will be loaded only in development.
    'middleware': [
        'tipfy.ext.debugger.DebuggerMiddleware',
    ],
    # Enable the Hello, World! app example.
    'apps_installed': [
        'apps.yvr',
    ],
}

config['tipfy.ext.auth.facebook'] = {
    'api_key':    '162867180394678',
    'app_secret': 'dc90c5891c685f2e44f43e249a0599b5',
}

config['tipfy.ext.jinja2'] = {
    'force_use_compiled': False,
    'engine_factory': 'apps.yvr.handlers.yvr_template_factory'
}

config['yvr.out.template_factory'] = {
    'enable_logging':False,
    'use_memory_cache':True,
    'use_memcache':True
}

twilio = {'from_number':'4155992671', 'account_sid':'AC8cb910ac2bc06ed184232be22bca8cf2', 'auth_token':'e3eddb2fcb7ba2f9c63f7390f6751626'}