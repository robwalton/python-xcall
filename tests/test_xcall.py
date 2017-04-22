# encoding: utf-8
#
# Copyright (c) 2016 Rob Walton <dhttps://github.com/robwalton>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2017-04-17
#


import time
import pytest
import subprocess
import os

from mock.mock import Mock

import xcall
from collections import OrderedDict
import urllib
import json
from threading import Thread

ACCESS_TOKEN = '8038e1f01b3742f8af957ff23d70d4bc'  # must be manually set


TEST_STRING = ur""" -- () ? & ' " ‘quoted text’ _x_y_z_ a://b.c/d?e=f&g=h"""

# string -> json -> utf8 -> quote
ENCODED_TEST_STRING = (
    urllib.quote(json.dumps(TEST_STRING).encode('utf8')))


def ulysses_installed():
    return not subprocess.call('open -Ra "Ulysses"', shell=True)


def create_mock_Popen(x_success='', x_error=''):
    """Return mock subprocess.Popen class.

    stdout and stderr will be returned by communicate() of its returned
    instance.
    """
    mock_Popen_instance = Mock()
    mock_Popen_instance.communicate = Mock(return_value=(x_success, x_error))
    mock_Popen = Mock(return_value=mock_Popen_instance)
    return mock_Popen


def test_string_coding_and_deencodin():
    assert (json.loads(urllib.unquote(ENCODED_TEST_STRING).decode('utf8')) ==
            TEST_STRING)


def test_xcall_path_correct():
    assert os.path.isfile(xcall.XCALL_PATH)


def test_Popen_mocking():
    mock_Popen = create_mock_Popen('x_success', 'x_error')

    process = mock_Popen(
        ['a', 'b'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    popen_args = mock_Popen.call_args[0][0]
    assert popen_args == ['a', 'b']
    assert stdout, stderr == ('x_success', 'x_error')


def test_xcall__no_parameters(monkeypatch):
    mock_Popen = create_mock_Popen('"ignored success response"', '')
    monkeypatch.setattr(subprocess, 'Popen', mock_Popen)

    xcall.xcall('scheme', 'action')

    popen_args = mock_Popen.call_args[0][0]
    assert popen_args == [xcall.XCALL_PATH, '-url',
                          '"scheme://x-callback-url/action"']


def test_xcall__no_parameters_with_activation(monkeypatch):
    mock_Popen = create_mock_Popen('"ignored success response"', '')
    monkeypatch.setattr(subprocess, 'Popen', mock_Popen)

    xcall.xcall('scheme', 'action', activate_app=True)

    popen_args = mock_Popen.call_args[0][0]
    assert popen_args == [xcall.XCALL_PATH, '-url',
                          '"scheme://x-callback-url/action"',
                          '-activateApp', 'YES']


def test_xcall__with_parameters(monkeypatch):
    mock_Popen = create_mock_Popen('"ignored success response"', '')
    monkeypatch.setattr(subprocess, 'Popen', mock_Popen)

    action_parameters = OrderedDict([('key1', 'val1'), ('key2', 'val2')])
    xcall.xcall('scheme', 'action', action_parameters)

    popen_args = mock_Popen.call_args[0][0]
    assert popen_args == [
        xcall.XCALL_PATH, '-url',
        '"scheme://x-callback-url/action?key1=val1&key2=val2"']


def test_xcall__with_unicode_and_unsafe_html_parameters(monkeypatch):
    mock_Popen = create_mock_Popen('"ignored success response"', '')
    monkeypatch.setattr(subprocess, 'Popen', mock_Popen)

    xcall.xcall('scheme', 'action', {'key1': TEST_STRING})

    popen_args = mock_Popen.call_args[0][0]
    encoded_test_string = urllib.quote(TEST_STRING.encode('utf8'))
    assert popen_args == [
        xcall.XCALL_PATH, '-url',
        u'"scheme://x-callback-url/action?key1=%s"' % encoded_test_string]


def test_xcall__success(monkeypatch):
    mock_Popen = create_mock_Popen('"success response"', '')
    monkeypatch.setattr(subprocess, 'Popen', mock_Popen)

    assert xcall.xcall('scheme', 'action') == 'success response'


def test_xcall__success_with_unicode_and_unsafe_html_parameters(monkeypatch):
    mock_Popen = create_mock_Popen(ENCODED_TEST_STRING, '')
    monkeypatch.setattr(subprocess, 'Popen', mock_Popen)

    assert xcall.xcall('scheme', 'action') == TEST_STRING


def test_xcall__xerror_response(monkeypatch):
    mock_Popen = create_mock_Popen('', 'x-error response')
    monkeypatch.setattr(subprocess, 'Popen', mock_Popen)

    with pytest.raises(xcall.XCallbackError) as excinfo:
        xcall.xcall('scheme', 'action')
    assert ("x-error callback: 'x-error response' (in response to url: "
            "'scheme://x-callback-url/action')" in excinfo.value)


@pytest.mark.skipif("not ulysses_installed()")
def test_xcall_to_ulysses():
    d = xcall.xcall('ulysses', 'get-version')
    assert d['apiVersion'] >= 2


@pytest.mark.skipif("not ulysses_installed()")
def test_xcall_to_ulysses_error():
    with pytest.raises(xcall.XCallbackError):
        xcall.xcall('ulysses', 'not-a-valid-action')


@pytest.mark.skipif("not ulysses_installed()")
def test_speed_or_urlcall():
    t_start = time.time()
    # Run once to ensure ulysses is open
    xcall.xcall('ulysses', 'get-version')
    n = 10
    for i in range(n):  # @UnusedVariable
        xcall.xcall('ulysses', 'get-version')
    dt = time.time() - t_start
    time_per_run = dt / n
    assert time_per_run < 0.15


def test_get_pid_of_running_xcall_processes__non_running():
    assert xcall.get_pid_of_running_xcall_processes() == []


def test_get_pid_of_running_xcall_processes():
    # There is 20-30ms delay before xcall is started (hence the sleep)
    # The solid way to prevent more than one running at once would be with
    # a persistent lock on disk.
    for _ in range(10):
        assert len(xcall.get_pid_of_running_xcall_processes()) == 0
        t = Thread(target=xcall.xcall, args=('ulysses', 'get-version'))
        t.start()
        time.sleep(.03)
        assert len(xcall.get_pid_of_running_xcall_processes()) == 1
        with pytest.raises(AssertionError):
            xcall.xcall('ulysses', 'get-version')
        t.join()
