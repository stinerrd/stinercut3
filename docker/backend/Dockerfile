FROM python:3.11-slim

# Install FFmpeg, rsvg-convert and system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libavcodec-extra \
    libavformat-dev \
    libavutil-dev \
    libswscale-dev \
    libavfilter-dev \
    libzbar0 \
    librsvg2-bin \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements file
COPY backend/requirements.txt /app/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend /app

# Create shared video directories
RUN mkdir -p /shared-videos/uploads /shared-videos/temp /shared-videos/output /shared-videos/thumbnails

# Create videodata directory
RUN mkdir -p /videodata

# Create app user with UID/GID 1000 (matches typical host user)
RUN groupadd -g 1000 appuser && useradd -u 1000 -g appuser -m appuser

# Set ownership of directories
RUN chown -R appuser:appuser /videodata /shared-videos /app

# Set custom bash prompt for both root and appuser
RUN echo 'PS1="\[\033[01;32m\]\u@backend\[\033[00m\]:\[\033[01;34m\]\w\[\033[01;31m\] \$\[\033[00m\] "' >> /root/.bashrc \
    && echo 'PS1="\[\033[01;32m\]\u@backend\[\033[00m\]:\[\033[01;34m\]\w\[\033[01;31m\] \$\[\033[00m\] "' >> /home/appuser/.bashrc

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
