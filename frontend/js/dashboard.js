// redirect to login if no session
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
  loadWhosOut(period);
  loadPayslips(period);
}

monthSelect.addEventListener("change", onPeriodChange);
yearSelect.addEventListener("change", onPeriodChange);

// ---- Pending approvals (HR only) ----
const pendingBody = document.querySelector(
  "#section-pending-approvals .card-body",
);

function formatDate(dateStr) {
  return new Date(dateStr).toLocaleDateString(undefined, {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

function renderPendingApprovals(requests) {
  if (requests.length === 0) {
    pendingBody.innerHTML = `<p class="state-empty">No leave requests waiting for review.</p>`;
    return;
  }

  pendingBody.innerHTML = "";
  requests.forEach((req) => {
    const row = document.createElement("div");
    row.className = "list-row";
    row.innerHTML = `
      <div class="list-row-main">
        <span class="list-row-title">${req.employee_name || "Unknown employee"}</span>
        <span class="list-row-sub">
          ${req.leave_type_name || "Leave"} · ${formatDate(req.start_date)} – ${formatDate(req.end_date)}
          · ${req.total_days} day${req.total_days === 1 ? "" : "s"}
        </span>
        ${req.reason ? `<span class="list-row-reason">"${req.reason}"</span>` : ""}
      </div>
      <div class="list-row-actions">
        <button class="btn-approve" data-id="${req.id}">Approve</button>
        <button class="btn-reject" data-id="${req.id}">Reject</button>
      </div>
    `;
    pendingBody.appendChild(row);
  });

  pendingBody.querySelectorAll(".btn-approve").forEach((btn) => {
    btn.addEventListener("click", () =>
      handleReview(btn.dataset.id, "approved", btn),
    );
  });
  pendingBody.querySelectorAll(".btn-reject").forEach((btn) => {
    btn.addEventListener("click", () =>
      handleReview(btn.dataset.id, "rejected", btn),
    );
  });
}

async function handleReview(requestId, status, btn) {
  if (status === "rejected" && !confirm("Reject this leave request?")) return;

  const row = btn.closest(".list-row");
  row.querySelectorAll("button").forEach((b) => (b.disabled = true));
  btn.textContent = status === "approved" ? "Approving…" : "Rejecting…";

  try {
    await api.reviewLeaveRequest(requestId, status);
    await loadPendingApprovals(); // refresh the list so the row disappears
  } catch (err) {
    alert(err.message || "Could not update this request. Try again.");
    row.querySelectorAll("button").forEach((b) => (b.disabled = false));
    btn.textContent = status === "approved" ? "Approve" : "Reject";
  }
}

async function loadPendingApprovals() {
  pendingBody.innerHTML = `<p class="state-loading">Loading pending requests…</p>`;
  try {
    const requests = await api.getPendingLeaveRequests();
    renderPendingApprovals(requests);
  } catch (err) {
    pendingBody.innerHTML = `<p class="state-error">Couldn't load pending requests. ${err.message || ""}</p>`;
  }
}

// ---- Who's out / when (everyone) ----
const whosOutBody = document.querySelector("#section-whos-out .card-body");

function renderWhosOut(requests) {
  if (requests.length === 0) {
    whosOutBody.innerHTML = `<p class="state-empty">No one is scheduled to be out this period.</p>`;
    return;
  }

  whosOutBody.innerHTML = "";
  requests.forEach((req) => {
    const row = document.createElement("div");
    row.className = "list-row";
    row.innerHTML = `
      <div class="list-row-main">
        <span class="list-row-title">${req.employee_name || "Unknown employee"}</span>
        <span class="list-row-sub">
          ${req.leave_type_name || "Leave"} · ${formatDate(req.start_date)} – ${formatDate(req.end_date)}
          · ${req.total_days} day${req.total_days === 1 ? "" : "s"}
        </span>
      </div>
    `;
    whosOutBody.appendChild(row);
  });
}

async function loadWhosOut(period) {
  whosOutBody.innerHTML = `<p class="state-loading">Loading…</p>`;
  try {
    const requests = await api.getApprovedLeaveForPeriod(
      period.month,
      period.year,
    );
    console.log("requests", requests);
    renderWhosOut(requests);
  } catch (err) {
    whosOutBody.innerHTML = `<p class="state-error">Couldn't load this data. ${err.message || ""}</p>`;
  }
}

// ---- Leave balances (everyone, scoped by role) ----
const balancesBody = document.querySelector(
  "#section-leave-balances .card-body",
);

function renderBalanceRows(balances) {
  if (balances.length === 0) {
    return `<p class="state-empty">No leave types configured yet.</p>`;
  }
  return balances
    .map(
      (b) => `
    <div class="list-row">
      <div class="list-row-main">
        <span class="list-row-title">${b.leave_type_name}</span>
        <span class="list-row-sub">${b.used_days} used of ${b.default_days_per_year}</span>
      </div>
      <span class="balance-pill">${b.remaining_days} left</span>
    </div>
  `,
    )
    .join("");
}

function renderMyBalances(balances) {
  balancesBody.innerHTML = renderBalanceRows(balances);
}

function renderAllBalances(employeeBalances) {
  if (employeeBalances.length === 0) {
    balancesBody.innerHTML = `<p class="state-empty">No active employees found.</p>`;
    return;
  }
  balancesBody.innerHTML = employeeBalances
    .map(
      (emp) => `
    <div class="balance-group">
      <h3 class="balance-group-title">${emp.employee_name}</h3>
      ${renderBalanceRows(emp.balances)}
    </div>
  `,
    )
    .join("");
}

async function loadLeaveBalances() {
  balancesBody.innerHTML = `<p class="state-loading">Loading…</p>`;
  const year = new Date().getFullYear();
  try {
    if (isHR) {
      const data = await api.getAllLeaveBalances(year);
      renderAllBalances(data);
    } else {
      const data = await api.getMyLeaveBalances(year);
      renderMyBalances(data);
    }
  } catch (err) {
    balancesBody.innerHTML = `<p class="state-error">Couldn't load leave balances. ${err.message || ""}</p>`;
  }
}

// ---- Payslips for selected period ----
const payslipsBody = document.querySelector("#section-payslips .card-body");

function formatCurrency(value) {
  return `$${Number(value).toLocaleString(undefined, { minimumFractionDigits: 2 })}`;
}

function renderPayslips(payslips, showEmployeeName) {
  if (payslips.length === 0) {
    payslipsBody.innerHTML = `<p class="state-empty">No payslips generated for this period yet.</p>`;
    return;
  }

  payslipsBody.innerHTML = payslips
    .map(
      (p) => `
    <div class="list-row">
      <div class="list-row-main">
        <span class="list-row-title">${showEmployeeName ? p.employee_name : "Net pay"}</span>
        <span class="list-row-sub">
          Gross ${formatCurrency(p.gross_pay)} · Tax ${formatCurrency(p.tax_amount)}
          · SS ${formatCurrency(p.social_security_amount)} · ${p.paid_days}/${p.working_days_in_period} days paid
        </span>
      </div>
      <span class="balance-pill">${formatCurrency(p.net_pay)}</span>
    </div>
  `,
    )
    .join("");
}

async function loadPayslips(period) {
  payslipsBody.innerHTML = `<p class="state-loading">Loading…</p>`;
  try {
    if (isHR) {
      const payslips = await api.getAllPayslipsForPeriod(
        period.month,
        period.year,
      );
      renderPayslips(payslips, true);
    } else {
      const payslips = await api.getMyPayslipsForPeriod(
        period.month,
        period.year,
      );
      renderPayslips(payslips, false);
    }
  } catch (err) {
    payslipsBody.innerHTML = `<p class="state-error">Couldn't load payslips. ${err.message || ""}</p>`;
  }
}

// ---- Generate payroll button (HR only) ----
const generateBtn = document.getElementById("generate-payroll-btn");

generateBtn.addEventListener("click", async () => {
  const period = getSelectedPeriod();
  const monthName = MONTH_NAMES[period.month - 1];

  if (
    !confirm(
      `Generate payroll for ${monthName} ${period.year} for all active employees?`,
    )
  )
    return;

  generateBtn.disabled = true;
  generateBtn.textContent = "Generating…";

  try {
    const result = await api.generatePayrollBatch(period.month, period.year);
    alert(
      `Done. Generated ${result.created.length} payslip(s).` +
        (result.skipped.length
          ? ` Skipped ${result.skipped.length} (already existed).`
          : ""),
    );
    await loadPayslips(period);
  } catch (err) {
    alert(err.message || "Payroll generation failed.");
  } finally {
    generateBtn.disabled = false;
    generateBtn.textContent = "Generate payroll for this period";
  }
});

const exportBtn = document.getElementById("export-payslips-btn");
exportBtn.hidden = !isHR;

exportBtn.addEventListener("click", async () => {
  const period = getSelectedPeriod();
  exportBtn.disabled = true;
  exportBtn.textContent = "Exporting…";
  try {
    await api.downloadPayslipsExcel(period.month, period.year);
  } catch (err) {
    alert(err.message || "Export failed.");
  } finally {
    exportBtn.disabled = false;
    exportBtn.textContent = "Export to Excel";
  }
});

// init
populatePeriodSelectors();
applyRoleVisibility();
loadWhosOut(getSelectedPeriod());
loadLeaveBalances();
loadPayslips(getSelectedPeriod());

if (isHR) {
  loadPendingApprovals();
}
