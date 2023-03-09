//
// Parses the output of https://play.ndn.today/ (use the 'Generate' button under "MiniNDN Config:")
//

#include <string>
#include <vector>
#include <tuple>
#include <iostream>
#include <sstream>
#include <fstream>
#include <map>

namespace ndn
{
    namespace svs
    {
        class TopologyHelper
        {
            public:
                TopologyHelper(std::string filepath)
                {
                    // Read the input file
                    std::ifstream infile(filepath);
                    std::string line;
                    std::string stage = "none";
                    while(std::getline(infile, line))
                    {
                        std::istringstream iss(line);

                        //
                        // We have to parse the [nodes], the [switches], and the [links]. [switches] should be empty.
                        // We implement a simple state machine.
                        //

                        // STATE 1: "none", or we haven't started parsing the file yet.
                        if(stage == "none")
                        {
                            std::string token;
                            iss >> token;
                            if(token == "[nodes]")
                            {
                                stage = "nodes";
                                continue;
                            }
                        }

                        // STATE 2: "nodes", or we are parsing the file for nodes.
                        if(stage == "nodes")
                        {
                            std::string nodeName;
                            iss >> nodeName;

                            // Edge case: we are out of node names, jump to stage 3
                            if(nodeName == "[switches]")
                            {
                                stage = "switches";
                                continue;
                            }

                            // Otherwise, add to our internal datastructures
                            // Remove the trailing ':'
                            nodeName = nodeName.substr(0, nodeName.length() - 1);
                            nameToIndex[nodeName] = nodes.size();
                            nodes.push_back(nodeName);
                        }

                        // STATE 3: "switches", which we don't support. So just skip over them.
                        if(stage == "switches")
                        {
                            std::string token;
                            iss >> token;

                            if(token == "[links]")
                            {
                                stage = "links";
                                continue;
                            }
                        }

                        // STATE 4: "links". This is where our adjacency links are! Important!
                        if(stage == "links")
                        {
                            std::string nodes, delay;
                            iss >> nodes;
                            iss >> delay;

                            int A, B, delay_ms;
                            A = nameToIndex[nodes.substr(0, nodes.find(":"))];
                            B = nameToIndex[nodes.substr(nodes.find(":") + 1, nodes.length())];
                            delay_ms = atoi(delay.substr(6, delay.length() - 2).c_str()); // always of the format "delay=Xms"

                            adjacencies.push_back(std::tuple<int, int, int>(A, B, delay_ms));
                        }
                    }
                }
                
            private:
                // All the nodes, mapped by index.
                std::vector<std::string> nodes;

                // Mapping of node names to index
                std::map<std::string, int> nameToIndex;
                
                // (index, index) tuples referencing `nodes` containing the indexes of the adjacent nodes A and B,
                // as well as the delay for this link in milliseconds.
                std::vector<std::tuple<int, int, int>> adjacencies;
        };
    }
}