#include "../ndn-svs/svsync.hpp"
#include "chat.hpp"
#include "ns3/application.h"
#include "ns3/integer.h"
#include "ns3/ndnSIM-module.h"
#include "ns3/ndnSIM/helper/ndn-stack-helper.hpp"
#include "ns3/string.h"
#include <strstream>

class ProgramPrefix : public Program
{
public:
  ProgramPrefix(const Options& options)
      : Program(options)
  {
    // Use HMAC signing
    ndn::svs::SecurityOptions securityOptions(m_keyChain);
    //securityOptions.interestSigner->signingInfo.setSigningHmacKey("dGhpcyBpcyBhIHNlY3JldCBtZXNzYWdl");

    m_svs = std::make_shared<ndn::svs::SVSync>(
            ndn::Name(m_options.prefix), ndn::Name(m_options.m_id), face,
            std::bind(&ProgramPrefix::onMissingData, this, _1),
            securityOptions);
  }
};

namespace ns3 {
namespace ndn {

// Class inheriting from ns3::Application
class Chat : public Application
{
public:
  static TypeId
  GetTypeId()
  {
    static TypeId tid =
            TypeId("Chat")
                    .SetParent<Application>()
                    .AddConstructor<Chat>()
                    .AddAttribute(
                            "PublishDelayMs", "publish Delay ms",
                            IntegerValue(1000),
                            MakeIntegerAccessor(&Chat::m_publish_delay_ms),
                            MakeIntegerChecker<int64_t>())
                    .AddAttribute("Prefix", "Prefix",
                                  StringValue("default_prefix"),
                                  MakeStringAccessor(&Chat::m_id),
                                  MakeStringChecker());

    return tid;
  }

protected:
  // inherited from Application base class.
  virtual void
  StartApplication()
  {
    Options opt;
    opt.prefix = "/ndn/svs";
    opt.m_id = m_id;
    opt.publish_delay_ms = m_publish_delay_ms;
    m_instance.reset(new ProgramPrefix(opt));
    m_instance->run();
  }

  virtual void
  StopApplication()
  {
    // Stop and destroy the instance of the app
    m_instance.reset();
  }

private:
  std::unique_ptr<ProgramPrefix> m_instance;
  std::string m_id;
  int64_t m_publish_delay_ms;
  //chunks::Producer::Options opts;
};
}// namespace ndn
}// namespace ns3
