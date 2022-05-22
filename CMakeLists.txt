cmake_minimum_required(VERSION 3.10)
project(scenario_svs)

set(CMAKE_CXX_STANDARD 20)

include_directories(extensions)
include_directories(extensions/app)
include_directories(extensions/ndn-svs)
include_directories(/usr/local/include/ns3.35/)
include_directories(/usr/local/include/ns3.35/ns3/ndnSIM/)

file(GLOB SVS_SRC "extensions/ndn-svs/*.cpp")

file(GLOB APP_SRC "extensions/app/*.cpp")

file(GLOB SCENARIO_SRC "scenarios/*.cpp")

add_library(scenario_svs ${SVS_SRC} ${APP_SRC} ${SCENARIO_SRC})
