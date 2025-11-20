cmake_minimum_required(VERSION 3.15)
project(toy_redis)

find_package(Python COMPONENTS Interpreter Development REQUIRED)

include(FetchContent)

FetchContent_Declare(
	pybind11
	GIT_REPOSITORY	https://github.com/pybind/pybind11.git
	GIT_TAG			v3.0.1
)
	
FetchContent_MakeAvailable(pybind11)

pybind11_add_module(toy_redis src/main.cpp src/engine.cpp)

target_link_libraries(toy_redis PRIVATE Python::Module)

install(TARGETS toy_redis DESTINATION .)