#!/usr/bin/env bash

cd $(dirname $0)/..

git pull origin main
echo "Pull: ok"

source venv/bin/activate
pip install -r requirements.txt
echo "Requirements: ok"

source .env
python manage.py makemigrations
python manage.py migrate
echo "Migrate: ok"

python manage.py collectstatic --noinput
echo "Static: ok"

sudo systemctl daemon-reload
sudo systemctl restart gunicorn
echo "Reloaded."