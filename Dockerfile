FROM python:3.10

# Install system dependencies including Tesseract and OpenCV requirements
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy project files
COPY . .

# Command to run the application
CMD ["gunicorn", "phoneproject.wsgi", "--log-file", "-"]