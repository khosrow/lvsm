"""
Dummy module to simulate the mib module in snimpy
"""

def load(mib):
	"""dummy load"""
	pass

class SMIException(Exception):
    """SMI related exception. Any exception thrown in this module is
    inherited from this one."""
    pass