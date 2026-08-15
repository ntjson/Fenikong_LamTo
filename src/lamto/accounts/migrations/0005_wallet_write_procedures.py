import os

from django.db import migrations


def provision_service_owner(apps, schema_editor):
    service_role = os.getenv("POSTGRES_SERVICE_ROLE") or "lamto_service"
    executor_role = os.getenv("POSTGRES_EXECUTOR_ROLE") or "lamto_writer"
    quote_name = schema_editor.connection.ops.quote_name
    quoted_service_role = quote_name(service_role)

    with schema_editor.connection.cursor() as cursor:
        cursor.execute(
            "SELECT current_user, rolsuper, rolcreaterole, oid "
            "FROM pg_roles WHERE rolname = current_user"
        )
        current_user, is_superuser, can_create_role, current_oid = cursor.fetchone()
        if is_superuser:
            raise RuntimeError("Run accountability migrations with a non-superuser schema owner.")
        if service_role == current_user:
            raise RuntimeError("POSTGRES_SERVICE_ROLE must be different from the migration/application role.")
        cursor.execute("SELECT oid FROM pg_roles WHERE rolname = %s", [service_role])
        service_oid_row = cursor.fetchone()
        if service_oid_row is None:
            if not (is_superuser or can_create_role):
                raise RuntimeError(
                    f"PostgreSQL role {service_role!r} must be pre-created, "
                    "or the migration role must have CREATEROLE."
                )
            cursor.execute(
                f"CREATE ROLE {quoted_service_role} NOLOGIN NOSUPERUSER NOCREATEDB "
                f"NOCREATEROLE NOINHERIT"
            )
            cursor.execute("SELECT oid FROM pg_roles WHERE rolname = %s", [service_role])
            service_oid_row = cursor.fetchone()

        cursor.execute(
            "SELECT 1 FROM pg_auth_members WHERE roleid = %s AND member = %s",
            [service_oid_row[0], current_oid],
        )
        if cursor.fetchone() is None:
            cursor.execute(f"GRANT {quoted_service_role} TO {quote_name(current_user)}")

        if executor_role:
            if executor_role == service_role:
                raise RuntimeError("POSTGRES_EXECUTOR_ROLE must be different from POSTGRES_SERVICE_ROLE.")
            cursor.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", [executor_role])
            if cursor.fetchone() is None:
                raise RuntimeError(f"PostgreSQL executor role {executor_role!r} does not exist.")
            quoted_executor_role = quote_name(executor_role)
            cursor.execute(
                "GRANT EXECUTE ON FUNCTION lamto_security.accounts_register_signer_wallet(bigint, text), "
                "lamto_security.accounts_revoke_signer_wallet(bigint, bigint) TO "
                + quoted_executor_role
            )

        cursor.execute(
            f"GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE "
            f"accounts_organizationmembership, accounts_signerwallet, "
            f"accounts_signerauthorizationrequest TO {quoted_service_role}"
        )
        cursor.execute(
            f"GRANT USAGE, SELECT ON SEQUENCE accounts_signerwallet_id_seq, "
            f"accounts_signerauthorizationrequest_id_seq TO {quoted_service_role}"
        )
        cursor.execute(
            f"GRANT USAGE, CREATE ON SCHEMA lamto_security TO {quoted_service_role}"
        )
        cursor.execute(
            "ALTER FUNCTION lamto_security.accounts_register_signer_wallet(bigint, text) OWNER TO "
            + quoted_service_role
        )
        cursor.execute(
            "ALTER FUNCTION lamto_security.accounts_revoke_signer_wallet(bigint, bigint) OWNER TO "
            + quoted_service_role
        )


class Migration(migrations.Migration):
    dependencies = [("accounts", "0004_guard_wallet_transitions")]

    operations = [
        migrations.RunSQL(
            "CREATE SCHEMA IF NOT EXISTS lamto_security AUTHORIZATION CURRENT_USER"
        ),
        migrations.RunSQL(
            r"""
            CREATE FUNCTION lamto_security.accounts_register_signer_wallet(p_membership_id bigint, p_address text)
            RETURNS bigint
            LANGUAGE plpgsql SECURITY DEFINER SET search_path = pg_catalog, public AS $$
            DECLARE
                wallet_id bigint;
                old_wallet record;
            BEGIN
                PERFORM 1 FROM public.accounts_organizationmembership
                WHERE id = p_membership_id AND active AND role IN ('OPERATOR', 'BOARD', 'RESIDENT_REP')
                FOR UPDATE;
                IF NOT FOUND THEN
                    RAISE EXCEPTION 'membership is not eligible to register a wallet'
                    USING ERRCODE = 'insufficient_privilege';
                END IF;

                FOR old_wallet IN
                    UPDATE public.accounts_signerwallet
                    SET active = FALSE, revoked_at = clock_timestamp()
                    WHERE membership_id = p_membership_id AND active
                    RETURNING id
                LOOP
                    INSERT INTO public.accounts_signerauthorizationrequest
                        (wallet_id, requested_by_id, action, status, transaction_hash,
                         last_error, created_at, confirmed_at)
                    VALUES (old_wallet.id, p_membership_id, 'REVOKE', 'PENDING', '', '',
                            clock_timestamp(), NULL)
                    ON CONFLICT ON CONSTRAINT wallet_authorization_action_once DO NOTHING;
                END LOOP;

                INSERT INTO public.accounts_signerwallet
                    (membership_id, address, active, registered_at, revoked_at)
                VALUES (p_membership_id, p_address, TRUE, clock_timestamp(), NULL)
                RETURNING id INTO wallet_id;
                INSERT INTO public.accounts_signerauthorizationrequest
                    (wallet_id, requested_by_id, action, status, transaction_hash,
                     last_error, created_at, confirmed_at)
                VALUES (wallet_id, p_membership_id, 'AUTHORIZE', 'PENDING', '', '',
                        clock_timestamp(), NULL);
                RETURN wallet_id;
            END;
            $$;

            CREATE FUNCTION lamto_security.accounts_revoke_signer_wallet(p_wallet_id bigint, p_authorizer_id bigint)
            RETURNS bigint
            LANGUAGE plpgsql SECURITY DEFINER SET search_path = pg_catalog, public AS $$
            DECLARE
                owner_membership_id bigint;
                owner_organization_id bigint;
            BEGIN
                SELECT membership_id INTO owner_membership_id
                FROM public.accounts_signerwallet WHERE id = p_wallet_id;
                IF owner_membership_id IS NULL THEN
                    RAISE EXCEPTION 'wallet does not exist' USING ERRCODE = 'no_data_found';
                END IF;
                PERFORM 1 FROM public.accounts_organizationmembership
                WHERE id IN (owner_membership_id, p_authorizer_id) ORDER BY id FOR UPDATE;
                SELECT organization_id INTO owner_organization_id
                FROM public.accounts_organizationmembership WHERE id = owner_membership_id;
                PERFORM 1 FROM public.accounts_organizationmembership
                WHERE id = p_authorizer_id AND active
                  AND role IN ('OPERATOR', 'BOARD', 'RESIDENT_REP')
                  AND organization_id = owner_organization_id;
                IF NOT FOUND THEN
                    RAISE EXCEPTION 'wallet revocation requires an eligible membership in the same organization'
                    USING ERRCODE = 'insufficient_privilege';
                END IF;

                UPDATE public.accounts_signerwallet
                SET active = FALSE, revoked_at = clock_timestamp()
                WHERE id = p_wallet_id AND active;
                IF FOUND THEN
                    INSERT INTO public.accounts_signerauthorizationrequest
                        (wallet_id, requested_by_id, action, status, transaction_hash,
                         last_error, created_at, confirmed_at)
                    VALUES (p_wallet_id, p_authorizer_id, 'REVOKE', 'PENDING', '', '',
                            clock_timestamp(), NULL)
                    ON CONFLICT ON CONSTRAINT wallet_authorization_action_once DO NOTHING;
                END IF;
                RETURN p_wallet_id;
            END;
            $$;

            REVOKE ALL ON FUNCTION lamto_security.accounts_register_signer_wallet(bigint, text) FROM PUBLIC;
            REVOKE ALL ON FUNCTION lamto_security.accounts_revoke_signer_wallet(bigint, bigint) FROM PUBLIC;

            CREATE OR REPLACE FUNCTION accounts_protect_wallet_history()
            RETURNS trigger AS $$
            DECLARE service_owner name;
            BEGIN
                SELECT pg_get_userbyid(proowner) INTO service_owner
                FROM pg_proc WHERE oid = 'lamto_security.accounts_register_signer_wallet(bigint,text)'::regprocedure;
                IF TG_OP = 'INSERT' THEN
                    IF current_user IS DISTINCT FROM service_owner THEN
                        RAISE EXCEPTION 'signer wallet inserts require the registration procedure'
                        USING ERRCODE = 'check_violation';
                    END IF;
                    RETURN NEW;
                END IF;
                IF TG_OP = 'DELETE' OR OLD.membership_id IS DISTINCT FROM NEW.membership_id
                   OR OLD.address IS DISTINCT FROM NEW.address
                   OR OLD.registered_at IS DISTINCT FROM NEW.registered_at
                   OR (NOT OLD.active AND NEW.active)
                   OR (OLD.revoked_at IS NOT NULL AND OLD.revoked_at IS DISTINCT FROM NEW.revoked_at) THEN
                    RAISE EXCEPTION 'signer wallet history is immutable' USING ERRCODE = 'check_violation';
                END IF;
                IF (OLD.active IS DISTINCT FROM NEW.active OR OLD.revoked_at IS DISTINCT FROM NEW.revoked_at)
                   AND current_user IS DISTINCT FROM service_owner THEN
                    RAISE EXCEPTION 'wallet revocation requires the wallet procedure'
                    USING ERRCODE = 'check_violation';
                END IF;
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;

            CREATE OR REPLACE FUNCTION accounts_protect_signer_request_identity()
            RETURNS trigger AS $$
            DECLARE service_owner name;
            BEGIN
                SELECT pg_get_userbyid(proowner) INTO service_owner
                FROM pg_proc WHERE oid = 'lamto_security.accounts_register_signer_wallet(bigint,text)'::regprocedure;
                IF TG_OP = 'INSERT' AND current_user IS DISTINCT FROM service_owner THEN
                    RAISE EXCEPTION 'signer authorization requests require the wallet procedure'
                    USING ERRCODE = 'check_violation';
                END IF;
                IF TG_OP = 'DELETE' OR (TG_OP = 'UPDATE' AND (
                   OLD.wallet_id IS DISTINCT FROM NEW.wallet_id
                   OR OLD.requested_by_id IS DISTINCT FROM NEW.requested_by_id
                   OR OLD.action IS DISTINCT FROM NEW.action
                   OR OLD.created_at IS DISTINCT FROM NEW.created_at)) THEN
                    RAISE EXCEPTION 'signer authorization request identity is immutable'
                    USING ERRCODE = 'check_violation';
                END IF;
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;

            DROP TRIGGER signer_authorization_request_identity ON accounts_signerauthorizationrequest;
            CREATE TRIGGER signer_authorization_request_identity
            BEFORE INSERT OR UPDATE OR DELETE ON accounts_signerauthorizationrequest
            FOR EACH ROW EXECUTE FUNCTION accounts_protect_signer_request_identity();
            """,
            r"""
            DROP TRIGGER signer_authorization_request_identity ON accounts_signerauthorizationrequest;
            CREATE TRIGGER signer_authorization_request_identity
            BEFORE UPDATE OR DELETE ON accounts_signerauthorizationrequest
            FOR EACH ROW EXECUTE FUNCTION accounts_protect_signer_request_identity();
            DROP FUNCTION lamto_security.accounts_revoke_signer_wallet(bigint, bigint);
            DROP FUNCTION lamto_security.accounts_register_signer_wallet(bigint, text);
            """,
        ),
        migrations.RunPython(provision_service_owner, migrations.RunPython.noop),
    ]
