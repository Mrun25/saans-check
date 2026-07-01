import { useRef, useState } from "react";
import { t } from "../locales/strings";

const MAX_RECORD_MS = 30000;

export default function CoughRecorder({ lang, onComplete, onSkip }) {
  const [phase, setPhase] = useState("idle"); // idle | recording | done
  const [seconds, setSeconds] = useState(0);
  const [error, setError] = useState(null);
  const mediaRecorderRef = useRef(null);
  const chunksRef = useRef([]);
  const timerRef = useRef(null);
  const streamRef = useRef(null);

  const startRecording = async () => {
    setError(null);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;
      const mimeType = MediaRecorder.isTypeSupported("audio/webm")
        ? "audio/webm"
        : "audio/mp4";
      const recorder = new MediaRecorder(stream, { mimeType });
      chunksRef.current = [];

      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data);
      };
      recorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: mimeType });
        streamRef.current?.getTracks().forEach((tr) => tr.stop());
        setPhase("done");
        onComplete(blob);
      };

      mediaRecorderRef.current = recorder;
      recorder.start();
      setPhase("recording");
      setSeconds(0);

      timerRef.current = setInterval(() => {
        setSeconds((s) => {
          if (s + 1 >= MAX_RECORD_MS / 1000) {
            stopRecording();
          }
          return s + 1;
        });
      }, 1000);
    } catch (err) {
      setError(err.message || "Microphone access denied");
    }
  };

  const stopRecording = () => {
    clearInterval(timerRef.current);
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== "inactive") {
      mediaRecorderRef.current.stop();
    }
  };

  return (
    <div className="screen record-screen">
      <h2 className="record-title">{t(lang, "recordTitle")}</h2>
      <p className="record-instructions">{t(lang, "recordInstructions")}</p>

      <div className="record-stage">
        <button
          className={`cough-btn ${phase === "recording" ? "recording" : ""}`}
          onClick={phase === "recording" ? stopRecording : startRecording}
          disabled={phase === "done"}
        >
          <LungIcon pulsing={phase === "recording"} />
          <span className="cough-btn-label">
            {phase === "recording" ? t(lang, "recordButtonStop") : t(lang, "recordButton")}
          </span>
        </button>

        {phase === "recording" && (
          <p className="recording-indicator">
            <span className="rec-dot" /> {t(lang, "recording")} · {seconds}s
          </p>
        )}

        {error && <p className="record-error">{error}</p>}
      </div>

      <button className="skip-link" onClick={onSkip}>
        {t(lang, "skipRecording")}
      </button>

      <style>{`
        .record-screen {
          display: flex;
          flex-direction: column;
          align-items: center;
          min-height: 100vh;
          padding: 40px 24px 32px;
          background: var(--sandstone-50);
          text-align: center;
        }
        .record-title {
          font-size: 1.7rem;
          font-weight: 700;
          color: var(--sandstone-800);
          margin: 0 0 8px;
        }
        .record-instructions {
          font-size: 1.05rem;
          color: var(--sandstone-600);
          margin: 0 0 40px;
        }
        .record-stage {
          flex: 1;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          gap: 20px;
        }
        .cough-btn {
          width: 220px;
          height: 220px;
          border-radius: 50%;
          background: var(--terracotta);
          border: none;
          box-shadow: 0 12px 32px rgba(179, 80, 47, 0.35);
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          gap: 10px;
          transition: transform 0.15s ease, background 0.15s ease;
        }
        .cough-btn:active { transform: scale(0.96); }
        .cough-btn.recording {
          background: var(--signal-teal);
          box-shadow: 0 12px 32px rgba(44, 122, 114, 0.4);
          animation: pulse-ring 1.4s ease-out infinite;
        }
        .cough-btn:disabled { opacity: 0.5; }
        .cough-btn-label {
          color: var(--paper);
          font-size: 1.25rem;
          font-weight: 700;
        }
        @keyframes pulse-ring {
          0% { box-shadow: 0 12px 32px rgba(44, 122, 114, 0.4), 0 0 0 0 rgba(44, 122, 114, 0.5); }
          70% { box-shadow: 0 12px 32px rgba(44, 122, 114, 0.4), 0 0 0 20px rgba(44, 122, 114, 0); }
          100% { box-shadow: 0 12px 32px rgba(44, 122, 114, 0.4), 0 0 0 0 rgba(44, 122, 114, 0); }
        }
        .recording-indicator {
          font-family: var(--font-mono);
          color: var(--signal-teal-dark);
          font-size: 1rem;
          display: flex;
          align-items: center;
          gap: 8px;
        }
        .rec-dot {
          width: 10px;
          height: 10px;
          border-radius: 50%;
          background: var(--terracotta);
          animation: blink 1s infinite;
        }
        @keyframes blink { 50% { opacity: 0.2; } }
        .record-error {
          color: var(--terracotta-dark);
          font-size: 0.95rem;
          max-width: 280px;
        }
        .skip-link {
          background: none;
          border: none;
          color: var(--sandstone-600);
          font-size: 1rem;
          text-decoration: underline;
          padding: 12px;
        }
      `}</style>
    </div>
  );
}

function LungIcon({ pulsing }) {
  return (
    <svg
      viewBox="0 0 120 100"
      width="64"
      height="54"
      style={{ opacity: pulsing ? 1 : 0.95 }}
      aria-hidden="true"
    >
      <path
        d="M55 8 C 50 8 46 14 46 22 L46 40 C 38 36 28 38 22 46 C 14 56 12 72 16 84 C 19 92 26 94 31 88 L 40 74 C 42 70 46 70 46 76 L46 90 C46 94 50 96 55 96 C 60 96 64 94 64 90 L64 76 C64 70 68 70 70 74 L79 88 C84 94 91 92 94 84 C98 72 96 56 88 46 C82 38 72 36 64 40 L64 22 C64 14 60 8 55 8 Z"
        fill="var(--paper)"
      />
    </svg>
  );
}
