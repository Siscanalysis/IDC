# §7.5 — concrete_uci_mo (real-application MO). Links OpenNN; the shared YAML
# constraint helper lives in examples/common/. EXAMPLE_DIR lets main.cpp find
# its nn/ model and problem.yaml regardless of the build directory.
add_executable(concrete_uci_mo main.cpp)
target_link_libraries(concrete_uci_mo PRIVATE opennn)
target_include_directories(concrete_uci_mo PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/../common")
target_compile_definitions(concrete_uci_mo PRIVATE EXAMPLE_DIR="${CMAKE_CURRENT_SOURCE_DIR}")
target_compile_features(concrete_uci_mo PRIVATE cxx_std_20)
