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


class AbstractPlugin(object):
    """Abstract plugin declaring basics methods."""

    def __init__(self, core, plugin_info, resources=None, *args, **kwargs):
        """Self-explanatory."""
        # A plugin has a reference to the Core object.
        self.core = core
        # A plugin contains several information like a group, a type, etc.
        self.info = None
        if check_info(plugin_info):
            self.info = plugin_info
        else:  # The information are not valid, throw something
            # TODO: Create a custom error maybe?
            raise ValueError(
                "The information of the plugin didn't not fulfill "
                "the requirements.")
        # Plugin might have a resource which might contains the command that
        # will be run for instance.
        self.resources = resources
        if not self.resources is None:
            self.resources = self.core.DB.Resource.GetResources(self.resources)

    def run(self):
        """Callback function that actually runs the plugin."""
        raise NotImplementedError('A plugin MUST implement the run method.')

    @staticmethod
    def check_info(info):
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

    @classmethod
    def get_output_dir(cls):
        """According to the plugin group and type, returns its path."""
        raise NotImplementedError('get_output_dir must be implemented')


class ActivePlugin(AbstractPlugin):
    """Active plugin."""

    def __init__(self, *args, **kwargs):
        """Self-explanatory."""
        AbstractPlugin.__init__(self, *args, **kwargs)


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
