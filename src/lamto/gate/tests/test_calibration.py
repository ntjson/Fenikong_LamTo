import pytest
from lamto.gate.calibration import CalibrationScores, error_rates, score_pairs, sweep

def scores(): return CalibrationScores([.9, .85, .8, .55, .35], [.1, .12, .2, .42])
def test_error_rates(): assert error_rates(scores(), .5) == pytest.approx((0, .2))
def test_low_threshold_admits_impostor(): assert error_rates(scores(), .4)[0] == pytest.approx(.25)
def test_sweep_is_inclusive():
    rows = sweep(scores(), .3, .6, .01)
    assert len(rows) == 31 and rows[0].threshold == .3 and rows[-1].threshold == .6
def test_empty_scores_are_safe(): assert error_rates(CalibrationScores(), .5) == (0, 0)

@pytest.mark.django_db
def test_score_pairs_uses_exact_model_name_and_version(occupancy, use_fake_embedder):
    from lamto.gate.crypto import seal_embedding
    from lamto.gate.models import FaceEnrollment, ReviewStatus
    from lamto.gate.tests.fakes import fake_vector
    FaceEnrollment.objects.create(occupancy=occupancy, embedding=seal_embedding(fake_vector("resident")), model_name="fake", model_version="1", status=ReviewStatus.APPROVED)
    with pytest.raises(ValueError, match="outside"):
        score_pairs(occupancy.unit.building, [(occupancy.pk, fake_vector("resident"))], model_name="fake", model_version="2")


@pytest.mark.django_db
def test_score_pairs_rejects_probe_outside_selected_building_model_enrollments(occupancy, second_occupancy, use_fake_embedder):
    from lamto.gate.crypto import seal_embedding
    from lamto.gate.models import FaceEnrollment, ReviewStatus
    from lamto.gate.tests.fakes import fake_vector
    FaceEnrollment.objects.create(occupancy=occupancy, embedding=seal_embedding(fake_vector("resident")), model_name="fake", model_version="1", status=ReviewStatus.APPROVED)
    with pytest.raises(ValueError, match="outside"):
        score_pairs(occupancy.unit.building, [(second_occupancy.pk, fake_vector("other"))], model_name="fake", model_version="1")
