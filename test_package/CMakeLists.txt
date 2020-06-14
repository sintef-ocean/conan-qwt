cmake_minimum_required(VERSION 3.13)
project(QwtTest CXX)

find_package(harfbuzz MODULE REQUIRED) # For some reason this must happen before conan_paths
include(${CMAKE_BINARY_DIR}/conan_paths.cmake)
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_set_vs_runtime()

find_package(Qt5 COMPONENTS Widgets REQUIRED)
find_package(Qwt MODULE REQUIRED)

add_executable(example example.cpp)
target_link_libraries(example Qwt::Qwt Qt5::Widgets)
