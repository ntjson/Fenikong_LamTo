import os

from django.db import migrations


MANAGEMENT_WALLET_PROCEDURES = r"""
GRANT SELECT, UPDATE ON TABLE public.accounts_managementmembership TO __SERVICE_ROLE__;
SET ROLE __SERVICE_ROLE__;

CREATE OR REPLACE FUNCTION lamto_security.accounts_register_signer_wallet(
    p_membership_id bigint, p_address text, p_authorization text
) RETURNS bigint
LANGUAGE plpgsql SECURITY DEFINER SET search_path = pg_catalog, public AS $$
DECLARE
    wallet_id bigint;
    old_wallet record;
BEGIN
    IF p_authorization IS DISTINCT FROM (
        SELECT encode(
            sha256(secret || sha256(secret || convert_to(format('wallet-register|%s|%s', p_membership_id, p_address), 'UTF8'))),
            'hex'
        )
        FROM lamto_security.write_authorization_secret
        WHERE id = TRUE
    ) THEN
        RAISE EXCEPTION 'wallet registration authorization is invalid'
        USING ERRCODE = 'insufficient_privilege';
    END IF;
    PERFORM 1 FROM public.accounts_managementmembership
    WHERE id = p_membership_id AND active
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

CREATE OR REPLACE FUNCTION lamto_security.accounts_revoke_signer_wallet(
    p_wallet_id bigint, p_authorizer_id bigint, p_authorization text
) RETURNS bigint
LANGUAGE plpgsql SECURITY DEFINER SET search_path = pg_catalog, public AS $$
DECLARE
    owner_membership_id bigint;
    owner_building_id bigint;
BEGIN
    IF p_authorization IS DISTINCT FROM (
        SELECT encode(
            sha256(secret || sha256(secret || convert_to(format('wallet-revoke|%s|%s', p_wallet_id, p_authorizer_id), 'UTF8'))),
            'hex'
        )
        FROM lamto_security.write_authorization_secret
        WHERE id = TRUE
    ) THEN
        RAISE EXCEPTION 'wallet revocation authorization is invalid'
        USING ERRCODE = 'insufficient_privilege';
    END IF;
    SELECT membership_id INTO owner_membership_id
    FROM public.accounts_signerwallet WHERE id = p_wallet_id;
    IF owner_membership_id IS NULL THEN
        RAISE EXCEPTION 'wallet does not exist' USING ERRCODE = 'no_data_found';
    END IF;
    PERFORM 1 FROM public.accounts_managementmembership
    WHERE id IN (owner_membership_id, p_authorizer_id) ORDER BY id FOR UPDATE;
    SELECT building_id INTO owner_building_id
    FROM public.accounts_managementmembership WHERE id = owner_membership_id;
    PERFORM 1 FROM public.accounts_managementmembership
    WHERE id = p_authorizer_id AND active
      AND building_id = owner_building_id;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'wallet revocation requires an eligible membership in the same building'
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

RESET ROLE;
"""


def apply_management_wallet_procedures(apps, schema_editor):
    service_role = schema_editor.connection.ops.quote_name(
        os.getenv("POSTGRES_SERVICE_ROLE") or "lamto_service"
    )
    schema_editor.execute(
        MANAGEMENT_WALLET_PROCEDURES.replace(
            "__SERVICE_ROLE__", service_role
        ).replace("%", "%%")
    )


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0013_alter_signerauthorizationrequest_requested_by_and_more"),
    ]

    operations = [
        migrations.RunPython(
            apply_management_wallet_procedures,
            # Forward-only: stage policy does not preserve removed role data/workflows.
            migrations.RunPython.noop,
        ),
    ]
