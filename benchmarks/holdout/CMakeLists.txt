# Held-out surrogate trainer (§8.4 value_gap/space_gap diagnostics).
# Trains one OpenNN surrogate on a held-out split and exports JSON + numpy .py.
add_executable(train_surrogate train_surrogate.cpp)
target_link_libraries(train_surrogate PRIVATE opennn)
target_compile_features(train_surrogate PRIVATE cxx_std_20)
