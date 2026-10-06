const fromSel = document.getElementById("from");
const toSel = document.getElementById("to");
const modeSel = document.getElementById("mode");
const form = document.getElementById("form");
const result = document.getElementById("result");
const history = document.getElementById("history");

async function getJSON(url) {
    const res = await fetch(url);
    const data = await res.json();
    if (!res.ok) {
        throw new Error(data.error || "Something went wrong");
    }
    return data;
}

function line(text, cls) {
    const p = document.createElement("p");
    p.textContent = text;
    if (cls) {
        p.className = cls;
    }
    return p;
}

async function loadAirports() {
    const airports = await getJSON("/api/airports");
    for (const a of airports) {
        for (const sel of [fromSel, toSel]) {
            const opt = document.createElement("option");
            opt.value = a.code;
            opt.textContent = a.name + " (" + a.code + ")";
            sel.appendChild(opt);
        }
    }
    toSel.selectedIndex = 1;
}

function showRoute(data) {
    result.replaceChildren();
    if (!data.found) {
        result.appendChild(line("No route found.", "error"));
        return;
    }
    result.appendChild(line(data.names.join(" → "), "route"));
    result.appendChild(line(
        "Layovers: " + data.layovers +
        " · Price: ₹" + data.total_price +
        " · Time: " + data.total_minutes + " min"
    ));
        if (data.cached) {
        result.appendChild(line("⚡ Served from cache"));
    }
    const ul = document.createElement("ul");
    for (const leg of data.legs) {
        const li = document.createElement("li");
        li.textContent = leg.from + " → " + leg.to + ": ₹" + leg.price + ", " + leg.minutes + " min";
        ul.appendChild(li);
    }
    result.appendChild(ul);
}

async function loadHistory() {
    const rows = await getJSON("/api/searches?limit=5");
    history.replaceChildren();
    if (rows.length === 0) {
        const li = document.createElement("li");
        li.textContent = "No searches yet.";
        history.appendChild(li);
        return;
    }
    for (const r of rows) {
        const li = document.createElement("li");
        li.textContent = r.origin + " → " + r.destination + " · " + r.mode +
            " · " + (r.found ? "found" : "no route");
        history.appendChild(li);
    }
}

form.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (fromSel.value === toSel.value) {
        result.replaceChildren(line("Please pick two different airports.", "error"));
        return;
    }
    const url = "/api/routes?from=" + encodeURIComponent(fromSel.value) +
        "&to=" + encodeURIComponent(toSel.value) +
        "&mode=" + encodeURIComponent(modeSel.value);
    try {
        showRoute(await getJSON(url));
        await loadHistory();
    } catch (error) {
        result.replaceChildren(line(error.message, "error"));
    }
});

loadAirports().then(loadHistory).catch((error) => {
    result.replaceChildren(line("Could not load data: " + error.message, "error"));
});

const find = document.getElementById("find");
const suggestions = document.getElementById("suggestions");

find.addEventListener("input", async () => {
    const q = find.value.trim();
    suggestions.replaceChildren();
    if (!q) {
        return;
    }
    try {
        const items = await getJSON("/api/suggest?q=" + encodeURIComponent(q));
        for (const a of items) {
            const li = document.createElement("li");
            const btn = document.createElement("button");
            btn.type = "button";
            btn.textContent = a.name + " (" + a.code + ")";
            btn.addEventListener("click", () => {
                fromSel.value = a.code;
                suggestions.replaceChildren();
                find.value = "";
            });
            li.appendChild(btn);
            suggestions.appendChild(li);
        }
    } catch (error) {
        suggestions.replaceChildren();
    }
});