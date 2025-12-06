#!/bin/bash
# Helper script to run Flutter with proper environment setup

export FLUTTER_ROOT=/Users/santhosh/Documents/flutter
export PATH="$FLUTTER_ROOT/bin:$PATH"

cd "$(dirname "$0")"

# Run flutter with the provided arguments
flutter "$@"

