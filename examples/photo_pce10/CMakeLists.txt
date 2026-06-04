# §8.4 — photo_pce10 (real-application SO). Links OpenNN; the shared YAML
# constraint helper lives in examples/common/. EXAMPLE_DIR lets main.cpp find
# its nn/ model and problem.yaml regardless of the build directory.
add_executable(photo_pce10 main.cpp)
target_link_libraries(photo_pce10 PRIVATE opennn)
target_include_directories(photo_pce10 PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/../common")
target_compile_definitions(photo_pce10 PRIVATE EXAMPLE_DIR="${CMAKE_CURRENT_SOURCE_DIR}")
target_compile_features(photo_pce10 PRIVATE cxx_std_20)
