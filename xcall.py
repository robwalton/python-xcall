# encoding: utf-8
#
# Copyright (c) 2016 Rob Walton <dhttps://github.com/robwalton>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2017-04-17
import json


"""
A Python x-callback-url client using xcall.

`xcall` is command line macOS application providing generic access to
applications with x-callback-url schemes:

   https://github.com/martinfinke/xcall

"""

import urllib
import logging
import os
import subprocess


__all__ = ['XCall', 'xcall']

XCALL_PATH = (os.path.dirname(os.path.abspath(__file__)) +
              '/lib/xcall.app/Contents/MacOS/xcall')


logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s',
                    level=logging.DEBUG)
logger = logging.getLogger(__name__)


class XCallbackError(Exception):
    """Exception representing an x-error callback from xcall.
    """
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


def default_xerror_handler(stderr, requested_url):
    msg = "x-error callback: '%s'" % stderr
    if requested_url:
        msg += " (in response to url: '%s')" % requested_url
    raise XCallbackError(msg)


def xcall(scheme, action, action_parameters={},
          activate_application=False):
    client = XCallClient(scheme)
    return client.call(action, action_parameters, activate_application)


class XCallClient(object):

    def __init__(self, scheme_name, on_xerror_handler=default_xerror_handler,
                 json_decode_success=True):
        self.scheme_name = scheme_name
        self.on_xerror_handler = on_xerror_handler
        self.json_decode_success = json_decode_success

    def call(self, action, action_parameters={}, activate_application=False):
        """Perform action and return result across xcall.

        action -- the name of the application action to perform
        action_parameters -- dictionary of parameters to pass with call. None
                             entries will be removed before sending. Values
                             will be utf-8 encoded and then url quoted.
        """

        for key in list(action_parameters):
            if action_parameters[key] is None:
                del action_parameters[key]

        cmdurl = self._build_url(action, action_parameters)
        logger.debug('--> ' + cmdurl)
        if not activate_application:
            result = self._xcall(cmdurl)
        else:
            result = self._call_outside_xcall(cmdurl)
        logger.debug('<-- ' + unicode(result) + '\n')
        return result

    __call__ = call

    def _build_url(self, action, action_parameter_dict):
        """Build url to send to Application.

        action -- action name
        action_parameter_dict -- parameters for given action
        """
        url = '%s://x-callback-url/%s' % (self.scheme_name, action)

        if action_parameter_dict:
            par_list = []
            for k, v in action_parameter_dict.iteritems():
                par_list.append(
                    k + '=' + urllib.quote(unicode(v).encode('utf8')))
            url = url + '?' + '&'.join(par_list)
        return url

    def _xcall(self, url):
        """Send a URL to application via xcall and return result as dictionary.

        xcall will call app in a way that it will stay in the background.

        url -- un-encoded URL to send. Will be encoded before sending.

        May raise XCallbackError with error message and code from app.
        """

        p = subprocess.Popen([XCALL_PATH, '-url', url],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()

        assert (stdout == '') or (stderr == '')
        assert not ((stdout == '') and (stderr == ''))
        if stdout:
            response = urllib.unquote(stdout).decode('utf8')
            if self.json_decode_success:
                return json.loads(response)
            else:
                return response
        elif stderr:
            self.on_xerror_handler(stderr, url)
