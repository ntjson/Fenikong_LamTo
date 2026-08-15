import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("accounts", "0002_capability_grants")]

    operations = [
        migrations.CreateModel(
            name="SignerWallet",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("address", models.CharField(max_length=42)),
                ("active", models.BooleanField(default=True)),
                ("registered_at", models.DateTimeField(auto_now_add=True)),
                ("revoked_at", models.DateTimeField(blank=True, null=True)),
                ("membership", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="accounts.organizationmembership")),
            ],
        ),
        migrations.CreateModel(
            name="SignerAuthorizationRequest",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("action", models.CharField(choices=[("AUTHORIZE", "Authorize"), ("REVOKE", "Revoke")], max_length=16)),
                ("status", models.CharField(choices=[("PENDING", "Pending"), ("CONFIRMED", "Confirmed"), ("FAILED", "Failed")], default="PENDING", max_length=16)),
                ("transaction_hash", models.CharField(blank=True, max_length=66)),
                ("last_error", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("confirmed_at", models.DateTimeField(blank=True, null=True)),
                ("requested_by", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="accounts.organizationmembership")),
                ("wallet", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="accounts.signerwallet")),
            ],
        ),
        migrations.CreateModel(
            name="WalletRegistrationChallenge",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nonce", models.CharField(max_length=64, unique=True)),
                ("expires_at", models.DateTimeField()),
                ("consumed_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("membership", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="accounts.organizationmembership")),
            ],
        ),
        migrations.AddConstraint(
            model_name="signerwallet",
            constraint=models.UniqueConstraint(condition=models.Q(("active", True)), fields=("membership",), name="one_active_wallet_per_membership"),
        ),
        migrations.AddConstraint(
            model_name="signerwallet",
            constraint=models.UniqueConstraint(condition=models.Q(("active", True)), fields=("address",), name="one_active_wallet_per_address"),
        ),
        migrations.AddConstraint(
            model_name="signerwallet",
            constraint=models.CheckConstraint(condition=models.Q(models.Q(("active", True), ("revoked_at__isnull", True)), models.Q(("active", False), ("revoked_at__isnull", False)), _connector="OR"), name="wallet_active_revocation_consistent"),
        ),
        migrations.AddConstraint(
            model_name="signerauthorizationrequest",
            constraint=models.UniqueConstraint(fields=("wallet", "action"), name="wallet_authorization_action_once"),
        ),
        migrations.AddConstraint(
            model_name="walletregistrationchallenge",
            constraint=models.UniqueConstraint(condition=models.Q(("consumed_at__isnull", True)), fields=("membership",), name="one_unused_wallet_challenge"),
        ),
        migrations.RunSQL(
            """
            CREATE FUNCTION accounts_protect_wallet_history()
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

            CREATE FUNCTION accounts_protect_signer_request_identity()
            RETURNS trigger AS $$
            BEGIN
                IF TG_OP = 'DELETE' OR OLD.wallet_id IS DISTINCT FROM NEW.wallet_id
                   OR OLD.requested_by_id IS DISTINCT FROM NEW.requested_by_id
                   OR OLD.action IS DISTINCT FROM NEW.action
                   OR OLD.created_at IS DISTINCT FROM NEW.created_at THEN
                    RAISE EXCEPTION 'signer authorization request identity is immutable' USING ERRCODE = 'check_violation';
                END IF;
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;

            CREATE TRIGGER signer_authorization_request_identity
            BEFORE UPDATE OR DELETE ON accounts_signerauthorizationrequest
            FOR EACH ROW EXECUTE FUNCTION accounts_protect_signer_request_identity();
            """,
            """
            DROP TRIGGER signer_authorization_request_identity ON accounts_signerauthorizationrequest;
            DROP FUNCTION accounts_protect_signer_request_identity();
            DROP TRIGGER signer_wallet_history ON accounts_signerwallet;
            DROP FUNCTION accounts_protect_wallet_history();
            """,
        ),
    ]
