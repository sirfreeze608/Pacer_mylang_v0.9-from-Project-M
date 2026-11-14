// new_syntax.ml  —  mylang v0.6.0
// Template literals, try/catch/throw, and import.

print("=== v0.6.0 SYNTAX DEMO ===");
print("");

// ── Template literals ──────────────────────────────────────────────────────
let name    = "mylang";
let version = "0.6.0";
let pi      = 3.14159;

print(`Welcome to ${name} v${version}!`);
print(`PI to 2 decimal places is approximately ${round(pi, 2)}.`);

let items = [10, 20, 30];
for (i in range(0,3,1)) {
    print(`  items[${i}] = ${items[i]}`);
}

// ── try / catch / throw ────────────────────────────────────────────────────
print("");
print("-- Error handling --");

fn safe_divide(a, b) {
    if (b == 0) {
        throw `Division by zero: ${a} / ${b}`;
    }
    return a / b;
}

try {
    let result = safe_divide(10, 2);
    print(`10 / 2 = ${result}`);
} catch(e) {
    print(`Error: ${e}`);
}

try {
    let bad = safe_divide(5, 0);
    print(bad);
} catch(e) {
    print(`Caught: ${e}`);
}

// ── Chained template + math ────────────────────────────────────────────────
print("");
print("-- Physics calculations --");

let mass     = 70;       // kg
let velocity = 15;       // m/s
let ke       = 0.5 * mass * velocity * velocity;
let height   = 10;       // m
let g        = 9.81;
let pe       = mass * g * height;

print(`Object: m=${mass}kg, v=${velocity}m/s, h=${height}m`);
print(`Kinetic energy:   ${ke} J`);
print(`Potential energy: ${round(pe, 2)} J`);
print(`Total mechanical: ${round(ke + pe, 2)} J`);

print("");
print("Done.");
