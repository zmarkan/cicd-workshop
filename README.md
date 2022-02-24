# CI/CD Workshop with CircleCI

## Prerequisites

Knowledge of Git version control system

GitHub account - where the code is hosted

A code editor

## Chapter 1 - Basics of CircleCI

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

🎉 Congratulations, you've completed the first part of the exercise!

## Chapter 2 - Intermediate CI/CD

In this section you will learn about the CircleCI orbs, and various other types of checks you can implement, as well as deploy your application!

If you got lost in the previous chapter, the initial state of the configuration is in `.circleci/chapters/config_1.yml`. You can restore it by running `./scripts/chapter_1.sh`.

### Use Node orb

- First let's replace our existing process for dependency installation and running tests by using an orb - this saves you a lot of configuration and manages caching for you. Introduce the orb: 

```yaml
version: 2.1

orbs: 
    node: circleci/node@5.0.0
```

- Replace the job caching and dependency installation code with the call to the `node/install_packages` in the Node orb:

```yaml
jobs:
  build-and-test:
    ...
    steps:
        - checkout
        - node/install-packages
        - run:
            name: Run tests
            command: npm run test-ci
```

### Integrate automated dependency vulnerability scan

- Now let's integrate a security scanning tool in our process. We will use Snyk - https://snyk.io for this. You can create a free Snyk account by logging in with your GitHub credentials. Get a Snyk Auth token by going to your Account Settings - https://app.snyk.io/account.

- Add the Auth token to your environment variables - `SNYK_TOKEN`

- Add Snyk orb: 

```yaml
orbs: 
    node: circleci/node@5.0.0
    snyk: snyk/snyk@1.1.2
```

- Add dependency vulnerability scan job:

```yaml
jobs:
...
  dependency-vulnerability-scan:
    docker:
      - image: cimg/node:16.14.0
    steps:
      - checkout
      - node/install-packages
      - snyk/scan:
          fail-on-issues: true
```

- Add the job to workflow:

```yaml
workflows:
  run-tests:
    jobs:
      - build-and-test
      - dependency-vulnerability-scan

```

### Build a Docker image


- Create 

Implement security scan
Use orb to install dependencies
Set up environment variables
Set up contexts & user groups
Build image (docker)
Deploy app (heroku prod)



## Chapter 3 - Advanced CircleCI