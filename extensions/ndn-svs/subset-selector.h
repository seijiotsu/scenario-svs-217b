//
// Created by developer on 5/22/22.
//

#ifndef SCENARIO_SVS_SUBSET_SELECTOR_H
#define SCENARIO_SVS_SUBSET_SELECTOR_H

#include "common.hpp"
#include "version-vector.hpp"
#include <algorithm>
#include <iostream>
#include <list>
#include <random>
#include <unordered_set>

namespace ndn::svs {

class SubsetSelector
{
public:
  SubsetSelector(size_t nRecent, size_t nRandom, size_t nBucketSize)
      : m_numRecent(nRecent)
      , m_numRandom(nRandom)
      , m_numBucketSize(nBucketSize)
      , bucket_counter(0)
  {}

  void
  setNRecent(size_t num)
  {m_numRecent = num;}


  void
  setNRandom(size_t num)
  {m_numRandom = num;}

  void
  setNBucketSize(size_t num)
  {m_numBucketSize = num;}



  void
  findBucket(const std::vector<NodeID>& bucketSelectionCandidate, std::unordered_set<NodeID>& selectedBucket)
  {
    //todo: i--?
    for (size_t i = m_numBucketSize; i > 0; i++, bucket_counter++)
    {
        bucket_counter = (bucket_counter > bucketSelectionCandidate.size()) ? 0 : bucket_counter;
        selectedBucket.insert(bucketSelectionCandidate[bucket_counter]);
    }
  }

  VersionVector
  selectBucketRecent(VersionVector vv, bool g_order = false)
  {
    VersionVector result;
    std::unordered_set<NodeID> selectedRecent;
    std::unordered_set<NodeID> selectedBucket;


    std::list<NodeID> recentUpdated = std::move(vv.getLru());
    for (size_t numRecentSelected = std::min(m_numRecent, recentUpdated.size());
         numRecentSelected > 0; numRecentSelected--)
    {
      selectedRecent.insert(*recentUpdated.begin());
      recentUpdated.pop_front();
    }

    std::vector<NodeID> bucketSelectionCandidate;
    for (auto i: vv)
    {
      if (selectedRecent.find(i.first) == selectedRecent.end())
      {
        bucketSelectionCandidate.push_back(i.first);
      }
    }

    if (g_order) 
    {
      // The method for sort should not matter as long as all nodes use the same method.
      std::sort(bucketSelectionCandidate.begin(), bucketSelectionCandidate.end());
    } 

    //TODO: why checking m_numRefcent != 0 here? If users want full-random (by setting m_numRecent = 0), we no longer inser random?
    if (!bucketSelectionCandidate.empty() && m_numRecent != 0)
    {
      findBucket(bucketSelectionCandidate, selectedBucket);
    }

    for (auto i: vv)
    {
      if (selectedRecent.find(i.first) != selectedRecent.end() ||
          selectedBucket.find(i.first) != selectedBucket.end())
      {
        result.set(i.first, i.second);
      }
    }

    return result;

  }

  VersionVector
  selectRandRecent(VersionVector vv)
  {
    VersionVector result;
    std::unordered_set<NodeID> selectedRecent;
    std::unordered_set<NodeID> selectedRandom;

    std::list<NodeID> recentUpdated = std::move(vv.getLru());
    for (size_t numRecentSelected = std::min(m_numRecent, recentUpdated.size());
         numRecentSelected > 0; numRecentSelected--)
    {
      selectedRecent.insert(*recentUpdated.begin());
      recentUpdated.pop_front();
    }

    std::vector<NodeID> randomSelectionCandidate;
    for (auto i: vv)
    {
      if (selectedRecent.find(i.first) == selectedRecent.end())
      {
        randomSelectionCandidate.push_back(i.first);
      }
    }

    //the condition is added to avoid a division by 0 bug in STL
    if (!randomSelectionCandidate.empty() && m_numRandom != 0)
    {
      std::default_random_engine engine = std::default_random_engine(
              ndn::time::steady_clock::now().time_since_epoch().count());
      std::sample(randomSelectionCandidate.begin(),
                  randomSelectionCandidate.end(),
                  std::inserter(selectedRandom, selectedRandom.begin()),
                  //TODO: what if recentUpdated size is smaller than n_Recent? should we auto-fill the empty spaces with random? Here the size of selectedRecent <= m_numRecent so we 
                  //can do subtraction 
                  (m_numRandom), engine);
                  //(m_numRandom + (m_numRecent - selectedRecent.size())), engine);
    }


    for (auto i: vv)
    {
      if (selectedRecent.find(i.first) != selectedRecent.end() ||
          selectedRandom.find(i.first) != selectedRandom.end())
      {
        result.set(i.first, i.second);
      }
    }

    return result;
  }

private:
  size_t m_numRecent;
  size_t m_numRandom;
  size_t m_numBucketSize;
  size_t bucket_counter;
};

}// namespace ndn::svs
#endif//SCENARIO_SVS_SUBSET_SELECTOR_H
