import { useState } from "react";
import LanguageSelect from "./components/LanguageSelect";
import ExposureIntake from "./components/ExposureIntake";
import CoughRecorder from "./components/CoughRecorder";
import ResultScreen from "./components/ResultScreen";
import Dashboard from "./components/Dashboard";
import { attachAudio, createSubmission, getOrCreateDeviceToken } from "./api";
import { t } from "./locales/strings";

// Simple path-based split: NGO/welfare-board staff visit /dashboard, workers visit "/".
// A production deployment would put these behind separate auth (worker flow needs none;
// the dashboard should sit behind at minimum a shared org login) — see
// docs/architecture.md for why these two surfaces are intentionally kept on one codebase
// but logically separate.

// In a real deployment, the site code would come from a QR code printed at the site,
// or a URL param the welfare board distributes per camp/location — not hardcoded.
// Kept simple here since site-routing logistics are an operational decision (PRD §6 Phase 1),
// not a frontend architecture one.
const SITE_CODE = new URLSearchParams(window.location.search).get("site") || "JDH-KaliBeri-01";

const SYMPTOM_LABELS = {
  cough: "long_lasting_cough",
  breath: "shortness_of_breath",
  chest_pain: "chest_pain",
  weight_loss: "weight_loss",
};

export default function App() {
  const isDashboard = window.location.pathname.startsWith("/dashboard");

  const [step, setStep] = useState("language"); // language | intake | record | submitting | result | error
  const [lang, setLang] = useState("hi");
  const [exposureData, setExposureData] = useState(null);
  const [submissionId, setSubmissionId] = useState(null);
  const [result, setResult] = useState(null);
  const [errorMsg, setErrorMsg] = useState(null);

  const handleLanguageSelect = (code) => {
    setLang(code);
    setStep("intake");
  };

  const handleIntakeComplete = async (data) => {
    setExposureData(data);
    try {
      const resp = await createSubmission({
        deviceToken: getOrCreateDeviceToken(),
        siteCode: SITE_CODE,
        yearsOfExposure: data.years,
        maskUsageFrequency: data.mask,
        dustSuppressionAtSite: data.dust,
        symptoms: data.symptoms.map((s) => SYMPTOM_LABELS[s] || s),
        language: lang,
      });
      setSubmissionId(resp.submission_id);
      setStep("record");
    } catch (err) {
      setErrorMsg(err.message);
      setStep("error");
    }
  };

  const handleAudioRecorded = async (blob) => {
    setStep("submitting");
    try {
      const resp = await attachAudio(submissionId, blob);
      setResult(resp);
      setStep("result");
    } catch (err) {
      setErrorMsg(err.message);
      setStep("error");
    }
  };

  const handleSkipRecording = () => {
    // Worker declined to record audio — they already have a valid exposure-only result
    // from the createSubmission call (NO_AUDIO_SUBMITTED tier). Fetch nothing further;
    // just show the message we'd have shown from that first response. For simplicity in
    // this flow we re-derive it client-side; a production build might cache the first
    // response instead of re-deriving it.
    setResult({
      risk_tier: "no_audio_submitted",
      message:
        lang === "en"
          ? "Your information has been recorded. You'll be notified when it's time for your next check."
          : "आपकी जानकारी दर्ज हो गई है। अगली जांच का समय आने पर सूचना मिलेगी।",
      proxy_disclaimer: null,
    });
    setStep("result");
  };

  const handleRestart = () => {
    setStep("language");
    setExposureData(null);
    setSubmissionId(null);
    setResult(null);
    setErrorMsg(null);
  };

  if (isDashboard) {
    return <Dashboard />;
  }

  if (step === "language") {
    return <LanguageSelect onSelect={handleLanguageSelect} />;
  }
  if (step === "intake") {
    return <ExposureIntake lang={lang} onComplete={handleIntakeComplete} />;
  }
  if (step === "record") {
    return (
      <CoughRecorder
        lang={lang}
        onComplete={handleAudioRecorded}
        onSkip={handleSkipRecording}
      />
    );
  }
  if (step === "submitting") {
    return (
      <div className="screen centered-screen">
        <p>{t(lang, "submitting")}</p>
      </div>
    );
  }
  if (step === "result") {
    return <ResultScreen lang={lang} result={result} onRestart={handleRestart} />;
  }
  if (step === "error") {
    return (
      <div className="screen centered-screen">
        <p style={{ color: "var(--terracotta-dark)" }}>{errorMsg}</p>
        <button className="primary-btn" onClick={handleRestart} style={{ marginTop: 20 }}>
          {t(lang, "backHome")}
        </button>
      </div>
    );
  }
  return null;
}
