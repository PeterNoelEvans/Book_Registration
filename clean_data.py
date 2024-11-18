# Clean up students.txt to preserve both full name and nickname
with open('students.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Clean student names while keeping nicknames
clean_students = []
for line in lines:
    # Split on tab to separate full name and nickname
    parts = line.strip().split('\t')
    if len(parts) == 2:
        full_name = parts[0].strip()
        nickname = parts[1].strip()
        # Combine with a special separator (we'll use '|' to split later)
        clean_students.append(f"{full_name}|{nickname}")

with open('students.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(clean_students))

print("Cleaned students.txt")
