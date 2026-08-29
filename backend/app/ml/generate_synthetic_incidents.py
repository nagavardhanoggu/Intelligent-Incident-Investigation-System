from __future__ import annotations

import argparse
import random
from pathlib import Path

import pandas as pd


ROOT_CAUSE_PROFILES = {
    "Deployment Issue": {
        "priority": ["High", "Critical"],
        "impact": ["Medium", "High"],
        "urgency": ["High", "Critical"],
        "category": ["Category 42", "Category 46"],
        "subcategory": ["Subcategory 223", "Subcategory 164"],
        "u_symptom": ["Symptom 471", "Symptom 534"],
        "assignment_group": ["Group 70", "Group 39"],
        "contact_type": ["Email", "Self Service"],
        "knowledge": ["False"],
        "made_sla": [0],
        "reassignment_count": (2, 7),
        "reopen_count": (0, 2),
        "sys_mod_count": (4, 14),
    },
    "Database Issue": {
        "priority": ["High", "Critical"],
        "impact": ["High", "Critical"],
        "urgency": ["High", "Critical"],
        "category": ["Category 26", "Category 53"],
        "subcategory": ["Subcategory 174", "Subcategory 175"],
        "u_symptom": ["Symptom 72", "Symptom 87"],
        "assignment_group": ["Group 56", "Group 24"],
        "contact_type": ["Phone", "Email"],
        "knowledge": ["True"],
        "made_sla": [0],
        "reassignment_count": (3, 9),
        "reopen_count": (1, 4),
        "sys_mod_count": (5, 18),
    },
    "Network Issue": {
        "priority": ["Medium", "High"],
        "impact": ["Medium", "High"],
        "urgency": ["Medium", "High"],
        "category": ["Category 23", "Category 37"],
        "subcategory": ["Subcategory 9", "Subcategory 75"],
        "u_symptom": ["Symptom 4", "Symptom 122"],
        "assignment_group": ["Group 25", "Group 18"],
        "contact_type": ["Phone", "Direct Opening"],
        "knowledge": ["False"],
        "made_sla": [0, 1],
        "reassignment_count": (4, 10),
        "reopen_count": (0, 2),
        "sys_mod_count": (3, 12),
    },
    "Memory Leak": {
        "priority": ["Medium", "High"],
        "impact": ["High", "Critical"],
        "urgency": ["Medium", "High"],
        "category": ["Category 32", "Category 57"],
        "subcategory": ["Subcategory 135", "Subcategory 303"],
        "u_symptom": ["Symptom 211", "Symptom 401"],
        "assignment_group": ["Group 31", "Group 44"],
        "contact_type": ["Self Service", "Email"],
        "knowledge": ["True", "False"],
        "made_sla": [0],
        "reassignment_count": (1, 5),
        "reopen_count": (2, 6),
        "sys_mod_count": (8, 22),
    },
    "Application Failure": {
        "priority": ["Low", "Medium", "High"],
        "impact": ["Low", "Medium"],
        "urgency": ["Low", "Medium"],
        "category": ["Category 40", "Category 61"],
        "subcategory": ["Subcategory 170", "Subcategory 43"],
        "u_symptom": ["Symptom 15", "Symptom 88"],
        "assignment_group": ["Group 12", "Group 28"],
        "contact_type": ["Phone", "Self Service"],
        "knowledge": ["True"],
        "made_sla": [1],
        "reassignment_count": (0, 3),
        "reopen_count": (0, 1),
        "sys_mod_count": (1, 8),
    },
}


def generate_dataset(
    rows_per_class: int,
    output_path: str | Path,
    seed: int = 42,
    label_noise_rate: float = 0.048,
) -> Path:
    if rows_per_class < 1:
        raise ValueError("rows_per_class must be at least 1")
    if not 0 <= label_noise_rate < 1:
        raise ValueError("label_noise_rate must be between 0 (inclusive) and 1 (exclusive)")

    random.seed(seed)
    rows = []
    incident_number = 100000
    root_causes = list(ROOT_CAUSE_PROFILES)

    for class_index, (root_cause, profile) in enumerate(ROOT_CAUSE_PROFILES.items()):
        class_start = len(rows)
        for _ in range(rows_per_class):
            incident_number += 1
            rows.append(
                {
                    "number": f"SIM-{incident_number}",
                    "priority": random.choice(profile["priority"]),
                    "impact": random.choice(profile["impact"]),
                    "urgency": random.choice(profile["urgency"]),
                    "reassignment_count": random.randint(*profile["reassignment_count"]),
                    "reopen_count": random.randint(*profile["reopen_count"]),
                    "made_sla": random.choice(profile["made_sla"]),
                    "category": random.choice(profile["category"]),
                    "subcategory": random.choice(profile["subcategory"]),
                    "u_symptom": random.choice(profile["u_symptom"]),
                    "assignment_group": random.choice(profile["assignment_group"]),
                    "contact_type": random.choice(profile["contact_type"]),
                    "knowledge": random.choice(profile["knowledge"]),
                    "sys_mod_count": random.randint(*profile["sys_mod_count"]),
                    "root_cause": root_cause,
                }
            )

        # Real incident labels contain occasional ambiguity and investigation error.
        # Rotating the same fraction into the next class adds reproducible noise while
        # keeping the final target distribution exactly balanced.
        noisy_rows = round(rows_per_class * label_noise_rate)
        noisy_label = root_causes[(class_index + 1) % len(root_causes)]
        for row_index in random.sample(range(class_start, len(rows)), noisy_rows):
            rows[row_index]["root_cause"] = noisy_label

    random.shuffle(rows)
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(output, index=False)
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate balanced synthetic root-cause training data.")
    parser.add_argument(
        "--rows-per-class",
        type=int,
        default=40_000,
        help="Number of examples to generate for each root-cause profile (default: 40,000).",
    )
    parser.add_argument("--output", default="data/synthetic_incident_root_cause.csv")
    parser.add_argument("--seed", type=int, default=42, help="Random seed used for reproducible data generation.")
    parser.add_argument(
        "--label-noise-rate",
        type=float,
        default=0.048,
        help="Balanced fraction of intentionally ambiguous labels (default: 0.048).",
    )
    args = parser.parse_args()
    if args.rows_per_class < 1:
        parser.error("--rows-per-class must be at least 1")
    if not 0 <= args.label_noise_rate < 1:
        parser.error("--label-noise-rate must be between 0 (inclusive) and 1 (exclusive)")
    path = generate_dataset(
        args.rows_per_class,
        args.output,
        seed=args.seed,
        label_noise_rate=args.label_noise_rate,
    )
    print(f"Generated synthetic dataset: {path}")
