import json
from pathlib import Path


def test_colab_notebook_manifest_exists_and_has_required_sections() -> None:
    notebook_path = Path("backend/notebooks/grounded_conversational_nlp_colab.ipynb")
    assert notebook_path.exists()

    payload = json.loads(notebook_path.read_text(encoding="utf-8"))
    source_text = "\n".join(
        "".join(cell.get("source", []))
        for cell in payload.get("cells", [])
    )

    assert "drive.mount" in source_text
    assert "umat_nlp_project" in source_text
    assert "generate_synthetic_dialogues" in source_text
    assert "run_retriever_training" in source_text
    assert "run_generator_training" in source_text
    assert "evaluate_generator_outputs" in source_text
