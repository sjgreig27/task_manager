# Use the official Python image from the Docker Hub
FROM python:3.10

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir poetry

# Set the working directory
WORKDIR /app

# Copy the pyproject.toml and poetry.lock files to the container
COPY pyproject.toml poetry.lock ./

ARG POETRY_VIRTUALENVS_CREATE=false
RUN poetry install --without dev --no-root

COPY . .
RUN chmod +x ./start.sh

# Expose the port FastAPI will run on
EXPOSE 8000

# Command to run the FastAPI app with uvicorn
CMD ["./start.sh"]