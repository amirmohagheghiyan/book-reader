/* app.js — small Bootstrap helpers: tooltips, toasts, swatch color codes, and the print button. */
(function () {
  "use strict";

  document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(function (el) {
    bootstrap.Tooltip.getOrCreateInstance(el);
  });

  document.querySelectorAll("[data-toast-target]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var toast = document.getElementById(btn.dataset.toastTarget);
      if (toast) bootstrap.Toast.getOrCreateInstance(toast).show();
    });
  });

  // The جزوه print view: open the browser's print dialog (Save as PDF lives there).
  document.querySelectorAll("[data-print]").forEach(function (btn) {
    btn.addEventListener("click", function () { window.print(); });
  });

  // Show the real computed color of each swatch as a hex code.
  function toHex(rgb) {
    var m = rgb.match(/\d+/g);
    if (!m || m.length < 3) return rgb;
    return "#" + m.slice(0, 3).map(function (n) {
      return ("0" + Number(n).toString(16)).slice(-2);
    }).join("").toUpperCase();
  }
  document.querySelectorAll(".ds-swatch").forEach(function (swatch) {
    var code = swatch.parentElement.querySelector("[data-swatch-code]");
    if (code) code.textContent = toHex(getComputedStyle(swatch).backgroundColor);
  });
})();
