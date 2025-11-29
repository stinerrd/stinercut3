FROM php:8.3-fpm

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    libpng-dev \
    libonig-dev \
    libxml2-dev \
    zip \
    unzip \
    nginx \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Install PHP extensions
RUN docker-php-ext-install pdo_mysql mbstring exif pcntl bcmath gd

# Install Composer
COPY --from=composer:latest /usr/bin/composer /usr/bin/composer

# Install Symfony CLI
RUN curl -sS https://get.symfony.com/cli/installer | bash && \
    mv /root/.symfony*/bin/symfony /usr/local/bin/symfony

# Set working directory
WORKDIR /var/www/html

# Copy nginx configuration
COPY docker/frontend/nginx.conf /etc/nginx/sites-available/default

# Create shared video directories
RUN mkdir -p /shared-videos/uploads /shared-videos/temp /shared-videos/output /shared-videos/thumbnails

# Set proper permissions
RUN chown -R www-data:www-data /var/www/html /shared-videos

# Expose port 80
EXPOSE 80

# Start nginx and php-fpm
CMD service nginx start && php-fpm
