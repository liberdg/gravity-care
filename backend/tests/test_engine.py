from app import engine as eng

BASE7 = [10.0, 10.5, 9.5, 10.2, 9.8, 10.1, 9.9]  # moyenne ~10, écart-type ~0.33


def test_baseline_mean_and_floor():
    b = eng.compute_baseline(BASE7)
    assert abs(b.mean - 10.0) < 0.05
    assert eng.compute_baseline([5.0] * 7).std > 0  # plancher : jamais de division par zéro


def test_baseline_needs_two_values():
    assert eng.compute_baseline([1.0]) is None


def test_zscore():
    b = eng.compute_baseline(BASE7)
    assert round(eng.zscore(b.mean + 2 * b.std, b), 6) == 2.0


def test_aggregate_mean_and_sum():
    assert eng.aggregate([1.0, 2.0, 3.0], "mean") == 2.0
    assert eng.aggregate([1.0, 2.0, 3.0], "sum") == 6.0


def test_calibration_gives_no_finding():
    assert eng.evaluate_indicator("hrv", BASE7, 7) is None


def test_normal_values_give_no_alert():
    assert eng.evaluate_indicator("hrv", BASE7 + [10.1, 9.9, 10.0], 7) is None


def test_orange_after_two_consecutive_days():
    f = eng.evaluate_indicator("hrv", BASE7 + [10.8, 10.8], 7)
    assert f is not None and f.level == "orange"


def test_single_day_above_warn_is_not_enough():
    assert eng.evaluate_indicator("hrv", BASE7 + [10.0, 10.8], 7) is None


def test_rouge_on_single_extreme_day():
    f = eng.evaluate_indicator("hrv", BASE7 + [12.0], 7)
    assert f is not None and f.level == "rouge"


def test_rouge_on_persistence_over_four_days():
    f = eng.evaluate_indicator("hrv", BASE7 + [10.7] * 4, 7)
    assert f is not None and f.level == "rouge"


def test_explanation_and_recommendation_are_labelled():
    f = eng.evaluate_indicator("sleep_hours", BASE7 + [8.9, 8.9], 7)
    assert "Règle de démonstration" in f.explanation and "Sommeil" in f.explanation
    assert "ne remplace pas un avis médical" in f.recommendation


def test_global_status():
    assert eng.global_status([], calibrated=False) == "calibration"
    assert eng.global_status([], calibrated=True) == "vert"


def test_forecast_follows_a_straight_line():
    f = eng.forecast([1, 2, 3, 4, 5, 6, 7], horizon=3)
    assert [round(x["value"], 6) for x in f] == [8.0, 9.0, 10.0]
    assert all(x["low"] <= x["value"] <= x["high"] for x in f)


def test_forecast_needs_four_points():
    assert eng.forecast([1, 2, 3]) is None
