# RetailCRM Test Application

A simple application to interact with RetailCRM API.

## Prerequisites

- Docker installed on your system
- Docker Compose (optional, for Docker Compose setup)

## Setup

1. **Create a `.env` file** in the project root directory with the following variables:
    ```bash
    RETAILCRM_API_KEY=your_api_key_here
    RETAILCRM_SUBDOMAIN=your_subdomain_here
    ```
   Replace `your_api_key_here` and `your_subdomain_here` with your RetailCRM API credentials.

## Running the Project

### Using Docker

1. Build the Docker image and run the container:
    ```bash
    docker build -t retailcrm_test_app . && docker run --env-file .env -p 80:80 retailcrm_test_app
    ```

### Using Docker Compose

1. Run the application with Docker Compose:
    ```bash
    docker-compose up
    ```

## Accessing API Documentation

Once the application is running, access the interactive API documentation at:  
[http://127.0.0.1/docs](http://127.0.0.1/docs)

---