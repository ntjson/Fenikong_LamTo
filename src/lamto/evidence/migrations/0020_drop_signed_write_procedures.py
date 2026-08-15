from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0016_remove_signerwallet_membership_and_more"),
        ("evidence", "0019_remove_blockchainoutboxevent_signer_wallet_and_more"),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                CREATE OR REPLACE FUNCTION evidence_protect_outbox_identity()
                RETURNS trigger AS $$
                BEGIN
                    IF TG_OP = 'INSERT' THEN
                        RETURN NEW;
                    END IF;
                    IF TG_OP = 'DELETE' OR OLD.event_id IS DISTINCT FROM NEW.event_id
                       OR OLD.event_type IS DISTINCT FROM NEW.event_type
                       OR OLD.payload IS DISTINCT FROM NEW.payload
                       OR OLD.payload_hash IS DISTINCT FROM NEW.payload_hash
                       OR OLD.previous_hash IS DISTINCT FROM NEW.previous_hash
                       OR OLD.signer_address IS DISTINCT FROM NEW.signer_address
                       OR OLD.building_id IS DISTINCT FROM NEW.building_id
                       OR OLD.signature IS DISTINCT FROM NEW.signature
                       OR OLD.created_at IS DISTINCT FROM NEW.created_at THEN
                        RAISE EXCEPTION 'signed outbox identity is immutable'
                        USING ERRCODE = 'check_violation';
                    END IF;
                    RETURN NEW;
                END;
                $$ LANGUAGE plpgsql;

                DROP FUNCTION IF EXISTS lamto_security.accounts_register_signer_wallet(bigint, text, text);
                DROP FUNCTION IF EXISTS lamto_security.accounts_revoke_signer_wallet(bigint, bigint, text);
                DROP FUNCTION IF EXISTS lamto_security.accounts_register_signer_wallet(bigint, text);
                DROP FUNCTION IF EXISTS lamto_security.accounts_revoke_signer_wallet(bigint, bigint);
                DROP FUNCTION IF EXISTS lamto_security.evidence_insert_outbox_event(text, smallint, jsonb, text, text, text, bigint, bigint, text, text);
                DROP FUNCTION IF EXISTS lamto_security.evidence_insert_outbox_event(text, smallint, jsonb, text, text, text, bigint, bigint, text);
                DROP FUNCTION IF EXISTS lamto_security.evidence_insert_outbox_event(text, smallint, jsonb, text, text, text, bigint, bigint);
                DROP FUNCTION IF EXISTS lamto_security.evidence_insert_platform_outbox_event(text, smallint, jsonb, text, text, text, text, bigint, text, text);
            """,
            reverse_sql=migrations.RunSQL.noop,
        )
    ]
