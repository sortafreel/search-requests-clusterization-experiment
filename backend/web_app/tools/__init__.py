class RetryableException(Exception):
    """
    Raise when there's a reason to retry the exception through Celetry
    to get better results. Don't raise for 100% failed state.
    """
