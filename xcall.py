# encoding: utf-8
#
# Copyright (c) 2016 Rob Walton <https://github.com/robwalton>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2017-04-17


"""
A Python x-callback-url client used to communicate with an application's
x-callback-url scheme registered with macOS.

Uses `xcall`. `xcall` is command line macOS application providing generic
access to applications with x-callback-url schemes:

   https://github.com/martinfinke/xcall
   
Call to this module are _probably_ not thread/process safe. An ettempt is made
to ensure that `xcall` is not running, but there is 20-30ms window in which
multiple calls to this module will result in multiple xcall processes running;
and the chance of replies being mixed up.

"""

import json
import urllib
import logging
import os
import subprocess


__all__ = ['XCallClient', 'xcall', 'XCallbackError']

XCALL_PATH = (os.path.dirname(os.path.abspath(__file__)) +
              '/lib/xcall.app/Contents/MacOS/xcall')


logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s',
                    level=logging.WARNING)
logger = logging.getLogger(__name__)

def enable_verbose_logging():
    logger.setLevel(logging.DEBUG)


class XCallbackError(Exception):
    """Exception representing an x-error callback from xcall.
    """
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


def default_xerror_handler(xerror, requested_url):
    """Handle an x-error callback by raising a generic XCallbackError

    xerror -- utf-8 un-encoded and then url unquoted x-error reply
    requested_url -- the encoded url sent to application

    (Note: this doc forms part of XCallClient API)
    """
    msg = "x-error callback: '%s'" % xerror
    if requested_url:
        msg += " (in response to url: '%s')" % requested_url
    raise XCallbackError(msg)


def xcall(scheme, action, action_parameters={},
          activate_app=False):
    """Perform action and return un-marshalled result.

    scheme -- scheme name of application to target
    action -- the name of the application action to perform
    action_parameters -- dictionary of parameters to pass with call. None
                         entries will be removed before sending. Values
                         will be utf-8 encoded and then url quoted.
    activate_app -- bring target application to foreground if True

    An x-success reply will be utf-8 un-encoded, then url unquoted,
    and then  unmarshalled using json into python objects before being
    returned.

    An x-error reply will result in an XCallbackError being raised.
    """
    client = XCallClient(scheme)
    return client.xcall(action, action_parameters, activate_app)


class XCallClient(object):
    """A client used for communicating with a particular application.
    """

    def __init__(self, scheme_name, on_xerror_handler=default_xerror_handler,
                 json_decode_success=True):
        """Create an xcall client for a particular application.

        scheme_name -- the url scheme name, as registered with macOS
        on_xerror_handler -- callable to handle x-error callbacks.
                             See xcall.default_xerror_handler
        json_decode_success -- unmarshal x-success calls if True
        """
        self.scheme_name = scheme_name
        self.on_xerror_handler = on_xerror_handler
        self.json_decode_success = json_decode_success

    def xcall(self, action, action_parameters={}, activate_app=False):
        """Perform action and return result across xcall.

        action -- the name of the application action to perform
        action_parameters -- dictionary of parameters to pass with call. None
                             entries will be removed before sending. Values
                             will be utf-8 encoded and then url quoted.
        activate_app -- bring target application to foreground if True

        An x-success reply will be utf-8 un-encoded, then url unquoted,
        and then (if configured)  unmarshalled using json into python objects
        before being returned.

        An x-error reply will result in a call to the configured
        on_xerror_handler.
        """

        for key in list(action_parameters):
            if action_parameters[key] is None:
                del action_parameters[key]

        pid_list = get_pid_of_running_xcall_processes()
        if pid_list:
            raise AssertionError('xcall processe(s) already running. pid(s): ' + str(pid_list))
        cmdurl = self._build_url(action, action_parameters)
        logger.debug('--> ' + cmdurl)
        result = self._xcall(cmdurl, activate_app)
        logger.debug('<-- ' + unicode(result) + '\n')

        return result

    __call__ = xcall

    def _build_url(self, action, action_parameter_dict):
        url = '%s://x-callback-url/%s' % (self.scheme_name, action)

        if action_parameter_dict:
            par_list = []
            for k, v in action_parameter_dict.iteritems():
                par_list.append(
                    k + '=' + urllib.quote(unicode(v).encode('utf8')))
            url = url + '?' + '&'.join(par_list)
        return url

    def _xcall(self, url, activate_app):
        args = [XCALL_PATH, '-url', '"%s"' % url]
        if activate_app:
            args += ['-activateApp', 'YES']

        logger.info('Making bash call: "%s"' % ' '.join(args))


        p = subprocess.Popen(
            args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()

        # Assert that reply had output on one, and only one of stdout and stderr
        if (stdout != '') and (stderr != ''):
            raise AssertionError(
                'xcall utility replied unexpectedly on *both* stdout and stderr.'
                '\nstdout: "%s"\nstderr: "%s"\n'
                'Try xcall directly from terminal with: "%s" ' % (stdout, stderr, ' '.join(args)))
        if (stdout == '') and (stderr == ''):
            raise AssertionError(
                'xcall utility unexpectedly replied on *neither* stdout nor stderr'
                'Try xcall directly from terminal with: "%s"' % ' '.join(args))

        if stdout:
            response = urllib.unquote(stdout).decode('utf8')
            if self.json_decode_success:
                return json.loads(response)
            else:
                return response
        elif stderr:
            self.on_xerror_handler(stderr, url)

 

def get_pid_of_running_xcall_processes():
    try:
        reply = subprocess.check_output(['pgrep', 'xcall'])
    except subprocess.CalledProcessError:
        return []
    pid_list = reply.strip().split('\n')
    if '' in pid_list:
        pid_list.remove('')
    return pid_list
