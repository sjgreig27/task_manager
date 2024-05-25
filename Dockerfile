# Use the official Python image from the Docker Hub
FROM python:3.10

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir poetry

# Set the working directory
WORKDIR /app

# Copy the pyproject.toml and poetry.lock files to the container
COPY pyproject.toml poetry.lock ./


# Install dependencies defined in pyproject.toml
RUN poetry install --no-root

# Copy the FastAPI app code into the container
COPY . .

# Expose the port FastAPI will run on
EXPOSE 8000

# Command to run the FastAPI app with uvicorn
CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]