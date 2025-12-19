cmake_minimum_required(VERSION 3.18)
project(MPI_CUDA C)

set(CMAKE_C_STANDARD 11)

set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -fopenmp")
set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -fopenmp")

# Mandelbrot (OpenMP)
add_executable(mandelbrot src/mandelbrot.c)