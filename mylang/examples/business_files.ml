// business_files.ml — sequential & fixed-record business file I/O  (v0.9.0)
//
// mylang writes the same fixed-width character records COBOL uses, so
// existing sequential files can be read directly and new ones can be
// produced for downstream systems.

file.mkdir("output");

// ── 1. Fixed-width records ──────────────────────────────────────────────────
record Reading {
    station pic x(4);
    temp    pic s9(3)v9;        // signed, one decimal place
    humidity pic 9(3);
}

let r1 = Reading();
r1.station  = "KJFK";
r1.temp     = dec("-12.3");
r1.humidity = 55;

let r2 = Reading();
r2.station  = "EGLL";
r2.temp     = dec("8.4");
r2.humidity = 81;

file.write_records("output/readings.dat", [r1, r2]);
print(`Record width : ${len(r1.pack())} bytes`);
print(`Record count : ${file.record_count("output/readings.dat", Reading)}`);

let loaded = file.read_records("output/readings.dat", Reading);
for (r in loaded) {
    print(`${r.station.trim()}  ${r.temp}°C  ${r.humidity}%`);
}

// A true fixed-width file (no line separators) is auto-detected by width.
file.write("output/readings.fixed", r1.pack() + r2.pack());
let fixed = file.read_records("output/readings.fixed", Reading);
print(`Fixed-width records: ${len(fixed)}`);

// ── 2. Line-sequential text ─────────────────────────────────────────────────
file.write_lines("output/notes.txt", [
    "Batch 2026-11-13",
    "All readings validated",
    "Ready for transfer"
]);
file.append_line("output/notes.txt", "Signed: operator 7");

let lines = file.read_lines("output/notes.txt");
perform varying i from 0 by 1 until i >= len(lines) {
    print(`${i + 1}. ${lines[i]}`);
}

// ── 3. CSV extracts ─────────────────────────────────────────────────────────
let rows = [
    ["station", "temp", "humidity"],
    ["KJFK", -12.3, 55],
    ["EGLL", 8.4, 81]
];

file.write_csv("output/readings.csv", rows);
let back = file.read_csv("output/readings.csv");
print(`CSV rows: ${len(back)}`);
print(`${back[1][0]} has temp ${back[1][1]}`);

// ── 4. Housekeeping ─────────────────────────────────────────────────────────
print(`Notes file is ${file.size("output/notes.txt")} bytes`);
file.copy("output/readings.dat", "output/readings.bak");
print(`Backup exists: ${file.exists("output/readings.bak")}`);

// Clean up the generated files so the example can run repeatedly.
for (name in ["readings.dat", "readings.fixed", "readings.bak",
              "notes.txt", "readings.csv"]) {
    file.delete("output/" + name);
}

print("Done.");
