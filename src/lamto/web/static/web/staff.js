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

  // Every mutation is a full page navigation; nothing announces the outcome
  // unless focus lands on the flash region.
  var flash = document.querySelector(".flash-messages");
  if (flash) {
    flash.focus();
  }
})();
