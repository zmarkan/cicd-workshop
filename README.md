# CI/CD Workshop with CircleCI

## Prerequisites

Knowledge of Git version control system
GitHub account - where the code is hosted
A code editor

## Chapter 1 - the basics

Fork this project!
Most of our work will be in `./circleci/config.yml` - the CircleCI configuration file. This is where we will be describing our CI/CD pipelines.
This workshop is written in chapters, so you can jump between them by running scripts in `srcipts/` dir, if you get lost and want to catch up with something.
To begin, prepare your environment for the initial state by running the start script: `./scripts/chapter_0_start.sh`

Go to app.circleci.com, log in with your GitHub account (or create a new one).
Navigate to the `Projects` tab, and find this workshop project there - `cicd-workshop`.

First we will create a basic continuous integration pipeline, which will run your tests each time you commit some code. Run a commit for each instruction.

- Run: `./scripts/chapter_0_start.sh` to create the environment.
- In the `.circleci/config.yaml` find the `jobs` section, and add a job called `build-and-test`:

```yaml
...
jobs:
  build-and-test:
    docker:
      - image: cimg/node:16.14.0
    steps:
      - checkout
      - run:
          name: Install deps
          command: npm install
      - run:
          name: Run tests
          command: npm run test-ci
```

- Now let's create a workflow that will run our job: 

```yaml
workflows:
  run-tests:
    jobs:
      - build-and-test
```

- Report test results to CircleCI. Add the following run commands to `build-and-test` job:

```yaml
jobs:
  build-and-test:
    ...
      - run:
          name: Run tests
          command: npm run test-ci
      - run:
          name: Copy tests results for storing
          command: |
            cp test-results.xml /test-results/
          when: always
      - store_test_results:
          path: /test-results
      - store_artifacts:
          path: /test-results
```

- 🚨 Error! Fix error by SSHing into the failed job 👩‍💻
- Discover that we missed a `mkdir /test-results`:

```yaml
 - run:
          name: Copy tests results for storing
          command: |
            cp test-results.xml /test-results/
          when: always

```
- Utilise cache for dependencies to avoid installing each time:

```yaml
jobs:
    build-and-test:
    ...
    steps:
        - checkout
        - restore_cache:
            key: v1-deps-{{ checksum "package-lock.json" }}
        - run:
            name: Install deps
            command: npm install
        - save_cache:
            key: v1-deps-{{ checksum "package-lock.json" }}
            paths: 
                - node_modules   
        - run:
            name: Run tests
            command: npm run test-ci

```