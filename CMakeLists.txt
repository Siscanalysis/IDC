cmake_minimum_required(VERSION 3.20)
project(IDC_paper_companion
    VERSION 1.0.0
    DESCRIPTION "Paper companion for IDC — iterative domain contraction over trained neural networks"
    LANGUAGES CXX)

# -----------------------------------------------------------------------------
# Build configuration
# -----------------------------------------------------------------------------
# OpenNN requires C++20; match it so the same standard flows to the examples.
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Release CACHE STRING "Build type" FORCE)
endif()

# Place all binaries in build/bin so example outputs are easy to find.
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin")

# -----------------------------------------------------------------------------
# OpenNN dependency (three-tier resolution: see cmake/FindOrFetchOpenNN.cmake)
# -----------------------------------------------------------------------------
list(APPEND CMAKE_MODULE_PATH "${CMAKE_SOURCE_DIR}/cmake")
include(FindOrFetchOpenNN)

# -----------------------------------------------------------------------------
# Worked examples (§7 of the paper)
# -----------------------------------------------------------------------------
# Each subdirectory adds one example_<name> executable that links against OpenNN.
# The CMake target name matches the §-anchor in the paper.

option(IDC_BUILD_EXAMPLES "Build the §7 worked examples" ON)

if(IDC_BUILD_EXAMPLES)
    # In-paper C++ neural-network case studies (§7.3–§7.5). Each subdirectory
    # adds one executable (target name matches the §-anchor) linking OpenNN.
    # The §7.2 BBOB analytical validation is Python-only (benchmarks/bbob/).
    add_subdirectory(examples/moeed13)           # §7.3 Validation (simulator MO)
    add_subdirectory(examples/photo_pce10)       # §7.4 Real application (SO)
    add_subdirectory(examples/concrete_uci_mo)   # §7.5 Real application (MO)
    add_subdirectory(benchmarks/holdout)         # §7.4 held-out surrogate trainer

    # Additional catalog examples (not shown in the manuscript). Their C++
    # drivers follow the same template; enable once their main.cpp land.
    option(IDC_BUILD_ADDITIONAL "Build the broader-catalog examples not in the paper" OFF)
    if(IDC_BUILD_ADDITIONAL)
        # add_subdirectory(examples/additional/concrete_uci_so)  # catalog: UCI Concrete SO
        # add_subdirectory(examples/additional/oer_plates)       # catalog: OER simplex SO
    endif()
endif()

# -----------------------------------------------------------------------------
# Installation
# -----------------------------------------------------------------------------
# install(...) targets are added per-example once the executables are wired up.
