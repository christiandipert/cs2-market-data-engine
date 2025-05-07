cmake_minimum_required(VERSION 3.10)
project(cs2_market_data_engine)

# Find Protocol Buffers
find_package(Protobuf REQUIRED)

# Add the generated protobuf files
add_library(engine_proto
    generated/pricing.pb.cc
    generated/pricing.pb.h
)

# Add your main engine library
add_library(engine
    src/pricing.cc
)

# Link against Protocol Buffers
target_link_libraries(engine
    PRIVATE
    engine_proto
    protobuf::libprotobuf
)

# Include directories
target_include_directories(engine
    PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}/generated
)