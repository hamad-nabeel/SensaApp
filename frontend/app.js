const API_BASE_URL = window.location.origin;

const state = {
  token: localStorage.getItem("sensa_token"),
  user: null,
  universities: [],
  currentUniversity: null,
  currentLocations: [],
};

const views = {
  login: document.querySelector("#loginView"),
  register: document.querySelector("#registerView"),
  universities: document.querySelector("#universitiesView"),
  locations: document.querySelector("#locationsView"),
  ambassador: document.querySelector("#ambassadorView"),
};

const elements = {
  authButton: document.querySelector("#authButton"),
  ambassadorButton: document.querySelector("#ambassadorButton"),
  universitiesButton: document.querySelector("#universitiesButton"),
  homeButton: document.querySelector("#homeButton"),
  loginForm: document.querySelector("#loginForm"),
  loginStatus: document.querySelector("#loginStatus"),
  openRegisterButton: document.querySelector("#openRegisterButton"),
  registerForm: document.querySelector("#registerForm"),
  registerStatus: document.querySelector("#registerStatus"),
  registerUniversitySelect: document.querySelector("#registerUniversitySelect"),
  backToLoginButton: document.querySelector("#backToLoginButton"),
  universitiesList: document.querySelector("#universitiesList"),
  campusSearchInput: document.querySelector("#campusSearchInput"),
  universitiesStatus: document.querySelector("#universitiesStatus"),
  refreshUniversitiesButton: document.querySelector("#refreshUniversitiesButton"),
  selectedUniversityLabel: document.querySelector("#selectedUniversityLabel"),
  locationsTitle: document.querySelector("#locationsTitle"),
  locationsList: document.querySelector("#locationsList"),
  locationsStatus: document.querySelector("#locationsStatus"),
  backToUniversitiesButton: document.querySelector("#backToUniversitiesButton"),
  reportForm: document.querySelector("#reportForm"),
  reportLocationSelect: document.querySelector("#reportLocationSelect"),
  reportStatus: document.querySelector("#reportStatus"),
  requestsList: document.querySelector("#requestsList"),
  requestsStatus: document.querySelector("#requestsStatus"),
  refreshRequestsButton: document.querySelector("#refreshRequestsButton"),
};

function showView(name) {
  Object.values(views).forEach((view) => view.classList.add("hidden"));
  views[name].classList.remove("hidden");
}

function setStatus(element, message = "", type = "") {
  element.textContent = message;
  element.classList.toggle("error", type === "error");
  element.classList.toggle("success", type === "success");
}

function authHeaders() {
  return state.token ? { Authorization: `Bearer ${state.token}` } : {};
}

function decodeToken(token) {
  try {
    const payload = token.split(".")[1];
    const json = atob(payload.replace(/-/g, "+").replace(/_/g, "/"));
    return JSON.parse(json);
  } catch {
    return null;
  }
}

async function apiFetch(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      ...(options.headers || {}),
    },
  });

  let data = null;
  const contentType = response.headers.get("content-type") || "";
  if (contentType.includes("application/json")) {
    data = await response.json();
  }

  if (!response.ok) {
    const detail = data?.detail || "Request failed";
    throw new Error(Array.isArray(detail) ? detail[0]?.msg || "Request failed" : detail);
  }

  return data;
}

async function login(email, password) {
  const form = new URLSearchParams();
  form.set("username", email);
  form.set("password", password);

  const data = await apiFetch("/auth/token", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: form,
  });

  state.token = data.access_token;
  state.user = decodeToken(state.token);
  localStorage.setItem("sensa_token", state.token);
  syncAuthUi();
}

async function registerViewer(form) {
  const payload = {
    first_name: form.first_name.value.trim(),
    last_name: form.last_name.value.trim(),
    email: form.email.value.trim(),
    password: form.password.value,
    uni_id: Number(form.uni_id.value),
  };

  await apiFetch("/auth/new_account", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  await login(payload.email, payload.password);
}

function logout() {
  state.token = null;
  state.user = null;
  localStorage.removeItem("sensa_token");
  syncAuthUi();
  showView("login");
}

function syncAuthUi() {
  state.user = state.token ? decodeToken(state.token) : null;
  const canUseAmbassador = ["ambassador", "admin"].includes(state.user?.role);
  elements.authButton.textContent = state.token ? "Logout" : "Login";
  elements.ambassadorButton.classList.toggle("hidden", !canUseAmbassador);
}

async function loadUniversities() {
  setStatus(elements.universitiesStatus, "Loading universities...");
  elements.universitiesList.innerHTML = "";
  try {
    state.universities = await apiFetch("/users/universities");
    renderUniversities();
    renderRegistrationUniversities();
    setStatus(elements.universitiesStatus, state.universities.length ? "" : "No universities found.");
  } catch (error) {
    setStatus(elements.universitiesStatus, error.message, "error");
  }
}

function renderRegistrationUniversities() {
  elements.registerUniversitySelect.innerHTML = "";
  state.universities.forEach((university) => {
    const option = document.createElement("option");
    option.value = university.id;
    option.textContent = university.name;
    elements.registerUniversitySelect.append(option);
  });
}

function renderUniversities() {
  elements.universitiesList.innerHTML = "";
  const query = elements.campusSearchInput.value.trim().toLowerCase();
  const universities = query
    ? state.universities.filter((university) => university.name.toLowerCase().includes(query))
    : state.universities;

  universities.forEach((university, index) => {
    const button = document.createElement("button");
    button.className = "item-button";
    button.type = "button";
    button.innerHTML = `
      <span class="campus-copy">
        <span>${index % 2 ? "Study spaces" : "Campus comfort"}</span>
        <strong>${escapeHtml(university.name)}</strong>
      </span>
      <span class="chevron">›</span>
    `;
    button.addEventListener("click", () => openUniversity(university));
    elements.universitiesList.append(button);
  });

  if (!universities.length && state.universities.length) {
    setStatus(elements.universitiesStatus, "No campuses match that search.");
  } else {
    setStatus(elements.universitiesStatus, state.universities.length ? "" : "No universities found.");
  }
}

async function openUniversity(university) {
  state.currentUniversity = university;
  elements.selectedUniversityLabel.textContent = university.name;
  elements.locationsTitle.textContent = "Locations";
  elements.locationsList.innerHTML = "";
  setStatus(elements.locationsStatus, "Loading locations...");
  showView("locations");

  try {
    const locations = await apiFetch(`/users/universities/${university.id}`);
    state.currentLocations = locations;
    await renderLocations(locations, university.id);
    setStatus(elements.locationsStatus, locations.length ? "" : "No locations found.");
  } catch (error) {
    setStatus(elements.locationsStatus, error.message, "error");
  }
}

async function renderLocations(locations, universityId) {
  elements.locationsList.innerHTML = "";

  await Promise.all(
    locations.map(async (location) => {
      let report = null;
      try {
        report = await apiFetch(`/users/get_location_report?university_id=${universityId}&location_id=${location.id}`);
      } catch {
        report = null;
      }
      elements.locationsList.append(createLocationCard(location, report));
    }),
  );
}

function createLocationCard(location, report) {
  const card = document.createElement("article");
  card.className = "location-card";

  const score = Number(report?.overall_score);
  const scoreText = Number.isFinite(score) ? score.toFixed(1) : "--";
  const details = report
    ? ["noise", "crowdedness", "lighting", "temperature"]
        .map((key) => scoreRow(labelFor(key), report[`${key}_score`]))
        .join("")
    : `<p class="note-box">No report yet.</p>`;

  card.innerHTML = `
    <button class="location-summary" type="button" aria-expanded="false">
      <span class="location-title">${escapeHtml(location.name)}</span>
      <span class="score-ring ${report ? "" : "score-muted"}">${scoreText}</span>
    </button>
    <div class="location-details">
      <div class="location-details-inner">
        ${details}
        ${report?.additional_notes ? `<p class="note-box">${escapeHtml(report.additional_notes)}</p>` : ""}
        <button class="secondary-button request-update-button" type="button">Request update</button>
      </div>
    </div>
  `;

  const summary = card.querySelector(".location-summary");
  const detailsPanel = card.querySelector(".location-details");
  summary.addEventListener("click", () => {
    toggleLocationCard(card, summary, detailsPanel);
  });
  detailsPanel.addEventListener("transitionend", resetLocationDetailsHeight);

  card.querySelector(".request-update-button").addEventListener("click", () => requestUpdate(location.id));

  return card;
}

function toggleLocationCard(card, summary, detailsPanel) {
  const isExpanded = card.classList.contains("expanded");

  if (isExpanded) {
    detailsPanel.style.height = `${detailsPanel.scrollHeight}px`;
    void detailsPanel.offsetHeight;
    card.classList.remove("expanded");
    summary.setAttribute("aria-expanded", "false");
    detailsPanel.style.height = "0px";
    return;
  }

  card.classList.add("expanded");
  summary.setAttribute("aria-expanded", "true");
  detailsPanel.style.height = "0px";
  void detailsPanel.offsetHeight;
  detailsPanel.style.height = `${detailsPanel.scrollHeight}px`;
}

function resetLocationDetailsHeight(event) {
  if (event.propertyName !== "height") return;

  const detailsPanel = event.currentTarget;
  if (detailsPanel.closest(".location-card")?.classList.contains("expanded")) {
    detailsPanel.style.height = "auto";
  }
}

function scoreRow(label, value) {
  const numeric = Number(value) || 0;
  const percent = Math.max(0, Math.min(100, (numeric / 5) * 100));
  return `
    <div class="score-row">
      <span>${label}</span>
      <span class="score-bar"><span style="width: ${percent}%"></span></span>
      <strong>${numeric || "--"}</strong>
    </div>
  `;
}

function labelFor(key) {
  return key.charAt(0).toUpperCase() + key.slice(1);
}

async function requestUpdate(locationId) {
  if (!state.token) {
    showView("login");
    setStatus(elements.loginStatus, "Login or create a viewing account to request an update.", "error");
    return;
  }

  setStatus(elements.locationsStatus, "Sending update request...");
  try {
    const data = await apiFetch(`/users/request_update?id=${locationId}`, {
      method: "POST",
      headers: authHeaders(),
    });
    setStatus(elements.locationsStatus, data.message, "success");
  } catch (error) {
    setStatus(elements.locationsStatus, error.message, "error");
  }
}

async function openAmbassadorDashboard() {
  if (!["ambassador", "admin"].includes(state.user?.role)) {
    showView("login");
    return;
  }

  showView("ambassador");
  await Promise.all([loadReportLocations(), loadUpdateRequests()]);
}

async function loadReportLocations() {
  elements.reportLocationSelect.innerHTML = "";
  const universityId = state.user?.uni || state.currentUniversity?.id || state.universities[0]?.id;

  if (!universityId) {
    setStatus(elements.reportStatus, "Choose a university first.", "error");
    return;
  }

  try {
    const locations = await apiFetch(`/users/universities/${universityId}`);
    locations.forEach((location) => {
      const option = document.createElement("option");
      option.value = location.id;
      option.textContent = location.name;
      elements.reportLocationSelect.append(option);
    });
    setStatus(elements.reportStatus, locations.length ? "" : "No locations found.");
  } catch (error) {
    setStatus(elements.reportStatus, error.message, "error");
  }
}

async function loadUpdateRequests() {
  setStatus(elements.requestsStatus, "Loading requests...");
  elements.requestsList.innerHTML = "";
  try {
    const requests = await apiFetch("/ambassadors/update_requests", {
      headers: authHeaders(),
    });
    renderRequests(requests);
    setStatus(elements.requestsStatus, requests.length ? "" : "No update requests.");
  } catch (error) {
    setStatus(elements.requestsStatus, error.message, "error");
  }
}

function renderRequests(requests) {
  elements.requestsList.innerHTML = "";
  requests.forEach((request) => {
    const item = document.createElement("div");
    item.className = "request-item";
    const locationName = request.location_name || `Location #${request.location_id}`;
    item.innerHTML = `
      <strong>${escapeHtml(locationName)}</strong>
      <span>${formatDate(request.created_at)}</span>
    `;
    elements.requestsList.append(item);
  });
}

async function submitReport(event) {
  event.preventDefault();
  setStatus(elements.reportStatus, "Submitting report...");

  const payload = {
    location_id: Number(elements.reportLocationSelect.value),
    noise_level: Number(document.querySelector("#noiseInput").value),
    crowdedness_level: Number(document.querySelector("#crowdednessInput").value),
    lighting_level: Number(document.querySelector("#lightingInput").value),
    temperature_level: Number(document.querySelector("#temperatureInput").value),
    note: document.querySelector("#noteInput").value,
  };

  try {
    await apiFetch("/ambassadors/submit_report", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...authHeaders(),
      },
      body: JSON.stringify(payload),
    });
    setStatus(elements.reportStatus, "Report submitted.", "success");
    if (state.currentUniversity) {
      await openUniversity(state.currentUniversity);
    }
  } catch (error) {
    setStatus(elements.reportStatus, error.message, "error");
  }
}

function formatDate(value) {
  if (!value) return "";
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? value : date.toLocaleString();
}

function escapeHtml(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

elements.loginForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  setStatus(elements.loginStatus, "Logging in...");
  try {
    await login(elements.loginForm.email.value, elements.loginForm.password.value);
    setStatus(elements.loginStatus, "");
    await loadUniversities();
    showView("universities");
  } catch (error) {
    setStatus(elements.loginStatus, error.message, "error");
  }
});

elements.registerForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  setStatus(elements.registerStatus, "Creating account...");
  try {
    await registerViewer(elements.registerForm);
    elements.registerForm.reset();
    setStatus(elements.registerStatus, "");
    await loadUniversities();
    showView("universities");
  } catch (error) {
    setStatus(elements.registerStatus, error.message, "error");
  }
});

elements.openRegisterButton.addEventListener("click", async () => {
  setStatus(elements.loginStatus, "");
  if (!state.universities.length) await loadUniversities();
  showView("register");
});

elements.backToLoginButton.addEventListener("click", () => {
  setStatus(elements.registerStatus, "");
  showView("login");
});

elements.authButton.addEventListener("click", () => {
  if (state.token) {
    logout();
  } else {
    showView("login");
  }
});

elements.homeButton.addEventListener("click", async () => {
  showView("universities");
  if (!state.universities.length) await loadUniversities();
});

elements.universitiesButton.addEventListener("click", async () => {
  showView("universities");
  if (!state.universities.length) await loadUniversities();
});

elements.refreshUniversitiesButton.addEventListener("click", loadUniversities);
elements.campusSearchInput.addEventListener("input", renderUniversities);
elements.backToUniversitiesButton.addEventListener("click", () => showView("universities"));
elements.ambassadorButton.addEventListener("click", openAmbassadorDashboard);
elements.refreshRequestsButton.addEventListener("click", loadUpdateRequests);
elements.reportForm.addEventListener("submit", submitReport);

syncAuthUi();
loadUniversities().then(() => showView("universities"));
