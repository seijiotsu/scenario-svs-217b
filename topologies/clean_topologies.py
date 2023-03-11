"""
Windows is stupid and uses \r\n for newlines, so it will break your topologies
if you copy-pasted into processed.
"""

import os

for filepath in os.scandir('./processed'):
    with open(filepath, 'r') as hdl:
        data = hdl.read()
        data.replace('\r', '')
    
    with open(filepath, 'w') as hdl:
        hdl.write(data)