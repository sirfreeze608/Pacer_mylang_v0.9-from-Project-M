// payroll.ml — a small business workload   (v0.9.0)
//
// Combines fixed-width records, exact decimals, evaluate, perform,
// compute, and sequential file I/O — the COBOL workload, in mylang.

record Employee {
    emp_no pic 9(4);
    name   pic x(20);
    rate   pic 9(5)v99;      // hourly rate
    hours  pic 9(3);
    gross  pic 9(7)v99;
    status pic x(1);
    cond active   for status == "A";
    cond on_leave for status == "L";
}

fn new_employee(no, name, rate, hours, status) {
    let e = Employee();
    e.emp_no = no;
    e.name   = name;
    e.rate   = rate;
    e.hours  = hours;
    e.status = status;
    return e;
}

let staff = [
    new_employee(1001, "Ada Lovelace",  dec("42.50"), 40, "A"),
    new_employee(1002, "Grace Hopper",  dec("55.00"), 38, "A"),
    new_employee(1003, "Alan Turing",   dec("38.75"),  0, "L")
];

// ── Compute gross pay for every employee ────────────────────────────────────
perform varying i from 0 by 1 until i >= len(staff) {
    let e = staff[i];
    compute e.gross = e.rate * e.hours;
}

// ── Write the fixed-width payroll file ──────────────────────────────────────
file.mkdir("output");
file.write_records("output/payroll.dat", staff);

let count = file.record_count("output/payroll.dat", Employee);
print(`Wrote ${count} records to output/payroll.dat`);
print(`Record width: ${len(staff[0].pack())} bytes`);

// ── Read it back and report ─────────────────────────────────────────────────
let loaded = file.read_records("output/payroll.dat", Employee);
let total  = dec("0");

for (e in loaded) {
    evaluate e.status {
        when "A" {
            print(`${e.emp_no}  ${e.name.trim()}  ${e.gross}  (active)`);
            total = total + e.gross;
        }
        when "L" {
            print(`${e.emp_no}  ${e.name.trim()}  on leave`);
        }
        when other {
            print(`${e.emp_no}  ${e.name.trim()}  unknown status`);
        }
    }
}

print(`Total gross payroll: ${total}`);

// Conditions are live views over the record's fields.
let first = loaded[0];
print(`First employee active?   ${first.active}`);
print(`First employee on leave? ${first.on_leave}`);

// tidy up
file.delete("output/payroll.dat");
print("Done.");
