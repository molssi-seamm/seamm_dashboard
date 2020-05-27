"""
API calls for the status
"""
import logging


logger = logging.getLogger('__file__')

__all__ = ['status']


def status():
    """The status of the dashboard.

    Currently always 'running', but in the future other
    values may be added.
    """
    return 'running', 200
    
