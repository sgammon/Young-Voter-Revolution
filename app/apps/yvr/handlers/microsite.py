from apps.yvr.forms import PledgeLanding, ShareStatus, EmailInvites

from . import YVRRequestHandler
from tipfy import Response, abort, redirect


#### MAIN LANDING
class LandingHandler(YVRRequestHandler):
    def get(self):
        """Simply returns a Response object with an enigmatic salutation."""
        
        pledgeSuccess = self.request.args.get('pledgeSuccess', False)
        
        forms = {
        
            'pledgeForm':PledgeLanding(self.request),
            'inviteForm':EmailInvites(self.request),
            'statusForm':ShareStatus(self.request)
        
        }
        
        return self.render('landing.html', title='2010 Young Voter Revolution', forms=forms, pledgeSuccess=pledgeSuccess)
