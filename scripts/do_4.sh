#!/bin/bash

rm -f .circleci/continue_config.yml

# cp scripts/do/README.md .
cp -f scripts/do/configs/config_4.yml .circleci/config.yml


# Copy over test files
cp -a scripts/util/long-running-*.test.js test/

# Add flaky test
# cp scripts/util/flaky-test-example.test.js test/