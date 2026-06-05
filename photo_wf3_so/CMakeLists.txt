# Sec. 3 — photo_wf3 single-objective OPV photostability. Links OpenNN; the
# shared YAML constraint helper lives in sci2026/common/. EXAMPLE_DIR lets
# main.cpp find its nn/ model and problem.yaml regardless of the build dir.
add_executable(sci2026_photo_wf3_so main.cpp)
target_link_libraries(sci2026_photo_wf3_so PRIVATE opennn)
target_include_directories(sci2026_photo_wf3_so PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/../common")
target_compile_definitions(sci2026_photo_wf3_so PRIVATE EXAMPLE_DIR="${CMAKE_CURRENT_SOURCE_DIR}")
target_compile_features(sci2026_photo_wf3_so PRIVATE cxx_std_20)
