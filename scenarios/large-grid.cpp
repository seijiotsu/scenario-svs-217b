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
  uv->SetStream (50);
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

  // Creating topology
  PointToPointHelper p2p;
  PointToPointGridHelper grid(nRows, nCols, p2p);
  grid.BoundingBox(100, 100, 200, 200);

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
  for (int row = 0; row < nRows; row++)
  {
    for (int col = 0; col < nCols; col++)
    {
      Ptr<Node> participant = grid.GetNode(row, col);
      std::string prefix =
              "/" + std::to_string(row) + "-" + std::to_string(col);
      bool isFastPublisher = false;
      if (fastPublishers.find(prefix) != fastPublishers.end())
      {
        isFastPublisher = true;
      }
      ndn::AppHelper svsHelper("Chat");
      svsHelper.SetPrefix(prefix);
      svsHelper.SetAttribute(
              "PublishDelayMs",
              IntegerValue(isFastPublisher ? interPubMsFast : interPubMsSlow));
      svsHelper.SetAttribute("NRecent", IntegerValue(nRecent));
      svsHelper.SetAttribute("NRand", IntegerValue(nRandom));

      auto apps = svsHelper.Install(participant);
      if (row == 0 && col == 0){
        apps.Start(Seconds(3));
      }
      apps.Stop(Seconds(stopSecond));
      ndnGlobalRoutingHelper.AddOrigins(prefix, participant);
    }
  }

  // Calculate and install FIBs
  ndn::GlobalRoutingHelper::CalculateRoutes();
  for (int row = 0; row < nRows; row++)
  {
    for (int col = 0; col < nCols; col++)
    {
      Ptr<Node> participant = grid.GetNode(row, col);
      if (row > 0)
      {
        ndn::FibHelper::AddRoute(participant, "/ndn/svs",
                                 grid.GetNode(row - 1, col), 1);
      }
      if (col > 0)
      {
        ndn::FibHelper::AddRoute(participant, "/ndn/svs",
                                 grid.GetNode(row, col - 1), 1);
      }
      if (row < nRows - 1)
      {
        ndn::FibHelper::AddRoute(participant, "/ndn/svs",
                                 grid.GetNode(row + 1, col), 1);
      }
      if (col < nCols - 1)
      {
        ndn::FibHelper::AddRoute(participant, "/ndn/svs",
                                 grid.GetNode(row, col + 1), 1);
      }
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
