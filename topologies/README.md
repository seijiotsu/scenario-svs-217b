# How to add new topologies
Go to https://play.ndn.today/ and then make some nodes and edges in a blank graph. Then on the side under "MiniNDN Config:", hit Generate and copy the output and paste into a file in the src directory.

# Building
Run `python3 build.py` to build the topologies into a format understandable by
ndn sim in the `/processed` directory.