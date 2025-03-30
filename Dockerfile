FROM python:3.11-slim

WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create necessary directories
RUN mkdir -p uploads reports

# Set environment variables
ENV FLASK_ENV=production
ENV PORT=8080

# Expose the port the app runs on
EXPOSE 8080

# Command to run the application
CMD gunicorn --bind 0.0.0.0:$PORT lutcomparetool_app:app
