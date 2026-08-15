from lamto.maintenance.triage_prompt import (
    CATEGORY_CODES,
    MANAGEMENT_QUEUE_CODES,
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
        "management_queue",
        "deadline_minutes",
        "missing_information",
    ):
        assert key in prompt
    # It must NOT ask the model for provider_request_id (we inject that).
    assert "provider_request_id" not in prompt
    # Both taxonomies are the required closed sets.
    for code in (*CATEGORY_CODES, *MANAGEMENT_QUEUE_CODES):
        assert code in prompt
    # Free text must come back Vietnamese for a Vietnamese operator.
    assert "Vietnamese" in prompt
    # Prompt-injection defense is present.
    assert "UNTRUSTED" in prompt
    # Text-only triage.
    assert "photo" in prompt.lower()
