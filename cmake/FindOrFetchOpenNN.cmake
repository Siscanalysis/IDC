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
# the ResponseOptimization class used throughout §8), which currently lives on
# the `dev-refactor` branch of Artelnics/opennn. Until that work is cut into a
# numbered release, the default tracks that branch so the repository builds out
# of the box. The published tags v6.0.x predate the refactor and will NOT
# compile these examples.
#
# Action item on paper acceptance: once Artelnics/opennn tags the refactor
# (e.g. v6.1.0 / v1.0-IDC-paper), set OPENNN_DEFAULT_TAG below to that tag for
# byte-reproducibility and bump CITATION.cff's references.OpenNN.version field.
#
set(OPENNN_DEFAULT_TAG "dev-refactor" CACHE STRING
    "Default OpenNN ref for reproduction. Tracks the refactor branch until a \
     numbered release of Artelnics/opennn carries the §8 ResponseOptimization API.")

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
            "  OPENNN_DEFAULT_TAG in cmake/FindOrFetchOpenNN.cmake (will be set on paper acceptance)")
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
