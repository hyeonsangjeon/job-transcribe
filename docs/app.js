const THRESHOLDS = [0, 0.01, 0.03, 0.05, 0.1, 0.15, 0.2];
const SCRIPT_NODE = document.currentScript;
const DATA_URL = SCRIPT_NODE?.dataset.dataUrl ?? "./data/asr-benchmark.json";
const LANGUAGE = document.documentElement.lang === "en" ? "en" : "ko";
const TEXT = {
  ko: {
    singleDataset: "단일 화자 3,922문장",
    callDataset: "콜센터 3개 시나리오",
    chartSingle: "Pass rate by model",
    chartCall: "Provider별 시나리오 Pass / Fail",
    hangulBasis: "Hangul ground truth",
    numericBasis: "Numeric ground truth",
    passLabel: "Pass",
    failLabel: "Fail",
    legendPass: "Pass: CER 기준 이하",
    legendFail: "Fail: CER 기준 초과",
    subtitleSuffix: "기준",
    loadError: "데이터를 불러오지 못했습니다",
  },
  en: {
    singleDataset: "single-speaker 3,922-utterance benchmark",
    callDataset: "3 call-center scenarios",
    chartSingle: "Pass rate by model",
    chartCall: "Scenario pass/fail by provider",
    hangulBasis: "Hangul ground truth",
    numericBasis: "Numeric ground truth",
    passLabel: "Pass",
    failLabel: "Fail",
    legendPass: "Pass: CER within threshold",
    legendFail: "Fail: CER over threshold",
    subtitleSuffix: "threshold",
    loadError: "Could not load benchmark data",
  },
}[LANGUAGE];

const PROVIDER_ORDER = ["azure", "aws", "clova", "gcp"];

const state = {
  dataset: "single",
  basis: "hangul ground truth",
  thresholdIndex: 3,
  selectedEntity: "whisper_large",
};

const els = {
  datasetButtons: Array.from(document.querySelectorAll("[data-dataset]")),
  basisControl: document.querySelector(".basis-control"),
  basisSelect: document.querySelector("#basis-select"),
  entitySelect: document.querySelector("#entity-select"),
  thresholdSlider: document.querySelector("#threshold-slider"),
  thresholdOutput: document.querySelector("#threshold-output"),
  chart: d3.select("#rate-chart"),
  tooltip: document.querySelector("#tooltip"),
  chartTitle: document.querySelector("#chart-title"),
  chartSubtitle: document.querySelector("#chart-subtitle"),
  selectedLabel: document.querySelector("#selected-label"),
  meanCer: document.querySelector("#mean-cer"),
  passRate: document.querySelector("#pass-rate"),
  riskRate: document.querySelector("#risk-rate"),
  legendPass: document.querySelector("[data-legend-pass]"),
  legendFail: document.querySelector("[data-legend-fail]"),
};

let benchmarkData;

function pct(value, digits = 2) {
  if (value === null || value === undefined || Number.isNaN(value)) {
    return "n/a";
  }
  return `${(value * 100).toFixed(digits)}%`;
}

function pp(value) {
  if (value === null || value === undefined || Number.isNaN(value)) {
    return "n/a";
  }
  return `${(value * 100).toFixed(2)} pp`;
}

function threshold() {
  return THRESHOLDS[state.thresholdIndex];
}

function modelOptions() {
  if (state.dataset === "single") {
    return benchmarkData.single_speaker.summary.map((row) => ({
      id: row.model_id,
      label: row.model,
    }));
  }

  return Array.from(
    new Map(
      benchmarkData.call_center.provider_summary.map((row) => [
        row.provider_id,
        { id: row.provider_id, label: row.provider },
      ]),
    ).values(),
  ).sort((a, b) => providerOrder(a.id) - providerOrder(b.id));
}

function providerOrder(providerId) {
  const index = PROVIDER_ORDER.indexOf(providerId);
  return index === -1 ? PROVIDER_ORDER.length : index;
}

function currentRows() {
  const currentThreshold = threshold();

  if (state.dataset === "single") {
    return benchmarkData.single_speaker.summary.map((summary) => {
      const thresholdRow = benchmarkData.single_speaker.thresholds.find(
        (row) => row.model_id === summary.model_id && row.cer_threshold === currentThreshold,
      );
      return {
        id: summary.model_id,
        label: summary.model,
        passRate: thresholdRow?.pass_rate ?? 0,
        failRate: 1 - (thresholdRow?.pass_rate ?? 0),
        meanCer: summary.mean_cer,
        medianCer: summary.median_cer,
        riskLabel: `${pct(summary.over_10pct_rate)} >10%`,
      };
    });
  }

  const observations = benchmarkData.call_center.observations.filter((row) => row.basis === state.basis);
  const providerSummary = benchmarkData.call_center.provider_summary.filter((row) => row.basis === state.basis);

  return providerSummary.map((summary) => {
    const rows = observations.filter((row) => row.provider_id === summary.provider_id);
    const passCount = rows.filter((row) => row.cer <= currentThreshold).length;
    const passRate = rows.length ? passCount / rows.length : 0;
    return {
      id: summary.provider_id,
      label: summary.provider,
      passRate,
      failRate: 1 - passRate,
      meanCer: summary.mean_cer,
      medianCer: summary.median_cer,
      riskLabel: `max ${pct(summary.max_cer)}`,
    };
  });
}

function selectedRow() {
  return currentRows().find((row) => row.id === state.selectedEntity) ?? currentRows()[0];
}

function populateEntitySelect() {
  const options = modelOptions();
  if (!options.some((option) => option.id === state.selectedEntity)) {
    state.selectedEntity = options[0]?.id;
  }

  els.entitySelect.innerHTML = "";
  for (const option of options) {
    const node = document.createElement("option");
    node.value = option.id;
    node.textContent = option.label;
    node.selected = option.id === state.selectedEntity;
    els.entitySelect.append(node);
  }
}

function renderSummary() {
  const row = selectedRow();
  if (!row) {
    return;
  }

  els.selectedLabel.textContent = row.label;
  els.meanCer.textContent = pct(row.meanCer);
  els.passRate.textContent = pct(row.passRate);
  els.riskRate.textContent = row.riskLabel;
}

function showTooltip(event, row) {
  const title = state.dataset === "single" ? "Model" : "Provider";
  els.tooltip.innerHTML = `
    <strong>${title}: ${row.label}</strong><br>
    ${TEXT.passLabel}: ${pct(row.passRate)}<br>
    ${TEXT.failLabel}: ${pct(row.failRate)}<br>
    Mean CER: ${pct(row.meanCer)}
  `;
  els.tooltip.hidden = false;
  const panel = event.currentTarget.ownerSVGElement.getBoundingClientRect();
  const x = event.clientX - panel.left + 14;
  const y = event.clientY - panel.top + 14;
  els.tooltip.style.left = `${x}px`;
  els.tooltip.style.top = `${y}px`;
}

function hideTooltip() {
  els.tooltip.hidden = true;
}

function renderChart() {
  const rows = currentRows().sort((a, b) => {
    const passDelta = b.passRate - a.passRate;
    if (passDelta !== 0) {
      return passDelta;
    }
    if (state.dataset === "call") {
      return providerOrder(a.id) - providerOrder(b.id);
    }
    return a.label.localeCompare(b.label);
  });
  const container = els.chart.node().parentElement;
  const width = Math.max(container.clientWidth, 320);
  const height = Math.max(310, rows.length * 62 + 72);
  const isCompact = width < 560;
  const margin = isCompact
    ? { top: 18, right: 18, bottom: 34, left: 86 }
    : { top: 18, right: 84, bottom: 34, left: 142 };
  const innerWidth = width - margin.left - margin.right;
  const innerHeight = height - margin.top - margin.bottom;

  els.chart.attr("viewBox", `0 0 ${width} ${height}`).attr("height", height);
  els.chart.selectAll("*").remove();

  const svg = els.chart;
  const x = d3.scaleLinear().domain([0, 1]).range([0, innerWidth]);
  const y = d3
    .scaleBand()
    .domain(rows.map((row) => row.label))
    .range([0, innerHeight])
    .padding(0.28);

  const g = svg.append("g").attr("transform", `translate(${margin.left},${margin.top})`);

  g.append("g")
    .selectAll("line")
    .data([0, 0.25, 0.5, 0.75, 1])
    .join("line")
    .attr("class", "grid-line")
    .attr("x1", (d) => x(d))
    .attr("x2", (d) => x(d))
    .attr("y1", -8)
    .attr("y2", innerHeight + 8);

  g.append("g")
    .selectAll("text")
    .data([0, 0.25, 0.5, 0.75, 1])
    .join("text")
    .attr("class", "axis-label")
    .attr("x", (d) => x(d))
    .attr("y", innerHeight + 28)
    .attr("text-anchor", "middle")
    .text((d) => pct(d, 0));

  const rowGroups = g
    .selectAll("g.row")
    .data(rows, (row) => row.id)
    .join("g")
    .attr("class", (row) => (row.id === state.selectedEntity ? "row selected-row" : "row"))
    .attr("transform", (row) => `translate(0,${y(row.label)})`);

  rowGroups
    .append("text")
    .attr("class", "bar-label")
    .attr("x", -14)
    .attr("y", y.bandwidth() / 2 + 4)
    .attr("text-anchor", "end")
    .text((row) => row.label);

  rowGroups
    .append("rect")
    .attr("class", "fail-segment")
    .attr("x", 0)
    .attr("y", 0)
    .attr("width", innerWidth)
    .attr("height", y.bandwidth())
    .attr("rx", 6)
    .attr("fill", "#d86a63");

  rowGroups
    .filter((row) => row.passRate > 0)
    .append("rect")
    .attr("class", "pass-segment")
    .attr("x", 0)
    .attr("y", 0)
    .attr("width", (row) => x(row.passRate))
    .attr("height", y.bandwidth())
    .attr("rx", 6)
    .attr("fill", "#109e60");

  rowGroups
    .filter((row) => row.id === state.selectedEntity)
    .append("rect")
    .attr("class", "selected-outline")
    .attr("x", -4)
    .attr("y", -4)
    .attr("width", innerWidth + 8)
    .attr("height", y.bandwidth() + 8)
    .attr("rx", 9)
    .attr("fill", "none");

  rowGroups
    .append("rect")
    .attr("class", "bar-hitbox")
    .attr("x", 0)
    .attr("y", 0)
    .attr("width", innerWidth)
    .attr("height", y.bandwidth())
    .attr("rx", 6)
    .attr("fill", "transparent")
    .attr("tabindex", 0)
    .attr("role", "img")
    .attr("aria-label", (row) => `${row.label} ${TEXT.passLabel} ${pct(row.passRate)}, ${TEXT.failLabel} ${pct(row.failRate)}`)
    .on("mouseenter focus", showTooltip)
    .on("mousemove", showTooltip)
    .on("mouseleave blur", hideTooltip)
    .on("click", (_, row) => {
      state.selectedEntity = row.id;
      populateEntitySelect();
      render();
    });

  rowGroups
    .filter((row) => row.passRate > 0)
    .append("text")
    .attr("class", "value-label pass-value")
    .attr("x", (row) => (row.passRate > 0.45 ? x(row.passRate) - 8 : 8))
    .attr("y", y.bandwidth() / 2 + 4)
    .attr("text-anchor", (row) => (row.passRate > 0.45 ? "end" : "start"))
    .text((row) => `${pct(row.passRate)}${isCompact ? "" : ` ${TEXT.passLabel}`}`);

  rowGroups
    .filter((row) => row.failRate > 0)
    .append("text")
    .attr("class", "value-label fail-value")
    .attr("x", (row) => x(row.passRate))
    .attr("y", y.bandwidth() / 2 + 4)
    .attr("dx", 8)
    .text((row) => `${pct(row.failRate)}${isCompact ? "" : ` ${TEXT.failLabel}`}`);
}

function renderText() {
  const currentThreshold = threshold();
  const datasetLabel = state.dataset === "single" ? TEXT.singleDataset : TEXT.callDataset;
  const basisLabel = state.basis === "numeric ground truth" ? TEXT.numericBasis : TEXT.hangulBasis;
  els.thresholdOutput.textContent = pct(currentThreshold, currentThreshold < 0.1 ? 0 : 0);
  els.chartTitle.textContent = state.dataset === "single" ? TEXT.chartSingle : TEXT.chartCall;
  els.chartSubtitle.textContent =
    state.dataset === "single"
      ? `${datasetLabel} · CER <= ${pct(currentThreshold, 0)} ${TEXT.subtitleSuffix}`
      : `${basisLabel} · ${datasetLabel} · CER <= ${pct(currentThreshold, 0)} ${TEXT.subtitleSuffix}`;
  els.legendPass.textContent = TEXT.legendPass;
  els.legendFail.textContent = TEXT.legendFail;
}

function renderControls() {
  els.datasetButtons.forEach((button) => {
    button.classList.toggle("is-active", button.dataset.dataset === state.dataset);
  });
  els.basisControl.hidden = state.dataset !== "call";
  els.basisSelect.value = state.basis;
  els.thresholdSlider.value = String(state.thresholdIndex);
  populateEntitySelect();
}

function render() {
  renderControls();
  renderText();
  renderChart();
  renderSummary();
}

function bindEvents() {
  els.datasetButtons.forEach((button) => {
    button.addEventListener("click", () => {
      state.dataset = button.dataset.dataset;
      if (state.dataset === "call") {
        state.basis = "numeric ground truth";
        state.selectedEntity = "azure";
        state.thresholdIndex = 4;
      } else {
        state.selectedEntity = "whisper_large";
        state.thresholdIndex = 3;
      }
      render();
    });
  });

  els.basisSelect.addEventListener("change", () => {
    state.basis = els.basisSelect.value;
    render();
  });

  els.entitySelect.addEventListener("change", () => {
    state.selectedEntity = els.entitySelect.value;
    render();
  });

  els.thresholdSlider.addEventListener("input", () => {
    state.thresholdIndex = Number(els.thresholdSlider.value);
    render();
  });

  window.addEventListener("resize", () => {
    window.requestAnimationFrame(renderChart);
  });
}

fetch(DATA_URL)
  .then((response) => {
    if (!response.ok) {
      throw new Error(`Failed to load data: ${response.status}`);
    }
    return response.json();
  })
  .then((data) => {
    benchmarkData = data;
    bindEvents();
    render();
  })
  .catch((error) => {
    const root = document.querySelector("[data-app-root]");
    root.innerHTML = `<div class="notice">${TEXT.loadError}: ${error.message}</div>`;
  });
