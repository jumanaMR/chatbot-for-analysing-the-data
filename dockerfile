# Use an official Python runtime
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy project files into the container
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir flask flask-cors pdfplumber transformers

# Expose the application port
EXPOSE 5000

# Run the application
CMD ["python", "app.py"]
