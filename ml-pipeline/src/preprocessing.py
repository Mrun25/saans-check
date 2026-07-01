"""
Preprocessing (PRD §4.2.B): trim silence, isolate cough events, denoise, standardize sample
rate/length to whatever the downstream embedding model expects (16kHz mono for YAMNet).

The PRD is explicit that quarry-environment noise is "a non-trivial real-world engineering
problem, not an afterthought" — this module is the honest version of that, not a stub. It still
won't be perfect on first deployment; field recordings from an actual quarry will surface noise
profiles no public dataset captures (ambient drilling/crushing machinery, wind, voices). Treat
the thresholds below as a starting point to tune against real field recordings once available,
not as finished, validated constants.
"""

from dataclasses import dataclass

import librosa
import numpy as np
from scipy.signal import butter, sosfiltfilt

YAMNET_SAMPLE_RATE = 16000


@dataclass
class CoughEvent:
    start_sample: int
    end_sample: int
    audio: np.ndarray


def load_and_resample(filepath: str, target_sr: int = YAMNET_SAMPLE_RATE) -> np.ndarray:
    """Load an audio file (any common format librosa supports) as mono float32 at target_sr."""
    audio, _ = librosa.load(filepath, sr=target_sr, mono=True)
    return audio.astype(np.float32)


def bandpass_filter(
    audio: np.ndarray, sr: int = YAMNET_SAMPLE_RATE, low_hz: float = 80.0, high_hz: float = 6000.0
) -> np.ndarray:
    """
    Cough acoustic energy is concentrated roughly 50Hz–8kHz; quarry environments add a lot of
    low-frequency machinery rumble and high-frequency wind/dust noise outside that band.
    A simple Butterworth bandpass removes a meaningful chunk of that without needing a learned
    denoiser — cheap, fast, and a reasonable first-pass filter before anything fancier.
    """
    nyquist = sr / 2
    sos = butter(4, [low_hz / nyquist, high_hz / nyquist], btype="band", output="sos")
    return sosfiltfilt(sos, audio).astype(np.float32)


def detect_cough_events(
    audio: np.ndarray,
    sr: int = YAMNET_SAMPLE_RATE,
    energy_threshold_db: float = -35.0,
    min_event_duration_s: float = 0.15,
    max_event_duration_s: float = 1.2,
    merge_gap_s: float = 0.1,
) -> list[CoughEvent]:
    """
    Simple energy-based voice/cough-activity detection: a cough is a short, high-energy burst.
    This is intentionally a classical-DSP approach, not a learned VAD model — it's transparent,
    debuggable, and good enough to isolate cough bursts from quiet/background segments before
    they hit the embedding model. A learned cough-detector (e.g. a small CNN on mel-spectrogram
    frames) is a reasonable Phase 2.5 upgrade if this proves too noisy on real field audio, but
    isn't necessary to get the pipeline working end-to-end now.
    """
    frame_length = int(0.025 * sr)  # 25ms frames
    hop_length = int(0.010 * sr)  # 10ms hop

    rms = librosa.feature.rms(y=audio, frame_length=frame_length, hop_length=hop_length)[0]
    rms_db = librosa.amplitude_to_db(rms, ref=np.max(rms) + 1e-9)

    above_threshold = rms_db > energy_threshold_db

    events: list[CoughEvent] = []
    in_event = False
    event_start_frame = 0
    min_frames = int(min_event_duration_s / 0.010)
    max_frames = int(max_event_duration_s / 0.010)
    merge_gap_frames = int(merge_gap_s / 0.010)

    gap_counter = 0
    for i, is_active in enumerate(above_threshold):
        if is_active:
            if not in_event:
                in_event = True
                event_start_frame = i
            gap_counter = 0
        elif in_event:
            gap_counter += 1
            if gap_counter > merge_gap_frames:
                # event ended
                duration_frames = i - gap_counter - event_start_frame
                if min_frames <= duration_frames <= max_frames:
                    start_sample = event_start_frame * hop_length
                    end_sample = min((i - gap_counter) * hop_length, len(audio))
                    events.append(
                        CoughEvent(start_sample, end_sample, audio[start_sample:end_sample])
                    )
                in_event = False
                gap_counter = 0

    if in_event:
        duration_frames = len(above_threshold) - event_start_frame
        if min_frames <= duration_frames <= max_frames:
            start_sample = event_start_frame * hop_length
            events.append(CoughEvent(start_sample, len(audio), audio[start_sample:]))

    return events


def pad_or_trim(audio: np.ndarray, target_length_samples: int) -> np.ndarray:
    if len(audio) >= target_length_samples:
        return audio[:target_length_samples]
    pad_width = target_length_samples - len(audio)
    return np.pad(audio, (0, pad_width), mode="constant")


def preprocess_clip(
    filepath: str,
    target_sr: int = YAMNET_SAMPLE_RATE,
    apply_bandpass: bool = True,
) -> np.ndarray:
    """
    Full preprocessing pipeline for one audio file: load, resample, optionally bandpass-filter.
    Does NOT trim to individual cough events by default — YAMNet handles variable-length clips
    fine, and trimming to a single best event is a tuning decision left to extract_embeddings.py
    (controlled via --use-cough-events flag) since whether per-event or whole-clip embeddings
    work better is itself an empirical question to check against the held-out validation sets,
    not something to bake in here as a silent default.
    """
    audio = load_and_resample(filepath, target_sr)
    if apply_bandpass:
        audio = bandpass_filter(audio, target_sr)
    # Normalize amplitude to avoid clipping/quiet-recording artifacts dominating the embedding
    peak = np.max(np.abs(audio)) + 1e-9
    audio = audio / peak * 0.95
    return audio
