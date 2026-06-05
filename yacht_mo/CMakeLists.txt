# Sec. 4 — yacht bi-objective hull design. Links OpenNN. EXAMPLE_DIR lets
# main.cpp find its nn/ model regardless of the build dir.
add_executable(sci2026_yacht_mo main.cpp)
target_link_libraries(sci2026_yacht_mo PRIVATE opennn)
target_compile_definitions(sci2026_yacht_mo PRIVATE EXAMPLE_DIR="${CMAKE_CURRENT_SOURCE_DIR}")
target_compile_features(sci2026_yacht_mo PRIVATE cxx_std_20)
