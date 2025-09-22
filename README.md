# OFX Normalizer

A small, practical Python tool to clean, fix, and normalize OFX files produced by modern banks (e.g., Sicoob, Nubank, Itaú), making them compatible with legacy personal finance software such as Microsoft Money (discontinued in 2009).

The goal is to adjust the OFX file so it imports correctly without losing financial information, allowing you to keep using legacy software with minimal friction.

## Key Features
- Compatibility-focused normalization for Microsoft Money (tested with OFX 1.02 and 2.0).
- Encoding and headers alignment: outputs CP1252, sets `CHARSET:1252`, `ENCODING:USASCII`, and enforces CRLF line endings.
- Date normalization: removes timezone suffixes from `DTSERVER`, `DTSTART`, `DTEND`, `DTPOSTED` while keeping `yyyymmddhhmmss`.
- Transaction block fixes (`<STMTTRN>`): ensures `<NAME>` appears before `<MEMO>`, adds explicit closing tags, strips ASCII control chars, and applies a safe length cap to `<NAME>`.
- Robust removal of extra blocks: removes only `<BALLIST> ... </BALLIST>` when both tags are present; never touches `<BANKTRANLIST>`.
- Preserves financial integrity: amounts, FITID, and signs are left intact.

## How It Works
The script scans your OFX file and applies conservative, compatibility-driven transformations:
- Reads input using UTF-8/UTF-8-SIG with fallback to CP1252; writes output using CP1252 with CRLF.
- Strips ASCII control characters (except TAB, CR, LF) that break OFX parsers.
- Normalizes date fields by removing timezone trailers (e.g., `[-3:BRT]`).
- Within each `<STMTTRN>` block:
  - Ensures `<NAME>` is placed before `<MEMO>`.
  - Explicitly closes both tags when needed.
  - Limits `<NAME>` to a safe length (default: 32 characters) to satisfy Microsoft Money constraints. Overflow is appended to `<MEMO>`.
- Removes `<BALLIST>` only when both opening and closing tags are found; otherwise the block is preserved to avoid accidental data loss.

## Requirements
- Python 3.8+ (no third-party dependencies; only Python standard library).

## Usage
1. Place your OFX file alongside the script or provide a full path.
2. Run:
   ```bash
   python ofx_normalizer.py path/to/your_file.ofx
   ```
3. The output will be created next to your input file as:
   ```
   path/to/your_file_money.ofx
   ```

### Example
```bash
python ofx_normalizer.py "C:\Users\You\Documents\OFX\FEBRUARY.ofx"
# Output: C:\Users\You\Documents\OFX\FEBRUARY_money.ofx
```

## Configuration
- The maximum length for the `<NAME>` field is controlled by a constant in the script:
  ```python
  MAX_NAME_LEN = 32
  ```
  If your specific setup of Microsoft Money allows or requires a different limit, adjust this value accordingly.

## Notes and Limitations
- The tool focuses on textual normalization for compatibility; it does not alter transaction amounts, FITIDs, or signs.
- Bank account mapping during import is handled by your finance software, not by this script.
- If your data includes extremely long descriptions, they are preserved in `<MEMO>`, while `<NAME>` is kept short to pass strict parsers.
- If you encounter issues with `<MEMO>` length in your environment, please open an issue; we can introduce configurable limits or splitting strategies.

## Validation
- For best results, validate the output file using tools like OFX Analyzer/Formatter before importing into Microsoft Money.
- Typical success indicators: "No Parse Errors" and correct totals/uniqueness when analyzed.

## Contributing
Contributions are welcome! Please:
- Open an issue describing your scenario (bank, OFX version, software version, error message).
- Submit PRs with clear explanations and tests where applicable.
- Keep changes conservative and compatibility-focused (avoid breaking valid OFX files).

## Roadmap
- CLI options (e.g., custom `MAX_NAME_LEN`, toggles for specific normalizations).
- Heuristics per bank (Sicoob/Nubank/Itaú/Inter/C6 and others) to handle known quirks.
- Optional `<MEMO>` length constraints with splitting/truncation policies.
- Lightweight test suite and sample OFX fixtures.

## License
MIT License (to be confirmed by the maintainer).

## Acknowledgements
- Thanks to the open-source community and users maintaining legacy finance workflows.
- Special thanks to Br3n0k for initiating and maintaining this project.

## Development
- The script is developed by [Br3n0k](https://github.com/Br3n0k).
- Source code is available on [GitHub](https://github.com/Br3n0k/ofx-normalizer).
- Contributions are welcome! Please follow the [Contributing](#contributing) guidelines.