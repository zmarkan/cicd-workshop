#!/usr/bin/shell

rm .circleci/continue_config.yml

cp scripts/do/README.md .
cp scripts/do/.config_1.yml ./circleci/config.yml
