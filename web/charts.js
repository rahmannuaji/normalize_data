// Grafik normalitas (Plotly). Warna dan font dibaca dari token CSS di :root.
// Titik bermasalah di Q-Q: |z| lebih dari Z_FLAG (merah), bisa diklik.
export const Z_FLAG = 2.5;
const FONT = 12; // px; minimum tampilan sesuai brand guidelines

function tokens() {
  const css = getComputedStyle(document.documentElement);
  const get = (n) => css.getPropertyValue(n).trim();
  return { brand: get("--brand"), ink: get("--ink"), muted: get("--muted"), line: get("--line"), bad: get("--bad"), font: get("--font-body") };
}

// "#rrggbb" + alfa -> "rgba(...)": Plotly tidak mengerti color-mix().
function alpha(hex, a) {
  const n = parseInt(hex.slice(1), 16);
  return `rgba(${n >> 16}, ${(n >> 8) & 255}, ${n & 255}, ${a})`;
}

const CONFIG = { displayModeBar: false, responsive: true };

function layout(t, xTitle, yTitle, extra = {}) {
  const axis = (title) => ({ title: { text: title, font: { size: FONT, color: t.muted }, standoff: 8 }, tickfont: { size: FONT, color: t.muted }, gridcolor: t.line, linecolor: t.line, zeroline: false, automargin: true });
  return {
    height: 280, margin: { l: 44, r: 12, t: 8, b: 40 }, showlegend: false,
    paper_bgcolor: "rgba(0,0,0,0)", plot_bgcolor: "rgba(0,0,0,0)",
    separators: ",.", font: { family: t.font, size: FONT, color: t.ink },
    xaxis: axis(xTitle), yaxis: axis(yTitle), hoverlabel: { font: { family: t.font, size: FONT } },
    ...extra,
  };
}

const mean = (v) => v.reduce((s, x) => s + x, 0) / v.length;

export function histogram(el, values) {
  const t = tokens();
  const n = values.length;
  const lo = Math.min(...values);
  const hi = Math.max(...values);
  const k = Math.min(30, Math.max(5, Math.ceil(Math.log2(n)) + 1)); // aturan Sturges
  const w = (hi - lo) / k || 1;
  const counts = new Array(k).fill(0);
  for (const v of values) counts[Math.min(k - 1, Math.floor((v - lo) / w))]++;
  const centers = counts.map((_, i) => lo + w * (i + 0.5));
  const m = mean(values);
  const sd = Math.sqrt(values.reduce((s, x) => s + (x - m) ** 2, 0) / (n - 1));
  const xs = Array.from({ length: 81 }, (_, i) => lo - w + ((hi - lo + 2 * w) * i) / 80);
  const ys = xs.map((x) => (n * w * Math.exp(-0.5 * ((x - m) / sd) ** 2)) / (sd * Math.sqrt(2 * Math.PI)));
  return Plotly.react(el, [
    { type: "bar", x: centers, y: counts, width: w * 0.96, marker: { color: alpha(t.brand, 0.55) }, hovertemplate: "%{y} responden<extra></extra>" },
    { type: "scatter", mode: "lines", x: xs, y: ys, line: { color: t.ink, width: 2 }, hoverinfo: "skip" },
  ], layout(t, "Nilai", "Jumlah responden"), CONFIG);
}

export function qq(el, q, onPick) {
  const t = tokens();
  const flag = q.sample.map((z) => Math.abs(z) > Z_FLAG);
  const edge = Math.ceil(Math.max(3, ...q.theoretical.map(Math.abs), ...q.sample.map(Math.abs)));
  const p = Plotly.react(el, [
    { type: "scatter", mode: "lines", x: [-edge, edge], y: [-edge, edge], line: { color: t.ink, width: 2 }, hoverinfo: "skip" },
    {
      type: "scatter", mode: "markers", x: q.theoretical, y: q.sample, customdata: q.rows,
      marker: { size: flag.map((f) => (f ? 10 : 7)), color: flag.map((f) => (f ? t.bad : alpha(t.brand, 0.55))) },
      hovertemplate: "Baris %{customdata}<extra></extra>",
    },
  ], layout(t, "Nilai yang diharapkan jika normal", "Nilai respondenmu (terstandar)"), CONFIG);
  return p.then(() => {
    el.removeAllListeners?.("plotly_click");
    el.on("plotly_click", (e) => {
      const pt = e.points.find((x) => x.curveNumber === 1);
      if (pt && flag[pt.pointIndex]) onPick(q.rows[pt.pointIndex], q.sample[pt.pointIndex]);
    });
  });
}

export function pp(el, d) {
  const t = tokens();
  return Plotly.react(el, [
    { type: "scatter", mode: "lines", x: [0, 1], y: [0, 1], line: { color: t.ink, width: 2 }, hoverinfo: "skip" },
    { type: "scatter", mode: "markers", x: d.expected, y: d.observed, marker: { size: 6, color: alpha(t.brand, 0.55) }, hoverinfo: "skip" },
  ], layout(t, "Proporsi yang diharapkan", "Proporsi respondenmu"), CONFIG);
}

export function boxplot(el, values) {
  const t = tokens();
  return Plotly.react(el, [
    {
      type: "box", x: values, orientation: "h", boxpoints: "outliers", name: "",
      fillcolor: alpha(t.brand, 0.55), line: { color: t.ink, width: 2 },
      marker: { color: t.bad, size: 7, outliercolor: t.bad },
      hovertemplate: "%{x}<extra></extra>",
    },
  ], layout(t, "Nilai", "", { height: 200, yaxis: { visible: false } }), CONFIG);
}
