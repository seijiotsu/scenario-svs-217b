#include <string>
#include <iostream>

#include "../extensions/ndn-svs/topology_helper.cpp"

using ndn::svs::TopologyHelper;

namespace ns3
{
    int main(int argc, char* argv[])
    {
        // Arguments
        std::string graph_path = argv[1];

        // Load the graph
        TopologyHelper topologyHelper(graph_path);

        return 0;
    }
}

int main(int argc, char* argv[])
{
  return ns3::main(argc, argv);
}