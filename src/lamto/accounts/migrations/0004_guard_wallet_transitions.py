from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("accounts", "0003_signer_wallets")]

    operations = [
        migrations.RunSQL(
            """
            CREATE OR REPLACE FUNCTION accounts_protect_wallet_history()
            RETURNS trigger AS $$
            BEGIN
                IF TG_OP = 'INSERT' THEN
                    IF current_setting('lamto.wallet_transition', true) IS DISTINCT FROM 'on' THEN
                        RAISE EXCEPTION 'signer wallet inserts require the registration service'
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
                   AND current_setting('lamto.wallet_transition', true) IS DISTINCT FROM 'on' THEN
                    RAISE EXCEPTION 'wallet revocation requires the wallet service'
                    USING ERRCODE = 'check_violation';
                END IF;
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;

            DROP TRIGGER signer_wallet_history ON accounts_signerwallet;
            CREATE TRIGGER signer_wallet_history
            BEFORE INSERT OR UPDATE OR DELETE ON accounts_signerwallet
            FOR EACH ROW EXECUTE FUNCTION accounts_protect_wallet_history();
            """,
            """
            DROP TRIGGER signer_wallet_history ON accounts_signerwallet;
            CREATE OR REPLACE FUNCTION accounts_protect_wallet_history()
            RETURNS trigger AS $$
            BEGIN
                IF TG_OP = 'DELETE' OR OLD.membership_id IS DISTINCT FROM NEW.membership_id
                   OR OLD.address IS DISTINCT FROM NEW.address
                   OR OLD.registered_at IS DISTINCT FROM NEW.registered_at
                   OR (NOT OLD.active AND NEW.active)
                   OR (OLD.revoked_at IS NOT NULL AND OLD.revoked_at IS DISTINCT FROM NEW.revoked_at) THEN
                    RAISE EXCEPTION 'signer wallet history is immutable' USING ERRCODE = 'check_violation';
                END IF;
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;
            CREATE TRIGGER signer_wallet_history
            BEFORE UPDATE OR DELETE ON accounts_signerwallet
            FOR EACH ROW EXECUTE FUNCTION accounts_protect_wallet_history();
            """,
        )
    ]
