#!/usr/bin/env python
"""

owtf is an OWASP+PTES-focused try to unite great tools and facilitate pentests
Copyright (c) 2011, Abraham Aranguren <name.surname@gmail.com>
Twitter: @7a_ http://7-a.org
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

Consists of owtf process class and its manager

"""
import logging
from multiprocessing import Process, current_process, Queue


class OWTFProcess(Process):
    """
    Implementing own proxy of Process for better control of processes launched
    from OWTF both while creating and terminating the processes
    """
    def __init__(self, core, **kwargs):
        """
        Ideally not to override this but can be done if needed. If overridden
        please give a call to super() and make sure you run this
        """
        self.core = core  # Attach core
        self.poison_q = Queue()
        self._process = None
        for key in kwargs.keys():  # Attach all kwargs to self
            setattr(self, key, kwargs.get(key, None))
        super(OWTFProcess, self).__init__()

    def make_daemon(self):
        """
        Method used to set daemon value to true
        """
        self.daemon = True

    def initialize(self, **kwargs):
        """
        Supposed to be overridden if user wants to initialize something
        """
        pass

    def run(self):
        """
        This method must not be overridden by user
        + Set proper logger with file handler and Formatter
        + Launch process specific code
        """
        # ------ DB Reinitialization ------ #
        self.core.DB.create_session()
        # ------ Logging initialization ------ #
        self.core.enable_logging()
        # - Finally run process specific code - #
        self.pseudo_run()

    def pseudo_run(self):
        """
        This method must be overridden by user with the process related code
        """
        pass
