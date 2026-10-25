// State UI dan navigasi langkah. Isi langkah 1–7 dirender ke #step1..#step7 (Task 10–12).
import { ready } from "./engine.js";

const AUTHOR = ""; // nama pembuat untuk footer; biarkan kosong sampai diberikan pemilik proyek

export const state = {};

const pages = [...document.querySelectorAll("section.page")];
const stepsEl = document.getElementById("steps");
const reduceMotion = matchMedia("(prefers-reduced-motion: reduce)");
let cur = -1;

for (const p of pages.slice(1)) {
  const b = document.createElement("button");
  b.type = "button";
  b.className = "step";
  b.dataset.go = p.dataset.step;
  b.innerHTML = `<b>${p.dataset.step}</b>`;
  b.append(p.dataset.title);
  stepsEl.append(b);
}

// Semua elemen [data-go] (stepper, tombol Kembali/Lanjut, logo) berpindah langkah lewat go().
document.addEventListener("click", (e) => {
  const t = e.target.closest("[data-go]");
  if (!t || t.disabled) return;
  e.preventDefault();
  go(Number(t.dataset.go));
});

export function go(step) {
  if (step > 1 && !state.table) {
    go(1);
    showError("Masukkan datamu dulu di langkah 1.");
    return;
  }
  const first = cur < 0;
  cur = step;
  for (const p of pages) {
    p.classList.toggle("on", Number(p.dataset.step) === step);
    p.querySelector(":scope > .page-error")?.remove();
  }
  [...stepsEl.children].forEach((b, i) => {
    const n = i + 1;
    b.classList.toggle("on", n === step);
    b.classList.toggle("done", n < step);
    b.disabled = n > 1 && !state.table;
    if (n === step) b.setAttribute("aria-current", "step");
    else b.removeAttribute("aria-current");
  });
  stepsEl.hidden = step === 0;
  if (!first) {
    scrollTo({ top: 0, behavior: reduceMotion.matches ? "auto" : "smooth" });
    pages[step].querySelector("h1, h2")?.focus({ preventScroll: true });
  }
}

export function showError(msg) {
  const page = pages[cur];
  page.querySelector(":scope > .page-error")?.remove();
  const note = document.createElement("div");
  note.className = "note bad page-error";
  note.setAttribute("role", "alert");
  note.innerHTML = '<svg class="ic" aria-hidden="true"><use href="assets/icons.svg#circle-x"/></svg><span></span>';
  note.querySelector("span").textContent = msg;
  page.prepend(note);
  note.scrollIntoView({ block: "nearest", behavior: reduceMotion.matches ? "auto" : "smooth" });
}

ready().then(
  () => {
    document.getElementById("loadbar").hidden = true;
    document.getElementById("next1").disabled = false;
  },
  (err) => {
    const bar = document.getElementById("loadbar");
    bar.classList.add("bad");
    bar.querySelector("p").innerHTML = '<svg class="ic" aria-hidden="true"><use href="assets/icons.svg#circle-x"/></svg><span></span>';
    bar.querySelector("span").textContent = err.message;
  },
);

if (AUTHOR) {
  document.getElementById("author").textContent = AUTHOR;
  document.getElementById("footer").hidden = false;
}

go(0);
