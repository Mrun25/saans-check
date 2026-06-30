import { languageOptions } from "../locales/strings";

export default function LanguageSelect({ onSelect }) {
  return (
    <div className="screen language-screen">
      <div className="lung-mark" aria-hidden="true">
        <svg viewBox="0 0 120 100" width="72" height="60">
          <path
            d="M55 8 C 50 8 46 14 46 22 L46 40 C 38 36 28 38 22 46 C 14 56 12 72 16 84 C 19 92 26 94 31 88 L 40 74 C 42 70 46 70 46 76 L46 90 C46 94 50 96 55 96 C 60 96 64 94 64 90 L64 76 C64 70 68 70 70 74 L79 88 C84 94 91 92 94 84 C98 72 96 56 88 46 C82 38 72 36 64 40 L64 22 C64 14 60 8 55 8 Z"
            fill="var(--terracotta)"
          />
        </svg>
      </div>
      <h1 className="brand-title">सांस चेक</h1>
      <p className="brand-sub">Saans Check</p>

      <div className="lang-grid">
        {languageOptions.map((opt) => (
          <button key={opt.code} className="lang-btn" onClick={() => onSelect(opt.code)}>
            {opt.label}
          </button>
        ))}
      </div>

      <style>{`
        .language-screen {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          min-height: 100vh;
          padding: 32px 24px;
          text-align: center;
          background: radial-gradient(circle at 50% 0%, var(--sandstone-100), var(--sandstone-50) 70%);
        }
        .lung-mark { margin-bottom: 8px; }
        .brand-title {
          font-size: 2.4rem;
          font-weight: 700;
          color: var(--sandstone-800);
          margin: 0;
          letter-spacing: -0.01em;
        }
        .brand-sub {
          font-size: 1.1rem;
          color: var(--sandstone-600);
          margin: 2px 0 40px 0;
          font-family: var(--font-mono);
          letter-spacing: 0.04em;
          text-transform: uppercase;
        }
        .lang-grid {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 16px;
          width: 100%;
          max-width: 360px;
        }
        .lang-btn {
          background: var(--paper);
          border: 2px solid var(--sandstone-200);
          border-radius: var(--radius-md);
          padding: 22px 12px;
          font-size: 1.3rem;
          font-weight: 600;
          color: var(--sandstone-800);
          box-shadow: var(--shadow-soft);
          transition: transform 0.12s ease, border-color 0.12s ease;
        }
        .lang-btn:active {
          transform: scale(0.96);
          box-shadow: var(--shadow-press);
        }
        .lang-btn:hover {
          border-color: var(--terracotta);
        }
      `}</style>
    </div>
  );
}
