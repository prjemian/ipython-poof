
"""
check_limits
"""

__all__ = [
    'check_limits',
    ]

from ..session_logs import logger
logger.info(__file__)


def check_limits(plan):
    """
    Check that a bluesky plan will not move devices outside of their limits.

    Parameters
    ----------
    plan : iterable
        Must yield `Msg` objects
    """
    for msg in plan:
        if msg.command == 'set':
            msg.obj.check_value(msg.args[0])
