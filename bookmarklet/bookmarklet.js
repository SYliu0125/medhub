/* MedHub Timesheet Filler — Bookmarklet source
 * Minified version lives in install.html
 * Edit this file, then run: node build.js to regenerate install.html
 */
(function () {
  "use strict";

  var START = "8:00am";
  var END   = "6:00pm";

  if (!location.hostname.includes("medhub.com")) {
    alert("Please open MedHub in this tab first, then click the bookmark again.");
    return;
  }

  // If not on pull-down interface, redirect there (preserving startDate)
  var params = new URLSearchParams(location.search);
  if (params.get("method") !== "1") {
    var startDate = params.get("startDate");
    if (!startDate) {
      var today = new Date();
      var sun   = new Date(today);
      sun.setDate(today.getDate() - today.getDay());
      var mm = String(sun.getMonth() + 1).padStart(2, "0");
      var dd = String(sun.getDate()).padStart(2, "0");
      startDate = mm + "/" + dd + "/" + sun.getFullYear();
    }
    location.href = location.origin +
      "/u/r/schedule_timesheet.mh?startDate=" + encodeURIComponent(startDate) +
      "&tab=1&action=method&method=1";
    // After page loads, click the bookmark again to fill
    return;
  }

  // ── Modal UI ────────────────────────────────────────────────────────────────
  var overlay = document.createElement("div");
  overlay.style.cssText =
    "position:fixed;top:0;left:0;width:100%;height:100%;" +
    "background:rgba(0,0,0,.5);z-index:999998;" +
    "display:flex;align-items:center;justify-content:center";

  var box = document.createElement("div");
  box.style.cssText =
    "background:#fff;border-radius:12px;padding:24px;width:288px;" +
    "font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;" +
    "box-shadow:0 8px 32px rgba(0,0,0,.3)";

  box.innerHTML =
    "<h2 style='margin:0 0 6px;font-size:16px;color:#0d6efd'>MedHub Timesheet Filler</h2>" +
    "<p style='margin:0 0 16px;font-size:13px;color:#666'>Fill Mon–Fri: <b>8:00am – 6:00pm</b></p>" +
    "<button id='_mh_sub' style='width:100%;padding:9px;background:#0d6efd;color:#fff;" +
      "border:none;border-radius:7px;font-size:13px;font-weight:600;cursor:pointer;margin-bottom:8px'>" +
      "Fill &amp; Submit</button>" +
    "<button id='_mh_fill' style='width:100%;padding:9px;background:#e9ecef;color:#333;" +
      "border:none;border-radius:7px;font-size:13px;cursor:pointer;margin-bottom:8px'>" +
      "Fill Only (review before submit)</button>" +
    "<button id='_mh_cancel' style='width:100%;padding:8px;background:none;color:#999;" +
      "border:1px solid #ddd;border-radius:7px;font-size:12px;cursor:pointer'>" +
      "Cancel</button>";

  overlay.appendChild(box);
  document.body.appendChild(overlay);

  function close() { document.body.removeChild(overlay); }

  function fill(submitAfter) {
    var filled = 0;
    for (var d = 2; d <= 6; d++) {
      var inEl  = document.querySelector("select[name='day" + d + "_1_in']");
      var outEl = document.querySelector("select[name='day" + d + "_1_out']");
      if (!inEl || !outEl) continue;
      inEl.value  = START;  inEl.dispatchEvent(new Event("change", { bubbles: true }));
      outEl.value = END;   outEl.dispatchEvent(new Event("change", { bubbles: true }));
      filled++;
    }
    if (submitAfter) {
      var btn = document.querySelector("a[aria-label='Submit Work Hours']");
      if (btn) btn.click(); else alert("⚠ Submit button not found — please submit manually.");
    }
    return filled;
  }

  document.getElementById("_mh_sub").onclick = function () {
    close();
    var n = fill(true);
    alert("✓ Filled " + n + " day(s) and submitted!");
  };
  document.getElementById("_mh_fill").onclick = function () {
    close();
    var n = fill(false);
    alert("✓ Filled " + n + " day(s). Please review and click Submit.");
  };
  document.getElementById("_mh_cancel").onclick = close;
  overlay.onclick = function (e) { if (e.target === overlay) close(); };
})();
