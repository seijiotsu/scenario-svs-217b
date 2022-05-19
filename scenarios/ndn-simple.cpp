/* -*- Mode:C++; c-file-style:"gnu"; indent-tabs-mode:nil; -*- */
/**
 * Copyright (c) 2011-2015  Regents of the University of California.
 *
 * This file is part of ndnSIM. See AUTHORS for complete list of ndnSIM authors and
 * contributors.
 *
 * ndnSIM is free software: you can redistribute it and/or modify it under the terms
 * of the GNU General Public License as published by the Free Software Foundation,
 * either version 3 of the License, or (at your option) any later version.
 *
 * ndnSIM is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
 * without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
 * PURPOSE.  See the GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License along with
 * ndnSIM, e.g., in COPYING.md file.  If not, see <http://www.gnu.org/licenses/>.
 **/

// ndn-simple.cpp

#include "ns3/core-module.h"
#include "ns3/ndnSIM-module.h"
#include "ns3/network-module.h"
#include "ns3/point-to-point-module.h"

namespace ns3 {

int
main(int argc, char* argv[])
{
  // setting default parameters for PointToPoint links and channels
  Config::SetDefault("ns3::PointToPointNetDevice::DataRate",
                     StringValue("10Mbps"));
  Config::SetDefault("ns3::PointToPointChannel::Delay", StringValue("10ms"));
  // Config::SetDefault("ns3::QueueBase::MaxSize", StringValue("20p"));
  // ndn::Interest::setDefaultCanBePrefix(false);
  // Read optional command-line parameters (e.g., enable visualizer with ./waf --run=<> --visualize
  CommandLine cmd;
  cmd.Parse(argc, argv);

  // Creating nodes
  NodeContainer nodes;
  nodes.Create(3);

  // Connecting nodes using two links
  PointToPointHelper p2p;
  p2p.Install(nodes.Get(0), nodes.Get(1));
  p2p.Install(nodes.Get(1), nodes.Get(2));

  // Install NDN stack on all nodes
  ndn::StackHelper ndnHelper;
  ndnHelper.SetDefaultRoutes(true);
  ndnHelper.InstallAll();

  // Choosing forwarding strategy
  ndn::StrategyChoiceHelper::InstallAll("/ndn/svs",
                                        "/localhost/nfd/strategy/multicast");
  ndn::StrategyChoiceHelper::InstallAll("/",
                                        "/localhost/nfd/strategy/best-route");

  // Installing global routing interface on all nodes
  ndn::GlobalRoutingHelper ndnGlobalRoutingHelper;
  ndnGlobalRoutingHelper.InstallAll();

  // Installing applications

  // Consumer
  ndn::AppHelper consumerHelper1("Chat");
  consumerHelper1.SetPrefix("/node1");
  consumerHelper1.SetAttribute("PublishDelayMs", IntegerValue(500));
  auto apps = consumerHelper1.Install(nodes.Get(0));
  apps.Stop(Seconds(10.0));// stop the consumer app at 10 seconds mark
  ndnGlobalRoutingHelper.AddOrigins("/node1", nodes.Get(0));

  ndn::AppHelper consumerHelper2("Chat");
  consumerHelper2.SetPrefix("/node2");
  consumerHelper2.SetAttribute("PublishDelayMs", IntegerValue(1000));
  auto apps2 = consumerHelper2.Install(nodes.Get(2));
  apps2.Start(Seconds(0.04));
  apps2.Stop(Seconds(10.0));// stop the consumer app at 10 seconds mark
  ndnGlobalRoutingHelper.AddOrigins("/node2", nodes.Get(2));


  ndn::FibHelper::AddRoute(nodes.Get(2), "/ndn/svs", nodes.Get(1), 1);
  ndn::FibHelper::AddRoute(nodes.Get(1), "/ndn/svs", nodes.Get(2), 1);
  ndn::FibHelper::AddRoute(nodes.Get(1), "/ndn/svs", nodes.Get(0), 1);
  ndn::FibHelper::AddRoute(nodes.Get(0), "/ndn/svs", nodes.Get(1), 1);

  ndn::GlobalRoutingHelper::CalculateRoutes();

  Simulator::Stop(Seconds(10.0));

  Simulator::Run();
  Simulator::Destroy();

  return 0;
}

}// namespace ns3

int
main(int argc, char* argv[])
{
  return ns3::main(argc, argv);
}
