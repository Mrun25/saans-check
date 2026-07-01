"""
Dataset loaders for the public proxy datasets (PRD §4.2.D Stage 1).

Each loader returns a list of (filepath, label, metadata_dict) tuples where label is
0 (healthy/negative) or 1 (positive/symptomatic) — a binary "respiratory-distress-pattern"
label, deliberately collapsed from each dataset's richer label set, since the Stage-1 proxy
classifier is binary by design (PRD §4.2.D: "small and simple by design").

IMPORTANT: these labels are COVID/TB-positive vs. negative, not silicosis labels. See
data/README.md and the disclaimers threaded through app/result_copy.py — nothing downstream
of this loader is allowed to call the resulting classifier a silicosis detector.
"""

from dataclasses import dataclass
import csv
import logging
import os

logger = logging.getLogger("phase2.datasets")


@dataclass
class AudioSample:
    filepath: str
    label: int  # 0 = healthy/negative, 1 = positive/symptomatic
    source_dataset: str
    subject_id: str
    raw_label: str  # original label string, kept for auditability


def load_coswara(root_dir: str, sound_category: str = "cough-heavy") -> list[AudioSample]:
    """
    Coswara's actual structure (per github.com/iiscleap/Coswara-Data): after running the
    repo's own extract_data.py, you get Extracted_data/<subject_id>/ folders each containing
    a metadata.csv (with a `covid_status` field) and per-category .wav files such as
    cough-heavy.wav, cough-shallow.wav, breathing-deep.wav, etc.

    covid_status values in the real dataset include things like "healthy", "positive_mild",
    "positive_moderate", "positive_asymp", "recovered_full", "no_resp_illness_exposed", etc.
    We collapse anything starting with "positive" to label=1, everything else to label=0.
    Adjust COSWARA_POSITIVE_PREFIXES below if Coswara's metadata schema has changed since this
    was written — check Extracted_data/<any_subject>/metadata.csv directly before training.
    """
    extracted_dir = os.path.join(root_dir, "Extracted_data")
    if not os.path.isdir(extracted_dir):
        raise FileNotFoundError(
            f"{extracted_dir} not found. Did you run Coswara-Data's extract_data.py? "
            f"See data/README.md."
        )

    COSWARA_POSITIVE_PREFIXES = ("positive",)

    samples: list[AudioSample] = []
    for subject_id in sorted(os.listdir(extracted_dir)):
        subject_dir = os.path.join(extracted_dir, subject_id)
        metadata_path = os.path.join(subject_dir, "metadata.csv")
        audio_path = os.path.join(subject_dir, f"{sound_category}.wav")

        if not (os.path.isfile(metadata_path) and os.path.isfile(audio_path)):
            continue

        with open(metadata_path, newline="") as f:
            reader = csv.DictReader(f)
            row = next(reader, None)
            if row is None or "covid_status" not in row:
                continue
            status = row["covid_status"].strip().lower()

        label = 1 if status.startswith(COSWARA_POSITIVE_PREFIXES) else 0
        samples.append(
            AudioSample(
                filepath=audio_path,
                label=label,
                source_dataset="coswara",
                subject_id=subject_id,
                raw_label=status,
            )
        )

    logger.info("Loaded %d Coswara samples from %s", len(samples), root_dir)
    return samples


def load_virufy(root_dir: str) -> list[AudioSample]:
    """
    Virufy's public clinical dataset (github.com/virufy/virufy-data) ships with a metadata CSV
    mapping each cough clip filename to a PCR test result. Exact column names have shifted
    across Virufy's repo revisions historically — this loader checks for either
    `pcr_test_result` or `covid19_label`-style columns and fails loudly (rather than silently
    mislabeling) if neither is found, so a future dataset-format change surfaces as a clear
    error instead of corrupting training labels silently.
    """
    metadata_candidates = [
        os.path.join(root_dir, "patient_metadata.csv"),
        os.path.join(root_dir, "metadata.csv"),
    ]
    metadata_path = next((p for p in metadata_candidates if os.path.isfile(p)), None)
    if metadata_path is None:
        raise FileNotFoundError(
            f"No metadata CSV found in {root_dir} (checked {metadata_candidates}). "
            f"Check the current structure of github.com/virufy/virufy-data — it may have "
            f"changed since this loader was written."
        )

    label_columns = ["pcr_test_result", "covid19_label", "test_result", "label"]
    audio_dir_candidates = [os.path.join(root_dir, "audio"), os.path.join(root_dir, "segmented")]
    audio_dir = next((d for d in audio_dir_candidates if os.path.isdir(d)), root_dir)

    samples: list[AudioSample] = []
    with open(metadata_path, newline="") as f:
        reader = csv.DictReader(f)
        label_col = next((c for c in label_columns if c in (reader.fieldnames or [])), None)
        if label_col is None:
            raise ValueError(
                f"None of {label_columns} found in {metadata_path} columns "
                f"({reader.fieldnames}). Update label_columns in load_virufy() after checking "
                f"the current CSV schema."
            )
        filename_col = next(
            (c for c in ["filename", "file_name", "audio_path", "patient_id"] if c in reader.fieldnames),
            None,
        )
        if filename_col is None:
            raise ValueError(f"No filename column found in {metadata_path} ({reader.fieldnames})")

        for row in reader:
            raw_label = str(row[label_col]).strip().lower()
            label = 1 if raw_label in ("positive", "1", "true", "yes") else 0
            fname = row[filename_col]
            if not fname.endswith((".wav", ".mp3", ".webm")):
                fname = f"{fname}.wav"
            filepath = os.path.join(audio_dir, fname)
            if not os.path.isfile(filepath):
                logger.warning("Virufy metadata references missing file: %s", filepath)
                continue
            samples.append(
                AudioSample(
                    filepath=filepath,
                    label=label,
                    source_dataset="virufy",
                    subject_id=row.get("patient_id", fname),
                    raw_label=raw_label,
                )
            )

    logger.info("Loaded %d Virufy samples from %s", len(samples), root_dir)
    return samples
