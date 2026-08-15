from lamto.maintenance.triage_prompt import (
    CATEGORY_CODES,
    SUGGESTED_DEPARTMENTS,
    build_system_prompt,
)


def test_system_prompt_covers_contract_taxonomy_and_untrusted_warning():
    prompt = build_system_prompt()
    # Names every model-returned contract key.
    for key in (
        "category",
        "interpreted_location",
        "urgency",
        "confidence_percent",
        "requires_manual_review",
        "duplicate_report_ids",
        "department",
        "deadline_minutes",
        "missing_information",
    ):
        assert key in prompt
    # It must NOT ask the model for provider_request_id (we inject that).
    assert "provider_request_id" not in prompt
    # Taxonomy guidance is present.
    assert SUGGESTED_DEPARTMENTS[0] in prompt
    # Category codes are the required closed set.
    for code in CATEGORY_CODES:
        assert code in prompt
    # Prompt-injection defense is present.
    assert "UNTRUSTED" in prompt
    # Text-only triage.
    assert "photo" in prompt.lower()
