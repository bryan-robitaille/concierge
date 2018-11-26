import logging
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.core.exceptions import ValidationError
from django.utils.module_loading import import_string
from defender.connection import get_redis_connection
from defender import config
from django.core.mail import send_mail
from defender.data import store_login_attempt
from django.template import loader
from django.conf import settings
from django.core.validators import validate_email
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from core.models import User, SiteConfiguration
from accountlockout import ip

REDIS_SERVER = get_redis_connection()

LOG = logging.getLogger(__name__)

get_username_from_request = import_string(
    config.GET_USERNAME_FROM_REQUEST_PATH
)


def validate_email_address(email):
    try:
        validate_email(email)
        return True
    except ValidationError:
        return False

def send_blocked_email(request, username):
    if validate_email_address(username):
        found_user = User.objects.filter(email__iexact=username)
        if found_user.exists():
            #load site configuration
            site_config = SiteConfiguration.get_solo()
            config_data = site_config.get_values()
            for user in found_user:

                c = {
                    'domain': request.META['HTTP_HOST'],
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'user': user,
                    'token': default_token_generator.make_token(user),
                    'protocol': request.is_secure() and "https" or "http",
                    'attemps': config.IP_FAILURE_LIMIT,
                    'time': int(config.COOLOFF_TIME /60)
                }

                subject_template_name = 'emails/reset_password_subject.txt'
                email_template_name = 'emails/reset_password.txt'
                html_email_template_name = 'emails/reset_password_lockout.html'
                subject = loader.render_to_string(subject_template_name)
                subject = ''.join(subject.splitlines())
                email = loader.render_to_string(email_template_name, c)
                html_email = loader.render_to_string(html_email_template_name, c)
                send_mail(subject, email, config_data['from_email'], [user.email], fail_silently=False, html_message=html_email)


def lockout_response(request):
    """ if we are locked out, here is the response """
    username = get_username_from_request(request)
    if config.LOCKOUT_TEMPLATE:
        context = {
            'cooloff_time_seconds': config.COOLOFF_TIME,
            'cooloff_time_minutes': int(config.COOLOFF_TIME / 60),
            'failure_limit': config.FAILURE_LIMIT,
            'email_lockout': username,
        }
        send_blocked_email(request, username)
        return render(request, config.LOCKOUT_TEMPLATE, context)

    if config.LOCKOUT_URL:
        return HttpResponseRedirect(config.LOCKOUT_URL)

    if config.COOLOFF_TIME:
        return HttpResponse("Account locked: too many login attempts.  "
                            "Please try again later.")
    else:
        return HttpResponse("Account locked: too many login attempts.  "
                            "Contact an admin to unlock your account.")


def add_login_attempt_to_db(request, login_valid,
                            get_username=get_username_from_request,
                            username=None):
    """ Create a record for the login attempt If using celery call celery
    task, if not, call the method normally """

    if not config.STORE_ACCESS_ATTEMPTS:
        # If we don't want to store in the database, then don't proceed.
        return

    username = username or get_username(request)

    user_agent = request.META.get('HTTP_USER_AGENT', '<unknown>')[:255]
    ip_address = ip.get(request)
    http_accept = request.META.get('HTTP_ACCEPT', '<unknown>')
    path_info = request.META.get('PATH_INFO', '<unknown>')

    if config.USE_CELERY:
        from .tasks import add_login_attempt_task
        add_login_attempt_task.delay(user_agent, ip_address, username,
                                     http_accept, path_info, login_valid)
    else:
        store_login_attempt(user_agent, ip_address, username,
                            http_accept, path_info, login_valid)
