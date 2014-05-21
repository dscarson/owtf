import os
from framework.lib.general import PluginAbortException, FrameworkAbortException
from framework.lib.general import log
from framework.db.plugin_manager import TEST_GROUPS


class AbstractPlugin(object):
    """Abstract plugin declaring basics methods."""

    RESOURCES = None

    def __init__(self,
                 core,
                 plugin_info,
                 resources=None,
                 lazy_resources=False,
                 *args, **kwargs):
        """Self-explanatory."""
        # A plugin has a reference to the Core object.
        self.core = core
        # Keep track of the abort
        self.framework_abort = False
        self.plugin_abort = False
        # Keep track of the elapsed time
        self.elapsed_time = None
        # A plugin contains several information like a group, a type, etc.
        self.plugin_info = None
        if AbstractPlugin.is_valid_info(plugin_info):
            self.plugin_info = plugin_info
        else:  # The information are not valid, throw something
            # TODO: Create a custom error maybe?
            raise ValueError(
                "The information of the plugin did not fulfill "
                "the requirements.")
        # Plugin might have a resource which might contains the command that
        # will be run for instance.
        self._lazy_resources = lazy_resources
        self.resources = None
        self.resources_name = resources or self.RESOURCES
        if not self.resources_name is None and not self._lazy_resources:
            self._get_resources(self.resources_name)
        # The ouput of a plugin is saved into its attribute `output` and its
        # type is saved into `type`.
        self.output = None
        self.type = None

    def get_filename_and_extension(self, input_name):
        """From input_name returns a list of its name and its extension.

        Extension is 'txt' by default, except 'html' is found.

        """
        output_name = input_name
        output_extension = 'txt'  # Default extension.
        if input_name.split('.')[-1] in ['html']:
            output_name = input_name[:-5]
            output_extension = 'html'
        return [output_name, output_extension]

    def run(self):
        """Callback function that actually runs the plugin."""
        raise NotImplementedError('A plugin MUST implement the run method.')

    def _get_resources(self, resources_name):
        """Retrieve the resources of the plugin.

        If `resources_name` is a list, the plugin will loads each of its
        elements.

        """
        # If the plugin was configured as lazy, it is now time to load the
        # resources.
        if self.resources is None:
            if isinstance(resources_name, basestring):
                self.resources = self.core.DB.Resource.GetResources(
                    resources_name)
            else:  # Assuming that resources is a list.
                self.resources = self.core.DB.Resource.GetResourceList(
                    resources_name)

    @staticmethod
    def is_valid_info(info):
        """Check that the information of a plugin is correct.

        Currently checks that the plugin's group is valid.

        """
        # Check if a group is specified and if it is a valid one.
        if (not 'group' in info or
                ('group' in info and not info['group'] in TEST_GROUPS)):
            return False
        # TODO: Check the other info.
        # Everything's fine about the information
        return True

    def _init_output_dir(self):
        """Returns the output path of the plugin.

        If the plugin's output directory does not exist, force it's creation.

        """
        # Retrieve the relative path of the plugin output.
        output_dir = self.core.PluginHandler.GetPluginOutputDir(
            self.plugin_info)
        # FULL output path for plugins to use
        self.core.DB.Target.SetPath(
            'PLUGIN_OUTPUT_DIR',
            os.path.join(os.getcwd(), output_dir))
        self.core.Shell.RefreshReplacements()
        # Force the creation of the directory if it does not exist yet.
        self.core.CreateMissingDirs(output_dir)
        self.output_dir = output_dir

    # TODO: Implement research_fingerprint_in_log
    def research_fingerprint_in_log(self):
        self.type = 'FingerprintData'
        self.output = {}
        return (self.dump())

    def dump(self, type='type', output='output'):
        """Return the result of a plugin.

        Generate a dictionary from the attributes `type` and `output` and
        returns a list of it.

        """
        return [dict({type: self.type, output: self.output})]


class ActivePlugin(AbstractPlugin):

    """Active plugin.

    An active plugin is excepted to run shell command.

    """

    def __init__(self,
                 core,
                 plugin_info,
                 resources=None,
                 lazy_resources=False,
                 cmd_intro='Test Command',
                 output_intro='Output',
                 prev_output=None,
                 *args, **kwargs):
        """Self-explanatory."""
        AbstractPlugin.__init__(
            self,
            core,
            plugin_info,
            resources,
            lazy_resources,
            *args, **kwargs)
        self.cmd_modified = None
        self.raw_output = None
        self.cmd_intro = cmd_intro
        self.output_intro = output_intro
        self.prev_output = prev_output
        self._init_output_dir()

    def run_shell_command(self, cmd):
        """Run the shell command of the plugin."""
        if not hasattr(self, 'output_dir'):
            self._init_output_dir()
        # Keep track of the elapsed time.
        self.core.Timer.StartTimer('run_shell_command')
        self.cmd_modified = self.core.Shell.GetModifiedShellCommand(
            cmd,
            self.output_dir)
        # Run the shell command.
        try:
            self.raw_output = self.core.Shell.shell_exec_monitor(
                self.cmd_modified)
        except PluginAbortException as partial_output:
            self.raw_output = str(partial_output.parameter)
            self.plugin_abort = True
        except FrameworkAbortException as partial_output:
            self.raw_output = str(partial_output)
            self.framework_abort = True
        # Save the elapsed time.
        self.elapsed_time = self.core.Timer.GetElapsedTimeAsStr(
            'run_shell_command')
        log('Time=' + self.elapsed_time)

    def run(self):
        """Callback function which is run by OWTF.

        Default ActivePlugin behaviour.
        This function can be overrided by the user when declaring an
        ActivePlugin. That way, the user can take into account specific usages.

        """
        return self.command_run()

    def command_run(self, resources=None):
        """Run the plugin command(s) and format its output."""
        self.resources_name = resources or self.resources_name
        if self.resources is None:
            self._get_resources(self.resources_name)
        output_list = []
        # A plugin might use several resources.
        for name, cmd in self.resources:
            self.run_shell_command(cmd)
            self.type = 'CommandDump'
            self.output = {
                'Name': self.get_filename_and_extension(name)[0],
                'CommandIntro': self.cmd_intro,
                'ModifiedCommand': self.cmd_modified,
                'RelativeFilePath': self.core.PluginHandler.DumpOutputFile(
                    name,
                    self.raw_output,
                    self.plugin_info,
                    RelativePath=True),
                'OutputIntro': self.output_intro,
                'TimeStr': self.elapsed_time}
            plugin_output = self.dump()

            # This command returns URLs for processing
            if name == self.core.Config.FrameworkConfigGet('EXTRACT_URLS_RESERVED_RESOURCE_NAME'):
                plugin_output = self.log_urls()

            if self.plugin_abort:
                raise PluginAbortException(self.prev_output + plugin_output)
            if self.framework_abort:
                raise FrameworkAbortException(self.prev_output + plugin_output)

            output_list += plugin_output
        return (output_list)

    def log_urls(self):
        """Retrieve the URLs that have beend visited already."""
        # Keep track of the elapsed time.
        self.core.Timer.StartTimer('log_urls')
        urls = self.raw_output.strip().split('\n')
        self.core.DB.URL.ImportUrls(urls)
        nb_found = 0
        visit_urls = False
        # TODO: Whether or not active testing will depend on the user profile
        # ;). Have cool ideas for profile names
        if True:
            visit_urls = True
            nb_found = sum([
                transaction.Found
                for transaction in self.core.Requester.GetTransactions(
                    True, self.core.DB.URL.GetURLsToVisit())
                ])
        self.elapsed_time = self.core.Timer.GetElapsedTimeAsStr('log_urls')
        log('Spider/URL scraper time=' + self.elapsed_time)
        self.type = 'URLsFromStr'
        self.output = {
            'TimerStr': self.elapsed_time,
            'VisitUrls': visit_urls,
            'URLList': urls,
            'NumFound': nb_found}
        return (self.dump())


class PassivePlugin(AbstractPlugin):
    """Passive plugin."""

    NAME = None

    def __init__(self,
                 core,
                 plugin_info,
                 resources=None,
                 lazy_resources=True,
                 name=None,
                 *args, **kwargs):
        """Self-explanatory."""
        self.name = name or self.NAME
        AbstractPlugin.__init__(
            self,
            core,
            plugin_info,
            resources,
            lazy_resources
            *args, **kwargs)

    def _get_resources(self, resources_name):
        """Retrieve the resources of a passive plugin.

        A passive plugin can be ResourceLinkList (one resource only) or
        TabbedResourceLinkList (several resources).

        """
        if self.resources is None:
            if self.name is None:
                if isinstance(resources_name, dict):
                    self.type = 'TabbedResourceLinkList'
                    resources = []
                    for link_name, resource_name in resources_name.items():
                        resources.append([
                            link_name,
                            self.core.DB.Resource.GetResources(resource_name)])
                    self.resources = resources
            else:
                if isinstance(resources_name, basestring):
                    self.type = 'ResourceLinkList'
                    self.resources = self.core.DB.Resource.GetResources(
                        resources_name)

    def suggest_command_box(self, command_category_list, header=''):
        """Display a command box to suggest some options to the user."""
        self._init_output_dir()
        self.type = 'SuggestedCommandBox'
        self.output = {
            'PluginOutputDir': self.output_dir,
            'CommandCategoryList': command_category_list,
            'Header': header}
        return (self.dump())

    def run(self):
        """Run the passive plugin."""
        self.type = 'ResourceLinkList'
        self.output = {'ResourceList': None}
        if not self.name is None:
            self.output['ResourceListName'] = self.name
        self._get_resources(self.resources_name)
        self.output['ResourceList'] = self.resources
        return (self.dump())


class SemiPassivePlugin(ActivePlugin):
    """Semi Passive plugin."""

    RESOURCES = None

    def __init__(self, *args, **kwargs):
        """Self-explanatory."""
        ActivePlugin.__init__(self, *args, **kwargs)

    def get_transaction_table(self, transaction_list):
        """Add the transaction IDs to the output.

        The reporter will then be able to fetch the transaction from the DB.

        """
        transaction_ids = [
            transaction.GetID() for transaction in transaction_list]
        self.type = 'TransactionTableFromIDs'
        self.output = {'TransactionIDs': transaction_ids}
        return (self.dump())

    def get_transaction_table_for_url_list(self,
                                           url_types=None,
                                           use_cache=True,
                                           method='',
                                           data=''):
        """Ensure that the URLs from the list are visited.

        Does not save the transaction IDs into the output.

        """
        if url_types is None:
            url_types = ['TARGET_URL', 'TOP_URL']
        url_list = self.core.DB.Target.GetAsList(url_types)
        self.core.Requester.GetTransactions(use_cache, url_list, method, data)
        self.type = 'TransactionTableForURLList'
        self.output = {
            'UseCache': use_cache,
            'URLList': url_list,
            'Method': method,
            'Data': data}
        return (self.dump())


class GrepPlugin(AbstractPlugin):
    """Grep Passive plugin."""

    RE_HEADER = None
    RE_BODY = None

    def __init__(self,
                 core,
                 plugin_info,
                 re_header=None,
                 re_body=None,
                 resources=None,
                 lazy_resources=True,
                 *args, **kwargs):
        """Self-explanatory."""
        self.re_header = re_header or self.RE_HEADER
        self.re_body = re_body or self.RE_BODY
        AbstractPlugin.__init__(
            self,
            core,
            plugin_info,
            resources,
            lazy_resources,
            *args, **kwargs)

    def html_string(self, html_string):
        self.type = 'HtmlString'
        self.output = {'String': html_string}
        return (self.dump())

    def find_top_transactions_by_speed(self, order="Desc"):
        self.type = 'TopTransactionsBySpeed'
        self.output = {'Order': Order}
        return (self.dump())

    def find_response_header_matches(self, re_header=None):
        re_header = re_header or self.re_header
        if isinstance(re_header, basestring):
            re_header = [re_header]
        result = []
        for re_name in re_header:
            self.type = 'ResponseHeaderMatches'
            self.output = {'ResponseRegexpName': re_name}
            result.append(self.dump())
        return result

    def find_response_body_matches(self, re_body=None):
        re_body = re_body or self.re_body
        if isinstance(re_body, basestring):
            re_body = [re_body]
        result = []
        for re_name in re_body:
            self.type = 'ResponseBodyMatches'
            self.output = {'ResponseRegexpName': re_name}
            result.append(self.dump())
        return result


class ExternalPlugin(AbstractPlugin):
    """External Passive plugin."""

    def __init__(self, *args, **kwargs):
        """Self-explanatory."""
        AbstractPlugin.__init__(self, *args, **kwargs)
