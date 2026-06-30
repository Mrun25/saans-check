import { useState } from "react";
import { t } from "../locales/strings";

const YEAR_OPTIONS = [0, 1, 2, 5, 10, 15, 20, 30];

export default function ExposureIntake({ lang, onComplete }) {
  const [step, setStep] = useState(0);
  const [years, setYears] = useState(null);
  const [mask, setMask] = useState(null);
  const [dust, setDust] = useState(null);
  const [symptoms, setSymptoms] = useState([]);

  const toggleSymptom = (key) => {
    setSymptoms((prev) =>
      prev.includes(key) ? prev.filter((s) => s !== key) : [...prev, key]
    );
  };

  const steps = [
    {
      title: t(lang, "yearsWorked"),
      content: (
        <div className="option-grid years-grid">
          {YEAR_OPTIONS.map((y) => (
            <button
              key={y}
              className={`option-btn ${years === y ? "selected" : ""}`}
              onClick={() => setYears(y)}
            >
              {y}+ {t(lang, "years")}
            </button>
          ))}
        </div>
      ),
      canAdvance: years !== null,
    },
    {
      title: t(lang, "maskUsage"),
      content: (
        <div className="option-grid">
          {[
            ["never", t(lang, "maskNever")],
            ["sometimes", t(lang, "maskSometimes")],
            ["most_of_time", t(lang, "maskMost")],
            ["always", t(lang, "maskAlways")],
          ].map(([key, label]) => (
            <button
              key={key}
              className={`option-btn ${mask === key ? "selected" : ""}`}
              onClick={() => setMask(key)}
            >
              {label}
            </button>
          ))}
        </div>
      ),
      canAdvance: mask !== null,
    },
    {
      title: t(lang, "dustSuppression"),
      content: (
        <div className="option-grid">
          {[
            ["none", t(lang, "dustNone")],
            ["some", t(lang, "dustSome")],
            ["wet_drilling", t(lang, "dustWet")],
            ["unknown", t(lang, "dustUnknown")],
          ].map(([key, label]) => (
            <button
              key={key}
              className={`option-btn ${dust === key ? "selected" : ""}`}
              onClick={() => setDust(key)}
            >
              {label}
            </button>
          ))}
        </div>
      ),
      canAdvance: dust !== null,
    },
    {
      title: t(lang, "symptomsTitle"),
      content: (
        <div className="option-grid symptom-grid">
          {[
            ["cough", t(lang, "symptomCough")],
            ["breath", t(lang, "symptomBreath")],
            ["chest_pain", t(lang, "symptomChestPain")],
            ["weight_loss", t(lang, "symptomWeightLoss")],
          ].map(([key, label]) => (
            <button
              key={key}
              className={`option-btn checkbox-btn ${symptoms.includes(key) ? "selected" : ""}`}
              onClick={() => toggleSymptom(key)}
            >
              <span className="checkbox-indicator" aria-hidden="true" />
              {label}
            </button>
          ))}
        </div>
      ),
      canAdvance: true,
    },
  ];

  const current = steps[step];
  const isLastStep = step === steps.length - 1;

  const handleNext = () => {
    if (!current.canAdvance) return;
    if (isLastStep) {
      onComplete({ years, mask, dust, symptoms });
    } else {
      setStep((s) => s + 1);
    }
  };

  return (
    <div className="screen intake-screen">
      <div className="progress-dots">
        {steps.map((_, i) => (
          <span key={i} className={`dot ${i <= step ? "active" : ""}`} />
        ))}
      </div>

      <h2 className="intake-title">{current.title}</h2>
      {current.content}

      <button
        className="primary-btn"
        disabled={!current.canAdvance}
        onClick={handleNext}
      >
        {t(lang, "next")}
      </button>

      <style>{`
        .intake-screen {
          display: flex;
          flex-direction: column;
          min-height: 100vh;
          padding: 28px 20px 32px;
          background: var(--sandstone-50);
        }
        .progress-dots {
          display: flex;
          gap: 8px;
          justify-content: center;
          margin-bottom: 28px;
        }
        .dot {
          width: 10px;
          height: 10px;
          border-radius: 50%;
          background: var(--sandstone-200);
        }
        .dot.active { background: var(--terracotta); }
        .intake-title {
          font-size: 1.5rem;
          font-weight: 600;
          color: var(--sandstone-800);
          text-align: center;
          margin: 0 0 28px 0;
          line-height: 1.35;
        }
        .option-grid {
          display: flex;
          flex-direction: column;
          gap: 12px;
          flex: 1;
        }
        .years-grid {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 12px;
        }
        .option-btn {
          background: var(--paper);
          border: 2px solid var(--sandstone-200);
          border-radius: var(--radius-md);
          padding: 18px 16px;
          font-size: 1.15rem;
          font-weight: 600;
          color: var(--sandstone-800);
          text-align: left;
        }
        .years-grid .option-btn { text-align: center; }
        .option-btn.selected {
          border-color: var(--terracotta);
          background: var(--sandstone-100);
          color: var(--terracotta-dark);
        }
        .checkbox-btn {
          display: flex;
          align-items: center;
          gap: 14px;
        }
        .checkbox-indicator {
          width: 24px;
          height: 24px;
          border-radius: 6px;
          border: 2px solid var(--sandstone-400);
          flex-shrink: 0;
          background: var(--paper);
        }
        .checkbox-btn.selected .checkbox-indicator {
          background: var(--terracotta);
          border-color: var(--terracotta);
        }
        .primary-btn {
          margin-top: 28px;
          background: var(--terracotta);
          color: var(--paper);
          border: none;
          border-radius: var(--radius-md);
          padding: 18px;
          font-size: 1.2rem;
          font-weight: 700;
          box-shadow: var(--shadow-soft);
        }
        .primary-btn:disabled {
          background: var(--sandstone-200);
          color: var(--sandstone-600);
          box-shadow: none;
        }
        .primary-btn:active:not(:disabled) {
          transform: scale(0.98);
        }
      `}</style>
    </div>
  );
}
