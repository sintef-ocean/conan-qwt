cmake_minimum_required(VERSION 3.13)
project(QwtTest CXX)

include(${CMAKE_BINARY_DIR}/conan_paths.cmake)
find_package(Qt5 COMPONENTS Widgets REQUIRED)
find_package(Qwt MODULE REQUIRED)

add_executable(example example.cpp)
target_link_libraries(example Qwt::Qwt Qt5::Widgets)
