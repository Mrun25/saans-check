import { t } from "../locales/strings";

export default function ResultScreen({ lang, result, onRestart }) {
  const isElevated = result.risk_tier === "elevated_proxy";
  const isNormal = result.risk_tier === "normal_proxy";

  return (
    <div className="screen result-screen">
      <div className={`result-badge ${isElevated ? "elevated" : isNormal ? "normal" : "neutral"}`}>
        <BadgeIcon tier={result.risk_tier} />
      </div>

      <h2 className="result-title">{t(lang, "resultTitle")}</h2>
      <p className="result-message">{result.message}</p>

      {result.proxy_disclaimer && (
        <div className="disclaimer-box">
          <strong>{t(lang, "proxyDisclaimerLabel")}</strong> {result.proxy_disclaimer}
        </div>
      )}

      <button className="primary-btn" onClick={onRestart}>
        {t(lang, "backHome")}
      </button>

      <style>{`
        .result-screen {
          display: flex;
          flex-direction: column;
          align-items: center;
          min-height: 100vh;
          padding: 48px 24px 32px;
          background: var(--sandstone-50);
          text-align: center;
        }
        .result-badge {
          width: 96px;
          height: 96px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          margin-bottom: 24px;
        }
        .result-badge.normal { background: var(--signal-teal-bg); }
        .result-badge.elevated { background: var(--sandstone-200); }
        .result-badge.neutral { background: var(--sandstone-100); }
        .result-title {
          font-size: 1.6rem;
          font-weight: 700;
          color: var(--sandstone-800);
          margin: 0 0 16px;
        }
        .result-message {
          font-size: 1.15rem;
          color: var(--ink);
          line-height: 1.6;
          max-width: 380px;
          white-space: pre-line;
        }
        .disclaimer-box {
          margin-top: 24px;
          background: var(--paper);
          border: 1.5px dashed var(--sandstone-400);
          border-radius: var(--radius-md);
          padding: 14px 16px;
          font-size: 0.95rem;
          color: var(--sandstone-800);
          max-width: 380px;
          line-height: 1.5;
        }
        .primary-btn {
          margin-top: auto;
          width: 100%;
          max-width: 320px;
          background: var(--terracotta);
          color: var(--paper);
          border: none;
          border-radius: var(--radius-md);
          padding: 18px;
          font-size: 1.15rem;
          font-weight: 700;
          box-shadow: var(--shadow-soft);
        }
      `}</style>
    </div>
  );
}

function BadgeIcon({ tier }) {
  if (tier === "elevated_proxy") {
    return (
      <svg viewBox="0 0 24 24" width="44" height="44" fill="none">
        <circle cx="12" cy="12" r="10" stroke="var(--terracotta)" strokeWidth="2" />
        <path d="M12 7v6" stroke="var(--terracotta)" strokeWidth="2.5" strokeLinecap="round" />
        <circle cx="12" cy="16.5" r="1.2" fill="var(--terracotta)" />
      </svg>
    );
  }
  return (
    <svg viewBox="0 0 24 24" width="44" height="44" fill="none">
      <circle cx="12" cy="12" r="10" stroke="var(--signal-teal)" strokeWidth="2" />
      <path
        d="M8 12.5l2.5 2.5L16 9.5"
        stroke="var(--signal-teal)"
        strokeWidth="2.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}
