# cmake/FindOrFetchOpenNN.cmake
#
# Three-tier resolution of the OpenNN dependency.
#
# Priority (highest first):
#
#   1. -DOPENNN_ROOT=<path>   or  $ENV{OPENNN_ROOT}
#        Use a local OpenNN checkout in-place. Intended for contributors
#        who are hacking on OpenNN and IDC in lockstep. No download.
#
#   2. -DOPENNN_TAG=<tag>     or  $ENV{OPENNN_TAG}
#        Fetch a specific OpenNN tag from GitHub via FetchContent.
#        Intended for reviewers who want to reproduce a specific
#        version of the paper.
#
#   3. (default)
#        Use the default tag baked into this file (OPENNN_DEFAULT_TAG below).
#        This is the OpenNN release pinned for the paper version of record;
#        IDC_paper_companion ships byte-reproducible results against this tag.
#
# To bump the OpenNN version in a future paper without changing the API,
# either pass -DOPENNN_TAG=<new-tag> or edit OPENNN_DEFAULT_TAG below.

# -----------------------------------------------------------------------------
# Pinned default — the paper-of-record OpenNN release
# -----------------------------------------------------------------------------
#
# The examples build against the refactored OpenNN API (JSON model format and
# the ResponseOptimization class used throughout §7), which currently lives on
# the `dev-refactor` branch of Artelnics/opennn. That work is published as the
# immutable annotated tag `v1.2-IDC-paper` (commit 64889b5e4) -- the paper
# version of record -- so a clean clone is byte-reproducible and does not drift
# as `dev-refactor` advances. v1.2-IDC-paper carries the matched-budget
# multi-objective machinery used in §7.3 (MOEED13) and §7.5 (UCI Concrete): the
# total surrogate-evaluation cap (set_max_total_evaluations), the reworked
# affine-repair input swap (uniform-in-band projection; exact on equalities),
# and the configurable initial-sampling factor (set_initial_sampling_factor).
# It supersedes v1.1-IDC-paper and v1.0-IDC-paper (commit 26cd4634a); all the
# new knobs default to their no-op values, so the base API is unchanged. The
# published tags v6.0.x predate the refactor and will NOT compile these examples.
#
set(OPENNN_DEFAULT_TAG "v1.2-IDC-paper" CACHE STRING
    "Default OpenNN ref for reproduction. Pinned to the immutable tag \
     v1.2-IDC-paper (commit 64889b5e4) on Artelnics/opennn -- the §7 \
     ResponseOptimization API plus the matched-budget evaluation cap, \
     the paper version of record.")

# -----------------------------------------------------------------------------
# Eigen (required by OpenNN)
# -----------------------------------------------------------------------------
# OpenNN's CMake links the `Eigen3::Eigen` target but expects the *consumer* to
# supply it (it neither find_package'es nor vendors Eigen). We provide it here
# so a clean clone builds out of the box: prefer a discoverable system/local
# Eigen, otherwise fetch the pinned header-only Eigen 3.4.0 (no Eigen build).
# Override discovery with -DEigen3_DIR=<path> or -DEIGEN3_INCLUDE_DIR=<path>.
if(NOT TARGET Eigen3::Eigen)
    find_package(Eigen3 3.4 QUIET NO_MODULE)
endif()
if(NOT TARGET Eigen3::Eigen AND EIGEN3_INCLUDE_DIR)
    add_library(Eigen3::Eigen INTERFACE IMPORTED)
    set_target_properties(Eigen3::Eigen PROPERTIES
        INTERFACE_INCLUDE_DIRECTORIES "${EIGEN3_INCLUDE_DIR}")
    message(STATUS "Eigen: using EIGEN3_INCLUDE_DIR=${EIGEN3_INCLUDE_DIR}")
endif()
if(NOT TARGET Eigen3::Eigen)
    message(STATUS "Eigen: fetching header-only 3.4.0 via FetchContent")
    include(FetchContent)
    # SOURCE_SUBDIR points at a non-existent dir so MakeAvailable only *downloads*
    # Eigen (header-only) without running Eigen's own heavy CMake project.
    FetchContent_Declare(
        eigen
        GIT_REPOSITORY https://gitlab.com/libeigen/eigen.git
        GIT_TAG        3.4.0
        GIT_SHALLOW    TRUE
        SOURCE_SUBDIR  cmake-does-not-exist
    )
    FetchContent_MakeAvailable(eigen)
    add_library(Eigen3::Eigen INTERFACE IMPORTED)
    set_target_properties(Eigen3::Eigen PROPERTIES
        INTERFACE_INCLUDE_DIRECTORIES "${eigen_SOURCE_DIR}")
endif()

# -----------------------------------------------------------------------------
# Tier 1 — OPENNN_ROOT (local checkout)
# -----------------------------------------------------------------------------
if(NOT DEFINED OPENNN_ROOT AND DEFINED ENV{OPENNN_ROOT})
    set(OPENNN_ROOT "$ENV{OPENNN_ROOT}")
endif()

if(OPENNN_ROOT)
    message(STATUS "OpenNN: using local checkout at ${OPENNN_ROOT}")
    if(NOT EXISTS "${OPENNN_ROOT}/CMakeLists.txt")
        message(FATAL_ERROR
            "OPENNN_ROOT=${OPENNN_ROOT} does not contain a CMakeLists.txt. \
             Set OPENNN_ROOT to the OpenNN repository root, not a subdirectory.")
    endif()
    add_subdirectory("${OPENNN_ROOT}" "${CMAKE_BINARY_DIR}/opennn-build" EXCLUDE_FROM_ALL)
    set(OPENNN_RESOLUTION_TIER "local (OPENNN_ROOT=${OPENNN_ROOT})")
    return()
endif()

# -----------------------------------------------------------------------------
# Tier 2 / Tier 3 — FetchContent from Artelnics/opennn
# -----------------------------------------------------------------------------
if(NOT DEFINED OPENNN_TAG AND DEFINED ENV{OPENNN_TAG})
    set(OPENNN_TAG "$ENV{OPENNN_TAG}")
endif()

if(NOT OPENNN_TAG)
    if(OPENNN_DEFAULT_TAG)
        set(OPENNN_TAG "${OPENNN_DEFAULT_TAG}")
        set(OPENNN_RESOLUTION_TIER "default tag (${OPENNN_DEFAULT_TAG})")
    else()
        message(FATAL_ERROR
            "OpenNN: no resolution available. Set one of:\n"
            "  -DOPENNN_ROOT=<local-checkout>     (contributors)\n"
            "  -DOPENNN_TAG=<tag>                 (reviewers, specific paper version)\n"
            "  OPENNN_DEFAULT_TAG in cmake/FindOrFetchOpenNN.cmake (ships set to v1.2-IDC-paper)")
    endif()
else()
    set(OPENNN_RESOLUTION_TIER "tag (${OPENNN_TAG})")
endif()

message(STATUS "OpenNN: fetching ${OPENNN_TAG} from Artelnics/opennn")

include(FetchContent)
FetchContent_Declare(
    opennn
    GIT_REPOSITORY https://github.com/Artelnics/opennn.git
    GIT_TAG        ${OPENNN_TAG}
    GIT_SHALLOW    TRUE
)
FetchContent_MakeAvailable(opennn)

message(STATUS "OpenNN resolved via: ${OPENNN_RESOLUTION_TIER}")
