// Behaviour for the two data- attributes the staff templates already ship:
// data-busy-on-submit (loading state) and data-copy (hash copy button).
(function () {
  "use strict";

  // Loading state. Marks the form busy and blocks the double submit; the
  // browser is navigating away, so there is nothing to reset.
  document.addEventListener("submit", function (event) {
    var form = event.target;
    if (!(form instanceof HTMLFormElement)) return;
    if (!form.hasAttribute("data-busy-on-submit")) return;
    if (form.getAttribute("aria-busy") === "true") {
      event.preventDefault();
      return;
    }
    form.setAttribute("aria-busy", "true");
  });

  // Copy a hash. Announces the result in place: the button is the only thing
  // the user is looking at, and a silent copy is indistinguishable from a
  // broken one.
  document.addEventListener("click", function (event) {
    var button = event.target.closest("[data-copy]");
    if (!button) return;
    var strings = window.lamtoI18n || {};
    var value = button.getAttribute("data-copy");
    var original = button.textContent;
    var originalLabel = button.getAttribute("aria-label");
    var done = function (message) {
      button.textContent = message;
      button.setAttribute("aria-label", message);
      window.setTimeout(function () {
        button.textContent = original;
        if (originalLabel) {
          button.setAttribute("aria-label", originalLabel);
        } else {
          button.removeAttribute("aria-label");
        }
      }, 2000);
    };
    if (!navigator.clipboard) {
      done(strings.copyFailed || "Copy failed");
      return;
    }
    navigator.clipboard.writeText(value).then(
      function () {
        done(strings.copied || "Copied");
      },
      function () {
        done(strings.copyFailed || "Copy failed");
      }
    );
  });
  // Announce form validation errors to assistive technology.
  document.querySelectorAll("ul.errorlist").forEach(function (el) {
    el.setAttribute("role", "alert");
  });

  // Copy feedback swaps the button's own text; the live region makes the
  // swap announced.
  document.querySelectorAll("[data-copy]").forEach(function (el) {
    el.setAttribute("aria-live", "polite");
  });

  // Price comparison on proposal create form.
  // Advisory reading calculated client-side so attached quotation PDF is never discarded.
  document.addEventListener("click", function (event) {
    var button = event.target.closest("[data-price-compare]");
    if (!button) return;
    var strings = window.lamtoI18n || {};
    var form = button.closest("form");
    var amountInput = form ? form.querySelector('input[name="amount_vnd"]') : document.querySelector('input[name="amount_vnd"]');
    var resultEl = form ? form.querySelector("[data-price-comparison-result]") : document.querySelector("[data-price-comparison-result]");
    if (!resultEl) return;

    var rawValue = amountInput ? amountInput.value.trim() : "";
    var amount = parseInt(rawValue, 10);
    if (!rawValue || isNaN(amount) || amount <= 0) {
      resultEl.textContent = strings.priceCompareEnterAmount || "Enter an amount to compare.";
      return;
    }

    var hasRef = button.getAttribute("data-has-reference-price") === "true";
    if (!hasRef) {
      var catLabel = button.getAttribute("data-category-label") || "";
      var noRefTpl = strings.priceCompareNoReference || "No reference prices for {category}. Reference prices are synthetic sample data and currently cover Elevator only.";
      resultEl.textContent = noRefTpl.replace("{category}", catLabel);
      return;
    }

    var average = parseInt(button.getAttribute("data-average"), 10);
    var min = parseInt(button.getAttribute("data-min"), 10);
    var max = parseInt(button.getAttribute("data-max"), 10);
    var rangeFormatted = button.getAttribute("data-range-formatted") || "";
    var samplesFormatted = button.getAttribute("data-samples-formatted") || "";

    var diff = amount - average;
    var pct = Math.round(Math.abs(diff) / average * 100);

    var template = "";
    if (amount >= min && amount <= max) {
      template = diff >= 0
        ? (strings.priceCompareWithinAbove || "Within the range of comparable jobs ({range}, {samples}). {pct}% above the reference price.")
        : (strings.priceCompareWithinBelow || "Within the range of comparable jobs ({range}, {samples}). {pct}% below the reference price.");
    } else if (amount > max) {
      template = strings.priceCompareAbove || "Above the range of comparable jobs ({range}, {samples}). {pct}% above the reference price.";
    } else {
      template = strings.priceCompareBelow || "Below the range of comparable jobs ({range}, {samples}). {pct}% below the reference price.";
    }

    resultEl.textContent = template
      .replace("{range}", rangeFormatted)
      .replace("{samples}", samplesFormatted)
      .replace("{pct}", String(pct));
  });

  // Every mutation is a full page navigation; nothing announces the outcome
  // unless focus lands on the flash region.
  var flash = document.querySelector(".flash-messages");
  if (flash) {
    flash.focus();
  }
})();
