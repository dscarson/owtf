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


class SeleniumURLLauncherPlugin(ActivePlugin):
    """Sends a bunch of URLs through selenium"""

    CATEGORIES = ['RCE', 'SQLI', 'XSS', 'CHARSET']

    def run(self):
        self.core.log(
            "WARNING: This plugin requires a small selenium installation, "
            "please run '" + self.core.Config.Get('INSTALL_SCRIPT') +
            "' if you have issues")
        content = self.__doc__ + ' Results:<br />'
        for args in self.core.PluginParams.GetArgs({
                'Description': self.__doc__,
                'Mandatory': {
                    'BASE_URL' : 'The URL to be pre-pended to the tests',
                    'CATEGORY' :
                        'Category to use (i.e. ' +
                        ', '.join(sorted(CATEGORIES))+')',
                    },
                'Optional': {
                    'REPEAT_DELIM': self.core.Config.Get(
                        'REPEAT_DELIM_DESCRIP')
                    }
                },
                self.plugin_info):
            self.core.PluginParams.SetConfig(args)
            input_file = self.core.Config.Get(
                'SELENIUM_URL_VECTORS_' + args['CATEGORY'])
            url_launcher = self.core.selenium.CreateURLLauncher({
                'BASE_URL': args['BASE_URL'],
                'INPUT_FILE': input_file})
            url_launcher.Run()
        return content
