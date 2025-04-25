#!/bin/bash
set -e

# Esperar a que la base de datos esté disponible (reemplaza 'db' con el nombre de tu servicio de base de datos) esto es un bucle
until PGPASSWORD="$POSTGRES_PASSWORD" psql -h "db" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c '\q'
do
  echo "Waiting for database..."
  sleep 5
done

echo "Database is up!"

# Ejecutar las migraciones
python manage.py makemigrations --noinput
python manage.py migrate --noinput

# Crear el superusuario si no existe
python manage.py shell -c "from django.contrib.auth.models import User; \
if not User.objects.filter(username='${DJANGO_SUPERUSER_USERNAME}').exists(): \
    User.objects.create_superuser('${DJANGO_SUPERUSER_USERNAME}', '${DJANGO_SUPERUSER_EMAIL}', '${DJANGO_SUPERUSER_PASSWORD}')"

# Ejecutar el servidor de Django (esto se ejecutará si el script no termina antes)
exec "$@"