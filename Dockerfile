FROM python:3.11-slim

WORKDIR /src/app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y cron \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .


# Cron job for expiring bookings
RUN echo "*/5 * * * * cd /src/app && python manage.py expire_bookings >> /var/log/cron.log 2>&1" \
    > /etc/cron.d/expire_bookings

RUN chmod 0644 /etc/cron.d/expire_bookings \
    && crontab /etc/cron.d/expire_bookings \
    && touch /var/log/cron.log

EXPOSE 8000
