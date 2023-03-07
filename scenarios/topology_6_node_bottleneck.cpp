#include "ns3/core-module.h"
#include "ns3/ndnSIM-module.h"
#include "ns3/network-module.h"
#include "ns3/point-to-point-layout-module.h"
#include "ns3/point-to-point-module.h"
#include <random>

#include "../extensions/ndn-svs/global.h"

namespace ns3 {

int
main(int argc, char* argv[])
{

  //constants and configurations
  int nRows = atoi(argv[1]), nCols = atoi(argv[2]);
  int interPubMsSlow = atoi(argv[3]);
  int interPubMsFast = atoi(argv[4]);
  int nFastPublishNodes = atoi(argv[5]);
  int nRecent = atoi(argv[6]);
  int nRandom = atoi(argv[7]);
  double stopSecond = atoi(argv[8]);
  double dropRate = atof(argv[9]);
  fragmentation_mtu = 0;
  bool frag = argc == 11;
  if (frag){
    fragmentation_mtu = atoi(argv[10]);
  }

  Ptr<UniformRandomVariable> uv = CreateObject<UniformRandomVariable> ();
  uv->SetStream (0);
  RateErrorModel error_model;
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

  assert(nFastPublishNodes <= nRows * nCols);

  //select fast publishers
  std::unordered_set<std::string> fastPublishers;
  std::default_random_engine engine;
  //XXX: todo seed this random engine if you want different results!
  while (fastPublishers.size() < nFastPublishNodes)
  {
    uniform_int_distribution<int> distribution(0, nRows - 1);
    int row = uniform_int_distribution<int>(0, nRows - 1)(engine);
    int col = uniform_int_distribution<int>(0, nCols - 1)(engine);
    string prefix = "/" + std::to_string(row) + "-" + std::to_string(col);
    fastPublishers.insert(prefix);
  }


  // Read optional command-line parameters (e.g., enable visualizer with ./waf --run=<> --visualize
  CommandLine cmd;
  cmd.Parse(argc, argv);

  AnnotatedTopologyReader topologyReader("", 25);
  topologyReader.SetFileName("/home/developer/ndnSIM/ns-3/src/ndnSIM/examples/topologies/topo-6-node.txt");
  topologyReader.Read();

  // Install NDN stack on all nodes
  ndn::StackHelper ndnHelper;
  ndnHelper.InstallAll();

  // Set BestRoute strategy
  ndn::StrategyChoiceHelper::InstallAll("/ndn/svs",
                                        "/localhost/nfd/strategy/multicast");
  ndn::StrategyChoiceHelper::InstallAll("/",
                                        "/localhost/nfd/strategy/best-route");

  // Installing global routing interface on all nodes
  ndn::GlobalRoutingHelper ndnGlobalRoutingHelper;
  ndnGlobalRoutingHelper.InstallAll();

  //install svs application

  //Get "containers" for all nodes
  Ptr<Node> participant1 = Names::Find<Node>("Src1");
  Ptr<Node> participant2 = Names::Find<Node>("Src2");
  Ptr<Node> participant3 = Names::Find<Node>("Rtr1");
  Ptr<Node> participant4 = Names::Find<Node>("Rtr2");
  Ptr<Node> participant5 = Names::Find<Node>("Dst1");
  Ptr<Node> participant6 = Names::Find<Node>("Dst2");

  std::vector<Ptr<Node>> participant_names = { participant1, participant2, participant3, participant4, participant5, participant6 };
  //define prefixes for participants, original code assigned prefixes and randomly chose which of them would be fast publishers
  //in this case, we will use all slow publishers maybe
  string prefix1 = "/participant1";
  string prefix2 = "/participant2";
  string prefix3 = "/participant3";
  string prefix4 = "/participant4";
  string prefix5 = "/participant5";
  string prefix6 = "/participant6";

  std::vector<std::string> participant_prefixes = { prefix1, prefix2, prefix3, prefix4, prefix5, prefix6 };

  for (int i=0; i < participant_names.size(); i++){

    ndn::AppHelper svsHelper("Chat");
    //get prefix and node for current participant
    std::string prefix = participant_prefixes[i];
    Ptr<Node> participant = participant_names[i];
    svsHelper.SetPrefix(prefix);
    svsHelper.SetAttribute(
                "PublishDelayMs",
                IntegerValue(interPubMsSlow));
    svsHelper.SetAttribute("NRecent", IntegerValue(nRecent));
    svsHelper.SetAttribute("NRand", IntegerValue(nRandom));

    ndnGlobalRoutingHelper.AddOrigins(prefix, participant);
    auto apps = svsHelper.Install(participant);
  
    if (i==0){
      apps.Start(Seconds(3));
    }  
    apps.Stop(Seconds(stopSecond));
    

  }
  // Calculate and install FIBs
  ndn::GlobalRoutingHelper::CalculateRoutes();
  for (int i=0; i < participant_names.size(); i++){
    Ptr<Node> participant = participant_names[i];
    switch (i){
      case 0:
        // std::cout << "Case0\n";
        ndn::FibHelper::AddRoute(participant, "/ndn/svs", participant_names[2], 1);
        break;
      case 1:
        // std::cout << "Case 1\n";
        ndn::FibHelper::AddRoute(participant, "/ndn/svs", participant_names[2], 1);
        break;
      case 2:
        // std::cout << "Case 2\n";
        ndn::FibHelper::AddRoute(participant, "/ndn/svs", participant_names[3], 1);
        ndn::FibHelper::AddRoute(participant, "/ndn/svs", participant_names[1], 1);
        ndn::FibHelper::AddRoute(participant, "/ndn/svs", participant_names[0], 1);
        break;
      case 3:
        // std::cout << "Case 3\n";
        ndn::FibHelper::AddRoute(participant, "/ndn/svs", participant_names[4], 1);
        ndn::FibHelper::AddRoute(participant, "/ndn/svs", participant_names[5], 1);
        ndn::FibHelper::AddRoute(participant, "/ndn/svs", participant_names[2], 1);
        break;
      case 4:
        // std::cout << "Case 4\n";
        ndn::FibHelper::AddRoute(participant, "/ndn/svs", participant_names[3], 1);
        break;
      case 5:
        // std::cout << "Case 5\n";
        ndn::FibHelper::AddRoute(participant, "/ndn/svs", participant_names[3], 1);
        break;
    }
  }
  Simulator::Stop(Seconds(stopSecond));

  Simulator::Run();
  Simulator::Destroy();

  std::cout << "SYNC_PACK=" << total_sync_interest_count << std::endl
            << "SYNC_BYTE=" << total_sync_interest_sz << std::endl;

  return 0;
}

}// namespace ns3

int
main(int argc, char* argv[])
{
  return ns3::main(argc, argv);
}
