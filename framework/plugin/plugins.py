import os
from framework.lib.general import PluginAbortException, FrameworkAbortException
from framework.lib.general import WipeBadCharsForFilename as clean_filename
from framework.lib.general import log


# TODO: Checks if already declared elsewhere
# Defines the valid group for a plugin
GROUP_WEB = 'web'
GROUP_NET = 'net'
GROUP_AUX = 'aux'
VALID_GROUPS = [
    GROUP_WEB,
    GROUP_NET,
    GROUP_AUX]


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

    def __init__(self, core, plugin_info, resources=None, *args, **kwargs):
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
                "The information of the plugin didn't not fulfill "
                "the requirements.")
        # Plugin might have a resource which might contains the command that
        # will be run for instance.
        self.resources = resources or self.RESOURCES
        if not self.resources is None:
            if isinstance(self.resources, basestring):
                self.resources = self.core.DB.Resource.GetResources(
                    self.resources)
            else:  # Assuming that resources is a list.
                self.resources = self.core.DB.Resource.GetResourceList(
                    self.resources)
        # The ouput of a plugin is saved into its attribute `output` and its
        # type is saved into `type`.
        self.output = None
        self.type = None

    def run(self):
        """Callback function that actually runs the plugin."""
        raise NotImplementedError('A plugin MUST implement the run method.')

    @staticmethod
    def is_valid_info(info):
        """Check that the information of a plugin is correct."""
        # Check if a group is specified and if it is a valid one.
        if (not 'group' in info or
                ('group' in info and not info['group'] in VALID_GROUPS)):
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
        if self.info['group'] in [GROUP_WEB, GROUP_NET]:
            base_path = self.core.DB.Target.GetPath('PARTIAL_URL_OUTPUT_PATH')
        elif self.info['group'] == GROUP_AUX:
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


class AbstractRunCommandPlugin(AbstractPlugin):
    """Abstract plugin that runs a shell command."""

    def __init__(self, *args, **kwargs):
        """Self-explanatory."""
        AbstractPlugin.__init__(self, *args, **kwargs)
        self.cmd_modified = None
        self.raw_output = None

    def run_command(self, cmd):
        """Run the shell command of the plugin."""
        if not hasattr(self, 'output_dir'):
            self._init_output_dir()
        # Keep track of the elapsed time.
        self.core.Timer.StartTimer('run_command')
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
        self.elapsed_time = self.core.Timer.GetElapsedTimeAsStr('run_command')
        log('Time=' + self.elapsed_time)


class ActivePlugin(AbstractRunCommandPlugin):
    """Active plugin."""

    def __init__(self,
                 core,
                 plugin_info,
                 resources=None,
                 cmd_intro='Test command',
                 output_intro='Output',
                 prev_output=None,
                 *args, **kwargs):
        """Self-explanatory."""
        AbstractRunCommandPlugin.__init__(
            self,
            core,
            plugin_info,
            resources,
            *args, **kwargs)
        self.cmd_intro = cmd_intro
        self.output_intro = output_intro
        self.prev_output = prev_output
        self._init_output_dir()

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
            self.run_command(cmd)
            self.type = 'CommandDump'
            self.output = {
                'Name': None,  # TODO: Write GetCommandOutputFileNameAndExtension
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
    """Passive plugin."""

    def __init__(self, *args, **kwargs):
        """Self-explanatory."""
        AbstractPlugin.__init__(self, *args, **kwargs)


class SemiPassivePlugin(AbstractPlugin):
    """Semi Passive plugin."""

    def __init__(self, *args, **kwargs):
        """Self-explanatory."""
        AbstractPlugin.__init__(self, *args, **kwargs)


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