
---
## The `process()` Function Line-by-Line Breakdown:

### **Line 1: Function Signature**
```python
def process(self, filepath):
```
- `def process` - defines the method name
- `self` - required for all class methods (refers to this specific CSVRepairTool instance)
- `filepath` - the parameter users pass in (path to CSV file)

**This is required by BaseTool** - remember `base_tool.py` requires all tools to implement `process()`

---

### **Lines 2-12: Docstring**
```python
"""
Repair CSV structure issues before pandas parsing.
...
"""
```
- Explains what the function does
- Documents the approach (two-layer detection)
- Lists Args and Returns
- **Good practice:** Every function should have a docstring explaining its purpose

---

### **Line 13: Path Conversion**
```python
filepath = Path(filepath)
```
**Why?** User might pass in a string `"data.csv"` or a Path object. This ensures it's ALWAYS a Path object.

**Path vs string:**
```python
# String - old way:
file = "data.csv"
size = os.path.getsize(file)  # Different function for each operation

# Path object - modern way:
file = Path("data.csv")
size = file.stat().st_size    # Methods directly on the object
exists = file.exists()
parent = file.parent
```

**Path objects are cleaner and more readable.**

---

### **Line 15: Logging Start**
```python
self.logger.info("Starting CSV structure repair...")
```
- `self.logger` - the logger we set up in `__init__()` (inherited from BaseTool)
- `info()` - info-level message (not error, not warning, just informational)
- **Why log?** So users can see progress, and we can debug issues

**Example output:**
```
[CSV Repair Tool] Starting CSV structure repair...
```

---

### **Lines 17-19: Read File**
```python
# Read the raw CSV content
with open(filepath, 'r', encoding=DEFAULT_ENCODING) as f:
    lines = f.readlines()
```

**Breaking this down:**

**`with open(...) as f:`** - Context manager (automatically closes file when done)
- Old way: `f = open(...); data = f.read(); f.close()` ← Easy to forget close()
- New way: `with open(...) as f:` ← Automatically closes, even if error occurs

**`filepath`** - the Path object we're reading

**`'r'`** - Read mode (not write 'w' or append 'a')

**`encoding=DEFAULT_ENCODING`** - From config.py, this is 'utf-8'
- **Why specify?** Different systems have different defaults (Windows uses cp1252, Mac/Linux use utf-8)
- Explicit encoding prevents "weird characters" bugs

**`f.readlines()`** - Reads ALL lines into a list, keeping `\n` at end of each line
```python
# File content:
# Order_ID,Name
# 1001,John

# After readlines():
lines = ['Order_ID,Name\n', '1001,John\n']
```

**Alternative methods:**
- `f.read()` - Returns entire file as single string
- `f.readline()` - Returns ONE line at a time
- `f.readlines()` - Returns list of ALL lines ← **We use this because we need to work with each line separately**

---

### **Lines 21-23: Empty File Check**
```python
if not lines:
    self.logger.error("CSV file is empty")
    return None
```

**`if not lines:`** - If list is empty (no lines in file)
- Empty list is "falsy" in Python: `bool([]) == False`

**Why check?** If the file is empty, there's nothing to repair. Fail gracefully.

**`return None`** - Signals failure to the caller
- Remember `base_tool.py`'s `run()` method checks if result is None
- None means "something went wrong" vs actual data means "success"

---

### **Lines 25-27: Detect Issues**
```python
# Detect issues using two-layer detection
self.logger.info("Detecting field mismatches...")
issues = self._detect_field_mismatches(lines)
```

**`self._detect_field_mismatches(lines)`** - Call our "master hunter" function
- Pass in the list of lines
- Returns list of issues: `[(line_num, line_content, issue_type), ...]`
- Could be empty list `[]` if no issues found

**Why separate function?** 
- Keeps `process()` clean and readable
- Detection logic is complex - deserves its own function
- Can test detection separately

---

### **Lines 29-42: Conditional Repair**
```python
# Interactive repair if issues found
if issues:
    self.logger.info(f"Found {len(issues)} lines needing repair")
    lines = self._interactive_repair(lines, issues)

    if lines is None:
        self.logger.error("User cancelled repair process")
        return None
    
    self.repairs_made = len(issues)
else:
    self.logger.info("No field mismatches detected! CSV structure looks good.")
```

**Breaking this down:**

**`if issues:`** - If list has any items
- Empty list is falsy: `bool([]) == False`
- List with items is truthy: `bool([item1, item2]) == True`

**`f"Found {len(issues)} lines needing repair"`** - f-string with variable
- `len(issues)` - how many issues found
- Example: "Found 4 lines needing repair"

**`lines = self._interactive_repair(lines, issues)`** - Call repair function
- Pass in original lines AND the issues we found
- Returns MODIFIED lines (user has fixed them)
- **OR** returns None if user cancels

**`if lines is None:`** - Check if user cancelled
- Use `is None` not `== None` (Python best practice)
- If cancelled, log error and return None (propagate the cancellation)

**`self.repairs_made = len(issues)`** - Track statistics
- Remember in `__init__()` we created `self.repairs_made = 0`
- Now we update it with actual count
- **Why?** For logging/reporting at the end

**`else:`** - No issues found
- Log happy message
- Continue to return the unchanged content

---

### **Lines 44-45: Rejoin Lines**
```python
# Join lines back into single string
repaired_content = ''.join(lines)
```

**Why join?**
- `lines` is a list: `['Order_ID,Name\n', '1001,John\n']`
- We need a single string for pandas to parse
- `''.join(list)` - joins list items with empty string between them

**Example:**
```python
lines = ['Hello\n', 'World\n']
result = ''.join(lines)
# result = 'Hello\nWorld\n'
```

**Why not `' '.join(lines)`?** That would add a SPACE between lines:
```python
'Hello\n World\n'  # ← Extra space before World!
```

**The newlines (`\n`) are already in each line** from `readlines()`, so we just concatenate with empty string.

---

### **Lines 47-48: Success Log & Return**
```python
self.logger.info("CSV structure repair complete")
return repaired_content
```

**Log completion** - shows user we're done

**`return repaired_content`** - Return the fixed CSV as a string
- This string will be passed to pandas for parsing
- Or written to a file
- Or used by another tool

---

### Summary of Data Flow:

```
1. filepath (string or Path)
   ↓
2. Path(filepath) → Path object
   ↓
3. open() + readlines() → list of lines
   ↓
4. _detect_field_mismatches() → list of issues
   ↓
5. _interactive_repair() → modified list of lines (or None)
   ↓
6. ''.join() → single string
   ↓
7. return → CSV content ready for pandas
```

---

### Key Python Concepts Used:

1. **Context managers** (`with open() as f:`)
2. **Path objects** (modern file handling)
3. **List operations** (`readlines()`, `join()`)
4. **f-strings** (`f"Found {count}"`)
5. **Truthiness** (`if lines:`, `if issues:`)
6. **None checking** (`if result is None:`)
7. **Method chaining** (`self._detect()`, `self._repair()`)
8. **Early returns** (return None on error)

---

## The `_count_fields_respecting_quotes()` Function Line-by-Line Breakdown:

This is a **state machine** - a program that tracks what "state" it's in as it processes data.

### The Two States:
1. **Outside quotes** - commas are delimiters
2. **Inside quotes** - commas are just regular characters

### Visual Example:

```
david,"2,499.99",cancelled
^     ^         ^
|     |         |
State: OUT → IN → OUT

Position 1-5 (david): State = OUT
Position 6 (,): State = OUT → COUNT IT (field 2 starts)
Position 7 ("): State changes to IN
Position 8-15 (2,499.99): State = IN
Position 10 (,): State = IN → SKIP IT (it's data, not delimiter)
Position 16 ("): State changes to OUT
Position 17 (,): State = OUT → COUNT IT (field 3 starts)
Position 18-26 (cancelled): State = OUT

Result: 3 fields
```

### Why Start at 1?
- Empty line = 1 field (the empty field itself)
- `a` = 1 field
- `a,b` = 1 field + 1 comma = 2 fields
- `a,b,c` = 1 field + 2 commas = 3 fields

### The Toggle Trick:
```python
inside_quotes = not inside_quotes
```
This flips True/False like a light switch:
- Was False → becomes True (entering quotes)
- Was True → becomes False (exiting quotes)

### State Machine Pattern:
This pattern appears everywhere in programming:
- Parsers (reading code)
- Network protocols (connected/disconnected)
- Game states (menu/playing/paused)

---

## The `_detect_field_mismatches()` Function Line-by-Line Breakdown:

### Overall Structure:
This function orchestrates our two-layer detection system - it's the "master hunter" that calls both helper functions.

---

### Line 13-14: Minimum Line Check
```python
if len(lines) < 2:
    return []
```
- Need at least 2 lines: header + 1 data line
- Less than 2? Nothing to check, return empty list

---

### Lines 16-18: Get Expected Field Count
```python
header = lines[0]
expected_fields = self._count_fields_respecting_quotes(header)
```
- `lines[0]` = first line = header
- Use our smart counter (respects quotes) on header
- This is our "truth" - all other lines should match this count

**Example:**
```
Header: Order_ID,Name,Price
expected_fields = 3
```

---

### Line 20: Log Header Info
```python
self.logger.info(f"Header has {expected_fields} fields")
```
Shows user what we're checking against.

---

### Line 22: Initialize Issues List
```python
issues = []
```
Will collect tuples of problems found.

---

### Line 25: Loop Through Data Lines
```python
for i, line in enumerate(lines[1:], start=2):
```

**Breaking this down:**

**`lines[1:]`** - Slice starting at index 1 (skip header)
- `lines[0]` = header
- `lines[1:]` = everything AFTER header

**`enumerate()`** - Gives us both index AND value
```python
for index, value in enumerate(['a', 'b', 'c']):
    # Loop 1: index=0, value='a'
    # Loop 2: index=1, value='b'
```

**`start=2`** - **Why start at 2?**
- `lines[0]` = header (line 1 in file)
- `lines[1]` = first data row (line 2 in file)
- We're looping through `lines[1:]` but want line numbers to match the actual file
- Without `start=2`: first data line would be labeled "line 0" or "line 1"
- With `start=2`: first data line is labeled "line 2" ✓

**Example:**
```
File:
Line 1: Order_ID,Name     ← lines[0] (header, we skip this)
Line 2: 1001,John          ← lines[1] (enumerate gives i=2)
Line 3: 1002,Sarah         ← lines[2] (enumerate gives i=3)

enumerate(lines[1:], start=2):
  i=2, line="1001,John"    ← Matches actual line 2 in file
  i=3, line="1002,Sarah"   ← Matches actual line 3 in file
```

**Why this matters:** When we tell the user "Line 5 has an error", they can find it at line 5 in their file editor.

---

### Lines 27-29: Skip Empty Lines
```python
if not line.strip():
    continue
```
- `line.strip()` removes whitespace
- If nothing left, line was blank
- `continue` = skip to next iteration

---

### Lines 31-34: Layer 1 - Quote Balance Check
```python
if self._has_unbalanced_quotes(line):
    issues.append((i, line.strip(), "Unbalanced quotes"))
    continue
```
- Call our quote checker
- If unbalanced, record the issue
- `continue` = skip Layer 2 (no point counting fields if quotes are broken)

**Why skip Layer 2?** Unbalanced quotes make field counting unreliable.

---

### Lines 36-39: Layer 2 - Field Count Check
```python
field_count = self._count_fields_respecting_quotes(line)
if field_count != expected_fields:
    issues.append((i, line.strip(), f"Has {field_count} fields, expected {expected_fields}"))
```
- Use smart counter (respects quotes)
- Compare to expected count from header
- If mismatch, record it

**Note:** We only reach here if quotes are balanced (Layer 1 passed).

---

### Line 41: Return Results
```python
return issues
```
- List of tuples: `[(line_num, content, description), ...]`
- Empty list if no issues found

---

### Data Flow Summary:
```
1. Get header field count (expected_fields = 3)
2. Loop through each data line:
   a. Check Layer 1: Quotes balanced? → If no, record issue, skip to next line
   b. Check Layer 2: Field count matches? → If no, record issue
3. Return all issues found
```

---

## The `_interactive_repair()` Function Line-by-Line Breakdown:

This function loops through issues and lets the user fix each one interactively.

---

### Lines 11-14: Display Header
```python
print("\n" + "=" * 60)
print("INTERACTIVE REPAIR MODE")
print(f"Found {len(issues)} line(s) with structural issues")
print("=" * 60)
```
- Visual separator for user
- `"=" * 60` creates 60 equal signs
- Shows total issue count upfront

---

### Line 16: Loop Through Issues
```python
for line_num, line_content, issue_desc in issues:
```
- **Tuple unpacking** - each issue is a tuple with 3 values
- Example issue: `(5, "1001,John,$1,299.99", "Has 4 fields, expected 3")`
- Unpacks to: `line_num=5`, `line_content="..."`, `issue_desc="Has 4..."`

---

### Lines 17-18: Show Issue Details
```python
print(f"\nLine {line_num}: {issue_desc}")
print(f"Content: {line_content}")
```
Shows user exactly what's wrong and where.

**Example output:**
```
Line 5: Has 4 fields, expected 3
Content: 1001,John,$1,299.99
```

---

### Lines 20-24: Ask Permission to Fix
```python
should_fix = confirm_action(
    f"Fix line {line_num}?",
    default=True
)
```
- Calls our `confirm_action()` from `user_input.py`
- `default=True` means pressing Enter = yes
- Returns boolean: True or False

---

### Lines 26-28: Handle Skip
```python
if not should_fix:
    self.logger.info(f"Skipping line {line_num}")
    continue
```
- User said "no"
- Log it
- `continue` = skip to next issue in loop

---

### Lines 30-31: Let User Edit
```python
fixed_line = edit_line_interactive(line_content, line_num)
```
- Calls our `edit_line_interactive()` from `user_input.py`
- Shows helper text about common fixes
- Returns edited string OR None if cancelled

---

### Lines 33-41: Handle Cancellation
```python
if fixed_line is None:
    abort = confirm_action(
        "Cancel entire repair process?",
        default=False
    )
    if abort:
        return None
    else:
        continue
```

**User cancelled the edit (Ctrl+C or typed "cancel"):**
- Ask: "Do you want to abort the ENTIRE repair?"
- `default=False` = pressing Enter = continue with other issues
- If abort = True: return None (propagate cancellation upward)
- If abort = False: continue (skip this issue, move to next)

**Why two-step confirmation?** Accidentally hitting Ctrl+C shouldn't abort everything.

---

### Lines 43-45: Apply Fix
```python
lines[line_num - 1] = fixed_line + '\n'
self.logger.info(f"Repaired line {line_num}")
```

**`lines[line_num - 1]`** - Why minus 1?
- `line_num` is human-readable (starts at 1)
- List indices start at 0
- Line 2 in file = `lines[1]`
- Line 5 in file = `lines[4]`

**`fixed_line + '\n'`** - Why add newline?
- `edit_line_interactive()` returns string without newline
- `lines` list expects each line to end with `\n`
- We add it back

**Example:**
```
User edits line 5: "1001,John,$1299.99" (newline removed during edit)
We save: "1001,John,$1299.99\n" (newline added back)
```

---

### Line 47: Return Modified Lines
```python
return lines
```
- Returns the full lines list with user's fixes applied
- OR None if user aborted

---

### Key Concepts:

**Tuple unpacking:**
```python
data = (5, "content", "description")
num, text, desc = data  # Unpack into variables
```

**continue vs return:**
- `continue` = skip to next loop iteration
- `return` = exit function entirely

**Index adjustment:**
- Human line numbers (1, 2, 3...)
- List indices (0, 1, 2...)
- Always: `list_index = line_number - 1`

---

