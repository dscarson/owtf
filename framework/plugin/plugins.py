import os
import re
from framework.lib.general import PluginAbortException, FrameworkAbortException
from framework.lib.general import WipeBadCharsForFilename as clean_filename
from framework.lib.general import log
from framework.db.plugin_manager import WEB_GROUP, NET_GROUP, AUX_GROUP, \
                                        TEST_GROUPS


# TODO: Checks if already declared elsewhere
# Defines the valid type for a plugin
PLUGIN_ABSTRACT = 'abstract'
PLUGIN_ACTIVE = 'active'
PLUGIN_PASSIVE = 'passive'
PLUGIN_SEMI_PASSIVE = 'semi_passive'
PLUGIN_GREP = 'grep'
PLUGIN_EXTERNAL = 'external'
VALID_TYPES = [
    PLUGIN_ABSTRACT,
    PLUGIN_ACTIVE,
    PLUGIN_PASSIVE,
    PLUGIN_SEMI_PASSIVE,
    PLUGIN_GREP,
    PLUGIN_EXTERNAL]


# TODO: Might be pertinent to inherit AbstractPlugin from dict because of the
# `plugin_output`.
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
        self.info = None
        if AbstractPlugin.is_valid_info(plugin_info):
            self.info = plugin_info
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

    # TODO: Write the docstring.
    def get_filename_and_extension(self, input_name):
        output_name = input_name
        output_extension = 'txt'
        if input_name.split('.')[-1] in ['html']:
            output_name = input_name[:-5]
            output_extension = 'html'
        return [output_name, output_extension]

    def run(self):
        """Callback function that actually runs the plugin."""
        raise NotImplementedError('A plugin MUST implement the run method.')

    def _get_resources(self, resources_name):
        """Retrieve the resources of the plugin."""
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
        """Check that the information of a plugin is correct."""
        # Check if a group is specified and if it is a valid one.
        if (not 'group' in info or
                ('group' in info and not info['group'] in TEST_GROUPS)):
            return False
        # Check if a type is specified and if it is a valid one.
        if (not 'type' in info or
                ('type' in info and not info['type'] in VALID_TYPES)):
            return False
        # TODO: Check the other info.
        # Everything's fine about the information
        return True

    def _init_output_dir(self):
        """Returns the output path of the plugin."""
        # Retrieve the relative path of the plugin output.
        base_path = ''
        if self.info['group'] in [WEB_GROUP, NET_GROUP]:
            base_path = self.core.DB.Target.GetPath('PARTIAL_URL_OUTPUT_PATH')
        elif self.info['group'] == AUX_GROUP:
            base_path = self.core.Config.Get('AUX_OUTPUT_PATH')
        output_dir = os.path.join(
            base_path,
            os.path.join(
                clean_filename(self.info['title']), self.info['type'])
            )
        # FULL output path for plugins to use
        self.core.DB.Target.SetPath(
            'PLUGIN_OUTPUT_DIR',
            os.path.join(os.getcwd(), output_dir))
        # Force the creation of the directory if it does not exist yet.
        self.core.CreateMissingDirs(output_dir)
        self.output_dir = output_dir

    def dump(self, type='type', output='output'):
        """Return the result of a plugin.

        Generate a dictionary from the attributes `type` and `output` and
        returns a list of it.

        """
        return [dict({type: self.type, output: self.output})]


class ActivePlugin(AbstractPlugin):
    """Active plugin."""

    def __init__(self,
                 core,
                 plugin_info,
                 resources=None,
                 lazy_resources=False,
                 cmd_intro='Test command',
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

    # TODO: This function looks messy! It should be modified
    def command_run(self):
        """Run the plugin command and format its output."""
        output_list = []
        for name, cmd in self.resources:
            self.run_shell_command(cmd)
            self.type = 'CommandDump'
            self.output = {
                'Name': self.get_filename_and_extension(name)[0],
                'CommandIntro': self.cmd_intro,
                'ModifiedCommand': self.cmd_modified,
                'RelativeFilePath': self.core.PluginHandler.DumpOuputFile(
                    name,
                    self.raw_output,
                    self.info,
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

    # TODO: Write the doc string.
    def log_urls(self):
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
    """Passive plugin using link lists."""

    NAME = None

    def __init__(self,
                 core,
                 plugin_info,
                 resources=None,
                 lazy_resources=True,
                 name=None,
                 *args, **kwargs):
        """Self-explanatory."""
        AbstractPlugin.__init__(
            self,
            core,
            plugin_info,
            resources,
            lazy_resources
            *args, **kwargs)
        self.name = name or self.NAME

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
                if isinstance(resource_name, basestring):
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
        self.output = {'ResourceList': None}
        if not self.name is None:
            self.output['ResourceListName'] = self.name
        self._get_resources(self.resources_name)
        self.output['ResourceList'] = self.resources
        return (self.dump())


# TODO: Multiple inheritance is most of the time due to bad design. Should have
# a look on how to change the plugin class hierarchy in order to avoid multiple
# inheritance.
class SemiPassivePlugin(ActivePlugin, PassivePlugin):
    """Semi Passive plugin."""

    def __init__(self, *args, **kwargs):
        """Self-explanatory."""
        AbstractPlugin.__init__(self, *args, **kwargs)

    # TODO: Implement research_fingerprint_in_log
    def research_fingerprint_in_log(self):
        pass

    def get_transaction_table(self, transaction_list):
        """Add the transaction IDs to the output.

        The reporter will then be able to fetch the transaction from the DB.

        """
        transaction_ids = [
            transaction.GetId() for transaction in transaction_list]
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

    def __init__(self, *args, **kwargs):
        """Self-explanatory."""
        AbstractPlugin.__init__(self, *args, **kwargs)


class ExternalPlugin(AbstractPlugin):
    """External Passive plugin."""

    def __init__(self, *args, **kwargs):
        """Self-explanatory."""
        AbstractPlugin.__init__(self, *args, **kwargs)
