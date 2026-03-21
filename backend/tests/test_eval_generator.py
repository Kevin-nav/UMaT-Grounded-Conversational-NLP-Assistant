from app.ml.eval_generator import evaluate_generator_outputs


def test_evaluate_generator_outputs_scores_factuality_and_sections() -> None:
    predictions = [
        {
            "prediction": "Evans Obu is based at Essikado Campus. Follow the SRID office signs.",
            "reference": "Evans Obu is based at Essikado Campus. Follow the SRID office signs.",
            "fact_pack": {
                "display_name": "Evans Obu",
                "facts": {"campus": "Essikado Campus"},
                "directions_text": "Follow the SRID office signs.",
            },
        }
    ]

    summary = evaluate_generator_outputs(predictions)

    assert "generation" in summary
    assert "factuality_score" in summary["generation"]
    assert "field_coverage" in summary["generation"]
