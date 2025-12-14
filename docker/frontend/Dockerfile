FROM php:8.3-fpm

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    libpng-dev \
    libjpeg-dev \
    libfreetype6-dev \
    libonig-dev \
    libxml2-dev \
    zip \
    unzip \
    nginx \
    && rm -rf /var/lib/apt/lists/*

# Configure and install PHP extensions
RUN docker-php-ext-configure gd --with-jpeg --with-freetype \
    && docker-php-ext-install pdo_mysql mbstring exif pcntl bcmath gd

# Configure PHP upload limits
RUN echo "upload_max_filesize = 200M" >> /usr/local/etc/php/conf.d/uploads.ini \
    && echo "post_max_size = 200M" >> /usr/local/etc/php/conf.d/uploads.ini \
    && echo "max_execution_time = 300" >> /usr/local/etc/php/conf.d/uploads.ini \
    && echo "memory_limit = 256M" >> /usr/local/etc/php/conf.d/uploads.ini

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

# Create videodata directory
RUN mkdir -p /videodata

# Modify www-data to use UID/GID 1000 (matches typical host user)
RUN usermod -u 1000 www-data && groupmod -g 1000 www-data

# Set proper permissions
RUN chown -R www-data:www-data /var/www/html /shared-videos /videodata

# Set custom bash prompt
RUN echo 'PS1="\[\033[01;32m\]\u@frontend\[\033[00m\]:\[\033[01;34m\]\w\[\033[01;31m\] \$\[\033[00m\] "' >> /root/.bashrc

# Expose port 80
EXPOSE 80

# Start nginx and php-fpm
CMD ["sh", "-c", "service nginx start && php-fpm"]
