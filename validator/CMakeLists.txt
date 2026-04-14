# CMakeLists.txt is provided for IDE integration / cross-platform builds.
# For a quick local build, prefer the direct g++ command documented in CLAUDE.md.
cmake_minimum_required(VERSION 3.18)
project(ihtp_validator CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_executable(IHTP_Validator IHTP_Validator.cc)
# json.hpp lives next to the source file; no external dependency needed.
target_include_directories(IHTP_Validator PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})
