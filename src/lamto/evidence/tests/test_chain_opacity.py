"""Chain-payload opacity audit (spec 2.2).

Only opaque values reach the chain: random event IDs and payload hashes.
These tests freeze the properties that keep payload hashes non-invertible
and keep identifying free text (building names, personal content) out of
evidence payload schemas forever.
"""

from django.test import SimpleTestCase

from lamto.evidence.models import EvidenceType
from lamto.evidence.services import (
    EVIDENCE_PAYLOAD_SCHEMAS,
    HASH_PAYLOAD_SHAPES,
    OPAQUE_PAYLOAD_SHAPES,
)


class ChainOpacityTests(SimpleTestCase):
    def test_every_event_type_has_a_schema(self):
        self.assertEqual(
            set(EVIDENCE_PAYLOAD_SCHEMAS),
            {event_type.value for event_type in EvidenceType}
            - {
                EvidenceType.RESERVED_2.value,
                EvidenceType.RESERVED_3.value,
                EvidenceType.RESERVED_4.value,
                EvidenceType.RESERVED_5.value,
            },
        )

    def test_payload_schemas_admit_only_opaque_shapes(self):
        for event_type, (required, optional) in EVIDENCE_PAYLOAD_SCHEMAS.items():
            for field, shape in {**required, **optional}.items():
                with self.subTest(event_type=event_type, field=field):
                    if field == "schema":
                        continue
                    if isinstance(shape, frozenset):
                        # Closed enums only: uppercase machine tokens, no names.
                        for member in shape:
                            self.assertRegex(member, r"^[A-Z_]+$")
                    else:
                        self.assertIn(shape, OPAQUE_PAYLOAD_SHAPES)

    def test_every_schema_requires_a_hash_field(self):
        # At least one 256-bit unknown per payload keeps the on-chain
        # payload hash non-invertible by dictionary attack.
        for event_type, (required, _optional) in EVIDENCE_PAYLOAD_SCHEMAS.items():
            with self.subTest(event_type=event_type):
                self.assertTrue(
                    HASH_PAYLOAD_SHAPES.intersection(required.values()),
                    f"event type {event_type} has no required hash field",
                )
