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
            cp test-results.xml test-results/
          when: always
      - store_test_results:
          path: test-results
      - store_artifacts:
          path: test-results
```

- 🚨 Error! Fix error by SSHing into the failed job 👩‍💻
- Discover that we missed a `mkdir test-results`:

```yaml
 - run:
          name: Copy tests results for storing
          command: |
            mkdir test-results
            cp test-results.xml test-results/
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

### Build a Docker image & Deploy it to the registry

Each time the tests pass we will build a Docker image with the web app.

- Create Docker Hub account if you don't already have one - https://docker.com
- Get add Docker Hub account name to environment variables: `DOCKER_LOGIN`, and `DOCKER_PASSWORD`
- Add the Docker orb:

```yaml
orbs: 
  node: circleci/node@5.0.0
  snyk: snyk/snyk@1.1.2
  docker: circleci/docker@2.0.2
```

- Add a job to build a docker image and push it to Docker Hub

```yaml
 jobs:
  ... 
  build-docker:
    docker:
      - image: cimg/base:stable
    steps:
      - checkout
      - setup_remote_docker
      - docker/check
      - docker/build:
          image: $DOCKER_LOGIN/${CIRCLE_PROJECT_REPONAME}-1-March-22
          tag: 0.1.<< pipeline.number >>
      - docker/push:
          image: $DOCKER_LOGIN/${CIRCLE_PROJECT_REPONAME}-1-March-22
          tag: 0.1.<< pipeline.number >>
```

- Add job to workflow:

```yaml
workflows:
  run-tests:
    jobs:
      - build-and-test
      - dependency-vulnerability-scan
      - build-docker
```

- Add `requires` stanza to the job in the workflow, which ensures that verification jobs must complete before building the Docker image.

```yaml
workflows:
  run-tests:
    jobs:
      - build-and-test
      - dependency-vulnerability-scan
      - build-docker:
          requires:
            - build-and-test
            - dependency-vulnerability-scan
```

### Deploy the containerized application to Heroku

Heroku is a service for hosting applications with a free tier & no card required

- Create a Heroku account & grab your API key, store in environment variable: `HEROKU_API_KEY`
- Create a Heroku application - I named mine `hello-circleci-connect-dev`
- Add Heroku orb:

```yaml
orbs: 
  node: circleci/node@5.0.0
  snyk: snyk/snyk@1.1.2
  docker: circleci/docker@2.0.2
  heroku: circleci/heroku@1.2.6
```

- Add deployment job:

```yaml
deploy-to-heroku:
    docker: 
      - image: cimg/base:stable
    steps:
      - heroku/install
      - heroku/check-authentication
      - checkout
      - heroku/push-docker-image:
          app-name: hello-circleci-connect-dev
          process-types: web
      - heroku/release-docker-image:
          app-name: hello-circleci-connect-dev
          process-types: web
```

- Add job to workflow after image is built:

```yaml
workflows:
  run-tests:
    jobs:
      - build-and-test
      - dependency-vulnerability-scan
      - build-docker:
          requires:
            - build-and-test
            - dependency-vulnerability-scan
      - deploy-to-heroku:
          requires:
            - build-docker
```

🎉 Contratulations, you have completed the second chapter, and created a full CI/CD pipeline that builds, verifies, and deploys your application!

## Chapter 3 - Advanced CircleCI  

In this section you will learn about advanced features of CircleCI for parallelism, access control, scheduling, dynamic configuration, and more!

If you got lost in the previous chapter, the initial state of the configuration is in `.circleci/chapters/config_2.yml`. You can restore it by running `./scripts/chapter_2.sh`.

### Employing parallelism - running tests in a matrix

We often want to test the same code across different variants of the application. We can employ matrix with CircleCI for that.

- Create a new job parameter for `build-and-test` job:

```yaml
jobs:
  build-and-test:
    docker:
      - image: cimg/node:16.14.0
    parameters:
      node_version:
        type: string
        default: 16.14.0
    steps:
      - checkout
      ...
```

- Pass matrix of versions as parameters for the job in the workflow definition:

```yaml


```

Parallelism
Matrix tests
Split tests to run faster

Filter branches
Access control using groups
Approval job to continue

Deploy to multiple environments (multiple apps)
Nightly build (deploy)

Dynamic config - skip build on scripts


Exercise - send message to Discord!
