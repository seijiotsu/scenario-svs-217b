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

#include <iostream>
#include <string>
#include <thread>
#include <vector>

#include "../ndn-svs/svsync-base.hpp"

struct Options
{
  std::string prefix;
  std::string m_id;
};

class Program
{
public:
  Program(const Options &options)
    : m_options(options), m_scheduler(face.getIoService())
  {
    std::cerr << "SVS client " << m_options.m_id << "started" << std::endl;
    m_signingInfo.setSha256Signing();
  }

  void
  run()
  {

    m_scheduler.schedule(ndn::time::milliseconds(100), [this] { publishMsg("testmsg1 from "+m_options.m_id); });

    m_scheduler.schedule(ndn::time::milliseconds(300), [this] {publishMsg("testmsg2 from "+m_options.m_id); });

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
        m_svs->fetchData(nid, s, [this,nid] (const ndn::Data& data)
          {
            const std::string content(reinterpret_cast<const char*>(data.getContent().value()),
                                      data.getContent().value_size());
            std::cout <<m_options.m_id <<" received data#" << data.getName()[-1].toNumber() <<" from:"<<data.getName()[0]  << " at "<< ndn::time::steady_clock::now()<< std::endl;
          });
      }
    }
  }

  void
  publishMsg(const std::string& msg)
  {
    // Content block
    auto block = ndn::encoding::makeBinaryBlock(ndn::tlv::Content, msg.data(), msg.size());
    auto seq = m_svs->publishData(block, ndn::time::milliseconds(5000));
    std::cout <<m_options.m_id <<" publish data#" << seq <<" at "<< ndn::time::steady_clock::now()<< std::endl;
  }

public:
  const Options m_options;
  ndn::Face face;
  std::shared_ptr<ndn::svs::SVSyncBase> m_svs;
  ndn::KeyChain m_keyChain;
  ndn::security::SigningInfo m_signingInfo;
  ndn::Scheduler m_scheduler;
};

template <typename T>
int
callMain(int argc, char **argv)
{
  if (argc != 2) {
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
