# CI/CD Workshop with CircleCI

## Prerequisites

Knowledge of Git version control system
GitHub account - where the code is hosted
A code editor - you can use GitPod ...

## Chapter 0 - The Prologue and Prep

Fork this project! You will need a GitHub account.

This project can run on your machine if you have the correct dependencies installed (Git, Terraform, DigitalOcean CLI, Node.js) - or it can also run in a cloud based environment using GitPod!

[![Open in Gitpod](https://gitpod.io/button/open-in-gitpod.svg)](https://gitpod.io/#https://github.com/zmarkan/cicd-workshop)

This lets you spin up an environment with all the dependencies preinstalled, remotely connect to it, and work as it was on your machine. We suggest doing that route, as it will be much faster.


### Sign up for the required services that we'll use.

Create an account with DigitalOcean.com - https://cloud.digitalocean.com/ We will use DigitalOcean to deploy our application to. 

Create an account with Hashicorp Terraform - https://app.terraform.io/ We will use Terraform to provision our infrastructure on Digital Ocean.

Create an account with Docker Hub - https://hub.docker.com/ We will use Docker Hub as a repository for our app images.

Create an account with Snyk - https://app.snyk.io/ - We will use Snyk to run an automated security scan of our application an its dependencies. 

### How this workshop works

We will go from a chapter to chapter - depending on people's background we might skip a chapter (Chapter 1 is for complete beginners to CI/CD and subsequent chapters build on top of that, for example).

To jump between chapters we have prepared a set of handy scripts you can run in your terminal, which will set up your environment so you can follow along.

The scripts to run are:

`./scripts/do_0_start.sh` - Beginning of first chapter
`./scripts/do_1.sh` - End of first chapter/Start of second chapter
`./scripts/do_2.sh` -
`./scripts/do_3.sh` - 
`./scripts/do_4.sh` - 

The chapters will copy and overwrite certain files in your workspace, so after running each script, commit the changes and push it, which will run it on CircleCI.


### Overview of the project

The project is a simple web application, that is packaged in a Docker container, and deployed on Kubernetes - hosted on DigitalOcean infrastructure.
We also have some tests, a security scan, building the image, provisioning the infrastructure, deploying it, and breaking it down.

### Workshop flow

Chap 1:

- yaml
- setting up the first pipeline
- writing a job
- running tests
- deps without the orb (npm install)
- using the orb
- Contexts and secrets
- build the docker image & push to docker hub

Chap 2:

- Run security scan w/ Snyk
- Build the docker image
- Cloud native principles
- Provision infrastructure with Terraform on DigitalOcean
- Deploy to infra
- approve and destroy (explain approval job)

Chap 3:

- Running test in matrix
- Test splitting (populate with a long test)
- Pipeline params & scheduled jobs
- Branch and param filters

Chap 4: 

- Dynamic config

Assignment: 

- do something for swag and sense of personal accomplishment

### Terraform Cloud

Terraform is a tool that helps you manage your cloud infrastructurte.

## Chapter 1 - Basics of CircleCI

Most of our work will be in `./circleci/config.yml` - the CircleCI configuration file. This is where we will be describing our CI/CD pipelines.
This workshop is written in chapters, so you can jump between them by running scripts in `srcipts/` dir, if you get lost and want to catch up with something.
To begin, prepare your environment for the initial state by running the start script: `./scripts/do_0_start.sh`

Go to app.circleci.com, log in with your GitHub account (or create a new one).
Navigate to the `Projects` tab, and find this workshop project there - `cicd-workshop`.

First we will create a basic continuous integration pipeline, which will run your tests each time you commit some code. Run a commit for each instruction.

- Run: `./scripts/do_0_start.sh` to create the environment.
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

### Secrets and Contexts

CircleCI lets you store secrets safely on the platform where they will be encrypted and only made available to the executors as environment variables.
Th



🎉 Congratulations, you've completed the first part of the exercise!

## Chapter 2 - Intermediate CI/CD

In this section you will learn about the CircleCI orbs, various other types of checks you can implement, test optimisations, as well as deploy your application!

If you got lost in the previous chapter, the initial state of the configuration is in `.circleci/chapters/config_1.yml`. You can restore it by running `./scripts/do_1.sh`.

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
### Employing parallelism - running tests in a matrix

We often want to test the same code across different variants of the application. We can employ matrix with CircleCI for that.

- Create a new job parameter for `build-and-test` job, and use its value in the selected image:

```yaml
jobs:
  build-and-test:
    parameters:
      node_version:
        type: string
        default: 16.14.0
    docker:
      - image: cimg/node:<< parameters.node_version >>
    steps:
      - checkout
```

- Pass matrix of versions as parameters for the job in the workflow definition:

```yaml
workflows:
  run-tests:
    jobs:
      - build-and-test:
          matrix:
            parameters:
              node_version: ["16.14.0", "14.19.0", "17.6.0" ]
      - dependency-vulnerability-scan
      ...
```

This sets up the tests to run in a matrix, in parallel. But we must go further. Our tests still run for too long, so we can split them across multiple jobs.

### Split tests

- Change run test command to use CircleCI's test splitting feature:

```yaml
...
jobs:
  build-and-test:
    ...
    steps:
          - checkout
          - node/install-packages
          - run:          
              name: Run tests
              command: |
                echo $(circleci tests glob "test/**/*.test.js")
                circleci tests glob "test/**/*.test.js" | circleci tests split |
                xargs npm run test-ci
          ...
```

- Set job `parallelism` parameter:

```yaml
jobs:
  build-and-test:
    ...
    docker:
      - image: cimg/node:<< parameters.node-version >>
    parallelism: 4
    ...
```

- Make sure test results are merged correctly:

```yaml
jobs:
  build-and-test:
    ...
    steps:
          - checkout
          ...
          - run:
            name: Copy tests results for storing
            command: |
              mkdir test-results
              cp test-results.xml test-results/
            when: always
          - run:
              name: Process test report
              command: |
                  # Convert absolute paths to relative to support splitting tests by timing
                  if [ -e test-results.xml ]; then
                    sed -i "s|`pwd`/||g" test-results.xml
                  fi
          - store_test_results:
              path: test-results
          - store_artifacts:
              path: test-results
          ...
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
          image: $DOCKER_LOGIN/${CIRCLE_PROJECT_REPONAME}-31-march-22
          tag: 0.1.<< pipeline.number >>
      - docker/push:
          image: $DOCKER_LOGIN/${CIRCLE_PROJECT_REPONAME}-31-march-22
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
      - setup_remote_docker
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

In this section you will learn about advanced features of CircleCI for access control, scheduling, and more!

If you got lost in the previous chapter, the initial state of the configuration is in `.circleci/chapters/config_2.yml`. You can restore it by running `./scripts/chapter_2.sh`.

### Access and flow control

- Only deploy from `main` branch, using `filters` in the workflow:

```yaml
workflows:
  run-tests:
    jobs:
      ...
      - build-docker:
          requires:
            - build-and-test
            - dependency-vulnerability-scan
          filters:
            branches:
              only: main
      ...
```

Allow jobs fine grained access to credentials by using contexts. 

- In your CircleCI `Organization Settings` tab, create a new context - `workshop_deployment-dev`.
- Add your `HEROKU_API_KEY` environment variable to this context (same as before)
- Specify `context` parameter in the workflow for the `deploy_to_heroku` job:

```yaml
workflows:
  run-tests:
    jobs:
      ...
      - deploy-to-heroku:
          requires:
            - build-docker
          context: workshop_deployment-dev
      ...
```

- You can now delete `HEROKU_API_KEY` in project settings environment variables!
- Add approval job before deploying to Heroku:

```yaml
workflows:
  run-tests:
    jobs:
      ...
      - build-docker:
          requires:
            - build-and-test
            - dependency-vulnerability-scan
          filters:
            branches:
              only: main
      - hold-for-approval:
          type: approval
          requires: 
            - build-docker
      - deploy-to-heroku:
          requires:
            - hold-for-approval
          context: workshop_deployment-dev
      ...
```

You can also specify a security group to a context (in an org) to only allow those users to continue.
We can also have multiple deployment environments in different stages, using parameters and contexts.

- Create a new Heroku application - `hello-circleci-connect-prod`
- Add environment parameter to `deploy_to_heroku` job - `environment`:

```yaml
deploy-to-heroku:
    parameters:
      environment:
        type: string
        default: dev
    ...
```

- Use the `environment` parameter in the Heroku deployment steps:

```yaml
  deploy-to-heroku:
    ...
    steps:
      ...
      - heroku/push-docker-image:
          app-name: hello-circleci-connect-<< parameters.environment >>
          process-types: web
      - heroku/release-docker-image:
          app-name: hello-circleci-connect-<< parameters.environment >>
          process-types: web
```

- Add a new `deploy-to-heroku` job, that doesn't filter on branch to the workflow, and pass `dev` parameter to it:

```yaml
workflows:
  run-tests:
    jobs:
      ...
      - dependency-vulnerability-scan
      - deploy-to-heroku:
          context: workshop_deployment-dev
          environment: dev
      ...
```

- Add `prod` parameter to the "original" `deploy-to-heroku` job in the workflow:

```yaml
workflows:
  run-tests:
    jobs:
      ...
      - hold-for-approval:
          type: approval
          requires: 
            - build-docker
      - deploy-to-heroku:
          environment: prod
          requires:
            - hold-for-approval
          context: workshop_deployment-prod
```

### Set up a nightly build to deploy dev version of the application

- In `Project Settings` choose the `Triggers` tab and add a new trigger. Set it to run each day at 0:00 UTC, 1 per hour, off `main` branch. Add pipeline parameter `scheduled` set to `true`.

- Create a new boolean pipeline parameter in the config - `scheduled` which defaults to false:

```yaml
parameters:
  scheduled:
    type: boolean
    default: false
```

- Create a new workflow called `nightly_build` that only runs when `scheduled` is true:

```yaml
workflows:
  ...
  nightly-build:
    when: << pipeline.parameters.scheduled >>
    jobs:
      - build-and-test:
          matrix:
            parameters:
              node_version: ["16.14.0", "14.19.0", "17.6.0" ]
      - dependency-vulnerability-scan
      - deploy-to-heroku:
          context: workshop_deployment-dev
          environment: dev
```

- Add the `when/not` rule to the `run-tests` workflow:

```yaml
workflows:
  run-tests:
    when:
      not: << pipeline.parameters.scheduled >>
    jobs:
      - build-and-test:
      ...
```


🎉 Contratulations, you have completed the chapter, and created a complex CI/CD pipeline with access control.

## Chapter 4 - Dynamic Config

You can reset the state for this by running `.scripts/chapter_3.sh`

So far our config has been pretty straightforward. Trigger on commit or schedule would run our pipeline. But sometimes we want more flexibility, based on some external factors.

Dynamic config lets you change what your pipeline does while it's already running, based on git history, changes, or external factors.

- Toggle dynamic config in project settings - Advanced
- Copy your existing `config.yml` to `.circleci/continue-config.yml`:

```bash
cp .circleci/config.yml continue-config.yml
```

- Add `setup: true` stanza to your `config.yml`: 

```yaml
version: 2.1

setup: true
...
```

- Add the `path-filtering` orb (and remove others) in `config.yml`

```yaml
orbs: 
  path-filtering: circleci/path-filtering@0.1.1
  continuation: circleci/continuation@0.2.0
```

- Remove all jobs and workflows in `config.yml` and replace with the following:

```yaml
jobs:
  filter-paths:
    docker:
      - image: cimg/base:stable
    steps:   
      - checkout
      - path-filtering/set-parameters:
          base-revision: main
          mapping: |
            scripts/.*     skip-run  true
          output-path: /tmp/pipeline-parameters.json
      - continuation/continue:
          configuration_path: .circleci/continue-config.yml
          parameters: /tmp/pipeline-parameters.json 
workflows:
  choose-config:
    jobs:
      - filter-paths
```

Add the pipeline parameter for our scheduled pipeline

```yaml
parameters:
  scheduled:
    type: boolean
    default: false
```

- In `continue-config.yml` add the the `skip-run` pipeline parameter:

```yaml
parameters:
  skip-run:
    type: boolean
    default: false
  scheduled:
    type: boolean
    default: false
```

- Add the `skip-run` parameters to `when not` condition in the `run-tests` workflow:

```yaml
workflows:
  run-tests:
    when:
      and: 
        - not: << pipeline.parameters.scheduled >>
        - not: << pipeline.parameters.skip-run >>
    jobs:
      - build-and-test:
      ...
```

## Assignment!

Exercise - send message to our Discord server from CircleCI to get some CircleCI swag! ✨

Message should include:
  - your email, 
  - link to the CircleCI pipeline or job that sent the message

Discord Webhook URL will be provided at the event. 

How you implement it is up to you (there are many ways). Using an orb might be the easiest though... 

