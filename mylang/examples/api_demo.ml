// api_demo.ml  —  mylang v0.8.0
// Fetch real data from an API using http.* + json.* + time.*
// Requires an internet connection.

print("=== HTTP + JSON API DEMO ===");
print("");

// ── Fetch GitHub repo info ─────────────────────────────────────────────────
try {
    let repo = http.get_json("https://api.github.com/repos/python/cpython");
    print(`Repo:     ${repo["full_name"]}`);
    print(`Stars:    ${repo["stargazers_count"]}`);
    print(`Language: ${repo["language"]}`);
} catch(e) {
    print(`Request failed (offline?): ${e}`);
}

print("");

// ── POST JSON to an echo service ───────────────────────────────────────────
try {
    let payload = {"tool": "mylang", "version": 0.7};
    let resp = http.post("https://httpbin.org/post", payload);
    print(`POST status: ${resp["status"]}`);
    let body = json.parse(resp["body"]);
    print(`Echoed back: ${body["data"]}`);
} catch(e) {
    print(`POST failed (offline?): ${e}`);
}

print("");

// ── Timing the requests ────────────────────────────────────────────────────
let start = time.now();
time.sleep(0.2);
print(`Elapsed: ${round(time.elapsed(start), 2)}s`);
print(`Today is ${time.today()}`);
print(`Timestamp: ${time.format(time.now(), "%Y-%m-%d %H:%M")}`);
