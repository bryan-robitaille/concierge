"""
Initialize the emailvalidator django application, and configure
"""
import re
import requests
import json
from django.conf import settings
from .models import EmailRegExValidator
from core.models import SiteConfiguration


def is_email_valid(email):

    #load site configuration
    site_config = SiteConfiguration.get_solo()
    config_data = site_config.get_values()

    # Verify email address is in user invitation list
    if config_data['elgg_url']:
        elgg_url = config_data['elgg_url']

        valid_user_request = requests.post(elgg_url + "/services/api/rest/json/", data={'method': 'pleio.invited', 'email': email})
        valid_user_json = json.loads(valid_user_request.text)
        valid_user_result = valid_user_json["result"] if 'result' in valid_user_json else False

        if valid_user_result is True:
            return True

    """
    Determines if the provided email is valid based on the regular expressions
    stored in the database.
    """
    validators = EmailRegExValidator.objects.all().filter(allow_all=False)
    regexes = [re.compile(r.regex, re.IGNORECASE) for r in validators]
    domains = EmailRegExValidator.objects.all().filter(allow_all=True)
    regexes += [re.compile("^.*@[\w.]*?" + r.regex + "$", re.IGNORECASE) for r in domains]
    return any(regex.match(email) for regex in regexes)
