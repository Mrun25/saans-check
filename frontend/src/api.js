const BASE = "/api";

async function handleResponse(res) {
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`API error ${res.status}: ${text}`);
  }
  return res.json();
}

export function getOrCreateDeviceToken() {
  const key = "saans_check_device_token";
  let token = localStorage.getItem(key);
  if (!token) {
    token = crypto.randomUUID();
    localStorage.setItem(key, token);
  }
  return token;
}

export async function createSubmission({
  deviceToken,
  siteCode,
  yearsOfExposure,
  maskUsageFrequency,
  dustSuppressionAtSite,
  symptoms,
  language,
}) {
  const res = await fetch(`${BASE}/submissions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      device_token: deviceToken,
      site_code: siteCode,
      years_of_exposure: yearsOfExposure,
      mask_usage_frequency: maskUsageFrequency,
      dust_suppression_at_site: dustSuppressionAtSite,
      symptoms,
      language,
    }),
  });
  return handleResponse(res);
}

export async function attachAudio(submissionId, audioBlob) {
  const form = new FormData();
  form.append("audio", audioBlob, "cough.webm");
  const res = await fetch(`${BASE}/submissions/${submissionId}/audio`, {
    method: "POST",
    body: form,
  });
  return handleResponse(res);
}

export async function getHotspots() {
  const res = await fetch(`${BASE}/dashboard/hotspots`);
  return handleResponse(res);
}
