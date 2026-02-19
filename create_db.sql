-- Run this script using psql:
-- psql -U postgres -f create_db.sql

CREATE DATABASE verifihire_db;
CREATE USER verifihire_user WITH PASSWORD 'verifihire_password';

ALTER ROLE verifihire_user SET client_encoding TO 'utf8';
ALTER ROLE verifihire_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE verifihire_user SET timezone TO 'UTC';

GRANT ALL PRIVILEGES ON DATABASE verifihire_db TO verifihire_user;
-- For Postgres 15+ you also need to grant usage on the public schema
\c verifihire_db
GRANT ALL ON SCHEMA public TO verifihire_user;
