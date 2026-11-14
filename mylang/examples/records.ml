// records.ml — COBOL-style fixed-width records   (v0.8.0)
//
// `record` + `pic` describe storage exactly like a COBOL DATA DIVISION.
// pack()/unpack() convert to and from fixed-width character records, so
// existing sequential files can be read and written directly.

record Employee {
    name   pic x(30);        // text, 30 characters
    salary pic 9(7)v99;      // 7 integer digits + 2 decimals
    dept   pic x(10) = "SALES";
}

let e = Employee();

e.name   = "Ada Lovelace";
e.salary = dec("5400.50");

print(`Name   : ${e.name.trim()}`);
print(`Salary : ${e.salary}`);
print(`Dept   : ${e.dept.trim()}`);
print(`Fields : ${e.fields().join(",")}`);

// Decimals truncate (not round) when stored in a PIC field.
let raise_amount = dec("123.456");
e.salary = e.salary + raise_amount;
print(`Raised : ${e.salary}`);          // 5523.95 (extra 0.006 truncated)

// Fixed-width serialization: 30 + 9 + 10 = 49 characters.
let line = e.pack();
print(`Packed : ${len(line)} chars`);
print(`Raw    : |${line}|`);

// Round-trip through a "file".
let copy = Employee();
copy.unpack(line);
print(`Copy   : ${copy.name.trim()} / ${copy.salary} / ${copy.dept.trim()}`);

// Signed numeric fields keep their sign character.
record Reading {
    station pic x(4);
    temp    pic s9(3)v9;
}

let r = Reading();
r.station = "KJFK";
r.temp    = dec("-12.3");
let reading_line = r.pack();
print(`Reading: |${reading_line}| (${len(reading_line)} chars)`);

let r2 = Reading();
r2.unpack(reading_line);
print(`Parsed : ${r2.station.trim()} ${r2.temp}`);
