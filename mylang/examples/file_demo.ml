// file_demo.ml  —  mylang v0.6.0
// Demonstrates file.* namespace — read, write, append, list, delete.

print("=== FILE NAMESPACE DEMO ===");
print("");

// Write a file
let path = "output/demo_log.txt";
file.mkdir("output");
file.write(path, "Pacer + mylang v0.6.0\n");
file.append(path, "Line 2: file operations work!\n");
file.append(path, "Line 3: this was appended.\n");

// Read it back
let contents = file.read(path);
print("File contents:");
print(contents);

// Check existence
print("File exists: " + str(file.exists(path)));
print("Missing file: " + str(file.exists("does_not_exist.txt")));

// List directory
let files = file.list("output");
print("Files in output/: " + str(files));

// Copy it
file.copy(path, "output/demo_log_backup.txt");
print("Backup created: " + str(file.exists("output/demo_log_backup.txt")));

// Clean up
file.delete("output/demo_log_backup.txt");
print("Backup deleted. Remaining: " + str(file.list("output")));

print("");
print("Done.");
