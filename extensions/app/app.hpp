#include "ns3/ndnSIM/helper/ndn-stack-helper.hpp"
#include "ns3/ndnSIM-module.h"
#include "ns3/application.h"
#include "ns3/integer.h"
#include "ns3/string.h"
#include "chat.hpp"
#include "../ndn-svs/svsync.hpp"
#include <strstream>

class ProgramPrefix : public Program
{
public:
  ProgramPrefix(const Options &options) : Program(options)
  {
    // Use HMAC signing
    ndn::svs::SecurityOptions securityOptions(m_keyChain);
    //securityOptions.interestSigner->signingInfo.setSigningHmacKey("dGhpcyBpcyBhIHNlY3JldCBtZXNzYWdl");

    m_svs = std::make_shared<ndn::svs::SVSync>(
      ndn::Name(m_options.prefix),
      ndn::Name(m_options.m_id),
      face,
      std::bind(&ProgramPrefix::onMissingData, this, _1),
      securityOptions);
  }
};

namespace ns3 {
namespace ndn{

// Class inheriting from ns3::Application
class Chat : public Application
{
public:
  static TypeId
  GetTypeId()
  {
    static TypeId tid = TypeId("Chat")
      .SetParent<Application>()
      .AddConstructor<Chat>()
      .AddAttribute("Id", "Id", StringValue("default_id"),
            MakeStringAccessor(&Chat::m_id), MakeStringChecker());

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

  //chunks::Producer::Options opts;
};
}
} // namespace ns3

