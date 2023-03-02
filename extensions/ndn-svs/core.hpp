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

#ifndef NDN_SVS_CORE_HPP
#define NDN_SVS_CORE_HPP

#include "common.hpp"
#include "security-options.hpp"
#include "subset-selector.h"
#include "version-vector.hpp"

#include <ndn-cxx/util/random.hpp>
#include <ndn-cxx/util/scheduler.hpp>

#include <atomic>
#include <chrono>
#include <mutex>

namespace ndn {
namespace svs {

class MissingDataInfo
{
public:
  /// @brief session name
  NodeID nodeId;
  /// @brief the lowest one of missing sequence numbers
  SeqNo low;
  /// @brief the highest one of missing sequence numbers
  SeqNo high;
};

/**
 * @brief The callback function to handle state updates
 *
 * The parameter is a set of MissingDataInfo, of which each corresponds to
 * a session that has changed its state.
 */
using UpdateCallback = std::function<void(const std::vector<MissingDataInfo>&)>;

/**
 * @brief Pure SVS
 */
class SVSyncCore : noncopyable
{
public:
  class Error : public std::runtime_error
  {
  public:
    using std::runtime_error::runtime_error;
  };

public:
  /**
   * @brief Constructor
   *
   * @param face The face used to communication
   * @param syncPrefix The prefix of the sync group
   * @param onUpdate The callback function to handle state updates
   * @param syncKey Base64 encoded key to sign sync interests
   * @param nid ID for the node
   */
  SVSyncCore(ndn::Face& face,
             const Name& syncPrefix,
             const UpdateCallback& onUpdate,
             const SecurityOptions& securityOptions = SecurityOptions::DEFAULT,
             const NodeID& nid = EMPTY_NODE_ID,
             uint64_t numRand =128,
             uint64_t numRecent = 128);

  /**
   * @brief Reset the sync tree (and restart synchronization again)
   *
   * @param isOnInterest a flag that tells whether the reset is called by reset interest.
   */
  void
  reset(bool isOnInterest = false);

  /**
   * @brief Get the node ID of the local session.
   *
   * @param prefix prefix of the node
   */
  const NodeID&
  getNodeId()
  {
    return m_id;
  }

  /**
   * @brief Get current seqNo of the local session.
   *
   * This method gets the seqNo according to prefix, if prefix is not specified,
   * it returns the seqNo of default user.
   *
   * @param prefix prefix of the node
   */
  SeqNo
  getSeqNo(const NodeID& nid = EMPTY_NODE_ID) const;

  /**
   * @brief Update the seqNo of the local session
   *
   * The method updates the existing seqNo with the supplied seqNo and NodeID.
   *
   * @param seq The new seqNo.
   * @param nid The NodeID of node to update.
   */
  void
  updateSeqNo(const SeqNo& seq, const NodeID& nid = EMPTY_NODE_ID);

  /// @brief Get all the nodeIDs
  std::set<NodeID>
  getNodeIds() const;

  using GetExtraBlockCallback = std::function<ndn::Block(const VersionVector&)>;
  using RecvExtraBlockCallback = std::function<void(const ndn::Block&, const VersionVector&)>;

  /**
  * @brief Callback to get extra data block for sync interest
  * The version vector will be locked during the duration of this callback,
  * so it must return FAST
  */
  void setGetExtraBlockCallback(const GetExtraBlockCallback& callback)
  {
    m_getExtraBlock = callback;
  }

  /**
   * @brief Callback on receiving extra data in a sync interest.
   * Will be called BEFORE the interest is processed.
   */
  void setRecvExtraBlockCallback(const RecvExtraBlockCallback& callback)
  {
    m_recvExtraBlock = callback;
  }

  /// @brief Get current version vector
  VersionVector&
  getState()
  {
    return m_vv;
  }

  /// @brief Get human-readable representation of version vector
  std::string
  getStateStr() const
  {
    return m_vv.toStr();
  }

NDN_SVS_PUBLIC_WITH_TESTS_ELSE_PRIVATE:
  void
  onSyncInterest(const Interest &interest);

  void
  onSyncInterestValidated(const Interest &interest);

  /**
   * @brief Mark the instance as initialized and send the first interest
   */
  void
  sendInitialInterest();

  /**
   * @brief sendSyncInterestRandRecent and schedule a new retxSyncInterest event.
   *
   * @param send Send a sync interest immediately
   * @param delay Delay in milliseconds to schedule next interest (0 for default).
   */
  void
  retxSyncInterest(bool send, unsigned int delay);

  /**
   * @brief Add one sync interest to queue.
   *
   * Called by retxSyncInterest(), or after increasing a sequence
   * number with updateSeqNo()
   */
  void
  sendSyncInterest();


  /**
   * @brief Add sync interests to queue, generated by splitting by the MTU defined within
   *
   * Called by retxSyncInterest(), or after increasing a sequence
   * number with updateSeqNo()
   */
  void
  sendSyncInterestFrag();


  /**
   * @brief Add ONE sync interest to queue, generated by randomly filling untill reaching MTU
   * TODO: Should we randonmly fill up to the MTU? Or just up to a certain size?
   * Called by retxSyncInterest(), or after increasing a sequence
   * number with updateSeqNo()
   * @param nRand Number of randomly-selected states to include in the interest
   */
  void
  sendSyncInterestRand(size_t nRand);

  /**
   * @brief Add ONE sync interest to queue, generated by randomly filling untill reaching MTU, note
   * that most likely the recent might be < MTU, so the interest will include much fewer states than other methods
   * but this servers only as an experiment, use the mixture ones below for more realistic applications
   * TODO: Should we randonmly fill up to the MTU? Or just up to a certain size?
   * Called by retxSyncInterest(), or after increasing a sequence
   * number with updateSeqNo()
   * @param nRecent Number of recent states to include in the interest
   */
  void
  sendSyncInterestRecent(size_t nRecent);


  /**
   * @brief Add ONE sync interest to queue, generated by fill up to MTU by percents of random and recent
   * Called by retxSyncInterest(), or after increasing a sequence
   * Note pRecent + pRand must equals to 1.0 for now.
   * number with updateSeqNo()
   * @param pRecent Percent of randomly-selected states to include in the interest
   * @param pRand Percent of randomly-selected states to include in the interest
   */
  void sendSyncInterestRandRecent();


  /**
   * @brief Add ONE sync interest to queue, generated by picking a bucket. This bucket is logical in the sense that it is determined by the size of the MTU. It is realized
   * by the use of a counter in the state-vec to aovid resending the same set of states.
   * @param nBuckets Number of buckets to fill-in
   */
  void
  sendSyncInterestBucket(size_t nBucketSize);


  /**
   * @brief Add ONE sync interest to queue, generated by picking a bucket + LRU. This bucket is logical in the sense that it is determined by the size of the MTU. It is realized
   * by the use of a counter in the state-vec to aovid resending the same set of states.
   * @param nBuckets Number of buckets to fill-in
   */
  void
  sendSyncInterestBucketMix(size_t nBucketSize, size_t nRecent);

  /**
   * @brief Add ONE sync interest to queue, generated by picking a bucket. This bucket is logical in the sense that it is determined by the size of the MTU. It is realized
   * by the use of a counter in the state-vec to aovid resending the same set of states. Here all nodes must agree on a global-ordering of the states stored.
   * @param nBuckets Number of buckets to fill-in
   */
  void
  sendSyncInterestBucketOrdered(size_t nBucketSize);

  /**
   * @brief Add ONE sync interest to queue, generated by picking a bucket + LRU. This bucket is logical in the sense that it is determined by the size of the MTU. It is realized
   * by the use of a counter in the state-vec to aovid resending the same set of states. Here all nodes must agree on a global-ordering of the states stored.
   * @param nBuckets Number of buckets to fill-in
   */
  void
  sendSyncInterestBucketOrderedMix(size_t nBucketSize, size_t nRecent);

  /**
   * @brief Merge state vector into the current
   *
   * Also adds missing data interests to data interest queue.
   *
   * @param vvOther state vector to merge in
   *
   * @returns a pair of boolean representing:
   *    <my vector new, other vector new>.
   */
  std::pair<bool, bool>
  mergeStateVector(const VersionVector& vvOther);

  /**
   * @brief Record vector by merging it into m_recordedVv
   *
   * @param vvOther state vector to merge in
   * @returns if recorded successfully
   */
  bool
  recordVector(const VersionVector &vvOther);

  /**
   * @brief Enter suppression state by setting
   * m_recording to True and initializing m_recordedVv to vvOther
   *
   * Does nothing if already in suppression state
   *
   * @param vvOther first vector to record
   */
  void
  enterSuppressionState(const VersionVector &vvOther);

  /// @brief Reference to scheduler
  ndn::Scheduler&
  getScheduler()
  {
    return m_scheduler;
  }

  /// @brief Get the current time in microseconds with arbitrary reference
  long
  getCurrentTime() const;

public:
  static const NodeID EMPTY_NODE_ID;

private:
  static const ConstBufferPtr EMPTY_DIGEST;
  static const ndn::name::Component RESET_COMPONENT;
  static const ndn::name::Component RECOVERY_COMPONENT;

  // Communication
  ndn::Face& m_face;
  const Name m_syncPrefix;
  const SecurityOptions m_securityOptions;
  const NodeID m_id;
  ndn::ScopedRegisteredPrefixHandle m_syncRegisteredPrefix;

  const UpdateCallback m_onUpdate;

  // State
  VersionVector m_vv;
  mutable std::mutex m_vvMutex;
  // Aggregates incoming vectors while in suppression state
  std::unique_ptr<VersionVector> m_recordedVv = nullptr;
  mutable std::mutex m_recordedVvMutex;

  // Extra block
  GetExtraBlockCallback m_getExtraBlock;
  RecvExtraBlockCallback m_recvExtraBlock;

  // Random Engine
  ndn::random::RandomNumberEngine m_rng;
  // Milliseconds between sending two packets in the queues
  std::uniform_int_distribution<> m_packetDist;
  // Milliseconds between sending two sync interests
  std::uniform_int_distribution<> m_retxDist;
  // Milliseconds to send sync interest reply after
  std::uniform_int_distribution<> m_intrReplyDist;

  // Security
  ndn::KeyChain m_keyChainMem;

  ndn::Scheduler m_scheduler;
  mutable std::mutex m_schedulerMutex;
  scheduler::ScopedEventId m_retxEvent;
  scheduler::ScopedEventId m_packetEvent;

  std::chrono::steady_clock m_steadyClock;

  // Time at which the next sync interest will be sent
  std::atomic_long m_nextSyncInterest;

  int m_instanceId;
  static int s_instanceCounter;

  // Prevent sending interests before initialization
  bool m_initialized = false;

  //subset
  SubsetSelector m_subsetSelect;

  private:
    // set mtu here instead
    size_t this_mtu = 80;
};

}  // namespace svs
}  // namespace ndn

#endif // NDN_SVS_CORE_HPP
