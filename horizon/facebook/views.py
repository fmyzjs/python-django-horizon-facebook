import urllib

from django.http import HttpResponseRedirect
from django.conf import settings
from django.contrib.auth import login as auth_login
from django.contrib.auth import authenticate
from django.core.urlresolvers import reverse
from openstack_auth.user import set_session_from_user, create_user_from_token
from openstack_auth.forms import Login


def login(request):
    """ First step of process, redirects user to facebook, which redirects to authentication_callback. """
    args = {
        'client_id': settings.FACEBOOK_APP_ID,
        'scope': settings.FACEBOOK_SCOPE,
        'redirect_uri': request.build_absolute_uri(\
            reverse('horizon.facebook.views.authentication_callback')
        )
    }
    return HttpResponseRedirect('https://www.facebook.com/dialog/oauth?' + urllib.urlencode(args))


def authentication_callback(request):
    """ Second step of the login process.
    It reads in a code from Facebook, then redirects back to the home page. """
    code = request.GET.get('code')
    user = authenticate(token=code, request=request)
    auth_login(request, user)
    set_session_from_user(request, user)
    region = request.user.endpoint
    region_name = dict(Login.get_region_choices()).get(region)
    request.session['region_endpoint'] = region
    request.session['region_name'] = region_name
    url = getattr(settings, "LOGIN_REDIRECT_URL", "/")
    resp = HttpResponseRedirect(url)

    return resp
