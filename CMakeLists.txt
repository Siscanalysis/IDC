cmake_minimum_required(VERSION 3.20)
project(IDC_sci2026
    VERSION 1.0.0
    DESCRIPTION "SCI 2026 companion — IDC worked examples (Scala & Lopez)"
    LANGUAGES CXX)

# -----------------------------------------------------------------------------
# Self-contained companion for the SCI 2026 paper "Diseno industrial optimo con
# redes neuronales". It builds standalone (cd sci2026 && cmake -B build) and
# does NOT modify the AIMS journal-paper companion at the repository root; it
# only reuses the same OpenNN pin (v1.2-IDC-paper) via its own cmake/ copy.
# -----------------------------------------------------------------------------

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Release CACHE STRING "Build type" FORCE)
endif()

set(CMAKE_RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin")

# OpenNN dependency — three-tier resolver (OPENNN_ROOT / OPENNN_TAG / default),
# pinned to the immutable tag v1.2-IDC-paper for byte-reproducibility.
list(APPEND CMAKE_MODULE_PATH "${CMAKE_SOURCE_DIR}/cmake")
include(FindOrFetchOpenNN)

# The IDC drivers instantiate ResponseOptimization / ApproximationNetwork
# directly; MSVC needs /bigobj for the resulting object sections.
if(MSVC)
    add_compile_options(/bigobj)
    add_compile_definitions(NOMINMAX _CRT_SECURE_NO_WARNINGS)
endif()

option(IDC_BUILD_SCI2026 "Build the SCI 2026 worked examples" ON)
if(IDC_BUILD_SCI2026)
    add_subdirectory(photo_wf3_so)   # Sec. 3 — single-objective (OPV photostability)
    add_subdirectory(yacht_mo)       # Sec. 4 — multi-objective (yacht hull design)
endif()
