#!/usr/bin/shell

rm -f .circleci/continue_config.yml

# cp scripts/do/README.md .
cp -f scripts/do/configs/config_4.yml ./circleci/config.yml


# Copy over test files
cp -a scripts/util/long-running-*.test.js test/

# Remove old test files, use -f to ignore the error message if tests don't exist
rm -f test/long-running-*.test.js

# Add flaky test
cp scripts/util/flaky-test-example.test.js test/