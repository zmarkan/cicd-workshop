# CI/CD Workshop with CircleCI

## Prerequisites

Knowledge of Git version control system
GitHub account - where the code is hosted
A code editor - you can use GitPod ...

## Chapter 0 - The Prologue and Prep

Fork this project! You will need a GitHub account.

This project can run on your machine if you have the correct dependencies installed (Git, Terraform, DigitalOcean CLI, Node.js), or it can also run in a cloud based environment using Gitpod (we recommend Gitpod for best experience).

[![Open in Gitpod](https://gitpod.io/button/open-in-gitpod.svg)](https://gitpod.io/#https://github.com/zmarkan/cicd-workshop)

This lets you spin up an environment with all the dependencies preinstalled, remotely connect to it, and work on it as it was on your machine. This is much faster, believe us, we measured it with science. 

### If NOT using Gitpod

If you are using Gitpod you're good, everything you need should have been installed already.

The commands used here are mostly using Bash, Git, and Python 3 - make sure they are installed and available. If using Windows, the commands might be different than the ones listed here.

Copy over the credentials source file. This is untracked in Git and will be used by a script to populate your CircleCI secret variables.

```
cp scripts/util/credentials.sample.toml credentials.toml
```

### IMPORTANT! Sign up for the required services and prepare credentials

If you don't do this, you'll have a bad time.

#### DigitalOcean

- Create an account with DigitalOcean - https://cloud.digitalocean.com/ We will use DigitalOcean to deploy our application to. 
- Go to API (left)
- Generate New Token with read and write access
- copy the token string to `credentials.toml` - `digitalocean_token`
 
#### Terraform Cloud

- Create an account with Hashicorp Terraform - https://app.terraform.io/ We will use Terraform to provision our infrastructure on Digital Ocean.
- Got to your user settings (top right), and select Tokens
- Create an API token 
- Copy the token string to `credentials.toml` - `tf_cloud_key`

#### Docker Hub

- Create an account with Docker Hub - https://hub.docker.com/ We will use Docker Hub as a repository for our app images.
- Go to your user settings (top right), and select Security
- Create New Access Token
- copy your username to `credentials.toml` - `docker_username`
- copy your token string to `credentials.toml` - `docker_token`

#### Snyk

- Create an account with Snyk - https://app.snyk.io/ - We will use Snyk to run an automated security scan of our application an its dependencies. 
- Go to your Account settings (top right)
- Click to show Auth Token 
- Copy your token string to `credentials.toml` - `snyk_token`

### How this workshop works

We will go from a chapter to chapter - depending on people's background we might skip a chapter (Chapter 1 is for complete beginners to CI/CD and subsequent chapters build on top of that, for example).

To jump between chapters we have prepared a set of handy scripts you can run in your terminal, which will set up your environment so you can follow along.

The scripts to run are:

`./scripts/do_1_start.sh` - Beginning of first chapter
`./scripts/do_2.sh` - End of first chapter/Start of second chapter
`./scripts/do_3.sh` - End of second chapter/Start of third chapter
`./scripts/do_4.sh` - Final state
`./scripts/do_5_dynamic.sh` - Final state using Dynamic configuration

The chapters will copy and overwrite certain files in your workspace, so after running each script, commit the changes and push it, which will run it on CircleCI.

### Overview of the project

The project is a simple web application, that is packaged in a Docker container, and deployed on Kubernetes - hosted on DigitalOcean infrastructure. 
We also have some tests, a security scan, building the image, provisioning the infrastructure and deploying the application.

### Workshop topics covered

#### Chapter 1 - Basics of CI/CD

- YAML
- Setting up the first pipeline
- Writing a job and workflow
- Running tests
- Reporting test results
- Installing dependencies manually
- Caching dependencies
- Using the orb to install and cache dependencies 
- Setting up secrets and contexts
- Build the docker image & push to docker hub

#### Chapter 2 - A realistic CI/CD pipeline

- Run security scan w/ Snyk
- Cloud native principles
- Provision infrastructure with Terraform on DigitalOcean
- Deploy to infrastructure
- Run a smoke test on deployed app
- Destroy the deployed application and provisioned infrastructure
- Manual approval step before destroy
- approve and destroy (explain approval job)

#### Chapter 3 - Advanced CircleCI concepts

- Running test in matrix across multiple versions
- Using test splitting to tear down a long running test suite
- Filtering pipelines on branches and tags
- Scheduling pipelines and using pipeline parametres to drive the flow

#### Chapter 4 - Using Dynamic Configuration to select what gets built when

- Add a flow that only build the application and run tests if files outside of scripts have changed

## Chapter 1 - Basics of CircleCI

Most of our work will be in `./circleci/config.yml` - the CircleCI configuration file. This is where we will be describing our CI/CD pipelines.
This workshop is written in chapters, so you can jump between them by running scripts in `srcipts/` dir, if you get lost and want to catch up with something.
To begin, prepare your environment for the initial state by running the start script: `./scripts/do_1_start.sh`

Go to app.circleci.com, and if you haven't yet, log in with your GitHub account (or create a new one).
Navigate to the `Projects` tab, and find this workshop project there - `cicd-workshop`.

First we will create a basic continuous integration pipeline, which will run your tests each time you commit some code. Run a commit for each instruction.

- Run: `./scripts/do_0_start.sh` to create the environment.
- In the `.circleci/config.yaml` find the `jobs` section, and add a job called `build_and_test`:

```yaml
...
jobs:
  build_and_test:
    docker:
      - image: cimg/node:16.16.0
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
  test_scan_deploy:
    jobs:
      - build_and_test
```

- Report test results to CircleCI. Add the following run commands to `build_and_test` job:

```yaml
jobs:
  build_and_test:
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
    build_and_test:
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

### Using the orb instead of installing and caching dependencies manually

Now let's replace our existing process for dependency installation and running tests by using an orb - this saves you a lot of configuration and manages caching for you. Introduce the orb: 

```yaml
version: 2.1

orbs: 
    node: circleci/node@5.0.2
```

- Replace the job caching and dependency installation code with the call to the `node/install_packages` in the Node orb:

```yaml
jobs:
  build_and_test:
    ...
    steps:
        - checkout
        - node/install-packages
        - run:
            name: Run tests
            command: npm run test-ci
```

### Secrets and Contexts

CircleCI lets you store secrets safely on the platform where they will be encrypted and only made available to the executors as environment variables. The first secrets you will need are credentials for Docker Hub which you'll use to deploy your image to Docker Hub.

We have prepared a script for you to create a context and set it up with all the secrets you will need in CircleCI. This will use the CircleCI API.

You should have all the required accounts for third party services already, and are just missing the CircleCI API token and the organization ID:

- In app.circleci.com click on your user image (bottom left)
- Go to Personal API Tokens 
- Generate new API token and insert it `credentials.toml`
- In app.circleci.com click on the Organization settings. 
- Copy the Organization ID value and insert it in `credentials.toml`

Make sure that you have all the required service variables set in `credentials.toml`, and then run the script:

```bash
python scripts/prepare_contexts.py
```

Most of the things you do in CircleCI web interface can also be done with the API. You can inspect the newly created context and secrets by going to your organization settings. Now we can create a new job to build and deploy a Docker image.

### Building and deploying a Docker image

- First introduce the Docker orb:

```yaml
orbs:
  node: circleci/node@5.0.2
  docker: circleci/docker@2.1.1
```

- Add a new job:

```yaml
jobs:
...
  build_docker_image:
      docker:
        - image: cimg/base:stable
      steps:
        - checkout
        - setup_remote_docker:
            docker_layer_caching: false
        - docker/check
        - docker/build:
            image: $DOCKER_LOGIN/$CIRCLE_PROJECT_REPONAME
            tag: 0.1.<< pipeline.number >>
        - docker/push:
            image: $DOCKER_LOGIN/$CIRCLE_PROJECT_REPONAME
            tag: 0.1.<< pipeline.number >>
```

In the workflow, add the deployment job:

```yaml
workflows:
  test_scan_deploy:
    jobs:
      - build_and_test
      - build_docker_image

```

This doesn't run unfortunately - our `build_docker_image` doesn't have the required credentials. 
Add the context we created earlier:

```yaml
workflows:
  test_scan_deploy:
      jobs:
        - build_and_test
        - build_docker_image:
            context:
              - cicd-workshop
```

This runs both jobs in parallel. We might want to run them sequentially instead, so Docker deployment only happens when the tests have passed. Do this by adding a `requires` stanza to the `build_docker_image` job:

```yaml
workflows:
  test_scan_deploy:
      jobs:
        - build_and_test
        - build_docker_image:
            context:
              - cicd-workshop
            requires:
              - build_and_test
```

🎉 Congratulations, you've completed the first part of the exercise!

## Chapter 2 - A realistic CI/CD pipeline

In this section you will learn about cloud native paradigms, shift left security scanning, infrastructure provisioning, and deployment of infrastructure!

If you got lost in the previous chapter, the initial state of the configuration is in `scripts/do/configs/config_2.yml`. You can restore it by running `./scripts/do_2.sh`.

### Integrate automated dependency vulnerability scan

- First let's integrate a security scanning tool in our process. We will use Snyk, for which you should already have the account created and environment variable set.

- Add Snyk orb: 

```yaml
orbs: 
  node: circleci/node@5.0.2
  docker: circleci/docker@2.1.1
  snyk: snyk/snyk@1.2.3
```

- Add dependency vulnerability scan job:

```yaml
jobs:
...
  dependency_vulnerability_scan:
    docker:
      - image: cimg/node:16.16.0
    steps:
      - checkout
      - node/install-packages
      - snyk/scan:
          fail-on-issues: true
          monitor-on-build: false
```

- Add the job to workflow. Don't forget to give it the context!:

```yaml
workflows:
  test_scan_deploy:
      jobs:
        - build_and_test
        - dependency_vulnerability_scan:
            context:
              - cicd-workshop
        - build_docker_image:
            context:
              - cicd-workshop
```

- This will now run the automated security scan for your dependencies and fail your job if any of them have known vulnerabilities. Now let's add the security scan to our Docker image build job as well:

```yaml
  build_docker_image:
    docker:
      - image: cimg/base:stable
    steps:
      - checkout
      - setup_remote_docker:
          docker_layer_caching: false
      - docker/check
      - docker/build:
          image: $DOCKER_LOGIN/$CIRCLE_PROJECT_REPONAME
          tag: 0.1.<< pipeline.number >>
      - snyk/scan:
          fail-on-issues: false
          monitor-on-build: false
          target-file: "Dockerfile"
          docker-image-name: $DOCKER_LOGIN/$CIRCLE_PROJECT_REPONAME:0.1.<< pipeline.number >>
          project: ${CIRCLE_PROJECT_REPONAME}/${CIRCLE_BRANCH}-app
      - docker/push:
          image: $DOCKER_LOGIN/$CIRCLE_PROJECT_REPONAME
          tag: 0.1.<< pipeline.number >>
```

### Cloud Native deployments

We often use CI/CD pipelines to create our infrastructure, not just run our applications. In the following steps we will be doing just that.

First make sure you have all the credentials created and set in your `cicd-workshop` context:
- DIGITALOCEAN_TOKEN
- TF_CLOUD_KEY

This tells a cloud provider - in our case Digitalocean - what to create for us, so we can deploy our application. We will use a tool called Terraform for it.

- Add the orb for Terraform

```yaml
orbs:
  node: circleci/node@5.0.2
  docker: circleci/docker@2.1.1
  snyk: snyk/snyk@1.2.3
  terraform: circleci/terraform@3.0.0
```

- Add a command to install the Digitalocean CLI - `doctl`. This will be reusable in all jobs across the entire pipeline:

```yaml
commands:
  install_doctl:
    parameters:
      version:
        default: "1.79.0"
        type: string
    steps:
      - run:
          name: Install doctl client
          command: |
            cd ~
            wget https://github.com/digitalocean/doctl/releases/download/v<<parameters.version>>/doctl-<<parameters.version>>-linux-amd64.tar.gz
            tar xf ~/doctl-<<parameters.version>>-linux-amd64.tar.gz
            sudo mv ~/doctl /usr/local/bin
```

- In app.terraform.io create a new organization, and give it a name. Create a new workspace called `cicd-workshop-do`. 
In the workspace GUI, go to `Settings`, and make sure to switch the `Execution Mode` to `Local`.

- In the file `terraform/do_create_k8s/main.tf` locate the `backend "remote"` section and make sure to change the name to your organization:

```go
  backend "remote" {
    organization = "your_cicd_workshop_org"
    workspaces {
      name = "cicd-workshop-do"
    }
  }
```

Add a job to create a Terraform cluster

```yaml
create_do_k8s_cluster:
    docker:
      - image: cimg/node:16.16.0
    steps:
      - checkout
      - install_doctl:
          version: "1.78.0"
      - run:
          name: Create .terraformrc file locally
          command: echo "credentials \"app.terraform.io\" {token = \"$TF_CLOUD_KEY\"}" > $HOME/.terraformrc
      - terraform/install:
          terraform_version: "1.0.6"
          arch: "amd64"
          os: "linux"
      - terraform/init:
          path: ./terraform/do_create_k8s
      - run:
          name: Create K8s Cluster on DigitalOcean
          command: |
            export CLUSTER_NAME=${CIRCLE_PROJECT_REPONAME}
            export DO_K8S_SLUG_VER="$(doctl kubernetes options versions \
              -o json -t $DIGITAL_OCEAN_TOKEN | jq -r '.[0] | .slug')"

            terraform -chdir=./terraform/do_create_k8s apply \
              -var do_token=$DIGITAL_OCEAN_TOKEN \
              -var cluster_name=$CLUSTER_NAME \
              -var do_k8s_slug_ver=$DO_K8S_SLUG_VER \
              -auto-approve

```

Add the new job to the workflow:

```yaml
workflows:
  test_scan_deploy:
      jobs:
        - build_and_test
        - dependency_vulnerability_scan:
            context:
              - cicd-workshop
        - build_docker_image:
            context:
              - cicd-workshop
        - create_do_k8s_cluster:
            context:
              - cicd-workshop
```

### Deploying to your Kubernetes cluster 

Now that you have provisioned your infrastructure - a Kubernetes cluster on Digitalocean. It's time to deploy the application to this cluster.

- In app.terraform.io create a new workspace called `deploy-cicd-workshop-do`. 
In the workspace GUI, go to `Settings`, and make sure to switch the `Execution Mode` to `Local`. You should now have two workspaces. One holds the infrastructure definitions, and one for deployments.

- In the file `terraform/do_k8s_deploy_app/main.tf` locate the `backend "remote"` section and make sure to change the name to your organization:

```go
  backend "remote" {
    organization = "your_cicd_workshop_org"
    workspaces {
      name = "cicd-workshop-do"
    }
  }
```

Add a job `deploy_to_k8s` which will perform the deployment:

```yaml

deploy_to_k8s:
    docker:
      - image: cimg/node:14.16.0
    steps:
      - checkout
      - install_doctl:
          version: "1.78.0"
      - run:
          name: Create .terraformrc file locally
          command: echo "credentials \"app.terraform.io\" {token = \"$TF_CLOUD_KEY\"}" > $HOME/.terraformrc
      - terraform/install:
          terraform_version: "1.0.6"
          arch: "amd64"
          os: "linux"
      - terraform/init:
          path: ./terraform/do_k8s_deploy_app
      - run:
          name: Deploy Application to K8s on DigitalOcean
          command: |
            export CLUSTER_NAME=${CIRCLE_PROJECT_REPONAME}
            export TAG=0.1.<< pipeline.number >>
            export DOCKER_IMAGE="${DOCKER_LOGIN}/${CIRCLE_PROJECT_REPONAME}:$TAG"
            doctl auth init -t $DIGITALOCEAN_TOKEN
            doctl kubernetes cluster kubeconfig save $CLUSTER_NAME

            terraform -chdir=./terraform/do_k8s_deploy_app apply \
              -var do_token=$DIGITALOCEAN_TOKEN \
              -var cluster_name=$CLUSTER_NAME \
              -var docker_image=$DOCKER_IMAGE \
              -auto-approve

            # Save the Load Balancer Public IP Address
            export ENDPOINT="$(terraform -chdir=./terraform/do_k8s_deploy_app output lb_public_ip)"
            mkdir -p /tmp/do_k8s/
            echo 'export ENDPOINT='${ENDPOINT} > /tmp/do_k8s/dok8s-endpoint
      - persist_to_workspace:
          root: /tmp/do_k8s/
          paths:
            - "*"

```

- Add the new job to the workflow - add `requires` statements to only start deployment when all prior steps have completed

```yaml
workflows:
  test_scan_deploy:
    when:
      and:
        - not: << pipeline.parameters.scheduled >>
    jobs:
      ...
      - create_do_k8s_cluster:
            context:
              - cicd-workshop
      - deploy_to_k8s:
          requires:
            - dependency_vulnerability_scan
            - build_docker_image
            - build_and_test
            - create_do_k8s_cluster
          context:
            - cicd-workshop
```



👆 Done up to that point 👆


### Employing parallelism - running tests in a matrix

We often want to test the same code across different variants of the application. We can employ matrix with CircleCI for that.

- Create a new job parameter for `build_and_test` job, and use its value in the selected image:

```yaml
jobs:
  build_and_test:
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
      - build_and_test:
          matrix:
            parameters:
              node_version: ["16.14.0", "14.19.0", "17.6.0" ]
      - dependency_vulnerability_scan
      ...
```

This sets up the tests to run in a matrix, in parallel. But we must go further. Our tests still run for too long, so we can split them across multiple jobs.

### Split tests

- Change run test command to use CircleCI's test splitting feature:

```yaml
...
jobs:
  build_and_test:
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
  build_and_test:
    ...
    docker:
      - image: cimg/node:<< parameters.node-version >>
    parallelism: 4
    ...
```

- Make sure test results are merged correctly:

```yaml
jobs:
  build_and_test:
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
      - build_and_test
      - dependency_vulnerability_scan
      - build-docker
```

- Add `requires` stanza to the job in the workflow, which ensures that verification jobs must complete before building the Docker image.

```yaml
workflows:
  run-tests:
    jobs:
      - build_and_test
      - dependency_vulnerability_scan
      - build-docker:
          requires:
            - build_and_test
            - dependency_vulnerability_scan
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
      - build_and_test
      - dependency_vulnerability_scan
      - build-docker:
          requires:
            - build_and_test
            - dependency_vulnerability_scan
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
            - build_and_test
            - dependency_vulnerability_scan
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
            - build_and_test
            - dependency_vulnerability_scan
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
      - dependency_vulnerability_scan
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
      - build_and_test:
          matrix:
            parameters:
              node_version: ["16.14.0", "14.19.0", "17.6.0" ]
      - dependency_vulnerability_scan
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
      - build_and_test:
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
      - build_and_test:
      ...
```

## Assignment!

Exercise - send message to our Discord server from CircleCI to get some CircleCI swag! ✨

Message should include:
  - your email, 
  - link to the CircleCI pipeline or job that sent the message

Discord Webhook URL will be provided at the event. 

How you implement it is up to you (there are many ways). Using an orb might be the easiest though... 

