# csvdiff-cli

A command-line tool to compare two CSV files and output human-readable diffs with column-level granularity.

---

## Installation

```bash
pip install csvdiff-cli
```

Or install from source:

```bash
git clone https://github.com/yourname/csvdiff-cli.git
cd csvdiff-cli
pip install .
```

---

## Usage

```bash
csvdiff <file1.csv> <file2.csv> [OPTIONS]
```

### Example

```bash
csvdiff old_data.csv new_data.csv --key id
```

**Output:**

```
Row 3 | id=1042
  ~ email:  alice@old.com  →  alice@new.com
  ~ status: active         →  inactive

Row 7 | id=2089
  + (row added)

Row 12 | id=3301
  - (row removed)
```

### Options

| Flag | Description |
|------|-------------|
| `--key` | Column(s) to use as the row identifier (default: row index) |
| `--ignore` | Comma-separated list of columns to exclude from comparison |
| `--output` | Output format: `text` (default), `json`, or `csv` |
| `--no-color` | Disable colored terminal output |

---

## Requirements

- Python 3.8+
- No external dependencies (uses standard library only)

---

## License

This project is licensed under the [MIT License](LICENSE).