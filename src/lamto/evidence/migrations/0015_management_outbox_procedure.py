import os
from importlib import import_module

from django.db import migrations


_legacy_sql = import_module(
    "lamto.evidence.migrations.0009_outbox_building_backfill_and_guard"
).INSERT_FUNCTION_WITH_BUILDING

MANAGEMENT_OUTBOX_PROCEDURE = (
    "SET ROLE __SERVICE_ROLE__;\n"
    + _legacy_sql.replace(
        """    PERFORM 1 FROM public.accounts_organizationmembership
    WHERE id = p_membership_id AND active
      AND role IN ('OPERATOR', 'BOARD', 'RESIDENT_REP') FOR UPDATE;""",
        """    PERFORM 1 FROM public.accounts_managementmembership
    WHERE id = p_membership_id AND active FOR UPDATE;""",
    ).replace(
        """    SELECT o.building_id INTO v_building_id
    FROM public.accounts_organizationmembership m
    JOIN public.accounts_organization o ON o.id = m.organization_id
    WHERE m.id = p_membership_id;""",
        """    SELECT building_id INTO v_building_id
    FROM public.accounts_managementmembership
    WHERE id = p_membership_id;""",
    )
    + "\nRESET ROLE;"
)


def apply_management_outbox_procedure(apps, schema_editor):
    service_role = schema_editor.connection.ops.quote_name(
        os.getenv("POSTGRES_SERVICE_ROLE") or "lamto_service"
    )
    schema_editor.execute(
        MANAGEMENT_OUTBOX_PROCEDURE.replace(
            "__SERVICE_ROLE__", service_role
        ).replace("%", "%%")
    )


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0014_management_wallet_procedures"),
        ("evidence", "0014_alter_blockchainoutboxevent_event_type"),
    ]

    operations = [
        migrations.RunPython(
            apply_management_outbox_procedure,
            # Forward-only: stage policy does not preserve removed role data/workflows.
            migrations.RunPython.noop,
        ),
    ]
