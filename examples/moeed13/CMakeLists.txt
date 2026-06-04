# §8.3 — moeed13 (simulator-grounded MO validation). Links OpenNN; the shared
# YAML constraint helper lives in examples/common/. EXAMPLE_DIR lets main.cpp
# find its nn/ model and problem.yaml regardless of the build directory.
add_executable(moeed13 main.cpp)
target_link_libraries(moeed13 PRIVATE opennn)
target_include_directories(moeed13 PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/../common")
target_compile_definitions(moeed13 PRIVATE EXAMPLE_DIR="${CMAKE_CURRENT_SOURCE_DIR}")
target_compile_features(moeed13 PRIVATE cxx_std_20)
