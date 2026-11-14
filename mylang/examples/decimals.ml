// decimals.ml — exact financial arithmetic with dec()   (v0.8.0)
//
// Plain floats are binary fractions: 0.1 + 0.2 == 0.30000000000000004.
// dec() gives exact fixed-point arithmetic for money.

let price    = dec("19.99");
let quantity = 3;
let subtotal = price * quantity;

print(`Unit price  : ${price}`);
print(`Quantity    : ${quantity}`);
print(`Subtotal    : ${subtotal}`);

// Tax at 8.25% — still exact.
let taxRate = dec("0.0825");
let tax     = (subtotal * taxRate).round(2);
print(`Tax (8.25%) : ${tax}`);

let total = subtotal + tax;
print(`Total       : ${total}`);

// Comparisons work across decimals and integers.
print(`Over $50?   : ${total > 50}`);
print(`Type        : ${type(total)}`);

// Explicit rounding, never implicit.
print(`Rounded     : ${dec("2.345").round(2)}`);     // 2.35 (half-up)
print(`Truncated   : ${dec("2.349").truncate(2)}`);  // 2.34

// Decimals refuse to mix silently with floats — that is the point.
// print(total + 1.5);   // RuntimeError: cannot mix decimal with number
