#!/usr/bin/env python

#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
#

"""
    test wbemcli script.  This test generates a cmdline that calls
    wbemcli with a specific set of options and tests the returns.
    Because wbemcli always goes to interactive mode, the test call
    includes a wbemcli script that forces wbemcli to quit.

    It dynamically generates the set of tests from the TEST_MAP table.
"""

from __future__ import print_function, absolute_import
import os
import unittest
from re import findall
from subprocess import Popen, PIPE
import six

# Location of any test scripts for testing wbemcli.py
SCRIPT_DIR = os.path.dirname(__file__)


# Output fragments to test against for each test defined
# Each item is a list of fragmants that are tested against the cmd execution
# result
HELP_OUTPUT = ['-n namespace,',
               '-t timeout', ]
LOG_DEST_STDERR_OUTPUT = ['log=on',
                          'Connection: http://localhost,',
                          ' no creds']
LOG_DEST_FILE_OUTPUT = ['log=on',
                        'Connection: http://localhost,',
                        ' no creds']

TIMEOUT_OUTPUT = ['Connection: http://localhost,',
                  ' no creds',
                  'timeout=10']
NAMESPACE_OUTPUT = ['log=on',
                    'Connection: http://localhost,',
                    ' no creds',
                    'default-namespace=rex/fred']

# TODO ks: change this to use named tuple for clarity
# Each test is dictionary with list containing test definition.
#    For each test the dictionary entry includes:
#    0 string defining 
# expected stderr

TESTS_MAP = {  # pylint: disable=invalid-name
    'help': ["--help", HELP_OUTPUT, 0, None],
    'namespace': ["-n rex/fred", NAMESPACE_OUTPUT, 0, None],
    'timeout': ["-t 10", TIMEOUT_OUTPUT, 0, None], }

# more tests
#    'log_dest_stderr': ['-l stderr', LOG_DEST_STDERR_OUTPUT]}
#    'log_dest_file': ['-l file', LOG_DEST_STDERR_OUTPUT]}


class ContainerMeta(type):
    """Class to define the function to generate unittest methods."""

    def __new__(mcs, name, bases, dict):  # pylint: disable=redefined-builtin
        def generate_test(test_name, cmd_str, expected_stdout, expected_stderr):
            """
            Defines the test method (test) that we generate for each test
            and returns the method.

            The cmd_str defines ONLY the arguments and options part of the
            command.  This function prepends wbemcli to the cmd_str.

            Since wbemcli is interactive, it also includes a quit script

            Each test builds the pywbemcli command executes it and tests the
            results
            """
            def test(self):  # pylint: disable=missing-docstring
                """ The test method that is generated."""
                term_script_file = os.path.join(SCRIPT_DIR,
                                                'wbemcli_quit_script.py')
                term_script_param = '-s %s' % term_script_file

                command = ('wbemcli http://blah %s %s' %
                           (cmd_str, term_script_param))
                # Disable python warnings for wbemcli call
                # because some imports generate deprecated warnings
                # that appear in std_err when nothing expected
                command = 'export PYTHONWARNINGS="" && %s' % command
                proc = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
                std_out, std_err = proc.communicate()
                exitcode = proc.returncode
                if six.PY3:
                    std_out = std_out.decode()
                    std_err = std_err.decode()

                self.assertEqual(exitcode, 0, ('%s: Unexpected ExitCode Err, '
                                               'cmd="%s" '
                                               'exitcode %s stderr=%s' %
                                               (test_name, command,
                                               exitcode, std_err)))

                if not expected_stderr:
                    self.assertEqual(std_err, "",
                                     '%s stderr not empty. returned %s'
                                     % (test_name, std_err))
                else:
                    for item in expected_stderr:
                        match_result = findall(item, std_err)
                        self.assertIsNotNone(match_result, 'test %s, '
                                             'stderr did not match test '
                                             'definition. Expected %s in %s' %
                                             (test_name, item, expected_stderr))

                for item in expected_stdout:
                    match_result = findall(item, std_out)
                    self.assertIsNotNone(match_result,
                                         'Test %s, stdout did not match test '
                                         'definition. Expected %s in %s' %
                                         (test_name, item, expected_stdout))
            return test

        for test_name, params in six.iteritems(TESTS_MAP):
            test_name = "test_%s" % test_name
            dict[test_name] = generate_test(test_name, params[0], params[1],
                                            params[2])
        return type.__new__(mcs, name, bases, dict)


@six.add_metaclass(ContainerMeta)
class TestsContainer(unittest.TestCase):
    """Container class for all tests"""
    __metaclass__ = ContainerMeta


if __name__ == '__main__':
    unittest.main()
