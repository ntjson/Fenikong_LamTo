from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("evidence", "0001_initial")]

    operations = [
        migrations.RunSQL(
            """
            CREATE OR REPLACE FUNCTION evidence_protect_outbox_identity()
            RETURNS trigger AS $$
            BEGIN
                IF TG_OP = 'INSERT' THEN
                    IF current_setting('lamto.outbox_transition', true) IS DISTINCT FROM 'on' THEN
                        RAISE EXCEPTION 'outbox inserts require the queue service'
                        USING ERRCODE = 'check_violation';
                    END IF;
                    RETURN NEW;
                END IF;
                IF TG_OP = 'DELETE' OR OLD.event_id IS DISTINCT FROM NEW.event_id
                   OR OLD.event_type IS DISTINCT FROM NEW.event_type
                   OR OLD.payload IS DISTINCT FROM NEW.payload
                   OR OLD.payload_hash IS DISTINCT FROM NEW.payload_hash
                   OR OLD.previous_hash IS DISTINCT FROM NEW.previous_hash
                   OR OLD.signer_wallet_id IS DISTINCT FROM NEW.signer_wallet_id
                   OR OLD.signature IS DISTINCT FROM NEW.signature
                   OR OLD.created_at IS DISTINCT FROM NEW.created_at THEN
                    RAISE EXCEPTION 'signed outbox identity is immutable' USING ERRCODE = 'check_violation';
                END IF;
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;

            DROP TRIGGER blockchain_outbox_identity ON evidence_blockchainoutboxevent;
            CREATE TRIGGER blockchain_outbox_identity
            BEFORE INSERT OR UPDATE OR DELETE ON evidence_blockchainoutboxevent
            FOR EACH ROW EXECUTE FUNCTION evidence_protect_outbox_identity();

            CREATE FUNCTION evidence_prevent_outbox_truncate()
            RETURNS trigger AS $$
            BEGIN
                RAISE EXCEPTION 'signed outbox history is immutable' USING ERRCODE = 'check_violation';
            END;
            $$ LANGUAGE plpgsql;
            CREATE TRIGGER blockchain_outbox_truncate
            BEFORE TRUNCATE ON evidence_blockchainoutboxevent
            FOR EACH STATEMENT EXECUTE FUNCTION evidence_prevent_outbox_truncate();
            """,
            """
            DROP TRIGGER blockchain_outbox_truncate ON evidence_blockchainoutboxevent;
            DROP FUNCTION evidence_prevent_outbox_truncate();
            DROP TRIGGER blockchain_outbox_identity ON evidence_blockchainoutboxevent;
            CREATE OR REPLACE FUNCTION evidence_protect_outbox_identity()
            RETURNS trigger AS $$
            BEGIN
                IF TG_OP = 'DELETE' OR OLD.event_id IS DISTINCT FROM NEW.event_id
                   OR OLD.event_type IS DISTINCT FROM NEW.event_type
                   OR OLD.payload IS DISTINCT FROM NEW.payload
                   OR OLD.payload_hash IS DISTINCT FROM NEW.payload_hash
                   OR OLD.previous_hash IS DISTINCT FROM NEW.previous_hash
                   OR OLD.signer_wallet_id IS DISTINCT FROM NEW.signer_wallet_id
                   OR OLD.signature IS DISTINCT FROM NEW.signature
                   OR OLD.created_at IS DISTINCT FROM NEW.created_at THEN
                    RAISE EXCEPTION 'signed outbox identity is immutable' USING ERRCODE = 'check_violation';
                END IF;
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;
            CREATE TRIGGER blockchain_outbox_identity
            BEFORE UPDATE OR DELETE ON evidence_blockchainoutboxevent
            FOR EACH ROW EXECUTE FUNCTION evidence_protect_outbox_identity();
            """,
        )
    ]
