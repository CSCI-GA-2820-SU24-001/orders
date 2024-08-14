# NYU DevOps Project Template

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Language-Python-blue.svg)](https://python.org/)
![Build Status](https://github.com/CSCI-GA-2820-SU24-001/orders/actions/workflows/workflow.yml/badge.svg)
[![codecov](https://codecov.io/gh/CSCI-GA-2820-SU24-001/orders/graph/badge.svg?token=OY1LYZTLY0)](https://codecov.io/gh/CSCI-GA-2820-SU24-001/orders)


## Overview

This project is for NYU Devops class. The primary goal of this project is to develop microservices for managing orders and items. Each microservice is designed to be RESTful, and support the complete lifecycle calls endpoints of Create, Read, Update, & Delete
(CRUD) plus List. 

The `/service` folder contains the `models.py` file for order and item model. The `routes.py` file for the service. The `/tests` folder has test case starter code for testing the model and the service separately. 

## Automatic Setup

To use this repo: start your own repo using it as a git template. To do this just press the green **Use this template** button in GitHub and this will become the source for your repository.

## Manual Setup

You can also clone this repository and then copy and paste the starter code into your project repo folder on your local computer. Be careful not to copy over your own `README.md` file so be selective in what you copy.

There are 4 hidden files that you will need to copy manually if you use the Mac Finder or Windows Explorer to copy files from this folder into your repo folder.

These should be copied using a bash shell as follows:

```bash
    cp .gitignore  ../<your_repo_folder>/
    cp .flaskenv ../<your_repo_folder>/
    cp .gitattributes ../<your_repo_folder>/
```

## Contents

The project contains the following:

```text
.gitignore          - this will ignore vagrant and other metadata files
.flaskenv           - Environment variables to configure Flask
.gitattributes      - File to gix Windows CRLF issues
.devcontainers/     - Folder with support for VSCode Remote Containers
dot-env-example     - copy to .env to use environment variables
pyproject.toml      - Poetry list of Python libraries required by your code

service/                   - service python package
├── __init__.py            - package initializer
├── config.py              - configuration parameters
├── models.py              - module with business models
├── routes.py              - module with service routes
└── common                 - common code package
    ├── cli_commands.py    - Flask command to recreate all tables
    ├── error_handlers.py  - HTTP error handling code
    ├── log_handlers.py    - logging setup code
    └── status.py          - HTTP status constants

tests/                     - test cases package
├── __init__.py            - package initializer
├── factories.py           - Factory for testing with fake objects
├── test_cli_commands.py   - test suite for the CLI
├── test_item.py           - test suite for item models
├── test_order.py          - test suite for order models
└──  test_routes.py         - test suite for service routes
```

## REST API Conventions
The Orders API endpoints:

| Operation                         | Method | URL                                          |
|-----------------------------------|--------|----------------------------------------------|
| **Create a new order**         | POST   | `/orders`                                 |
| **View a order**                | GET    | `/orders/order_id`                   |
| **List all orders**            | GET    | `/orders/customer/customer_id`                                 |
| **Update the address of order**             | PUT    | `/orders/order_id`                   |
| **Update the status of order**             | PUT    | `/orders/order_id/status`                   |
| **Delete a order**             | DELETE | `/orders/order_id`                   |
| **Add an item to a order**     | POST   | `/orders/order_id/item`             |
| **View an item from a order**   | GET    | `/orders/order_id/item/item_id`   |
| **Update a order item**        | PUT    | `/orders/order_id/item/item_id`   |
| **Delete a order item**        | DELETE | `/orders/order_id/item/item_id`   |



## To Run the Tests

To run the tests for this project, you can use the command:

```bash
make test
```

It will run the test suite using `pytest` and to check the tests pass condition.

## To Run the Service

To run the orders service locally, you can use the command:

```bash
honcho start
```

After the service start, you can access at `http://localhost:8000`.

## Kubernetes
- **Delete cluster:** make cluster-rm
- **Create cluster:** make cluster
- **Build the docker image:** docker build -t orders:latest .
- **Create tag for image:** docker tag orders:latest cluster-registry:5000/orders:latest
- **Push the docker image:** docker push cluster-registry:5000/orders:latest
- **Apply Kubernetes:** kubectl apply -f k8s/ or alternatively, make deploy


## License

Copyright (c) 2016, 2024 [John Rofrano](https://www.linkedin.com/in/JohnRofrano/). All rights reserved.

Licensed under the Apache License. See [LICENSE](LICENSE)

This repository is part of the New York University (NYU) masters class: **CSCI-GA.2820-001 DevOps and Agile Methodologies** created and taught by [John Rofrano](https://cs.nyu.edu/~rofrano/), Adjunct Instructor, NYU Courant Institute, Graduate Division, Computer Science, and NYU Stern School of Business.
