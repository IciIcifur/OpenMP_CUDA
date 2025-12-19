#!/usr/bin/env bash
set -euo pipefail

BUILD_TYPE=${BUILD_TYPE:-Debug}
BUILD_DIR=${BUILD_DIR:-cmake-build-${BUILD_TYPE,,}}

echo "==> Building Mandelbrot project (type=${BUILD_TYPE})"

cmake -S . -B "${BUILD_DIR}" -DCMAKE_BUILD_TYPE="${BUILD_TYPE}"
cmake --build "${BUILD_DIR}"

MANDEL_EXE="${BUILD_DIR}/mandelbrot.exe"

if [[ -x "${MANDEL_EXE}" ]]; then
  echo "==> Build OK: ${MANDEL_EXE}"
else
  echo "ERROR: ${MANDEL_EXE} not found or not executable" >&2
  exit 1
fi

echo "==> Done."