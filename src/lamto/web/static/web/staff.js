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
  // Advisory reading requested via endpoint; attached quotation PDF is never discarded.
  document.addEventListener("click", function (event) {
    var button = event.target.closest("[data-price-compare]");
    if (!button) return;
    var strings = window.lamtoI18n || {};
    var form = button.closest("form");
    var amountInput = form ? form.querySelector('input[name="amount_vnd"]') : document.querySelector('input[name="amount_vnd"]');
    var resultEl = form ? form.querySelector("[data-price-comparison-result]") : document.querySelector("[data-price-comparison-result]");
    if (!resultEl) return;

    var rawValue = amountInput ? amountInput.value.trim() : "";
    if (!rawValue) {
      resultEl.textContent = strings.priceCompareEnterAmount || "Enter an amount to compare.";
      return;
    }
    // A dot is the ordinary VND thousands separator, and a number input keeps
    // the first one: "460.000.000" arrives here as "460.000000". parseInt would
    // read that as 460 and report a confident comparison against the wrong
    // amount, so anything but whole digits is refused.
    var amount = parseInt(rawValue, 10);
    if (!/^\d+$/.test(rawValue) || amount <= 0) {
      resultEl.textContent = strings.priceCompareWholeVnd
        || "Enter the amount in whole VND, with no separators.";
      return;
    }

    var hasRef = button.getAttribute("data-has-reference-price") === "true";
    if (!hasRef) {
      var catLabel = button.getAttribute("data-category-label") || "";
      var noRefTpl = strings.priceCompareNoReference || "Price predictions not yet supported for {category}. Currently available for Elevator only.";
      resultEl.textContent = noRefTpl.replace("{category}", catLabel);
      return;
    }

    var compareUrl = button.getAttribute("data-compare-url");
    if (!compareUrl) {
      var average = parseInt(button.getAttribute("data-average"), 10);
      var rangeFormatted = button.getAttribute("data-range-formatted") || "";
      var diff = amount - average;
      if (diff === 0) {
        resultEl.textContent = strings.priceCompareEqual || "Equal to the reference price";
        return;
      }
      var pct = Math.round(Math.abs(diff) / average * 100);
      var isBelow = diff < 0;
      var arrow = isBelow ? "↓" : "↑";
      var arrowClass = isBelow ? "price-comparison-arrow-below" : "price-comparison-arrow-above";
      var template = isBelow
        ? (strings.priceCompareBelow || "{pct}% below the reference price (around {range})")
        : (strings.priceCompareAbove || "{pct}% above the reference price (around {range})");
      var text = template
        .replace("{range}", rangeFormatted)
        .replace("{pct}", String(pct));
      resultEl.innerHTML = '<span class="price-comparison-arrow ' + arrowClass + '" aria-hidden="true">' + arrow + "</span> " + text;
      return;
    }

    button.setAttribute("aria-busy", "true");
    button.disabled = true;

    var csrfEl = form ? form.querySelector('input[name="csrfmiddlewaretoken"]') : document.querySelector('input[name="csrfmiddlewaretoken"]');
    var csrfToken = csrfEl ? csrfEl.value : "";

    fetch(compareUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken
      },
      body: JSON.stringify({ amount_vnd: amount })
    })
      .then(function (response) {
        return response.json();
      })
      .then(function (data) {
        if (data.id) {
          var predictionInput = form ? form.querySelector('input[name="price_prediction_id"]') : document.querySelector('input[name="price_prediction_id"]');
          if (predictionInput) {
            predictionInput.value = data.id;
          }
        }
        if (data.formatted) {
          var arrowHtml = data.formatted.arrow
            ? '<span class="price-comparison-arrow ' + data.formatted.arrow_class + '" aria-hidden="true">' + data.formatted.arrow + '</span> '
            : '';
          var lineHtml = arrowHtml + (data.formatted.comparison_text || data.formatted.message || "");
          var reasoningHtml = data.formatted.reasoning
            ? '<div class="price-comparison-reasoning">' + data.formatted.reasoning + '</div>'
            : '';
          resultEl.innerHTML = lineHtml + reasoningHtml;
        } else if (data.error) {
          resultEl.textContent = data.error;
        }
      })
      .catch(function () {
        resultEl.textContent = strings.priceCompareEnterAmount || "Enter an amount to compare.";
      })
      .finally(function () {
        button.removeAttribute("aria-busy");
        button.disabled = false;
      });
  });

  // Every mutation is a full page navigation; nothing announces the outcome
  // unless focus lands on the flash region.
  var flash = document.querySelector(".flash-messages");
  if (flash) {
    flash.focus();
  }
})();
