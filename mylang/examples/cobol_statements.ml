// cobol_statements.ml — the COBOL-style statement set   (v0.9.0)
//
// Every verb here is a *soft* keyword: `let string = 5;` still works, and
// expressions remain the preferred style. These statements are sugar that
// maps familiar business-programming shapes onto mylang.

print("── evaluate ─────────────────────────────────────────────");

let grade = 87;
evaluate grade {
    when 90 thru 100 { print("A"); }
    when 80 thru 89  { print("B"); }
    when 70 thru 79  { print("C"); }
    when other       { print("Below C"); }
}

// Multi-value arms and the boolean form.
let day = "SAT";
evaluate day {
    when "SAT", "SUN" { print("Weekend"); }
    when other        { print("Weekday"); }
}

let score = 93;
evaluate {
    when score >= 90 { print("Distinction"); }
    when score >= 75 { print("Merit"); }
    when other       { print("Pass"); }
}

print("\n── perform ──────────────────────────────────────────────");

let i = 0;
perform until i >= 3 {
    print(`perform until → ${i}`);
    i = i + 1;
}

perform varying n from 1 by 1 until n > 3 {
    print(`perform varying → ${n}`);
}

perform 2 times { print("perform N times"); }

print("\n── arithmetic verbs ─────────────────────────────────────");

let balance = dec("100.00");
add dec("25.50") to balance;
subtract dec("10.00") from balance;
print(`balance = ${balance}`);            // 115.50

let qty = 3;
multiply qty by 7;                        // literal second → qty is target
print(`qty = ${qty}`);                    // 21

let total = 0;
add 40 to 2 giving total;
print(`add giving → ${total}`);           // 42

let share = 0;
let remainder = 0;
divide 10 by 3 giving share remainder remainder;
print(`10 / 3 = ${share} remainder ${remainder}`);

print("\n── compute ──────────────────────────────────────────────");

let invoice = 0;
compute invoice = dec("19.99") * 3 + dec("4.95");
print(`invoice = ${invoice}`);

record Counter { n pic 9(2); }
let c = Counter();
compute c.n = 99 + 1 on size error { print("Counter overflow — handled"); }
print(`counter still ${c.n}`);

print("\n── string verbs ─────────────────────────────────────────");

let full = "";
string "Ada", " ", "Lovelace" into full;
print(full);

let parts = [];
unstring "red,green,blue" by "," into parts;
print(parts);

let cleaned = "";
inspect "a  b   c" replacing "  " with "_" giving cleaned;
print(cleaned);

let hits = 0;
inspect "banana" tallying "a" giving hits;
print(`a appears ${hits} times`);

print("\n── slices ───────────────────────────────────────────────");

let text = "COBOL workload edition";
print(text[0:5]);          // COBOL
print(text[6:14]);         // workload
print(text[-7:]);          // edition
print([10, 20, 30, 40][1:3]);

print("\n── 88-level conditions ──────────────────────────────────");

record Employee {
    name   pic x(12);
    status pic x(1);
    cond active   for status == "A";
    cond inactive for status == "I";
}

let emp = Employee();
emp.name = "Grace";
emp.status = "A";
print(`active?   ${emp.active}`);
print(`inactive? ${emp.inactive}`);

print("\nDone.");
