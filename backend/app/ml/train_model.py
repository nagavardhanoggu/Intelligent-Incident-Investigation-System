import argparse

from app.ml.incident_pipeline import run_pipeline


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", required=True, help="Path to the Kaggle incident CSV")
    parser.add_argument("--artifact-dir", default="app/ml/artifacts", help="Directory where model artifacts are saved")
    args = parser.parse_args()
    run_pipeline(args.dataset, args.artifact_dir)
