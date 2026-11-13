const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => Array.from(document.querySelectorAll(selector));

const letters = "ᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴘǫʀꜱᴛᴜᴠᴡxʏᴢ";

const tools = {
  video: { title: "ᴠɪᴅᴇᴏ ᴅᴏᴡɴʟᴏᴀᴅᴇʀ", hint: "ꜱᴀᴠᴇ ᴀ ᴠɪᴅᴇᴏ ɪɴ ᴛʜᴇ ʙᴇꜱᴛ ǫᴜᴀʟɪᴛʏ" },
  audio: { title: "ᴀᴜᴅɪᴏ ᴇxᴛʀᴀᴄᴛᴏʀ", hint: "ᴘᴜʟʟ ᴛʜᴇ ꜱᴏᴜɴᴅ ᴏᴜᴛ ᴏꜰ ᴀ ᴘᴏꜱᴛ" },
  image: { title: "ɪᴍᴀɢᴇ ꜱᴀᴠᴇʀ", hint: "ꜱᴀᴠᴇ ᴘʜᴏᴛᴏꜱ ɪɴ ᴏʀɪɢɪɴᴀʟ ǫᴜᴀʟɪᴛʏ" },
  slideshow: { title: "ꜱʟɪᴅᴇꜱʜᴏᴡ", hint: "ꜱᴀᴠᴇ ᴘʜᴏᴛᴏ ᴄᴀʀᴏᴜꜱᴇʟꜱ" },
  montage: { title: "ᴛɪᴋᴛᴏᴋ ᴍᴏɴᴛᴀɢᴇ", hint: "ᴛᴜʀɴ ᴀ ᴘʜᴏᴛᴏ ᴘᴏꜱᴛ ᴀɴᴅ ɪᴛꜱ ᴍᴜꜱɪᴄ ɪɴᴛᴏ ᴀɴ ᴍᴘ4" }
};

const views = ["home", "batch", "history", "favorites", "sites", "faq", "contact"];

const catalog = { categories: {}, names: {}, formats: {} };
const state = { fmt: "video", batchFmt: "video", pending: null, ticker: null, progress: 0, timer: null };

function smallcaps(text) {
  return String(text).toLowerCase().replace(/[a-z]/g, (char) => letters[char.charCodeAt(0) - 97]);
}

function el(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

function safe(url) {
  return /^(https?:\/\/|\/api\/file\/)/.test(url);
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

const store = {
  read(key) {
    try {
      return JSON.parse(localStorage.getItem(key)) || [];
    } catch {
      return [];
    }
  },
  write(key, value) {
    try {
      localStorage.setItem(key, JSON.stringify(value));
    } catch {
      return;
    }
  }
};

async function call(url, options) {
  try {
    const response = await fetch(url, options);
    return await response.json();
  } catch {
    return { status: "error", message: "Network error. Try again." };
  }
}

function pull(url, fmt) {
  return call("/api/fetch", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url, fmt })
  });
}

function remember(url, fmt, name) {
  const entries = store.read("history").filter((entry) => !(entry.url === url && entry.fmt === fmt));
  entries.unshift({ url, fmt, name, time: Date.now() });
  store.write("history", entries.slice(0, 50));
}

function isFavorite(url, fmt) {
  return store.read("favorites").some((entry) => entry.url === url && entry.fmt === fmt);
}

function toggleFavorite(url, fmt, name) {
  const entries = store.read("favorites");
  const kept = entries.filter((entry) => !(entry.url === url && entry.fmt === fmt));
  if (kept.length === entries.length) kept.unshift({ url, fmt, name, time: Date.now() });
  store.write("favorites", kept);
  return kept.length !== entries.length;
}

function reopen(url, fmt, auto) {
  state.pending = { url, fmt, auto };
  location.hash = "#/" + fmt;
}

function listEntries(container, entries, empty) {
  container.replaceChildren();
  if (!entries.length) {
    container.append(el("div", "empty", empty));
    return;
  }
  entries.forEach((entry) => {
    const row = el("div", "row");
    const text = el("div", "grow");
    text.append(el("strong", "", `${entry.name || "Link"} · ${smallcaps(entry.fmt)}`), el("small", "", entry.url));
    const again = el("button", "text", "ᴀɢᴀɪɴ");
    again.type = "button";
    again.addEventListener("click", () => reopen(entry.url, entry.fmt, false));
    row.append(text, again);
    container.append(row);
  });
}

function renderSites() {
  const names = Object.keys(catalog.names);
  $("#sitecount").textContent = names.length ? smallcaps(`${names.length} sites across ${Object.keys(catalog.categories).length} groups`) : "";
  const holder = $("#sitelist");
  holder.replaceChildren();
  Object.entries(catalog.categories).forEach(([category, members]) => {
    const card = el("div", "list glass");
    const title = el("div", "row");
    title.append(el("h2", "grow", smallcaps(category)), el("span", "mute", String(members.length)));
    card.append(title);
    members.forEach((platform) => {
      const row = el("div", "row");
      const chips = el("div", "chips");
      (catalog.formats[platform] || []).forEach((fmt) => chips.append(el("span", "", smallcaps(fmt))));
      row.append(el("span", "grow", catalog.names[platform] || platform), chips);
      card.append(row);
    });
    holder.append(card);
  });
}

function toolHint(name) {
  const count = Object.values(catalog.formats).filter((list) => list.includes(name)).length;
  return tools[name].hint + (count ? " · " + smallcaps(`${count} sites`) : "");
}

function renderTool(name) {
  state.fmt = name;
  $("#tooltitle").textContent = tools[name].title;
  $("#toolhint").textContent = toolHint(name);
  $("#toolnote").replaceChildren();
  $("#toollink").value = "";
  $("#loader").hidden = true;
  $("#result").hidden = true;
  if (state.pending && state.pending.fmt === name) {
    const { url, auto } = state.pending;
    state.pending = null;
    $("#toollink").value = url;
    if (auto) grab(url, name);
  }
}

function route() {
  const name = location.hash.replace("#/", "") || "home";
  const key = tools[name] ? "tool" : views.includes(name) ? name : "home";
  $$(".view").forEach((view) => view.classList.toggle("on", view.dataset.view === key));
  const tab = key === "batch" ? "tool" : key === "favorites" ? "history" : key;
  $$(".tabs a").forEach((link) => link.classList.toggle("on", link.dataset.tab === tab));
  $$(".drawer .item").forEach((link) => link.classList.toggle("on", link.getAttribute("href") === "#/" + name));
  document.title = smallcaps(key === "tool" ? tools[name].title : name) + " · ᴍᴇᴅɪᴀ ꜱᴀᴠᴇʀ";
  if (key === "tool") renderTool(name);
  if (key === "home") listEntries($("#recent"), store.read("history").slice(0, 3), "ɴᴏᴛʜɪɴɢ ʏᴇᴛ");
  if (key === "history") listEntries($("#historylist"), store.read("history"), "ɴᴏ ᴅᴏᴡɴʟᴏᴀᴅꜱ ʏᴇᴛ");
  if (key === "favorites") listEntries($("#favoritelist"), store.read("favorites"), "ᴛᴀᴘ ᴛʜᴇ ꜱᴛᴀʀ ᴏɴ ᴀ ʀᴇꜱᴜʟᴛ ᴛᴏ ꜱᴀᴠᴇ ɪᴛ ʜᴇʀᴇ");
  if (key === "sites") renderSites();
  closeDrawer();
  window.scrollTo(0, 0);
}

function setStep(index) {
  $$("#loader .step").forEach((step, position) => {
    step.className = "step" + (position < index ? " done" : position === index ? " active" : "");
  });
}

function paint() {
  $("#bar").style.width = state.progress + "%";
  $("#percent").textContent = Math.round(state.progress) + "%";
}

function begin() {
  clearInterval(state.ticker);
  state.progress = 0;
  paint();
  setStep(1);
  $("#result").hidden = true;
  $("#loader").hidden = false;
  state.ticker = setInterval(() => {
    state.progress += (92 - state.progress) * 0.06;
    if (state.progress > 40) setStep(2);
    paint();
  }, 200);
}

async function finish() {
  clearInterval(state.ticker);
  state.progress = 100;
  setStep(3);
  paint();
  await sleep(450);
  $("#loader").hidden = true;
}

function showResult(data, url) {
  const box = $("#result");
  box.replaceChildren();
  const top = el("div", "row");
  const text = el("div", "grow");
  text.append(el("strong", "", `${data.name} · ${smallcaps(data.fmt)}`), el("small", "", `ʀᴇᴀᴅʏ ɪɴ ${data.speed}ꜱ`));
  const star = el("button", "round", isFavorite(url, data.fmt) ? "★" : "☆");
  star.type = "button";
  star.setAttribute("aria-label", "Toggle favorite");
  star.addEventListener("click", () => {
    star.textContent = toggleFavorite(url, data.fmt, data.name) ? "★" : "☆";
  });
  top.append(text, star);
  const actions = el("div", "stack");
  data.items.filter((item) => safe(item.url)).forEach((item, index) => {
    const link = el("a", "btn " + (index ? "ghost" : "accent"), "ᴅᴏᴡɴʟᴏᴀᴅ " + smallcaps(item.quality));
    link.href = item.url;
    link.target = "_blank";
    link.rel = "noopener";
    link.setAttribute("download", "");
    actions.append(link);
  });
  box.append(top, actions);
  box.hidden = false;
}

async function grab(url, fmt) {
  const note = $("#toolnote");
  const go = $("#toolgo");
  go.disabled = true;
  note.replaceChildren();
  begin();
  const data = await pull(url, fmt);
  await finish();
  go.disabled = false;
  if (data.status !== "success") {
    note.textContent = data.message;
    return;
  }
  remember(url, fmt, data.name);
  showResult(data, url);
}

async function inspect(value, note, fmt) {
  const data = await call("/api/detect?url=" + encodeURIComponent(value));
  note.replaceChildren();
  if (data.status !== "success") {
    note.textContent = smallcaps("unsupported or invalid link");
    return;
  }
  const badge = el("span", "badge");
  badge.append(el("span", "live"), document.createTextNode(smallcaps(data.name) + " " + smallcaps("detected")));
  note.append(badge);
  if (fmt && !data.formats.includes(fmt)) {
    note.append(document.createTextNode(" · " + smallcaps("try") + " "));
    data.formats.filter((option) => tools[option]).forEach((option) => {
      const link = el("a", "", smallcaps(option));
      link.href = "#/" + option;
      note.append(link);
    });
  }
}

function watch(input, note, pick) {
  input.addEventListener("input", () => {
    clearTimeout(state.timer);
    note.replaceChildren();
    const value = input.value.trim();
    if (value) state.timer = setTimeout(() => inspect(value, note, pick()), 350);
  });
}

async function homeSubmit(event) {
  event.preventDefault();
  const note = $("#homenote");
  const value = $("#homelink").value.trim();
  note.textContent = "";
  const data = await call("/api/detect?url=" + encodeURIComponent(value));
  if (data.status !== "success") {
    note.textContent = smallcaps("unsupported or invalid link");
    return;
  }
  const options = data.formats.filter((option) => tools[option]);
  const fmt = options.includes("video") ? "video" : options[0];
  if (!fmt) {
    note.textContent = smallcaps("no tool for this link");
    return;
  }
  reopen(value, fmt, true);
}

function batchRow(url) {
  const row = el("div", "row");
  const text = el("div", "grow");
  const status = el("span", "state", "ǫᴜᴇᴜᴇᴅ");
  text.append(el("strong", "", url), status);
  const slot = el("div");
  row.append(text, slot);
  $("#batchlist").append(row);
  return { status, slot };
}

async function batchSubmit(event) {
  event.preventDefault();
  const lines = $("#batchlinks").value.split("\n").map((line) => line.trim()).filter(Boolean).slice(0, 20);
  const go = $("#batchgo");
  const list = $("#batchlist");
  go.disabled = true;
  list.replaceChildren();
  list.hidden = false;
  const rows = lines.map(batchRow);
  for (let index = 0; index < lines.length; index += 1) {
    const { status, slot } = rows[index];
    status.className = "state";
    status.textContent = "ᴡᴏʀᴋɪɴɢ";
    let data = await pull(lines[index], state.batchFmt);
    while (data.wait) {
      status.textContent = smallcaps(`waiting ${data.wait}s`);
      await sleep(data.wait * 1000);
      data = await pull(lines[index], state.batchFmt);
    }
    const first = data.status === "success" ? data.items.find((item) => safe(item.url)) : null;
    if (!first) {
      status.className = "state bad";
      status.textContent = data.message || "No media found.";
      continue;
    }
    status.className = "state ok";
    status.textContent = smallcaps(`${data.name} ready`);
    const link = el("a", "btn accent", "ꜱᴀᴠᴇ");
    link.href = first.url;
    link.target = "_blank";
    link.rel = "noopener";
    link.setAttribute("download", "");
    slot.append(link);
    remember(lines[index], state.batchFmt, data.name);
  }
  go.disabled = false;
}

function openDrawer() {
  $("#drawer").classList.add("on");
  $("#scrim").classList.add("on");
}

function closeDrawer() {
  $("#drawer").classList.remove("on");
  $("#scrim").classList.remove("on");
}

function boot() {
  if (sessionStorage.getItem("seen")) {
    $("#splash").classList.add("gone");
  } else {
    sessionStorage.setItem("seen", "1");
    setTimeout(() => $("#splash").classList.add("gone"), 3400);
  }
  $("#open").addEventListener("click", openDrawer);
  $("#close").addEventListener("click", closeDrawer);
  $("#scrim").addEventListener("click", closeDrawer);
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") closeDrawer();
  });
  $("#homeform").addEventListener("submit", homeSubmit);
  $("#toolform").addEventListener("submit", (event) => {
    event.preventDefault();
    grab($("#toollink").value.trim(), state.fmt);
  });
  $("#batchform").addEventListener("submit", batchSubmit);
  $("#batchfmt").addEventListener("click", (event) => {
    const button = event.target.closest("button");
    if (!button) return;
    state.batchFmt = button.dataset.fmt;
    $$("#batchfmt button").forEach((item) => item.classList.toggle("on", item === button));
  });
  $("#clearhistory").addEventListener("click", () => {
    store.write("history", []);
    route();
  });
  watch($("#toollink"), $("#toolnote"), () => state.fmt);
  watch($("#homelink"), $("#homenote"), () => null);
  window.addEventListener("hashchange", route);
  call("/api/sites").then((data) => {
    if (data.categories) {
      catalog.categories = data.categories;
      catalog.names = data.names;
      catalog.formats = data.formats;
      const name = location.hash.replace("#/", "");
      if (tools[name]) $("#toolhint").textContent = toolHint(name);
      if (name === "sites") renderSites();
    }
  });
  route();
}

boot();
