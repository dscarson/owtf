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


from framework.plugin.plugins import ActivePlugin


class SBDCommanderPlugin(ActivePlugin):
    """Runs commands on an agent server via SBD -i.e. for IDS testing-"""

    def run(self):
        content = self.__doc__ + ' Results:<br />'
        iteration = 1
        for args in self.core.PluginParams.GetArgs({
                'Description': self.__doc__,
                'Mandatory': {
                    'RHOST': self.core.Config.Get('RHOST_DESCRIP'),
                    'SBD_PORT': self.core.Config.Get('SBD_PORT_DESCRIP'),
                    'SBD_PASSWORD': self.core.Config.Get('SBD_PASSWORD_DESCRIP'),
                    'COMMAND_FILE': self.core.Config.Get('COMMAND_FILE_DESCRIP')
                    },
                'Optional': {
                    'REPEAT_DELIM': self.core.Config.Get('REPEAT_DELIM_DESCRIP')
                    }
                },
                self.plugin_info):
            self.core.PluginParams.SetConfig(Args) # Sets the aux plugin arguments as config
            #print "Args="+str(Args)
            self.core.RemoteShell.Open({
                'ConnectVia': self.core.Config.GetResources(
                    'RCE_SBD_Connection'),
                'InitialCommands': None
                },
                self.plugin_info)
            self.core.RemoteShell.RunCommandList(
                self.core.GetFileAsList(Args['COMMAND_FILE']))
            self.core.RemoteShell.Close(self.plugin_info)
            #Content += Core.PluginHelper.DrawCommandDump('Test Command', 'Output', Core.Config.GetResources('LaunchExploit_'+Args['CATEGORY']+"_"+Args['SUBCATEGORY']), PluginInfo, "") # No previous output
        return content
