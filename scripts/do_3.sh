#!/usr/bin/shell

rm -f .circleci/continue_config.yml

# cp scripts/do/README.md .
cp -f scripts/do/configs/config_3.yml ./circleci/config.yml

# Populate the long running tests 

cp -f scripts/util/long-running-*.test.js test/