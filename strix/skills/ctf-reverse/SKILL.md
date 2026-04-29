---
name: ctf-reverse
description: Provides reverse engineering techniques for CTF challenges. Use when the main job is to understand how a compiled, obfuscated, packed, or virtualized target works before exploiting or solving it, including binaries, APKs, WASM, firmware, custom VMs, bytecode, game clients, malware-like loaders, and anti-debug or anti-analysis logic. Do not use it when the vulnerability is already understood and the remaining task is exploitation; use pwn instead. Do not use it for pure web workflows, log or disk forensics, or standalone crypto problems unless reversing the implementation is the real blocker.
license: MIT
compatibility: Requires filesystem-based agent (Claude Code or similar) with bash, Python 3, and internet access for tool installation.
allowed-tools: Bash Read Write Edit Glob Grep Task WebFetch WebSearch
metadata:
  user-invocable: "false"
category: ctf
---
# CTF Reverse Engineering

Quick reference for RE challenges. For detailed techniques, see supporting files.

## Prerequisites

**Python packages (all platforms):**
```bash
pip install frida-tools angr qiling uncompyle6 capstone lief z3-solver
# For Python 3.9+ bytecode: build pycdc from source
git clone https://github.com/zrax/pycdc && cd pycdc && cmake . && make
```

**Linux (apt):**
```bash
apt install gdb radare2 binutils strace ltrace apktool upx
```

**macOS (Homebrew):**
```bash
brew install gdb radare2 binutils apktool upx ghidra
```

**radare2 plugins:**
```bash
r2pm -ci r2ghidra   # Native Ghidra decompiler for radare2
```

**Manual install:**
- pwndbg — Linux: [GitHub](https://github.com/pwndbg/pwndbg), macOS: `brew install pwndbg/tap/pwndbg-gdb`

## Additional Resources

- [tools.md](tools.md) - Static analysis tools (GDB, Ghidra, radare2, IDA, Binary Ninja, dogbolt.org, RISC-V with Capstone, Unicorn emulation, Python bytecode, WASM, Android APK, .NET, packed binaries)
- [tools-dynamic.md](tools-dynamic.md) (includes Intel Pin instruction-counting side channel for movfuscated binaries, opcode-only trace reconstruction) - Dynamic analysis tools: Frida (hooking, anti-debug bypass, memory scanning, Android/iOS), angr symbolic execution (path exploration, constraints, CFG), lldb (macOS/LLVM debugger), x64dbg (Windows), Qiling (cross-platform emulation with OS support), Triton (dynamic symbolic execution)
- [tools-advanced.md](tools-advanced.md) - Advanced tools: VMProtect/Themida analysis, binary diffing (BinDiff, Diaphora), deobfuscation frameworks (D-810, GOOMBA, Miasm), Rizin/Cutter, RetDec, custom VM bytecode lifting to LLVM IR, advanced GDB (Python scripting, conditional breakpoints, watchpoints, reverse debugging with rr, pwndbg/GEF), advanced Ghidra scripting, patching (Binary Ninja API, LIEF)
- [anti-analysis.md](anti-analysis.md) - Comprehensive anti-analysis: Linux anti-debug (ptrace, /proc, timing, signals, direct syscalls), Windows anti-debug (PEB, NtQueryInformationProcess, heap flags, TLS callbacks, HW/SW breakpoint detection, exception-based, thread hiding), anti-VM/sandbox (CPUID, MAC, timing, artifacts, resources), anti-DBI (Frida detection/bypass), code integrity/self-hashing, anti-disassembly (opaque predicates, junk bytes), MBA identification/simplification, SIGFPE signal handler side-channel via strace counting, bypass strategies
- [patterns.md](patterns.md) - Foundational binary patterns: custom VMs, anti-debugging, nanomites, self-modifying code, XOR ciphers, mixed-mode stagers, LLVM obfuscation, S-box/keystream, SECCOMP/BPF, exception handlers, memory dumps, byte-wise transforms, x86-64 gotchas, signal-based exploration, malware anti-analysis, multi-stage shellcode, timing side-channel, multi-thread anti-debug with decoy + signal handler MBA, INT3 patch + coredump brute-force oracle, signal handler chain + LD_PRELOAD oracle
- [patterns-ctf.md](patterns-ctf.md) - Competition-specific patterns (Part 1): hidden emulator opcodes, LD_PRELOAD key extraction, SPN static extraction, image XOR smoothness, byte-at-a-time cipher, mathematical convergence bitmap, Windows PE XOR bitmap OCR, two-stage RC4+VM loaders, GBA ROM meet-in-the-middle, Sprague-Grundy game theory, kernel module maze solving, multi-threaded VM channels, backdoored shared library detection via string diffing, custom binfmt kernel module with RC4 flat binaries, hash-resolved imports / no-import ransomware, ELF section header corruption for anti-analysis
- [patterns-ctf-2.md](patterns-ctf-2.md) - Competition-specific patterns (Part 2): multi-layer self-decrypting brute-force, embedded ZIP+XOR license, stack string deobfuscation, prefix hash brute-force, CVP/LLL lattice for integer validation, decision tree function obfuscation, GF(2^8) Gaussian elimination, ROP chain obfuscation analysis (ROPfuscation)
- [patterns-ctf-3.md](patterns-ctf-3.md) - Competition-specific patterns (Part 3): Z3 single-line Python circuit, sliding window popcount, keyboard LED Morse code via ioctl, C++ destructor-hidden validation, syscall side-effect memory corruption, MFC dialog event handlers, VM sequential key-chain brute-force, Burrows-Wheeler transform inversion, OpenType font ligature exploitation, GLSL shader VM with self-modifying code, instruction counter as cryptographic state, batch crackme automation via objdump, fork+pipe+dead branch anti-analysis
- [languages.md](languages.md) - Language-specific: Python bytecode & opcode remapping, Python version-specific bytecode, Pyarmor static unpack, DOS stubs, Unity IL2CPP, HarmonyOS HAP/ABC, Brainfuck/esolangs (+ BF character-by-character static analysis, BF side-channel read count oracle, BF comparison idiom detection), UEFI, transpilation to C, code coverage side-channel, OPAL functional reversing, non-bijective substitution, FRACTRAN program inversion
- [languages-platforms.md](languages-platforms.md) - Platform/framework-specific: Roblox place file analysis, Godot game asset extraction, Rust serde_json schema recovery, Android JNI RegisterNatives obfuscation, Android DEX runtime bytecode patching via /proc/self/maps, Frida Firebase Cloud Functions bypass, Verilog/hardware RE, prefix-by-prefix hash reversal, Ruby/Perl polyglot constraint satisfaction, Electron ASAR extraction + native binary analysis, Node.js npm runtime introspection
- [languages-compiled.md](languages-compiled.md) - Go binary reversing (GoReSym, goroutines, memory layout, channel ops, embed.FS, Go binary UUID patching for C2 enumeration), Rust binary reversing (demangling, Option/Result, Vec, panic strings), Swift binary reversing (demangling, protocol witness tables), Kotlin/JVM (coroutine state machines), C++ (vtable reconstruction, RTTI, STL patterns)
- [platforms.md](platforms.md) - Platform-specific RE: macOS/iOS (Mach-O, code signing, Objective-C runtime, Swift, dyld, jailbreak bypass), embedded/IoT firmware (binwalk, UART/JTAG/SPI extraction, ARM/MIPS, RTOS), kernel drivers (Linux .ko, eBPF, Windows .sys), game engines (Unreal Engine, Unity, anti-cheat, Lua), automotive CAN bus
- [platforms-hardware.md](platforms-hardware.md) - Hardware and advanced architecture RE: HD44780 LCD controller GPIO reconstruction, RISC-V advanced (custom extensions, privileged modes, debugging), ARM64/AArch64 reversing and exploitation (calling convention, ROP gadgets, qemu-aarch64-static emulation)

---

## When to Pivot

- If you already understand the binary and now need heap, ROP, or kernel exploitation, switch to `/ctf-pwn`.
- If the challenge is really about recovering deleted files, PCAP data, or disk artifacts, switch to `/ctf-forensics`.
- If the target is a web app and you are only reversing a small client-side helper script, switch to `/ctf-web`.
- If the binary implements a machine learning model and the challenge is about model attacks or adversarial inputs, switch to `/ctf-ai-ml`.
- If the reversed binary's core logic is a cryptographic algorithm or math problem, switch to `/ctf-crypto`.
- If the binary is a real malware sample with C2, packing, or evasion behavior, switch to `/ctf-malware`.
- If the challenge is a toy VM, encoding puzzle, or pyjail rather than a real binary, switch to `/ctf-misc`.

## Problem-Solving Workflow

1. **Start with strings extraction** - many easy challenges have plaintext flags
2. **Try ltrace/strace** - dynamic analysis often reveals flags without reversing
3. **Try Frida hooking** - hook strcmp/memcmp to capture expected values without reversing
4. **Try angr** - symbolic execution solves many flag-checkers automatically
5. **Try Qiling** - emulate foreign-arch binaries or bypass heavy anti-debug without artifacts
6. **Map control flow** before modifying execution
7. **Automate manual processes** via scripting (r2pipe, Frida, angr, Python)
8. **Validate assumptions** by comparing decompiler outputs (dogbolt.org for side-by-side)

## Quick Wins (Try First!)

```bash
# Plaintext flag extraction
strings binary | grep -E "flag\{|CTF\{|pico"
strings binary | grep -iE "flag|secret|password"
rabin2 -z binary | grep -i "flag"

# Dynamic analysis - often captures flag directly
ltrace ./binary
strace -f -s 500 ./binary

# Hex dump search
xxd binary | grep -i flag

# Run with test inputs
./binary AAAA
echo "test" | ./binary
```

## Initial Analysis

```bash
file binary           # Type, architecture
checksec --file=binary # Security features (for pwn)
chmod +x binary       # Make executable
```

## Memory Dumping Strategy

**Key insight:** Let the program compute the answer, then dump it. Break at final comparison (`b *main+OFFSET`), enter any input of correct length, then `x/s $rsi` to dump computed flag.

## Decoy Flag Detection

**Pattern:** Multiple fake targets before real check. Look for multiple comparison targets in sequence with different success messages. Set breakpoint at FINAL comparison, not earlier ones.

## GDB PIE Debugging

PIE binaries randomize base address. Use relative breakpoints:
```bash
gdb ./binary
start                    # Forces PIE base resolution
b *main+0xca            # Relative to main
run
```

## Comparison Direction (Critical!)

Two patterns: (1) `transform(flag) == stored_target` — reverse the transform. (2) `transform(stored_target) == flag` — flag IS the transformed data, just apply transform to stored target.

## Common Encryption Patterns

- XOR with single byte - try all 256 values
- XOR with known plaintext (`flag{`, `CTF{`)
- RC4 with hardcoded key
- Custom permutation + XOR
- XOR with position index (`^ i` or `^ (i & 0xff)`) layered with a repeating key

## Quick Tool Reference

```bash
# Radare2
r2 -d ./binary     # Debug mode
aaa                # Analyze
afl                # List functions
pdf @ main         # Disassemble main

# Ghidra (headless)
analyzeHeadless project/ tmp -import binary -postScript script.py

# IDA
ida64 binary       # Open in IDA64
```

## Deep-Dive Notes

Use [field-notes.md](field-notes.md) after the first round of triage when you know what kind of target you have.

- Target formats: Python bytecode, WASM, Android, Flutter, .NET, UPX, Tauri
- Technique notes: anti-debug bypass, VM analysis, x86-64 gotchas, iterative solvers, Unicorn, timing side channels
- Platform notes: Godot, Roblox, macOS/iOS, embedded firmware, kernel drivers, game engines, Swift, Kotlin, Go, Rust, D
- Case notes: modern CTF-specific reversing patterns and older classic challenge patterns


---


# anti-analysis

# CTF Reverse - Anti-Analysis Techniques & Bypasses

Comprehensive reference for anti-debugging, anti-VM, anti-DBI, and integrity-check techniques encountered in CTF challenges, with practical bypasses.

## Table of Contents
- [Linux Anti-Debug (Advanced)](#linux-anti-debug-advanced)
  - [ptrace-Based](#ptrace-based)
  - [/proc Filesystem Checks](#proc-filesystem-checks)
  - [Timing-Based Detection](#timing-based-detection)
  - [Signal-Based Anti-Debug](#signal-based-anti-debug)
  - [Syscall-Level Evasion](#syscall-level-evasion)
- [Windows Anti-Debug (Advanced)](#windows-anti-debug-advanced)
  - [PEB-Based Checks](#peb-based-checks)
  - [NtQueryInformationProcess](#ntqueryinformationprocess)
  - [Heap Flags](#heap-flags)
  - [TLS Callbacks](#tls-callbacks)
  - [Hardware Breakpoint Detection](#hardware-breakpoint-detection)
  - [Software Breakpoint Detection (INT3 Scanning)](#software-breakpoint-detection-int3-scanning)
  - [Exception-Based Anti-Debug](#exception-based-anti-debug)
  - [NtSetInformationThread (Thread Hiding)](#ntsetinformationthread-thread-hiding)
- [Anti-VM / Anti-Sandbox](#anti-vm--anti-sandbox)
  - [CPUID Hypervisor Bit](#cpuid-hypervisor-bit)
  - [MAC Address / Hardware Fingerprinting](#mac-address--hardware-fingerprinting)
  - [Timing-Based VM Detection](#timing-based-vm-detection)
  - [File / Registry Artifacts](#file--registry-artifacts)
  - [Resource Checks (CPU Count, RAM, Disk)](#resource-checks-cpu-count-ram-disk)
- [Anti-DBI (Dynamic Binary Instrumentation)](#anti-dbi-dynamic-binary-instrumentation)
  - [Frida Detection](#frida-detection)
  - [Pin/DynamoRIO Detection](#pindynamorio-detection)
- [Code Integrity / Self-Hashing](#code-integrity--self-hashing)
- [Anti-Disassembly Techniques](#anti-disassembly-techniques)
  - [Opaque Predicates](#opaque-predicates)
  - [Junk Bytes / Overlapping Instructions](#junk-bytes--overlapping-instructions)
  - [Jump-in-the-Middle](#jump-in-the-middle)
  - [Function Chunking / Scattered Code](#function-chunking--scattered-code)
  - [Control Flow Flattening (Advanced)](#control-flow-flattening-advanced)
  - [Mixed Boolean-Arithmetic (MBA) Identification & Simplification](#mixed-boolean-arithmetic-mba-identification--simplification)
- [SIGILL Handler for Execution Mode Switching (Hack.lu 2015)](#sigill-handler-for-execution-mode-switching-hacklu-2015)
- [SIGFPE Signal Handler Side-Channel via strace Counting (PlaidCTF 2017)](#sigfpe-signal-handler-side-channel-via-strace-counting-plaidctf-2017)
- [Instruction Trace Inversion with Keystone and Unicorn (MeePwn CTF 2017)](#instruction-trace-inversion-with-keystone-and-unicorn-meepwn-ctf-2017)
- [Comprehensive Bypass Strategies](#comprehensive-bypass-strategies)
  - [Universal Bypass Checklist](#universal-bypass-checklist)
  - [Layered Anti-Debug (Real-World Pattern)](#layered-anti-debug-real-world-pattern)
  - [Quick Reference: Check to Bypass](#quick-reference-check-to-bypass)

---

## Linux Anti-Debug (Advanced)

### ptrace-Based

**Self-ptrace (most common):**
```c
if (ptrace(PTRACE_TRACEME, 0, 0, 0) == -1) exit(1); // Already traced = debugger attached
```

**Bypasses:**
```bash
# 1. LD_PRELOAD (see patterns.md for full hook)
LD_PRELOAD=./hook.so ./binary

# 2. Patch with pwntools
python3 -c "
from pwn import *
elf = ELF('./binary', checksec=False)
elf.asm(elf.symbols.ptrace, 'xor eax, eax; ret')
elf.save('patched')
"

# 3. GDB: catch the syscall
gdb ./binary
(gdb) catch syscall ptrace
(gdb) run
# When it stops at ptrace:
(gdb) set $rax = 0
(gdb) continue

# 4. Kernel config (requires root)
echo 0 > /proc/sys/kernel/yama/ptrace_scope
```

**Double-ptrace pattern:**
```c
// Fork child to ptrace parent — blocks all other debuggers
pid_t child = fork();
if (child == 0) {
    ptrace(PTRACE_ATTACH, getppid(), 0, 0);
    // Child sits in waitpid loop, keeping parent traced
} else {
    // Parent continues with real logic
}
```
**Bypass:** Kill the watchdog child process, then attach debugger.

### /proc Filesystem Checks

```c
// TracerPid check
FILE *f = fopen("/proc/self/status", "r");
// Looks for "TracerPid:\t0" — non-zero means debugger

// /proc/self/exe link check (some debuggers change this)
readlink("/proc/self/exe", buf, sizeof(buf));

// /proc/self/maps — check for debugger libraries
grep("frida", "/proc/self/maps");
```

**Bypasses:**
```bash
# 1. LD_PRELOAD fopen/fread to fake /proc contents
# 2. Mount namespace isolation
unshare -m bash -c 'mount --bind /dev/null /proc/self/status && ./binary'

# 3. GDB: set breakpoint at fopen, change filename argument
(gdb) b fopen
(gdb) run
(gdb) set {char[20]} $rdi = "/dev/null"
(gdb) continue
```

### Timing-Based Detection

```c
// rdtsc (CPU timestamp counter)
uint64_t start = __rdtsc();
// ... code ...
uint64_t delta = __rdtsc() - start;
if (delta > THRESHOLD) exit(1);  // too slow = debugger

// clock_gettime
struct timespec ts1, ts2;
clock_gettime(CLOCK_MONOTONIC, &ts1);
// ... code ...
clock_gettime(CLOCK_MONOTONIC, &ts2);

// gettimeofday
struct timeval tv1, tv2;
gettimeofday(&tv1, NULL);
```

**Bypasses:**
```bash
# 1. Frida hook (see tools-dynamic.md for clock_gettime hook)

# 2. GDB: skip rdtsc by patching with constant
(gdb) set {unsigned char[2]} 0x401234 = {0x90, 0x90}  # NOP the rdtsc

# 3. Pin tool to fix TSC reads
# 4. faketime library
LD_PRELOAD=/usr/lib/faketime/libfaketime.so.1 FAKETIME="2024-01-01" ./binary
```

### Signal-Based Anti-Debug

```c
// SIGTRAP handler — INT3 under debugger is caught by debugger, not handler
signal(SIGTRAP, handler);
__asm__("int3");
// If handler runs: no debugger. If debugger catches: debugged.

// SIGALRM timeout — kill self if analysis takes too long
signal(SIGALRM, kill_handler);
alarm(5);

// SIGSEGV handler that does real work (see patterns.md for MBA pattern)
signal(SIGSEGV, real_logic_handler);
*(int*)0 = 0;  // deliberate crash → handler runs real code
```

**Bypasses:**
```bash
# GDB: pass signals to program instead of handling them
(gdb) handle SIGTRAP nostop pass
(gdb) handle SIGALRM ignore
(gdb) handle SIGSEGV nostop pass

# For alarm-based: patch alarm() to return immediately
```

### Syscall-Level Evasion

```c
// Direct syscall instead of libc — bypasses LD_PRELOAD hooks
long ret;
asm volatile("syscall" : "=a"(ret) : "a"(101), "D"(0), "S"(0), "d"(0), "r"(0));
// Syscall 101 = ptrace on x86_64
```

**Bypass:** Must patch the binary itself or use ptrace to intercept at syscall level.
```bash
# GDB: catch syscall
(gdb) catch syscall 101
(gdb) commands
> set $rax = 0
> continue
> end
```

---

## Windows Anti-Debug (Advanced)

### PEB-Based Checks

```c
// BeingDebugged flag (offset 0x2 in PEB)
bool debugged = NtCurrentPeb()->BeingDebugged;

// NtGlobalFlag (offset 0x68/0xBC in PEB)
// When debugger: FLG_HEAP_ENABLE_TAIL_CHECK | FLG_HEAP_ENABLE_FREE_CHECK | FLG_HEAP_VALIDATE_PARAMETERS = 0x70
DWORD flags = *(DWORD*)((BYTE*)NtCurrentPeb() + 0xBC); // 64-bit offset
if (flags & 0x70) exit(1);
```

**Bypass (x64dbg):**
```text
# ScyllaHide plugin auto-patches PEB fields
# Manual: dump PEB, zero BeingDebugged and NtGlobalFlag
```

### NtQueryInformationProcess

```c
// ProcessDebugPort (0x7)
DWORD_PTR debugPort = 0;
NtQueryInformationProcess(GetCurrentProcess(), 7, &debugPort, sizeof(debugPort), NULL);
if (debugPort != 0) exit(1);

// ProcessDebugObjectHandle (0x1E)
HANDLE debugObj = NULL;
NTSTATUS status = NtQueryInformationProcess(GetCurrentProcess(), 0x1E, &debugObj, sizeof(debugObj), NULL);
if (status == 0) exit(1); // STATUS_SUCCESS means debugger present

// ProcessDebugFlags (0x1F) — returns inverse: 0 = debugger present
DWORD noDebug = 0;
NtQueryInformationProcess(GetCurrentProcess(), 0x1F, &noDebug, sizeof(noDebug), NULL);
if (noDebug == 0) exit(1);
```

**Bypass:** Hook `NtQueryInformationProcess` to return fake values, or use ScyllaHide.

### Heap Flags

```c
// Process heap has debug flags when debugger attached
PHEAP heap = (PHEAP)GetProcessHeap();
// Flags at offset 0x70 (64-bit): should be HEAP_GROWABLE (0x2)
// ForceFlags at offset 0x74: should be 0
if (heap->Flags != 0x2 || heap->ForceFlags != 0) exit(1);
```

### TLS Callbacks

**Key technique:** TLS (Thread Local Storage) callbacks execute BEFORE `main()` / entry point.

```c
// Registered in PE header's TLS directory
void NTAPI TlsCallback(PVOID DllHandle, DWORD Reason, PVOID Reserved) {
    if (Reason == DLL_PROCESS_ATTACH) {
        if (IsDebuggerPresent()) {
            ExitProcess(1);  // Kills process before main runs
        }
    }
}

#pragma comment(linker, "/INCLUDE:_tls_used")
#pragma data_seg(".CRT$XLB")
PIMAGE_TLS_CALLBACK callbacks[] = { TlsCallback, NULL };
```

**Detection in IDA/Ghidra:** Check PE TLS Directory → AddressOfCallBacks. Functions listed there run before EP.

**Bypass:** Set breakpoint on TLS callback in x64dbg (Options → Events → TLS Callbacks), or patch the TLS directory entry.

### Hardware Breakpoint Detection

```c
// Read debug registers via GetThreadContext
CONTEXT ctx;
ctx.ContextFlags = CONTEXT_DEBUG_REGISTERS;
GetThreadContext(GetCurrentThread(), &ctx);
if (ctx.Dr0 || ctx.Dr1 || ctx.Dr2 || ctx.Dr3) exit(1);

// Also via exception handler: deliberate exception, check DR regs in handler
```

**Bypass:**
```bash
# x64dbg: use software breakpoints instead, or hook GetThreadContext
# Frida: hook GetThreadContext to zero DR registers
```

### Software Breakpoint Detection (INT3 Scanning)

```c
// CRC / hash check over code section
unsigned char *code = (unsigned char*)function_addr;
uint32_t checksum = 0;
for (int i = 0; i < code_size; i++) {
    checksum += code[i];
    if (code[i] == 0xCC) exit(1);  // INT3 = software breakpoint
}
if (checksum != EXPECTED_CHECKSUM) exit(1);
```

**Bypass:** Use hardware breakpoints (DR0-DR3) instead of software breakpoints. Or hook the scanning function.

### Exception-Based Anti-Debug

```c
// UnhandledExceptionFilter — under debugger, filter is NOT called
SetUnhandledExceptionFilter(handler);
RaiseException(EXCEPTION_ACCESS_VIOLATION, 0, 0, NULL);
// If handler runs: no debugger
// If debugger catches: debugger present

// INT 2D — debugger single-step anomaly
__asm { int 2dh }  // Debugger silently consumes the exception
// If execution continues: debugger present
```

### NtSetInformationThread (Thread Hiding)

```c
// Hide thread from debugger — stops all debug events
typedef NTSTATUS(NTAPI *pNtSIT)(HANDLE, ULONG, PVOID, ULONG);
pNtSIT NtSIT = (pNtSIT)GetProcAddress(GetModuleHandle("ntdll"), "NtSetInformationThread");
NtSIT(GetCurrentThread(), 0x11 /*ThreadHideFromDebugger*/, NULL, 0);
// After this, debugger won't see breakpoints or exceptions from this thread
```

**Bypass:** Hook `NtSetInformationThread` to ignore class 0x11, or patch the call.

---

## Anti-VM / Anti-Sandbox

### CPUID Hypervisor Bit

```c
int regs[4];
__cpuid(regs, 1);
if (regs[2] & (1 << 31)) {  // ECX bit 31 = hypervisor present
    exit(1);
}

// Hypervisor brand string
__cpuid(regs, 0x40000000);
char brand[13] = {0};
memcpy(brand, &regs[1], 12);
// "VMwareVMware", "Microsoft Hv", "KVMKVMKVM", "XenVMMXenVMM"
```

**Bypass:** Patch `cpuid` results or use `LD_PRELOAD` to hook wrapper functions.

### MAC Address / Hardware Fingerprinting

```text
Known VM MAC prefixes:
  VMware:     00:0C:29, 00:50:56
  VirtualBox: 08:00:27
  Hyper-V:    00:15:5D
  Parallels:  00:1C:42
  QEMU:       52:54:00
```

### Timing-Based VM Detection

```c
// VM exits on privileged instructions are measurably slower
uint64_t start = __rdtsc();
__cpuid(regs, 0);  // Forces VM exit
uint64_t delta = __rdtsc() - start;
if (delta > 500) { /* likely VM */ }
```

### File / Registry Artifacts

```text
Files: C:\Windows\System32\drivers\vm*.sys, vbox*.dll, VBoxService.exe
Registry: HKLM\SOFTWARE\VMware, Inc.\VMware Tools
Services: VMTools, VBoxService
Processes: vmtoolsd.exe, VBoxTray.exe, qemu-ga.exe
Linux: /sys/class/dmi/id/product_name contains "VirtualBox"|"VMware"
       dmesg | grep -i "hypervisor detected"
```

### Resource Checks (CPU Count, RAM, Disk)

```c
// Sandboxes typically have minimal resources
SYSTEM_INFO si;
GetSystemInfo(&si);
if (si.dwNumberOfProcessors < 2) exit(1);

MEMORYSTATUSEX ms;
ms.dwLength = sizeof(ms);
GlobalMemoryStatusEx(&ms);
if (ms.ullTotalPhys < 2ULL * 1024 * 1024 * 1024) exit(1); // < 2GB RAM

// Disk size check (< 60GB = sandbox)
GetDiskFreeSpaceEx("C:\\", NULL, &total, NULL);
```

**Bypass:** Use a VM configured with adequate resources (4+ CPUs, 8GB+ RAM, 100GB+ disk).

---

## Anti-DBI (Dynamic Binary Instrumentation)

### Frida Detection

```c
// 1. Check /proc/self/maps for frida-agent
FILE *f = fopen("/proc/self/maps", "r");
while (fgets(line, sizeof(line), f)) {
    if (strstr(line, "frida") || strstr(line, "gadget")) exit(1);
}

// 2. Check for Frida's default port (27042)
int sock = socket(AF_INET, SOCK_STREAM, 0);
struct sockaddr_in addr = {.sin_family=AF_INET, .sin_port=htons(27042), .sin_addr.s_addr=inet_addr("127.0.0.1")};
if (connect(sock, (struct sockaddr*)&addr, sizeof(addr)) == 0) exit(1);

// 3. Check for inline hooks (function prologue modification)
// Compare first bytes of libc functions against expected values
unsigned char *strcmp_bytes = (unsigned char *)strcmp;
if (strcmp_bytes[0] == 0xE9 || strcmp_bytes[0] == 0xFF) exit(1); // JMP = hooked

// 4. Thread name check
// Frida creates threads with names like "gmain", "gdbus", "frida-*"
DIR *dir = opendir("/proc/self/task");
while ((entry = readdir(dir))) {
    char comm_path[256];
    snprintf(comm_path, sizeof(comm_path), "/proc/self/task/%s/comm", entry->d_name);
    // Read comm and check for "gmain", "gdbus"
}

// 5. Named pipe detection (Windows)
// Frida creates \\.\pipe\frida-* named pipes
```

**Frida bypass of Frida detection:**
```javascript
// Hook the detection functions themselves
Interceptor.attach(Module.findExportByName(null, "strstr"), {
    onEnter(args) {
        this.haystack = Memory.readUtf8String(args[0]);
        this.needle = Memory.readUtf8String(args[1]);
    },
    onLeave(retval) {
        if (this.needle && (this.needle.includes("frida") || this.needle.includes("gadget"))) {
            retval.replace(ptr(0)); // Not found
        }
    }
});

// Early Frida load (before anti-DBI runs)
// Use frida-gadget as early-init shared library
```

### Pin/DynamoRIO Detection

```c
// Check for instrumentation libraries in /proc/self/maps
// Pin: "pin-", "pinbin", "pinatrace"
// DynamoRIO: "dynamorio", "drcov", "drrun"

// Instruction count timing — DBI adds overhead
// Execute known instruction sequence, compare execution time
```

---

## Code Integrity / Self-Hashing

```c
// CRC32 over .text section
uint32_t crc = compute_crc32(text_start, text_size);
if (crc != EXPECTED_CRC) exit(1);  // Code was modified (breakpoints, patches)

// MD5/SHA256 of function bodies
unsigned char hash[32];
SHA256(function_addr, function_size, hash);
if (memcmp(hash, expected_hash, 32) != 0) exit(1);
```

**Bypasses:**
1. **Hardware breakpoints** (don't modify code, DR0-DR3)
2. **Patch the comparison** to always succeed
3. **Hook the hash function** to return expected value
4. **Emulate** instead of debug (Unicorn/Qiling — no code modification)
5. **Snapshot + restore:** dump memory before and after, diff to find checks

**Self-checksumming in loops:**
```c
// Continuous integrity check in separate thread
void *watchdog(void *arg) {
    while (1) {
        if (compute_crc32(text_start, text_end - text_start) != saved_crc) {
            memset(flag_buffer, 0, flag_len);  // Destroy flag
            exit(1);
        }
        usleep(100000);
    }
}
```
**Bypass:** Kill the watchdog thread or patch its sleep to infinite.

---

## Anti-Disassembly Techniques

### Opaque Predicates

```asm
; Condition that always evaluates the same way but looks data-dependent
mov eax, [some_memory]
imul eax, eax          ; x^2
and eax, 1             ; x^2 mod 2 is always 0 for any x
jnz fake_branch        ; Never taken, but disassembler doesn't know
; real code here
```

**Identification:** Z3/SMT can prove branch is always/never taken.

### Junk Bytes / Overlapping Instructions

```asm
jmp real_code
db 0xE8           ; Looks like start of CALL to linear disassembler
real_code:
mov eax, 1        ; Real code — disassembler may misalign here
```

**Fix:** Switch to graph-mode disassembly (Ghidra/IDA handle this well). Manual: undefine and re-analyze from correct offset.

### Jump-in-the-Middle

```asm
; Jumps into the middle of a multi-byte instruction
eb 01          ; jmp +1 (skip next byte)
e8             ; fake CALL opcode — disassembler tries to decode as call
90             ; real: NOP (landed here from jmp)
```

### Function Chunking / Scattered Code

Functions split into non-contiguous chunks connected by unconditional jumps. Defeats linear function boundary detection.

**Tool:** IDA's "Append function tail" or Ghidra's "Create function" at each chunk.

### Control Flow Flattening (Advanced)

Beyond basic switch-case (see patterns.md): modern OLLVM variants use:
- **Bogus control flow:** Fake branches with opaque predicates
- **Instruction substitution:** `a + b` → `a - (-b)`, `a ^ b` → `(a | b) & ~(a & b)`
- **String encryption:** Strings decrypted at runtime, cleared after use

**Deobfuscation tools:**
- **D-810** (IDA plugin): Pattern-based deobfuscation, MBA simplification
- **GOOMBA** (Ghidra): Automated deobfuscation for OLLVM
- **Miasm**: Symbolic execution for deobfuscation
- **Arybo** / **SiMBA**: MBA expression simplification

```bash
# D-810: install in IDA plugins directory, Edit → Plugins → D-810
# Simplifies MBA expressions: (a | b) & ~(a & b) → a ^ b
# Removes opaque predicates via pattern matching
```

### Mixed Boolean-Arithmetic (MBA) Identification & Simplification

```python
# Common MBA patterns and their simplified forms:
# (x & y) + (x | y) == x + y
# (x ^ y) + 2*(x & y) == x + y
# (x | y) - (x & ~y) == y
# ~(~x & ~y) == x | y (De Morgan's)
# (x | y) & ~(x & y) == x ^ y

# SiMBA tool for automated simplification:
# pip install simba-simplifier
from simba import simplify_mba
expr = "(a | b) + (a & b) - (~a & b)"
print(simplify_mba(expr))  # → a
```

---

## SIGILL Handler for Execution Mode Switching (Hack.lu 2015)

Binaries may install SIGILL (illegal instruction) handlers to switch between x86 and x86-64 execution modes or implement custom opcode dispatch:

1. **Signal registration:** `signal(SIGILL, handler)` installs a callback for illegal instruction exceptions
2. **Mode switching:** The handler modifies the saved instruction pointer or segment registers to switch between 32-bit and 64-bit code
3. **Custom opcodes:** Invalid x86 instructions trigger the handler, which interprets operand bytes as custom VM opcodes

```c
// Signal handler decodes "illegal" instructions as custom opcodes
void sigill_handler(int sig, siginfo_t *info, void *ucontext) {
    ucontext_t *ctx = (ucontext_t *)ucontext;
    unsigned char *pc = (unsigned char *)ctx->uc_mcontext.gregs[REG_RIP];
    // Decode custom opcode from bytes at PC
    // Advance PC past the custom instruction
    ctx->uc_mcontext.gregs[REG_RIP] += opcode_length;
}
```

**Key insight:** If a binary installs signal handlers for SIGILL/SIGSEGV/SIGTRAP early in execution, suspect custom instruction dispatch. Trace signal deliveries with `strace -e signal` or set GDB to not intercept: `handle SIGILL nostop pass`.

---

## SIGFPE Signal Handler Side-Channel via strace Counting (PlaidCTF 2017)

Binary uses SIGFPE signal handlers for control flow, making static analysis unreliable. Brute-force by counting SIGFPE signals via strace — correct input characters produce more signals.

```bash
# Count SIGFPE signals per input character guess
for c in {a..z} {A..Z} {0..9}; do
    count=$(echo -n "${c}AAAAAAA" | strace -e signal=SIGFPE ./binary 2>&1 | grep -c SIGFPE)
    echo "$c: $count"
done
# Character producing the most SIGFPEs is correct
# Repeat for each position, extending the known prefix
```

**Key insight:** Signal handlers (SIGFPE, SIGSEGV, SIGILL) create implicit control flow invisible to static analysis. The number of signals raised correlates with validation progress. Counting signals via `strace -e signal=SIGFPE` turns opaque signal-based validation into a measurable side-channel for character-by-character brute-force.

---

## Instruction Trace Inversion with Keystone and Unicorn (MeePwn CTF 2017)

UPX-packed binary applies a sequence of arithmetic-only transforms (sub, add, xor, rol, ror) to the flag. No memory side-effects — purely register arithmetic. IDAPython traces non-jump instructions, the sequence is then inverted to recover the flag.

**Inversion rules:**
- Reverse the instruction sequence (last instruction first)
- Swap inverse pairs: `add ↔ sub`, `rol ↔ ror`, `xor` is self-inverse

```python
# IDAPython: collect non-jump instructions in the obfuscated routine
import idaapi, idc

def trace_transforms(start_ea, end_ea):
    instructions = []
    ea = start_ea
    while ea < end_ea:
        mnem = idc.print_insn_mnem(ea)
        if mnem not in ('jmp', 'je', 'jne', 'call', 'ret'):
            instructions.append((ea, mnem, idc.print_operands(ea)))
        ea = idc.next_head(ea)
    return instructions

transforms = trace_transforms(0x401000, 0x401200)

# Invert: reverse order, swap add/sub and rol/ror
inverse_map = {'add': 'sub', 'sub': 'add', 'rol': 'ror', 'ror': 'rol', 'xor': 'xor'}
inverted = [(mnem, op) for (_, mnem, op) in reversed(transforms)]
inverted = [(inverse_map.get(m, m), op) for m, op in inverted]
```

```python
# Assemble inverted instructions with Keystone, emulate with Unicorn
from keystone import *
from unicorn import *
from unicorn.x86_const import *

ks = Ks(KS_ARCH_X86, KS_MODE_64)
uc = Uc(UC_ARCH_X86, UC_MODE_64)

asm_src = '\n'.join(f'{mnem} {op}' for mnem, op in inverted)
encoding, _ = ks.asm(asm_src)

CODE_BASE = 0x400000
uc.mem_map(CODE_BASE, 0x10000)
uc.mem_write(CODE_BASE, bytes(encoding))

# Set initial register state to the observed output value
uc.reg_write(UC_X86_REG_RAX, known_output)
uc.emu_start(CODE_BASE, CODE_BASE + len(encoding))
flag_bytes = uc.reg_read(UC_X86_REG_RAX).to_bytes(8, 'little')
```

**PEB anti-debug note:** If the binary reads `PEB.BeingDebugged` and uses it to select between two comparison target values, the traced instructions under IDAPython may use the debug-mode target. Patch `BeingDebugged` to 0 before tracing, or identify both branches and use the non-debug target value.

**Key insight:** Arithmetic-only obfuscation (no memory writes) is fully reversible by tracing, inverting the instruction sequence, and swapping inverse operations. PEB anti-debug can silently change comparison targets — always verify which branch is taken.

**References:** MeePwn CTF 2017

---

## Comprehensive Bypass Strategies

### Universal Bypass Checklist

1. **Identify all anti-analysis checks** — search for: `ptrace`, `IsDebuggerPresent`, `rdtsc`, `cpuid`, `NtQuery`, `GetTickCount`, `CheckRemoteDebuggerPresent`, `/proc/self`, `SIGTRAP`, `alarm`
2. **Static patching** — NOP/patch checks with pwntools or Ghidra before running
3. **LD_PRELOAD** (Linux) — hook libc functions returning fake values
4. **ScyllaHide** (Windows x64dbg) — patches PEB, hooks NT functions automatically
5. **Emulation** (Unicorn/Qiling) — no debugger artifacts to detect
6. **Kernel-level bypass** — modify `/proc/sys/kernel/yama/ptrace_scope`, use `prctl`

### Layered Anti-Debug (Real-World Pattern)

Many CTF challenges stack multiple checks:
```text
1. TLS callback → IsDebuggerPresent (before main)
2. main() → ptrace(TRACEME)
3. Watchdog thread → timing check + /proc scan
4. Code section → self-CRC32 integrity
5. Signal handler → real logic in SIGSEGV handler
```

**Approach:** Identify ALL checks before patching. Patch or hook each one systematically. Run under emulator if too many to patch individually.

### Quick Reference: Check to Bypass

| Anti-Debug Check | Platform | Bypass |
|---|---|---|
| `ptrace(TRACEME)` | Linux | `LD_PRELOAD`, patch to `ret 0`, `catch syscall` |
| `IsDebuggerPresent` | Windows | ScyllaHide, Frida hook, PEB patch |
| `NtQueryInformationProcess` | Windows | ScyllaHide, hook ntdll |
| `rdtsc` timing | Both | NOP rdtsc, Frida time hook, Pin |
| `/proc/self/status` | Linux | Mount namespace, hook fopen |
| `alarm(N)` | Linux | `handle SIGALRM ignore` in GDB |
| `SIGTRAP` handler | Linux | `handle SIGTRAP nostop pass` |
| `SIGFPE` handler side-channel | Linux | `strace -e signal=SIGFPE` count per input |
| TLS callback | Windows | Break on TLS in x64dbg, patch |
| DR register scan | Windows | Use software BPs, hook GetThreadContext |
| INT3 scan / CRC | Both | Hardware BPs, patch CRC comparison |
| Frida detection | Both | Early-load gadget, hook strstr |
| CPUID hypervisor | Both | Patch CPUID result, bare metal |
| Thread hiding | Windows | Hook NtSetInformationThread |


# field-notes

# Reverse Engineering Field Notes

Detailed quick notes that support [`SKILL.md`](SKILL.md). Read this file after triage, not before.

## Table of Contents

- [Binary Types](#binary-types)
- [Anti-Debugging Bypass](#anti-debugging-bypass)
- [Specialized Patterns](#specialized-patterns)
- [CTF Case Notes](#ctf-case-notes)

## Binary Types

### Python .pyc
Disassemble with `marshal.load()` + `dis.dis()`. Header: 8 bytes (2.x), 12 (3.0-3.6), 16 (3.7+). See [languages.md](languages.md#python-bytecode-reversing-disdis-output).

### WASM
```bash
wasm2c checker.wasm -o checker.c
gcc -O3 checker.c wasm-rt-impl.c -o checker

# WASM patching (game challenges):
wasm2wat main.wasm -o main.wat    # Binary → text
# Edit WAT: flip comparisons, change constants
wat2wasm main.wat -o patched.wasm # Text → binary
```

**WASM game patching (Tac Tic Toe, Pragyan 2026):** If proof generation is independent of move quality, patch minimax (flip `i64.lt_s` → `i64.gt_s`, change bestScore sign) to make AI play badly while proofs remain valid. Invoke `/ctf-misc` for full game patching patterns (games-and-vms).

### Android APK
`apktool d app.apk -o decoded/` for resources; `jadx app.apk` for Java decompilation. Check `decoded/res/values/strings.xml` for flags. See [tools.md](tools.md#android-apk).

### Flutter APK (Dart AOT)
If `lib/arm64-v8a/libapp.so` + `libflutter.so` present, use [Blutter](https://github.com/worawit/blutter): `python3 blutter.py path/to/app/lib/arm64-v8a out_dir`. Outputs reconstructed Dart symbols + Frida script. See [tools.md](tools.md#flutter-apk-blutter).

### .NET
- dnSpy - debugging + decompilation
- ILSpy - decompiler

### Packed (UPX)
```bash
upx -d packed -o unpacked
```
If unpacking fails, inspect UPX metadata first: verify UPX section names, header fields, and version markers are intact. If metadata looks tampered or uncertain, review UPX source on GitHub to identify likely modification points.

### Tauri Packed Desktop Apps
Tauri embeds Brotli-compressed frontend assets in the executable. Find `index.html` xrefs to locate asset index table, dump blobs, Brotli decompress. Reference: `tauri-codegen/src/embedded_assets.rs`.

## Anti-Debugging Bypass

Common checks:
- `IsDebuggerPresent()` / PEB.BeingDebugged / NtQueryInformationProcess (Windows)
- `ptrace(PTRACE_TRACEME)` / `/proc/self/status` TracerPid (Linux)
- TLS callbacks (run before main — check PE TLS Directory)
- Timing checks (`rdtsc`, `clock_gettime`, `GetTickCount`)
- Hardware breakpoint detection (DR0-DR3 via GetThreadContext)
- INT3 scanning / code self-hashing (CRC over .text section)
- Signal-based: SIGTRAP handler, SIGALRM timeout, SIGSEGV for real logic
- Frida/DBI detection: `/proc/self/maps` scan, port 27042, inline hook checks

Bypass: Set breakpoint at check, modify register to bypass conditional. pwntools patch: `elf.asm(elf.symbols.ptrace, 'ret')` to replace function with immediate return. See [patterns.md](patterns.md#pwntools-binary-patching-crypto-cat).

For comprehensive anti-analysis techniques and bypasses (30+ methods with code), see [anti-analysis.md](anti-analysis.md).

## Specialized Patterns

### S-Box / Keystream Patterns
**Xorshift32:** Shifts 13, 17, 5  
**Xorshift64:** Shifts 12, 25, 27  
**Magic constants:** `0x2545f4914f6cdd1d`, `0x9e3779b97f4a7c15`

### Custom VM Analysis
1. Identify structure: registers, memory, IP
2. Reverse `executeIns` for opcode meanings
3. Write disassembler mapping opcodes to mnemonics
4. Often easier to bruteforce than fully reverse
5. Look for the bytecode file loaded via command-line arg

See [patterns.md](patterns.md#custom-vm-reversing) for VM workflow, opcode tables, and state machine BFS.

**Sequential key-chain brute-force:** When a VM validates input in small blocks (e.g., 3 bytes = 2^24 candidates) with each block's output key feeding the next, brute-force each block sequentially with OpenMP parallelization. Compile solver with `gcc -O3 -march=native -fopenmp`. See [patterns-ctf-3.md](patterns-ctf-3.md#vm-sequential-key-chain-brute-force-midnight-flag-2026).

### Python Bytecode Reversing
XOR flag checkers with interleaved even/odd tables are common. See [languages.md](languages.md#python-bytecode-reversing-disdis-output) for bytecode analysis tips and reversing patterns.

### Signal-Based Binary Exploration
Binary uses UNIX signals as binary tree navigation; hook `sigaction` via `LD_PRELOAD`, DFS by sending signals. See [patterns.md](patterns.md#signal-based-binary-exploration).

### Malware Anti-Analysis Bypass via Patching
Flip `JNZ`/`JZ` (0x75/0x74), change sleep values, patch environment checks in Ghidra (`Ctrl+Shift+G`). See [patterns.md](patterns.md#malware-anti-analysis-bypass-via-patching).

### Expected Values Tables
Locate with `objdump -s -j .rodata binary | less` — look near comparison instructions, size matches flag length.

### x86-64 Gotchas
Sign extension and 32-bit truncation pitfalls. See [patterns.md](patterns.md#x86-64-gotchas) for details and code examples.

### Iterative Solver Pattern
Try each byte (0-255) per position, match against expected output. **Uniform transform shortcut:** if one input byte only changes one output byte, build 0..255 mapping then invert. See [patterns.md](patterns.md) for full implementation.

### Unicorn Emulation (Complex State)
`from unicorn import *` -- map segments, set up stack, hook to trace. **Mixed-mode pitfall:** 64-bit stub jumping to 32-bit via `retf` requires switching to UC_MODE_32 and copying GPRs + EFLAGS + XMM regs. See [tools.md](tools.md#unicorn-emulation).

### Multi-Stage Shellcode Loaders
Nested shellcode with XOR decode loops; break at `call rax`, bypass ptrace with `set $rax=0`, extract flag from `mov` instructions. See [patterns.md](patterns.md#multi-stage-shellcode-loaders).

### Timing Side-Channel Attack
Validation time varies per correct character; measure elapsed time per candidate to recover flag byte-by-byte. See [patterns.md](patterns.md#timing-side-channel-attack).

### Godot Game Asset Extraction
Use KeyDot to extract encryption key from executable, then gdsdecomp to extract .pck package. See [languages-platforms.md](languages-platforms.md#godot-game-asset-extraction).

### Roblox Place File Analysis
Query Asset Delivery API for version history; parse `.rbxlbin` chunks (INST/PROP/PRNT) to diff script sources across versions. See [languages-platforms.md](languages-platforms.md#roblox-place-file-analysis).

### Unstripped Binary Information Leaks
**Pattern:** Debug info and file paths leak author identity. Quick checks: `strings binary | grep "/home/"` (home dirs), `file binary` (stripped?), `readelf -S binary | grep debug` (debug sections).

### Custom Mangle Function Reversing
Binary mangles input 2 bytes at a time with running state; extract target from `.rodata`, write inverse function. See [patterns.md](patterns.md#custom-mangle-function-reversing).

### Rust serde_json Schema Recovery
Disassemble serde `Visitor` implementations to recover expected JSON schema; field names in order reveal flag. See [languages-platforms.md](languages-platforms.md#rust-serdejson-schema-recovery).

### Position-Based Transformation Reversing
Binary adds/subtracts position index; reverse by undoing per-index offset. See [patterns.md](patterns.md#position-based-transformation-reversing).

### Hex-Encoded String Comparison
Input converted to hex, compared against constant. Decode with `xxd -r -p`. See [patterns.md](patterns.md#hex-encoded-string-comparison).

## CTF Case Notes

### Embedded ZIP + XOR License Decryption
Binary with named symbols (`EMBEDDED_ZIP`, `ENCRYPTED_MESSAGE`) in `.rodata` → extract ZIP containing license, XOR encrypted message with license bytes to recover flag. No execution needed. See [patterns-ctf-2.md](patterns-ctf-2.md#embedded-zip-xor-license-decryption-metactf-2026).

### Stack String Deobfuscation (.rodata XOR Blob)
Binary mmaps `.rodata` blob, XOR-deobfuscates, uses it to validate input. Reimplement verification loop with pyelftools to extract blob. Look for `0x9E3779B9`, `0x85EBCA6B` constants and `rol32()`. See [patterns-ctf-2.md](patterns-ctf-2.md#stack-string-deobfuscation-from-rodata-xor-blob-nullcon-2026).

### Prefix Hash Brute-Force
Binary hashes every prefix independently. Recover one character at a time by matching prefix hashes. See [patterns-ctf-2.md](patterns-ctf-2.md#prefix-hash-brute-force-nullcon-2026).

### Mathematical Convergence Bitmap
**Pattern:** Binary classifies coordinate pairs by Newton's method convergence (e.g., z^3-1=0). Grid of pass/fail results renders ASCII art flag. Key: the binary is a classifier, not a checker — reverse the math and visualize. See [patterns-ctf.md](patterns-ctf.md#mathematical-convergence-bitmap-ehax-2026).

### RISC-V Binary Analysis
Statically linked, stripped RISC-V ELF. Use Capstone with `CS_MODE_RISCVC | CS_MODE_RISCV64` for mixed compressed instructions. Emulate with `qemu-riscv64`. Watch for fake flags and XOR decryption with incremental keys. See [tools.md](tools.md#risc-v-binary-analysis-ehax-2026).

### Sprague-Grundy Game Theory Binary
Game binary plays bounded Nim with PRNG for losing-position moves. Identify game framework (Grundy values = pile % (k+1), XOR determines position), track PRNG state evolution through user input feedback. See [patterns-ctf.md](patterns-ctf.md#sprague-grundy-game-theory-binary-dicectf-2026).

### Kernel Module Maze Solving
Rust kernel module implements maze via device ioctls. Enumerate commands dynamically, build DFS solver with decoy avoidance, deploy as minimal static binary (raw syscalls, no libc). See [patterns-ctf.md](patterns-ctf.md#kernel-module-maze-solving-dicectf-2026).

### Multi-Threaded VM with Channels
Custom VM with 16+ threads communicating via futex channels. Trace data flow across thread boundaries, extract constants from GDB, watch for inverted validity logic, solve via BFS state space search. See [patterns-ctf.md](patterns-ctf.md#multi-threaded-vm-with-channel-synchronization-dicectf-2026).

### CVP/LLL Lattice for Constrained Integer Validation
Binary validates flag via matrix multiplication with 64-bit coefficients; solutions must be printable ASCII. Use LLL reduction + CVP in SageMath to find nearest lattice point in the constrained range. Two-phase pattern: Phase 1 recovers AES key, Phase 2 decrypts custom VM bytecode with another linear system (mod 2^32). See [patterns-ctf-2.md](patterns-ctf-2.md#cvplll-lattice-for-constrained-integer-validation-htb-shadowlabyrinth).

### Decision Tree Function Obfuscation
~200+ auto-generated functions routing input through polynomial comparisons. Script extraction via Ghidra headless rather than reversing each function manually. Constraint propagation from known output format cascades through arithmetic constraints. See [patterns-ctf-2.md](patterns-ctf-2.md#decision-tree-function-obfuscation-htb-wondersms).

### Android JNI RegisterNatives Obfuscation
`RegisterNatives` in `JNI_OnLoad` hides which C++ function handles each Java native method (no standard `Java_com_pkg_Class_method` symbol). Find the real handler by tracing `JNI_OnLoad` → `RegisterNatives` → `fnPtr`. Use x86_64 `.so` from APK for best Ghidra decompilation. See [languages-platforms.md](languages-platforms.md#android-jni-registernatives-obfuscation-htb-wondersms).

### Multi-Layer Self-Decrypting Binary
N-layer binary where each layer decrypts the next using user-provided key bytes + SHA-NI. Use oracle (correct key → valid code with expected pattern). JIT execution with fork-per-candidate COW isolation for speed. See [patterns-ctf-2.md](patterns-ctf-2.md#multi-layer-self-decrypting-binary-dicectf-2026).

### GLSL Shader VM with Self-Modifying Code
**Pattern:** WebGL2 fragment shader implements Turing-complete VM on a 256x256 RGBA texture (program memory + VRAM). Self-modifying code (STORE opcode) patches drawing instructions. GPU parallelism causes write conflicts — emulate sequentially in Python to recover full output. See [patterns-ctf-3.md](patterns-ctf-3.md#glsl-shader-vm-with-self-modifying-code-apoorvctf-2026).

### GF(2^8) Gaussian Elimination for Flag Recovery
**Pattern:** Binary performs Gaussian elimination over GF(2^8) with the AES polynomial (0x11b). Matrix + augmentation vector in `.rodata`; solution vector is the flag. Look for constant `0x1b` in disassembly. Addition is XOR, multiplication uses polynomial reduction. See [patterns-ctf-2.md](patterns-ctf-2.md#gf28-gaussian-elimination-for-flag-recovery-apoorvctf-2026).

### Z3 for Single-Line Python Boolean Circuit
**Pattern:** Single-line Python (2000+ semicolons) with walrus operator chains validates flag as big-endian integer via boolean circuit. Obfuscated XOR `(a | b) & ~(a & b)`. Split on semicolons, translate to Z3 symbolically, solve in under a second. See [patterns-ctf-3.md](patterns-ctf-3.md#z3-for-single-line-python-boolean-circuit-bearcatctf-2026).

### Sliding Window Popcount Differential Propagation
**Pattern:** Binary validates input via expected popcount for each position of a 16-bit sliding window. Popcount differences create a recurrence: `bit[i+16] = bit[i] + (data[i+1] - data[i])`. Brute-force ~4000-8000 valid initial 16-bit windows; each determines the entire bit sequence. See [patterns-ctf-3.md](patterns-ctf-3.md#sliding-window-popcount-differential-propagation-bearcatctf-2026).

### Ruby/Perl Polyglot Constraint Satisfaction
**Pattern:** Single file valid in both Ruby and Perl, each imposing different constraints on a key. Exploits `=begin`/`=end` (Ruby block comment) vs `=begin`/`=cut` (Perl POD) to run different code per interpreter. Intersect constraints from both languages to recover the unique key. See [languages-platforms.md](languages-platforms.md#rubyperl-polyglot-constraint-satisfaction-bearcatctf-2026).

### Verilog/Hardware RE
**Pattern:** Verilog HDL source for state machines with hidden conditions gated on shift register history. Analyze `always @(posedge clk)` blocks and `case` statements to find correct input sequences. See [languages-platforms.md](languages-platforms.md#veriloghardware-reverse-engineering-srdnlenctf-2026).

### Custom binfmt Kernel Module with RC4 Flat Binaries
**Pattern:** Kernel module registers binfmt handler for encrypted flat binaries. Reverse the `.ko` to find RC4 key (in `movabs` immediates), decrypt the flat binary, import at the fixed virtual address from the module's `vm_mmap` call. See [patterns-ctf.md](patterns-ctf.md#custom-binfmt-kernel-module-with-rc4-flat-binaries-bsidessf-2026).

### Hash-Resolved Imports / No-Import Ransomware
**Pattern:** Binary with zero visible imports resolves APIs via symbol name hashing at runtime. Skip the hash reversing — hook OpenSSL functions via `LD_PRELOAD` in Docker to capture AES keys directly. See [patterns-ctf.md](patterns-ctf.md#hash-resolved-imports-no-import-ransomware-bsidessf-2026).

### ELF Section Header Corruption for Anti-Analysis
**Pattern:** Corrupted section headers crash analysis tools but program headers are intact so binary runs normally. Patch `e_shoff` to zero or use `readelf -l` (program headers only). Flag hidden after corrupted sections with magic marker + XOR. See [patterns-ctf.md](patterns-ctf.md#elf-section-header-corruption-for-anti-analysis-bsidessf-2026).

### Brainfuck Character-by-Character Static Analysis
**Pattern:** BF programs validating input have `,` (read char) followed by `+` operations whose count = expected ASCII value. Extract increment counts per input position to recover expected input without execution. See [languages.md](languages.md#brainfuck-character-by-character-static-analysis-bsidessf-2026).

### Brainfuck Side-Channel via Read Count Oracle
**Pattern:** BF input validators read more bytes when a character is correct. Count `,` operations per candidate — highest read count = correct byte. Character-by-character recovery. See [languages.md](languages.md#brainfuck-side-channel-via-read-count-oracle-bsidessf-2026).

### Brainfuck Comparison Idiom Detection
**Pattern:** Compiled BF uses fixed idioms for equality checks (`<[-<->] +<[>-<[-]]>[-<+>]`). Instrument interpreter to detect patterns and extract comparison operands (expected flag bytes). See [languages.md](languages.md#brainfuck-comparison-idiom-detection-bsidessf-2026).

### Backdoored Shared Library Detection
Binary works in GDB but fails when run normally (suid)? Check `ldd` for non-standard libc paths, then `strings | diff` the suspicious vs. system library to find injected code/passwords. See [patterns-ctf.md](patterns-ctf.md#backdoored-shared-library-detection-via-string-diffing-hacklu-ctf-2012).

### Go Binary Reversing
Large static binary with `go.buildid`? Use GoReSym to recover function names (works even on stripped binaries). Go strings are `{ptr, len}` pairs — not null-terminated. Look for `main.main`, `runtime.gopanic`, channel ops (`runtime.chansend1`/`chanrecv1`). Use Ghidra golang-loader plugin for best results. See [languages-compiled.md](languages-compiled.md#go-binary-reversing).

### Go Binary UUID Patching for C2 Enumeration
**Pattern:** Go C2 client with UUID from `-ldflags -X`. Binary-patch UUID bytes (same length), register with C2, enumerate clients/files via API. See [languages-compiled.md](languages-compiled.md#go-binary-uuid-patching-for-c2-client-enumeration-bsidessf-2026).

### D Language Binary Reversing
D language binaries have unique symbol mangling (not C++ style). Template-heavy, many function variants. Look for `_D` prefix in symbols. See [languages-compiled.md](languages-compiled.md#d-language-binary-reversing-csaw-ctf-2016).

### Rust Binary Reversing
Binary with `core::panicking` strings and `_ZN` mangled symbols? Use `rustfilt` for demangling. Panic messages contain source paths and line numbers — `strings binary | grep "panicked"` is the fastest approach. Option/Result enums use discriminant byte (0=None/Err, 1=Some/Ok). See [languages-compiled.md](languages-compiled.md#rust-binary-reversing).

### Frida Dynamic Instrumentation
Hook runtime functions without modifying binary. `frida -f ./binary -l hook.js` to spawn with instrumentation. Hook `strcmp`/`memcmp` to capture expected values, bypass anti-debug by replacing `ptrace` return value, scan memory for flag patterns, replace validation functions. See [tools-dynamic.md](tools-dynamic.md#frida-dynamic-instrumentation).

### Frida Firebase Cloud Functions Bypass
**Pattern:** Android app validates via Firebase Cloud Functions. Post-login Frida hook constructs valid payload (UID + value + timestamp) and calls Cloud Function directly, bypassing QR/payment validation. See [languages-platforms.md](languages-platforms.md#frida-firebase-cloud-functions-bypass-bsidessf-2026).

### angr Symbolic Execution
Automatic path exploration to find inputs satisfying constraints. Load binary with `angr.Project`, set find/avoid addresses, call `simgr.explore()`. Constrain input to printable ASCII and known prefix for faster solving. Hook expensive functions (crypto, I/O) to prevent path explosion. See [tools-dynamic.md](tools-dynamic.md#angr-symbolic-execution).

### Qiling Emulation
Cross-platform binary emulation with OS-level support (syscalls, filesystem). Emulate Linux/Windows/ARM/MIPS binaries on any host. No debugger artifacts — bypasses all anti-debug by default. Hook syscalls and addresses with Python API. See [tools-dynamic.md](tools-dynamic.md#qiling-framework-cross-platform-emulation).

### VMProtect / Themida Analysis
VMProtect virtualizes code into custom bytecode. Identify VM entry (pushad-like), find handler table (large indirect jump), trace handlers dynamically. For CTF, focus on tracing operations on input rather than full devirtualization. Themida: dump at OEP with ScyllaHide + Scylla. See [tools-advanced.md](tools-advanced.md#vmprotect-analysis).

### Binary Diffing
BinDiff and Diaphora compare two binaries to highlight changes. Essential when challenge provides patched/original versions. Export from IDA/Ghidra, diff to find vulnerability or hidden functionality. See [tools-advanced.md](tools-advanced.md#binary-diffing).

### Advanced GDB (pwndbg, rr)
pwndbg: `context`, `vmmap`, `search -s "flag{"`, `telescope $rsp`. GEF alternative. Reverse debugging with `rr record`/`rr replay` — step backward through execution. Python scripting for brute-force and automated tracing. See [tools-advanced.md](tools-advanced.md#advanced-gdb-techniques).

### macOS / iOS Reversing
Mach-O binaries: `otool -l` for load commands, `class-dump` for Objective-C headers. Swift: `swift demangle` for symbols. iOS apps: decrypt FairPlay DRM with frida-ios-dump, bypass jailbreak detection with Frida hooks. Re-sign patched binaries with `codesign -f -s -`. See [platforms.md](platforms.md#macos-ios-reversing).

### Embedded / IoT Firmware RE
`binwalk -Me firmware.bin` for recursive extraction. Hardware: UART/JTAG/SPI flash for firmware dumps. Filesystems: SquashFS (`unsquashfs`), JFFS2, UBI. Emulate with QEMU: `qemu-arm -L /usr/arm-linux-gnueabihf/ ./binary`. See [platforms.md](platforms.md#embedded-iot-firmware-re).

### Kernel Driver Reversing
Linux `.ko`: find ioctl handler via `file_operations` struct, trace `copy_from_user`/`copy_to_user`. Debug with QEMU+GDB (`-s -S`). eBPF: `bpftool prog dump xlated`. Windows `.sys`: find `DriverEntry` → `IoCreateDevice` → IRP handlers. See [platforms.md](platforms.md#kernel-driver-reversing).

### Game Engine Reversing
Unreal: extract .pak with UnrealPakTool, reverse Blueprint bytecode with FModel. Unity Mono: decompile Assembly-CSharp.dll with dnSpy. Anti-cheat (EAC, BattlEye, VAC): identify system, bypass specific check. Lua games: `luadec`/`unluac` for bytecode. See [platforms.md](platforms.md#game-engine-reversing).

### Swift / Kotlin Binary Reversing
Swift: `swift demangle` symbols, protocol witness tables for dispatch, `__swift5_*` sections. Kotlin/JVM: coroutines compile to state machines in `invokeSuspend`, `jadx` with Kotlin mode for best decompilation. Kotlin/Native: LLVM backend, looks like C++ in disassembly. See [languages-compiled.md](languages-compiled.md#swift-binary-reversing).

### INT3 Patch + Coredump Brute-Force Oracle
Patch `0xCC` (INT3) after transform output, enable core dumps, brute-force each input character by extracting computed state from coredump via `strings`. Avoids full reverse of transformation. See [patterns.md](patterns.md#int3-patch-coredump-brute-force-oracle-pwn2win-2016).

### Signal Handler Chain + LD_PRELOAD Oracle
Binary uses signal handler chains for per-character password validation. Hook `signal()` via LD_PRELOAD -- the call to install the next handler confirms the current character is correct. See [patterns.md](patterns.md#signal-handler-chain-ldpreload-oracle-nuit-du-hack-2016).

### Font Ligature Exploitation
Custom OpenType font maps multi-character ligature sequences to single glyphs; reverse the GSUB table to decode hidden messages. See [patterns-ctf-3.md](patterns-ctf-3.md#opentype-font-ligature-exploitation-for-hidden-messages-hack-the-vote-2016).

### Instruction Counter as Cryptographic State
**Pattern:** Hand-written assembly uses a dedicated register (e.g., `r12`) as an instruction counter incremented after nearly every instruction. The counter feeds into XOR/ROL/multiply transformations on input bytes, making transformation path-dependent. Byte-by-byte brute force with Unicorn emulation recovers the flag. See [patterns-ctf-3.md](patterns-ctf-3.md#instruction-counter-as-cryptographic-state-metactf-flash-2026).

### Burrows-Wheeler Transform Inversion
Invert BWT without terminator character by trying all possible row indices. Standard `bwtool` or manual column-sorting reconstruction. See [patterns-ctf-3.md](patterns-ctf-3.md#burrows-wheeler-transform-inversion-without-terminator-asis-ctf-finals-2016).

### FRACTRAN Program Inversion
Esoteric language using iterated fraction multiplication. Invert by swapping numerator/denominator in fraction table, run output backward. I/O encoded as prime factorization exponents. See [languages.md](languages.md#fractran-program-inversion-boston-key-party-2016).

### Opcode-Only Trace Reconstruction
Execution traces with only opcodes (no data) still leak info through branch decisions. Sorting algorithm comparisons reveal element ordering. Reconstruct by deduplicating trace, splitting into basic blocks. See [tools-dynamic.md](tools-dynamic.md#opcode-only-trace-reconstruction-0ctf-2016).

### Thread Race Signed Integer Overflow
Game binary with thread-unsafe skill lock. Race between skill selection and damage calculation; `cdqe` sign-extends 0xFFFFFFFF to -1 (signed), causing HP overflow on subtraction. See [patterns-ctf-3.md](patterns-ctf-3.md#thread-race-condition-with-signed-integer-overflow-codegate-2017).

### ESP32/Xtensa Firmware Reversing
No IDA support — use radare2 + ESP-IDF ROM linker script (`esp32.rom.ld`) for symbol resolution. Cross-reference with public ESP-IDF HTTP server examples to identify app logic. See [patterns-ctf-3.md](patterns-ctf-3.md#esp32xtensa-firmware-reversing-with-rom-symbol-map-insomnihack-2017).

### Custom VM Bytecode Lifting to LLVM IR
Transpile custom VM bytecode to LLVM IR, then use `opt -O3` to simplify (inlining, constant folding, dead code elimination). Reduces 1300 lines to ~150 lines, revealing the underlying algorithm. See [tools-advanced.md](tools-advanced.md#custom-vm-bytecode-lifting-to-llvm-ir-google-ctf-2017).

### SIGFPE Signal Handler Side-Channel
SIGFPE signal handlers create implicit control flow invisible to static analysis. Count SIGFPE signals via `strace -e signal=SIGFPE` per candidate character -- correct characters produce more signals. See [anti-analysis.md](anti-analysis.md#sigfpe-signal-handler-side-channel-via-strace-counting-plaidctf-2017).

### Batch Crackme Automation via objdump
Mass crackme challenges (100s of binaries) with identical structure: script `objdump` to extract CMP immediates and add/sub arithmetic sequences, then reverse-compute keys algebraically without execution. See [patterns-ctf-3.md](patterns-ctf-3.md#batch-crackme-automation-via-objdump-pattern-extraction-def-con-2017).

### Android DEX Runtime Bytecode Patching
Native JNI library patches Dalvik bytecode in memory via `/proc/self/maps` + `mprotect` + XOR. Static APK analysis alone is insufficient -- extract XOR key and offsets from the native `.so` to reconstruct the runtime DEX. See [languages-platforms.md](languages-platforms.md#android-dex-runtime-bytecode-patching-via-procselfmaps-google-ctf-2017).

### Fork + Pipe + Dead Branch Anti-Analysis
Fork/pipe IPC where parent writes data and exits, child reads and continues. Real validation hidden in a dead branch (always-false comparison). `strace` reveals the fork/pipe pattern; patch the comparison constant to reach hidden code. See [patterns-ctf-3.md](patterns-ctf-3.md#fork-pipe-dead-branch-anti-analysis-rctf-2017).


# languages-compiled

# CTF Reverse - Compiled Language Reversing (Go, Rust)

## Table of Contents
- [Go Binary Reversing](#go-binary-reversing)
  - [Recognition](#recognition)
  - [Symbol Recovery](#symbol-recovery)
  - [Go Memory Layout](#go-memory-layout)
  - [Goroutine and Concurrency Analysis](#goroutine-and-concurrency-analysis)
  - [Common Go Patterns in Decompilation](#common-go-patterns-in-decompilation)
  - [Go Binary Reversing Workflow](#go-binary-reversing-workflow)
  - [Go Binary UUID Patching for C2 Client Enumeration (BSidesSF 2026)](#go-binary-uuid-patching-for-c2-client-enumeration-bsidessf-2026)
- [Rust Binary Reversing](#rust-binary-reversing)
  - [Rust Recognition](#rust-recognition)
  - [Symbol Demangling](#symbol-demangling)
  - [Common Rust Patterns in Decompilation](#common-rust-patterns-in-decompilation)
  - [Rust-Specific Analysis Tools](#rust-specific-analysis-tools)
- [Swift Binary Reversing](#swift-binary-reversing)
- [Kotlin / JVM Binary Reversing](#kotlin--jvm-binary-reversing)
  - [JVM Bytecode (Android/Server)](#jvm-bytecode-androidserver)
  - [Kotlin/Native](#kotlinnative)
- [D Language Binary Reversing (CSAW CTF 2016)](#d-language-binary-reversing-csaw-ctf-2016)
- [C++ Binary Reversing (Quick Reference)](#c-binary-reversing-quick-reference)
  - [vtable Reconstruction](#vtable-reconstruction)
  - [RTTI (Run-Time Type Information)](#rtti-run-time-type-information)
  - [Standard Library Patterns](#standard-library-patterns)

---

## Go Binary Reversing

Go binaries are increasingly common in CTF challenges due to Go's popularity for CLI tools, network services, and malware.

### Recognition

```bash
# Detect Go binary
file binary | grep -i "go"
strings binary | grep "go.buildid"
strings binary | grep "runtime.gopanic"

# Go version embedded in binary
strings binary | grep "^go1\."
```

**Key indicators:**
- Very large static binary (even "hello world" is ~2MB)
- Embedded `go.buildid` string
- `runtime.*` symbols (even in stripped binaries, some remain)
- `main.main` as entry point (not `main`)
- Strings like `GOROOT`, `GOPATH`, `/usr/local/go/src/`

### Symbol Recovery

Go embeds rich type and function information even in stripped binaries:

```bash
# GoReSym - recovers function names, types, interfaces from Go binaries
# https://github.com/mandiant/GoReSym
./GoReSym -d binary > symbols.json

# Parse output
python3 -c "
import json
with open('symbols.json') as f:
    data = json.load(f)
for fn in data.get('UserFunctions', []):
    print(f\"{fn['Start']:#x}  {fn['FullName']}\")
"
```

**Ghidra with golang-loader:**
```bash
# Install: Ghidra → Window → Script Manager → search "golang"
# Or use: https://github.com/getCUJO/ThreatFox/tree/main/ghidra-golang
# Recovers function names, string references, interface tables
```

**redress (Go binary analysis):**
```bash
# https://github.com/goretk/redress
redress -src binary         # Reconstruct source tree
redress -pkg binary         # List packages
redress -type binary        # List types and methods
redress -interface binary   # List interfaces
```

### Go Memory Layout

Understanding Go's data structures in decompilation:

```c
# String: {pointer, length} (16 bytes on 64-bit)
# NOT null-terminated! Length field is critical.
struct GoString {
    char *ptr;    // pointer to UTF-8 data
    int64 len;    // byte length
};

# Slice: {pointer, length, capacity} (24 bytes on 64-bit)
struct GoSlice {
    void *ptr;    // pointer to backing array
    int64 len;    // current length
    int64 cap;    // allocated capacity
};

# Interface: {type_descriptor, data_pointer} (16 bytes)
struct GoInterface {
    void *type;   // points to type metadata (itab for non-empty interface)
    void *data;   // points to actual value
};

# Map: pointer to runtime.hmap struct
# Channel: pointer to runtime.hchan struct
```

**In Ghidra/IDA:** When you see a function taking `(ptr, int64)` — it's likely a Go string. Three-field `(ptr, int64, int64)` is a slice.

### Goroutine and Concurrency Analysis

```bash
# Identify goroutine spawns in disassembly
strings binary | grep "runtime.newproc"
# newproc1 is the internal goroutine creation function

# In GDB with Go support:
gdb ./binary
(gdb) source /usr/local/go/src/runtime/runtime-gdb.py
(gdb) info goroutines          # List all goroutines
(gdb) goroutine 1 bt          # Backtrace for goroutine 1
```

**Channel operations in disassembly:**
- `runtime.chansend1` → `ch <- value`
- `runtime.chanrecv1` → `value = <-ch`
- `runtime.selectgo` → `select { case ... }`
- `runtime.closechan` → `close(ch)`

### Common Go Patterns in Decompilation

**Defer mechanism:**
- `runtime.deferproc` → registers deferred function
- `runtime.deferreturn` → executes deferred functions at function exit
- Deferred calls execute in LIFO order — relevant for cleanup/crypto key wiping

**Error handling (the `if err != nil` pattern):**
```text
# In disassembly, this appears as:
# call some_function        → returns (result, error) as two values
# test rax, rax             → check if error (second return value) is nil
# jne error_handler
```

**String concatenation:**
- `runtime.concatstrings` → `s1 + s2 + s3`
- `fmt.Sprintf` → formatted string building
- Look for format strings in `.rodata`: `"%s%d"`, `"%x"`

**Common stdlib patterns in CTF:**
```go
// Crypto operations → look for these in strings/imports:
// "crypto/aes", "crypto/cipher", "crypto/sha256", "encoding/hex", "encoding/base64"

// Network operations:
// "net/http", "net.Dial", "bufio.NewReader"

// File operations:
// "os.Open", "io.ReadAll", "os.ReadFile"
```

### Go Binary Reversing Workflow

```bash
1. file binary                          # Confirm Go, get arch
2. GoReSym -d binary > syms.json       # Recover symbols
3. strings binary | grep -i flag        # Quick win check
4. Load in Ghidra with golang-loader    # Apply recovered symbols
5. Find main.main                       # Entry point
6. Identify string comparisons          # GoString {ptr, len} pairs
7. Trace crypto operations              # crypto/* package usage
8. Check for embedded resources         # embed.FS in Go 1.16+
```

**Go embed.FS (Go 1.16+):** Binaries can embed files at compile time:
```bash
# Look for embedded file data
strings binary | grep "embed"
# Embedded files appear as raw data in the binary
# Search for known file signatures (PK for zip, PNG header, etc.)
```

**Key insight:** Go's runtime embeds extensive metadata even in stripped binaries. Use GoReSym before any manual analysis — it often recovers 90%+ of function names, making decompilation dramatically easier. Go strings are `{ptr, len}` tuples, not null-terminated — Ghidra's default string analysis will miss them without the golang-loader plugin.

**Detection:** Large static binary (2MB+ for simple programs), `go.buildid`, `runtime.gopanic`, source paths like `/home/user/go/src/`.

### Go Binary UUID Patching for C2 Client Enumeration (BSidesSF 2026)

**Pattern (see-two):** A Go-compiled C2 client has a UUID embedded via `-ldflags -X`. The C2 server uses mTLS for authentication. To enumerate other clients and their files, patch the UUID to register as a new client, then use the C2 API to list all clients and download their exfiltrated files.

**Approach:**
1. Extract embedded UUID from Go build metadata: `go version -m client_binary`
2. Binary-patch the UUID (simple byte replacement — Go strings have fixed-length backing arrays)
3. Register with the C2 server using the patched binary (mTLS certs are embedded or in distfiles)
4. Enumerate clients via API: `GET /api/clients` or iterate known endpoints
5. List and download files from each client's GCS bucket or file store
6. Grep downloaded files for the flag

```bash
# Extract Go build info
go version -m ./client_binary | grep ldflags
# Output shows: -X main.clientUUID=<uuid>

# Patch UUID in binary (replace old UUID bytes with new UUID)
python3 -c "
import sys
data = open('client_binary', 'rb').read()
old_uuid = b'original-uuid-value-here'
new_uuid = b'attacker-uuid-value-here'
patched = data.replace(old_uuid, new_uuid)
open('client_patched', 'wb').write(patched)
"
chmod +x client_patched
./client_patched --register
```

**Key insight:** Go binaries embed string values from `-ldflags -X` directly in the binary data section. Since Go strings are `{ptr, len}` pairs pointing to backing byte arrays, replacing the UUID bytes (same length) produces a valid patched binary. The mTLS certificates authenticate the client to the server but don't bind to a specific UUID.

**References:** BSidesSF 2026 "see-two"

---

## Rust Binary Reversing

Rust binaries are common in modern CTFs, especially for crypto, systems, and security tooling challenges.

### Rust Recognition

```bash
# Detect Rust binary
strings binary | grep -c "rust"
strings binary | grep "rustc"             # Compiler version
strings binary | grep "/rustc/"           # Source paths
strings binary | grep "core::panicking"   # Panic infrastructure
```

**Key indicators:**
- `core::panicking::panic` in strings
- Mangled symbols starting with `_ZN` (Itanium ABI) — e.g., `_ZN4main4main17h...`
- `.rustc` section in ELF
- References to `/rustc/<commit_hash>/library/`
- Large binary size (Rust statically links by default)

### Symbol Demangling

```bash
# Rust uses Itanium ABI mangling (same as C++)
# rustfilt demangles Rust-specific symbols
cargo install rustfilt
nm binary | rustfilt | grep "main"

# Or use c++filt (works for most Rust symbols)
nm binary | c++filt | grep "main"

# In Ghidra: Window → Script Manager → search "Demangler"
# Enable "DemangleAllScript" for automatic demangling
```

### Common Rust Patterns in Decompilation

**Option/Result enum:**
```text
# Option<T> in memory: {discriminant (0=None, 1=Some), value}
# Result<T, E>: {discriminant (0=Ok, 1=Err), union{ok_val, err_val}}

# In disassembly:
# cmp byte [rbp-0x10], 0    → check if None/Err
# je handle_none_case
```

**Vec<T> (same as Go slice):**
```c
struct RustVec {
    void *ptr;      // heap pointer
    uint64 cap;     // capacity
    uint64 len;     // length
};
```

**String / &str:**
```text
# String (owned): {ptr, capacity, length} — 24 bytes, heap-allocated
# &str (borrowed): {ptr, length} — 16 bytes, can point anywhere

# In decompilation, look for:
# alloc::string::String::from    → String creation
# core::str::from_utf8           → byte slice to str
```

**Iterator chains:**
```text
# .iter().map().filter().collect() compiles to loop fusion
# In disassembly: tight loop with inlined closures
# Look for: core::iter::adapters::map, filter, etc.
```

**Panic unwinding:**
```bash
# Panic strings reveal source locations and error messages
strings binary | grep "panicked at"
strings binary | grep "called .unwrap().. on"
# These often contain file paths, line numbers, and variable names
```

### Rust-Specific Analysis Tools

```bash
# cargo-bloat: analyze binary size by function
cargo install cargo-bloat
cargo bloat --release -n 50

# Ghidra Rust helper scripts
# https://github.com/AmateursCTF/ghidra-rust (community scripts for Rust RE)
```

**Key insight:** Rust panic messages are goldmines — they contain source file paths, line numbers, and descriptive error strings even in release builds. Always `strings binary | grep "panicked"` first. Rust's monomorphization means generic functions get duplicated per type — expect many similar-looking functions.

**Detection:** `core::panicking`, `.rustc` section, `/rustc/` paths, `_ZN` mangled symbols with Rust-style module paths.

---

## Swift Binary Reversing

See [platforms.md](platforms.md#swift-binary-reversing) for full Swift reversing guide including demangling, runtime structures, and Ghidra integration. Key quick reference:

```bash
# Detect Swift binary
strings binary | grep "swift"
otool -l binary | grep "swift"

# Demangle Swift symbols
swift demangle 's14MyApp0A8ClassC10checkInput6resultSbSS_tF'
# → MyApp.MyAppClass.checkInput(result: String) -> Bool

# Key runtime functions: swift_allocObject, swift_release, swift_once
# String: small (≤15 bytes inline) or large (heap pointer + length)
# Protocol witness tables = dynamic dispatch (like vtables)
```

**Detection:** `__swift5_*` sections in Mach-O, `swift_` runtime symbols, `s` prefix in mangled names.

---

## Kotlin / JVM Binary Reversing

Kotlin compiles to JVM bytecode or native (via Kotlin/Native). Common in Android and server-side CTF.

### JVM Bytecode (Android/Server)

```bash
# Detect Kotlin
strings classes.dex | grep "kotlin"
# Look for: kotlin.Metadata annotation, kotlin/jvm/internal/*

# Decompile
jadx classes.dex                     # Best for Kotlin bytecode
cfr classes.jar --kotlin             # CFR with Kotlin mode
fernflower classes.jar output/       # IntelliJ's decompiler

# Kotlin-specific patterns in decompiled output:
# - Companion objects: ClassName$Companion
# - Data classes: copy(), component1(), component2(), toString()
# - Coroutines: ContinuationImpl, invokeSuspend, state machine
# - Null checks: Intrinsics.checkNotNull() everywhere
# - When expression: compiled as tableswitch/lookupswitch
# - Sealed classes: instanceof checks in chain
```

**Kotlin coroutines in disassembly:**
```text
# Coroutines compile to state machines:
# invokeSuspend(result) {
#     switch (this.label) {
#         case 0: this.label = 1; return suspendFunction();
#         case 1: processResult(result); return Unit;
#     }
# }
# Each suspend point becomes a state in the switch.
# Follow the state machine to understand async flow.
```

### Kotlin/Native

```bash
# Kotlin/Native produces platform binaries (no JVM)
# Recognize by: konan, kotlin.native strings
strings binary | grep "konan"

# Much harder to reverse — no reflection metadata
# Uses LLVM backend, looks similar to C/C++ in disassembly
# Key functions: InitRuntime, DeinitRuntime, CreateStablePointer
# Memory management: automatic reference counting (not GC)
```

**Detection:** `kotlin.Metadata` annotations (JVM), `konan` strings (Native), `kotlin/` package paths.

---

## D Language Binary Reversing (CSAW CTF 2016)

D language binaries have unique symbol mangling different from C++. Template instantiation at compile-time produces many function variants.

```bash
# Recognition: D binaries use different mangling than C++
# Symbols contain "_D" prefix and numeric length-prefixed names
# Example: _D4mainQaFNaNbNfZv

# Symbol demangling:
# GDB: set language d
# Radare2: export names show demangled D symbols
# Online: dlang.org/phobos/core_demangle.html

# Common D binary patterns:
# - Templates instantiated at compile-time: enc!("111"), enc!("222"), ...
# - Garbage collector references (GC.malloc, GC.free)
# - Phobos standard library functions (_D3std...)
# - String processing: std.string, std.conv.to

# Reversing a D cipher (XOR with cycling key):
def reverse_d_cipher(encrypted, num_functions=500):
    """D binaries may chain multiple transformation functions.
    Each function XORs with key character, then XORs with key length.
    Process in reverse order."""
    result = encrypted[:]
    for i in range(num_functions - 1, -1, -1):
        key = str(i) * 3  # e.g., "499499499" for function enc!("499")
        key_len = len(key)
        for j in range(len(result)):
            result[j] ^= key_len
            result[j] ^= ord(key[j % key_len])
    return bytes(result)
```

**Key insight:** D binaries are rare in CTFs but identifiable by `_D` symbol prefixes and Phobos library references. The compile-time template system means D functions may be duplicated hundreds of times with different parameters — look for patterns like `enc!("N")` where N varies.

---

## C++ Binary Reversing (Quick Reference)

While C++ RE is well-covered by general tools, these patterns are CTF-specific:

### vtable Reconstruction

```text
# Virtual function tables (vtables):
# First 8 bytes of object → pointer to vtable
# vtable entries: [typeinfo_ptr, destructor, method1, method2, ...]
# In Ghidra: Data → Create Pointer at vtable address

# Identify polymorphic dispatch:
# mov rax, [rdi]           # Load vtable from this pointer
# call [rax + 0x18]        # Call 4th virtual method (0x18/8 = 3rd after typeinfo+dtor)
```

### RTTI (Run-Time Type Information)

```bash
# If not stripped, RTTI reveals class hierarchy
strings binary | grep -E "^[0-9]+[A-Z]"   # Mangled type names
c++filt _ZTI7MyClass                        # → typeinfo for MyClass

# In Ghidra: search for vtable references, follow typeinfo pointer
# typeinfo struct: {vtable_for_typeinfo, name_string, base_class_ptr}
```

### Standard Library Patterns

```text
std::string (libstdc++):
  SSO (Small String Optimization): inline buffer for ≤15 chars
  Layout: {char* ptr, size_t size, union{size_t cap, char buf[16]}}

std::vector<T>:
  {T* begin, T* end, T* capacity_end}

std::map<K,V>:
  Red-black tree: each node has {left, right, parent, color, key, value}

std::unordered_map<K,V>:
  Hash table: {bucket_array, size, load_factor_max, ...}
```


# languages-platforms

# CTF Reverse - Platform & Framework-Specific Techniques

## Table of Contents
- [Roblox Place File Analysis](#roblox-place-file-analysis)
- [Godot Game Asset Extraction](#godot-game-asset-extraction)
- [Rust serde_json Schema Recovery](#rust-serde_json-schema-recovery)
- [Android JNI RegisterNatives Obfuscation (HTB WonderSMS)](#android-jni-registernatives-obfuscation-htb-wondersms)
- [Android DEX Runtime Bytecode Patching via /proc/self/maps (Google CTF 2017)](#android-dex-runtime-bytecode-patching-via-procselfmaps-google-ctf-2017)
- [Frida Firebase Cloud Functions Bypass (BSidesSF 2026)](#frida-firebase-cloud-functions-bypass-bsidessf-2026)
- [Verilog/Hardware Reverse Engineering (srdnlenCTF 2026)](#veriloghardware-reverse-engineering-srdnlenctf-2026)
- [Prefix-by-Prefix Hash Reversal (Nullcon 2026)](#prefix-by-prefix-hash-reversal-nullcon-2026)
- [Ruby/Perl Polyglot Constraint Satisfaction (BearCatCTF 2026)](#rubyperl-polyglot-constraint-satisfaction-bearcatctf-2026)
- [Electron App + Native Binary Reversing (RootAccess2026)](#electron-app--native-binary-reversing-rootaccess2026)
- [Node.js npm Package Runtime Introspection (RootAccess2026)](#nodejs-npm-package-runtime-introspection-rootaccess2026)
- [Frida Android Certificate Pinning Bypass (h1702ctf 2017)](#frida-android-certificate-pinning-bypass-h1702ctf-2017)
- [Android Anti-Debug: TracerPid, su Binary, System Properties (h1702ctf 2017)](#android-anti-debug-tracerpid-su-binary-system-properties-h1702ctf-2017)
- [Android Log-Based Key Extraction (HackIT 2017)](#android-log-based-key-extraction-hackit-2017)
- [Native JNI Key Extraction via Memory Dump and Smali Patching (HackIT 2017)](#native-jni-key-extraction-via-memory-dump-and-smali-patching-hackit-2017)
- [IBM AS/400 SAVF File EBCDIC Decoding (EKOPARTY 2017)](#ibm-as400-savf-file-ebcdic-decoding-ekoparty-2017)
- [Intel SGX Enclave Reverse Engineering (Pwn2Win 2017)](#intel-sgx-enclave-reverse-engineering-pwn2win-2017)

For core language reversing (Python, BF/esolangs, DOS, Unity, OPAL), see [languages.md](languages.md).
For Go and Rust binary reversing, see [languages-compiled.md](languages-compiled.md).

---

## Roblox Place File Analysis

**Pattern (MazeRunna, 0xFun 2026):** Roblox game with flag hidden in older version; latest version contains decoy.

**Version history via Asset Delivery API:**
```bash
# Extract placeId and universeId from game page HTML
# Query each version (requires .ROBLOSECURITY cookie):
curl -H "Cookie: .ROBLOSECURITY=..." \
  "https://assetdelivery.roblox.com/v2/assetId/{placeId}/version/1"
# Download location URL → place_v1.rbxlbin
```

**Binary format parsing:** `.rbxlbin` files contain chunks:
- **INST** — class buckets and referent IDs
- **PROP** — per-instance fields (including `Script.Source`)
- **PRNT** — parent-child relationships (object tree)

Decode chunk payloads, walk PROP entries for `Source` field, dump `Script.Source` / `LocalScript.Source` per version, then diff.

**Key lesson:** Always check version history. Latest version may contain decoy flag while real flag is in an older version. Diff script sources across versions.

---

## Godot Game Asset Extraction

**Pattern (Steal the Xmas):** Encrypted Godot .pck packages.

**Tools:**
- [gdsdecomp](https://github.com/GDRETools/gdsdecomp) - Extract Godot packages
- [KeyDot](https://github.com/Titoot/KeyDot) - Extract encryption key from Godot executables

**Workflow:**
1. Run KeyDot against game executable → extract encryption key
2. Input key into gdsdecomp
3. Extract and open project in Godot editor
4. Search scripts/resources for flag data

---

## Rust serde_json Schema Recovery

**Pattern (Curly Crab, PascalCTF 2026):** Rust binary reads JSON from stdin, deserializes via serde_json, prints success/failure emoji.

**Approach:**
1. Disassemble serde-generated `Visitor` implementations
2. Each visitor's `visit_map` / `visit_seq` reveals expected keys and types
3. Look for string literals in deserializer code (field names like `"pascal"`, `"CTF"`)
4. Reconstruct nested JSON schema from visitor call hierarchy
5. Identify value types from visitor method names: `visit_str` = string, `visit_u64` = number, `visit_bool` = boolean, `visit_seq` = array

```json
{"pascal":"CTF","CTF":2026,"crab":{"I_":true,"cr4bs":1337,"crabby":{"l0v3_":["rust"],"r3vv1ng_":42}}}
```

**Key insight:** Flag is the concatenation of JSON keys in schema order. Reading field names in order reveals the flag.

---

## Android JNI RegisterNatives Obfuscation (HTB WonderSMS)

**Pattern:** Android app loads native library with `System.loadLibrary()`, but uses `RegisterNatives` in `JNI_OnLoad` instead of standard JNI naming convention (`Java_com_pkg_Class_method`). This hides which C++ function handles each Java native method.

**Identification:**
```java
// In decompiled Java (jadx):
static { System.loadLibrary("audio"); }
private final native ProcessedMessage processMessage(SmsMessage msg);
```
Standard JNI would have a symbol `Java_com_rloura_wondersms_SmsReceiver_processMessage`. If that symbol is missing from the `.so`, `RegisterNatives` is being used.

**Finding the real handler in Ghidra:**
1. Locate `JNI_OnLoad` (exported symbol, always present)
2. Trace to `RegisterNatives(env, clazz, methods, count)` call
3. The `methods` array contains `{name, signature, fnPtr}` structs
4. Follow `fnPtr` to find the actual native function

```c
// JNI_OnLoad registers functions manually:
static JNINativeMethod methods[] = {
    {"processMessage", "(Landroid/telephony/SmsMessage;)LProcessedMessage;", (void*)real_handler}
};
(*env)->RegisterNatives(env, clazz, methods, 1);
```

**Architecture selection for analysis:**
```bash
# x86_64 gives best Ghidra decompilation (most similar to desktop code)
# Extract from APK:
unzip WonderSMS.apk -d extracted/
ls extracted/lib/x86_64/  # Prefer this over arm64-v8a for static analysis
```

**Key insight:** `RegisterNatives` is a deliberate obfuscation technique — it decouples Java method names from native symbol names, making it impossible to find handlers by string search alone. Always check `JNI_OnLoad` first when reversing Android native libraries with stripped symbols.

**Detection:** Native method declared in Java + no matching JNI symbol in `.so` + `JNI_OnLoad` present. The library is typically stripped (no debug symbols).

---

## Android DEX Runtime Bytecode Patching via /proc/self/maps (Google CTF 2017)

Native JNI library patches Dalvik bytecode in memory at runtime: reads `/proc/self/maps` to find loaded DEX, `mprotect`s it writable, then XOR-patches specific bytecode offsets.

```python
# Reconstruct the patched DEX offline:
# 1. Extract the embedded DEX from the APK
# 2. Find the XOR key and patch offsets in the native .so (IDA/Ghidra)
# 3. Apply the same patches to the static DEX
import struct

with open('classes.dex', 'rb') as f:
    dex = bytearray(f.read())

# Patch 144 bytes starting at offset found in .so
xor_key = 0x5A
for i in range(patch_offset, patch_offset + 144):
    dex[i] ^= xor_key

# 4. Recompute DEX checksum and SHA-1 hash
# 5. Decompile with jadx or baksmali
```

**Key insight:** Native libraries can modify DEX bytecode in memory via `/proc/self/maps` + `mprotect`, making static analysis of the APK alone insufficient. The XOR key and patch offsets must be extracted from the native `.so` to reconstruct the actual runtime DEX. Only works on Dalvik (API < 21), not ART.

---

## Frida Firebase Cloud Functions Bypass (BSidesSF 2026)

**Pattern (vinyl-drop, doremi):** Android app validates actions (QR codes, purchases) via Firebase Cloud Functions. The expected payload format includes the Firebase UID, a value, and a timestamp. Use Frida to hook the app post-login, construct a valid payload, and call the Cloud Function directly.

```javascript
// Frida hook to bypass QR validation
Java.perform(function() {
    var FirebaseFunctions = Java.use('com.google.firebase.functions.FirebaseFunctions');
    var FirebaseAuth = Java.use('com.google.firebase.auth.FirebaseAuth');

    // Get current user UID after login
    var auth = FirebaseAuth.getInstance();
    var uid = auth.getCurrentUser().getUid();

    // Construct valid payload: uid + amount + timestamp
    var unixMs = Java.use('java.lang.System').currentTimeMillis();
    var payload = uid + "+100+" + unixMs;

    // Call the Cloud Function directly
    var functions = FirebaseFunctions.getInstance();
    var data = Java.use('java.util.HashMap').$new();
    data.put("payload", payload);
    functions.getHttpsCallable("validateScanPayload").call(data);
});
```

**Key insight:** Firebase AppCheck and Cloud Functions rely on the client to construct valid payloads. Post-authentication, Frida can hook the app to call any Cloud Function with arbitrary parameters, bypassing client-side validation (QR scanning, payment processing, etc.).

**When to recognize:** Android app with `google-services.json`, Firebase dependencies in `build.gradle`, Cloud Function calls in decompiled code.

**References:** BSidesSF 2026 "vinyl-drop"

---

## Verilog/Hardware Reverse Engineering (srdnlenCTF 2026)

**Pattern (Rev Juice):** Verilog HDL source for a vending machine with hidden product unlocked by specific coin insertion and selection sequence.

**Approach:**
1. Analyze Verilog modules to understand state machine and history tracking
2. Identify hidden conditions (e.g., product 8 enabled only when `COINS_HISTORY` array has specific values at specific taps)
3. Build timing model for each action type (how many clock cycles each operation takes)
4. Work backward from required history values to construct the correct input sequence

**Timing model construction:**
```python
# Map each action to its cycle count (determined from Verilog state machines)
TIMING = {
    "insert_coin": 3,       # 3 cycles per coin insertion
    "select_success": 7,    # 7 cycles for successful product selection
    "select_fail": 5,       # 5 cycles for failed selection attempt
    "cancel_with_coins": 4, # 4 cycles for cancel when coins > 0
    "cancel_at_zero": 2,    # 2 cycles for cancel when coins = 0
}

# COINS_HISTORY is a shift register updated each cycle
# History tap requirements (from Verilog conditions):
# H[0]=1, H[7]=4, H[28]=H[33]=H[38]=6
# H[63]=H[73]=2, H[80]=9
# (H[19]+H[21]+H[56]+H[69]) mod 32 = 0
```

**Key insight:** Hardware challenges require understanding the exact timing model — each operation takes a specific number of clock cycles, and shift registers record history at fixed tap positions. Work backward from the required tap values to determine what action must have occurred at each cycle. The solution is often a specific sequence notation (e.g., `I9C_SP6_CNL_I2C_SP2_I6C_SP6_SP6_SP5_CNL_I4C_SP1`).

**Detection:** Look for `.v` or `.sv` (Verilog/SystemVerilog) files, `always @(posedge clk)` blocks, shift register patterns, and state machine `case` statements with hidden conditions gated on history values.

---

## Prefix-by-Prefix Hash Reversal (Nullcon 2026)

See [patterns-ctf-2.md](patterns-ctf-2.md#prefix-hash-brute-force-nullcon-2026) for the full technique. This section covers language-specific considerations.

**Language-specific notes:**
- Hash algorithm may be uncommon (MD2, custom) — don't need to identify it, just match outputs by running the binary
- Use `subprocess.run()` with `timeout=2` to handle binaries that hang on bad input
- For stripped binaries, check if `ltrace` reveals the hash function name (e.g., `MD2_Update`)

---

## Ruby/Perl Polyglot Constraint Satisfaction (BearCatCTF 2026)

**Pattern (Polly's Key):** A single file valid in both Ruby and Perl. Each language imposes different validation constraints on a 50-character key. Satisfy both simultaneously to decrypt the flag.

**Polyglot structure exploits:**
- Ruby: `=begin`...`=end` is a block comment
- Perl: `=begin`...`=cut` is POD (Plain Old Documentation), `=end` is ignored
- Different code runs in each language based on comment block boundaries

**Typical constraints:**
- **Ruby:** Character set must form a mathematical property (e.g., all 50 printable ASCII chars except `^` used exactly once, each satisfying `XOR(val, (val-16) % 257)` is a primitive root mod 257)
- **Perl:** Ordering constraint via insertion sort inversion count (hardcoded inversion table determines exact permutation)

**Solution approach:**
1. Find the valid character set (mathematical constraint from one language)
2. Use the ordering constraint (from other language) to determine exact arrangement
3. Compute key hash (e.g., MD5) and decrypt

```python
# Determine character ordering from inversion counts
def reconstruct_from_inversions(chars, inv_counts):
    result = []
    remaining = sorted(chars)
    for i in range(len(chars) - 1, -1, -1):
        # inv_counts[i] = number of elements to the left that are greater
        idx = inv_counts[i]
        result.insert(idx, remaining.pop(i))
    return result
```

**Key insight:** Polyglot files exploit language-specific comment/block syntax to run different code in each interpreter. The constraints from both languages intersect to uniquely determine the key. Identify which code runs in which language by testing the file with both interpreters and comparing behavior.

**Detection:** File that runs under multiple interpreters (`ruby file && perl file`). Challenge mentions "polyglot" or provides a file ending in `.rb` that also looks like Perl.

---

## Electron App + Native Binary Reversing (RootAccess2026)

**Pattern (Rootium Browser):** Electron desktop app bundles a native ELF/DLL binary for sensitive operations (vault, crypto, auth). The Electron layer is a wrapper; the real flag logic is in the native binary.

**Extraction workflow:**
1. **Unpack Electron ASAR archive:**
```bash
# Install ASAR tool
npm install -g @electron/asar

# Extract the app.asar archive
asar extract resources/app.asar app_extracted/
ls app_extracted/
```

2. **Locate native binary:** Search for ELF/DLL files called from JavaScript:
```bash
# Find native binaries
find app_extracted/ -name "*.node" -o -name "*.so" -o -name "*vault*" -o -name "*auth*"

# Check JS for child_process.spawn or ffi-napi calls
grep -r "spawn\|execFile\|ffi\|require.*native" app_extracted/
```

3. **Reverse the native binary** (XOR + rotation cipher example):
```python
def decrypt_password(encrypted_bytes, key):
    """Common pattern: XOR with constant + bit rotation + key XOR."""
    result = []
    for i, byte in enumerate(encrypted_bytes):
        decrypted = ((byte ^ 0x42) >> 3) ^ key[i % len(key)]
        result.append(chr(decrypted))
    return ''.join(result)

def decrypt_flag(encrypted_flag, password):
    """Flag uses password as key with position-dependent rotation."""
    result = []
    for i, byte in enumerate(encrypted_flag):
        key_byte = ord(password[i % len(password)])
        decrypted = ((byte ^ 0x7E) >> (i % 8)) ^ key_byte
        result.append(chr(decrypted))
    return ''.join(result)
```

**Key insight:** Electron apps are JavaScript wrapping native code. Extract with `asar`, then focus on the native binary. The JS layer often contains the password verification flow in plaintext, revealing what the native binary expects. Look for encrypted data in the `.data` or `.rodata` sections of the ELF.

**Detection:** `.asar` files in `resources/` directory, Electron framework files, `package.json` with electron dependency.

---

## Node.js npm Package Runtime Introspection (RootAccess2026)

**Pattern (RootAccess CLI):** Obfuscated npm package with RC4 encoding, control flow flattening, and flag split across multiple fragments. Static analysis is impractical — use runtime introspection instead.

**Dynamic analysis approach:**
```javascript
#!/usr/bin/env node

// 1. Load obfuscated modules
const cryptoMod = require('target-package/dist/lib/crypto.js');
const vaultMod = require('target-package/dist/lib/vault.js');

// 2. Enumerate all exported properties
for (const mod of [cryptoMod, vaultMod]) {
    for (const key of Object.keys(mod)) {
        const obj = mod[key];
        console.log(`Export: ${key}`);
        // List all methods including hidden ones
        const props = Object.getOwnPropertyNames(obj);
        const proto = Object.getOwnPropertyNames(obj.prototype || {});
        console.log('  Own:', props);
        console.log('  Proto:', proto);
    }
}

// 3. Extract flag fragments
const Engine = cryptoMod.CryptoEngine;
const total = Engine.getTotalFragments();
let flag = '';
for (let i = 1; i <= total; i++) {
    flag += Engine.getFragment(i);
}
console.log('Flag:', flag);

// 4. Check for hidden methods (common: __getFullFlag__, _debug, _raw)
const hidden = Object.getOwnPropertyNames(Engine)
    .filter(p => p.startsWith('__') || p.startsWith('_'));
console.log('Hidden methods:', hidden);
```

**Key insight:** Heavily obfuscated JavaScript (control flow flattening, RC4 string encoding, dead code) makes static analysis prohibitively slow. Runtime introspection via `Object.getOwnPropertyNames()` reveals all methods including hidden ones. The module's own decryption runs automatically when loaded — just call the decoded functions directly.

**Detection:** npm package with minified/obfuscated `dist/` directory, challenge says "reverse engineer the CLI tool", `package.json` with custom commands.

---

## Frida Android Certificate Pinning Bypass (h1702ctf 2017)

APK uses OkHttp `CertificatePinner` for SSL pinning. Rather than setting up a MITM proxy or patching the APK, use Frida to directly invoke native JNI methods on loaded classes.

```javascript
Java.perform(function() {
    var Requestor = Java.use("com.h1702ctf.ctfone.Requestor");
    console.log("hName: " + Requestor.hName());
    console.log("hVal: " + Requestor.hVal());
});
```

Calling `hName()` and `hVal()` returns the HTTP header name and value needed to bypass the server-side check — no cert pinning bypass required because the secret is in the class methods themselves.

**Key insight:** Frida can invoke native JNI methods directly on a loaded class — no need to bypass cert pinning at network layer or fully reverse the native binary.

**References:** h1702ctf 2017

---

## Android Anti-Debug: TracerPid, su Binary, System Properties (h1702ctf 2017)

Native ARM code implements three sequential anti-analysis checks:
1. Read `/proc/self/status` and look for a non-zero `TracerPid` (debugger attached)
2. Check for existence of the `su` binary (root detection)
3. Read a custom system property via `__system_property_get`

The checks gate a required register value computation. Bypass via static analysis: use IDA's graph view to trace the control flow and identify the "happy path" through all three checks, then compute what register values must hold at each branch.

**Key insight:** Anti-debug checks in native Android code (TracerPid, su, system properties) can be bypassed by static graph analysis to find correct register values without running a debugger.

**References:** h1702ctf 2017

---

## Android Log-Based Key Extraction (HackIT 2017)

A secure messenger app logs cryptographic material via Android's `Log.d()`:
- Curve25519 base agreement value
- Ephemeral shared key per message
- Message IDs and shift counters

The AES-CBC IV derives from the logged ephemeral/shared value; the key derives from the logged base agreement and an accumulated shift counter. Collect all log entries with `adb logcat`, then reconstruct AES-CBC parameters to decrypt intercepted messages.

```bash
adb logcat | grep -E "(agreement|ephemeral|shared|key)" > crypto_log.txt
# Parse log entries to reconstruct: key = f(base_agreement, shift_counter)
#                                   iv  = f(ephemeral_shared)
```

**Key insight:** Overly verbose logging in security-sensitive apps leaks enough state to reconstruct encryption parameters without any private key access.

**References:** HackIT CTF 2017

---

## Native JNI Key Extraction via Memory Dump and Smali Patching (HackIT 2017)

A JNI native library handles request signing using an XOR-obfuscated key stored in the `.data` section. The key is deobfuscated at runtime just before use.

**Workflow:**
1. Load the library in IDA with a GDB stub on a rooted device
2. Set a breakpoint after the XOR decryption routine
3. Dump the memory region containing the decrypted key
4. Use `baksmali` to disassemble the APK's DEX, identify the smali file that constructs the signed POST request
5. Patch the smali to change which parameter gets signed, then rebuild with `apktool` and reinstall

```bash
# Decompile APK
apktool d target.apk -o target_decompiled/
# Edit smali: change signed parameter from original to desired value
# Rebuild
apktool b target_decompiled/ -o target_patched.apk
# Sign and install
```

**Key insight:** For JNI signing: memory-dump the decrypted key region during execution, then patch smali to sign desired parameters — avoids fully reversing the native signing algorithm.

**References:** HackIT CTF 2017

---

## IBM AS/400 SAVF File EBCDIC Decoding (EKOPARTY 2017)

IBM AS/400 SAVF (Save File) binary files use EBCDIC encoding rather than ASCII. The flag is interleaved with dummy text using a take-2-skip-2 pattern.

```python
import codecs

with open('savefile.savf', 'rb') as f:
    data = f.read()

# Convert EBCDIC to ASCII
ascii_data = data.decode('cp500')  # cp500 is IBM EBCDIC International

# Filter: keep uppercase letters and underscores (flag charset)
flag_chars = [c for c in ascii_data if c.isupper() or c == '_']
# Or apply take-2-skip-2 pattern after decoding
flag = ''.join(ascii_data[i] for i in range(0, len(ascii_data), 4)
               if ascii_data[i].isupper() or ascii_data[i] == '_')
```

**Key insight:** EBCDIC encoding is IBM mainframe-native. Examine character distribution after decoding to identify interleaving patterns. Filtering for uppercase letters and underscores is an effective shortcut for CTF flag formats.

**References:** EKOPARTY CTF 2017

---

## Intel SGX Enclave Reverse Engineering (Pwn2Win 2017)

Intel SGX enclave `.so` files expose an ECALL dispatch table. The enclave logic (including key derivation) is fully reversible with IDA since SGX code is standard x86-64.

**Workflow:**
1. Locate the ECALL table in the `.so` — a function pointer array indexed by ECALL number
2. Decompile ECALLs with IDA to identify the remote attestation protocol
3. Implement the attestation protocol manually in Python using `sgx_crypto_wrapper`
4. Key derivation: ECDH over P-256 followed by CMAC-AES-128 to derive the session key (SK)
5. Decrypt the AES-128-GCM-encrypted flag blob using the derived SK

```python
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import cmac, ciphers

# ECDH: derive shared secret from server's P-256 public key
private_key = ec.generate_private_key(ec.SECP256R1())
shared_secret = private_key.exchange(ec.ECDH(), server_pub_key)

# CMAC-AES-128 key derivation (per SGX attestation spec)
c = cmac.CMAC(ciphers.algorithms.AES(b'\x00' * 16))
c.update(shared_secret[:16])
sk = c.finalize()

# Decrypt flag with AES-128-GCM using derived SK
```

**Key insight:** SGX remote attestation key derivation is deterministic given the enclave measurement — reimplementing the protocol in Python recovers the same session key.

**References:** Pwn2Win CTF 2017


# languages

# CTF Reverse - Language-Specific Techniques

## Table of Contents
- [Python Bytecode Reversing (dis.dis output)](#python-bytecode-reversing-disdis-output)
  - [Common Pattern: XOR Validation with Split Indices](#common-pattern-xor-validation-with-split-indices)
  - [Bytecode Analysis Tips](#bytecode-analysis-tips)
- [Python Opcode Remapping](#python-opcode-remapping)
  - [Identification](#identification)
  - [Recovery](#recovery)
- [Pyarmor 8/9 Static Unpack (1shot)](#pyarmor-89-static-unpack-1shot)
- [DOS Stub Analysis](#dos-stub-analysis)
- [Unity IL2CPP Games](#unity-il2cpp-games)
- [HarmonyOS HAP/ABC Reverse (abc-decompiler)](#harmonyos-hapabc-reverse-abc-decompiler)
- [Brainfuck/Esolangs](#brainfuckesolangs)
  - [Brainfuck Character-by-Character Static Analysis (BSidesSF 2026)](#brainfuck-character-by-character-static-analysis-bsidessf-2026)
  - [Brainfuck Side-Channel via Read Count Oracle (BSidesSF 2026)](#brainfuck-side-channel-via-read-count-oracle-bsidessf-2026)
  - [Brainfuck Comparison Idiom Detection (BSidesSF 2026)](#brainfuck-comparison-idiom-detection-bsidessf-2026)
- [UEFI Binary Analysis](#uefi-binary-analysis)
- [Transpilation to C](#transpilation-to-c)
- [Code Coverage Side-Channel Attack](#code-coverage-side-channel-attack)
- [Functional Language Reversing (OPAL)](#functional-language-reversing-opal)
- [Python Version-Specific Bytecode (VuwCTF 2025)](#python-version-specific-bytecode-vuwctf-2025)
- [Non-Bijective Substitution Cipher Reversing](#non-bijective-substitution-cipher-reversing)
- [FRACTRAN Program Inversion (Boston Key Party 2016)](#fractran-program-inversion-boston-key-party-2016)

For platform/framework-specific techniques (Android, Roblox, Godot, Electron, Node.js, Verilog, Ruby/Perl polyglot, etc.), see [languages-platforms.md](languages-platforms.md).
For Go and Rust binary reversing, see [languages-compiled.md](languages-compiled.md).

---

## Python Bytecode Reversing (dis.dis output)

### Common Pattern: XOR Validation with Split Indices

Challenge gives raw CPython bytecode (dis.dis disassembly). Common pattern:
1. Check flag length
2. XOR chars at even indices with key1, compare to list p1
3. XOR chars at odd indices with key2, compare to list p2

**Reversing:**
```python
# Given: p1, p2 (expected values), key1, key2 (XOR keys)
flag = [''] * flag_length
for i in range(len(p1)):
    flag[2*i] = chr(p1[i] ^ key1)      # Even indices
    flag[2*i+1] = chr(p2[i] ^ key2)    # Odd indices
print(''.join(flag))
```

### Bytecode Analysis Tips
- `LOAD_CONST` followed by `COMPARE_OP` reveals expected values
- `BINARY_XOR` identifies the transformation
- `BUILD_TUPLE`/`BUILD_LIST` with constants = expected output array
- Loop structure: `FOR_ITER` + `BINARY_SUBSCR` = iterating over flag chars
- `CALL_FUNCTION` on `ord` = character-to-int conversion

**Key insight:** Python bytecode challenges give you the algorithm in explicit stack operations. Focus on `LOAD_CONST` values (expected outputs), `BINARY_XOR`/`BINARY_ADD` (the transform), and `BUILD_TUPLE` (the target array) to reconstruct the validation logic without running the bytecode.

---

## Python Opcode Remapping

### Identification
Decompiler fails with opcode errors.

### Recovery
1. Find modified `opcode.pyc` in PyInstaller bundle
2. Compare with original Python opcodes
3. Build mapping: `{new_opcode: original_opcode}`
4. Patch target .pyc
5. Decompile normally

**Shortcut (Hack.lu CTF 2013):** If the challenge bundles its own modified Python interpreter (e.g., a custom `./py` binary), install `uncompyle2`/`uncompyle6` into that interpreter's environment and decompile using the challenge's own runtime. The modified interpreter understands its own opcode mapping, so standard decompilation tools work without manual opcode recovery.

**Tool selection by Python version:** `uncompyle6` supports Python 2.x–3.8. For Python 3.9+ bytecode, use [`pycdc`](https://github.com/zrax/pycdc) (compile from source: `git clone && cmake . && make`).

**Key insight:** Opcode remapping breaks all standard decompilers. The fastest fix is to find the modified `opcode.pyc` in the PyInstaller bundle, diff it against the stock Python opcodes, and patch the target `.pyc` back to standard opcodes before decompiling.

---

## Pyarmor 8/9 Static Unpack (1shot)

- Tool: `Lil-House/Pyarmor-Static-Unpack-1shot`
- Use for Pyarmor 8.x/9.x armored scripts without executing sample code
- Quick signature check: payload typically starts with `PY` + six digits (Pyarmor 7 and earlier `PYARMOR` format is not supported)

Workflow:
1. Ensure target directory contains armored scripts and matching `pyarmor_runtime` library.
2. Run one-shot unpack to emit `.1shot.` outputs (disassembly + experimental decompile).
3. Treat disassembly as ground truth; verify decompiled source with bytecode when inconsistent.

```bash
python /path/to/oneshot/shot.py /path/to/scripts
```

Optional flags:
```bash
# Specify runtime explicitly
python /path/to/oneshot/shot.py /path/to/scripts -r /path/to/pyarmor_runtime.so

# Write outputs to another directory
python /path/to/oneshot/shot.py /path/to/scripts -o /path/to/output
```

Notes:
- `oneshot/pyarmor-1shot` executable must exist before running `shot.py`.
- PyInstaller bundles or archives should be unpacked first, then processed with 1shot.

**Key insight:** Pyarmor 8/9 wraps scripts with runtime decryption. The 1shot tool statically unpacks without execution by directly processing the armored bytecode and `pyarmor_runtime` library. Treat the disassembly output as ground truth when the experimental decompiled source looks inconsistent.

---

## DOS Stub Analysis

PE files can hide code in DOS stub:
1. Check for large DOS stub in Ghidra/IDA
2. Run in DOSBox
3. Load in IDA as 16-bit DOS
4. Look for `int 16h` (keyboard input)

**Key insight:** PE files can embed a fully functional 16-bit DOS program in the DOS stub (before the PE header). If the stub is unusually large, load it in IDA as 16-bit DOS or run it in DOSBox -- the challenge logic may live entirely in the stub.

---

## Unity IL2CPP Games

- Use Il2CppDumper to dump symbols
- If Il2CppDumper fails, consider that `global-metadata.dat` may be encrypted; search strings/xrefs in the main binary and inspect the metadata loading path for custom decryption before dump.
- Look for `Start()` functions
- Key derivation: `key = SHA256(companyName + "\n" + productName)`
- Decrypt server responses with derived key

Please note most of that the executable file for the PC platform is GameAssembly.dll or *Assembly.dll, for the Android is libil2cpp.so.

**Key insight:** IL2CPP compiles C# to native code, but Il2CppDumper recovers method names and offsets. If the dumper fails, the `global-metadata.dat` is likely encrypted -- trace the metadata loading path in the native binary to find the custom decryption before dumping.

---

## HarmonyOS HAP/ABC Reverse (abc-decompiler)

- Target files: `.hap` package and embedded `.abc` bytecode
- Tool: `https://github.com/ohos-decompiler/abc-decompiler`
- Download `jadx-dev-all.jar` from releases

Critical startup note:
- `java -jar` may enter GUI mode
- For CLI mode, always use:

```bash
java -cp "./jadx-dev-all.jar" jadx.cli.JadxCLI [options] <input>
```

Most common commands:
```bash
# Basic decompile to directory
java -cp "./jadx-dev-all.jar" jadx.cli.JadxCLI -d "out" ".abc"

# Decompile .abc (recommended for this scenario)
java -cp "./jadx-dev-all.jar" jadx.cli.JadxCLI -m simple -d "out_hap" "modules.abc"
```

Recommended parameters for this challenge:
- `-m simple`: reduce high-level reconstruction to avoid SSA/PHI-heavy failures
- `--log-level ERROR`: keep only critical errors
- Full recommended command:

```bash
java -cp "./jadx-dev-all.jar" jadx.cli.JadxCLI -m simple --log-level ERROR -d "out_abc_simple" "modules.abc"
```

Parameter quick reference:
- `-d` output directory
- `--help` help

Notes:
- `.hap` is a package: extract it first (zip), then locate and analyze `.abc`
- Quote paths containing spaces or non-ASCII characters
- Use a new output directory name per run to avoid stale results
- Errors do not always mean full failure; prioritize `out_xxx/sources/`
- If `auto` fails, switch to `-m simple` first

Standard workflow:
1. Run with `-m simple --log-level ERROR`
2. Inspect key business files in output (for example `pages/Index.java`)
3. If cleaner output is needed, retry with `-m auto` or `-m restructure`
4. If some methods still fail, keep the `simple` output and continue logic analysis via alternate paths

**Key insight:** HarmonyOS `.hap` packages are ZIP archives containing `.abc` bytecode. Use the abc-decompiler's CLI mode (`jadx.cli.JadxCLI`) with `-m simple` for the most reliable decompilation -- GUI mode may launch instead of processing files.

---

## Brainfuck/Esolangs

- Check if compiled with known tools (BF-it)
- Understand tape/memory model
- Static analysis of cell operations

### Brainfuck Character-by-Character Static Analysis (BSidesSF 2026)

**Pattern (i-love-my-bf-part1):** BF programs that validate input character-by-character follow a recognizable pattern: `,` (read char) followed by a sequence of `+` operations whose count equals the expected ASCII value of that character.

**Extraction technique:**
```python
import re

bf_code = open('challenge.bf', 'r').read()

# Split on comma (input read) — each segment handles one character
segments = bf_code.split(',')
expected = []

for seg in segments[1:]:  # Skip preamble before first comma
    # Count consecutive '+' operations before any branch/output
    plus_count = 0
    for ch in seg:
        if ch == '+':
            plus_count += 1
        elif ch in '-.[]><':
            break  # Stop at first non-increment operation
    if plus_count > 0:
        expected.append(chr(plus_count % 256))

flag = ''.join(expected)
print(f"Flag: {flag}")
```

**Variations:**
- `-` operations: character value = `256 - minus_count`
- Mixed `+`/`-`: net increment determines value
- Cell reset (`[-]`) between characters: each segment is independent
- Loop-based multiplication: `[->>+++<<]` multiplies by 3 — count the inner operations

**Detection:** Large BF file with repeating pattern of `,` followed by many `+` or `-` characters, then a comparison structure (`[-]` or `[->+<]` patterns).

**Key insight:** BF programs that check input are structurally simple — each input byte is compared against a constant built by incrementing a cell. Extract the increment counts to recover the expected input without running the program.

**References:** BSidesSF 2026 "i-love-my-bf-part1"

### Brainfuck Side-Channel via Read Count Oracle (BSidesSF 2026)

**Pattern (i-love-my-bf-part2):** When a BF program validates input character-by-character, a correct character causes the program to consume MORE input bytes (advancing to check the next position). By counting how many `,` (read) operations execute for each candidate input, the character that triggers the most reads is correct.

```python
import itertools

def bytes_read_running_bf(bf_code, input_iter, braces):
    """Run BF and count how many input bytes were consumed."""
    tape = [0] * 30000
    ptr = ip = reads = 0
    input_list = list(input_iter)
    input_idx = 0
    while ip < len(bf_code):
        c = bf_code[ip]
        if c == ',':
            if input_idx < len(input_list):
                tape[ptr] = input_list[input_idx]
                input_idx += 1
                reads += 1
            else:
                return reads
        elif c == '.': pass
        elif c == '+': tape[ptr] = (tape[ptr] + 1) % 256
        elif c == '-': tape[ptr] = (tape[ptr] - 1) % 256
        elif c == '>': ptr += 1
        elif c == '<': ptr -= 1
        elif c == '[' and tape[ptr] == 0: ip = braces[ip]
        elif c == ']' and tape[ptr] != 0: ip = braces[ip]
        ip += 1
    return reads

# Recover flag character by character
PRINTABLE = list(range(32, 127))
flag = []
for pos in range(50):  # max flag length
    best_byte = None
    max_reads = 0
    baseline = bytes_read_running_bf(bf, flag + [PRINTABLE[0]], braces)
    for b in PRINTABLE[1:]:
        reads = bytes_read_running_bf(bf, flag + [b], braces)
        if reads > baseline:
            best_byte = b
            break
    if best_byte is None:
        break
    flag.append(best_byte)
print(bytes(flag).decode())
```

**Key insight:** BF input validation programs are sequential — they read one character, check it, and only read the next if it matches. The character causing more reads is correct because the program advances past the validation gate to check the next position.

**References:** BSidesSF 2026 "i-love-my-bf-part2"

### Brainfuck Comparison Idiom Detection (BSidesSF 2026)

**Pattern (i-love-my-bf-part3):** BF programs compiled from higher-level languages use recognizable comparison idioms. The equality check `<[-<->] +<[>-<[-]]>[-<+>]` compares two adjacent cells. By instrumenting a BF interpreter to detect this pattern during execution, you can extract the comparison operands (expected flag bytes) directly from the tape.

```python
EQ_PATTERN = "<[-<->] +<[>-<[-]]>[-<+>]"

def instrumented_bf_run(bf_code, dummy_input):
    """Run BF, detect equality comparisons, extract operands."""
    tape = [0] * 30000
    ptr = ip = 0
    comparisons = []

    while ip < len(bf_code):
        # Check if current position starts the eq pattern
        if bf_code[ip:ip+len(EQ_PATTERN)] == EQ_PATTERN:
            # The two cells being compared are at ptr-2 and ptr-1
            lhs = tape[ptr - 2]  # User input byte
            rhs = tape[ptr - 1]  # Expected byte
            comparisons.append((chr(lhs), chr(rhs)))
        # ... normal BF execution ...
        ip += 1

    return comparisons

# Expected bytes from comparisons reveal the flag
```

**Key insight:** Compiled BF programs reuse fixed idioms for operations like equality comparison, conditional branching, and loops. Pattern-matching these idioms in the BF source or during execution lets you extract constants without fully understanding the program logic.

**Common BF idioms:**
- `[-]` — clear cell (set to 0)
- `[->+<]` — move cell right
- `<[-<->] +<[>-<[-]]>[-<+>]` — equality comparison of two cells

**References:** BSidesSF 2026 "i-love-my-bf-part3"

---

## UEFI Binary Analysis

```bash
7z x firmware.bin -oextracted/
file extracted/* | grep "PE32+"
```

- Bootkit replaces boot loader
- Custom VM protects decryption
- Lift VM bytecode to C

**Key insight:** UEFI binaries are PE32+ executables. Extract the firmware with `7z`, identify PE files with `file`, and load them in Ghidra/IDA. Bootkits replace the boot loader, so focus on DXE drivers and boot services protocols for the challenge logic.

---

## Transpilation to C

For heavily obfuscated code:
```python
for opcode, args in instructions:
    if opcode == 'XOR':
        print(f"r{args[0]} ^= r{args[1]};")
    elif opcode == 'ADD':
        print(f"r{args[0]} += r{args[1]};")
```

Compile with `-O3` for constant folding.

**Key insight:** Transpiling obfuscated VM bytecode to C and compiling with `-O3` lets the compiler's constant folding and dead code elimination simplify the algorithm automatically. This is faster than manual deobfuscation for complex instruction sets.

---

## Code Coverage Side-Channel Attack

**Pattern (Coverup, Nullcon 2026):** PHP challenge provides XDebug code coverage data alongside encrypted output.

**How it works:**
- PHP code uses `xdebug_start_code_coverage(XDEBUG_CC_UNUSED | XDEBUG_CC_DEAD_CODE | XDEBUG_CC_BRANCH_CHECK)`
- Encryption uses data-dependent branches: `if ($xored == chr(0)) ... if ($xored == chr(1)) ...`
- Coverage JSON reveals which branches were executed during encryption
- This leaks the set of XOR intermediate values that occurred

**Exploitation:**
```python
import json

# Load coverage data
with open('coverage.json') as f:
    cov = json.load(f)

# Extract executed XOR values from branch coverage
executed_xored = set()
for line_no, hit_count in cov['encrypt.php']['lines'].items():
    if hit_count > 0:
        # Map line numbers to the chr(N) value in the if-statement
        executed_xored.add(extract_value_from_line(line_no))

# For each position, filter candidates
for pos in range(len(ciphertext)):
    candidates = []
    for key_byte in range(256):
        xored = plaintext_byte ^ key_byte  # or reverse S-box lookup
        if xored in executed_xored:
            candidates.append(key_byte)
    # Combined with known plaintext prefix, this uniquely determines key
```

**Key insight:** Code coverage is a powerful oracle — it tells you which conditional paths were taken. Any encryption with data-dependent branching leaks information through coverage.

**Mitigation detection:** Look for branchless/constant-time crypto implementations that defeat this attack.

---

## Functional Language Reversing (OPAL)

**Pattern (Opalist, Nullcon 2026):** Binary compiled from OPAL (Optimized Applicative Language), a purely functional language.

**Recognition markers:**
- `.impl` (implementation) and `.sign` (signature) source files
- `IMPLEMENTATION` / `SIGNATURE` keywords
- Nested `IF..THEN..ELSE..FI` structures
- Functions named `f1`, `f2`, ... `fN` (numeric naming)
- Heavy use of `seq[nat]`, `string`, `denotation` types

**Reversing approach:**
1. Pure functions are mathematically invertible — reverse each step in the pipeline
2. Identify the transformation chain: `f_final(f_n(...f_2(f_1(input))...))`
3. For each function, build the inverse

**Aggregate brute-force for scramble functions:**
When a transformation accumulates state that depends on original (unknown) values:
```python
# Example: f8 adds cumulative offset based on parity of original bytes
# offset contribution per element depends on whether pre-scramble value is even/odd
# Total offset S = sum of contributions, but S mod 256 has only 256 possibilities

decoded = base64_decode(target)
for total_offset_S in range(256):
    candidate = [(b - total_offset_S) % 256 for b in decoded]
    # Verify: recompute S from candidate values
    recomputed_S = sum(contribution(i, candidate[i]) for i in range(len(candidate))) % 256
    if recomputed_S == total_offset_S:
        # Apply remaining inverse steps
        result = apply_inverse_substitution(candidate)
        if all(32 <= c < 127 for c in result):
            print(bytes(result))
```

**Key lesson:** When a scramble function has a chicken-and-egg dependency (result depends on original, which is unknown), brute-force the aggregate effect (often mod 256 = 256 possibilities) rather than all possible states (exponential).

---

## Python Version-Specific Bytecode (VuwCTF 2025)

**Pattern (A New Machine):** Challenge targets specific Python version (e.g., 3.14.0 alpha).

**Key requirement:** Compile that exact Python version to disassemble bytecode — alpha/beta versions have different opcodes than stable releases.

```bash
# Build specific Python version
wget https://www.python.org/ftp/python/3.14.0/Python-3.14.0a4.tar.xz
tar xf Python-3.14.0a4.tar.xz
cd Python-3.14.0a4 && ./configure && make -j$(nproc)
./python -c "import dis, marshal; dis.dis(marshal.loads(open('challenge.pyc','rb').read()[16:]))"
```

**Common validation:** Flag compared against tuple of squared ASCII values:
```python
# Reverse: flag[i] = sqrt(expected_tuple[i])
import math
flag = ''.join(chr(int(math.isqrt(v))) for v in expected_values)
```

---

## Non-Bijective Substitution Cipher Reversing

**Pattern (Coverup, Nullcon 2026):** S-box/substitution table has collisions (multiple inputs map to same output).

**Detection:**
```python
sbox = [...]  # substitution table
if len(set(sbox)) < len(sbox):
    print("Non-bijective! Collisions exist.")
```

**Building reverse lookup:**
```python
from collections import defaultdict
rev_sub = defaultdict(list)
for i, v in enumerate(sbox):
    rev_sub[v].append(i)
# rev_sub[output] = [list of possible inputs]
```

**Disambiguation strategies:**
1. Known plaintext format (e.g., `ENO{`, `flag{`) fixes key bytes at known positions
2. Side-channel data (code coverage, timing) eliminates impossible candidates
3. Printable ASCII constraint (32-126) reduces candidate space
4. Re-encrypt candidates and verify against known ciphertext

---

## FRACTRAN Program Inversion (Boston Key Party 2016)

FRACTRAN: an esoteric language where computation is iterated multiplication by a fraction table. Input is encoded as prime factorization (ASCII values as exponents of sequential primes). To invert: swap each fraction's numerator and denominator, run the "success" output backward through the inverted program.

```python
# Original: for each step, find first fraction where n*frac is integer
def fractran_step(n, fractions):
    for num, den in fractions:
        if (n * num) % den == 0:
            return (n * num) // den
    return None  # Halt

# Inversion: swap num/denom in fraction table
inverted = [(d, n) for n, d in fraction_table]
# Run target output through inverted program to recover input
```

**Key insight:** FRACTRAN programs can be inverted by swapping numerators and denominators. The prime factorization encoding is the key to understanding I/O -- factor the result to extract exponents of sequential primes, map to ASCII.

**Detection:** Challenge mentions fractions, prime factorization, or provides a list of rational numbers.


# patterns-ctf-2

# CTF Reverse - Competition-Specific Patterns (Part 2)

## Table of Contents
- [Multi-Layer Self-Decrypting Binary (DiceCTF 2026)](#multi-layer-self-decrypting-binary-dicectf-2026)
- [Embedded ZIP + XOR License Decryption (MetaCTF 2026)](#embedded-zip--xor-license-decryption-metactf-2026)
- [Stack String Deobfuscation from .rodata XOR Blob (Nullcon 2026)](#stack-string-deobfuscation-from-rodata-xor-blob-nullcon-2026)
- [Prefix Hash Brute-Force (Nullcon 2026)](#prefix-hash-brute-force-nullcon-2026)
- [CVP/LLL Lattice for Constrained Integer Validation (HTB ShadowLabyrinth)](#cvplll-lattice-for-constrained-integer-validation-htb-shadowlabyrinth)
- [Decision Tree Function Obfuscation (HTB WonderSMS)](#decision-tree-function-obfuscation-htb-wondersms)
- [GF(2^8) Gaussian Elimination for Flag Recovery (ApoorvCTF 2026)](#gf28-gaussian-elimination-for-flag-recovery-apoorvctf-2026)
- [ROP Chain Obfuscation in Modified Binary (PlaidCTF 2016)](#rop-chain-obfuscation-in-modified-binary-plaidctf-2016)

---

## Multi-Layer Self-Decrypting Binary (DiceCTF 2026)

**Pattern (another-onion):** Binary with N layers (e.g., 256), each reading 2 key bytes, deriving keystream via SHA-256 NI instructions, XOR-decrypting the next layer, then jumping to it. Must solve within a time limit (e.g., 30 minutes).

**Oracle for correct key:** Wrong key bytes produce garbage code. Correct key bytes produce code with exactly 2 `call read@plt` instructions (next layer's reads). Brute-force all 65536 candidates per layer using this oracle.

**JIT execution approach (fastest):**
```c
// Map binary's memory at original virtual addresses into solver process
// Compile solver at non-overlapping address: -Wl,-Ttext-segment=0x10000000
void *text = mmap((void*)0x400000, text_size, PROT_RWX, MAP_FIXED|MAP_PRIVATE, fd, 0);
void *bss = mmap((void*)bss_addr, bss_size, PROT_RW, MAP_FIXED|MAP_SHARED, shm_fd, 0);

// Patch read@plt to inject candidate bytes instead of reading stdin
// Patch tail jmp/call to next layer with ret/NOP to return from layer

// Fork-per-candidate: COW gives isolated memory without memcpy
for (int candidate = 0; candidate < 65536; candidate++) {
    pid_t pid = fork();
    if (pid == 0) {
        // Child: remap BSS as MAP_PRIVATE (COW from shared file)
        mmap(bss_addr, bss_size, PROT_RW, MAP_FIXED|MAP_PRIVATE, shm_fd, 0);
        inject_key(candidate >> 8, candidate & 0xff);
        ((void(*)())layer_addr)();  // Execute layer as function call
        // Check: does decrypted code contain exactly 2 call read@plt?
        if (count_read_calls(next_layer_addr) == 2) signal_found(candidate);
        _exit(0);
    }
}
```

**Performance tiers:**
| Approach | Speed | 256-layer estimate |
|----------|-------|--------------------|
| Python subprocess | ~2/s | days |
| Ptrace fork injection | ~119/s | 6+ hours |
| JIT + fork-per-candidate | ~1000/s | 140 min |
| JIT + shared BSS + 32 workers | ~3500/s | **~17 min** |

**Shared BSS optimization:** BSS (16MB+) stored in `/dev/shm` as `MAP_SHARED` in parent. Children remap as `MAP_PRIVATE` for COW. Reduces fork overhead from 16MB page-table setup to ~4KB.

**Key insight:** Multi-layer decryption challenges are fundamentally about building fast brute-force engines. JIT execution (mapping binary memory into solver, running code directly as function calls) is orders of magnitude faster than ptrace. Fork-based COW provides free memory isolation per candidate.

**Gotchas:**
- Real binary may use `call` (0xe8) instead of `jmp` (0xe9) for layer transitions — adjust tail patching
- BSS may extend beyond ELF MemSiz via kernel brk mapping — map extra space
- SHA-NI instructions work even when not advertised in `/proc/cpuinfo`

---

## Embedded ZIP + XOR License Decryption (MetaCTF 2026)

**Pattern (License To Rev):** Binary requires a license file as argument. Contains an embedded ZIP archive with the expected license, and an XOR-encrypted flag.

**Recognition:**
- `strings` reveals `EMBEDDED_ZIP` and `ENCRYPTED_MESSAGE` symbols
- Binary is not stripped — `nm` or `readelf -s` shows data symbols in `.rodata`
- `file` shows PIE executable, source file named `licensed.c`

**Analysis workflow:**
1. **Find data symbols:**
```bash
readelf -s binary | grep -E "EMBEDDED|ENCRYPTED|LICENSE"
# EMBEDDED_ZIP at offset 0x2220, 384 bytes
# ENCRYPTED_MESSAGE at offset 0x21e0, 35 bytes
```

2. **Extract embedded ZIP:**
```python
import struct
with open('binary', 'rb') as f:
    data = f.read()
# Find PK\x03\x04 magic in .rodata
zip_start = data.find(b'PK\x03\x04')
# Extract ZIP (size from symbol table or until next symbol)
open('embedded.zip', 'wb').write(data[zip_start:zip_start+384])
```

3. **Extract license from ZIP:**
```bash
unzip embedded.zip  # Contains license.txt
```

4. **XOR decrypt the flag:**
```python
license = open('license.txt', 'rb').read()
enc_msg = open('encrypted_msg.bin', 'rb').read()  # Extract from .rodata
flag = bytes(a ^ b for a, b in zip(enc_msg, license))
print(flag.decode())
```

**Key insight:** No need to run the binary or bypass the expiry date check. The embedded ZIP and encrypted message are both in `.rodata` — extract and XOR offline.

**Disassembly confirms:**
- `memcmp(user_license, decompressed_embedded_zip, size)` — license validation
- Date parsing with `sscanf("%d-%d-%d")` on `EXPIRY_DATE=` field
- XOR loop: `ENCRYPTED_MESSAGE[i] ^ license[i]` → `putc()` per byte

**Lesson:** When a binary has named symbols (`EMBEDDED_*`, `ENCRYPTED_*`), extract data directly from the binary without execution. XOR with known plaintext (the license) is trivially reversible.

---

## Stack String Deobfuscation from .rodata XOR Blob (Nullcon 2026)

**Pattern (stack_strings_1/2):** Binary mmaps a blob from `.rodata`, XOR-deobfuscates it, then uses the blob to validate input. Flag is recovered by reimplementing the verification loop.

**Recognition:**
- `mmap()` call followed by XOR loop over `.rodata` data
- Verification loop with running state (`eax`, `ebx`, `r9`) updated with constants like `0x9E3779B9`, `0x85EBCA6B`, `0xA97288ED`
- `rol32()` operations with position-dependent shifts
- Expected bytes stored in deobfuscated buffer

**Approach:**
1. Extract `.rodata` blob with pyelftools:
   ```python
   from elftools.elf.elffile import ELFFile
   with open(binary, "rb") as f:
       elf = ELFFile(f)
       ro = elf.get_section_by_name(".rodata")
       blob = ro.data()[offset:offset+size]
   ```
2. Recover embedded constants (length, magic values) by XOR with known keys from disassembly
3. Reimplement the byte-by-byte verification loop:
   - Each iteration: compute two hash-like values from running state
   - XOR them together and with expected byte to recover input byte
   - Update running state with constant additions

**Variant (stack_strings_2):** Adds position permutation + state dependency on previous character:
- Position permutation: byte `i` may go to position `pos[i]` in the output
- State dependency: `need = (expected - rol8(prev_char, 1)) & 0xFF`
- Must track `state` variable that updates to current character each iteration

**Key constants to look for:**
- `0x9E3779B9` (golden ratio fractional, common in hash functions)
- `0x85EBCA6B` (MurmurHash3 finalizer constant)
- `0xA97288ED` (related hash constant)
- `rol32()` with shift `i & 7`

---

## Prefix Hash Brute-Force (Nullcon 2026)

**Pattern (Hashinator):** Binary hashes every prefix of the input independently and outputs one digest per prefix. Given N output digests, the flag has N-1 characters.

**Attack:** Recover input one character at a time:
```python
for pos in range(1, len(target_hashes)):
    for ch in charset:
        candidate = known_prefix + ch + padding
        hashes = run_binary(candidate)
        if hashes[pos] == target_hashes[pos]:
            known_prefix += ch
            break
```

**Key insight:** If each prefix hash is independent (no chaining/HMAC), the problem decomposes into `N` x `|charset|` binary executions. This is the hash equivalent of byte-at-a-time block cipher attacks.

**Detection:** Binary outputs multiple hash lines. Changing last character only changes last hash. Different input lengths produce different numbers of output lines.

---

## CVP/LLL Lattice for Constrained Integer Validation (HTB ShadowLabyrinth)

**Pattern:** Binary validates flag via matrix multiplication where grouped input characters are multiplied by coefficient matrices and checked against expected 64-bit results. Standard algebra fails because solutions must be printable ASCII (32-126). Lattice-based CVP (Closest Vector Problem) with LLL reduction solves this efficiently.

**Identification:**
1. Binary groups input characters (e.g., 4 at a time)
2. Each group is multiplied by a coefficient matrix
3. Results compared against hardcoded 64-bit values
4. Need integer solutions in a constrained range (printable ASCII)

**SageMath CVP solver:**
```python
from sage.all import *

def solve_constrained_matrix(coefficients, targets, char_range=(32, 126)):
    """
    coefficients: list of coefficient rows (e.g., 4 values per group)
    targets: expected output values
    char_range: valid character range (printable ASCII)
    """
    n = len(coefficients[0])  # characters per group
    mid = (char_range[0] + char_range[1]) // 2

    # Build lattice: [coeff_matrix | I*scale]
    # The target vector includes adjusted targets
    M = matrix(ZZ, n + len(targets), n + len(targets))
    scale = 1000  # Weight to constrain character range

    for i, row in enumerate(coefficients):
        for j, c in enumerate(row):
            M[j, i] = c
        M[n + i, i] = 1  # padding

    for j in range(n):
        M[j, len(targets) + j] = scale

    target_vec = vector(ZZ, [t - sum(c * mid for c in row)
                              for row, t in zip(coefficients, targets)]
                        + [0] * n)

    # LLL + CVP
    L = M.LLL()
    closest = L * L.solve_left(target_vec)  # or use Babai
    solution = [closest[len(targets) + j] // scale + mid for j in range(n)]
    return bytes(solution)
```

**Two-phase validation pattern:**
1. **Phase 1 (matrix math):** Solve via CVP/LLL → recovers first N characters
2. First N characters become AES key → decrypt `file.bin` (XOR last 16 bytes + AES-256-CBC + zlib decompress)
3. **Phase 2 (custom VM):** Decrypted bytecode runs in custom VM, validates remaining characters via another linear system (mod 2^32)

**Modular linear system solving (Phase 2 — VM validation):**
```python
import numpy as np
from sympy import Matrix

# M * x = v (mod 2^32)
M_mod = Matrix(coefficients) % (2**32)
v_mod = Matrix(targets) % (2**32)
# Gaussian elimination in Z/(2^32)
solution = M_mod.solve(v_mod)  # Returns flag characters
```

**Key insight:** When a binary validates input through linear combinations with large coefficients and the solution must be in a small range (printable ASCII), this is a lattice problem in disguise. LLL reduction + CVP finds the nearest lattice point, recovering the constrained solution. Cross-reference: invoke `/ctf-crypto` for LLL/CVP fundamentals (advanced-math.md in ctf-crypto).

**Detection:** Binary performs matrix-like operations on grouped input, compares against 64-bit constants, and a brute-force search space is too large (e.g., 256^4 per group × 12 groups).

---

## Decision Tree Function Obfuscation (HTB WonderSMS)

**Pattern:** Binary routes input through ~200+ auto-generated functions, each computing a polynomial expression from input positions, comparing against a constant, and branching left/right. The tree makes static analysis impractical without scripted extraction.

**Identification:**
1. Large number of similar functions with random-looking names (e.g., `f315732804`)
2. Each function computes arithmetic on specific input positions
3. Functions call other tree functions or a final validation function
4. Decompiled code shows `if (expr cmp constant) call_left() else call_right()`

**Ghidra headless scripting for mass extraction:**
```python
# Extract comparison constants from all tree functions
# Run via: analyzeHeadless project/ tmp -import binary -postScript extract_tree.py
from ghidra.program.model.listing import *
from ghidra.program.model.symbol import *

fm = currentProgram.getFunctionManager()
results = []
for func in fm.getFunctions(True):
    name = func.getName()
    if name.startswith('f') and name[1:].isdigit():
        # Find CMP instruction and extract immediate constant
        inst_iter = currentProgram.getListing().getInstructions(func.getBody(), True)
        for inst in inst_iter:
            if inst.getMnemonicString() == 'CMP':
                operand = inst.getOpObjects(1)
                if operand:
                    results.append((name, int(operand[0].getValue())))
```

**Constraint propagation from known output format:**
1. Start from known output bytes (e.g., `http://HTB{...}`) → fix several input positions
2. Fixed positions cascade through arithmetic constraints → determine dependent positions
3. Tree root equation pins down remaining free variables
4. Recognize English words in partial flag to disambiguate multiple solutions

**Key insight:** Auto-generated decision trees look overwhelming but are repetitive by construction. Script the extraction (Ghidra, Binary Ninja, radare2) rather than reversing each function manually. The tree is just a dispatcher — the real logic is in the leaf function and its constraints.

**Detection:** Binary with hundreds of similarly-structured functions, 3-5 input position references per function, branching to two other functions or a common leaf.

---

## GF(2^8) Gaussian Elimination for Flag Recovery (ApoorvCTF 2026)

**Pattern (Forge):** Stripped binary performs Gaussian elimination over GF(2^8) (Galois Field with 256 elements, using the AES polynomial). A matrix and augmentation vector are embedded in `.rodata`. The solution vector is the flag.

**GF(2^8) arithmetic with AES polynomial (x^8+x^4+x^3+x+1 = 0x11b):**
```python
def gf_mul(a, b):
    """Multiply in GF(2^8) with AES reduction polynomial."""
    p = 0
    for _ in range(8):
        if b & 1:
            p ^= a
        hi = a & 0x80
        a = (a << 1) & 0xff
        if hi:
            a ^= 0x1b  # Reduction: x^8 = x^4+x^3+x+1
        b >>= 1
    return p

def gf_inv(a):
    """Brute-force multiplicative inverse (fine for 256 elements)."""
    if a == 0: return 0
    for x in range(1, 256):
        if gf_mul(a, x) == 1:
            return x
    return 0
```

**Solving the linear system:**
```python
# Extract N×N matrix + N-byte augmentation from binary .rodata
N = 56  # Flag length
# Build augmented matrix: N rows × (N+1) cols

for col in range(N):
    # Find non-zero pivot
    pivot = next((r for r in range(col, N) if aug[r][col] != 0), -1)
    if pivot != col:
        aug[col], aug[pivot] = aug[pivot], aug[col]
    # Scale pivot row by inverse
    inv = gf_inv(aug[col][col])
    aug[col] = [gf_mul(v, inv) for v in aug[col]]
    # Eliminate column in all other rows
    for row in range(N):
        if row == col: continue
        factor = aug[row][col]
        if factor == 0: continue
        aug[row] = [v ^ gf_mul(factor, aug[col][j]) for j, v in enumerate(aug[row])]

flag = bytes(aug[i][N] for i in range(N))
```

**Key insight:** GF(2^8) is NOT regular integer arithmetic — addition is XOR, multiplication uses polynomial reduction. The AES polynomial (0x11b) is the most common; look for the constant `0x1b` in disassembly. The binary may encrypt the result with AES-GCM afterward, but the raw solution vector (pre-encryption) is the flag.

**Detection:** Binary with a large matrix in `.rodata` (N² bytes), XOR-based row operations, constants `0x1b` or `0x11b`, and flag length matching sqrt of matrix size.

---

## ROP Chain Obfuscation in Modified Binary (PlaidCTF 2016)

**Pattern (quite quixotic quest):** Modified `curl` binary with a custom `--pctfkey KEY` option. Key validation replaces `esp` with a buffer address and returns into a ~250KB ROP chain stored in a `magic_buf` symbol. The ROP chain validates the key through XOR, MD5, and constant comparisons.

**Analysis approach:**

1. **Detect the ROP dispatch:** Look for `mov esp, eax; ret` or similar stack pivot — this redirects execution into the ROP chain
2. **Dump the ROP chain:** Script GDB to disassemble instructions after each return address in the chain:
```python
# GDB script to trace ROP gadgets
import gdb

magic_buf = 0x080b0000  # symbol address
buf_size = 0x40000       # quarter megabyte
offset = 0

while offset < buf_size:
    addr = int.from_bytes(gdb.selected_inferior().read_memory(magic_buf + offset, 4), 'little')
    gdb.execute(f'x/3i {addr}')
    # Advance past the gadget (typically 4 bytes per return address)
    offset += 4
```

3. **Identify patterns in the chain:** Look for unrolled loops (repeated gadget sequences), `pop` instructions that skip data, and `ret imm16` that skip large blocks
4. **Reconstruct the algorithm:** The chain typically performs:
   - Key length check (compare with constant)
   - Character-level operations (sum ASCII values, XOR with constants)
   - Hash computation (MD5 of derived value)
   - Hash prefix comparison
   - XOR of input with hash as keystream
   - Comparison with embedded constants

5. **Extract and solve:** Dump the embedded constants, brute-force any intermediate values (e.g., character sum → MD5 with matching prefix), then XOR to recover the key:
```python
import hashlib

# Brute-force the sum that produces correct MD5 prefix
target_prefix = 0xc0050bdd  # extracted from ROP chain
for s in range(128 * 0x35):  # max sum of printable chars * key_length
    h = hashlib.md5(str(s ^ xor_constant).encode()).hexdigest()
    if int(h[:8], 16) == target_prefix:
        md5_key = bytes.fromhex(h)
        break

# XOR embedded values with MD5 keystream to get flag
flag = bytes(v ^ md5_key[i % 16] for i, v in enumerate(embedded_values))
```

**Key insight:** ROP chain obfuscation ("ROPfuscation") hides algorithms in chains of return-oriented gadgets. The chain looks incomprehensible as raw addresses but becomes analyzable when you: (a) dump each gadget's disassembly, (b) filter repetitions and skip regions, (c) annotate register effects. The chain is functionally equivalent to normal code — it just uses `ret` instead of sequential execution. Large chains (100K+ gadgets) often contain unrolled loops that compress to ~1000 lines of pseudocode.

See also: [patterns-ctf.md](patterns-ctf.md) for Part 1 (hidden emulator opcodes, SPN static extraction, image XOR smoothness, byte-at-a-time cipher, mathematical convergence bitmap, Windows PE XOR bitmap OCR, two-stage RC4+VM loaders, GBA ROM meet-in-the-middle, Sprague-Grundy game theory, kernel module maze solving, multi-threaded VM channels). [patterns-ctf-3.md](patterns-ctf-3.md) for Part 3 (Z3 single-line Python circuit, sliding window popcount, keyboard LED Morse code, C++ destructor-hidden validation, syscall side-effect memory corruption, MFC dialog event handlers, VM sequential key-chain brute-force, Burrows-Wheeler transform inversion, OpenType font ligature exploitation, GLSL shader VM with self-modifying code, instruction counter as cryptographic state).


# patterns-ctf-3

# CTF Reverse - Competition-Specific Patterns (Part 3)

## Table of Contents
- [Z3 for Single-Line Python Boolean Circuit (BearCatCTF 2026)](#z3-for-single-line-python-boolean-circuit-bearcatctf-2026)
- [Sliding Window Popcount Differential Propagation (BearCatCTF 2026)](#sliding-window-popcount-differential-propagation-bearcatctf-2026)
- [Morse Code from Keyboard LEDs via ioctl (PlaidCTF 2013)](#morse-code-from-keyboard-leds-via-ioctl-plaidctf-2013)
- [C++ Destructor-Hidden Validation (Defcamp 2015)](#c-destructor-hidden-validation-defcamp-2015)
- [Syscall Side-Effect Memory Corruption (Hack.lu 2015)](#syscall-side-effect-memory-corruption-hacklu-2015)
- [MFC Dialog Event Handler Location (WhiteHat 2015)](#mfc-dialog-event-handler-location-whitehat-2015)
- [VM Sequential Key-Chain Brute-Force (Midnight Flag 2026)](#vm-sequential-key-chain-brute-force-midnight-flag-2026)
- [Burrows-Wheeler Transform Inversion without Terminator (ASIS CTF Finals 2016)](#burrows-wheeler-transform-inversion-without-terminator-asis-ctf-finals-2016)
- [OpenType Font Ligature Exploitation for Hidden Messages (Hack The Vote 2016)](#opentype-font-ligature-exploitation-for-hidden-messages-hack-the-vote-2016)
- [GLSL Shader VM with Self-Modifying Code (ApoorvCTF 2026)](#glsl-shader-vm-with-self-modifying-code-apoorvctf-2026)
- [Instruction Counter as Cryptographic State (MetaCTF Flash 2026)](#instruction-counter-as-cryptographic-state-metactf-flash-2026)
- [Thread Race Condition with Signed Integer Overflow (Codegate 2017)](#thread-race-condition-with-signed-integer-overflow-codegate-2017)
- [ESP32/Xtensa Firmware Reversing with ROM Symbol Map (Insomni'hack 2017)](#esp32xtensa-firmware-reversing-with-rom-symbol-map-insomnihack-2017)
- [Batch Crackme Automation via objdump Pattern Extraction (DEF CON 2017)](#batch-crackme-automation-via-objdump-pattern-extraction-def-con-2017)
- [Fork + Pipe + Dead Branch Anti-Analysis (RCTF 2017)](#fork--pipe--dead-branch-anti-analysis-rctf-2017)
- [Time-Locked Binary with Date-Based Key (Hack.lu 2017)](#time-locked-binary-with-date-based-key-hacklu-2017)
- [ARM Code in Image Pixels via UnicornJS (Hack.lu 2017)](#arm-code-in-image-pixels-via-unicornjs-hacklu-2017)
- [x86 16-bit MBR psadbw Constraint Solving (CSAW 2017)](#x86-16-bit-mbr-psadbw-constraint-solving-csaw-2017)

---

## Z3 for Single-Line Python Boolean Circuit (BearCatCTF 2026)

**Pattern (Captain Morgan):** Single-line Python (2000+ semicolons) validates flag via walrus operator chains decomposing input as a big-endian integer, with bitwise operations producing a boolean circuit.

**Identification:**
- Single-line Python with semicolons separating statements
- Walrus operator `:=` chains: `(x := expr)`
- Obfuscated XOR: `(x | i) & ~(x & i)` instead of `x ^ i`
- Input treated as a single large integer, decomposed via bit-shifting

**Z3 solution:**
```python
from z3 import *

n_bytes = 29  # Flag length
ari = BitVec('ari', n_bytes * 8)

# Parse semicolon-separated statements
# Model walrus chains as LShR(ari, shift_amount)
# Evaluate boolean expressions symbolically
# Final assertion: result_var == 0

s = Solver()
s.add(bfu == 0)  # Final validation variable
if s.check() == sat:
    m = s.model()
    val = m[ari].as_long()
    flag = val.to_bytes(n_bytes, 'big').decode('ascii')
```

**Key insight:** Single-line Python obfuscation creates a boolean circuit over input bits. The walrus operator chains are just variable assignments — split on semicolons and translate each to Z3 symbolically. Obfuscated XOR `(a | b) & ~(a & b)` is just `a ^ b`. Z3 solves these circuits in under a second. Look for `__builtins__` access or `ord()`/`chr()` calls to identify the input→integer conversion.

**Detection:** Single-line Python with 1000+ semicolons, walrus operators, bitwise operations, and a final comparison to 0 or True.

---

## Sliding Window Popcount Differential Propagation (BearCatCTF 2026)

**Pattern (Treasure Hunt 4):** Binary validates input via expected popcount (number of set bits) for each position of a 16-bit sliding window over the input bits.

**Differential propagation:**
When the window slides by 1 bit:
```text
popcount(window[i+1]) - popcount(window[i]) = bit[i+16] - bit[i]
```
So: `bit[i+16] = bit[i] + (data[i+1] - data[i])`

```python
expected = [...]  # 337 expected popcount values
total_bits = 337 + 15  # = 352

# Brute-force the initial 16-bit window (must have popcount = expected[0])
for start_val in range(0x10000):
    if bin(start_val).count('1') != expected[0]:
        continue

    bits = [0] * total_bits
    for j in range(16):
        bits[j] = (start_val >> (15 - j)) & 1

    valid = True
    for i in range(len(expected) - 1):
        new_bit = bits[i] + (expected[i + 1] - expected[i])
        if new_bit not in (0, 1):
            valid = False
            break
        bits[i + 16] = new_bit

    if valid:
        # Convert bits to bytes
        flag_bytes = bytes(int(''.join(map(str, bits[i:i+8])), 2)
                          for i in range(0, total_bits, 8))
        if b'BCCTF' in flag_bytes or flag_bytes[:5].isascii():
            print(flag_bytes.decode(errors='replace'))
            break
```

**Key insight:** Sliding window popcount differences create a recurrence relation: each new bit is determined by the bit 16 positions back plus the popcount delta. Only the first 16 bits are free (constrained by initial popcount). Brute-force the ~4000-8000 valid initial windows — for each, the entire bit sequence is deterministic. Runs in under a second.

**Detection:** Binary computing popcount/hamming weight on fixed-size windows. Expected value array with length ≈ input_bits - window_size + 1. Values in array are small integers (0 to window_size).

---

---

## Morse Code from Keyboard LEDs via ioctl (PlaidCTF 2013)

**Pattern:** Binary uses `ioctl(fd, KDSETLED, value)` to blink keyboard LEDs (Num/Caps/Scroll Lock). Timing patterns encode Morse code.

```bash
# Step 1: Bypass ptrace anti-debug
# Patch ptrace call at offset with NOP (0x90)
python3 -c "
data = open('binary','rb').read()
data = data[:0x72b] + b'\x90'*5 + data[:0x730]  # NOP the ptrace call
open('patched','wb').write(data)
"

# Step 2: Run under strace, capture ioctl calls
strace -e ioctl ./patched 2>&1 | grep KDSETLED > leds.txt

# Step 3: Decode timing patterns
# Short blink (250ms) = dit (.), long blink (750ms) = dah (-)
# Inter-character pause = 3x, inter-word pause = 7x
```

```python
# Parse strace output to extract Morse
import re
morse_map = {'.-':'A', '-...':'B', '-.-.':'C', '-..':'D', '.':'E',
             '..-.':'F', '--.':'G', '....':'H', '..':'I', '.---':'J',
             '-.-':'K', '.-..':'L', '--':'M', '-.':'N', '---':'O',
             '.--.':'P', '--.-':'Q', '.-.':'R', '...':'S', '-':'T',
             '..-':'U', '...-':'V', '.--':'W', '-..-':'X', '-.--':'Y',
             '--..':'Z', '-----':'0', '.----':'1'}
# Map LED on-durations to dots/dashes, group by pauses
```

**Key insight:** `KDSETLED` controls physical keyboard LEDs on Linux (`/dev/console`). The binary must run with console access. Use `strace -e ioctl` to capture all LED state changes without needing physical observation. Timing between calls determines dot vs dash.

---

## C++ Destructor-Hidden Validation (Defcamp 2015)

Validation logic may hide in C++ destructors that execute after `main()` returns. The `__cxa_atexit` mechanism registers destructor callbacks:

1. **Locate destructors:** Search for `__cxa_atexit` calls in `.init_array`/constructor sections
2. **Static analysis:** Identify global objects whose destructors perform flag checking
3. **Dynamic verification:** Set breakpoints on `__cxa_finalize` to trace post-main execution

```asm
# In IDA/Ghidra: look for atexit registrations
__cxa_atexit(destructor_func, object_ptr, dso_handle);

# Destructor contains actual validation:
# - Regex pattern matching on 4-byte blocks (8 sequential checks)
# - Arithmetic: v2 += -3 * s[i] + 36 + (s[i] ^ 0x2FCFBA)
# - Modular verification of accumulated sum
```

**Key insight:** When `main()` appears trivial or incomplete, check destructors of global/static C++ objects. The `.fini_array` section and `__cxa_atexit` registrations reveal hidden post-main logic.

---

## Syscall Side-Effect Memory Corruption (Hack.lu 2015)

The `rt_sigprocmask` syscall writes a `sigset_t` structure to its output pointer. When input parsing passes a pointer near a security-critical variable:

1. Certain input characters (e.g., `:` to `@` range, values 0x3A-0x40) trigger `rt_sigprocmask` as a side effect
2. The syscall zeros out bytes at the output address, which may overlap adjacent variables
3. In little-endian layout, zeroing the MSB of an adjacent integer variable effectively sets it to a small value

```c
// Memory layout (no ASLR):
// 0x603390: input_buffer[4]
// 0x603394: security_check_var

// Input ':' triggers: rt_sigprocmask(SIG_BLOCK, NULL, (sigset_t*)0x603397, ...)
// This zeros bytes at 0x603397+, corrupting security_check_var's high bytes
```

**Key insight:** Audit how input validation functions interact with syscalls. Character-to-syscall mappings in hex conversion routines can produce unintended memory writes via kernel-space operations.

---

## MFC Dialog Event Handler Location (WhiteHat 2015)

To find event handlers in MFC (Microsoft Foundation Class) applications:

1. **Break on SendMessageW:** Set breakpoint on `user32!SendMessageW` to intercept dialog messages
2. **Filter for WM_COMMAND:** Message ID 0x111 indicates button clicks and control events
3. **Trace message map:** Follow the MFC message dispatch from `CWnd::OnWndMsg` → `CCmdTarget::OnCmdMsg` → handler function
4. **OnInitDialog:** Often contains decryption or validation setup; triggered by WM_INITDIALOG (0x110)

```asm
# WinDbg/x64dbg:
bp user32!SendMessageW ".if (poi(@esp+8)==0x111) {} .else {gc}"
# Or in IDA: find cross-references to AFX_MSGMAP_ENTRY structures
```

**Key insight:** MFC applications route messages through dispatch tables. Identify the `AFX_MSGMAP` structure to enumerate all handled messages without runtime analysis.

---

## VM Sequential Key-Chain Brute-Force (Midnight Flag 2026)

**Pattern (67):** Custom VM validates input in N-byte blocks. Each block's output key feeds as input to the next block, preventing parallel solving. Per-block search space is small enough to brute-force (2^24 for 3-byte blocks).

**Recognition signs:**
- Bytecode with XOR-obfuscated opcodes (all bytes XOR'd with a constant, producing ASCII-looking bytecode)
- Iterative transformation loop (xorshift + multiply, repeated 1000+ times) making algebraic inversion impractical
- CHECK opcodes comparing accumulated state against embedded constants
- Large `.data` section with repetitive bytecode patterns

**Solving approach:**
1. Parse bytecode to extract CHECK values (expected key after each block)
2. For each block sequentially, brute-force the input bytes that produce the expected key
3. Use the CHECK value as the key for the next block

```c
// OpenMP-parallelized per-block brute-force
uint32_t process(uint32_t val) {
    for (int i = 0; i < 1000; i++) {
        val ^= (val << 13);
        val ^= (val >> 17);
        val ^= (val << 5);
        val *= 0x2545f491;
    }
    return val;
}

int solve_block(uint32_t old_key, uint32_t expected_key, unsigned char *out) {
    int found = 0;
    #pragma omp parallel for shared(found)
    for (int v = 0; v < 0x1000000; v++) {
        if (found) continue;
        uint32_t input_val = ((v >> 16) << 16) | (v & 0xFF) | ((v >> 8 & 0xFF) << 8);
        uint32_t saved = input_val ^ old_key;
        uint32_t final_val = process(saved);
        if ((final_val ^ saved) == expected_key) {
            #pragma omp critical
            { if (!found) { out[0]=v>>16; out[1]=(v>>8)&0xFF; out[2]=v&0xFF; found=1; } }
        }
    }
    return found;
}
// Compile: gcc -O3 -march=native -fopenmp -o solve solve.c
```

**Key insight:** When a transformation is intentionally non-invertible (iterated hash-like function), brute-force is the intended solution. OpenMP parallelization is critical — 287 blocks x 16.7M candidates each takes minutes parallelized vs hours single-threaded. The sequential key dependency means blocks must be solved in order, but each individual block search is embarrassingly parallel.

---

## Burrows-Wheeler Transform Inversion without Terminator (ASIS CTF Finals 2016)

BWT applied to binary representation without a standard terminating character. Requires brute-force inversion by trying all possible original strings.

```python
def bwt_inverse_bruteforce(bwt_string):
    """Invert BWT when no terminating character is present.
    Standard BWT inverse needs the terminator position.
    Without it, try all n possible rotations."""
    n = len(bwt_string)

    # Standard BWT inverse produces a table
    table = [''] * n
    for _ in range(n):
        table = sorted([bwt_string[i] + table[i] for i in range(n)])

    # Without terminator, all n rows are valid candidates
    # Filter by known constraints (e.g., starts with '1' for binary, matches XOR pattern)
    candidates = []
    for row in table:
        # Apply challenge-specific validation
        if is_valid_plaintext(row):
            candidates.append(row)

    return candidates

def bwt_with_xor_rounds(encrypted_hex, num_rounds):
    """Multi-round BWT with XOR key derived from round index"""
    data = bytes.fromhex(encrypted_hex)
    for round_idx in range(num_rounds - 1, -1, -1):
        # Each round: BWT on binary representation, then XOR with round-based key
        binary_str = ''.join(format(b, '08b') for b in data)
        candidates = bwt_inverse_bruteforce(binary_str)
        # Select candidate matching constraints (leading '1', trailing bit rule)
        data = select_valid_candidate(candidates, round_idx)
    return data
```

**Key insight:** Standard BWT uses a terminating character (like '$') to mark the original string's position. Without it, BWT inversion produces n candidates (one per rotation). Use domain-specific constraints (binary format, XOR round structure, flag prefix) to identify the correct candidate.

---

## OpenType Font Ligature Exploitation for Hidden Messages (Hack The Vote 2016)

Font files with custom OpenType ligatures map visible characters to hidden glyphs. The GSUB (Glyph Substitution) table defines these mappings.

```python
from fontTools.ttLib import TTFont

def decode_font_ligatures(font_path, encoded_text):
    """Extract ligature substitution table and decode message"""
    font = TTFont(font_path)

    # Extract GSUB table for ligature substitutions
    gsub = font['GSUB']

    # Navigate to ligature lookup
    ligature_map = {}
    for lookup in gsub.table.LookupList.Lookup:
        for subtable in lookup.SubTable:
            if hasattr(subtable, 'ligatures'):
                for glyph_name, ligatures in subtable.ligatures.items():
                    for lig in ligatures:
                        # Map: input sequence -> output glyph
                        input_seq = [glyph_name] + lig.Component
                        output = lig.LigGlyph
                        ligature_map[tuple(input_seq)] = output

    print("Ligature mappings found:")
    for inp, out in ligature_map.items():
        print(f"  {inp} -> {out}")

    # Alternative: convert TTF to XML for manual analysis
    # font.saveXML('font_dump.xml')
    # Search for <LigatureSubst> entries

# Command-line approach:
# pip install fonttools
# ttx font.otf  # converts to XML
# grep -A5 'LigatureSubst' font.ttx
```

**Key insight:** Custom fonts with GSUB ligature tables create a cipher where displayed characters differ from their glyph mappings. The `fonttools` library's `ttx` command dumps the font to XML, making ligature substitution tables easily readable. Each ligature maps an input character sequence to a different output glyph.

---

## GLSL Shader VM with Self-Modifying Code (ApoorvCTF 2026)

**Pattern (Draw Me):** A WebGL2 fragment shader implements a Turing-complete VM on a 256x256 RGBA texture. The texture is both program memory and display output.

**Texture layout:**
- **Row 0:** Registers (pixel 0 = instruction pointer, pixels 1-32 = general purpose)
- **Rows 1-127:** Program memory (RGBA = opcode, arg1, arg2, arg3)
- **Rows 128-255:** VRAM (display output)

**Opcodes:** NOP(0), SET(1), ADD(2), SUB(3), XOR(4), JMP(5), JNZ(6), VRAM-write(7), STORE(8), LOAD(9). 16 steps per frame.

**Self-modifying code:** Phase 1 (decryption) uses STORE opcode to XOR-patch program memory that Phase 2 (drawing) then executes. The decryption overwrites SET instructions with correct pixel color values before the drawing code runs.

**Why GPU rendering fails:** The GPU runs all pixels in parallel per frame, but the shader tracks only ONE write target per pixel per frame. With multiple VRAM writes per frame, only the last survives — losing 75%+ of pixels. Similarly, STORE patches conflict during parallel decryption.

**Solve via sequential emulation:**
```python
from PIL import Image
import numpy as np

img = Image.open('program.png').convert('RGBA')
state = np.array(img, dtype=np.int32).copy()
regs = [0] * 33

# Phase 1: Trace decryption — apply all STORE patches sequentially
x, y = start_x, start_y
while True:
    r, g, b, a = state[y][x]
    opcode = int(r)
    if opcode == 1: regs[g] = b & 255           # SET
    elif opcode == 4: regs[g] = regs[b] ^ regs[a]  # XOR
    elif opcode == 8:                              # STORE — patches program memory
        tx, ty = regs[g], regs[b]
        state[ty][tx] = [regs[a], regs[a+1], regs[a+2], regs[a+3]]
    elif opcode == 5: break                        # JMP to drawing phase
    x += 1
    if x > 255: x, y = 0, y + 1

# Phase 2: Execute drawing code — all VRAM writes preserved
vram = np.zeros((128, 256), dtype=np.uint8)
# ... trace with opcode 7 writing to vram[ty][tx] = color
Image.fromarray(vram, mode='L').save('output.png')
```

**Key insight:** GLSL shaders are Turing-complete but GPU parallelism causes write conflicts. Self-modifying code (STORE patches) compounds the problem — patches from parallel executions overwrite each other. Sequential emulation in Python recovers the full output. The program.png file IS the bytecode.

**Detection:** WebGL/shader challenge with a PNG "program" file, challenge says "nothing renders" or output is garbled. Look for custom opcode tables in GLSL source.

---

## Instruction Counter as Cryptographic State (MetaCTF Flash 2026)

**Pattern (Who's Counting?):** Hand-written assembly binary uses a dedicated register (e.g., `r12`) as an instruction counter that increments after nearly every instruction. The counter value feeds into XOR, ROL, and multiply transformations on each input byte, making the entire transformation path-dependent on the number of instructions executed before reaching each byte.

**Identification:**
- Hand-written assembly (no compiler patterns, unusual register usage)
- A register that only increments (`inc r12` or `add r12, 1`) appearing after most instructions
- Transformations that reference this counter register (`xor rax, r12`, `rol al, cl` where `cl` derives from counter)
- Sequential byte processing loop where state carries forward

**Solving approach:**
```python
# Byte-by-byte brute force with emulation
# Since each byte's transformation depends on the counter (which depends
# on all prior instructions), state is path-dependent.

from unicorn import *
from unicorn.x86_const import *

def try_byte(known_prefix, candidate_byte):
    """Emulate binary with known prefix + candidate, check output."""
    uc = Uc(UC_ARCH_X86, UC_MODE_64)
    # Map code, stack, data segments
    uc.mem_map(CODE_BASE, 0x10000)
    uc.mem_write(CODE_BASE, binary_code)
    uc.mem_map(STACK_BASE, 0x10000)
    uc.mem_map(DATA_BASE, 0x10000)

    # Write input: known_prefix + candidate
    test_input = known_prefix + bytes([candidate_byte])
    uc.mem_write(DATA_BASE, test_input + b'\x00' * (64 - len(test_input)))

    # Set up registers (rsp, rdi pointing to input, r12 = 0)
    uc.reg_write(UC_X86_REG_RSP, STACK_BASE + 0x8000)
    uc.reg_write(UC_X86_REG_R12, 0)  # instruction counter starts at 0

    try:
        uc.emu_start(CODE_BASE + ENTRY_OFFSET, CODE_BASE + EXIT_OFFSET)
        # Read transformed output, compare against expected
        output = uc.mem_read(OUTPUT_ADDR, len(test_input))
        return output[:len(test_input)] == expected[:len(test_input)]
    except:
        return False

# Recover flag byte by byte
flag = b''
for pos in range(FLAG_LEN):
    for b in range(256):
        if try_byte(flag, b):
            flag += bytes([b])
            print(f"Position {pos}: {chr(b)} -> {flag}")
            break
```

**Key insight:** When a register acts as an instruction counter feeding into byte transformations, the transformation of byte N depends on the exact number of instructions executed while processing bytes 0 through N-1. This makes analytical inversion impractical because the counter value at each byte position depends on the execution path through all prior bytes. Byte-by-byte brute force with full emulation (Unicorn or GDB scripting) is the most reliable approach -- try all 256 values for each position, keeping the state from the correct prefix.

**When to recognize:** Binary has no standard library calls, uses unusual registers consistently, and shows a register that only increments. The transformation per byte involves operations (XOR, rotate, multiply) that reference this counter. Challenge name hints at "counting" or "instructions".

**Alternative approaches:**
- GDB scripting: set breakpoint after each byte's transformation, compare output
- Static analysis: count instructions manually to compute counter values, then invert transforms algebraically (error-prone due to counter accumulation)

**References:** MetaCTF Flash CTF 2026 "Who's Counting?"

---

## Thread Race Condition with Signed Integer Overflow (Codegate 2017)

**Pattern (Hunting):** A game binary uses thread-unsafe skill selection. The attack thread checks `skill_id <= 4` using signed comparison, then sleeps briefly before applying damage. During the sleep, switch to a different skill. The fireball skill uses `cdqe` (sign-extend EAX to RAX), converting `0xFFFFFFFF` (icesword damage) to `-1` as a signed 64-bit value. Subtracting `-1` from the boss's HP (`0x7FFFFFFFFFFFFFFF`) causes signed overflow to a negative value, killing the boss.

```python
# Race condition exploit:
# Thread A: select fireball (skill_id=2, passes <= 4 check)
# Thread A: sleeps for animation
# Main: switch to icesword (skill_id=5, damage=0xFFFFFFFF)
# Thread A: wakes, reads damage from icesword slot
# cdqe: 0xFFFFFFFF -> 0xFFFFFFFFFFFFFFFF (-1 signed)
# boss_hp -= (-1) -> boss_hp = 0x7FFFFFFFFFFFFFFF + 1 = negative -> dead

import time, threading
def race():
    select_skill(2)  # fireball - passes bounds check
    time.sleep(0.001)
    select_skill(5)  # icesword - race into damage calculation
```

**Key insight:** `cdqe` (Convert Doubleword to Quadword Extension) sign-extends 32-bit EAX into 64-bit RAX. When the attack code reads a 32-bit damage value and sign-extends it, `0xFFFFFFFF` becomes `-1`. Subtracting a negative number adds to HP, but if HP is already at `INT64_MAX`, the addition overflows to negative, killing the target.

---

## ESP32/Xtensa Firmware Reversing with ROM Symbol Map (Insomni'hack 2017)

**Pattern (Internet of Fail):** ESP32 firmware (Xtensa architecture) with no native IDA support. Use radare2 with the ESP32 ROM linker script (`esp32.rom.ld`) to map function addresses to names. Cross-reference with public ESP32 HTTP server source code to identify the password-checking logic, composed of ~20 conditional XOR functions operating on a global state variable.

```bash
# Load ESP32 firmware in radare2
r2 -a xtensa -b 32 firmware.bin

# Apply ROM symbol map from ESP-IDF
# esp32.rom.ld maps addresses like:
# 0x40000000 = ets_printf
# 0x400013A0 = cache_Read_Enable
# Load as flags: . esp32.rom.ld.r2

# Identify HTTP request handler by cross-referencing
# with esp-idf/examples/protocols/http_server
# Look for URI handler registration patterns
```

**Key insight:** ESP32's Xtensa architecture lacks mainstream RE tool support, but the ESP-IDF SDK provides ROM linker scripts mapping every ROM function address to its name. Loading these as symbols in radare2 immediately resolves hundreds of function calls. Cross-referencing with public ESP-IDF example code identifies application-level patterns (HTTP handlers, WiFi callbacks) even in stripped firmware.

---

## Batch Crackme Automation via objdump Pattern Extraction (DEF CON 2017)

Solve hundreds of identical-structure crackmes by scripting `objdump` to extract comparison values and arithmetic operations, computing keys without execution.

```bash
# Simple variant: extract CMP immediates directly
objdump -M intel -d $binary | grep -P "cmp\s+rdi" | \
    grep -oP "0x\w{1,2}" | xxd -r -p

# Complex variant: parse add/sub/cmp chains and reverse-compute
# Each binary: series of add/sub rdi,N then cmp rdi,target
# Reverse: start from target, undo operations in reverse order
python3 <<'EOF'
import subprocess, re, glob
for binary in sorted(glob.glob("crackmes/*")):
    asm = subprocess.check_output(["objdump", "-M", "intel", "-d", binary]).decode()
    ops = re.findall(r'(add|sub)\s+rdi,(0x\w+)', asm)
    target = int(re.search(r'cmp\s+rdi,(0x\w+)', asm).group(1), 16)
    # Reverse operations
    for op, val in reversed(ops):
        val = int(val, 16)
        target = (target - val) if op == 'add' else (target + val)
    print(chr(target & 0xff), end='')
EOF
```

**Key insight:** Mass crackme challenges (100s-1000s of binaries) have identical structure with per-binary constants. Script `objdump` disassembly parsing to extract immediates and arithmetic sequences, then reverse-compute the key algebraically. No execution or emulation needed.

---

## Fork + Pipe + Dead Branch Anti-Analysis (RCTF 2017)

Binary uses fork/pipe IPC where the parent writes data and exits, child reads from pipe and continues. Key validation is in a dead branch (always-false comparison) that requires binary patching to reach.

```bash
# Detection: fork() + pipe() + read()/write() in main
# The child process reads from pipe, needs to know its own PID

# Dead branch pattern:
# cmp DWORD PTR [ebp-0xc], 0x1  ; compares 0 with 1, always false
# je  real_flag_computation      ; never taken

# Patch: change comparison value from 0x1 to 0x0
# Find: 83 7d f4 01 → change to: 83 7d f4 00
python3 -c "
data = open('binary','rb').read()
data = data.replace(b'\x83\x7d\xf4\x01', b'\x83\x7d\xf4\x00')
open('binary_patched','wb').write(data)
"
```

**Key insight:** Fork+pipe creates a parent-child relationship where the parent provides data and exits. Dead branches (comparisons that always evaluate to false) hide the real validation logic. `strace` reveals the fork/pipe/read pattern; patching the comparison constant reaches the hidden code path.

---

---

## Time-Locked Binary with Date-Based Key (Hack.lu 2017)

Binary reads the system date and only executes correctly on a specific date (e.g., December 21, 2012). The date constant appears in the binary as a Unix timestamp or structured date comparison.

**Detection:** Look for comparisons against large integer constants that fall in a recognizable date range (Unix timestamps: 2012 = ~1.35B, 2017 = ~1.5B). Cultural significance helps: apocalypse dates, CTF release dates, historical events.

```bash
# Set system clock to the required date
sudo date -s "2012-12-21 00:00:00"
./binary

# Or use faketime to avoid system-wide change
LD_PRELOAD=/usr/lib/faketime/libfaketime.so.1 FAKETIME="2012-12-21 00:00:00" ./binary

# Restore system time afterward
sudo ntpdate pool.ntp.org
```

**In IDA/Ghidra:** Search for `time()` or `localtime()` calls. The struct `tm` fields to watch: `tm_year` (years since 1900), `tm_mon` (0-based), `tm_mday`.

**Key insight:** Time-based keys use culturally significant dates. Always check for date comparisons in reversed code and try setting the system clock or using faketime before attempting deeper analysis.

**References:** Hack.lu CTF 2017

---

## ARM Code in Image Pixels via UnicornJS (Hack.lu 2017)

JavaScript challenge embeds ARM bytecode in image pixel data. The image is base64-encoded in the HTML/JS source. Pixel RGBA values encode ARM instructions. A bundled UnicornJS library (ARM CPU emulator in JavaScript) extracts and executes the bytecode.

**Identification flow:**
1. Find base64 blob in JS source → decode → PNG/BMP file
2. Identify UnicornJS import (`unicorn.js`, `uc.js`, or similar) → confirms ARM emulation
3. Pixel extraction loop: RGBA bytes concatenated in raster order form the ARM instruction stream
4. Feed the extracted bytes to an ARM disassembler

```python
from PIL import Image
import capstone

img = Image.open('decoded.png').convert('RGBA')
pixels = list(img.getdata())

# Extract ARM bytecode from pixel data (4 bytes per pixel: R, G, B, A)
arm_code = bytes([channel for pixel in pixels for channel in pixel])

# Disassemble as ARM Thumb or ARM32
md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)
for insn in md.disasm(arm_code, 0x0):
    print(f"0x{insn.address:04x}: {insn.mnemonic} {insn.op_str}")
```

**Key insight:** Multi-layer obfuscation: ARM code in image pixels, base64 encoded, emulated via UnicornJS at runtime. Identify the emulator library first to know which ISA to reverse — the library name reveals the architecture.

**References:** Hack.lu CTF 2017

---

## x86 16-bit MBR psadbw Constraint Solving (CSAW 2017)

Bootable MBR uses SSE2 `psadbw` (Packed Sum of Absolute Differences of Bytes) on xmm registers to validate the flag. Each iteration masks 2 input bytes, computes `psadbw` against known constants, and compares the sum to an expected value.

**`psadbw` semantics:**
```asm
psadbw xmm0, xmm1
; For each of 8 byte pairs: sum += |xmm0[i] - xmm1[i]|
; Result stored as 16-bit integer in low qword of xmm0
```

This generates sum-of-absolute-differences equations:
```text
|a[0] - k[0]| + |a[1] - k[1]| + ... + |a[7] - k[7]| = C
```

**Solution approach:**
```python
import numpy as np
from itertools import product

# For each 2-byte masked group, extract the constants and expected sum
# Equations are not purely linear (absolute value), but printable ASCII
# constrains each byte to [0x20, 0x7e], limiting brute-force space

def solve_psadbw_group(known_constants, expected_sum, printable_range=(0x20, 0x7e)):
    """Brute-force 2 unknown bytes given sum-of-abs-diff constraint."""
    solutions = []
    for a, b in product(range(*printable_range), repeat=2):
        pair = [a, b]
        sad = sum(abs(pair[i] - known_constants[i]) for i in range(len(pair)))
        if sad == expected_sum:
            solutions.append(bytes([a, b]))
    return solutions

# For ambiguous cases with multiple solutions: apply additional constraints
# (flag format prefix, character frequency, subsequent iterations)
```

**Key insight:** `psadbw` creates sum-of-absolute-difference equations — not purely linear but solvable with constrained brute-force when bytes are limited to printable ASCII. Each 2-byte group is independent, keeping the search space to 95^2 = ~9000 candidates per group.

**References:** CSAW CTF 2017

---

See also: [patterns-ctf.md](patterns-ctf.md) for Part 1, [patterns-ctf-2.md](patterns-ctf-2.md) for Part 2 (multi-layer self-decrypting binary, embedded ZIP+XOR license, stack string deobfuscation, prefix hash brute-force, CVP/LLL lattice, decision tree obfuscation, GF(2^8) Gaussian elimination).


# patterns-ctf

# CTF Reverse - Competition-Specific Patterns (Part 1)

## Table of Contents
- [Hidden Emulator Opcodes + LD_PRELOAD Key Extraction (0xFun 2026)](#hidden-emulator-opcodes--ld_preload-key-extraction-0xfun-2026)
- [Spectre-RSB SPN Cipher — Static Parameter Extraction (0xFun 2026)](#spectre-rsb-spn-cipher--static-parameter-extraction-0xfun-2026)
- [Image XOR Mask Recovery via Smoothness (VuwCTF 2025)](#image-xor-mask-recovery-via-smoothness-vuwctf-2025)
- [Shellcode in Data Section via mmap RWX (VuwCTF 2025)](#shellcode-in-data-section-via-mmap-rwx-vuwctf-2025)
- [Recursive execve Subtraction (VuwCTF 2025)](#recursive-execve-subtraction-vuwctf-2025)
- [Byte-at-a-Time Block Cipher Attack (UTCTF 2024)](#byte-at-a-time-block-cipher-attack-utctf-2024)
- [Mathematical Convergence Bitmap (EHAX 2026)](#mathematical-convergence-bitmap-ehax-2026)
- [Windows PE XOR Bitmap Extraction + OCR (srdnlenCTF 2026)](#windows-pe-xor-bitmap-extraction--ocr-srdnlenctf-2026)
- [Two-Stage Loader: RC4 Gate + VM Constraints (srdnlenCTF 2026)](#two-stage-loader-rc4-gate--vm-constraints-srdnlenctf-2026)
- [GBA ROM VM Hash Inversion via Meet-in-the-Middle (srdnlenCTF 2026)](#gba-rom-vm-hash-inversion-via-meet-in-the-middle-srdnlenctf-2026)
- [Sprague-Grundy Game Theory Binary (DiceCTF 2026)](#sprague-grundy-game-theory-binary-dicectf-2026)
- [Kernel Module Maze Solving (DiceCTF 2026)](#kernel-module-maze-solving-dicectf-2026)
- [Multi-Threaded VM with Channel Synchronization (DiceCTF 2026)](#multi-threaded-vm-with-channel-synchronization-dicectf-2026)
- [Backdoored Shared Library Detection via String Diffing (Hack.lu CTF 2012)](#backdoored-shared-library-detection-via-string-diffing-hacklu-ctf-2012)
- [Custom binfmt Kernel Module with RC4 Flat Binaries (BSidesSF 2026)](#custom-binfmt-kernel-module-with-rc4-flat-binaries-bsidessf-2026)
- [Hash-Resolved Imports / No-Import Ransomware (BSidesSF 2026)](#hash-resolved-imports--no-import-ransomware-bsidessf-2026)
- [ELF Section Header Corruption for Anti-Analysis (BSidesSF 2026)](#elf-section-header-corruption-for-anti-analysis-bsidessf-2026)

---

## Hidden Emulator Opcodes + LD_PRELOAD Key Extraction (0xFun 2026)

**Pattern (CHIP-8):** Non-standard opcode `FxFF` triggers hidden `superChipRendrer()` → AES-256-CBC decryption. Key derived from binary constants.

**Technique:**
1. Check all instruction dispatch branches for non-standard opcodes
2. Hidden opcode may trigger crypto functions (OpenSSL)
3. Use `LD_PRELOAD` hook on `EVP_DecryptInit_ex` to capture AES key at runtime:

```c
#include <openssl/evp.h>
int EVP_DecryptInit_ex(EVP_CIPHER_CTX *ctx, const EVP_CIPHER *type,
                       ENGINE *impl, const unsigned char *key,
                       const unsigned char *iv) {
    // Log key
    for (int i = 0; i < 32; i++) printf("%02x", key[i]);
    printf("\n");
    // Call original
    return ((typeof(EVP_DecryptInit_ex)*)dlsym(RTLD_NEXT, "EVP_DecryptInit_ex"))
           (ctx, type, impl, key, iv);
}
```

```bash
gcc -shared -fPIC -ldl -lssl hook.c -o hook.so
LD_PRELOAD=./hook.so ./emulator rom.ch8
```

---

## Spectre-RSB SPN Cipher — Static Parameter Extraction (0xFun 2026)

**Pattern:** Binary uses cache side channels to implement S-boxes, but ALL cipher parameters (round keys, S-box tables, permutation) are in the binary's data section.

**Key insight:** Don't try to run on special hardware. Extract parameters statically:
- 8 S-boxes × 8 output bits, 256 entries each
- Values `0x340` = bit 1, `0x100` = bit 0
- 64-byte permutation table, 8 round keys

```python
# Extract from binary data section
import struct
sbox = [[0]*256 for _ in range(8)]
for i in range(8):
    for j in range(256):
        val = struct.unpack('<I', data[sbox_offset + (i*256+j)*4 : ...])[0]
        sbox[i][j] = 1 if val == 0x340 else 0
```

**Lesson:** Side-channel implementations embed lookup tables in memory. Extract statically.

---

## Image XOR Mask Recovery via Smoothness (VuwCTF 2025)

**Pattern (Trianglification):** Image divided into triangle regions, each XOR-encrypted with `key = (mask * x - y) & 0xFF` where mask is unknown (0-255).

**Recovery:** Natural images have smooth gradients. Brute-force mask (256 values per region), score by neighbor pixel differences:

```python
import numpy as np
from PIL import Image

img = np.array(Image.open('encrypted.png'))

def score_smoothness(region_pixels, mask, positions):
    decrypted = []
    for (x, y), pixel in zip(positions, region_pixels):
        key = (mask * x - y) & 0xFF
        decrypted.append(pixel ^ key)
    # Score: sum of absolute differences between adjacent pixels
    return -sum(abs(decrypted[i] - decrypted[i+1]) for i in range(len(decrypted)-1))

for region in regions:
    best_mask = max(range(256), key=lambda m: score_smoothness(region, m, positions))
```

**Search space:** 256 candidates × N regions = trivial. Smoothness is a reliable scoring metric for natural images.

---

## Shellcode in Data Section via mmap RWX (VuwCTF 2025)

**Pattern (Missing Function):** Binary relocates data to RWX memory (mmap with PROT_READ|PROT_WRITE|PROT_EXEC) and jumps to it.

**Detection:** Look for `mmap` with PROT_EXEC flag. Embedded shellcode often uses XOR with rotating key.

**Analysis:** Extract data section, apply XOR key (try 3-byte rotating), disassemble result.

---

## Recursive execve Subtraction (VuwCTF 2025)

**Pattern (String Inspector):** Binary recursively calls itself via `execve`, subtracting constants each time.

**Solution:** Find base case and work backward. Often a mathematical relationship like `N * M + remainder`.

---

## Byte-at-a-Time Block Cipher Attack (UTCTF 2024)

**Pattern (PES-128):** First output byte depends only on first input byte (no diffusion).

**Attack:** For each position, try all 256 byte values, compare output byte with target ciphertext. One match per byte = full plaintext recovery without knowing the key.

**Detection:** Change one input byte → only corresponding output byte changes. This means zero cross-byte diffusion = trivially breakable.

---

## Mathematical Convergence Bitmap (EHAX 2026)

**Pattern (Compute It):** Binary classifies complex-plane coordinates by Newton's method convergence. The classification results, arranged as a grid, spell out the flag in ASCII art.

**Recognition:**
- Input file with coordinate pairs (x, y)
- Binary iterates a mathematical function (e.g., z^3 - 1 = 0) and outputs pass/fail
- Grid dimensions hinted by point count (e.g., 2600 = 130×20)
- 5-pixel-high ASCII art font common in CTFs

**Newton's method for z^3 - 1:**
```python
def newton_converges_to_one(px, py, max_iter=50, target_count=12):
    """Returns True if Newton's method converges to z=1 in exactly target_count steps."""
    x, y = px, py
    count = 0
    for _ in range(max_iter):
        f_real = x**3 - 3*x*y**2 - 1.0
        f_imag = 3*x**2*y - y**3
        J_rr = 3.0 * (x**2 - y**2)
        J_ri = 6.0 * x * y
        det = J_rr**2 + J_ri**2
        if det < 1e-9:
            break
        x -= (f_real * J_rr + f_imag * J_ri) / det
        y -= (f_imag * J_rr - f_real * J_ri) / det
        count += 1
        if abs(x - 1.0) < 1e-6 and abs(y) < 1e-6:
            break
    return count == target_count

# Read coordinates and render bitmap
points = [(float(x), float(y)) for x, y in ...]
bits = [1 if newton_converges_to_one(px, py) else 0 for px, py in points]
WIDTH = 130  # 2600 / 20 rows
for r in range(len(bits) // WIDTH):
    print(''.join('#' if bits[r*WIDTH+c] else '.' for c in range(WIDTH)))
```

**Key insight:** The binary is a mathematical classifier, not a flag checker. The flag is in the visual pattern of classifications, not in the binary's output. Reverse-engineer the math, apply to all coordinates, and visualize as bitmap.

---

## Windows PE XOR Bitmap Extraction + OCR (srdnlenCTF 2026)

**Pattern (Artistic Warmup):** Binary renders input text, compares rendered bitmap against expected pixel data stored XOR'd with constant in `.rdata`. No need to compute — extract expected pixels directly.

**Attack:**
1. Reverse the core check function to identify rendering and comparison logic
2. Find the expected pixel blob in `.rdata` (look for large data block referenced near comparison)
3. XOR with constant (e.g., 0xAA) to recover expected rendered DIB
4. Save as image and OCR to recover flag text

```python
import numpy as np
from PIL import Image

with open("binary.exe", "rb") as f:
    data = f.read()

# Extract from .rdata section (offsets from reversing)
blob_offset = 0xC3620  # .rdata offset to XOR'd blob
blob_size = 0x15F90     # 450 * 50 * 4 (BGRA)
blob = np.frombuffer(data[blob_offset:blob_offset + blob_size], dtype=np.uint8)
expected = blob ^ 0xAA  # XOR with constant key

# Reshape as BGRA image (dimensions from reversing)
img = expected.reshape(50, 450, 4)
channel = img[:, :, 0]  # Take one channel (grayscale text)
Image.fromarray(channel, "L").save("target.png")

# OCR with charset whitelist
import subprocess
result = subprocess.run(
    ["tesseract", "target.png", "stdout", "-c",
     "tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789{}_"],
    capture_output=True, text=True)
print(result.stdout)
```

**Key insight:** When a binary renders text and compares pixels, the expected pixel data is the flag rendered as an image. Extract it directly from the binary data section without needing to understand the rendering logic. OCR with charset whitelist improves accuracy for CTF flag characters.

---

## Two-Stage Loader: RC4 Gate + VM Constraints (srdnlenCTF 2026)

**Pattern (Cornflake v3.5):** Two-stage malware loader — stage 1 uses RC4 username gate, stage 2 downloaded from C2 contains VM-based password validation.

**Stage 1 — RC4 username recovery:**
```python
def rc4(key, data):
    s = list(range(256))
    j = 0
    for i in range(256):
        j = (j + s[i] + key[i % len(key)]) & 0xFF
        s[i], s[j] = s[j], s[i]
    i = j = 0
    out = bytearray()
    for b in data:
        i = (i + 1) & 0xFF
        j = (j + s[i]) & 0xFF
        s[i], s[j] = s[j], s[i]
        out.append(b ^ s[(s[i] + s[j]) & 0xFF])
    return bytes(out)

# Key from binary strings, ciphertext from stored hex
username = rc4(b"s3cr3t_k3y_v1", bytes.fromhex("46f5289437bc009c17817e997ae82bfbd065545d"))
```

**Stage 2 — VM constraint extraction:**
1. Download stage 2 from C2 endpoint (e.g., `/updates/check.php`)
2. Reverse VM bytecode interpreter (typically 15-20 opcodes)
3. Extract linear equality constraints over flag characters
4. Solve constraint system (Z3 or manual)

**Key insight:** Multi-stage loaders often use simple crypto (RC4) for the first gate and more complex validation (custom VM) for the second. The VM memory may be uninitialized (all zeros), drastically simplifying constraint extraction since memory-dependent operations become constants.

---

## GBA ROM VM Hash Inversion via Meet-in-the-Middle (srdnlenCTF 2026)

**Pattern (Dante's Trial):** Game Boy Advance ROM implements a custom VM. Hash function uses FNV-1a variant with uninitialized memory (stays all zeros). Meet-in-the-middle attack splits the search space.

**Hash function structure:**
```python
# FNV-1a variant with XOR/multiply
P = 0x100000001b3        # FNV prime
CUP = 0x9e3779b185ebca87  # Golden ratio constant
MASK64 = (1 << 64) - 1

def fmix64(h):
    """Finalization mixer."""
    h ^= h >> 33; h = (h * 0xff51afd7ed558ccd) & MASK64
    h ^= h >> 33; h = (h * 0xc4ceb9fe1a85ec53) & MASK64
    h ^= h >> 33
    return h

def hash_input(chars, seed_lo=0x84222325, seed_hi=0xcbf29ce4):
    hlo, hhi, ptr = seed_lo, seed_hi, 0
    for c in chars:
        # tri_mix(c, mem[ptr]) — mem is always 0
        delta = ((ord(c) * CUP) ^ (0 * P)) & MASK64
        hlo = ((hlo ^ (delta & 0xFFFFFFFF)) * (P & 0xFFFFFFFF)) & 0xFFFFFFFF
        hhi = ((hhi ^ (delta >> 32)) * (P >> 32)) & 0xFFFFFFFF
        ptr = (ptr + 1) & 0xFF
    combined = ((hhi << 32) | (hlo ^ ptr)) & MASK64
    return fmix64((combined * P) & MASK64)
```

**Meet-in-the-middle attack:**
```python
import string

TARGET = 0x73f3ebcbd9b4cd93
LENGTH = 6
SPLIT = 3
charset = [c for c in string.printable if 32 <= ord(c) < 127]

# Forward pass: enumerate first 3 characters from seed state
forward = {}
for c1 in charset:
    for c2 in charset:
        for c3 in charset:
            state = hash_forward(seed, [c1, c2, c3])
            forward[state] = c1 + c2 + c3

# Backward pass: invert fmix64 and final multiply, enumerate last 3 chars
inv_target = invert_fmix64(TARGET)
for c4 in charset:
    for c5 in charset:
        for c6 in charset:
            state = hash_backward(inv_target, [c4, c5, c6])
            if state in forward:
                print(f"Found: {forward[state]}{c4}{c5}{c6}")
```

**Key insight:** Meet-in-the-middle reduces search from `95^6 ≈ 7.4×10^11` to `2×95^3 ≈ 1.7×10^6` — a factor of ~430,000x speedup. Critical when the hash function is invertible from the output side (i.e., `fmix64` and the final multiply can be undone). Also: uninitialized VM memory that stays zero simplifies the hash function by removing a variable.

---

## Sprague-Grundy Game Theory Binary (DiceCTF 2026)

**Pattern (Bedtime):** Stripped Rust binary plays N rounds of bounded Nim. Each round has piles and max-move parameter k. Binary uses a PRNG for moves when in a losing position; user must respond optimally so the PRNG eventually generates an invalid move (returns 1). Sum of return values must equal a target.

**Game theory identification:**
- Bounded Nim: remove 1 to k items from any pile per turn
- **Grundy value** per pile: `pile_value % (k+1)`
- **XOR** of all Grundy values: non-zero = winning (N-position), zero = losing (P-position)
- N-positions: computer wins automatically (returns 0)
- P-positions: computer uses PRNG, may make invalid move (returns 1)

**PRNG state tracking through user feedback:**
```python
MASK64 = (1 << 64) - 1

def prng_step(state, pile_count, k):
    """Computer's PRNG move. Returns (pile_idx, amount, new_state)."""
    r12 = state[2] ^ 0x28027f28b04ccfa7
    rax = (state[1] + r12) & MASK64
    s0_new = ROL64((state[0] ** 2 + rax) & MASK64, 32)
    r12_upd = (r12 + rax) & MASK64
    s0_final = ROL64((s0_new ** 2 + r12_upd) & MASK64, 32)

    pile_idx = rax % pile_count
    amount = (r12_upd % k) + 1
    return pile_idx, amount, [s0_final, r12_upd, state[2]]

# Critical: state[2] updated ONLY by user moves (XOR of pile_idx, amount, new_value)
# PRNG moves do NOT affect state[2] — creates feedback loop
```

**Solving approach:**
1. Dump game data from GDB (all entries with pile values and parameters)
2. Classify: count P-positions (return 1) vs N-positions (return 0)
3. Simulate each P-position: PRNG moves → user responds optimally → track state[2]
4. Encode user moves as input format (4-digit decimal pairs, reversed order)

**Key insight:** When a game binary's PRNG state depends on user input, you must simulate the full feedback loop — not just solve the game theory. Use GDB hardware watchpoints to discover which state variables are affected by user vs computer moves.

---

## Kernel Module Maze Solving (DiceCTF 2026)

**Pattern (Explorer):** Rust kernel module implements a 3D maze via `/dev/challenge` ioctls. Navigate the maze, avoid decoy exits (status=2), find the real exit (status=1), read the flag.

**Ioctl enumeration:**
| Command | Description |
|---------|-------------|
| `0x80046481-83` | Get maze dimensions (3 axes, 8-16 each) |
| `0x80046485` | Get status: 0=playing, 1=WIN, 2=decoy |
| `0x80046486` | Get wall bitfield (6 directions) |
| `0x80406487` | Get flag (64 bytes, only when status=1) |
| `0x40046488` | Move in direction (0-5) |
| `0x6489` | Reset position |

**DFS solver with decoy avoidance:**
```c
// Minimal static binary using raw syscalls (no libc) for small upload size
// gcc -nostdlib -static -Os -fno-builtin -o solve solve.c -Wl,--gc-sections && strip solve

int visited[16][16][16];
int bad[16][16][16];   // decoy positions across resets

void dfs(int fd, int x, int y, int z) {
    if (visited[x][y][z] || bad[x][y][z]) return;
    visited[x][y][z] = 1;

    int status = ioctl_get_status(fd);
    if (status == 1) { read_flag(fd); exit(0); }
    if (status == 2) { bad[x][y][z] = 1; return; }  // decoy — mark bad

    int walls = ioctl_get_walls(fd);
    int dx[] = {1,-1,0,0,0,0}, dy[] = {0,0,1,-1,0,0}, dz[] = {0,0,0,0,1,-1};
    int opp[] = {2,3,0,1,5,4};  // opposite directions for backtracking

    for (int dir = 0; dir < 6; dir++) {
        if (!(walls & (1 << dir))) continue;  // wall present
        ioctl_move(fd, dir);
        dfs(fd, x+dx[dir], y+dy[dir], z+dz[dir]);
        ioctl_move(fd, opp[dir]);  // backtrack
    }
}
// After decoy hit: reset via ioctl 0x6489, clear visited, re-run DFS
```

**Remote deployment:** Upload binary via base64 chunks over netcat shell, decode, execute.

**Key insight:** For kernel module challenges, injecting test binaries into initramfs and probing ioctls dynamically is faster than static RE of stripped kernel modules. Keep solver binary minimal (raw syscalls, no libc) for fast upload.

---

## Multi-Threaded VM with Channel Synchronization (DiceCTF 2026)

**Pattern (locked-in):** Custom stack-based VM runs 16 concurrent threads verifying a 30-char flag. Threads communicate via futex-based channels. Pipeline: input → XOR scramble → transformation → base-4 state machine → final check.

**Analysis approach:**
1. **Identify thread roles** by tracing channel read/write patterns in GDB
2. **Extract constants** (XOR scramble values, lookup tables) via breakpoints on specific opcodes
3. **Watch for inverted logic:** validity check returns 0 for valid, non-zero for blocked (opposite of intuition)
4. **Detect futex quirks:** `unlock_pi` on unowned mutex returns EPERM=1, which can change all computations

**BFS state space search for constrained state machines:**
```python
from collections import deque

def solve_flag(scramble_vals, lookup_table, initial_state, target_state):
    """BFS through state machine to find valid flag bytes."""
    flag = [None] * 30
    # Known prefix/suffix from flag format
    flag[0:5] = list(b'dice{')
    flag[29] = ord('}')

    # For each unknown position, try all printable ASCII
    states = {initial_state}
    for pos in range(28, 4, -1):  # processed in reverse
        next_states = {}
        for state in states:
            for ch in range(32, 127):
                transformed = transform(ch, scramble_vals[pos])
                digits = to_base4(transformed)
                new_state = apply_digits(state, digits, lookup_table)
                if new_state is not None:  # valid path exists
                    next_states.setdefault(new_state, []).append((state, ch))
        states = set(next_states.keys())

    # Trace back from target_state to recover flag
```

**Key insight:** Multi-threaded VMs require tracing data flow across thread boundaries. Channel-based communication creates a pipeline — identify each thread's role (input, transform, validate, output) by watching which channels it reads/writes. Constants that affect computation may come from unexpected sources (futex return values, thread IDs).

---

## Backdoored Shared Library Detection via String Diffing (Hack.lu CTF 2012)

**Pattern (Zombie Lockbox):** A setuid binary uses `strcmp` for password validation. The expected password is visible via `strings` and works under GDB (which drops suid), but fails when run normally. The binary links against a non-standard libc that patches function behavior based on suid status.

**Detection steps:**
1. Check for non-standard library paths with `ldd`:
```bash
ldd ./binary
# Suspicious: libc.so.6 => /lib/libc/libc.so.6  (non-standard path)
# Normal:    libc.so.6 => /lib32/libc.so.6
```

2. Diff strings between the suspicious and system libc:
```bash
strings /lib/libc/libc.so.6 > suspicious_strings
strings /lib32/libc-2.15.so > normal_strings
diff suspicious_strings normal_strings
```

3. Disassemble the patched function (e.g., `puts`) to find injected code:
```bash
gdb /lib/libc/libc.so.6
(gdb) disas puts
# Look for unexpected calls or branches
# Injected code may check suid status (getuid/geteuid syscalls)
# and swap the expected password at runtime
```

**Key insight:** When a binary behaves differently under GDB vs. normal execution, check `ldd` for non-standard library paths. Suid binaries drop privileges under debuggers, so a backdoored libc can detect this via `getuid`/`geteuid` syscalls and change program behavior accordingly. The `strings | diff` approach quickly reveals injected data without full disassembly.

---

---

## Custom binfmt Kernel Module with RC4 Flat Binaries (BSidesSF 2026)

**Pattern (Private Binary):** A custom Linux kernel module (`.ko`) registers a `binfmt` handler for non-standard binary formats. When a file with a specific magic number is executed, the kernel module intercepts it, decrypts the contents in memory, and jumps to the entry point.

**Reverse engineering approach:**
1. **Analyze the `.ko`:** Look for `register_binfmt()` call — it registers a `struct linux_binfmt` with a `load_binary` callback
2. **Find the magic number:** The `load_binary` function checks the file's first bytes against a specific magic number to identify its format
3. **Extract the encryption key:** Look for `movabs` instructions loading 8-byte constants — these are often RC4 key bytes
4. **Identify the encryption scheme:** Common choices are RC4, XOR, or AES-ECB. RC4 is identifiable by the S-box initialization loop (256-byte array, swap pattern)
5. **Decrypt the flat binary:** Apply the recovered key to the encrypted file contents, skipping any header

```python
from Crypto.Cipher import ARC4

# Extract RC4 key from kernel module (found via movabs instructions)
key = bytes([0x41, 0x42, 0x43, ...])  # Key bytes from .ko disassembly

with open('encrypted.bin', 'rb') as f:
    header = f.read(HEADER_SIZE)  # Skip binfmt header
    encrypted = f.read()

cipher = ARC4.new(key)
decrypted = cipher.decrypt(encrypted)

# The decrypted output is a flat binary (no ELF headers)
# Load at the fixed virtual address specified in the kernel module
# Disassemble with: objdump -b binary -m i386:x86-64 -D decrypted.bin
# Or in Ghidra: import as "Raw Binary", set base address from .ko
```

**Detection in kernel module:**
- `register_binfmt` / `unregister_binfmt` calls
- `vm_mmap()` or `vm_brk()` for memory allocation at fixed addresses
- Direct jump to mapped memory (entry point execution)
- S-box initialization pattern (RC4): loop 0-255, swap `S[i]` with `S[j]`

**Key insight:** The flat binary has no ELF headers, so standard tools won't recognize it. You must extract the load address from the kernel module (look for the `vm_mmap` call's address argument) and import the decrypted blob at that address in your disassembler. RC4 keys in kernel modules are often stored as immediate values in `mov` or `movabs` instructions rather than in data sections.

**References:** BSidesSF 2026 "Private Binary"

---

## Hash-Resolved Imports / No-Import Ransomware (BSidesSF 2026)

**Pattern (Ran Somewhere):** Malware binary has zero visible imports — all API calls are resolved at runtime by hashing symbol names and comparing against pre-computed hash values. The binary uses `dlopen` + a custom hash table to find libc and libcrypto functions.

**Identification:**
- `readelf -d` shows no dynamic symbols or very few (just `dlopen`/`dlsym`)
- Strings reveal no standard API names
- Disassembly shows hash computation loops followed by indirect calls
- RC4-encrypted embedded strings (RSA public key, file paths, passphrases)

**Analysis shortcut — LD_PRELOAD key extraction:**

Rather than reversing the full hash resolution and key derivation, hook the crypto functions that the malware ultimately calls:

```c
// hook_crypto.c — captures AES key used by the ransomware
#define _GNU_SOURCE
#include <dlfcn.h>
#include <openssl/evp.h>
#include <stdio.h>

int EVP_CipherInit_ex(EVP_CIPHER_CTX *ctx, const EVP_CIPHER *type,
                       ENGINE *impl, const unsigned char *key,
                       const unsigned char *iv) {
    if (key) {
        FILE *f = fopen("/tmp/aes_key.bin", "wb");
        fwrite(key, 1, 32, f);  // AES-256
        fclose(f);
        fprintf(stderr, "[HOOK] AES key captured\n");
    }
    typedef int (*orig_t)(EVP_CIPHER_CTX*, const EVP_CIPHER*, ENGINE*,
                          const unsigned char*, const unsigned char*);
    orig_t orig = (orig_t)dlsym(RTLD_NEXT, "EVP_CipherInit_ex");
    return orig(ctx, type, impl, key, iv);
}
```

```bash
# Compile and run
gcc -shared -fPIC -o hook.so hook_crypto.c -ldl
# Run in Docker container (ransomware may be destructive!)
docker run --rm -v $(pwd):/work -w /work ubuntu:22.04 \
  bash -c "LD_PRELOAD=./hook.so ./ransomware; xxd /tmp/aes_key.bin"
```

**Hash resolution patterns:**
- **SipHash variant:** Two 64-bit seeds, iterative mixing with symbol name bytes
- **DJB2/FNV variants:** Simpler hash functions with recognizable constants (`5381`, `0xcbf29ce484222325`)
- **ROR13-based:** Windows malware favorite: `hash = (hash >> 13) | (hash << 19); hash += c`

**Decryption after key capture:**
```python
from Crypto.Cipher import AES

key = open('/tmp/aes_key.bin', 'rb').read()
iv = open('/tmp/aes_iv.bin', 'rb').read()  # Also hookable
cipher = AES.new(key, AES.MODE_CBC, iv)

with open('flag.txt.enc', 'rb') as f:
    ct = f.read()
pt = cipher.decrypt(ct)
# Remove PKCS7 padding
pt = pt[:-pt[-1]]
print(pt.decode())
```

**Key insight:** When a binary resolves all imports via hashing, don't waste time reversing the hash function and building a rainbow table. Instead, let the malware resolve everything itself by running it in a sandboxed environment with `LD_PRELOAD` hooks on the functions you care about (OpenSSL crypto functions, file I/O, network calls). The AES key is deterministic across runs — if it works once, it works always.

**Safety:** Always run suspected ransomware in a Docker container or VM. Mount only copies of the encrypted files, never originals.

**References:** BSidesSF 2026 "Ran Somewhere"

---

## ELF Section Header Corruption for Anti-Analysis (BSidesSF 2026)

**Pattern (stubborn-elf):** An ELF binary has deliberately corrupted section header table entries, causing standard analysis tools (`readelf`, `objdump`, IDA, Ghidra) to crash or produce errors. However, the **program headers** (which the OS loader uses) are intact, so the binary executes normally. The flag is appended after the corrupted sections, marked with magic bytes.

```python
import sys

# Standard tools fail on corrupted section headers
# Manual parsing bypasses section headers entirely

with open("stubborn_elf", "rb") as f:
    data = f.read()

# Search for magic marker appended after ELF sections
magic = b"\xDE\xAD\xBE\xEF\xCA\xFE\xBA\xBE"
idx = data.find(magic)
if idx >= 0:
    # Data after magic is XOR-encrypted
    encrypted = data[idx + len(magic):]
    decrypted = bytes(b ^ 0x42 for b in encrypted)
    print(decrypted.decode(errors='ignore'))
```

**Key insight:** ELF execution requires **program headers** (PT_LOAD segments), NOT section headers. Section headers are metadata for debuggers and analysis tools — they're optional at runtime. Corrupting `e_shoff`, `e_shnum`, or `e_shstrndx` in the ELF header breaks tools but not execution. When tools fail, parse the binary manually or patch the ELF header to zero out section header references before loading in a disassembler.

**Recovery approach:**
```bash
# Patch section header offset to 0 (removes section table)
printf '\x00\x00\x00\x00\x00\x00\x00\x00' | dd of=binary bs=1 seek=40 conv=notrunc
# Now Ghidra/IDA can load it using program headers only

# Or use readelf -l (program headers only, ignores sections)
readelf -l stubborn_elf
```

**When to recognize:** `readelf -S` crashes or shows garbage. `file` command identifies it as ELF. `readelf -l` (lowercase L, program headers) works fine. The binary runs normally despite tool failures.

**References:** BSidesSF 2026 "stubborn-elf"

---

See also: [patterns-ctf-2.md](patterns-ctf-2.md) for Part 2 (multi-layer self-decrypting binary, embedded ZIP+XOR license, stack string deobfuscation, prefix hash brute-force, CVP/LLL lattice, decision tree obfuscation, GF(2^8) Gaussian elimination), [patterns-ctf-3.md](patterns-ctf-3.md) for Part 3 (Z3 boolean circuit, sliding window popcount, keyboard LED Morse code, C++ destructor-hidden validation, VM sequential key-chain brute-force, BWT inversion, OpenType font ligature exploitation, GLSL shader VM with self-modifying code).


# patterns

# CTF Reverse - Patterns & Techniques

## Table of Contents
- [Custom VM Reversing](#custom-vm-reversing)
  - [Analysis Steps](#analysis-steps)
  - [Common VM Patterns](#common-vm-patterns)
  - [RVA-Based Opcode Dispatching](#rva-based-opcode-dispatching)
  - [State Machine VMs (90K+ states)](#state-machine-vms-90k-states)
- [Anti-Debugging Techniques](#anti-debugging-techniques)
  - [Common Checks](#common-checks)
  - [Bypass Technique](#bypass-technique)
  - [LD_PRELOAD Hook](#ld_preload-hook)
  - [pwntools Binary Patching (Crypto-Cat)](#pwntools-binary-patching-crypto-cat)
- [Nanomites](#nanomites)
  - [Linux (Signal-Based)](#linux-signal-based)
  - [Windows (Debug Events)](#windows-debug-events)
  - [Analysis](#analysis)
- [Self-Modifying Code](#self-modifying-code)
  - [Pattern: XOR Decryption](#pattern-xor-decryption)
- [Known-Plaintext XOR (Flag Prefix)](#known-plaintext-xor-flag-prefix)
  - [Variant: XOR with Position Index](#variant-xor-with-position-index)
- [Mixed-Mode (x86-64 / x86) Stagers](#mixed-mode-x86-64--x86-stagers)
- [LLVM (Low Level Virtual Machine) Obfuscation (Control Flow Flattening)](#llvm-low-level-virtual-machine-obfuscation-control-flow-flattening)
  - [Pattern](#pattern)
  - [De-obfuscation](#de-obfuscation)
- [S-Box / Keystream Generation](#s-box--keystream-generation)
  - [Fisher-Yates Shuffle (Xorshift32)](#fisher-yates-shuffle-xorshift32)
  - [Xorshift64* Keystream](#xorshift64-keystream)
  - [Identifying Patterns](#identifying-patterns)
- [SECCOMP/BPF Filter Analysis](#seccompbpf-filter-analysis)
  - [BPF Analysis](#bpf-analysis)
- [Exception Handler Obfuscation](#exception-handler-obfuscation)
  - [RtlInstallFunctionTableCallback](#rtlinstallfunctiontablecallback)
  - [Vectored Exception Handlers (VEH)](#vectored-exception-handlers-veh)
- [Memory Dump Analysis](#memory-dump-analysis)
  - [When Binary Dumps Memory](#when-binary-dumps-memory)
  - [Known Plaintext Attack](#known-plaintext-attack)
- [Byte-Wise Uniform Transforms](#byte-wise-uniform-transforms)
- [x86-64 Gotchas](#x86-64-gotchas)
  - [Sign Extension](#sign-extension)
  - [Loop Boundary State Updates](#loop-boundary-state-updates)
- [Custom Mangle Function Reversing](#custom-mangle-function-reversing)
- [Position-Based Transformation Reversing](#position-based-transformation-reversing)
- [Hex-Encoded String Comparison](#hex-encoded-string-comparison)
- [Signal-Based Binary Exploration](#signal-based-binary-exploration)
- [Malware Anti-Analysis Bypass via Patching](#malware-anti-analysis-bypass-via-patching)
- [Multi-Stage Shellcode Loaders](#multi-stage-shellcode-loaders)
- [Timing Side-Channel Attack](#timing-side-channel-attack)
- [Multi-Thread Anti-Debug with Decoy + Signal Handler MBA (ApoorvCTF 2026)](#multi-thread-anti-debug-with-decoy--signal-handler-mba-apoorvctf-2026)
- [INT3 Patch + Coredump Brute-Force Oracle (Pwn2Win 2016)](#int3-patch--coredump-brute-force-oracle-pwn2win-2016)
- [Signal Handler Chain + LD_PRELOAD Oracle (Nuit du Hack 2016)](#signal-handler-chain--ld_preload-oracle-nuit-du-hack-2016)

---

## Custom VM Reversing

### Analysis Steps
1. Identify VM structure: registers, memory, instruction pointer
2. Reverse `executeIns`/`runvm` function for opcode meanings
3. Write a disassembler to parse bytecode
4. Decompile disassembly to understand algorithm

### Common VM Patterns
```c
switch (opcode) {
    case 1: *R[op1] *= op2; break;      // MUL
    case 2: *R[op1] -= op2; break;      // SUB
    case 3: *R[op1] = ~*R[op1]; break;  // NOT
    case 4: *R[op1] ^= mem[op2]; break; // XOR
    case 5: *R[op1] = *R[op2]; break;   // MOV
    case 7: if (R0) IP += op1; break;   // JNZ
    case 8: putc(R0); break;            // PRINT
    case 10: R0 = getc(); break;        // INPUT
}
```

### RVA-Based Opcode Dispatching
- Opcodes are RVAs pointing to handler functions
- Handler performs operation, reads next RVA, jumps
- Map all handlers by following RVA chain

### State Machine VMs (90K+ states)
```java
// BFS for valid path
var agenda = new ArrayDeque<State>();
agenda.add(new State(0, ""));
while (!agenda.isEmpty()) {
    var current = agenda.remove();
    if (current.path.length() == TARGET_LENGTH) {
        println(current.path);
        continue;
    }
    for (var transition : machine.get(current.state).entrySet()) {
        agenda.add(new State(transition.getValue(),
                            current.path + (char)transition.getKey()));
    }
}
```

**Key insight:** Custom VMs appear when the challenge bundles a bytecode blob alongside a dispatcher loop. Reverse the opcode switch table first, then write a disassembler to lift the bytecode before attempting to understand the algorithm.

---

## Anti-Debugging Techniques

### Common Checks
- `IsDebuggerPresent()` (Windows)
- `ptrace(PTRACE_TRACEME)` (Linux)
- `/proc/self/status` TracerPid
- Timing checks (`rdtsc`, `time()`)
- Registry checks (Windows)

### Bypass Technique
1. Identify `test` instructions after debug checks
2. Set breakpoint at the `test`
3. Modify register to bypass conditional

```bash
# In radare2
db 0x401234          # Break at test
dc                   # Run
dr eax=0             # Clear flag
dc                   # Continue
```

### LD_PRELOAD Hook
```c
#define _GNU_SOURCE
#include <dlfcn.h>
#include <sys/ptrace.h>

long int ptrace(enum __ptrace_request req, ...) {
    long int (*orig)(enum __ptrace_request, pid_t, void*, void*);
    orig = dlsym(RTLD_NEXT, "ptrace");
    // Log or modify behavior
    return orig(req, pid, addr, data);
}
```

Compile: `gcc -shared -fPIC -ldl hook.c -o hook.so`
Run: `LD_PRELOAD=./hook.so ./binary`

**Key insight:** Anti-debugging checks are the first obstacle in most reversing challenges. Look for `ptrace`, `IsDebuggerPresent`, or timing checks early in `main()` and patch or hook them before attempting deeper analysis.

### pwntools Binary Patching (Crypto-Cat)
Patch out anti-debug calls directly using pwntools — replaces function with `ret` instruction:
```python
from pwn import *

elf = ELF('./challenge', checksec=False)
elf.asm(elf.symbols.ptrace, 'ret')   # Replace ptrace() with immediate return
elf.save('patched')                   # Save patched binary
```

Other common patches:
```python
elf.asm(addr, 'nop')                  # NOP out an instruction
elf.asm(addr, 'xor eax, eax; ret')    # Return 0 (bypass checks)
elf.asm(addr, 'mov eax, 1; ret')      # Return 1 (force success)
```

---

## Nanomites

### Linux (Signal-Based)
- `SIGTRAP` (`int 3`) → Custom operation
- `SIGILL` (`ud2`) → Custom operation
- `SIGFPE` (`idiv 0`) → Custom operation
- `SIGSEGV` (null deref) → Custom operation

### Windows (Debug Events)
- `EXCEPTION_DEBUG_EVENT` → Main handler
- Parent modifies child via `PTRACE_POKETEXT`
- Magic markers: `0x1337BABE`, `0xDEADC0DE`

### Analysis
1. Check for `fork()` + `ptrace(PTRACE_TRACEME)`
2. Find `WaitForDebugEvent` loop
3. Map EAX values to operations
4. Log operations to reconstruct algorithm

**Key insight:** Nanomites hide the real computation inside signal/exception handlers that only fire under a debugger parent. If the binary forks and the child calls `ptrace(TRACEME)`, the parent is the real CPU -- log its POKE operations to reconstruct the algorithm.

---

## Self-Modifying Code

### Pattern: XOR Decryption
```asm
lea     rax, next_block
mov     dl, [rcx]        ; Input char
xor_loop:
    xor     [rax+rbx], dl
    inc     rbx
    cmp     rbx, BLOCK_SIZE
    jnz     xor_loop
jmp     rax              ; Execute decrypted
```

**Solution:** Known opcode at block start reveals XOR key (flag char).

**Key insight:** Self-modifying code decrypts the next block using each input character as a key. A known-good opcode at the start of each decrypted block (e.g., function prologue) reveals the correct key byte, recovering the flag one character at a time.

---

## Known-Plaintext XOR (Flag Prefix)

**Pattern:** Encrypted bytes given; flag format known (e.g., `0xL4ugh{`).

**Approach:**
1. Assume repeating XOR key.
2. Use known prefix (and any hint phrase) to recover key bytes.
3. Try small key lengths and validate printable output.

```python
enc = bytes.fromhex("...")  # ciphertext
known = b"0xL4ugh{say_yes_to_me"
for klen in range(2, 33):
    key = bytearray(klen)
    ok = True
    for i, b in enumerate(known):
        if i >= len(enc):
            break
        ki = i % klen
        v = enc[i] ^ b
        if key[ki] != 0 and key[ki] != v:
            ok = False
            break
        key[ki] = v
    if not ok:
        continue
    pt = bytes(enc[i] ^ key[i % klen] for i in range(len(enc)))
    if all(32 <= c < 127 for c in pt):
        print(klen, key, pt)
```

**Note:** Challenge hints often appear verbatim in the flag body (e.g., "say_yes_to_me").

### Variant: XOR with Position Index
**Pattern:** `cipher[i] = plain[i] ^ key[i % k] ^ i` (or `^ (i & 0xff)`).

**Symptoms:**
- Repeating-key XOR almost fits known prefix but breaks at later positions
- XOR with known prefix yields a "key" that changes by +1 per index

**Fix:** Remove index first, then recover key with known prefix.
```python
enc = bytes.fromhex("...")
known = b"0xL4ugh{say_yes_to_me"
for klen in range(2, 33):
    key = bytearray(klen)
    ok = True
    for i, b in enumerate(known):
        if i >= len(enc):
            break
        ki = i % klen
        v = (enc[i] ^ i) ^ b  # strip index XOR
        if key[ki] != 0 and key[ki] != v:
            ok = False
            break
        key[ki] = v
    if not ok:
        continue
    pt = bytes((enc[i] ^ i) ^ key[i % klen] for i in range(len(enc)))
    if all(32 <= c < 127 for c in pt):
        print(klen, key, pt)
```

---

## Mixed-Mode (x86-64 / x86) Stagers

**Pattern:** 64-bit ELF jumps into a 32-bit blob via far return (`retf`/`retfq`), often after anti-debug.

**Identification:**
- Bytes `0xCB` (retf) or `0xCA` (retf imm16), sometimes preceded by `0x48` (retfq)
- 32-bit disasm shows SSE ops (`psubb`, `pxor`, `paddb`) in a tight loop
- Computed jumps into the 32-bit region

**Gotchas:**
- `retf` pops **6 bytes**: 4-byte EIP + 2-byte CS (not 8)
- 32-bit blob may rely on inherited **XMM state** and **EFLAGS**
- Missing XMM/flags transfer when switching emulators yields wrong output

**Bypass/Emulation Tips:**
1. Create a UC_MODE_32 emulator, copy memory + GPRs, **EFLAGS**, and **XMM regs**
2. Run 32-bit block, then copy memory + regs back to 64-bit
3. If anti-debug uses `fork/ptrace` + patching, emulate parent to log POKEs and apply them in child

---

## LLVM (Low Level Virtual Machine) Obfuscation (Control Flow Flattening)

### Pattern
```c
while (1) {
    if (i == 0xA57D3848) { /* block */ }
    if (i != 0xA5AA2438) break;
    i = 0x39ABA8E6;  // Next state
}
```

### De-obfuscation
1. GDB script to break at `je` instructions
2. Log state variable values
3. Map state transitions
4. Reconstruct true control flow

**Key insight:** Control flow flattening replaces structured if/else/loops with a single dispatcher switch. The state variable is the key -- trace its values at runtime to reconstruct the original control flow graph without fighting the obfuscation statically.

---

## S-Box / Keystream Generation

### Fisher-Yates Shuffle (Xorshift32)
```python
def gen_sbox():
    sbox = list(range(256))
    state = SEED
    for i in range(255, -1, -1):
        state = ((state << 13) ^ state) & 0xffffffff
        state = ((state >> 17) ^ state) & 0xffffffff
        state = ((state << 5) ^ state) & 0xffffffff
        j = state % (i + 1) if i > 0 else 0
        sbox[i], sbox[j] = sbox[j], sbox[i]
    return sbox
```

### Xorshift64* Keystream
```python
def gen_keystream():
    ks = []
    state = SEED_64
    mul = 0x2545f4914f6cdd1d
    for _ in range(256):
        state ^= (state >> 12)
        state ^= (state << 25)
        state ^= (state >> 27)
        state = (state * mul) & 0xffffffffffffffff
        ks.append((state >> 56) & 0xff)
    return ks
```

### Identifying Patterns
- Xorshift32: shifts 13, 17, 5 (no multiplication constant)
- Xorshift64*: shifts 12, 25, 27, then multiply by `0x2545f4914f6cdd1d`
- Other common constant: `0x9e3779b97f4a7c15` (golden ratio)

**Key insight:** Recognize S-box generation by the Fisher-Yates shuffle pattern (loop counting down from 255, swap with PRNG-chosen index) and keystream generators by the xorshift constants. Once the PRNG family is identified, the algorithm is fully determined by its seed.

---

## SECCOMP/BPF Filter Analysis

```bash
seccomp-tools dump ./binary
```

### BPF Analysis
- `A = sys_number` followed by comparisons
- `mem[N] = A`, `A = mem[N]` for memory ops
- Map to constraint equations, solve with z3

```python
from z3 import *
flag = [BitVec(f'c{i}', 32) for i in range(14)]
s = Solver()
s.add(flag[0] >= 0x20, flag[0] < 0x7f)
# Add constraints from filter
if s.check() == sat:
    m = s.model()
    print(''.join(chr(m[c].as_long()) for c in flag))
```

**Key insight:** SECCOMP (Secure Computing Mode) filters encode flag validation as BPF bytecode operating on syscall arguments. Dump the filter with `seccomp-tools`, translate the comparisons and memory operations into z3 constraints, and solve for the flag without ever running the binary.

---

## Exception Handler Obfuscation

### RtlInstallFunctionTableCallback
- Dynamic exception handler registration
- Handler installs new handler, modifies code
- Use x64dbg with exception handler breaks

### Vectored Exception Handlers (VEH)
- `AddVectoredExceptionHandler` installs handler
- Handler decrypts code at exception address
- Step through, dump decrypted code

**Key insight:** Exception-handler-based obfuscation hides the real control flow inside SEH/VEH handlers that trigger on deliberate faults. Set breakpoints inside the exception handlers rather than on the faulting instructions to follow the actual execution path.

---

## Memory Dump Analysis

### When Binary Dumps Memory
- Check for `/proc/self/maps` reads
- Check for `/proc/self/mem` reads
- Heap data often appended to dump

### Known Plaintext Attack
```python
prologue = bytes([0xf3, 0x0f, 0x1e, 0xfa, 0x55, 0x48, 0x89, 0xe5])
encrypted = data[func_offset:func_offset+8]
partial_key = bytes(a ^ b for a, b in zip(encrypted, prologue))
```

**Key insight:** When a binary reads `/proc/self/mem` or `/proc/self/maps`, it is dumping its own memory -- possibly after encrypting it. Use known function prologues (`endbr64; push rbp; mov rbp, rsp`) as known plaintext to recover the XOR key from the encrypted dump.

---

## Byte-Wise Uniform Transforms

**Pattern:** Output buffer depends on each input byte independently (no cross-byte coupling).

**Detection:**
- Change one input position → only one output position changes
- Fill input with a single byte → output buffer becomes constant

**Solve:**
1. For each byte value 0..255, run the program with that byte repeated
2. Record output byte → build mapping and inverse mapping
3. Apply inverse mapping to static target bytes to recover the flag

---

## x86-64 Gotchas

### Sign Extension
```python
esi = 0xffffffc7  # NOT -57

# For XOR: low byte only
esi_xor = esi & 0xff  # 0xc7

# For addition: full 32-bit with overflow
r12 = (r13 + esi) & 0xffffffff
```

### Loop Boundary State Updates
Assembly often splits state updates across loop boundaries:
```asm
    jmp loop_middle        ; First iteration in middle!

loop_top:                   ; State for iterations 2+
    mov  r13, sbox[a & 0xf]
    ; Uses OLD 'a', not new!

loop_middle:
    ; Main computation
    inc  a
    jne  loop_top
```

**Key insight:** Decompilers often get x86-64 sign extension and loop boundary state updates wrong. Always verify decompiled output against the raw assembly for operations involving `movsx`/`cdqe`, and check whether loop variables update before or after their use in each iteration.

---

## Custom Mangle Function Reversing

**Pattern (Flag Appraisal):** Binary mangles input 2 bytes at a time with intermediate state, compares to static target.

**Approach:**
1. Extract static target bytes from `.rodata` section
2. Understand mangle: processes pairs with running state value
3. Write inverse function (process in reverse, undo each operation)
4. Feed target bytes through inverse → recovers flag

**Key insight:** When a binary mangles input in pairs with running state and compares to a static target, extract the target from `.rodata` and write the inverse function. Process the target bytes in reverse order, undoing each operation, to recover the original input.

---

## Position-Based Transformation Reversing

**Pattern (PascalCTF 2026):** Binary transforms input by adding/subtracting position index.

**Reversing:**
```python
expected = [...]  # Extract from .rodata
flag = ''
for i, b in enumerate(expected):
    if i % 2 == 0:
        flag += chr(b - i)   # Even: input = output - i
    else:
        flag += chr(b + i)   # Odd: input = output + i
```

---

## Hex-Encoded String Comparison

**Pattern (Spider's Curse):** Input converted to hex, compared against hex constant.

**Quick solve:** Extract hex constant from strings/Ghidra, decode:
```bash
echo "4d65746143..." | xxd -r -p
```

---

## Signal-Based Binary Exploration

**Pattern (Signal Signal Little Star):** Binary uses UNIX signals as a binary tree navigation mechanism.

**Identification:**
- Multiple `sigaction()` calls with `SA_SIGINFO`
- `sigaltstack()` setup (alternate signal stack)
- Handler decodes embedded payload, installs next pair of signals
- Two types: Node (installs children) vs Leaf (prints message + exits)

**Solving approach:**
1. Hook `sigaction` via `LD_PRELOAD` to log signal installations
2. DFS through the binary tree by sending signals
3. At each stage, observe which 2 signals are installed
4. Send one, check if program exits (leaf) or installs 2 more (node)
5. If wrong leaf, backtrack and try sibling

```c
// LD_PRELOAD interposer to log sigaction calls
int sigaction(int signum, const struct sigaction *act, ...) {
    if (act && (act->sa_flags & SA_SIGINFO))
        log("SET %d SA_SIGINFO=1\n", signum);
    return real_sigaction(signum, act, oldact);
}
```

---

## Malware Anti-Analysis Bypass via Patching

**Pattern (Carrot):** Malware with multiple environment checks before executing payload.

**Common checks to patch:**
| Check | Technique | Patch |
|-------|-----------|-------|
| `ptrace(PTRACE_TRACEME)` | Anti-debug | Change `cmp -1` to `cmp 0` |
| `sleep(150)` | Anti-sandbox timing | Change sleep value to 1 |
| `/proc/cpuinfo` "hypervisor" | Anti-VM | Flip `JNZ` to `JZ` |
| "VMware"/"VirtualBox" strings | Anti-VM | Flip `JNZ` to `JZ` |
| `getpwuid` username check | Environment | Flip comparison |
| `LD_PRELOAD` check | Anti-hook | Skip check |
| Fan count / hardware check | Anti-VM | Flip `JLE` to `JGE` |
| Hostname check | Environment | Flip `JNZ` to `JZ` |

**Ghidra patching workflow:**
1. Find check function, identify the conditional jump
2. Click on instruction → `Ctrl+Shift+G` → modify opcode
3. For `JNZ` (0x75) → `JZ` (0x74), or vice versa
4. For immediate values: change operand bytes directly
5. Export: press `O` → choose "Original File" format
6. `chmod +x` the patched binary

**Server-side validation bypass:**
- If patched binary sends system info to remote server, patch the data too
- Modify string addresses in data-gathering functions
- Change format strings to embed correct values directly

---

## Multi-Stage Shellcode Loaders

**Pattern (I Heard You Liked Loaders):** Nested shellcode with XOR decode loops and anti-debug.

**Debugging workflow:**
1. Break at `call rax` in launcher, step into shellcode
2. Bypass ptrace anti-debug: step to syscall, `set $rax=0`
3. Step through XOR decode loop (or break on `int3` if hidden)
4. Repeat for each stage until final payload

**Flag extraction from `mov` instructions:**
```python
# Final stage loads flag 4 bytes at a time via mov ebx, value
# Extract little-endian 4-byte chunks
values = [0x6174654d, 0x7b465443, ...]  # From disassembly
flag = b''.join(v.to_bytes(4, 'little') for v in values)
```

---

## Timing Side-Channel Attack

**Pattern (Clock Out):** Validation time varies per correct character (longer sleep on match).

**Exploitation:**
```python
import time
from pwn import *

flag = ""
for pos in range(flag_length):
    best_char, best_time = '', 0
    for c in string.printable:
        io = remote(host, port)
        start = time.time()
        io.sendline((flag + c).ljust(total_len, 'X'))
        io.recvall()
        elapsed = time.time() - start
        if elapsed > best_time:
            best_time = elapsed
            best_char = c
        io.close()
    flag += best_char
```

---

## Multi-Thread Anti-Debug with Decoy + Signal Handler MBA (ApoorvCTF 2026)

**Pattern (A Golden Experience Requiem):** Multi-threaded binary with layered anti-analysis: Thread 1 performs decoy operations (fake AES + deliberate crash via `ud2`), Thread 2 does the real flag computation in a SIGSEGV signal handler using Mixed Boolean Arithmetic (MBA), Thread 3 erases memory to prevent post-mortem analysis.

**Thread layout:**
| Thread | Purpose | Trap |
|--------|---------|------|
| Thread 1 | Decoy: AES-looking operations → `ud2` crash | Analysts waste time reversing fake crypto |
| Thread 2 | Real flag: SIGSEGV handler with MBA transforms | Hidden in signal handler, not main code path |
| Thread 3 | Memory eraser: zeros out flag data after computation | Prevents memory dumping |
| Main | rdtsc-based anti-debug timing check | Penalizes debugger-attached execution |

**Solving approach — pure Python emulation of MBA logic:**
```python
# MBA helpers (extracted from assembly)
def mba_add(a, b): return (a + b) & 0xff
def mba_xor(a, b): return (a ^ b) & 0xff

def mba_transform(i):
    """Position-dependent transform from signal handler."""
    val = (i * 7 + 0x3f) & 0xff
    rotated = ((i << 3) | (i >> 5)) & 0xff
    return mba_xor(val, rotated)

# S-box (SHA-256 initial hash values repurposed)
SBOX = [0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
        0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19]

def sbox_lookup(i):
    idx = i & 7
    shift = ((i >> 3) & 3) * 8
    return (SBOX[idx] >> shift) & 0xff

# Two interleaved rodata arrays (even indices → array1, odd → array2)
rodata1 = bytes.fromhex("39407691b717c97879013adf3a2adea11c2b04e0")
rodata2 = bytes.fromhex("bb19b025e37eaa786c4116e7aeea00c9c623940d")

flag = []
for i in range(40):  # flag length
    t = mba_transform(i)
    s = sbox_lookup(i)
    mem = rodata1[i // 2] if i % 2 == 0 else rodata2[i // 2]
    flag.append(chr(t ^ s ^ mem))

print(''.join(flag))
```

**Key insight:** The real flag logic is in the signal handler (SIGSEGV/SIGILL), not the main thread. Thread 1's AES-like code and `ud2` crash are intentional misdirection. The `rdtsc` timing check detects debuggers and corrupts output. Bypass by extracting the MBA logic from assembly and reimplementing in Python — never run the binary under a debugger.

**Detection indicators:**
- Multiple `pthread_create` calls with different handler functions
- `signal(SIGSEGV, handler)` or `sigaction` setup
- `ud2` instruction (deliberate illegal instruction)
- `rdtsc` instructions for timing checks
- SHA-256 constants (0x6a09e667...) used as lookup tables, not for hashing

---

## INT3 Patch + Coredump Brute-Force Oracle (Pwn2Win 2016)

Instead of reversing complex transformation logic, patch a byte to `0xCC` (INT3) after the transform, enable core dumps, brute-force each character by running the binary and extracting the transformed result from the coredump via `strings`.

```bash
# Patch byte at transform output point to 0xCC
printf '\xcc' | dd of=binary bs=1 seek=$((0x400ebb)) conv=notrunc
ulimit -c unlimited
# Brute-force each position:
for c in $(seq 32 126); do
    echo -ne "$(printf '\\x%02x' $c)$known_suffix" | ./binary 2>/dev/null
    strings core | grep -q "$expected" && echo "Found: $c"
done
```

**Key insight:** Use INT3/SIGTRAP as a breakpoint oracle -- the coredump captures computed state at the crash point. Avoids full reverse engineering of the transformation.

---

## Signal Handler Chain + LD_PRELOAD Oracle (Nuit du Hack 2016)

Binary uses Unix signals for flow control: `main()` sends SIGINT to itself 1024 times, each handler checks one password character, then calls `signal()` to install the next handler. Bypass: LD_PRELOAD a custom `signal()` that logs when it's called (indicating correct character), brute-force each position.

```c
// LD_PRELOAD library:
#include <signal.h>
sighandler_t signal(int sig, sighandler_t handler) {
    write(2, "CORRECT\n", 8);  // signal() called = char was correct
    return SIG_DFL;
}
```

**Key insight:** Signal-handler-chain anti-reversing can be defeated by hooking `signal()` via LD_PRELOAD. The call to `signal()` (to install the next handler) acts as a side-channel confirming the current character.


# platforms-hardware

# CTF Reverse - Hardware and Advanced Architecture Reversing

HD44780 LCD GPIO reconstruction, RISC-V advanced extensions and debugging, ARM64/AArch64 reversing and exploitation.

## Table of Contents
- [HD44780 LCD Controller GPIO Reconstruction (32C3 2015)](#hd44780-lcd-controller-gpio-reconstruction-32c3-2015)
- [RISC-V (Advanced)](#risc-v-advanced)
  - [Custom Extensions](#custom-extensions)
  - [Privileged Modes](#privileged-modes)
  - [RISC-V Debugging](#risc-v-debugging)
- [ARM64/AArch64 Reversing and Exploitation](#arm64aarch64-reversing-and-exploitation)
- [MIPS64 Cavium OCTEON Coprocessor 2 Crypto (SEC-T CTF 2017)](#mips64-cavium-octeon-coprocessor-2-crypto-sec-t-ctf-2017)
- [EFM32 ARM Microcontroller MMIO AES (SEC-T CTF 2017)](#efm32-arm-microcontroller-mmio-aes-sec-t-ctf-2017)
- [MBR/Bootloader Reversing with QEMU + GDB (Square CTF 2017)](#mbrbootloader-reversing-with-qemu--gdb-square-ctf-2017)
- [Game Boy ROM Z80 Analysis in bgb Debugger (Square CTF 2017)](#game-boy-rom-z80-analysis-in-bgb-debugger-square-ctf-2017)

---

## HD44780 LCD Controller GPIO Reconstruction (32C3 2015)

Recover text displayed on an HD44780 LCD from raw Raspberry Pi GPIO recordings:

1. **Identify signal lines:** Map GPIO pins to HD44780 signals (RS, CLK, D4-D7 for 4-bit mode)
2. **Clock edge detection:** Sample data lines on falling clock edges (1->0 transition)
3. **Nibble assembly:** Combine two 4-bit samples into one 8-bit command/data byte
4. **DRAM address mapping:** HD44780 uses non-contiguous addressing for multi-line displays:
   - Line 0: 0x00-0x27
   - Line 1: 0x40-0x67
   - Line 2: 0x14-0x3B
   - Line 3: 0x54-0x7B

```python
display = [' '] * 80  # 4 lines x 20 chars
cursor = 0

for timestamp, gpio_state in sorted(gpio_log):
    if falling_edge(gpio_state, CLK_PIN):
        nibble = extract_data_bits(gpio_state)
        byte = assemble_nibble(nibble)  # Two nibbles per byte
        if rs_high(gpio_state):  # RS=1: data write
            display[dram_to_position(cursor)] = chr(byte)
            cursor += 1
        else:  # RS=0: command (set cursor, clear, etc.)
            cursor = parse_command(byte)
```

**Key insight:** GPIO pin-to-signal mapping is rarely documented; identify CLK by finding the pin with most transitions, RS by correlation with data patterns (alternating command/data phases).

---

## RISC-V (Advanced)

Beyond basic disassembly (see [tools.md](tools.md#risc-v-binary-analysis-ehax-2026)):

### Custom Extensions

```text
Bitmanip extensions (Zbb, Zbc, Zbs):
  clz, ctz, cpop         -> count leading/trailing zeros, popcount
  orc.b, rev8            -> byte-level bit manipulation
  andn, orn, xnor        -> negated logic operations
  clmul, clmulh, clmulr  -> carry-less multiplication (crypto)
  bset, bclr, binv, bext -> single-bit operations

Crypto extensions (Zk*):
  aes32esi, aes32dsmi     -> AES round operations
  sha256sig0, sha512sum0  -> SHA hash acceleration
  sm3p0, sm4ed            -> Chinese crypto standards
```

### Privileged Modes

```text
Machine mode (M):  Highest privilege, firmware/bootloader
Supervisor mode (S): OS kernel
User mode (U):      Applications

CSR registers to watch:
  mstatus/sstatus    -> privilege level, interrupt enable
  mtvec/stvec       -> trap handler address
  mepc/sepc         -> exception return address
  mcause/scause     -> trap cause
  satp              -> page table root (virtual memory)
```

### RISC-V Debugging

```bash
# OpenOCD + GDB for hardware debugging
openocd -f interface/jlink.cfg -f target/riscv.cfg

# GDB for RISC-V
riscv64-unknown-elf-gdb binary
(gdb) target remote :3333

# QEMU with GDB server
qemu-riscv64 -g 1234 -L /usr/riscv64-linux-gnu/ ./binary
riscv64-linux-gnu-gdb -ex 'target remote :1234' ./binary
```

---

## ARM64/AArch64 Reversing and Exploitation

AArch64 (ARM 64-bit) appears in mobile apps, cloud servers (AWS Graviton), Apple Silicon, and CTF challenges. Key differences from x86-64 affect both reversing and exploitation.

**Setup and emulation:**

```bash
# Install cross-toolchain and emulator
apt install gcc-aarch64-linux-gnu gdb-multiarch qemu-user-static

# Run AArch64 binary on x86 host
qemu-aarch64-static -L /usr/aarch64-linux-gnu/ ./arm64_binary

# Debug with GDB
qemu-aarch64-static -g 12345 -L /usr/aarch64-linux-gnu/ ./arm64_binary &
gdb-multiarch -ex 'set arch aarch64' -ex 'target remote :1234' ./arm64_binary

# With library preloading (for challenges that ship libc)
qemu-aarch64-static -g 12345 -E LD_PRELOAD=./libc.so.6 -L ./lib ./arm64_binary
```

**AArch64 calling convention (key differences from x86-64):**

```text
Registers:
  x0-x7    -- function arguments AND return values (x0 = first arg / return)
  x8       -- indirect result location (struct returns)
  x9-x15   -- caller-saved temporaries
  x19-x28  -- callee-saved (preserved across calls)
  x29 (fp) -- frame pointer
  x30 (lr) -- link register (return address, NOT on stack by default)
  sp       -- stack pointer (must be 16-byte aligned)
  xzr      -- zero register (reads as 0, writes discarded)

Key exploitation differences:
  - Return address in LR (x30), not on stack -- pushed only if function calls others
  - No RIP-relative addressing like x86 -- uses ADRP+ADD pairs for PC-relative loads
  - Fixed 4-byte instruction width -- no variable-length gadget tricks
  - NOP = 0xD503201F (not 0x90)
  - BLR x8 / BR x30 -- indirect calls/jumps use register operands
```

**Common AArch64 patterns in Ghidra/IDA:**

```text
# PC-relative address loading (equivalent to x86 LEA):
ADRP  x0, #0x411000      ; Load page address (4KB aligned)
ADD   x0, x0, #0x8       ; Add page offset -> x0 = 0x411008

# Function prologue:
STP   x29, x30, [sp, #-0x30]!  ; Push fp + lr, decrement sp
MOV   x29, sp                   ; Set frame pointer

# Function epilogue:
LDP   x29, x30, [sp], #0x30    ; Pop fp + lr, increment sp
RET                              ; Branch to x30 (lr)

# Switch/jump table:
ADR   x1, jump_table
LDRB  w2, [x1, x0]       ; Load offset byte
ADD   x1, x1, w2, SXTB   ; Sign-extend and add
BR    x1                   ; Indirect branch
```

**ROP on AArch64:**

```python
from pwn import *

# AArch64 gadgets differ from x86:
# - "pop {x0}; ret" equivalent: LDP x0, x1, [sp], #0x10; RET
# - Prologue gadgets: LDP x29, x30, [sp, #0x20]; ... RET
# - system() call: x0 = pointer to "/bin/sh", BLR to system

context.arch = 'aarch64'
elf = ELF('./arm64_binary')

# Common gadget pattern in AArch64 libc:
# LDP X19, X20, [SP,#var_s10]
# LDP X29, X30, [SP+var_s0],#0x20
# RET
# Controls x19, x20, x29, x30 and advances sp by 0x20
```

**Key insight:** AArch64's fixed instruction width and register-based return address (`lr`/`x30`) make ROP gadgets more constrained than x86. Look for `LDP` (load pair) gadgets that pop multiple registers from the stack. The `STP`/`LDP` instruction pairs that save/restore callee-saved registers in function prologues/epilogues are the primary gadget source.

**When to recognize:** `file` shows "ELF 64-bit LSB ... ARM aarch64". Ghidra auto-detects but may need manual processor selection for raw binaries. Use `qemu-aarch64-static` for emulation on x86 hosts.

**Tools:** radare2 (`r2 -AA -a arm -b 64`), Ghidra (auto-detect), `aarch64-linux-gnu-objdump -d`, Unicorn Engine (`UC_ARCH_ARM64`)

**References:** Google CTF 2016 "Forced Puns", Insomni'hack 2018 "onecall"

---

## MIPS64 Cavium OCTEON Coprocessor 2 Crypto (SEC-T CTF 2017)

Cavium OCTEON network processors implement hardware AES and SHA256 via MIPS Coprocessor 2 (CP2) using `dmtc2` (move to CP2) and `dmfc2` (move from CP2) instructions. These look like ordinary register moves to a disassembler but drive the hardware crypto engine.

**Key CP2 register layout (OCTEON):**
```text
AES key registers:
  0x0104 – AES key quadword 0
  0x0105 – AES key quadword 1
  0x0106 – AES key quadword 2
  0x0107 – AES key quadword 3

SHA256 hash registers:
  0x400E–0x4012 – SHA256 intermediate hash words
  0x404F        – SHA256 control/result

dmtc2  rN, 0x0104   ; load 64 bits of AES key into CP2 register 0x104
dmtc2  rN, 0x0105   ; ...next quadword
```

**Approach:**
1. Disassemble in IDA/Ghidra — `dmtc2`/`dmfc2` with selector in 0x100-0x40FF range indicates OCTEON CP2
2. Cross-reference the Cavium OCTEON Hardware Reference Manual for register semantics
3. Trace the key loading sequence to recover the AES or HMAC key material

**Key insight:** Hardware crypto accelerators on MIPS appear as CP2 register writes (`dmtc2`/`dmfc2`). Identify the base register address and cross-reference vendor documentation.

**References:** SEC-T CTF 2017

---

## EFM32 ARM Microcontroller MMIO AES (SEC-T CTF 2017)

Silicon Labs EFM32 Cortex-M binary — a flat binary loaded at 0x1000 in Thumb mode.

**IDA setup:**
```text
Processor: ARM Little-endian (ARMv7-M)
Load address: 0x1000
Set T register = 1 (force Thumb mode decoding)
```

**AES accelerator MMIO layout (EFM32 AES peripheral at 0x400E0000):**
```text
0x400E0000 + 0x000  CTRL   – enable, decrypt mode
0x400E0000 + 0x004  CMD    – start/stop
0x400E0000 + 0x010  KEYLA  – key low word 0
0x400E0000 + 0x014  KEYLB  – key low word 1
0x400E0000 + 0x018  KEYLC  – key low word 2
0x400E0000 + 0x01C  KEYLD  – key low word 3
```

The binary loads two separate values, XORs them together, then writes the result as the AES key. Decrypt the embedded ciphertext block with the composed key in ECB mode.

```python
from Crypto.Cipher import AES

key_part_a = bytes.fromhex("...")  # extracted from IDA .data section
key_part_b = bytes.fromhex("...")  # second value
key = bytes(a ^ b for a, b in zip(key_part_a, key_part_b))

cipher = AES.new(key, AES.MODE_ECB)
plaintext = cipher.decrypt(ciphertext)
```

**Key insight:** Hardware AES accelerators on microcontrollers appear as MMIO register writes at a specific base address — cross-reference the vendor reference manual (EFM32 Reference Manual for Silicon Labs peripherals).

**References:** SEC-T CTF 2017

---

## MBR/Bootloader Reversing with QEMU + GDB (Square CTF 2017)

Boot a floppy/disk image in QEMU with the GDB stub enabled, then attach GDB for full source-level debugging of 16-bit real mode or 32-bit protected mode bootloader code.

```bash
# Boot with GDB stub on port 1234; -S pauses execution at start
qemu-system-x86_64 -fda disk.img -s -S

# In another terminal, attach GDB
gdb -ex "set architecture i8086" \
    -ex "target remote :1234" \
    -ex "break *0x7c00" \
    -ex "continue"

# Common MBR entry point is 0x7c00 (BIOS loads MBR here)
# Step through bootloader, inspect registers and memory:
(gdb) x/20i $pc
(gdb) info registers
(gdb) x/16xb 0x7c00
```

To bypass a password check: identify the conditional jump after the comparison and NOP it out in the image file, or patch the comparison to always succeed.

```bash
# Find the comparison offset in the image and patch it
python3 -c "
data = open('disk.img', 'rb').read()
# Replace JNZ (0x75) with JMP-short-always or NOP
data = data[:offset] + b'\x90\x90' + data[offset+2:]
open('disk_patched.img', 'wb').write(data)
"
```

**Key insight:** QEMU's `-s` flag exposes a GDB stub on port 1234 for full debugging of MBR/bootloader code — workflow identical to userland debugging.

**References:** Square CTF 2017

---

## Game Boy ROM Z80 Analysis in bgb Debugger (Square CTF 2017)

Game Boy ROMs use the Sharp SM83 (LR35902) CPU, a Z80/8080 hybrid. Load the ROM in the **bgb** emulator which provides GDB-like debugging: breakpoints, memory inspection, and register display.

**Key instructions for flag comparisons:**
```asm
LD   A, [HL]    ; load byte from memory pointed to by HL into A
AND  [HL]       ; A = A & *HL  — compares player byte against memory value
CP   N          ; compare A with immediate N (sets Z flag if equal)
```

When `and (hl)` or `cp (hl)` fires during input validation, the expected byte is visible at the `(hl)` address in the memory view.

**bgb workflow:**
1. Load ROM: File → Open ROM
2. Right-click disassembly → "Run to cursor" or set breakpoint (F2)
3. When comparison fires, inspect Registers panel (HL value) and Memory panel (`*HL`)
4. Note expected value, advance to next comparison position

**Key insight:** Game Boy ROMs are Z80/SM83 architecture. The bgb debugger provides GDB-like functionality; key comparisons use `(hl)`-indirect addressing so the expected value is directly visible in the memory view during the comparison.

**References:** Square CTF 2017


# platforms

# CTF Reverse - Platform-Specific Reversing

macOS/iOS, embedded/IoT firmware, kernel driver, automotive, and game engine reverse engineering.

## Table of Contents
- [macOS / iOS Reversing](#macos--ios-reversing)
  - [Mach-O Binary Format](#mach-o-binary-format)
  - [Code Signing & Entitlements](#code-signing--entitlements)
  - [Objective-C Runtime RE](#objective-c-runtime-re)
  - [Swift Binary Reversing](#swift-binary-reversing)
  - [iOS App Analysis](#ios-app-analysis)
  - [dyld / Dynamic Linking](#dyld--dynamic-linking)
- [Embedded / IoT Firmware RE](#embedded--iot-firmware-re)
  - [Firmware Extraction](#firmware-extraction)
  - [Firmware Unpacking](#firmware-unpacking)
  - [Architecture-Specific Notes](#architecture-specific-notes)
  - [RTOS Analysis](#rtos-analysis)
- [Kernel Driver Reversing](#kernel-driver-reversing)
  - [Linux Kernel Modules](#linux-kernel-modules)
  - [eBPF Programs](#ebpf-programs)
  - [Windows Kernel Drivers](#windows-kernel-drivers)
- [Game Engine Reversing](#game-engine-reversing)
  - [Unreal Engine](#unreal-engine)
  - [Unity (Beyond IL2CPP)](#unity-beyond-il2cpp)
  - [Anti-Cheat Analysis](#anti-cheat-analysis)
  - [Lua-Scripted Games](#lua-scripted-games)
- [Automotive / CAN Bus RE](#automotive--can-bus-re)

---

## macOS / iOS Reversing

### Mach-O Binary Format

```bash
# File identification
file binary                    # "Mach-O 64-bit executable arm64" or "x86_64"
otool -l binary               # Load commands (segments, dylibs, entry point)
otool -L binary               # Linked dynamic libraries

# Universal (fat) binaries — multiple architectures in one file
lipo -info universal_binary    # List architectures
lipo universal_binary -thin arm64 -output binary_arm64  # Extract one arch

# Segments and sections
otool -l binary | grep -A5 "segment\|section"
# Key segments: __TEXT (code), __DATA (globals), __LINKEDIT (symbols)
# Key sections: __text (instructions), __cstring (C strings), __objc_methname
```

**Key Mach-O concepts:**
- Load commands drive the dynamic linker (`dyld`)
- `LC_MAIN` → entry point (replaces `LC_UNIXTHREAD`)
- `LC_LOAD_DYLIB` → shared library dependencies
- `LC_CODE_SIGNATURE` → code signing blob
- `__DATA_CONST.__got` → Global Offset Table
- `__DATA.__la_symbol_ptr` → Lazy symbol pointers (like PLT)

### Code Signing & Entitlements

```bash
# Check code signature
codesign -dvvv binary
codesign --verify binary

# Extract entitlements (capability permissions)
codesign -d --entitlements - binary
# Key entitlements: com.apple.security.app-sandbox, com.apple.security.network.client

# Remove code signature (for patching)
codesign --remove-signature binary

# Re-sign (ad-hoc, for testing)
codesign -f -s - binary
```

**CTF relevance:** Patched binaries need re-signing to run on macOS. Ad-hoc signing (`-s -`) works for local testing.

### Objective-C Runtime RE

```bash
# Dump Objective-C class info
class-dump binary > classes.h
# Shows: @interface, @protocol, method signatures with types

# Runtime inspection with lldb
(lldb) expression -l objc -O -- [NSClassFromString(@"ClassName") new]
(lldb) expression -l objc -O -- [[ClassName alloc] init]

# Method swizzling detection (anti-tamper)
# Look for: method_exchangeImplementations, class_replaceMethod
```

**Objective-C in disassembly:**
```text
# objc_msgSend(receiver, selector, ...) is THE dispatch mechanism
# RDI = self (receiver), RSI = selector (char* method name)

# In Ghidra/IDA, look for:
objc_msgSend(obj, "checkPassword:", input)
# Selector strings are in __objc_methname section
# Cross-reference selectors to find implementations
```

**class-dump alternatives:**
- `dsdump` — faster, supports Swift + Objective-C
- `otool -oV binary` — dump Objective-C segments
- Ghidra: Enable "Objective-C" analyzer in Analysis Options

### Swift Binary Reversing

```bash
# Detect Swift
strings binary | grep "swift"
otool -l binary | grep "swift"   # __swift5_* sections

# Swift demangling
swift demangle 's14MyApp0A8ClassC10checkInput6resultSbSS_tF'
# → MyApp.MyAppClass.checkInput(result: String) -> Bool

# xcrun swift-demangle < mangled_names.txt
```

**Swift in disassembly:**
```text
# Swift uses value witness tables (VWT) for type operations
# Protocol witness tables (PWT) for dynamic dispatch (like vtables)

# Key runtime functions to watch:
swift_allocObject          → heap allocation
swift_release             → reference count decrement
swift_bridgeObjectRetain  → bridged (ObjC ↔ Swift) retain
swift_once                → lazy initialization (like dispatch_once)

# String layout:
# Small strings (≤15 bytes): inline in 16-byte buffer, tagged pointer
# Large strings: heap-allocated, pointer + length + flags

# Array<T>: pointer to ContiguousArrayStorage (header + elements)
# Dictionary<K,V>: hash table with open addressing
```

**Ghidra for Swift:** Enable "Swift" language module. Swift metadata sections (`__swift5_types`, `__swift5_proto`) contain type descriptors that Ghidra can parse.

### iOS App Analysis

```bash
# Extract IPA (iOS app package)
unzip app.ipa -d extracted/
ls extracted/Payload/*.app/

# Check if encrypted (App Store encryption / FairPlay DRM)
otool -l extracted/Payload/*.app/binary | grep -A4 "LC_ENCRYPTION_INFO"
# cryptid = 1 means encrypted, 0 means decrypted

# Decrypt with frida-ios-dump (requires jailbroken device)
# Or use Clutch / bfdecrypt on device
frida-ios-dump -H jailbroken_ip -p 22 "App Name"

# Analyze decrypted binary
class-dump decrypted_binary > headers.h
```

**Jailbreak detection and bypass:**
```javascript
// Common jailbreak checks:
// 1. Check for Cydia/Sileo
// 2. Check /private/var/lib/apt
// 3. fork() succeeds (sandboxed apps can't fork)
// 4. Open /etc/apt, /bin/sh with write
// 5. Check for substrate/substitute libraries

// Frida bypass:
var paths = ["/Applications/Cydia.app", "/bin/sh", "/etc/apt",
             "/private/var/lib/apt", "/usr/bin/ssh"];
Interceptor.attach(Module.findExportByName(null, "access"), {
    onEnter(args) {
        this.path = Memory.readUtf8String(args[0]);
    },
    onLeave(retval) {
        if (paths.some(p => this.path && this.path.includes(p))) {
            retval.replace(-1);  // File not found
        }
    }
});
```

### dyld / Dynamic Linking

```bash
# DYLD environment variables (for analysis, blocked in hardened runtime)
DYLD_PRINT_LIBRARIES=1 ./binary       # Print loaded dylibs
DYLD_INSERT_LIBRARIES=hook.dylib ./binary  # Inject dylib (like LD_PRELOAD)
# Note: SIP (System Integrity Protection) blocks this for system binaries

# Inspect dyld shared cache (contains all system frameworks)
dyld_shared_cache_util -list /System/Cryptexes/OS/System/Library/dyld/dyld_shared_cache_arm64e
```

---

## Embedded / IoT Firmware RE

### Firmware Extraction

```bash
# binwalk — firmware analysis and extraction
binwalk firmware.bin                        # Identify embedded filesystems, compressed data
binwalk -e firmware.bin                     # Extract all identified components
binwalk -Me firmware.bin                    # Recursive extraction (matryoshka)
binwalk --dd='.*' firmware.bin              # Extract everything raw

# Manual extraction by signature
strings firmware.bin | head -50             # Look for version strings, filesystem markers
hexdump -C firmware.bin | grep "hsqs"       # SquashFS magic
hexdump -C firmware.bin | grep "UBI#"       # UBI magic
```

**Hardware extraction methods (physical access):**
```text
UART:  Serial console — often gives root shell or bootloader access
       Tools: USB-UART adapter, baudrate detection (usually 115200)
       Identify: 4 pins (GND, TX, RX, VCC), use multimeter

JTAG:  Direct CPU debug — read/write flash, halt CPU, set breakpoints
       Tools: OpenOCD, J-Link, Bus Pirate
       Identify: 10/14/20-pin header, use JTAGulator for auto-detection

SPI Flash: Direct chip read — dump entire firmware
           Tools: flashrom, CH341A programmer
           Identify: 8-pin SOIC chip (Winbond, Macronix, etc.)

eMMC:  Embedded MMC — common in routers, phones
       Tools: eMMC reader, direct solder to test pads
```

### Firmware Unpacking

```bash
# SquashFS (most common in routers)
unsquashfs -d output/ squashfs-root.sqfs
# If custom compression: try different compressors (-comp xz|lzma|lzo|gzip)

# JFFS2
jefferson -d output/ jffs2.img

# UBI/UBIFS
ubireader_extract_images firmware.ubi
ubireader_extract_files ubifs.img

# CPIO (initramfs)
cpio -idv < initramfs.cpio

# Device tree blob
dtc -I dtb -O dts -o output.dts device_tree.dtb

# Kernel extraction
binwalk -e firmware.bin
# Look for: zImage, uImage, vmlinux
# Extract vmlinux from compressed: vmlinux-to-elf tool
```

### Architecture-Specific Notes

**ARM (most common in IoT):**
```bash
# Cross-toolchain
apt install gcc-arm-linux-gnueabihf gdb-multiarch

# QEMU emulation
qemu-arm -L /usr/arm-linux-gnueabihf/ ./arm_binary
qemu-arm -g 1234 ./arm_binary    # Start GDB server on port 1234
gdb-multiarch -ex 'target remote :1234' ./arm_binary

# ARM vs Thumb: ARM instructions are 4 bytes, Thumb are 2 bytes
# LSB of function pointer indicates mode: 0=ARM, 1=Thumb
# Ghidra: Right-click → Processor Options → ARM/Thumb mode
```

**ARM64/AArch64:** See [platforms-hardware.md](platforms-hardware.md#arm64aarch64-reversing-and-exploitation) for AArch64 calling convention, ROP gadgets, and qemu-aarch64-static emulation.

**MIPS (routers, embedded):**
```bash
# Big-endian vs little-endian — check ELF header or file command
file binary    # "MIPS, MIPS32 rel2 (MIPS-II), big-endian" or "little-endian"

# Emulation
qemu-mips -L /usr/mips-linux-gnu/ ./mips_binary         # Big-endian
qemu-mipsel -L /usr/mipsel-linux-gnu/ ./mipsel_binary   # Little-endian

# Key MIPS patterns:
# Branch delay slots — instruction AFTER branch always executes
# $gp (global pointer) — used for PIC, points to .got
# lui + addiu pair — loads 32-bit constant (upper 16 + lower 16)
```

**RISC-V:** See main [tools.md](tools.md#risc-v-binary-analysis-ehax-2026) for Capstone disassembly and [platforms-hardware.md](platforms-hardware.md#risc-v-advanced) for advanced extensions and debugging.

### RTOS Analysis

```text
FreeRTOS:
  - Tasks (like threads): xTaskCreate → function pointer + stack
  - Strings: "IDLE", "Tmr Svc", task names
  - xQueueSend/xQueueReceive → inter-task communication
  - Look for vTaskDelay() for timing, xSemaphoreTake() for sync

Zephyr:
  - k_thread_create → kernel thread creation
  - k_msgq_put/k_msgq_get → message queues
  - CONFIG_* symbols reveal kernel configuration

Bare metal (no OS):
  - Interrupt vector table at address 0x0 or 0x08000000 (STM32)
  - main loop pattern: while(1) { read_input(); process(); output(); }
  - Peripheral registers at memory-mapped addresses (check datasheet)
```

---

## Kernel Driver Reversing

### Linux Kernel Modules

```bash
# Identify kernel module
file module.ko                      # "ELF 64-bit LSB relocatable"
modinfo module.ko                   # Module info (description, author, license)

# List module symbols
nm module.ko | grep -v " U "       # Exported symbols

# Strings for quick recon
strings module.ko | grep -i "flag\|secret\|ioctl\|device"

# Find ioctl handler
# Key pattern: .unlocked_ioctl = my_ioctl_handler in file_operations struct
# In Ghidra: find struct with function pointers, identify by position

# Load in Ghidra
# Language: x86:LE:64:default
# Base address: doesn't matter for .ko (relocatable)
# Look for init_module / cleanup_module entry points
```

**Common kernel module CTF patterns:**
```c
// Device creation (creates /dev/challenge)
alloc_chrdev_region(&dev, 0, 1, "challenge");
cdev_init(&cdev, &fops);

// ioctl handler (main interface)
long my_ioctl(struct file *f, unsigned int cmd, unsigned long arg) {
    switch (cmd) {
        case CUSTOM_CMD_1: /* operation */ break;
        case CUSTOM_CMD_2: /* operation */ break;
    }
}

// copy_from_user / copy_to_user — data transfer with userspace
copy_from_user(kernel_buf, (void __user *)arg, size);
copy_to_user((void __user *)arg, kernel_buf, size);
```

**Debugging kernel modules:**
```bash
# QEMU + GDB for kernel debugging
qemu-system-x86_64 -kernel bzImage -initrd initrd.cpio -s -S \
  -append "console=ttyS0 nokaslr" -nographic

# In another terminal
gdb vmlinux
(gdb) target remote :1234
(gdb) lx-symbols           # Load module symbols (requires scripts)
(gdb) add-symbol-file module.ko 0x<loaded_address>
```

### eBPF Programs

```bash
# Dump eBPF programs from running system
bpftool prog list
bpftool prog dump xlated id <N>    # Disassemble
bpftool prog dump jited id <N>     # JIT'd machine code

# eBPF bytecode analysis
# eBPF has 11 registers (r0-r10), 64-bit
# r0 = return value, r1-r5 = arguments, r10 = frame pointer
# Instructions are 8 bytes each

# Disassemble .o file containing eBPF
llvm-objdump -d ebpf_prog.o

# Key eBPF patterns:
# bpf_map_lookup_elem → read from map
# bpf_map_update_elem → write to map
# bpf_probe_read → read kernel memory
# bpf_trace_printk → debug output
```

### Windows Kernel Drivers

```bash
# .sys files are PE format — load in IDA/Ghidra as normal PE
# Entry point: DriverEntry(PDRIVER_OBJECT, PUNICODE_STRING)

# Key patterns:
# IoCreateDevice → creates device object
# IRP_MJ_DEVICE_CONTROL → ioctl handler
# MmMapIoSpace → memory-mapped I/O
# ObReferenceObjectByHandle → get kernel object from handle
# ZwCreateFile/ZwReadFile → kernel-mode file operations
```

---

## Game Engine Reversing

### Unreal Engine

```bash
# Pak file extraction
# UnrealPakTool or quickbms with unreal_tournament_4.bms
unrealpak.exe extract GameName.pak -output extracted/

# UE4/UE5 asset formats:
# .uasset — serialized UObject (meshes, textures, blueprints)
# .umap — level/map data
# .ushaderbytecode — compiled shader
# FModel (https://fmodel.app/) — GUI asset viewer/extractor
```

**Blueprint reversing:**
```text
Blueprints compile to bytecode in .uasset files.
- UAssetGUI / FModel to browse Blueprint assets
- Kismet bytecode → visual scripting logic
- Look for: K2_SetTimer, DoOnce, Branch, Custom Events
- Flag logic often in Blueprint event graphs, not C++
```

**UE4/UE5 C++ reversing:**
```bash
# Key engine classes:
# UObject → base class for everything
# AActor → entities in the world
# UGameInstance → game state
# APlayerController → player input handling

# Reflection system — UCLASS(), UPROPERTY(), UFUNCTION() macros
# Generates metadata accessible at runtime
# In Ghidra: look for UClass::StaticClass() calls → type identification

# String handling: FString (UTF-16), FName (hashed identifier), FText (localized)
# In memory: FString = {TCHAR* Data, int32 ArrayNum, int32 ArrayMax}
```

### Unity (Beyond IL2CPP)

See [languages.md](languages.md#unity-il2cpp-games) for IL2CPP basics.

**Mono-based Unity (not IL2CPP):**
```bash
# Managed assemblies in Data/Managed/ directory
# Assembly-CSharp.dll contains game logic
dnspy Assembly-CSharp.dll       # Full decompilation + debugging
ilspy Assembly-CSharp.dll       # Decompilation only

# Common Unity patterns:
# MonoBehaviour.Start() → initialization
# MonoBehaviour.Update() → per-frame logic
# PlayerPrefs.GetString("key") → stored data
# SceneManager.LoadScene("level") → scene transitions
```

**Unity asset extraction:**
```bash
# AssetStudio — extract textures, models, audio, scripts
# AssetRipper — comprehensive Unity asset extraction
# UABE (Unity Asset Bundle Extractor) — low-level asset editing

# Search for flags in:
# - Text assets (.txt, .json)
# - TextMesh / UI Text components
# - Shader source code
# - ScriptableObject assets
# - PlayerPrefs save files
```

### Anti-Cheat Analysis

```text
For CTF challenges involving game anti-cheat:

EasyAntiCheat (EAC):
- Kernel driver (EasyAntiCheat_EOS.sys)
- User-mode module injected into game
- Integrity checks on game memory
- Bypass: kernel-level memory R/W (for research only)

BattlEye:
- BEService.exe → BEClient.dll injected
- Communication via encrypted channel
- Screenshot capture, process scanning
- Module: BEClient2.dll

Valve Anti-Cheat (VAC):
- User-mode only (no kernel driver)
- Module hashing, memory scanning
- Network-based detection (server-side)
- Delayed bans (not immediate)

CTF approach:
1. Identify which anti-cheat (strings, loaded modules)
2. For CTF: usually need to bypass specific check, not full anti-cheat
3. Memory patching: find game state in memory, modify values
4. Save file manipulation: often easier than runtime cheating
```

### Lua-Scripted Games

```bash
# Many games embed Lua for scripting
# Look for: lua51.dll, luajit.dll, .lua files in assets

# Luac bytecode decompilation
luadec bytecode.luac > decompiled.lua      # Lua 5.1-5.3
unluac bytecode.luac > decompiled.lua      # Alternative

# LuaJIT bytecode
luajit -bl bytecode.lua                     # Disassemble
# ljd (LuaJIT decompiler): python3 ljd bytecode.lua

# Embedded Lua: strings binary | grep "lua_\|luaL_\|LUA_"
# Hook lua_pcall to intercept script execution
```

---

## Automotive / CAN Bus RE

```bash
# CAN bus interface setup
sudo ip link set can0 type can bitrate 500000
sudo ip link set up can0

# Capture CAN traffic
candump can0                               # Live capture
candump -l can0                            # Log to file
cansniffer can0                            # Filter/highlight changes

# Replay CAN messages
canplayer -I logfile.log can0
cansend can0 7DF#0201000000000000          # Send single frame (OBD-II request)

# UDS (Unified Diagnostic Services) — common in automotive CTF
# Service 0x27: Security Access (seed-key authentication)
# Service 0x2E: Write Data By Identifier
# Service 0x31: Routine Control

# Decode CAN frames
# ID: 11-bit or 29-bit identifier
# DLC: Data Length Code (0-8 bytes)
# Data: up to 8 bytes payload
```

**CTF automotive patterns:**
- Seed-key bypass: Reverse the key derivation algorithm from ECU firmware
- CAN message replay: Capture legitimate command, replay to unlock feature
- Firmware extraction from ECU via UDS/KWP2000


# tools-advanced

# CTF Reverse - Advanced Tools & Deobfuscation

Advanced tooling for commercial packers/protectors, binary diffing, deobfuscation frameworks, emulation, and symbolic execution beyond angr.

## Table of Contents
- [VMProtect Analysis](#vmprotect-analysis)
  - [Recognition](#recognition)
  - [Approach](#approach)
  - [Tools](#tools)
  - [CTF Strategy](#ctf-strategy)
- [Themida / WinLicense Analysis](#themida--winlicense-analysis)
  - [Themida Recognition](#themida-recognition)
  - [Approach for CTF](#approach-for-ctf)
- [Binary Diffing](#binary-diffing)
  - [BinDiff](#bindiff)
  - [Diaphora](#diaphora)
- [Deobfuscation Frameworks](#deobfuscation-frameworks)
  - [D-810 (IDA)](#d-810-ida)
  - [GOOMBA (Ghidra)](#goomba-ghidra)
  - [Miasm](#miasm)
- [Qiling Framework (Emulation)](#qiling-framework-emulation)
- [Triton (Dynamic Symbolic Execution)](#triton-dynamic-symbolic-execution)
- [Manticore (Symbolic Execution)](#manticore-symbolic-execution)
- [Rizin / Cutter](#rizin--cutter)
- [RetDec (Retargetable Decompiler)](#retdec-retargetable-decompiler)
- [Custom VM Bytecode Lifting to LLVM IR (Google CTF 2017)](#custom-vm-bytecode-lifting-to-llvm-ir-google-ctf-2017)
- [Advanced GDB Techniques](#advanced-gdb-techniques)
  - [Python Scripting](#python-scripting)
  - [Brute-Force with GDB Script](#brute-force-with-gdb-script)
  - [Conditional Breakpoints](#conditional-breakpoints)
  - [Watchpoints](#watchpoints)
  - [Reverse Debugging (rr)](#reverse-debugging-rr)
  - [GDB Dashboard / GEF / pwndbg](#gdb-dashboard--gef--pwndbg)
- [Advanced Ghidra Scripting](#advanced-ghidra-scripting)
- [Patching Strategies](#patching-strategies)
  - [Binary Ninja Patching (Python API)](#binary-ninja-patching-python-api)
  - [LIEF (Library for Instrumenting Executable Formats)](#lief-library-for-instrumenting-executable-formats)
- [GDB Constraint Extraction with ILP/LP Solver (BackdoorCTF 2017)](#gdb-constraint-extraction-with-ilplp-solver-backdoorctf-2017)
- [GDB Position-Encoded Input with Zero Flag Monitoring (EKOPARTY 2017)](#gdb-position-encoded-input-with-zero-flag-monitoring-ekoparty-2017)
- [LD_PRELOAD to Dump Execute-Only Binary (BackdoorCTF 2017)](#ld_preload-to-dump-execute-only-binary-backdoorctf-2017)

---

## VMProtect Analysis

VMProtect virtualizes x86/x64 code into custom bytecode interpreted by a generated VM. One of the most challenging protectors in CTF.

### Recognition

```bash
# VMProtect signatures
strings binary | grep -i "vmp\|vmprotect"
# PE sections: .vmp0, .vmp1 (VMProtect adds its own sections)
readelf -S binary | grep ".vmp"
# Large binary with entropy > 7.5 in certain sections
```

**Key indicators:**
- `push` / `pop` heavy prologues (VM entry pushes all registers to stack)
- Large switch-case dispatcher (the VM handler loop)
- Anti-debug checks embedded in VM handlers
- Mutation engine: same opcode has different handlers per build

### Approach

```text
1. Identify VM entry points — look for pushad/pushaq-like sequences
2. Find the handler table — large indirect jump (jmp [reg + offset])
3. Trace handler execution — each handler ends with jump to next
4. Identify handlers:
   - vAdd, vSub, vMul, vXor, vNot (arithmetic)
   - vPush, vPop (stack operations)
   - vLoad, vStore (memory access)
   - vJmp, vJcc (control flow)
   - vRet (VM exit — restores real registers)
5. Build disassembler for VM bytecode
6. Simplify / deobfuscate the lifted IL
```

### Tools

- **VMPAttack** (IDA plugin): Automatically identifies VM handlers
- **NoVmp**: Devirtualization via VTIL (open-source)
- **VMProtect devirtualizer scripts**: Community IDA/Binary Ninja scripts
- **Approach for CTF:** Often easier to trace specific operations (crypto, comparisons) than fully devirtualize

### CTF Strategy

```python
# Trace VM execution dynamically to extract operations on flag
# Hook VM handler dispatch to log opcode + operands

import frida

script = """
var vm_dispatch = ptr('0x...');  // Address of handler table jump
Interceptor.attach(vm_dispatch, {
    onEnter(args) {
        // Log handler index and stack state
        var handler_idx = this.context.rax;  // or whichever register
        console.log('Handler:', handler_idx, 'RSP:', this.context.rsp);
    }
});
"""
```

**Key insight:** Full devirtualization is rarely needed for CTF. Focus on tracing what operations are performed on your input. Hook comparison/crypto functions called from within the VM.

---

## Themida / WinLicense Analysis

Similar to VMProtect but with additional anti-debug layers.

### Themida Recognition
- Sections: `.themida`, `.winlice`
- Extremely heavy anti-debug (kernel-level checks, driver installation)
- Code mutation + virtualization + packing combined

### Approach for CTF
1. **Dump unpacked code:** Let it run, dump process memory after unpacking
2. **Bypass anti-debug:** ScyllaHide in x64dbg with Themida-specific preset
3. **Fix imports:** Use Scylla plugin for IAT reconstruction
4. **Focus on dumped code:** Once unpacked, analyze as normal binary

```bash
# x64dbg workflow for Themida:
1. Load binary
2. Enable ScyllaHide → Profile: Themida
3. Run to OEP (Original Entry Point) — may need several attempts
4. Dump with Scylla: OEP → IAT Autosearch → Get Imports → Dump
5. Fix dump: Scylla → Fix Dump
6. Analyze fixed dump in Ghidra/IDA
```

---

## Binary Diffing

Critical for patch analysis, 1-day exploit development, and CTF challenges that provide two versions of a binary.

### BinDiff

```bash
# Export from IDA/Ghidra first, then diff
# IDA: File → BinExport → Export as BinExport2
# Ghidra: Use BinExport plugin

# Command line diffing
bindiff primary.BinExport secondary.BinExport
# Opens in BinDiff GUI — shows matched/unmatched functions
```

**Key metrics:**
- Similarity score (0.0-1.0) per function pair
- Changed instructions highlighted
- Unmatched functions = new/removed code

### Diaphora

Free, open-source alternative to BinDiff, runs as IDA plugin.

```bash
# In IDA:
# File → Script file → diaphora.py
# Export first binary, then open second and diff

# Ghidra version: diaphora_ghidra.py
```

**Useful for CTF:** When challenge provides "patched" and "original" binaries, diff reveals the vulnerability or hidden functionality.

---

## Deobfuscation Frameworks

### D-810 (IDA)

Pattern-based deobfuscation plugin for IDA Pro. Excellent for OLLVM-obfuscated binaries.

```text
Capabilities:
- MBA simplification: (a ^ b) + 2*(a & b) → a + b
- Dead code elimination
- Opaque predicate removal
- Constant folding
- Control flow unflattening (partial)

Installation: Copy to IDA plugins directory
Usage: Edit → Plugins → D-810 → Select rules → Apply
```

### GOOMBA (Ghidra)

```text
GOOMBA (Ghidra-based Obfuscated Object Matching and Bytes Analysis):
- Integrates with Ghidra's P-Code
- Simplifies MBA expressions
- Pattern matching for known obfuscation

Installation: Copy .jar to Ghidra extensions
Usage: Code Browser → Analysis → GOOMBA
```

### Miasm

Powerful reverse engineering framework with symbolic execution and IR lifting.

```python
from miasm.analysis.binary import Container
from miasm.analysis.machine import Machine
from miasm.expression.expression import *

# Load binary and lift to Miasm IR
cont = Container.from_stream(open("binary", "rb"))
machine = Machine(cont.arch)
mdis = machine.dis_engine(cont.bin_stream, loc_db=cont.loc_db)

# Disassemble function
asmcfg = mdis.dis_multiblock(entry_addr)

# Lift to IR
lifter = machine.lifter_model_call(loc_db=cont.loc_db)
ircfg = lifter.new_ircfg_from_asmcfg(asmcfg)

# Symbolic execution
from miasm.ir.symbexec import SymbolicExecutionEngine
sb = SymbolicExecutionEngine(lifter)
# Execute symbolically, then simplify expressions
```

**Use case:** Deobfuscate expression trees, simplify complex arithmetic, trace data flow through obfuscated code.

---

## Qiling Framework (Emulation)

Cross-platform emulation framework built on Unicorn, with OS-level support (syscalls, filesystem, registry).

```python
from qiling import Qiling
from qiling.const import QL_VERBOSE

# Emulate Linux ELF
ql = Qiling(["./binary"], "rootfs/x8664_linux",
            verbose=QL_VERBOSE.DEBUG)

# Hook specific address
@ql.hook_address
def hook_check(ql, address, size):
    if address == 0x401234:
        ql.arch.regs.rax = 0  # Bypass check
        ql.log.info("Anti-debug bypassed")

# Hook syscall
@ql.hook_syscall(name="ptrace")
def hook_ptrace(ql, request, pid, addr, data):
    return 0  # Always succeed

# Hook API (Windows)
@ql.set_api("IsDebuggerPresent", target=ql.os.user_defined_api)
def hook_isdebug(ql, address, params):
    return 0

ql.run()
```

**Advantages over Unicorn:**
- OS emulation (file I/O, network, registry)
- Multi-platform (Linux, Windows, macOS, Android, UEFI)
- Built-in debugger interface
- Rootfs for library loading

**CTF use cases:**
- Emulate binaries for foreign architectures (ARM, MIPS, RISC-V)
- Bypass all anti-debug at once (no debugger artifacts)
- Fuzz embedded/IoT firmware without hardware
- Trace execution without code modification

---

## Triton (Dynamic Symbolic Execution)

Pin-based dynamic binary analysis framework with symbolic execution, taint analysis, and AST simplification.

```python
from triton import *

ctx = TritonContext(ARCH.X86_64)

# Load binary sections
with open("binary", "rb") as f:
    binary = f.read()
ctx.setConcreteMemoryAreaValue(0x400000, binary)

# Symbolize input
for i in range(32):
    ctx.symbolizeMemory(MemoryAccess(INPUT_ADDR + i, CPUSIZE.BYTE), f"input_{i}")

# Emulate instructions
pc = ENTRY_POINT
while pc:
    inst = Instruction(pc, ctx.getConcreteMemoryAreaValue(pc, 16))
    ctx.processing(inst)

    # At comparison point, extract path constraint
    if pc == CMP_ADDR:
        ast = ctx.getPathConstraintsAst()
        model = ctx.getModel(ast)
        for k, v in sorted(model.items()):
            print(f"input[{k}] = {chr(v.getValue())}", end="")
        break

    pc = ctx.getConcreteRegisterValue(ctx.registers.rip)
```

**Triton vs angr:**
| Feature | Triton | angr |
|---|---|---|
| Execution | Concrete + symbolic (DSE) | Fully symbolic |
| Speed | Faster (concrete-driven) | Slower (explores all paths) |
| Path explosion | Less prone (follows one path) | Major issue |
| API | C++ / Python | Python |
| Best for | Single-path deobfuscation, taint tracking | Multi-path exploration |

**Key use:** Triton excels at deobfuscation — run the program concretely, but track symbolic state, then simplify the collected constraints.

---

## Manticore (Symbolic Execution)

Trail of Bits' symbolic execution tool. Similar to angr but with native EVM (Ethereum) support.

```python
from manticore.native import Manticore

m = Manticore("./binary")

# Hook success/failure
@m.hook(0x401234)
def success(state):
    buf = state.solve_one_n_batched(state.input_symbols, 32)
    print("Flag:", bytes(buf))
    m.kill()

@m.hook(0x401256)
def fail(state):
    state.abandon()

m.run()
```

**Best for:** EVM/smart contract analysis, simpler Linux binaries. angr is generally more mature for complex RE tasks.

---

## Rizin / Cutter

Rizin is the maintained fork of radare2. Cutter is its Qt-based GUI.

```bash
# Rizin CLI (r2-compatible commands)
rizin -d ./binary
> aaa                    # Analyze all
> afl                    # List functions
> pdf @ main             # Print disassembly
> VV                     # Visual graph mode

# Cutter GUI
cutter binary           # Open in GUI with decompiler
```

**Cutter advantages:**
- Built-in Ghidra decompiler (via r2ghidra plugin)
- Graph view, hex editor, debug panel in one GUI
- Integrated Python/JavaScript scripting console
- Free and open source

---

## RetDec (Retargetable Decompiler)

LLVM-based decompiler supporting many architectures. Free and open-source.

```bash
# Install
pip install retdec-decompiler
# Or use web: https://retdec.com/decompilation/

# CLI
retdec-decompiler binary
# Outputs: binary.c (decompiled C), binary.dsm (disassembly)

# Specific function
retdec-decompiler --select-ranges 0x401000-0x401100 binary
```

**Strengths:** Multi-arch support (x86, ARM, MIPS, PowerPC, PIC32), free, produces compilable C. Good for architectures not well-supported by Ghidra.

---

## Custom VM Bytecode Lifting to LLVM IR (Google CTF 2017)

For complex custom VMs, transpile the VM bytecode to LLVM IR and use LLVM's optimization passes to simplify the code, then decompile the optimized IR.

```python
# Pipeline: VM bytecode → custom disassembler → LLVM IR → optimize → decompile
# 1. Write disassembler for the custom VM opcodes
# 2. Emit LLVM IR for each opcode:
#    INC reg  → %reg = add i32 %reg, 1
#    CDEC reg → conditional decrement
#    CALL fn  → call void @fn()
# 3. Use MCJIT or llc to optimize:
#    opt -O3 -S vm_lifted.ll -o vm_optimized.ll
# 4. Load optimized IR in IDA or decompile with RetDec
# Result: 1300 lines → 150 lines after inlining + constant folding
```

**Key insight:** LLVM's optimization passes (inlining, constant folding, dead code elimination) dramatically simplify lifted VM bytecode. A custom VM with 26 registers and 3 opcodes that produces 1300 lines of IL reduces to ~150 lines after `-O3`, revealing the underlying algorithm (e.g., Collatz sequence computation).

---

## Advanced GDB Techniques

### Python Scripting

```python
# ~/.gdbinit or source from GDB
import gdb

class TraceCompare(gdb.Breakpoint):
    """Log all comparison operations."""
    def __init__(self, addr):
        super().__init__(f"*{addr}", gdb.BP_BREAKPOINT)

    def stop(self):
        frame = gdb.selected_frame()
        rdi = int(frame.read_register("rdi"))
        rsi = int(frame.read_register("rsi"))
        rdx = int(frame.read_register("rdx"))
        # Read compared buffers
        inferior = gdb.selected_inferior()
        buf1 = inferior.read_memory(rdi, rdx).tobytes()
        buf2 = inferior.read_memory(rsi, rdx).tobytes()
        print(f"memcmp({buf1!r}, {buf2!r}, {rdx})")
        return False  # Don't stop, just log

# Usage in GDB:
# (gdb) source trace_cmp.py
# (gdb) python TraceCompare(0x401234)
```

### Brute-Force with GDB Script

```python
# Byte-by-byte brute force via GDB Python API
import gdb, string

def bruteforce_flag(check_addr, success_addr, fail_addr, flag_len):
    flag = []
    for pos in range(flag_len):
        for ch in string.printable:
            candidate = ''.join(flag) + ch + 'A' * (flag_len - pos - 1)
            gdb.execute('start', to_string=True)
            gdb.execute(f'b *{check_addr}', to_string=True)
            # Write candidate to stdin pipe
            # ... (setup input)
            gdb.execute('continue', to_string=True)
            rip = int(gdb.parse_and_eval('$rip'))
            if rip == success_addr:
                flag.append(ch)
                break
        gdb.execute('delete breakpoints', to_string=True)
    return ''.join(flag)
```

### Conditional Breakpoints

```bash
# Break only when register has specific value
(gdb) b *0x401234 if $rax == 0x41
(gdb) b *0x401234 if *(char*)$rdi == 'f'

# Break on Nth hit
(gdb) b *0x401234
(gdb) ignore 1 99    # Skip first 99 hits, break on 100th

# Log without stopping
(gdb) b *0x401234
(gdb) commands
> silent
> printf "rax=%lx rdi=%lx\n", $rax, $rdi
> continue
> end
```

### Watchpoints

```bash
# Hardware watchpoint — break when memory changes
(gdb) watch *(int*)0x601050        # Break on write to address
(gdb) rwatch *(int*)0x601050       # Break on read
(gdb) awatch *(int*)0x601050       # Break on read or write

# Watch a variable by name (needs debug symbols)
(gdb) watch flag_buffer[0]

# Conditional watchpoint
(gdb) watch *(int*)0x601050 if *(int*)0x601050 == 0x42
```

### Reverse Debugging (rr)

```bash
# Record execution
rr record ./binary
# Replay with reverse execution support
rr replay

# In rr replay (GDB commands plus):
(gdb) reverse-continue     # Run backward to previous breakpoint
(gdb) reverse-stepi        # Step backward one instruction
(gdb) reverse-next         # Reverse next
(gdb) when                 # Show current event number

# Set checkpoint and return to it
(gdb) checkpoint
(gdb) restart 1           # Return to checkpoint 1
```

**Key use:** When you step past the critical moment, reverse back instead of restarting. Invaluable for anti-debug that corrupts state.

### GDB Dashboard / GEF / pwndbg

```bash
# pwndbg (most popular for CTF)
# https://github.com/pwndbg/pwndbg
git clone https://github.com/pwndbg/pwndbg && cd pwndbg && ./setup.sh

# Key pwndbg commands:
pwndbg> context           # Show registers, stack, code, backtrace
pwndbg> vmmap             # Memory map (like /proc/self/maps)
pwndbg> search -s "flag{" # Search memory for string
pwndbg> telescope $rsp 20 # Smart stack dump
pwndbg> cyclic 200        # Generate De Bruijn pattern
pwndbg> hexdump $rdi 64   # Pretty hex dump
pwndbg> got               # Show GOT entries
pwndbg> plt               # Show PLT entries

# GEF (alternative)
# https://github.com/hugsy/gef
bash -c "$(curl -fsSL https://gef.blah.cat/sh)"

# Key GEF commands:
gef> xinfo $rdi           # Detailed info about address
gef> checksec             # Binary security features
gef> heap chunks          # Heap chunk listing
gef> pattern create 100   # De Bruijn pattern
```

---

## Advanced Ghidra Scripting

```python
# Ghidra Python (Jython) — run via Script Manager or headless

# Batch rename functions matching a pattern
from ghidra.program.model.symbol import SourceType
fm = currentProgram.getFunctionManager()
for func in fm.getFunctions(True):
    if func.getName().startswith("FUN_"):
        # Check if function contains specific instruction pattern
        body = func.getBody()
        inst_iter = currentProgram.getListing().getInstructions(body, True)
        for inst in inst_iter:
            if inst.getMnemonicString() == "CPUID":
                func.setName("anti_vm_check_" + hex(func.getEntryPoint().getOffset()),
                            SourceType.USER_DEFINED)
                break

# Extract all XOR constants from a function
def extract_xor_constants(func):
    """Find all XOR operations and their immediate operands."""
    constants = []
    body = func.getBody()
    inst_iter = currentProgram.getListing().getInstructions(body, True)
    for inst in inst_iter:
        if inst.getMnemonicString() == "XOR":
            for i in range(inst.getNumOperands()):
                op = inst.getOpObjects(i)
                if op and hasattr(op[0], 'getValue'):
                    constants.append(int(op[0].getValue()))
    return constants

# Bulk decompile and search for pattern
from ghidra.app.decompiler import DecompInterface
decomp = DecompInterface()
decomp.openProgram(currentProgram)

for func in fm.getFunctions(True):
    result = decomp.decompileFunction(func, 30, monitor)
    if result.depiledFunction():
        code = result.getDecompiledFunction().getC()
        if "strcmp" in code or "memcmp" in code:
            print(f"Comparison in {func.getName()} at {func.getEntryPoint()}")
```

---

## Patching Strategies

### Binary Ninja Patching (Python API)

```python
import binaryninja as bn

bv = bn.open_view("binary")

# NOP out instruction
bv.write(0x401234, b"\x90" * 5)  # 5-byte NOP

# Patch conditional jump (JNZ → JZ)
bv.write(0x401234, b"\x74")  # 0x75 (JNZ) → 0x74 (JZ)

# Insert always-true (mov eax, 1; ret)
bv.write(0x401234, b"\xb8\x01\x00\x00\x00\xc3")

bv.save("patched")
```

### LIEF (Library for Instrumenting Executable Formats)

```python
import lief

# Parse and modify ELF/PE/Mach-O
binary = lief.parse("binary")

# Add a new section
section = lief.ELF.Section(".patch")
section.content = list(b"\xcc" * 0x100)
section.type = lief.ELF.SECTION_TYPES.PROGBITS
section.flags = lief.ELF.SECTION_FLAGS.EXECINSTR | lief.ELF.SECTION_FLAGS.ALLOC
binary.add(section)

# Modify entry point
binary.header.entrypoint = 0x401000

# Hook imported function
binary.patch_pltgot("strcmp", 0x401000)

binary.write("patched")
```

**LIEF advantages:** Cross-format (ELF, PE, Mach-O), Python API, can add sections/segments, modify headers, patch imports.

---

## GDB Constraint Extraction with ILP/LP Solver (BackdoorCTF 2017)

When a binary enforces linear arithmetic relationships between input bytes, extract constraints automatically via GDB and solve with an ILP solver.

**Technique:** Send position-encoded input (`input[i] = i`) so that when a comparison fires, you know exactly which positions are involved and what their sum/difference must equal. Collect all constraints from logged comparisons, then feed to PuLP or Gurobi.

```python
from pulp import *

n = 32  # flag length
prob = LpProblem("crackme", LpMinimize)
x = [LpVariable(f'x{i}', 32, 126, cat='Integer') for i in range(n)]
prob += 0  # dummy objective

# Constraints extracted via GDB automation (input[i]=i, monitor comparisons):
prob += x[3] + x[7] == 0xAB
prob += x[1] - x[5] == 0x0C
# ... add all extracted constraints ...

# Constrain to printable ASCII
for xi in x:
    prob += xi >= 32
    prob += xi <= 126

prob.solve(PULP_CBC_CMD(msg=0))
flag = ''.join(chr(int(value(xi))) for xi in x)
print("Flag:", flag)
```

**GDB automation to extract constraints:**
```python
# In GDB Python: set input[i]=i, run, log every CMP instruction result
import gdb

class CmpLogger(gdb.Breakpoint):
    def stop(self):
        frame = gdb.selected_frame()
        # Read compared values, map back to input indices via position encoding
        return False
```

**Key insight:** When a binary enforces linear arithmetic relationships between input bytes, ILP solvers directly find the satisfying assignment once constraints are extracted via GDB automation.

**References:** BackdoorCTF 2017

---

## GDB Position-Encoded Input with Zero Flag Monitoring (EKOPARTY 2017)

Send input where `input[i] = i` (position-encoded). Single-step through the binary monitoring the CPU zero flag (ZF). When ZF is set at a comparison involving a specific position's value, the comparison matched — log the expected value for that position.

```python
import gdb

# Script: single-step binary with position-encoded input, watch ZF
class ZFMonitor(gdb.Breakpoint):
    def stop(self):
        zf = (int(gdb.parse_and_eval('$eflags')) >> 6) & 1
        if zf:
            rip = int(gdb.parse_and_eval('$rip'))
            # Disassemble at rip to find the compared immediate
            disasm = gdb.execute(f'x/1i {rip-5}', to_string=True)
            print(f"ZF set at {rip:#x}: {disasm.strip()}")
        return False

# Run once with input b'\x00\x01\x02\x03...\x1f'
# ZF fires when comparison matches the position's own value -> that IS the key byte
```

Maps each input byte to its required value in one pass without manual reversing.

**Key insight:** Position-encoded input (`input[i]=i`) combined with zero flag monitoring reveals the full key/password in one pass — the zero flag fires when the expected value for position i equals i itself.

**References:** EKOPARTY CTF 2017

---

## LD_PRELOAD to Dump Execute-Only Binary (BackdoorCTF 2017)

A binary has execute-only permissions (mode `--x`, no read bit). The file cannot be read directly or with standard tools, but the kernel still maps it into memory on execution.

LD_PRELOAD a shared library with a constructor that runs inside the process and reads its own memory via `/proc/self/mem`:

```c
// dump_xo.c — compile: gcc -shared -fPIC -o dump_xo.so dump_xo.c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

__attribute__((constructor)) void dump() {
    FILE *maps = fopen("/proc/self/maps", "r");
    char line[256];
    unsigned long base = 0, end = 0;

    // Find the execute-only binary's mapping (r-xp or --xp)
    while (fgets(line, sizeof(line), maps)) {
        if (strstr(line, "binary_name")) {
            sscanf(line, "%lx-%lx", &base, &end);
            break;
        }
    }
    fclose(maps);

    FILE *mem = fopen("/proc/self/mem", "rb");
    fseek(mem, base, SEEK_SET);
    size_t size = end - base;
    void *buf = malloc(size);
    fread(buf, 1, size, mem);
    fclose(mem);

    FILE *out = fopen("/tmp/dumped_binary", "wb");
    fwrite(buf, 1, size, out);
    fclose(out);
}
// Usage: LD_PRELOAD=./dump_xo.so ./binary_xo
```

**Key insight:** Execute-only prevents file reading but not execution. LD_PRELOAD constructors run inside the process where `/proc/self/mem` provides access to mapped memory regardless of file permissions.

**References:** BackdoorCTF 2017


# tools-dynamic

# CTF Reverse - Dynamic Analysis Tools

## Table of Contents
- [Frida (Dynamic Instrumentation)](#frida-dynamic-instrumentation)
  - [Installation](#installation)
  - [Basic Function Hooking](#basic-function-hooking)
  - [Anti-Debug Bypass](#anti-debug-bypass)
  - [Memory Scanning and Patching](#memory-scanning-and-patching)
  - [Function Replacement](#function-replacement)
  - [Tracing and Stalker](#tracing-and-stalker)
  - [r2frida (Radare2 + Frida Integration)](#r2frida-radare2--frida-integration)
  - [Frida for Android/iOS](#frida-for-androidios)
- [angr (Symbolic Execution)](#angr-symbolic-execution)
  - [angr Installation](#angr-installation)
  - [Basic Path Exploration](#basic-path-exploration)
  - [Symbolic Input with Constraints](#symbolic-input-with-constraints)
  - [Hook Functions to Simplify Analysis](#hook-functions-to-simplify-analysis)
  - [Exploring from Specific Address](#exploring-from-specific-address)
  - [Common Patterns and Tips](#common-patterns-and-tips)
  - [Dealing with Path Explosion](#dealing-with-path-explosion)
  - [angr CFG Recovery](#angr-cfg-recovery)
- [lldb (LLVM Debugger)](#lldb-llvm-debugger)
  - [Basic Commands](#basic-commands)
  - [Scripting (Python)](#scripting-python)
- [x64dbg (Windows Debugger)](#x64dbg-windows-debugger)
  - [Key Features](#key-features)
  - [Scripting](#scripting)
  - [Common CTF Workflow](#common-ctf-workflow)
- [Qiling Framework (Cross-Platform Emulation)](#qiling-framework-cross-platform-emulation)
  - [Qiling Installation](#qiling-installation)
  - [Basic Usage](#basic-usage)
  - [Anti-Debug Bypass via Emulation](#anti-debug-bypass-via-emulation)
  - [Input Fuzzing with Qiling](#input-fuzzing-with-qiling)
- [Triton (Dynamic Symbolic Execution)](#triton-dynamic-symbolic-execution)
- [Intel Pin Instruction-Counting Side Channel (Hackover CTF 2015)](#intel-pin-instruction-counting-side-channel-hackover-ctf-2015)
- [Opcode-Only Trace Reconstruction (0CTF 2016)](#opcode-only-trace-reconstruction-0ctf-2016)
- [LD_PRELOAD time() Freeze for Deterministic Analysis (EKOPARTY 2017)](#ld_preload-time-freeze-for-deterministic-analysis-ekoparty-2017)

---

## Frida (Dynamic Instrumentation)

Frida injects JavaScript into running processes for real-time hooking, tracing, and modification. Essential for anti-debug bypass, runtime inspection, and mobile RE.

### Installation

```bash
pip install frida-tools frida
# Verify
frida --version
```

### Basic Function Hooking

```javascript
// hook.js — intercept a function and log arguments/return value
Interceptor.attach(Module.findExportByName(null, "strcmp"), {
    onEnter: function(args) {
        this.arg0 = Memory.readUtf8String(args[0]);
        this.arg1 = Memory.readUtf8String(args[1]);
        console.log(`strcmp("${this.arg0}", "${this.arg1}")`);
    },
    onLeave: function(retval) {
        console.log(`  → ${retval}`);
    }
});
```

```bash
# Attach to running process
frida -p $(pidof binary) -l hook.js

# Spawn and instrument from start
frida -f ./binary -l hook.js --no-pause

# One-liner: hook strcmp and dump comparisons
frida -f ./binary --no-pause -e '
Interceptor.attach(Module.findExportByName(null, "strcmp"), {
    onEnter(args) {
        console.log("strcmp:", Memory.readUtf8String(args[0]), Memory.readUtf8String(args[1]));
    }
});
'
```

### Anti-Debug Bypass

```javascript
// Bypass ptrace(PTRACE_TRACEME) — returns 0 (success) without calling
Interceptor.attach(Module.findExportByName(null, "ptrace"), {
    onEnter: function(args) {
        this.request = args[0].toInt32();
    },
    onLeave: function(retval) {
        if (this.request === 0) { // PTRACE_TRACEME
            retval.replace(ptr(0));
            console.log("[*] ptrace(TRACEME) bypassed");
        }
    }
});

// Bypass IsDebuggerPresent (Windows)
var isDbg = Module.findExportByName("kernel32.dll", "IsDebuggerPresent");
Interceptor.attach(isDbg, {
    onLeave: function(retval) {
        retval.replace(ptr(0));
    }
});

// Bypass timing checks — hook clock_gettime to return constant
Interceptor.attach(Module.findExportByName(null, "clock_gettime"), {
    onLeave: function(retval) {
        // Force constant timestamp to defeat timing checks
        var ts = this.context.rsi || this.context.x1; // x86 or ARM
        Memory.writeU64(ts, 0);        // tv_sec
        Memory.writeU64(ts.add(8), 0); // tv_nsec
    }
});
```

### Memory Scanning and Patching

```javascript
// Scan for flag pattern in memory
Process.enumerateRanges('r--').forEach(function(range) {
    Memory.scan(range.base, range.size, "66 6c 61 67 7b", { // "flag{"
        onMatch: function(address, size) {
            console.log("[FLAG] Found at:", address, Memory.readUtf8String(address, 64));
        },
        onComplete: function() {}
    });
});

// Patch instruction (NOP out a check)
var addr = Module.findBaseAddress("binary").add(0x1234);
Memory.patchCode(addr, 2, function(code) {
    var writer = new X86Writer(code, { pc: addr });
    writer.putNop();
    writer.putNop();
    writer.flush();
});
```

### Function Replacement

```javascript
// Replace a validation function to always return true
var checkFlag = Module.findExportByName(null, "check_flag");
Interceptor.replace(checkFlag, new NativeCallback(function(input) {
    console.log("[*] check_flag called with:", Memory.readUtf8String(input));
    return 1; // always valid
}, 'int', ['pointer']));
```

### Tracing and Stalker

```javascript
// Trace all calls in a function (Stalker — instruction-level tracing)
var targetAddr = Module.findExportByName(null, "main");
Stalker.follow(Process.getCurrentThreadId(), {
    transform: function(iterator) {
        var instruction;
        while ((instruction = iterator.next()) !== null) {
            if (instruction.mnemonic === "call") {
                iterator.putCallout(function(context) {
                    console.log("CALL at", context.pc, "→", ptr(context.pc).readPointer());
                });
            }
            iterator.keep();
        }
    }
});
```

### r2frida (Radare2 + Frida Integration)

```bash
# Attach radare2 to process via Frida
r2 frida://spawn/./binary

# r2frida commands
\ii                    # List imports
\il                    # List loaded modules
\dt strcmp             # Trace strcmp calls
\dc                    # Continue execution
\dm                    # List memory maps
```

### Frida for Android/iOS

```bash
# Android (requires rooted device or Frida server)
adb push frida-server /data/local/tmp/
adb shell "chmod 755 /data/local/tmp/frida-server && /data/local/tmp/frida-server &"

# Hook Android Java methods
frida -U -f com.example.app -l hook_android.js --no-pause
```

```javascript
// hook_android.js — hook Java method
Java.perform(function() {
    var MainActivity = Java.use("com.example.app.MainActivity");
    MainActivity.checkPassword.implementation = function(input) {
        console.log("[*] checkPassword called with:", input);
        var result = this.checkPassword(input);
        console.log("[*] Result:", result);
        return result;
    };
});
```

**Key insight:** Frida excels where static analysis fails — obfuscated code, packed binaries, and runtime-generated data. Hook comparison functions (`strcmp`, `memcmp`, custom validators) to extract expected values without reversing the algorithm. Use `Interceptor.attach` for observation, `Interceptor.replace` for modification.

**When to use:** Anti-debugging bypass, extracting runtime-computed keys, hooking crypto functions to dump plaintext, mobile app analysis, packed binary inspection.

---

## angr (Symbolic Execution)

angr automatically explores program paths to find inputs satisfying constraints. Solves many flag-checking binaries in minutes that take hours manually.

### angr Installation

```bash
pip install angr
```

### Basic Path Exploration

```python
import angr
import claripy

# Load binary
proj = angr.Project('./binary', auto_load_libs=False)

# Find address of "Correct!" print, avoid "Wrong!" print
# Get these from disassembly (objdump -d or Ghidra)
FIND_ADDR = 0x401234    # Address of success path
AVOID_ADDR = 0x401256   # Address of failure path

# Create simulation manager and explore
simgr = proj.factory.simgr()
simgr.explore(find=FIND_ADDR, avoid=AVOID_ADDR)

if simgr.found:
    found = simgr.found[0]
    # Get stdin that reaches the target
    print("Flag:", found.posix.dumps(0))  # fd 0 = stdin
```

### Symbolic Input with Constraints

```python
import angr
import claripy

proj = angr.Project('./binary', auto_load_libs=False)

# Create symbolic input (e.g., 32-byte flag)
flag_len = 32
flag_chars = [claripy.BVS(f'flag_{i}', 8) for i in range(flag_len)]
flag = claripy.Concat(*flag_chars + [claripy.BVV(b'\n')])

# Constrain to printable ASCII
state = proj.factory.entry_state(stdin=flag)
for c in flag_chars:
    state.solver.add(c >= 0x20)
    state.solver.add(c <= 0x7e)

# Constrain known prefix: "flag{"
state.solver.add(flag_chars[0] == ord('f'))
state.solver.add(flag_chars[1] == ord('l'))
state.solver.add(flag_chars[2] == ord('a'))
state.solver.add(flag_chars[3] == ord('g'))
state.solver.add(flag_chars[4] == ord('{'))
state.solver.add(flag_chars[flag_len-1] == ord('}'))

simgr = proj.factory.simgr(state)
simgr.explore(find=0x401234, avoid=0x401256)

if simgr.found:
    found = simgr.found[0]
    result = found.solver.eval(flag, cast_to=bytes)
    print("Flag:", result.decode())
```

### Hook Functions to Simplify Analysis

```python
import angr

proj = angr.Project('./binary', auto_load_libs=False)

# Hook printf to avoid path explosion in I/O
@proj.hook(0x401100, length=5)  # Address of call to printf
def skip_printf(state):
    pass  # Do nothing, just skip

# Hook sleep/anti-debug functions
@proj.hook(0x401050, length=5)  # Address of call to sleep
def skip_sleep(state):
    pass

# Replace a function with a summary
class AlwaysSucceed(angr.SimProcedure):
    def run(self):
        return 1

proj.hook_symbol('check_license', AlwaysSucceed())
```

### Exploring from Specific Address

```python
# Start from middle of function (skip initialization)
state = proj.factory.blank_state(addr=0x401200)

# Set up registers/memory manually
state.regs.rdi = 0x600000  # Pointer to input buffer
state.memory.store(0x600000, b"AAAA" + b"\x00" * 28)

simgr = proj.factory.simgr(state)
simgr.explore(find=0x401300, avoid=0x401350)
```

### Common Patterns and Tips

```python
# Pattern 1: argv-based input
state = proj.factory.entry_state(args=['./binary', flag_sym])

# Pattern 2: Multiple find/avoid addresses
simgr.explore(
    find=[0x401234, 0x401300],     # Any success path
    avoid=[0x401256, 0x401400]     # All failure paths
)

# Pattern 3: Find by output string (no address needed)
def is_successful(state):
    stdout = state.posix.dumps(1)  # fd 1 = stdout
    return b"Correct" in stdout

def should_avoid(state):
    stdout = state.posix.dumps(1)
    return b"Wrong" in stdout

simgr.explore(find=is_successful, avoid=should_avoid)

# Pattern 4: Timeout protection
simgr.explore(find=0x401234, avoid=0x401256, num_find=1)
# Or use exploration techniques:
simgr.use_technique(angr.exploration_techniques.DFS())  # Depth-first
simgr.use_technique(angr.exploration_techniques.LengthLimiter(max_length=500))
```

### Dealing with Path Explosion

```python
# Use DFS instead of BFS (default) for flag checkers
simgr.use_technique(angr.exploration_techniques.DFS())

# Limit symbolic memory operations
state.options.add(angr.options.ZERO_FILL_UNCONSTRAINED_MEMORY)
state.options.add(angr.options.ZERO_FILL_UNCONSTRAINED_REGISTERS)

# Hook expensive functions (crypto, hashing) to avoid explosion
import hashlib
class SHA256Hook(angr.SimProcedure):
    def run(self, data, length, output):
        # Concretize input and compute hash
        concrete_data = self.state.solver.eval(
            self.state.memory.load(data, self.state.solver.eval(length)),
            cast_to=bytes
        )
        h = hashlib.sha256(concrete_data).digest()
        self.state.memory.store(output, h)

proj.hook_symbol('SHA256', SHA256Hook())
```

### angr CFG Recovery

```python
# Control flow graph for understanding structure
cfg = proj.analyses.CFGFast()
print(f"Functions found: {len(cfg.functions)}")

# Find main
for addr, func in cfg.functions.items():
    if func.name == 'main':
        print(f"main at {addr:#x}")
        break

# Cross-references
node = cfg.model.get_any_node(0x401234)
print("Predecessors:", [hex(p.addr) for p in cfg.model.get_predecessors(node)])
```

**Key insight:** angr works best on flag-checker binaries with clear success/failure paths. For complex binaries, hook expensive functions (crypto, I/O) and use DFS exploration. Start with the simplest approach (just find/avoid addresses) before adding constraints. If angr is slow, constrain input to printable ASCII and add known prefix.

**When to use:** Flag validators with branching logic, maze/path-finding binaries, constraint-heavy checks, automated binary analysis. Less effective for: heavy crypto, floating-point math, complex heap operations.

---

## lldb (LLVM Debugger)

Primary debugger for macOS/iOS. Also works on Linux. Preferred for Swift/Objective-C and Apple platform binaries.

### Basic Commands

```bash
lldb ./binary
(lldb) run                          # Run program
(lldb) b main                       # Breakpoint on main
(lldb) b 0x401234                   # Breakpoint at address
(lldb) breakpoint set -r "check.*"  # Regex breakpoint
(lldb) c                            # Continue
(lldb) si                           # Step instruction
(lldb) ni                           # Next instruction
(lldb) register read                # Show all registers
(lldb) register write rax 0         # Modify register
(lldb) memory read 0x401000 -c 32   # Read 32 bytes
(lldb) x/s $rsi                     # Examine string (GDB-style)
(lldb) dis -n main                  # Disassemble function
(lldb) image list                   # Loaded modules + base addresses
```

### Scripting (Python)

```python
# lldb Python scripting
import lldb

def hook_strcmp(debugger, command, result, internal_dict):
    target = debugger.GetSelectedTarget()
    process = target.GetProcess()
    thread = process.GetSelectedThread()
    frame = thread.GetSelectedFrame()
    arg0 = frame.FindRegister("rdi").GetValueAsUnsigned()
    arg1 = frame.FindRegister("rsi").GetValueAsUnsigned()
    s0 = process.ReadCStringFromMemory(arg0, 256, lldb.SBError())
    s1 = process.ReadCStringFromMemory(arg1, 256, lldb.SBError())
    print(f'strcmp("{s0}", "{s1}")')

# Register in lldb: command script add -f script.hook_strcmp hook_strcmp
```

**Key insight:** Use lldb for macOS binaries (Mach-O), iOS apps, and when GDB isn't available. `image list` gives ASLR slide for PIE binaries. Scripting API is more structured than GDB's.

---

## x64dbg (Windows Debugger)

Open-source Windows debugger with modern UI. Alternative to OllyDbg/WinDbg for Windows RE challenges.

### Key Features

```bash
# Launch
x64dbg.exe binary.exe         # 64-bit
x32dbg.exe binary.exe         # 32-bit

# Essential shortcuts
F2      → Toggle breakpoint
F7      → Step into
F8      → Step over
F9      → Run
Ctrl+G  → Go to address
Ctrl+F  → Find pattern in memory
```

### Scripting

```bash
# x64dbg command line
bp 0x401234                    # Breakpoint
SetBPX 0x401234, 0, "log {s:utf8@[esp+4]}"  # Log string arg on hit
run                            # Continue
StepOver                       # Step over
```

### Common CTF Workflow

1. Set breakpoint on `GetWindowTextA`/`MessageBoxA` for GUI crackers
2. Trace back from success/failure message
3. Use **Scylla** plugin for IAT reconstruction on packed binaries
4. **Snowman** decompiler plugin for quick pseudo-C

**Key insight:** x64dbg has built-in pattern scanning, hardware breakpoints, and conditional logging. For Windows CTF binaries, it's often faster than IDA/Ghidra for dynamic analysis. Use the **xAnalyzer** plugin for automatic function argument annotation.

---

## Qiling Framework (Cross-Platform Emulation)

Qiling emulates binaries with OS-level support (syscalls, filesystem, registry). Built on Unicorn but adds the OS layer that Unicorn lacks.

### Qiling Installation

```bash
pip install qiling
# Download rootfs for target OS:
git clone https://github.com/qilingframework/rootfs
```

### Basic Usage

```python
from qiling import Qiling
from qiling.const import QL_VERBOSE

# Linux ELF emulation
ql = Qiling(["./binary", "arg1"], "rootfs/x8664_linux",
            verbose=QL_VERBOSE.DEFAULT)
ql.run()

# Windows PE emulation (no Windows needed!)
ql = Qiling(["rootfs/x86_windows/bin/binary.exe"], "rootfs/x86_windows")
ql.run()

# ARM/MIPS emulation (IoT firmware)
ql = Qiling(["rootfs/arm_linux/bin/binary"], "rootfs/arm_linux")
ql.run()
```

### Anti-Debug Bypass via Emulation

```python
from qiling import Qiling

ql = Qiling(["./binary"], "rootfs/x8664_linux")

# Hook ptrace syscall — return 0 (success)
def hook_ptrace(ql, ptrace_request, pid, addr, data):
    ql.log.info("ptrace bypassed")
    return 0

ql.os.set_syscall("ptrace", hook_ptrace)

# Hook specific address (e.g., anti-VM check)
def skip_check(ql):
    ql.arch.regs.rax = 0  # Force success
    ql.log.info(f"Skipped check at {ql.arch.regs.rip:#x}")

ql.hook_address(skip_check, 0x401234)

ql.run()
```

### Input Fuzzing with Qiling

```python
# Emulate binary with different inputs to find flag
import string
from qiling import Qiling

def test_input(candidate):
    ql = Qiling(["./binary"], "rootfs/x8664_linux",
                verbose=QL_VERBOSE.DISABLED, stdin=candidate.encode())
    ql.run()
    return ql.os.stdout.read()

for ch in string.printable:
    output = test_input("flag{" + ch)
    if b"Correct" in output:
        print(f"Found: {ch}")
```

**Advantages over GDB/Frida:**
- No debugger artifacts (bypasses all anti-debug by default)
- Cross-platform without hardware (ARM, MIPS, RISC-V on x86 host)
- Scriptable with Python (faster iteration than GDB)
- Snapshot/restore for brute-forcing

**Key insight:** Qiling emulates the entire OS layer (syscalls, filesystem, registry), not just the CPU. This means anti-debug checks like `ptrace(TRACEME)` naturally return success without patching, and you can analyze ARM/MIPS binaries on an x86 host without QEMU or real hardware.

**When to use:** Foreign architecture binaries, IoT firmware, heavy anti-debug, automated testing of many inputs.

---

## Triton (Dynamic Symbolic Execution)

See [tools-advanced.md](tools-advanced.md#triton-dynamic-symbolic-execution) for full Triton reference. Quick usage:

```python
from triton import *

ctx = TritonContext(ARCH.X86_64)

# Symbolize input buffer
for i in range(32):
    ctx.symbolizeMemory(MemoryAccess(0x600000 + i, CPUSIZE.BYTE), f"flag_{i}")

# Process instructions and collect constraints
# At comparison point, solve for flag
model = ctx.getModel(ctx.getPathConstraintsAst())
flag = ''.join(chr(v.getValue()) for _, v in sorted(model.items()))
```

**Key insight:** Triton excels at single-path DSE (Dynamic Symbolic Execution) where angr's path explosion is a problem. Feed it a concrete execution trace, symbolize specific inputs, and solve for constraints at comparison points. Faster than angr for linear code paths with known execution flow.

**Best for:** Single-path symbolic execution, deobfuscation, taint analysis. Faster than angr for linear code paths.

---

## Intel Pin Instruction-Counting Side Channel (Hackover CTF 2015)

**Pattern:** Brute-force input character-by-character against a binary using Intel Pin's `inscount0` tool. Each correct character causes deeper execution (more instructions) in the comparison logic.

```python
import string
from subprocess import Popen, PIPE

pin = './pin'
tool = './source/tools/ManualExamples/obj-ia32/inscount0.so'
binary = './target'

key = ''
while True:
    best_count, best_char = 0, ''
    for c in string.printable:
        cmd = [pin, '-injection', 'child', '-t', tool, '--', binary]
        p = Popen(cmd, stdout=PIPE, stdin=PIPE, stderr=PIPE)
        p.communicate((key + c + '\n').encode())
        with open('inscount.out') as f:
            count = int(f.read().split()[-1])
        if count > best_count:
            best_count, best_char = count, c
    key += best_char
    print(f"Found: {key}")
```

**Key insight:** Movfuscated binaries (compiled with `movfuscator`) expand every instruction into sequences of `mov` operations, making static analysis impractical. However, character-by-character comparison still creates measurable instruction count differences. Pin's `inscount0.so` counts total executed instructions — the correct character at each position causes ~1000+ more instructions (proceeding further in the comparison). Also works for obfuscated binaries with sequential input checks.

---

## Opcode-Only Trace Reconstruction (0CTF 2016)

Given an execution trace with only opcodes (no register/memory values), reconstruct the program: sort/dedup trace by address, split into basic blocks, annotate functions. Sorting algorithms are particularly vulnerable -- branch decisions leak element ordering.

**Approach:**
1. Sort trace entries by address, deduplicate to recover code layout
2. Identify basic block boundaries (jumps, calls, returns)
3. Map branch taken/not-taken decisions from trace order
4. For sorting algorithms, partition comparisons reveal relative ordering of all input elements

**Key insight:** Execution traces without data values still leak information through branch decisions. Quicksort partition comparisons reveal which element is greater/lesser at each step, enabling full recovery of the sorted input from branch direction alone.

---

## LD_PRELOAD time() Freeze for Deterministic Analysis (EKOPARTY 2017)

Override `time()` via LD_PRELOAD to return a constant value, freezing any timestamp-seeded PRNG. Once the binary's cipher becomes deterministic, brute-force each output byte without understanding the VM or cipher internals.

```c
// freeze_time.c — compile: gcc -shared -fPIC -o freeze.so freeze_time.c
#include <time.h>

time_t time(time_t *t) {
    if (t) *t = 1234567890;
    return 1234567890;
}
```

```bash
# Build and use:
gcc -shared -fPIC -o freeze.so freeze_time.c
LD_PRELOAD=./freeze.so ./binary

# Byte-at-a-time oracle: run with frozen time, try each candidate byte,
# observe output — correct byte produces expected output character.
for byte in $(seq 0 255); do
    output=$(echo -n "$(printf '\x%02x' $byte)" | LD_PRELOAD=./freeze.so ./binary)
    # Check output against known/expected
done
```

If `srand()` or `rand()` is also involved, override `rand()` too:
```c
int rand(void) { return 42; }
```

**Key insight:** LD_PRELOAD function interception freezes non-determinism sources (time, rand). Once deterministic, even complex VMs become tractable byte-at-a-time oracles.

**References:** EKOPARTY CTF 2017


# tools

# CTF Reverse - Tools Reference

## Table of Contents
- [GDB](#gdb)
  - [Basic Commands](#basic-commands)
  - [PIE Binary Debugging](#pie-binary-debugging)
  - [One-liner Automation](#one-liner-automation)
  - [Memory Examination](#memory-examination)
- [Radare2](#radare2)
  - [Basic Session](#basic-session)
  - [r2pipe Automation](#r2pipe-automation)
- [Ghidra](#ghidra)
  - [Headless Analysis](#headless-analysis)
  - [Emulator for Decryption](#emulator-for-decryption)
  - [MCP Commands](#mcp-commands)
- [Unicorn Emulation](#unicorn-emulation)
  - [Basic Setup](#basic-setup)
  - [Mixed-Mode (64 to 32) Switch](#mixed-mode-64-to-32-switch)
  - [Register Tracing Hook](#register-tracing-hook)
  - [Track Register Changes](#track-register-changes)
- [Python Bytecode](#python-bytecode)
  - [Disassembly](#disassembly)
  - [Extract Constants](#extract-constants)
  - [Pyarmor Static Unpack (1shot)](#pyarmor-static-unpack-1shot)
- [WASM Analysis](#wasm-analysis)
  - [Decompile to C](#decompile-to-c)
  - [Common Patterns](#common-patterns)
- [Android APK](#android-apk)
  - [Extraction](#extraction)
  - [Key Locations](#key-locations)
  - [Search](#search)
  - [Flutter APK (Blutter)](#flutter-apk-blutter)
  - [HarmonyOS HAP/ABC (abc-decompiler)](#harmonyos-hapabc-abc-decompiler)
- [.NET Analysis](#net-analysis)
  - [Tools](#tools)
  - [Two-Stage XOR + AES-CBC Decode Pattern (Codegate 2013)](#two-stage-xor--aes-cbc-decode-pattern-codegate-2013)
  - [NativeAOT](#nativeaot)
- [Packed Binaries](#packed-binaries)
  - [UPX](#upx)
  - [Custom Packers](#custom-packers)
  - [PyInstaller](#pyinstaller)
- [LLVM IR](#llvm-ir)
  - [Convert to Assembly](#convert-to-assembly)
- [RISC-V Binary Analysis (EHAX 2026)](#risc-v-binary-analysis-ehax-2026)
- [Binary Ninja](#binary-ninja)
- [Decompiler Comparison with dogbolt.org](#decompiler-comparison-with-dogboltorg)
- [Useful Commands](#useful-commands)

For dynamic instrumentation tools (Frida, angr, lldb, x64dbg), see [tools-dynamic.md](tools-dynamic.md).

---

## GDB

### Basic Commands
```bash
gdb ./binary
run                      # Run program
start                    # Run to main
b *0x401234              # Breakpoint at address
b *main+0x100            # Relative breakpoint
c                        # Continue
si                       # Step instruction
ni                       # Next instruction (skip calls)
x/s $rsi                 # Examine string
x/20x $rsp               # Examine stack
info registers           # Show registers
set $eax=0               # Modify register
```

### PIE Binary Debugging
```bash
gdb ./binary
start                    # Forces PIE base resolution
b *main+0xca            # Relative to main
b *main+0x198
run
```

### One-liner Automation
```bash
gdb -ex 'start' -ex 'b *main+0x198' -ex 'run' ./binary
```

### Memory Examination
```bash
x/s $rsi                 # String at RSI
x/38c $rsi               # 38 characters
x/20x $rsp               # 20 hex words from stack
x/10i $rip               # 10 instructions from RIP
```

---

## Radare2

### Basic Session
```bash
r2 -d ./binary           # Open in debug mode
aaa                      # Analyze all
afl                      # List functions
pdf @ main               # Disassemble main
db 0x401234              # Set breakpoint
dc                       # Continue
ood                      # Restart debugging
dr                       # Show registers
dr eax=0                 # Modify register
```

### r2pipe Automation
```python
import r2pipe
r2 = r2pipe.open('./binary', flags=['-d'])
r2.cmd('aaa')
r2.cmd('db 0x401234')

for char in range(256):
    r2.cmd('ood')        # Restart
    r2.cmd(f'dr eax={char}')
    output = r2.cmd('dc')
    if 'correct' in output:
        print(f"Found: {chr(char)}")
```

---

## Ghidra

### Headless Analysis
```bash
analyzeHeadless /path/to/project tmp -import binary -postScript script.py
```

### Emulator for Decryption
```java
EmulatorHelper emu = new EmulatorHelper(currentProgram);
emu.writeRegister("RSP", 0x2fff0000);
emu.writeRegister("RBP", 0x2fff0000);

// Write encrypted data
emu.writeMemory(dataAddress, encryptedBytes);

// Set function arguments
emu.writeRegister("RDI", arg1);

// Run until return
emu.setBreakpoint(returnAddress);
emu.run(functionEntryAddress);

// Read result
byte[] decrypted = emu.readMemory(outputAddress, length);
```

### MCP Commands
- Recon: `list_functions`, `list_imports`, `list_strings`
- Analysis: `decompile_function`, `get_xrefs_to`
- Annotation: `rename_function`, `rename_variable`

---

## Unicorn Emulation

### Basic Setup
```python
from unicorn import *
from unicorn.x86_const import *

mu = Uc(UC_ARCH_X86, UC_MODE_64)

# Map code segment
mu.mem_map(0x400000, 0x10000)
mu.mem_write(0x400000, code_bytes)

# Map stack
mu.mem_map(0x7fff0000, 0x10000)
mu.reg_write(UC_X86_REG_RSP, 0x7fff0000 + 0xff00)

# Run
mu.emu_start(start_addr, end_addr)
```

### Mixed-Mode (64 to 32) Switch
```python
# When a 64-bit stub jumps into 32-bit code via retf/retfq:
# - retf pops 4-byte EIP + 2-byte CS (6 bytes)
# - retfq pops 8-byte RIP + 8-byte CS (16 bytes)

uc32 = Uc(UC_ARCH_X86, UC_MODE_32)
# Copy memory regions, then GPRs
reg_map = {
    UC_X86_REG_EAX: UC_X86_REG_RAX,
    UC_X86_REG_EBX: UC_X86_REG_RBX,
    UC_X86_REG_ECX: UC_X86_REG_RCX,
    UC_X86_REG_EDX: UC_X86_REG_RDX,
    UC_X86_REG_ESI: UC_X86_REG_RSI,
    UC_X86_REG_EDI: UC_X86_REG_RDI,
    UC_X86_REG_EBP: UC_X86_REG_RBP,
}
for e, r in reg_map.items():
    uc32.reg_write(e, mu.reg_read(r) & 0xffffffff)  # mu = 64-bit emulator from above
uc32.reg_write(UC_X86_REG_EFLAGS, mu.reg_read(UC_X86_REG_RFLAGS) & 0xffffffff)

# SSE-heavy blobs need XMM registers copied
for xr in [UC_X86_REG_XMM0, UC_X86_REG_XMM1, UC_X86_REG_XMM2, UC_X86_REG_XMM3,
           UC_X86_REG_XMM4, UC_X86_REG_XMM5, UC_X86_REG_XMM6, UC_X86_REG_XMM7]:
    uc32.reg_write(xr, mu.reg_read(xr))

# Run 32-bit, then copy regs/memory back to 64-bit
```

**Tip:** set `UC_IGNORE_REG_BREAK=1` to silence warnings on unimplemented regs.

### Register Tracing Hook
```python
def hook_code(uc, address, size, user_data):
    if address == TARGET_ADDR:
        rsi = uc.reg_read(UC_X86_REG_RSI)
        print(f"0x{address:x}: rsi=0x{rsi:016x}")

mu.hook_add(UC_HOOK_CODE, hook_code)
```

### Track Register Changes
```python
prev_rsi = [None]
def hook_rsi_changes(uc, address, size, user_data):
    rsi = uc.reg_read(UC_X86_REG_RSI)
    if rsi != prev_rsi[0]:
        print(f"0x{address:x}: RSI changed to 0x{rsi:016x}")
        prev_rsi[0] = rsi

mu.hook_add(UC_HOOK_CODE, hook_rsi_changes)
```

---

## Python Bytecode

### Disassembly
```python
import marshal, dis

with open('file.pyc', 'rb') as f:
    f.read(16)  # Skip header (varies by Python version)
    code = marshal.load(f)
    dis.dis(code)
```

### Extract Constants
```python
for ins in dis.get_instructions(code):
    if ins.opname == 'LOAD_CONST':
        print(ins.argval)
```

### Pyarmor Static Unpack (1shot)

Repository: `https://github.com/Lil-House/Pyarmor-Static-Unpack-1shot`

```bash
# Basic usage (recursive processing)
python /path/to/oneshot/shot.py /path/to/scripts

# Specify pyarmor runtime library explicitly
python /path/to/oneshot/shot.py /path/to/scripts -r /path/to/pyarmor_runtime.so

# Save outputs to another directory
python /path/to/oneshot/shot.py /path/to/scripts -o /path/to/output
```

Notes:
- `oneshot/pyarmor-1shot` must exist before running `shot.py`.
- Supported focus: Pyarmor 8.x-9.x (`PY` + six digits header style).
- Pyarmor 7 and earlier (`PYARMOR` header) are out of scope.
- Disassembly output is generally reliable; decompiled source is experimental.

---

## WASM Analysis

### Decompile to C
```bash
wasm2c checker.wasm -o checker.c
gcc -O3 checker.c wasm-rt-impl.c -o checker
```

### Common Patterns
- `w2c_memory` - Linear memory array
- `wasm_rt_trap(N)` - Runtime errors
- Function exports: `flagChecker`, `validate`

---

## Android APK

### Extraction
```bash
apktool d app.apk -o decoded/   # Best - decodes XML
jadx app.apk                     # Decompile to Java
unzip app.apk -d extracted/      # Simple extraction
```

### Key Locations
- `res/values/strings.xml` - String resources
- `AndroidManifest.xml` - App metadata
- `classes.dex` - Dalvik bytecode
- `assets/`, `res/raw/` - Resources

### Search
```bash
grep -r "flag\|CTF" decoded/
strings decoded/classes*.dex | grep -i flag
```

### Flutter APK (Blutter)

```bash
# Run Blutter on arm64 build
python3 blutter.py path/to/app/lib/arm64-v8a out_dir
```

### HarmonyOS HAP/ABC (abc-decompiler)

Repository: `https://github.com/ohos-decompiler/abc-decompiler`

```bash
# Extract .hap first to obtain .abc files
unzip app.hap -d hap_extracted/
```

Critical startup mode:
```bash
# Use CLI entrypoint (avoid java -jar GUI mode)
java -cp "./jadx-dev-all.jar" jadx.cli.JadxCLI [options] <input>
```

```bash
# Basic decompile
java -cp "./jadx-dev-all.jar" jadx.cli.JadxCLI -d "out" ".abc"

# Recommended for .abc
java -cp "./jadx-dev-all.jar" jadx.cli.JadxCLI -m simple --log-level ERROR -d "out_abc_simple" ".abc"
```

Notes:
- Start with `-m simple --log-level ERROR`.
- If `auto` fails, retry with `-m simple` first.
- Errors do not always mean total failure; check `out_xxx/sources/`.
- Use a fresh output directory per run.

---

## .NET Analysis

### Tools
- **dnSpy** - Debugging + decompilation (best)
- **ILSpy** - Decompiler
- **dotPeek** - JetBrains decompiler

### NativeAOT
- Look for `System.Private.CoreLib` strings
- Type metadata present but restructured
- Search for length-prefixed UTF-16 patterns

### Two-Stage XOR + AES-CBC Decode Pattern (Codegate 2013)

**Pattern:** .NET binary stores an encrypted byte array that undergoes XOR decoding followed by AES-256-CBC decryption. The same key value serves as both the AES key and IV.

**Steps:**
1. Extract hardcoded byte array and key string from binary (dnSpy/ILSpy)
2. XOR each byte (may be multi-pass, e.g., `0x25` then `0x58`, equivalent to single `0x7D`)
3. Base64-decode the XOR result
4. AES-256-CBC decrypt with `RijndaelManaged` using the extracted key as both Key and IV

```python
from Crypto.Cipher import AES
from base64 import b64decode

# Step 1: XOR decode
data = bytearray(encrypted_bytes)
for i in range(len(data)):
    data[i] ^= 0x7D  # Combined XOR key (0x25 ^ 0x58)

# Step 2: Base64 decode
ct = b64decode(bytes(data))

# Step 3: AES-256-CBC decrypt (same value for key and IV)
key = b"9e2ea73295c7201c5ccd044477228527"  # Padded to 32 bytes
cipher = AES.new(key, AES.MODE_CBC, iv=key)
plaintext = cipher.decrypt(ct)
```

**Key insight:** When `RijndaelManaged` appears in .NET decompilation, check if Key and IV are set to the same value — this is a common CTF pattern. The XOR stage often serves as a simple obfuscation layer before the real crypto.

---

## Packed Binaries

### UPX
```bash
upx -d packed -o unpacked
strings binary | grep UPX     # Check for UPX signature
```

### Custom Packers
1. Set breakpoint after unpacking stub
2. Dump memory
3. Fix PE/ELF headers

### PyInstaller
```bash
python pyinstxtractor.py binary.exe
# Look in: binary.exe_extracted/
```

---

## LLVM IR

### Convert to Assembly
```bash
llc task.ll --x86-asm-syntax=intel
gcc -c task.s -o file.o
```

---

## RISC-V Binary Analysis (EHAX 2026)

**Pattern (iguessbro):** Statically linked, stripped RISC-V ELF binary. Can't run natively on x86.

**Disassembly with Capstone:**
```python
from capstone import *

with open('binary', 'rb') as f:
    code = f.read()

# RISC-V 64-bit with compressed instruction support
md = Cs(CS_ARCH_RISCV, CS_MODE_RISCVC | CS_MODE_RISCV64)
md.detail = True

# Disassemble from entry point (check ELF header for e_entry)
TEXT_OFFSET = 0x10000  # typical for static RISC-V
for insn in md.disasm(code[TEXT_OFFSET:], TEXT_OFFSET):
    print(f"0x{insn.address:x}:\t{insn.mnemonic}\t{insn.op_str}")
```

**Common RISC-V patterns:**
- `li a0, N` → load immediate (argument setup)
- `mv a0, s0` → register move
- `call offset` → function call (auipc + jalr pair)
- `beq/bne a0, zero, label` → conditional branch
- `sd/ld` → 64-bit store/load
- `addiw` → 32-bit add (W-suffix = word operations)

**Key differences from x86:**
- No flags register — comparisons are inline with branch instructions
- Arguments in a0-a7 (not rdi/rsi/rdx)
- Return value in a0
- Saved registers s0-s11 (callee-saved)
- Compressed instructions (2 bytes) mixed with standard (4 bytes) — use `CS_MODE_RISCVC`

**Anti-RE tricks in RISC-V:**
- Fake flags as string constants (check for `"n0t_th3_r34l"` patterns)
- Timing anti-brute-force (rdtime instruction)
- XOR decryption with incremental key: `decrypted[i] = enc[i] ^ (key & 0xFF) ^ 0xA5; key += 7`

**Emulation:** `qemu-riscv64 -L /usr/riscv64-linux-gnu/ ./binary` (needs cross-toolchain sysroot)

---

## Binary Ninja

Interactive disassembler/decompiler with rapid community growth.

**Decompilation outputs:** High-Level Intermediate Language (HLIL), pseudo-C, pseudo-Rust, pseudo-Python.

```bash
# Open binary
binaryninja binary
```

```python
# Headless analysis (Python API)
import binaryninja
bv = binaryninja.open_view("binary")
for func in bv.functions:
    print(func.name, hex(func.start))
    print(func.hlil)  # High-Level IL
```

**Community plugins:** Available via Plugin Manager (Ctrl+Shift+P → "Plugin Manager").

**Free version:** https://binary.ninja/free/ (cloud-based, limited features).

**Advantages over Ghidra:** Faster startup, cleaner IL representations, better Python API for scripting.

---

## Decompiler Comparison with dogbolt.org

**dogbolt.org** runs multiple decompilers simultaneously on the same binary and shows results side-by-side.

**Supported decompilers:** Hex-Rays (IDA), Ghidra, Binary Ninja, angr, RetDec, Snowman, dewolf, Reko, Relyze.

**When to use:**
- Decompiler output is confusing — compare with alternatives for clarity
- One decompiler mishandles a construct — another may get it right
- Quick triage without installing every tool locally
- Validate decompiler correctness by cross-referencing outputs

```bash
# Upload via web interface: https://dogbolt.org/
# Or use the API:
curl -F "file=@binary" https://dogbolt.org/api/binaries/
```

**Key insight:** Different decompilers excel at different constructs. When one produces unreadable output, another often generates clearer pseudocode. Cross-referencing catches decompiler bugs.

---

## Useful Commands

```bash
# File info
file binary
checksec --file=binary
rabin2 -I binary

# String extraction
strings binary | grep -iE "flag|secret"
rabin2 -z binary

# Sections
readelf -S binary
objdump -h binary

# Symbols
nm binary
readelf -s binary

# Disassembly
objdump -d binary
objdump -M intel -d binary
```

