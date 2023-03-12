#include <string>
#include <iostream>
#include <random>
#include <tuple>

#include "ns3/core-module.h"
#include "ns3/ndnSIM-module.h"
#include "ns3/network-module.h"
#include "ns3/point-to-point-layout-module.h"
#include "ns3/point-to-point-module.h"

#include "../extensions/ndn-svs/topology_helper.cpp"
#include "../extensions/ndn-svs/global.h"

using ndn::svs::TopologyHelper;

namespace ns3
{
  RateErrorModel error_model;
  ndn::StackHelper ndnHelper;
  ndn::GlobalRoutingHelper ndnGlobalRoutingHelper;

  void configureDatalinks(double dropRate)
  {
    Ptr<UniformRandomVariable> uv = CreateObject<UniformRandomVariable>();
    uv->SetStream(0);
    error_model.SetRandomVariable(uv);
    error_model.SetUnit(RateErrorModel::ERROR_UNIT_PACKET);
    error_model.SetRate(dropRate);

    //pkt drop rate
    Config::SetDefault("ns3::PointToPointNetDevice::ReceiveErrorModel", PointerValue(&error_model));
    // Setting default parameters for PointToPoint links and channels
    Config::SetDefault("ns3::PointToPointNetDevice::DataRate",
                      StringValue("50Mbps"));
    Config::SetDefault("ns3::PointToPointChannel::Delay", StringValue("5ms"));
    // Config::SetDefault("ns3::QueueBase::MaxSize", StringValue("1000p"));
  }

  void installNDN()
  {
    ndnHelper.InstallAll();

    ndn::StrategyChoiceHelper::InstallAll("/ndn/svs",
                                          "/localhost/nfd/strategy/multicast");
    ndn::StrategyChoiceHelper::InstallAll("/",
                                          "/localhost/nfd/strategy/best-route");

    ndnGlobalRoutingHelper.InstallAll();
  }

  void installSVS(ndn::AppHelper& svsHelper, std::vector<Ptr<Node>> participants,
    std::vector<std::string> prefixes, int interPubMsSlow, int nRecent,
    int nRandom, double stopSecond)
  {
    for (int i=0; i < participants.size(); i++){

      //get prefix and node for current participant
      std::string prefix = prefixes[i];
      Ptr<Node> participant = participants[i];
      svsHelper.SetPrefix(prefix);
      svsHelper.SetAttribute(
                  "PublishDelayMs",
                  IntegerValue(interPubMsSlow));
      svsHelper.SetAttribute("NRecent", IntegerValue(nRecent));
      svsHelper.SetAttribute("NRand", IntegerValue(nRandom));

      ndnGlobalRoutingHelper.AddOrigins(prefix, participant);
      auto apps = svsHelper.Install(participant);
      
      apps.Stop(Seconds(stopSecond));
    }
  }

  int main(int argc, char* argv[])
  {
    //
    // Initial configuration
    //
    // Where the topology is kept
    std::string filepath = argv[1];
    int nRandom = atoi(argv[2]);
    // The number of milliseconds in between publishing a new sync interest
    // for each node
    // The number of recent states in each sync interest
    int nRecent = atoi(argv[3]);
    // The number of random states in each sync interest
    int publishRateMs = atoi(argv[4]);
    // How many seconds to simulate
    double stopSecond = atoi(argv[5]);
    // The percent of packets to drop
    double dropRate = atof(argv[6]);
    // We don't need to worry about this; it's not something that specifies
    // the size of the rand-recent state vector, but rather specifies the size
    // of the MTU when conducting full fragmentation experiments (read up on the
    // paper to understand what this is)
    // See fragmentation.cpp if you want an implementation of this.
    fragmentation_mtu = 0;

    configureDatalinks(dropRate);

    // Read in the topology. The nodes will be added into the 'system' via
    // AnnotatedTopologyReader, I'm not really sure how or where, but we will
    // be able to access them with Names::Find. And TopologyHelper is a class
    // that I (Seiji) wrote to enable easy access to all of the nodes and links
    // specified in the file.
    AnnotatedTopologyReader topologyReader("", 25);
    topologyReader.SetFileName(filepath);
    topologyReader.Read();
    TopologyHelper topologyHelper(filepath);

    installNDN();

    // Get the objects for all the participants. I don't know if this is O(1) or
    // not, so I'm going to cache them here rather than just using Names::Find
    // everywhere in the code.
    std::vector<Ptr<Node>> participants;
    for(std::string name : topologyHelper.nodes)
    {
      participants.push_back(Names::Find<Node>(name));
    }

    // Generate prefixes for the participants. Just use a simple '/' before
    // their names, I think this should work.
    std::vector<std::string> participant_prefixes;
    for(std::string name : topologyHelper.nodes)
    {
      participant_prefixes.push_back("/" + name);
    }

    ndn::AppHelper svsHelper("Chat");
    installSVS(svsHelper, participants, participant_prefixes, publishRateMs,
      nRecent, nRandom, stopSecond);

    // Finalize routes
    ndn::GlobalRoutingHelper::CalculateRoutes();
    for(std::tuple<int, int> adjacency : topologyHelper.adjacencies)
    {
      Ptr<Node> A = participants[std::get<0>(adjacency)];
      Ptr<Node> B = participants[std::get<1>(adjacency)];

      ndn::FibHelper::AddRoute(A, "/ndn/svs", B, 1);
      ndn::FibHelper::AddRoute(B, "/ndn/svs", A, 1);
    }

    // Finally, run the simulation.
    Simulator::Stop(Seconds(stopSecond));
    Simulator::Run();
    Simulator::Destroy();

    // Print other statistics
    std::cout << "SYNC_PACK=" << total_sync_interest_count << std::endl
              << "SYNC_BYTE=" << total_sync_interest_sz << std::endl;

    return 0;
  }
}

int main(int argc, char* argv[])
{
  return ns3::main(argc, argv);
}