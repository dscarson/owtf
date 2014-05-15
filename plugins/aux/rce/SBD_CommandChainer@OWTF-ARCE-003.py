"""

owtf is an OWASP+PTES-focused try to unite great tools and facilitate pen testing
Copyright (c) 2011, Abraham Aranguren <name.surname@gmail.com> Twitter: @7a_ http://7-a.org
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
    * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.
    * Neither the name of the copyright owner nor the
      names of its contributors may be used to endorse or promote products
      derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.  LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""


import time
from framework.plugin.plugins import ActivePlugin


class SBDCommandChainerPlugin(ActivePlugin):
    """Runs a chain of commands on an agent server via SBD -i.e. for IDS testing-"""

    def run(self):
        content = self.__doc__ + ' Results:<br />'
        iteration = 1
        for args in self.core.PluginParams.GetArgs({
                'Description': self.__doc__,
                'Mandatory': {
                    'RHOST': self.core.Config.Get('RHOST_DESCRIP'),
                    'SBD_PORT': self.core.Config.Get('SBD_PORT_DESCRIP'),
                    'SBD_PASSWORD': self.core.Config.Get(
                        'SBD_PASSWORD_DESCRIP'),
                    'COMMAND_PREFIX':
                        'The command string to be pre-pended to the tests '
                        '(i.e. /usr/lib/firefox... http...)',
                    },
                'Optional': {
                    'TEST': 'The test to be included between prefix and suffix',
                    'COMMAND_SUFIX':
                        'The URL to be appended to the tests '
                        '(i.e. ...whatever)',
                    'ISHELL_REUSE_CONNECTION': self.core.Config.Get(
                        'ISHELL_REUSE_CONNECTION_DESCRIP'),
                    'ISHELL_EXIT_METHOD': self.core.Config.Get(
                        'ISHELL_EXIT_METHOD_DESCRIP'),
                    'ISHELL_DELAY_BETWEEN_COMMANDS': self.core.Config.Get(
                        'ISHELL_DELAY_BETWEEN_COMMANDS_DESCRIP'),
                    'ISHELL_COMMANDS_BEFORE_EXIT': self.core.Config.Get(
                        'ISHELL_COMMANDS_BEFORE_EXIT_DESCRIP'),
                    'ISHELL_COMMANDS_BEFORE_EXIT_DELIM': self.core.Config.Get(
                        'ISHELL_COMMANDS_BEFORE_EXIT_DELIM_DESCRIP'),
                    'REPEAT_DELIM': self.core.Config.Get(
                        'REPEAT_DELIM_DESCRIP')
                    }
                },
                self.plugin_info):
            # Sets the aux plugin arguments as config.
            self.core.PluginParams.SetConfig(args)
            REUSE_CONNECTION = (args['ISHELL_REUSE_CONNECTION'] == 'yes')
            #print "REUSE_CONNECTION=" + str(REUSE_CONNECTION)
            DELAY_BETWEEN_COMMANDS = args['ISHELL_DELAY_BETWEEN_COMMANDS']
            #print "Args="+str(Args)
            #print "'ISHELL_COMMANDS_BEFORE_EXIT_DELIM'=" + Args['ISHELL_COMMANDS_BEFORE_EXIT_DELIM']
            #break
            if iteration == 1 or not REUSE_CONNECTION:
                self.core.InteractiveShell.Open({
                    'ConnectVia': self.core.Config.GetResources(
                        'RCE_SBD_Connection'),
                    'InitialCommands': None, #[ Args['BROWSER_PATH'] + ' about:blank']
                    'ExitMethod': args['ISHELL_EXIT_METHOD'],
                    'CommandsBeforeExit': args['ISHELL_COMMANDS_BEFORE_EXIT'],
                    'CommandsBeforeExitDelim': args[
                        'ISHELL_COMMANDS_BEFORE_EXIT_DELIM'],
                    'RHOST': args['RHOST'],
                    'RPORT': args['SBD_PORT']
                    },
                    self.plugin_info)
            else:
                self.core.log("Reusing initial connection..")
            self.core.InteractiveShell.Run(
                args['COMMAND_PREFIX'] +
                args['TEST'] +
                args['COMMAND_SUFIX'])
            self.core.log(
                "Sleeping " + DELAY_BETWEEN_COMMANDS +
                " second(s) (increases reliability)..")
            time.sleep(int(DELAY_BETWEEN_COMMANDS))
            #Core.RemoteShell.Run("sleep " + str(WAIT_SECONDS))
            if not REUSE_CONNECTION:
                self.core.InteractiveShell.Close(self.plugin_info)
            #Content += Core.PluginHelper.DrawCommandDump('Test Command', 'Output', Core.Config.GetResources('LaunchExploit_'+Args['CATEGORY']+"_"+Args['SUBCATEGORY']), PluginInfo, "") # No previous output
            iteration += 1 # Increase Iteration counter
        # Ensure clean exit if reusing connection.
        if not self.core.InteractiveShell.IsClosed():
            self.core.InteractiveShell.Close(PluginInfo)
        return content
