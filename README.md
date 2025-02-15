# Logistics Optimization API

This project provides a FastAPI-based logistics optimization API.

## Prerequisites
- Docker installed on your machine.
- (Optional) Docker Compose if using multiple services.

## Setup & Run using Docker

1. Build the Docker image:
   ```bash
   docker build -t logistics-optimization .
   ```

2. Run the container:
   ```bash
   docker run -d -p 8000:8000 logistics-optimization
   ```

3. Access the API at [http://localhost:8000](http://localhost:8000).

## Using Docker Compose
If you prefer Docker Compose, create a `docker-compose.yml` file with the following minimal configuration:
