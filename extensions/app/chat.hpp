/* -*- Mode: C++; c-file-style: "gnu"; indent-tabs-mode:nil -*- */
/*
 * Copyright (c) 2012-2022 University of California, Los Angeles
 *
 * This file is part of ndn-svs, synchronization library for distributed realtime
 * applications for NDN.
 *
 * ndn-svs library is free software: you can redistribute it and/or modify it under the
 * terms of the GNU Lesser General Public License as published by the Free Software
 * Foundation, in version 2.1 of the License.
 *
 * ndn-svs library is distributed in the hope that it will be useful, but WITHOUT ANY
 * WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
 * PARTICULAR PURPOSE. See the GNU Lesser General Public License for more details.
 */

#include <functional>
#include <iostream>
#include <random>
#include <string>
#include <vector>

#include "../ndn-svs/svsync-base.hpp"

struct Options
{
  std::string prefix;
  std::string m_id;
  int64_t publish_delay_ms;
  int64_t nRand;
  int64_t nRecent;
};

class Program
{
public:
  Program(const Options& options)
      : m_options(options)
      , m_scheduler(face.getIoService())
  {
    std::cerr << "SVS client " << m_options.m_id << " started" << "\n";
    m_signingInfo.setSha256Signing();
  }

  void
  fetchLoop()
  {
    publishMsg("msg from " + m_options.m_id);
    std::uniform_int_distribution<int64_t> rd(-m_options.publish_delay_ms / 4,
                                              m_options.publish_delay_ms / 4);
    m_scheduler.schedule(ndn::time::milliseconds(m_options.publish_delay_ms +
                                                 rd(m_random_engine)),
                         [this] { fetchLoop(); });
  }

  void
  run()
  {
    m_random_engine.seed(std::hash<std::string>()(m_options.m_id));
    fetchLoop();
    face.processEvents();
  }

protected:
  void
  onMissingData(const std::vector<ndn::svs::MissingDataInfo>& v)
  {
    for (size_t i = 0; i < v.size(); i++)
    {
      for (ndn::svs::SeqNo s = v[i].low; s <= v[i].high; ++s)
      {
        ndn::svs::NodeID nid = v[i].nodeId;
        std::cout << std::fixed <<
                ndn::time::steady_clock::now().time_since_epoch().count() / 1e6 << "," <<
                m_options.m_id << "," <<
                "RECV," <<
                nid.toUri() << "::" << s <<
            std::endl << std::scientific;
      }
    }
  }

  void
  publishMsg(const std::string& msg)
  {
    // Content block
    auto block = ndn::encoding::makeBinaryBlock(ndn::tlv::Content, msg.data(),
                                                msg.size());
    auto seq = m_svs->publishData(block, ndn::time::milliseconds(5000));

    std::cout << std::fixed <<
        ndn::time::steady_clock::now().time_since_epoch().count() / 1e6 << "," <<
        m_options.m_id << "," <<
        "PUB," <<
        m_options.m_id << "::" << seq <<
      std::endl << std::scientific;
  }

public:
  const Options m_options;
  ndn::Face face;
  std::shared_ptr<ndn::svs::SVSyncBase> m_svs;
  ndn::KeyChain m_keyChain;
  ndn::security::SigningInfo m_signingInfo;
  ndn::Scheduler m_scheduler;
  std::default_random_engine m_random_engine;
};

template<typename T>
int
callMain(int argc, char** argv)
{
  if (argc != 2)
  {
    std::cout << "Usage: client <prefix>" << std::endl;
    exit(1);
  }

  Options opt;
  opt.prefix = "/ndn/svs";
  opt.m_id = argv[1];

  T program(opt);
  program.run();
  return 0;
}
