from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# commmand to backup database
# docker exec -t nome_do_container pg_dump -U postgres barbershop_db > backup.sql