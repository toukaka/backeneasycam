#!/bin/bash

sudo cp -rv app.py /var/www/backend_app/
sudo cp -rv app.wsgi /var/www/backend_app/
sudo cp -rv user.py /var/www/backend_app/
sudo cp -rv templates /var/www/backend_app/
sudo cp -rv static /var/www/backend_app/
sync
sudo systemctl reload apache2
