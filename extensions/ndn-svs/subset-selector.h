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
  SubsetSelector(size_t nRecent, size_t nRandom)
      : m_numRecent(nRandom)
      , m_numRandom(nRecent)
  {}

  void
  setNRecent(size_t num)
  {m_numRecent = num;}


  void
  setNRandom(size_t num)
  {m_numRandom = num;}

  VersionVector
  select(VersionVector vv)
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

    if (!randomSelectionCandidate.empty() && m_numRecent != 0)
    {
      std::default_random_engine engine = std::default_random_engine(
              ndn::time::steady_clock::now().time_since_epoch().count());
      std::sample(randomSelectionCandidate.begin(),
                  randomSelectionCandidate.end(),
                  std::inserter(selectedRandom, selectedRandom.begin()),
                  m_numRandom, engine);
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
};

}// namespace ndn::svs
#endif//SCENARIO_SVS_SUBSET_SELECTOR_H
