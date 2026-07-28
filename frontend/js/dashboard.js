// ---- guard: redirect to login if no session ----
if (!api.isLoggedIn()) {
  window.location.href = "login.html";
}

const user = api.getUser();
const isHR = user && ["admin", "hr_manager"].includes(user.role);

// ---- topbar ----
document.getElementById("user-name").textContent = user.email;
document.getElementById("user-role").textContent = user.role;

document.getElementById("logout-btn").addEventListener("click", () => {
  api.clearSession();
  window.location.href = "login.html";
});

// ---- period selector: populate month/year, default to current period ----
const monthSelect = document.getElementById("period-month");
const yearSelect = document.getElementById("period-year");

const MONTH_NAMES = [
  "January",
  "February",
  "March",
  "April",
  "May",
  "June",
  "July",
  "August",
  "September",
  "October",
  "November",
  "December",
];

function populatePeriodSelectors() {
  const now = new Date();

  MONTH_NAMES.forEach((name, idx) => {
    const opt = document.createElement("option");
    opt.value = idx + 1; // 1-12, matches payslips.period_month
    opt.textContent = name;
    if (idx === now.getMonth()) opt.selected = true;
    monthSelect.appendChild(opt);
  });

  const currentYear = now.getFullYear();
  for (let y = currentYear - 1; y <= currentYear + 1; y++) {
    const opt = document.createElement("option");
    opt.value = y;
    opt.textContent = y;
    if (y === currentYear) opt.selected = true;
    yearSelect.appendChild(opt);
  }
}

function getSelectedPeriod() {
  return {
    month: parseInt(monthSelect.value, 10),
    year: parseInt(yearSelect.value, 10),
  };
}

// ---- role-based visibility ----
function applyRoleVisibility() {
  document.getElementById("section-pending-approvals").hidden = !isHR;
  document.getElementById("generate-payroll-btn").hidden = !isHR;
  document.getElementById("request-leave-btn").hidden = isHR;

  document.getElementById("leave-balances-title").textContent = isHR
    ? "Leave balances — all employees"
    : "My leave balance";

  document.getElementById("payslips-title").textContent = isHR
    ? "Payslips for this period — all employees"
    : "My payslips";
}

// ---- re-fetch data when period changes (wired up in later steps) ----
function onPeriodChange() {
  const period = getSelectedPeriod();
  console.log("Period changed to:", period);
  // loadWhosOut(period), loadPayslips(period) etc. get called here in Step 6
}

monthSelect.addEventListener("change", onPeriodChange);
yearSelect.addEventListener("change", onPeriodChange);

// ---- init ----
populatePeriodSelectors();
applyRoleVisibility();
