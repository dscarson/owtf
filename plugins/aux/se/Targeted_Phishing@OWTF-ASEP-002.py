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
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""


from framework.plugin.plugins import ActivePlugin


class TargetedPhishingPlugin(ActivePlugin):
    """Targeted Phishing Testing plugin"""

    def run(self):
        content = self.__doc__ + ' Results:<br />'
        for args in self.core.PluginParams.GetArgs({
                'Description': self.__doc__,
                'Mandatory': {
                    'EMAIL_TARGET': self.core.Config.Get('EMAIL_TARGET_DESCRIP'),
                    'EMAIL_FROM': self.core.Config.Get('EMAIL_FROM_DESCRIP'),
                    'SMTP_LOGIN': self.core.Config.Get('SMTP_LOGIN_DESCRIP'),
                    'SMTP_PASS': self.core.Config.Get('SMTP_PASS_DESCRIP'),
                    'SMTP_HOST': self.core.Config.Get('SMTP_HOST_DESCRIP'),
                    'SMTP_PORT': self.core.Config.Get('SMTP_PORT_DESCRIP'),
                    'EMAIL_PRIORITY': self.core.Config.Get(
                        'EMAIL_PRIORITY_DESCRIP'),
                    'EMAIL_SUBJECT': self.core.Config.Get(
                        'EMAIL_SUBJECT_DESCRIP'),
                    'EMAIL_BODY': self.core.Config.Get('EMAIL_BODY_DESCRIP'),
                  },
                'Optional': {
                    'EMAIL_ATTACHMENT': self.core.Config.Get(
                        'EMAIL_ATTACHMENT_DESCRIP'),
                    'REPEAT_DELIM': self.core.Config.Get(
                        'REPEAT_DELIM_DESCRIP')},
                },
                self.plugin_info):
            self.core.PluginParams.SetConfig(args) # Update config
            #print "Args="+str(Args)
            if self.core.SMTP.Send(args):
                content += 'Email delivered succcessfully'
            else:
                content += 'Email delivery failed'
            #Content += Core.PluginHelper.DrawCommandDump('Test Command', 'Output', Core.Config.GetResources('SendPhishingAttackviaSET'), PluginInfo, Content)
        return content

