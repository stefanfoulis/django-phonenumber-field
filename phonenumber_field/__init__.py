try:
    from .version import version
except ImportError:
    # The version module is written by setuptools_scm when packaging.
    __version__ = None
else:
    __version__ = version
