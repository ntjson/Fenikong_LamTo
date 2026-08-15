-- The bootstrap role supplied by the postgres image is never used by Django.
-- Django migrations run as lamto_owner; web/worker processes run as lamto_writer.
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'lamto_owner') THEN
        CREATE ROLE lamto_owner
            LOGIN PASSWORD 'lamto-owner'
            NOSUPERUSER CREATEDB NOCREATEROLE NOINHERIT;
    END IF;
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'lamto_app') THEN
        CREATE ROLE lamto_app
            LOGIN PASSWORD 'lamto-app'
            NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT;
    END IF;
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'lamto_writer') THEN
        CREATE ROLE lamto_writer
            LOGIN PASSWORD 'lamto-writer'
            NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT;
    END IF;
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'lamto_service') THEN
        CREATE ROLE lamto_service
            NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT;
    END IF;
END
$$;

ALTER DATABASE lamto OWNER TO lamto_owner;
ALTER SCHEMA public OWNER TO lamto_owner;
GRANT CONNECT ON DATABASE lamto TO lamto_owner, lamto_app, lamto_writer;
GRANT lamto_service TO lamto_owner WITH ADMIN OPTION;
GRANT lamto_app TO lamto_owner WITH ADMIN OPTION;
GRANT lamto_writer TO lamto_owner WITH ADMIN OPTION;
REVOKE CREATE ON SCHEMA public FROM lamto_app, lamto_writer;
