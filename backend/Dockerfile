# Use a slim Python base image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirement file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your backend code
COPY . .

ENV PYTHONPATH=/app

# Expose the FastAPI port
EXPOSE 8000

# By default, run uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]