/* Renders #fund-chart from the #fund-chart-data json_script payload.
   data-compact="1" = balance line only (Action inbox card). */
(function () {
  "use strict";
  var dataEl = document.getElementById("fund-chart-data");
  var canvas = document.getElementById("fund-chart");
  if (!dataEl || !canvas || typeof Chart === "undefined") return;
  var points = JSON.parse(dataEl.textContent);
  if (!points.length) return;
  var compact = canvas.dataset.compact === "1";
  var palette = getComputedStyle(document.documentElement);
  var color = function (name) { return palette.getPropertyValue(name).trim(); };
  var vnd = function (v) { return Number(v).toLocaleString("vi-VN"); };
  var datasets = [
    {
      type: "line",
      label: canvas.dataset.labelBalance || "Balance",
      data: points.map(function (p) { return p.balance_vnd; }),
      borderColor: color("--color-brand"),
      backgroundColor: color("--color-surface-muted"),
      fill: true,
      tension: 0.2,
      pointRadius: compact ? 0 : 2,
      order: 0,
    },
  ];
  if (!compact) {
    datasets.push(
      {
        type: "bar",
        label: canvas.dataset.labelInflows || "Inflows",
        data: points.map(function (p) { return p.inflows_vnd; }),
        backgroundColor: color("--color-info"),
        order: 1,
      },
      {
        type: "bar",
        label: canvas.dataset.labelOutflows || "Outflows",
        data: points.map(function (p) { return p.outflows_vnd; }),
        // Distinct from the brand balance line; still the brand family, never semantic.
        backgroundColor: color("--color-brand-active"),
        order: 1,
      }
    );
  }
  new Chart(canvas, {
    data: {
      labels: points.map(function (p) {
        var raw = String(p.period_start || "");
        // period_start is ISO date; show d/m/Y to match staff_datetime day-first.
        var m = raw.match(/^(\d{4})-(\d{2})-(\d{2})/);
        return m ? m[3] + "/" + m[2] + "/" + m[1] : raw;
      }),
      datasets: datasets,
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: false,
      interaction: { mode: "index", intersect: false },
      scales: {
        x: { ticks: { display: !compact } },
        y: { ticks: { callback: vnd } },
      },
      plugins: {
        legend: { display: !compact },
        tooltip: {
          callbacks: {
            label: function (ctx) {
              return ctx.dataset.label + ": " + vnd(ctx.parsed.y) + " VND";
            },
          },
        },
      },
    },
  });
})();
