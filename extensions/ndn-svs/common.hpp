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

#ifndef NDN_SVS_COMMON_HPP
#define NDN_SVS_COMMON_HPP

#include <ndn-cxx/data.hpp>
#include <ndn-cxx/face.hpp>
#include <ndn-cxx/interest.hpp>


#include <functional>
#include <memory>
#include <utility>
#include <vector>

#ifdef NDN_SVS_HAVE_TESTS
#define NDN_SVS_PUBLIC_WITH_TESTS_ELSE_PRIVATE public
#else
#define NDN_SVS_PUBLIC_WITH_TESTS_ELSE_PRIVATE private
#endif

namespace ndn {
namespace svs {

// Type and constant declarations for State Vector Sync (SVS)
using NodeID = ndn::Name;
using SeqNo = uint64_t;

//using ndn::security::ValidationError;
using ValidationError = unsigned;

using DataValidatedCallback = std::function<void(const Data&)>;
using DataValidationErrorCallback = std::function<void(const Data&, const ValidationError&)> ;

} // namespace svs
} // namespace ndn

namespace ndn {
namespace security {

using ValidationError = unsigned;

/**
 * @brief Callback to report a successful Data validation.
 */
typedef function<void(const Data& data)> DataValidationSuccessCallback;

/**
 * @brief Callback to report a failed Data validation.
 */
typedef function<void(const Data& data, const ValidationError& error)> DataValidationFailureCallback;

/**
 * @brief Callback to report a successful Interest validation.
 */
typedef function<void(const Interest& interest)> InterestValidationSuccessCallback;

/**
 * @brief Callback to report a failed Interest validation.
 */
typedef function<void(const Interest& interest, const ValidationError& error)> InterestValidationFailureCallback;

} // namespace security
} // namespace ndn



#endif // NDN_SVS_COMMON_HPP
