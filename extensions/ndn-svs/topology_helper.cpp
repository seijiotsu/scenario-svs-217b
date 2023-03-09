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
                // All the nodes, mapped by index.
                std::vector<std::string> nodes;
                // tuples referencing node names containing the
                // indices of adjacent nodes A and B
                std::vector<std::tuple<int, int>> adjacencies;

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
                        // We have to parse the nodes under "router", and the
                        // links under "link"

                        // STATE 1: "none", or we haven't started parsing the
                        // file yet.
                        if(stage == "none")
                        {
                            std::string token;
                            iss >> token;
                            if(token == "router")
                            {
                                stage = "nodes";
                                continue;
                            }
                        }

                        // STATE 2: "nodes", or we are parsing the file for
                        // node names.
                        if(stage == "nodes")
                        {
                            std::string nodeName;
                            iss >> nodeName;

                            // Edge case: we are out of node names, jump to
                            // stage 3
                            if(nodeName == "link")
                            {
                                stage = "links";
                                continue;
                            }

                            // Edge case: comment or empty
                            if(nodeName.length() == 0 || nodeName[0] == '#')
                            {
                                continue;
                            }

                            // Otherwise, add to our internal datastructures
                            // Remove the trailing ':'
                            nameToIndex[nodeName] = nodes.size();
                            nodes.push_back(nodeName);
                        }

                        // STATE 3: "links". This is where our adjacency links
                        // are! Important!
                        if(stage == "links")
                        {


                            std::string A;
                            std::string B;
                            std::string bandwidth;
                            int metric;
                            std::string delay;
                            int queue;

                            iss >> A >> B >> bandwidth >> metric >> delay >> queue;

                            // Edge case: comment or empty
                            if(A.length() == 0 || A[0] == '#')
                            {
                                continue;
                            }

                            adjacencies.push_back(
                                std::tuple<int, int>(nameToIndex[A], nameToIndex[B]));
                        }
                    }
                }
                
            private:
                // Needed by ns3 in certain places
                std::string m_path = "";

                // Mapping of node names to index
                std::map<std::string, int> nameToIndex;
                
        };
    }
}