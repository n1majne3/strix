---
name: ctf-crypto
description: Provides cryptography attack techniques for CTF challenges. Use when attacking encryption, hashing, signatures, ZKP, PRNG, or mathematical crypto problems involving RSA, AES, ECC, lattices, LWE, CVP, number theory, Coppersmith, Pollard, Wiener, padding oracle, GCM, key derivation, or stream/block cipher weaknesses.
license: MIT
compatibility: Requires filesystem-based agent (Claude Code or similar) with bash, Python 3, and internet access for tool installation.
allowed-tools: Bash Read Write Edit Glob Grep Task WebFetch WebSearch
metadata:
  user-invocable: "false"
category: ctf
---
# CTF Cryptography

Quick reference for crypto CTF challenges. Each technique has a one-liner here; see supporting files for full details with code.

## Prerequisites

**Python packages (all platforms):**
```bash
pip install pycryptodome z3-solver sympy gmpy2 hashpumpy fpylll py_ecc
```

**Linux (apt):**
```bash
apt install hashcat sagemath
```

**macOS (Homebrew):**
```bash
brew install hashcat
```

**Manual install:**
- SageMath — Linux: `apt install sagemath`, macOS: `brew install --cask sage`
- RsaCtfTool — `git clone https://github.com/RsaCtfTool/RsaCtfTool` (automated RSA attacks)

> **Note:** `gmpy2` requires libgmp — Linux: `apt install libgmp-dev`, macOS: `brew install gmp`.

## Additional Resources

- [classic-ciphers.md](classic-ciphers.md) - Classic ciphers: Vigenere (+ Kasiski examination), Atbash, substitution wheels, XOR variants (+ multi-byte frequency analysis), deterministic OTP, cascade XOR, book cipher, OTP key reuse / many-time pad, variable-length homophonic substitution, grid permutation cipher keyspace reduction, image-based Caesar shift ciphers, XOR key recovery via file format headers
- [modern-ciphers.md](modern-ciphers.md) - Modern cipher attacks: AES (CFB-8, ECB leakage), CBC-MAC/OFB-MAC, padding oracle, S-box collisions, GF(2) elimination, LCG partial output recovery, affine cipher over composite modulus, AES-GCM with derived keys, AES-GCM nonce reuse (forbidden attack), Ascon-like reduced-round differential cryptanalysis, custom linear MAC forgery, CBC padding oracle (full block decryption), Bleichenbacher RSA PKCS#1 v1.5 padding oracle (ROBOT), birthday attack / meet-in-the-middle, CRC32 collision signature forgery, AES key recovery via byte-by-byte zeroing oracle
- [modern-ciphers-2.md](modern-ciphers-2.md) - Modern cipher attacks (continued): Blum-Goldwasser bit-extension oracle, hash length extension, compression oracle (CRIME-style), hash function time reversal via cycle detection, OFB mode invertible RNG backward decryption, weak key derivation via public key hash XOR, HMAC-CRC linearity attack, DES weak keys in OFB mode, SRP protocol bypass, modified AES S-Box brute-force, square attack on reduced-round AES, AES-ECB byte-at-a-time chosen plaintext, AES-ECB cut-and-paste block manipulation, AES-CBC IV bit-flip auth bypass, Rabin LSB parity oracle, PBKDF2 pre-hash bypass, MD5 multi-collision via fastcol, custom hash state reversal, CRC32 brute-force for small payloads, noisy RSA LSB oracle error correction, sponge hash MITM collision, CBC IV forgery + block truncation, padding oracle to CBC bitflip RCE, SPN S-box intersection attack
- [stream-ciphers.md](stream-ciphers.md) - Stream cipher attacks: LFSR (Berlekamp-Massey, correlation attack, known-plaintext, Galois vs Fibonacci, Galois tap recovery via autocorrelation), RC4 second-byte bias, XOR consecutive byte correlation
- [rsa-attacks.md](rsa-attacks.md) - RSA attacks: small e (cube root), common modulus, Wiener's, Pollard's p-1, Hastad's broadcast, Hastad with linear padding (Coppersmith), Fermat/consecutive primes, multi-prime, restricted-digit, Coppersmith structured primes, Manger oracle, polynomial hash
- [rsa-attacks-2.md](rsa-attacks-2.md) - RSA attacks (specialized): RSA p=q validation bypass, cube root CRT gcd(e,phi)>1, factoring from phi(n) multiple, multiplicative homomorphism signature forgery, weak keygen via base representation, RSA with gcd(e,phi)>1 exponent reduction, batch GCD shared prime factoring, partial key recovery from dp/dq/qinv, RSA-CRT fault attack, homomorphic decryption oracle bypass, small prime CRT decomposition, Montgomery reduction timing attack, Bleichenbacher low-exponent signature forgery
- [ecc-attacks.md](ecc-attacks.md) - ECC attacks: small subgroup, invalid curve, Smart's attack (anomalous, with Sage code), fault injection, clock group DLP, Pohlig-Hellman, ECDSA nonce reuse, Ed25519 torsion side channel, DSA nonce reuse, DSA key recovery via MD5 collision on k-generation
- [zkp-and-advanced.md](zkp-and-advanced.md) - ZKP/graph 3-coloring, Z3 solver guide, garbled circuits, Shamir SSS, bigram constraint solving, race conditions, Groth16 broken setup, DV-SNARG forgery, KZG pairing oracle for permutation recovery, Shamir SSS reused polynomial coefficients
- [prng.md](prng.md) - PRNG attacks (MT19937, MT float recovery via GF(2) magic matrix for token prediction, LCG, GF(2) matrix PRNG, V8 XorShift128+ Math.random state recovery via Z3, middle-square, deterministic RNG hill climbing, random-mode oracle, time-based seeds, C srand/rand synchronization via ctypes, password cracking, logistic map chaotic PRNG)
- [historical.md](historical.md) - Historical ciphers (Lorenz SZ40/42, book cipher implementation)
- [advanced-math.md](advanced-math.md) - Advanced mathematical attacks (isogenies, Pohlig-Hellman, baby-step giant-step (BSGS) for general DLP, LLL, Merkle-Hellman knapsack via LLL, Coppersmith, quaternion RSA, GF(2)[x] CRT, S-box collision code, LWE lattice CVP attack, affine cipher over non-prime modulus, introspective CRC via GF(2) linear algebra)
- [lattice-and-lwe.md](lattice-and-lwe.md) - Lattice attack triage and workflow: LLL/BKZ/Babai, HNP from partial or biased nonces, truncated LCG state recovery, LWE embedding and CVP, Ring-LWE / Module-LWE recognition, orthogonal lattices, subset sum / knapsack, and common failure modes
- [exotic-crypto.md](exotic-crypto.md) - Exotic algebraic structures (braid group DH / Alexander polynomial, monotone function inversion, tropical semiring residuation, Paillier cryptosystem, Hamming code helical interleaving, ElGamal universal re-encryption, FPE Feistel brute-force, icosahedral symmetry group cipher, Goldwasser-Micali replication oracle, BB-84 QKD MITM attack)

---

## When to Pivot

- If the real blocker is understanding a binary, obfuscated client, or weird VM, switch to `/ctf-reverse`.
- If the challenge is mostly packet carving, disk recovery, or stego extraction before any decryption starts, switch to `/ctf-forensics`.
- If the task is just implementing an exploit against a vulnerable network service after the crypto part is solved, switch to `/ctf-pwn` or `/ctf-web`.
- If the crypto challenge involves adversarial ML, model extraction, or neural-network-based ciphers, switch to `/ctf-ai-ml`.
- If the challenge is really an encoding puzzle, esoteric cipher, or polyglot trick rather than true cryptanalysis, switch to `/ctf-misc`.

## Quick Start Commands

```bash
# Identify cipher type
python3 -c "from Crypto.Util.number import *; n=<N>; print(f'bits={n.bit_length()}')"

# RSA quick check
python3 -c "from sympy import factorint; print(factorint(<n>))"  # Small factors?
openssl rsa -pubin -in key.pub -text -noout  # Extract n, e from PEM

# Quick factorization tools
python3 RsaCtfTool.py -n <n> -e <e> --uncipher <c>

# XOR analysis
python3 -c "from pwn import xor; print(xor(bytes.fromhex('<hex>'), b'flag{'))"

# Hash identification
hashid '<hash>'
hashcat --identify '<hash>'

# SageMath (for lattice/ECC)
sage -c "print(factor(<n>))"
```

## Classic Ciphers

- **Caesar:** Frequency analysis or brute force 26 keys
- **Vigenere:** Known plaintext attack with flag format prefix; derive key from `(ct - pt) mod 26`. Kasiski examination for unknown key length (GCD of repeated sequence distances)
- **Atbash:** A<->Z substitution; look for "Abashed" hints in challenge name
- **Substitution wheel:** Brute force all rotations of inner/outer alphabet mapping
- **Multi-byte XOR:** Split ciphertext by key position, frequency-analyze each column independently; score by English letter frequency (space = 0x20)
- **Cascade XOR:** Brute force first byte (256 attempts), rest follows deterministically
- **XOR rotation (power-of-2):** Even/odd bits never mix; only 4 candidate states
- **Weak XOR verification:** Single-byte XOR check has 1/256 pass rate; brute force with enough budget
- **Deterministic OTP:** Known-plaintext XOR to recover keystream; match load-balanced backends
- **OTP key reuse (many-time pad):** `C1 XOR C2 XOR known_P = unknown_P`; crib dragging when no plaintext known
- **Homophonic (variable-length):** Multi-character ciphertext groups map to single plaintext chars. Find n-grams with identical sub-n-gram frequencies, replace with symbols, solve as monoalphabetic. See [classic-ciphers.md](classic-ciphers.md#variable-length-homophonic-substitution-asis-ctf-finals-2013).
- **Grid permutation cipher:** 5x5 grid with independent row/column permutations collapses keyspace to 5! x 5! = 14,400; brute-force in milliseconds. See [classic-ciphers.md](classic-ciphers.md#grid-permutation-cipher-keyspace-reduction-bsidessf-2026).
- **Image-based Caesar shift:** Pixel rows/columns shifted by per-strip offsets; compare original vs shifted image to extract ASCII-encoded flag from shift amounts. See [classic-ciphers.md](classic-ciphers.md#image-based-caesar-shift-ciphers-bsidessf-2026).
- **Polybius square cipher:** 5x5 grid maps letter pairs to plaintext; digits/coordinates encode positions. See [classic-ciphers.md](classic-ciphers.md#polybius-square-cipher-qiwi-infosec-2016).
- **XOR key recovery via file format headers:** File claims to be PDF/PNG/ZIP but `file` reports "data". XOR first bytes against expected magic bytes to derive repeating key; extend using trailer structures (`%%EOF`, IEND marker). See [classic-ciphers.md](classic-ciphers.md#xor-key-recovery-via-file-format-headers-metactf-flash-2026).

See [classic-ciphers.md](classic-ciphers.md) for full code examples.

## Modern Cipher Attacks

- **AES-ECB:** Block shuffling, byte-at-a-time chosen-plaintext suffix recovery (256 queries per byte, tool: FeatherDuster `ecb_cpa_decrypt`); image ECB preserves visual patterns. ECB cut-and-paste: splice ciphertext blocks to forge JSON fields (e.g., `is_admin: true`). See [modern-ciphers-2.md](modern-ciphers-2.md#aes-ecb-byte-at-a-time-chosen-plaintext-abctf-2016).
- **AES-CBC:** Bit flipping to change plaintext; padding oracle for decryption without key. IV bit-flip: flip specific bits in the IV to change first plaintext block (requires no MAC). See [modern-ciphers-2.md](modern-ciphers-2.md#aes-cbc-iv-bit-flip-authentication-bypass-google-ctf-2016).
- **CBC IV forgery + block truncation:** XOR IV bytes to change decrypted block 0; strip trailing ciphertext blocks (no length integrity in CBC). Forges authenticated tokens when MAC is embedded in the ciphertext. See [modern-ciphers-2.md](modern-ciphers-2.md#cbc-iv-forgery-block-truncation-for-authentication-bypass-0ctf-2017).
- **Padding oracle to CBC bitflip RCE:** Chain padding oracle (recover plaintext) with CBC bitflipping (inject shell metacharacters) for command injection via encrypted parameters. See [modern-ciphers-2.md](modern-ciphers-2.md#padding-oracle-to-cbc-bitflip-command-injection-bsidessf-2017).
- **AES-CFB-8:** Static IV with 8-bit feedback allows state reconstruction after 16 known bytes
- **CBC-MAC/OFB-MAC:** XOR keystream for signature forgery: `new_sig = old_sig XOR block_diff`
- **S-box collisions:** Non-permutation S-box (`len(set(sbox)) < 256`) enables 4,097-query key recovery
- **GF(2) elimination:** Linear hash functions (XOR + rotations) solved via Gaussian elimination over GF(2)
- **Padding oracle:** Byte-by-byte decryption by modifying previous block and testing padding validity
- **LFSR stream ciphers:** Berlekamp-Massey recovers feedback polynomial from 2L keystream bits; correlation attack breaks combined generators with biased combining functions
- **Galois LFSR tap recovery:** XOR known file header (PNG/PDF/ZIP) with ciphertext to get keystream; split into N-bit windows, compute `(state >> 1) XOR next_state` for LSB=1 transitions to directly recover tap mask. Autocorrelation sliding finds correct length. See [stream-ciphers.md](stream-ciphers.md#galois-lfsr-tap-recovery-via-autocorrelation-bsidessf-2026).
- **OFB with invertible RNG:** Known plaintext in any block leaks RNG state; if state transition is bijective, run RNG backwards to decrypt all blocks. See [modern-ciphers-2.md](modern-ciphers-2.md#ofb-mode-with-invertible-rng-backward-decryption-bsidessf-2026).
- **Weak key derivation (public key hash XOR):** AES key derived from `SHA256(public_key) XOR seed` is fully recoverable without private key; "hybrid" RSA+AES provides no security. See [modern-ciphers-2.md](modern-ciphers-2.md#weak-key-derivation-via-public-key-hash-xor-bsidessf-2026).
- **HMAC-CRC linearity:** CRC is linear over GF(2), so HMAC-CRC key is recoverable from a single message-MAC pair via polynomial arithmetic. See [modern-ciphers-2.md](modern-ciphers-2.md#hmac-crc-linearity-attack-boston-key-party-2016).
- **DES weak keys in OFB:** 4 DES weak keys make encryption self-inverse; OFB keystream cycles with period 2, reducing to 16-byte repeating XOR. See [modern-ciphers-2.md](modern-ciphers-2.md#des-weak-keys-in-ofb-mode-boston-key-party-2016).
- **Square attack (reduced-round AES):** 4-round AES broken by integral cryptanalysis: 256-plaintext lambda set, guess last round key bytes via XOR-sum = 0 distinguisher. See [modern-ciphers-2.md](modern-ciphers-2.md#square-attack-on-reduced-round-aes-0ctf-2016).
- **AES-GCM nonce reuse (forbidden attack):** Same nonce = CTR keystream reuse + GHASH authentication key recovery via polynomial factoring over GF(2^128). Tool: `nonce-disrespect`. See [modern-ciphers.md](modern-ciphers.md#aes-gcm-nonce-reuse-forbidden-attack).
- **SRP protocol bypass:** Send `A = 0` or `A = n` to force shared secret to 0, bypassing password verification entirely. See [modern-ciphers-2.md](modern-ciphers-2.md#srp-secure-remote-password-protocol-bypass-via-modular-arithmetic-asis-ctf-finals-2016).
- **Modified AES S-Box brute force:** Custom S-Box with only 16 unique outputs reduces key entropy; brute-force feasible key bytes per round. See [modern-ciphers-2.md](modern-ciphers-2.md#modified-aes-s-box-brute-force-recovery-h4ckit-ctf-2016).
- **Rabin LSB parity oracle:** Rabin ciphertext `c = m^2 mod n` with LSB oracle enables binary search plaintext recovery in `log2(n)` queries via multiplicative homomorphism (`c * 4 mod n` doubles plaintext). See [modern-ciphers-2.md](modern-ciphers-2.md#rabin-cryptosystem-lsb-parity-oracle-plaidctf-2016).
- **Noisy RSA LSB oracle error correction:** When LSB oracle has sporadic errors, run standard attack then inspect output charset. Flip oracle results at error positions to correct remaining decryption. See [modern-ciphers-2.md](modern-ciphers-2.md#noisy-rsa-lsb-oracle-with-post-hoc-error-correction-sharifctf-7-2016).
- **PBKDF2 pre-hash bypass:** HMAC pre-hashes keys > 64 bytes (SHA-1/SHA-256 block size). Login with `SHA1(password)` instead of `password` when original exceeds 64 bytes. See [modern-ciphers-2.md](modern-ciphers-2.md#pbkdf2-pre-hash-bypass-for-long-passwords-backdoorctf-2016).
- **MD5 multi-collision (fastcol):** Chain `fastcol` runs to produce 2^k files with identical MD5. Merkle-Damgard composition: collisions propagate through appended suffixes. See [modern-ciphers-2.md](modern-ciphers-2.md#md5-multi-collision-via-fastcol-backdoorctf-2016).
- **Custom hash state reversal:** When iterative hash leaks intermediate states, isolate per-block hash values by inverting the state update equation, then brute-force each 4-byte block independently. See [modern-ciphers-2.md](modern-ciphers-2.md#custom-hash-state-reversal-via-known-intermediates-backdoorctf-2016).
- **CRC32 brute-force (small payloads):** ZIP CRC32 headers are unencrypted; brute-force content of small files (≤ 6 bytes) by checking all printable strings against stored CRC32. See [modern-ciphers-2.md](modern-ciphers-2.md#crc32-brute-force-for-small-payloads-backdoorctf-2016).

See [modern-ciphers.md](modern-ciphers.md) and [modern-ciphers-2.md](modern-ciphers-2.md) for full code examples.

## RSA Attacks

- **Small e with small message:** Take eth root
- **Common modulus:** Extended GCD attack
- **Wiener's attack:** Small d
- **Fermat factorization:** p and q close together
- **Pollard's p-1:** Smooth p-1
- **Hastad's broadcast:** Same message, multiple e=3 encryptions
- **Consecutive primes:** q = next_prime(p); find first prime below sqrt(N)
- **Multi-prime:** Factor N with sympy; compute phi from all factors
- **Restricted-digit primes:** Digit-by-digit factoring from LSB with modular pruning
- **Coppersmith structured primes:** Partially known prime; `f.small_roots()` in SageMath
- **Manger oracle (simplified):** Phase 1 doubling + phase 2 binary search; ~128 queries for 64-bit key
- **Manger on RSA-OAEP (timing):** Python `or` short-circuit skips expensive PBKDF2 when Y != 0, creating fast/slow timing oracle. Full 3-step attack (~1024 iterations for 1024-bit RSA). Calibrate timing bounds with known-fast/known-slow samples.
- **Polynomial hash (trivial root):** `g(0) = 0` for polynomial hash; craft suffix for `msg = 0 (mod P)`, signature = 0
- **Polynomial CRT in GF(2)[x]:** Collect ~20 remainders `r = flag mod f`, filter coprime, CRT combine
- **Affine over composite modulus:** CRT in each prime factor field; Gauss-Jordan per prime
- **RSA p=q validation bypass:** Set `p=q` so server computes wrong `phi=(p-1)^2` instead of `p*(p-1)`; test decryption fails, leaking ciphertext
- **RSA cube root CRT (gcd(e,phi)>1):** When all primes ≡ 1 mod e, compute eth roots per-prime via `nthroot_mod`, enumerate CRT combinations (3^k feasible for small k)
- **Factoring from phi(n) multiple:** Any multiple of `phi(n)` (e.g., `e*d-1`) enables factoring via Miller-Rabin square root technique; succeeds with prob ≥ 1/2 per attempt
- **Weak keygen via base representation:** Primes `p = kp*B + tp` with small kp create mixed-radix structure in n; brute-force kp*kq (2^24) to factor
- **RSA with gcd(e,phi)>1 (exponent reduction):** Reduce `e' = e/g`, compute `d' = e'^(-1) mod phi`, partial decrypt to `m^g`, then take g-th root over integers
- **RSA partial key recovery (dp/dq/qinv):** CRT exponents from partial PEM leak allow O(e) prime recovery: iterate k, check if `(dp*e-1)/k+1` is prime. See [rsa-attacks-2.md](rsa-attacks-2.md#rsa-partial-key-recovery-from-dp-dq-qinv-0ctf-2016).
- **RSA-CRT fault attack:** Single faulty CRT signature leaks factor via `gcd(s^e - m, n)` (Bellcore attack). See [rsa-attacks-2.md](rsa-attacks-2.md#rsa-crt-fault-attack-bit-flip-recovery-csaw-ctf-2016).
- **RSA homomorphic decryption bypass:** Multiplicative homomorphism lets you decrypt `c` by querying oracle with `c * r^e mod n`, then dividing result by `r`. See [rsa-attacks-2.md](rsa-attacks-2.md#rsa-homomorphic-decryption-oracle-bypass-ectf-2016).
- **RSA small prime CRT decomposition:** When `n` has many small prime factors, factor with trial division, solve `m mod p_i` per prime, CRT combine. See [rsa-attacks-2.md](rsa-attacks-2.md#rsa-with-small-prime-factors-and-crt-decomposition-hack-the-vote-2016).
- **Hastad broadcast with linear padding (Coppersmith):** When each of `e` recipients applies a known affine transform `a_i*m+b_i` before encryption, CRT + Coppersmith small_roots recovers `m`. See [rsa-attacks.md](rsa-attacks.md#hastad-broadcast-attack-with-linear-padding----coppersmith-plaidctf-2017).
- **RSA Montgomery reduction timing attack:** Leaked extra-subtraction counts in Montgomery multiplication reveal private key bits MSB-to-LSB via statistical correlation. See [rsa-attacks-2.md](rsa-attacks-2.md#rsa-timing-attack-on-montgomery-reduction-def-con-2017).
- **Bleichenbacher low-exponent signature forgery:** With e=3, forge PKCS#1 v1.5 signatures by computing cube root of a value with correct padding prefix; trailing garbage absorbs the remainder. See [rsa-attacks-2.md](rsa-attacks-2.md#bleichenbacher-low-exponent-rsa-signature-forgery-google-ctf-2017).

See [rsa-attacks.md](rsa-attacks.md) and [advanced-math.md](advanced-math.md) for full code examples.

## Elliptic Curve Attacks

- **Small subgroup:** Check curve order for small factors; Pohlig-Hellman + CRT
- **Invalid curve:** Send points on weaker curves if validation missing
- **Singular curves:** Discriminant = 0; DLP maps to additive/multiplicative group
- **Smart's attack:** Anomalous curves (order = p); p-adic lift solves DLP in O(1)
- **Baby-step giant-step (BSGS):** General DLP in O(sqrt(n)) time/space. Combined with Pohlig-Hellman for smooth-order groups (all factors of `p-1` or curve order are small). Sage: `discrete_log(Mod(h,p), Mod(g,p))`. See [advanced-math.md](advanced-math.md#baby-step-giant-step-for-general-dlp).
- **Fault injection:** Compare correct vs faulty output; recover key bit-by-bit
- **Clock group (x^2+y^2=1):** Order = p+1 (not p-1!); Pohlig-Hellman when p+1 is smooth
- **Isogenies:** Graph traversal via modular polynomials; pathfinding via LCA
- **ECDSA nonce reuse:** Same `r` in two signatures leaks nonce `k` and private key `d` via modular arithmetic. Check for repeated `r` values
- **Braid group DH:** Alexander polynomial is multiplicative under braid concatenation — Eve computes shared secret from public keys. See [exotic-crypto.md](exotic-crypto.md#braid-group-dh-alexander-polynomial-multiplicativity-dicectf-2026)
- **Ed25519 torsion side channel:** Cofactor h=8 leaks secret scalar bits when key derivation uses `key = master * uid mod l`; query powers of 2, check y-coordinate consistency
- **Tropical semiring residuation:** Tropical (min-plus) DH is broken — residual `b* = max(Mb[i] - M[i][j])` recovers shared secret directly from public matrices
- **FPE Feistel brute-force:** Format-preserving encryption with 16-bit round key is brute-forceable; remaining affine GF(2) mixing layer solved via Gaussian elimination. See [exotic-crypto.md](exotic-crypto.md#format-preserving-encryption-feistel-brute-force-bsidessf-2026)
- **Icosahedral symmetry cipher:** Dodecahedron face permutations form order-120 group; build lookup table of all permutations via API probing, match visible face patterns. See [exotic-crypto.md](exotic-crypto.md#icosahedral-symmetry-group-cipher-bsidessf-2026)
- **Goldwasser-Micali replication oracle:** GM encrypts one bit per ciphertext; replaying a single ciphertext value N times as an N-bit key forces all-zero or all-one key, distinguishable via hash oracle. 128 queries recover full AES key. See [exotic-crypto.md](exotic-crypto.md#goldwasser-micali-ciphertext-replication-oracle-bsidessf-2026)
- **DSA nonce reuse:** Same r in two DSA signatures leaks private key via same formula as ECDSA nonce reuse. See [ecc-attacks.md](ecc-attacks.md#dsa-nonce-reuse-for-private-key-recovery-volgactf-2016).
- **DSA limited k brute force:** When nonce `k` is small (e.g., 20-bit), brute-force all `k` values and check which yields the known `r`. See [ecc-attacks.md](ecc-attacks.md#dsa-limited-k-value-brute-force-asis-ctf-finals-2016).
- **ECC shared prime GCD:** Multiple ECC curves sharing a prime factor in their modulus; `gcd(n1, n2)` reveals the shared prime. See [ecc-attacks.md](ecc-attacks.md#ecc-shared-prime-factor-via-gcd-asis-ctf-finals-2016).
- **DSA key recovery via MD5 collision on k-generation:** When nonce `k` derives from `MD5(prefix+counter)`, use `fastcoll` to produce MD5 prefix collision forcing nonce reuse, then standard private key recovery. See [ecc-attacks.md](ecc-attacks.md#dsa-key-recovery-via-md5-collision-on-k-generation-confidence-ctf-2017).
- **BB-84 QKD MITM:** Simulated BB-84 without authenticated classical channels allows full MITM -- independently negotiate keys with both parties, force constant value to one side. See [exotic-crypto.md](exotic-crypto.md#bb-84-quantum-key-distribution-mitm-attack-plaidctf-2017).

See [ecc-attacks.md](ecc-attacks.md), [advanced-math.md](advanced-math.md), and [exotic-crypto.md](exotic-crypto.md) for full code examples.

## Lattice / LWE Attacks

- **Quick triage:** If the challenge gives modular linear equations plus a promise that the hidden quantity is small, sparse, biased, or only partially leaked, treat it as a lattice candidate first. See [lattice-and-lwe.md](lattice-and-lwe.md#quick-triage-is-this-a-lattice-problem).
- **LLL / BKZ / Babai:** Start with LLL, move to BKZ when LLL almost works, and use Babai after reduction for approximate CVP. See [lattice-and-lwe.md](lattice-and-lwe.md#core-tools-lll-bkz-babai-cvp-svp-asis-ctf-finals-2015-ctfzone-2017).
- **HNP from partial nonce leakage:** Partial or biased ECDSA/Schnorr nonces often reduce to Hidden Number Problem lattices; normalize equations, isolate bounded error, reduce, then brute-force the last few bits if needed. See [lattice-and-lwe.md](lattice-and-lwe.md#hidden-number-problem-hnp-partial-nonce-biased-nonce-nullcon-hackim-2020-ledger-donjon-ctf-2020).
- **Truncated LCG state recovery:** High-bit or low-bit leakage from affine recurrences is often just HNP in disguise; write each state as `observed * 2^t + hidden` and solve for the small hidden corrections. See [lattice-and-lwe.md](lattice-and-lwe.md#lcg-and-truncated-output-as-a-lattice-problem-x-mas-ctf-2018-fwordctf-2020).
- **LWE via CVP (Babai):** Construct lattice from `[q*I | 0; A^T | I]`, use fpylll CVP.babai to find closest vector, project to ternary {-1,0,1}. Watch for endianness mismatches between server description and actual encoding.
- **Ring-LWE / Module-LWE recognition:** Polynomial or negacyclic structure often looks scary but many CTFs weaken it with tiny coefficients, buggy representations, or enough leakage to flatten back into plain LWE. See [lattice-and-lwe.md](lattice-and-lwe.md#ring-lwe-module-lwe-recognition-notes-plaidctf-2016-dicectf-2022).
- **Orthogonal lattices:** Hidden subset or hidden subspace problems may need you to recover an orthogonal lattice first, then reconstruct the actual binary or short basis from its complement. See [lattice-and-lwe.md](lattice-and-lwe.md#orthogonal-lattices-hssp-ahssp-style-recovery-zer0pts-ctf-2022).
- **LLL for approximate GCD:** Short vector in lattice reveals hidden factors
- **Subset sum / knapsack:** Binary knapsack and low-density subset-sum instances are still classic lattice territory; build the standard basis and look for a reduced row with a zero final coordinate. See [lattice-and-lwe.md](lattice-and-lwe.md#subset-sum-knapsack-via-lattice-reduction-hitcon-ctf-2017-backdoorctf-2023).
- **Multi-layer challenges:** Geometry → subspace recovery → LWE → AES-GCM decryption chain

See [advanced-math.md](advanced-math.md) for worked LWE solving code and [lattice-and-lwe.md](lattice-and-lwe.md) for attack selection, embeddings, and failure-mode triage.

## ZKP & Constraint Solving

- **ZKP cheating:** For impossible problems (3-coloring K4), find hash collisions or predict PRNG salts
- **Graph 3-coloring:** `nx.coloring.greedy_color(G, strategy='saturation_largest_first')`
- **Z3 solver:** BitVec for bit-level, Int for arbitrary precision; BPF/SECCOMP filter solving
- **Garbled circuits (free XOR):** XOR three truth table entries to recover global delta
- **Bigram substitution:** OR-Tools CP-SAT with automaton constraint for known plaintext structure
- **Trigram decomposition:** Positions mod n form independent monoalphabetic ciphers
- **Shamir SSS (deterministic coefficients):** One share + seeded RNG = univariate equation in secret
- **Race condition (TOCTOU):** Synchronized concurrent requests bypass `counter < N` checks
- **Groth16 broken setup (delta==gamma):** Trivially forge: A=alpha, B=beta, C=-vk_x. Always check verifier constants first
- **Groth16 proof replay:** Unconstrained nullifier + no tracking = infinite replays from setup tx
- **DV-SNARG forgery:** With verifier oracle access, learn secret v values from unconstrained pairs, forge via CRS entry cancellation
- **Shamir SSS reused polynomial coefficients:** When same random coefficients are used for every secret byte, subtracting shares cancels all randomness, leaving only plaintext differences. See [zkp-and-advanced.md](zkp-and-advanced.md#shamir-secret-sharing-with-reused-polynomial-coefficients-polictf-2017).

See [zkp-and-advanced.md](zkp-and-advanced.md) for full code examples and solver patterns.

## Modern Cipher Attacks (Additional)

- **Affine over composite modulus:** `c = A*x+b (mod M)`, M composite (e.g., 65=5*13). Chosen-plaintext recovery via one-hot vectors, CRT inversion per prime factor. See [modern-ciphers.md](modern-ciphers.md#affine-cipher-over-composite-modulus-nullcon-2026).
- **Custom linear MAC forgery:** XOR-based signature linear in secret blocks. Recover secrets from ~5 known pairs, forge for target. See [modern-ciphers.md](modern-ciphers.md#custom-linear-mac-forgery-nullcon-2026).
- **Manger oracle (RSA threshold):** RSA multiplicative + binary search on `m*s < 2^128`. ~128 queries to recover AES key.
- **AES key recovery via byte-by-byte zeroing oracle:** Integer overflow in key slot indexing allows selective byte zeroing; brute-force one byte at a time (256 per byte, 4096 total). See [modern-ciphers.md](modern-ciphers.md#aes-key-recovery-via-byte-by-byte-zeroing-oracle-confidence-ctf-2017).

## Introspective CRC via GF(2) Linear Algebra

Self-referential CRC: find ASCII string whose CRC equals itself. CRC is linear over GF(2), so the constraint becomes a solvable linear system. Free variables chosen for printable ASCII range. See [advanced-math.md](advanced-math.md#introspective-crc-via-gf2-linear-algebra-google-ctf-2017).

## CBC Padding Oracle Attack

Server reveals valid/invalid padding → decrypt any CBC ciphertext without key. ~4096 queries per 16-byte block. Use PadBuster or `padding-oracle` Python library. See [modern-ciphers.md](modern-ciphers.md#cbc-padding-oracle-attack).

## Bleichenbacher RSA Padding Oracle (ROBOT)

RSA PKCS#1 v1.5 padding validation oracle → adaptive chosen-ciphertext plaintext recovery. ~10K queries for RSA-2048. Affects TLS implementations via timing. See [modern-ciphers.md](modern-ciphers.md#bleichenbacher-pkcs1-v15-rsa-padding-oracle).

## Birthday Attack / Meet-in-the-Middle

n-bit hash collision in ~2^(n/2) attempts. Meet-in-the-middle breaks double encryption in O(2^k) instead of O(2^(2k)). See [modern-ciphers.md](modern-ciphers.md#birthday-attack-meet-in-the-middle).

- **Sponge hash MITM collision:** When sponge rate < state size, uncontrolled state bytes enable MITM — precompute forward encryptions keyed on uncontrolled bytes, search backward for matches. Reduces 2^48 to 2^24. See [modern-ciphers-2.md](modern-ciphers-2.md#sponge-hash-collision-via-meet-in-the-middle-on-partial-state-bkp-2017).

## CRC32 Collision-Based Signature Forgery (iCTF 2013)

CRC32 is linear — append 4 chosen bytes to force any target CRC32, forging `CRC32(msg || secret)` signatures without the secret. See [modern-ciphers.md](modern-ciphers.md#crc32-collision-based-signature-forgery-ictf-2013).

## Blum-Goldwasser Bit-Extension Oracle (PlaidCTF 2013)

Extend ciphertext by one bit per oracle query to leak plaintext via parity. Manipulate BBS squaring sequence to produce valid extended ciphertexts. See [modern-ciphers-2.md](modern-ciphers-2.md#blum-goldwasser-bit-extension-oracle-plaidctf-2013).

## Hash Length Extension Attack

Exploits Merkle-Damgard hashes (`hash(SECRET || user_data)`) — append arbitrary data and compute valid hash without knowing the secret. Use `hashpump` or `hashpumpy`. See [modern-ciphers-2.md](modern-ciphers-2.md#hash-length-extension-attack-plaidctf-2014).

## Compression Oracle (CRIME-Style)

Compression before encryption leaks plaintext via ciphertext length changes. Send chosen plaintexts; matching n-grams compress shorter. Same class as CRIME/BREACH. See [modern-ciphers-2.md](modern-ciphers-2.md#compression-oracle-crime-style-attack-bctf-2015).

## RC4 Second-Byte Bias

RC4's second output byte is biased toward `0x00` (probability 1/128 vs 1/256). Distinguishes RC4 from random with ~2048 samples. See [stream-ciphers.md](stream-ciphers.md#rc4-second-byte-bias-distinguisher-hackover-ctf-2015).

## RSA Multiplicative Homomorphism Signature Forgery

Unpadded RSA: `S(a) * S(b) mod n = S(a*b) mod n`. If oracle blacklists target message, sign its factors and multiply. See [rsa-attacks-2.md](rsa-attacks-2.md#rsa-signature-forgery-via-multiplicative-homomorphism-mma-ctf-2015).

## Common Patterns

- **RSA basics:** `phi = (p-1)*(q-1)`, `d = inverse(e, phi)`, `m = pow(c, d, n)`. See [rsa-attacks.md](rsa-attacks.md) for full examples.
- **XOR:** `from pwn import xor; xor(ct, key)`. See [classic-ciphers.md](classic-ciphers.md) for XOR variants.

## C srand/rand Prediction via ctypes (L3akCTF 2024, MireaCTF)

**Pattern:** Binary uses `srand(time(NULL))` + `rand()` for keys/XOR masks. Python's `random` module uses a different PRNG. Use `ctypes.CDLL('./libc.so.6')` to call C's `srand(int(time()))` and `rand()` directly, reproducing the exact sequence. See [prng.md](prng.md#c-srandrand-synchronization-via-python-ctypes) for XOR decryption examples and timing tips.

## V8 XorShift128+ (Math.random) State Recovery

**Pattern:** V8 JavaScript engine uses xs128p PRNG for `Math.random()`. Given 5-10 consecutive outputs of `Math.floor(CONST * Math.random())`, recover internal state (state0, state1) with Z3 QF_BV solver and predict future values. Values must be reversed (LIFO cache). Tool: `d0nutptr/v8_rand_buster`. See [prng.md](prng.md#v8-xorshift128-state-recovery-mathrandom-prediction).

## MT State Recovery from Float Outputs (PHD CTF Quals 2012)

**Pattern:** Server exposes `random.random()` floats. Standard untemper needs 624 × 32-bit integers, but floats yield only ~8 usable bits each. A precomputed GF(2) magic matrix (`not_random` library) recovers the full MT state from 3360+ float observations. Use to predict password reset tokens, session IDs, or CSRF tokens derived from `random.random()`. See [prng.md](prng.md#mt-state-recovery-from-randomrandom-floats-via-gf2-matrix-phd-ctf-quals-2012).

## Chaotic PRNG (Logistic Map)

- **Logistic map:** `x = r * x * (1 - x)`, `r ≈ 3.99-4.0`; seed recovery by brute-forcing high-precision decimals
- **Keystream:** `struct.pack("<f", x)` per iteration; XOR with ciphertext

See [prng.md](prng.md#logistic-map-chaotic-prng-seed-recovery-bypass-ctf-2025) for full code.

## SPN S-box Intersection Attack

Divide-and-conquer SPN key recovery: attack each S-box position independently, intersect valid key candidates across multiple plaintext-ciphertext pairs. Reduces exponential key space to independent sub-key searches. See [modern-ciphers-2.md](modern-ciphers-2.md#spn-cipher-partial-key-recovery-via-s-box-intersection-sharifctf-7-2016).

## Useful Tools

- **Python:** `pip install pycryptodome z3-solver sympy gmpy2`
- **SageMath:** `sage -python script.py` (required for ECC, Coppersmith, lattice attacks)
- **RsaCtfTool:** `python RsaCtfTool.py -n <n> -e <e> --uncipher <c>` — automated RSA attack suite (tries Wiener, Hastad, Fermat, Pollard, and many more)
- **quipqiup.com:** Automated substitution cipher solver (frequency + word pattern analysis)


---


# advanced-math

# CTF Crypto - Advanced Mathematical Attacks

## Table of Contents
- [Elliptic Curve Isogenies](#elliptic-curve-isogenies)
- [Pohlig-Hellman Attack (Weak ECC)](#pohlig-hellman-attack-weak-ecc)
- [Baby-Step Giant-Step for General DLP](#baby-step-giant-step-for-general-dlp)
- [LLL Algorithm for Approximate GCD](#lll-algorithm-for-approximate-gcd)
- [Merkle-Hellman Knapsack Cryptosystem via LLL (ASIS 2014)](#merkle-hellman-knapsack-cryptosystem-via-lll-asis-2014)
- [Coppersmith's Method (Close Private Keys)](#coppersmiths-method-close-private-keys)
- [Coppersmith's Method (Structured Primes, LACTF 2026)](#coppersmiths-method-structured-primes-lactf-2026)
- [Clock Group (x^2+y^2=1 mod p) DLP (LACTF 2026)](#clock-group-x2y21-mod-p-dlp-lactf-2026)
- [Quaternion RSA](#quaternion-rsa)
- [Polynomial Arithmetic in GF(2)[x]](#polynomial-arithmetic-in-gf2x)
- [RSA Signing Bug](#rsa-signing-bug)
- [Non-Permutation S-box Collision Attack (Nullcon 2026)](#non-permutation-s-box-collision-attack-nullcon-2026)
- [Polynomial CRT in GF(2)[x] (Nullcon 2026)](#polynomial-crt-in-gf2x-nullcon-2026)
- [Manger's RSA Padding Oracle Attack (Nullcon 2026)](#mangers-rsa-padding-oracle-attack-nullcon-2026)
- [LWE Lattice Attack via CVP (EHAX 2026)](#lwe-lattice-attack-via-cvp-ehax-2026)
- [Affine Cipher over Non-Prime Modulus (Nullcon 2026)](#affine-cipher-over-non-prime-modulus-nullcon-2026)
- [Introspective CRC via GF(2) Linear Algebra (Google CTF 2017)](#introspective-crc-via-gf2-linear-algebra-google-ctf-2017)
- [Baby-Step Giant-Step for Sparse/Low Hamming Weight Exponents (SEC-T CTF 2017)](#baby-step-giant-step-for-sparselow-hamming-weight-exponents-sec-t-ctf-2017)

---

## Elliptic Curve Isogenies

Isogeny-based crypto challenges are often **graph traversal problems in disguise**:

**Key concepts:**
- j-invariant uniquely identifies curve isomorphism class
- Curves connected by isogenies form a graph (often tree-like)
- Degree-2 isogenies: each node has ~3 neighbors (2 children + 1 parent)

**Modular polynomial approach:**
- Connected j-invariants j₁, j₂ satisfy Φ₂(j₁, j₂) = 0
- Find neighbors by computing roots of Φ₂(j, Y) in the finite field
- Much faster than computing actual isogenies

**Pathfinding in isogeny graphs:**
```python
# Height estimation via random walks to leaves
def estimate_height(j, neighbors_func, trials=100):
    min_depth = float('inf')
    for _ in range(trials):
        depth, curr = 0, j
        while True:
            nbrs = neighbors_func(curr)
            if len(nbrs) <= 1:  # leaf node
                break
            curr = random.choice(nbrs)
            depth += 1
        min_depth = min(min_depth, depth)
    return min_depth

# Find path between two nodes via LCA
def find_path(start, end):
    # Ascend from both nodes tracking heights
    # Find least common ancestor
    # Concatenate: path_up(start) + reversed(path_up(end))
```

**Complex multiplication (CM) curves:**
- Discriminant D = f² · D_K where D_K is fundamental discriminant
- Conductor f determines tree depth
- Look for special discriminants: -163, -67, -43, etc. (class number 1)

## Pohlig-Hellman Attack (Weak ECC)

For elliptic curves with smooth order (many small prime factors):

```python
from sage.all import *

# Factor curve order
E = EllipticCurve(GF(p), [a, b])
n = E.order()
factors = factor(n)

# Solve DLP in each small subgroup
partial_logs = []
for (prime, exp) in factors:
    # Compute subgroup generator
    cofactor = n // (prime ** exp)
    G_sub = cofactor * G
    P_sub = cofactor * P  # Target point

    # Solve small DLP
    d_sub = discrete_log(P_sub, G_sub, ord=prime**exp)
    partial_logs.append((d_sub, prime**exp))

# Combine with CRT
from sympy.ntheory.modular import crt
moduli = [m for (_, m) in partial_logs]
residues = [r for (r, _) in partial_logs]
private_key, _ = crt(moduli, residues)
```

## Baby-Step Giant-Step for General DLP

**Pattern:** Compute discrete logarithm `x` where `g^x = h (mod p)` in O(sqrt(n)) time and space, where n is the group order. Works for any cyclic group — multiplicative groups mod p, elliptic curves, or abstract groups. Combined with Pohlig-Hellman for smooth-order groups, solves DLP when `p-1` (or group order) has only small prime factors.

**Baby-step giant-step algorithm:**

```python
from math import isqrt

def bsgs(g, h, p, order=None):
    """Baby-step giant-step: find x such that g^x = h (mod p).

    Time/space: O(sqrt(order)). For subgroups, pass the subgroup order.
    """
    if order is None:
        order = p - 1
    m = isqrt(order) + 1

    # Baby step: build table of g^j for j in [0, m)
    table = {}
    power = 1
    for j in range(m):
        table[power] = j
        power = (power * g) % p

    # Giant step: compute g^(-m), then check h * (g^(-m))^i
    factor = pow(g, -m, p)  # g^(-m) mod p
    gamma = h
    for i in range(m):
        if gamma in table:
            return i * m + table[gamma]
        gamma = (gamma * factor) % p
    return None  # No solution found (order was wrong)

# Example: ElGamal with smooth p-1 (MMA CTF 2015 "Alicegame")
# p-1 = 2 * 3^4 * 5 * 13 * 397 * 34703 * ... (all small factors)
# Pohlig-Hellman: solve DLP in each prime-power subgroup, combine with CRT
```

**Full Pohlig-Hellman + BSGS pipeline:**

```python
from sympy.ntheory import factorint
from sympy.ntheory.modular import crt

def pohlig_hellman(g, h, p):
    """Solve g^x = h (mod p) when p-1 is smooth."""
    order = p - 1
    factors = factorint(order)  # {prime: exponent}

    residues = []
    moduli = []
    for prime, exp in factors.items():
        pe = prime ** exp
        # Project to subgroup of order prime^exp
        cofactor = order // pe
        gi = pow(g, cofactor, p)  # Generator of subgroup
        hi = pow(h, cofactor, p)  # Target in subgroup

        # Solve DLP in small subgroup via BSGS
        xi = bsgs(gi, hi, p, order=pe)
        if xi is None:
            return None
        residues.append(xi)
        moduli.append(pe)

    # Combine via CRT
    x, _ = crt(moduli, residues)
    assert pow(g, x, p) == h % p
    return x
```

**Key insight:** BSGS runs in O(sqrt(q)) for a subgroup of order q. Pohlig-Hellman decomposes the full DLP into subgroup DLPs. If `p-1 = q1^e1 * q2^e2 * ...` where all qi are small, the total cost is O(sum(sqrt(qi^ei))). A 1024-bit prime with smooth `p-1` (all factors under ~40 bits) is solvable in seconds. Sage's `discrete_log()` automatically applies Pohlig-Hellman + BSGS.

**When to recognize:**
- ElGamal, DSA, or Diffie-Hellman with a randomly generated prime — check if `p-1` is smooth: `factor(p-1)` in Sage
- ECC with smooth curve order — same approach, replace modular exponentiation with point multiplication
- Challenge generates new parameters on each connection — retry until you get a smooth prime
- Challenge description mentions "weak parameters" or uses suspiciously small primes

**Sage one-liner:** `discrete_log(Mod(h, p), Mod(g, p))` handles everything automatically.

**References:** MMA CTF 2015 "Alicegame", SEC-T CTF "Madlog", Crypto CTF 2021 "RoHaLd"

---

## LLL Algorithm for Approximate GCD

**Pattern (Grinch's Cryptological Defense):** Server gives hints `h_i = f * p_i + n_i` where f is the flag, p_i are small primes, n_i is small noise.

**Lattice construction:**
```python
from sage.all import *

# Collect 3 hints from server
# h_i = f * p_i + n_i (noise is small)
# Construct lattice where short vector reveals primes

M = matrix(ZZ, [
    [1, 0, 0, h1],
    [0, 1, 0, h2],
    [0, 0, 1, h3],
    [0, 0, 0, -1]  # Scaling factor
])

reduced = M.LLL()
# Short vector contains p1, p2, p3
# Recover f = (h1 - n1) / p1
```

## Merkle-Hellman Knapsack Cryptosystem via LLL (ASIS 2014)

The Merkle-Hellman knapsack is a broken asymmetric scheme. Given public key P = [p0, ..., pn-1] and ciphertext C (sum of selected public key elements), recover the binary plaintext vector:

```python
# Sage
nbit = len(pubKey)
A = Matrix(ZZ, nbit + 1, nbit + 1)

# Identity matrix in upper-left (tracks which elements are selected)
for i in range(nbit):
    A[i, i] = 1
    A[i, nbit] = pubKey[i]

# Target sum in bottom-right
A[nbit, nbit] = -int(encoded)

# LLL reduction finds short vector where last element is 0
res = A.LLL()

# Find row with last element == 0 and all others in {0, 1}
for row in res:
    if row[-1] == 0 and all(b in (0, 1) for b in row[:-1]):
        plaintext_bits = list(row[:-1])
        break
```

**Key insight:** The knapsack problem becomes easy when reformulated as a shortest vector problem. The LLL-reduced basis contains a row representing the binary plaintext when the last column is zero.

## Coppersmith's Method (Close Private Keys)

**Pattern (Duality of Key):** Two RSA key pairs with d1 ≈ d2 (small difference).

**Attack:**
```python
# From e1*d1 ≡ 1 mod φ and e2*d2 ≡ 1 mod φ:
# d2 - d1 ≡ (e1*e2)^(-1) * (e1 - e2) mod p

# Construct polynomial f(x) = (r - x) mod p where x = d2-d1
# Use Coppersmith small_roots() to find x

R.<x> = PolynomialRing(Zmod(N))
r = inverse_mod(e1*e2, N) * (e1 - e2) % N
f = r - x
roots = f.small_roots(X=2^128, beta=0.5)  # Adjust bounds
# x = d2 - d1, recover p from gcd(f(x), N)
```

## Coppersmith's Method (Structured Primes, LACTF 2026)

**Pattern (six-seven-again):** p = base + 10^k · x where base is fully known, x is small.

**Condition:** x < N^{1/e} for degree-e polynomial (≈ N^0.25 for linear).

**Attack:**
```python
# p = base + 10^k * x, so x ≡ -base * (10^k)^{-1} (mod p)
# Since p | N, construct polynomial with root x mod N
R.<x> = PolynomialRing(Zmod(N))
inv_10k = inverse_mod(10^k, N)
f = x + (base * inv_10k) % N  # Must be monic!
roots = f.small_roots(X=2^70, beta=0.5)
if roots:
    x_val = int(roots[0])
    p = base + 10^k * x_val
    q = N // p
```

**Key details:**
- Polynomial MUST be monic (leading coefficient 1)
- `beta=0.5` means we're looking for a factor ≥ N^0.5
- `X` parameter is upper bound on root size
- Works for any "partially known prime" pattern

## Clock Group (x^2+y^2=1 mod p) DLP (LACTF 2026)

**Pattern (the-clock):** Diffie-Hellman on the unit circle group.

**Group structure:**
```python
# Group law: (x1,y1) * (x2,y2) = (x1*y2 + y1*x2, y1*y2 - x1*x2)
# Identity: (0, 1)
# Inverse of (x, y): (-x, y)
# Group order: p + 1 (NOT p - 1!)

def clock_mul(P, Q, p):
    x1, y1 = P
    x2, y2 = Q
    return ((x1*y2 + y1*x2) % p, (y1*y2 - x1*x2) % p)

def clock_pow(P, n, p):
    result = (0, 1)  # identity
    base = P
    while n > 0:
        if n & 1:
            result = clock_mul(result, base, p)
        base = clock_mul(base, base, p)
        n >>= 1
    return result
```

**Recovering hidden prime p:**
```python
# Given points on the curve, p divides (x^2 + y^2 - 1)
from math import gcd
vals = [x**2 + y**2 - 1 for x, y in known_points]
p = reduce(gcd, vals)
# May need to remove small factors
```

**Pohlig-Hellman when p+1 is smooth:**
```python
order = p + 1
factors = factor(order)
# Standard Pohlig-Hellman in the clock group
# Solve d in each prime-power subgroup, CRT combine
```

**CRITICAL:** The order is p+1, isomorphic to norm-1 elements of GF(p²)*. This is different from multiplicative group (order p-1) and elliptic curves (order ≈ p).

## Quaternion RSA

**Pattern:** RSA encryption using Hamilton quaternion algebra over Z/nZ. The plaintext is embedded into quaternion components that are linear combinations of m, p, q, then the quaternion matrix is raised to power e mod n.

**Key structure:**
```python
# Quaternion q = a0 + a1*i + a2*j + a3*k
# Components are linear in m, p, q:
a0 = m
a1 = m + α1*p + β1*q  # e.g., m + 3p + 7q
a2 = m + α2*p + β2*q  # e.g., m + 11p + 13q
a3 = m + α3*p + β3*q  # e.g., m + 17p + 19q

# 4x4 matrix representation:
# Row 0: [a0, -a1, -a2, -a3]
# Row 1: [a1,  a0, -a3,  a2]
# Row 2: [a2,  a3,  a0, -a1]
# Row 3: [a3, -a2,  a1,  a0]

# Ciphertext = first row of matrix^e mod n
```

**Critical property:** For quaternion `q = s + v` (scalar + vector), `q^k = s_k + t_k*v` — the vector part stays **proportional** under exponentiation. This means the ratios of imaginary components are preserved:

`c1 : c2 : c3 = a1 : a2 : a3 (mod n)`

**Factoring n (the attack):**

```python
import math

# Extract quaternion components from ciphertext row [ct0, ct1, ct2, ct3]
# Row 0 = [c0, -c1, -c2, -c3], so negate last 3:
c0, c1, c2, c3 = ct[0], (-ct[1]) % n, (-ct[2]) % n, (-ct[3]) % n

# From ratio preservation: c1*a2 = c2*a1 (mod n), c1*a3 = c3*a1 (mod n)
# Substituting a_i = m + αi*p + βi*q and eliminating m between two equations:
# Result: A*p + B*q ≡ 0 (mod n=pq) => q|A, p|B

# For components a1=m+α1p+β1q, a2=m+α2p+β2q, a3=m+α3p+β3q:
# Eliminate m from (c1*a2=c2*a1) and (c1*a3=c3*a1):
A = (-(α1*c1 - α2*c2)*(c1-c3) + (α1*c1 - α3*c3)*(c1-c2)) % n
B = (-(β1*c1 - β2*c2)*(c1-c3) + (β1*c1 - β3*c3)*(c1-c2)) % n

# More concretely for coefficients [3,7], [11,13], [17,19]:
A = (-(11*c1-3*c2)*(c1-c3) + (17*c1-3*c3)*(c1-c2)) % n
B = (-(13*c1-7*c2)*(c1-c3) + (19*c1-7*c3)*(c1-c2)) % n

q_factor = math.gcd(A, n)  # gives q
p_factor = math.gcd(B, n)  # gives p
```

**Decryption after factoring:**

Over F_p, the quaternion algebra H_p ≅ M_2(F_p) (Wedderburn theorem), so the quaternion's multiplicative order divides p²-1. Decrypt using:

```python
# Group order for quaternions over F_p divides p²-1
d_p = pow(e, -1, p**2 - 1)
d_q = pow(e, -1, q**2 - 1)

# Decrypt mod p and mod q separately, then CRT
enc_mod_p = [[x % p for x in row] for row in enc_matrix]
enc_mod_q = [[x % q for x in row] for row in enc_matrix]
dec_p = matrix_pow(enc_mod_p, d_p, p)
dec_q = matrix_pow(enc_mod_q, d_q, q)

# CRT combine: dec_matrix[0][0] = m (the flag)
m = CRT(dec_p[0][0], dec_q[0][0], p, q)
flag = long_to_bytes(m)
```

**Why it works:** The "reduced dimension" is that 4D quaternion exponentiation reduces to a 2D recurrence (scalar + magnitude of vector), and the direction of the vector part is invariant. This leaks the ratio a1:a2:a3 directly from the ciphertext, enabling factorization.

**References:** SECCON CTF 2023 "RSA 4.0", 0xL4ugh CTF "Reduced Dimension"

---

## Polynomial Arithmetic in GF(2)[x]

**Key operations for CTF crypto:**
```python
def poly_add(a, b):
    """Addition in GF(2)[x] = XOR of coefficient integers."""
    return a ^ b

def poly_mul(a, b):
    """Carry-less multiplication in GF(2)[x]."""
    result = 0
    while b:
        if b & 1:
            result ^= a
        a <<= 1
        b >>= 1
    return result

def poly_divmod(a, b):
    """Division with remainder in GF(2)[x]."""
    if b == 0:
        raise ZeroDivisionError
    deg_a, deg_b = a.bit_length() - 1, b.bit_length() - 1
    q = 0
    while deg_a >= deg_b and a:
        shift = deg_a - deg_b
        q ^= (1 << shift)
        a ^= (b << shift)
        deg_a = a.bit_length() - 1
    return q, a  # quotient, remainder
```

**Applications:** CRT in GF(2)[x] for recovering secrets from polynomial remainders, Reed-Solomon-like error correction.

---

## RSA Signing Bug

**Vulnerability:** Using wrong exponent for signing
- Correct: `sign = m^d mod n` (private exponent)
- Bug: `sign = m^e mod n` (public exponent)

**Exploitation:**
```python
# If signature is m^e mod n, we can "encrypt" to verify
# and compute e-th root to forge signatures
from sympy import integer_nthroot

# For small e (e.g., 3), take e-th root if m^e < n
forged_sig, exact = integer_nthroot(message, e)
if exact:
    print(f"Forged signature: {forged_sig}")
```

---

## Non-Permutation S-box Collision Attack (Nullcon 2026)

**Detection:** Check if S-box is a permutation:
```python
sbox = [...]  # 256 entries
if len(set(sbox)) < 256:
    from collections import Counter
    counts = Counter(sbox)
    for val, cnt in counts.items():
        if cnt > 1:
            colliders = [i for i in range(256) if sbox[i] == val]
            delta = colliders[0] ^ colliders[1]
            print(f"S[{hex(colliders[0])}] = S[{hex(colliders[1])}] = {hex(val)}, delta = {hex(delta)}")
```

**Attack:** For each key byte position k (0-15):
1. Try all 256 values v: encrypt two plaintexts differing by `delta` at position k
2. When `ct1 == ct2`: S-box input at position k was in the collision set `{c0, c1}`
3. Deduce: `key[k] = v ^ round_const` OR `key[k] = v ^ round_const ^ delta`
4. 2-way ambiguity per byte -> 2^16 = 65,536 candidates, brute-force locally

**Total oracle queries:** 16 x 256 + 1 = 4,097 (reference ciphertext + probes).

**Key lessons:**
- SAT/SMT solvers time out on 15+ rounds of symbolic AES even with simplified S-box
- Integral/square attacks fail because non-permutation S-box breaks balance property
- Always check S-box for non-permutation FIRST before attempting complex cryptanalysis

---

## Polynomial CRT in GF(2)[x] (Nullcon 2026)

**Pattern:** Server gives `r = flag mod f` where `f` is a random polynomial over GF(2).

**Attack:** Chinese Remainder Theorem in polynomial ring GF(2)[x]:
1. Collect ~20 pairs `(r_i, f_i)` from server (each `f_i` is ~32-bit random polynomial)
2. Filter for coprime pairs using polynomial GCD
3. Apply CRT to combine: `flag = r_i (mod f_i)` for all i
4. With ~13-20 coprime 32-bit moduli (>= 400 bits combined), flag is unique

```python
def poly_crt(remainders, moduli):
    """CRT in GF(2)[x]: combine (r_i, f_i) pairs."""
    result, mod = remainders[0], moduli[0]
    for i in range(1, len(remainders)):
        g, s, t = poly_xgcd(mod, moduli[i])
        combined_mod = poly_mul(mod, moduli[i])
        result = poly_add(poly_mul(poly_mul(remainders[i], s), mod),
                         poly_mul(poly_mul(result, t), moduli[i]))
        result = poly_mod(result, combined_mod)
        mod = combined_mod
    return result, mod
```

---

## Manger's RSA Padding Oracle Attack (Nullcon 2026)

**Setup:**
- Key `k < 2^64` (small), RSA modulus `n` is large (1337+ bits)
- Oracle: "invalid padding" = `decrypt < threshold`, "error" = `decrypt >= threshold`
- No modular wrap-around because `k << n`

**Attack (simplified Manger's):**
```python
# Phase 1: Find f1 where k * f1 >= threshold
f1 = 1
while oracle(encrypt(f1)) == "below":  # multiply ciphertext by f1^e mod n
    f1 *= 2
# f1/2 < threshold/k <= f1, so k is in [threshold/f1, threshold/(f1/2)]

# Phase 2: Binary search for exact key
lo, hi = 0, threshold
while lo < hi:
    mid = (lo + hi) // 2
    f_test = ceil(threshold, mid + 1)  # f such that k*f >= threshold iff k > mid
    if oracle(encrypt(f_test)) == "above":
        hi = mid
    else:
        lo = mid + 1
key = lo  # ~64 queries for 64-bit key
```

**Total queries:** ~128 (64 for phase 1 + 64 for phase 2).

---

## LWE Lattice Attack via CVP (EHAX 2026)

**Pattern (Dream Labyrinth):** Multi-layer challenge ending with Learning With Errors (LWE) recovery. Secret vector `s` in {-1, 0, 1}^n, public matrix A, ciphertext `b = A*s + e (mod q)`.

**LWE solving with fpylll (CVP/Babai):**
```python
from fpylll import IntegerMatrix, LLL, CVP
import numpy as np

q = 3329  # Common LWE modulus (Kyber uses this)
n = 256   # Secret dimension
m = 512   # Number of samples

# A is m×n matrix, b is m-vector, all mod q
# Construct lattice basis for CVP approach
# Lattice: rows of [q*I_m | 0] on top, [A^T | I_n] below
# Target: b

def solve_lwe_cvp(A, b, q, n, m):
    # Build lattice basis (m+n) × (m+n)
    dim = m + n
    B = IntegerMatrix(dim, dim)

    # Top m rows: q*I_m (ensures solutions mod q)
    for i in range(m):
        B[i, i] = q

    # Bottom n rows: A columns + identity
    for j in range(n):
        for i in range(m):
            B[m + j, i] = int(A[i][j])
        B[m + j, m + j] = 1

    # LLL reduce the basis
    LLL.reduction(B)

    # Target vector: (b | 0...0)
    target = [int(b[i]) for i in range(m)] + [0] * n

    # CVP via Babai's nearest plane
    closest = CVP.babai(B, target)

    # Extract secret from last n components
    s_candidate = [closest[m + j] for j in range(n)]

    # Project to ternary {-1, 0, 1}
    s = []
    for val in s_candidate:
        val_mod = val % q
        if val_mod == 0:
            s.append(0)
        elif val_mod == 1:
            s.append(1)
        elif val_mod == q - 1:
            s.append(-1)
        else:
            # Try closest ternary value
            s.append(min([-1, 0, 1], key=lambda t: abs((val_mod - t) % q)))
    return s

s = solve_lwe_cvp(A, b, q, n, m)
```

**CRITICAL: Endianness gotcha.** Server may describe data as "big-endian" but actually use little-endian (or vice versa). If CVP produces garbage, try swapping byte order of the secret interpretation:
```python
# If server says big-endian but actually uses little-endian:
s_bytes_le = bytes([(v % 256) for v in s])  # little-endian
s_bytes_be = s_bytes_le[::-1]               # big-endian
# Try both interpretations for key derivation
```

**Key derivation after LWE recovery (common pattern):**
```python
import hashlib
from Cryptodome.Cipher import AES

s_bytes = bytes([(v % 256) for v in s])

# Recover session nonce: XOR wrapped_nonce with hash of secret
session_nonce = bytes(a ^ b for a, b in
    zip(wrapped_nonce, hashlib.sha256(s_bytes).digest()[:16]))

# Derive AES key from secret + nonce
aes_key = hashlib.sha256(s_bytes + session_nonce).digest()

# Decrypt AES-GCM
cipher = AES.new(aes_key, AES.MODE_GCM, nonce=aes_nonce)
plaintext = cipher.decrypt_and_verify(ciphertext, tag)
```

**Layer patterns in multi-stage crypto challenges:**
- **Layer 1 (Geometry):** Reconstruct point positions from noisy distance measurements. Use least-squares or trilateration with multiple models. Compute convex hull of recovered points.
- **Layer 2 (Subspace):** Find hidden low-dimensional subspace in high-dimensional data. Self-dot products of candidate vectors identify correct answers (smallest self-dot products = closest to subspace).
- **Layer 3 (LWE):** Recover secret vector from lattice problem. Use CVP with fpylll, project result to expected domain (ternary, binary, etc.).

**References:** EHAX CTF 2026 "Dream Labyrinth". Related: Kyber/CRYSTALS lattice cryptography.

---

## Affine Cipher over Non-Prime Modulus (Nullcon 2026)

**Pattern:** `c = A @ p + b (mod m)` where A is nxn matrix, m may not be prime (e.g., 65).

**Chosen-plaintext attack:**
1. Send n+1 crafted inputs to get n+1 ciphertext blocks
2. Difference attack: `c_i - c_0 = A @ (p_i - p_0) (mod m)`
3. Build difference matrices D (plaintext) and E (ciphertext)
4. Solve: `A = E @ D^{-1} (mod m)` using Gauss-Jordan with GCD invertibility checks
5. Recover: `b = c_0 - A @ p_0 (mod m)`

**CRT approach for composite modulus (preferred):**
```python
def crt2(r1, m1, r2, m2):
    """CRT: x = r1 (mod m1) and x = r2 (mod m2)"""
    m1_inv = pow(m1, m2 - 2, m2)  # Fermat's little theorem
    t = ((r2 - r1) * m1_inv) % m2
    return (r1 + m1 * t) % (m1 * m2)

def gauss_elim(A, b, mod):
    """Gaussian elimination over Z/modZ. A=matrix, b=vector, returns solution x."""
    n = len(b)
    M = [list(A[i]) + [b[i]] for i in range(n)]  # augmented matrix
    for col in range(n):
        pivot = next((r for r in range(col, n) if M[r][col] % mod), None)
        if pivot is None: continue
        M[col], M[pivot] = M[pivot], M[col]
        inv = pow(M[col][col], -1, mod)
        M[col] = [x * inv % mod for x in M[col]]
        for r in range(n):
            if r != col and M[r][col] % mod:
                f = M[r][col]
                M[r] = [(M[r][j] - f * M[col][j]) % mod for j in range(n + 1)]
    return [M[i][n] % mod for i in range(n)]

# For m=65=5x13: Gaussian elimination in GF(5) and GF(13) separately
A5, b5 = A % 5, rhs % 5
A13, b13 = A % 13, rhs % 13
x5 = gauss_elim(A5, b5, mod=5)
x13 = gauss_elim(A13, b13, mod=13)
x = [crt2(x5[i], 5, x13[i], 13) for i in range(len(x5))]
```

---

## Introspective CRC via GF(2) Linear Algebra (Google CTF 2017)

**Pattern:** Find an ASCII string whose CRC-N value equals the string itself (self-referential CRC). Model CRC as a linear function over GF(2) and solve the resulting system.

```python
# CRC is linear over GF(2): CRC(a XOR b) = CRC(a) XOR CRC(b)
# Goal: find x where CRC(x) = x (as ASCII hex)
# 1. Compute CRC of all-zeros baseline
# 2. For each bit position, compute the CRC difference (remainder)
# 3. Set up GF(2) linear system: CRC(x) XOR x = 0
# 4. Solve with Gaussian elimination over GF(2)
from sage.all import *
F = GF(2)
# Build matrix where each column represents flipping one bit
# Rows represent the CRC output bits XOR input bits
M = Matrix(F, n_bits, n_bits)
# ... fill with CRC remainders ...
solution = M.solve_right(target_vector)
```

**Key insight:** CRC is a linear function over GF(2). The self-referential constraint CRC(x)=x becomes a system of linear equations over GF(2), solvable by Gaussian elimination. The ASCII constraint requires choosing free variables to keep all bytes in the printable range.

**References:** Google CTF 2017

---

## Baby-Step Giant-Step for Sparse/Low Hamming Weight Exponents (SEC-T CTF 2017)

**Pattern:** DLP where the exponent is known to have low Hamming weight — e.g., at most k=11 bits set in a 128-bit exponent. Split the exponent into two halves `e = e1 * 2^64 + e2`. Precompute baby steps for all `e1` values with ⌊k/2⌋ = 5 bits set, then do giant steps for all `e2` values with ⌈k/2⌉ = 6 bits set.

**Complexity:** `C(128, 5) ≈ 10^8` baby steps + `C(128, 6) ≈ 10^9` giant steps — vastly less than `O(2^128)` brute force or `O(2^64)` standard BSGS.

```python
from itertools import combinations
from math import comb

# Parameters: g^x = a (mod p), x has at most k=11 bits set in 128 bits
# Split: x = x1 * 2^64 + x2, where x1 has 5 bits set, x2 has 6 bits set
half = 64
k_low, k_high = 5, 6

# Baby step: g^(x1 * 2^64) for all x1 with k_low bits set
baby = {}
for bit_positions in combinations(range(half), k_low):
    x1 = sum(1 << b for b in bit_positions)
    val = pow(g, x1 * (2**half), p)
    baby[val] = x1

# Giant step: check if a * g^(-x2) is in baby table
# a = g^x = g^(x1*2^64) * g^x2, so g^(x1*2^64) = a * g^(-x2)
g_inv = pow(g, -1, p)
for bit_positions in combinations(range(half), k_high):
    x2 = sum(1 << b for b in bit_positions)
    candidate = (a * pow(g_inv, x2, p)) % p
    if candidate in baby:
        x1 = baby[candidate]
        x = x1 * (2**half) + x2
        assert pow(g, x, p) == a
        print(f"Found exponent: {x}")
        break
```

**Verification:**
```python
# Check Hamming weight of recovered exponent
assert bin(x).count('1') <= 11
```

**Key insight:** Sparse-exponent DLP with only k bits set is attackable with meet-in-the-middle: each half uses `C(n, k/2)` entries, reducing complexity from `O(2^k)` to `O(C(n, k/2))`. For k=11 in 128 bits, this is ~10^8 vs 2^128. Always check if the challenge reveals or constrains the Hamming weight of the exponent.

**References:** SEC-T CTF 2017


# classic-ciphers

# CTF Crypto - Classic Ciphers

## Table of Contents
- [Vigenere Cipher](#vigenere-cipher)
- [Atbash Cipher](#atbash-cipher)
- [Polybius Square Cipher (Qiwi-Infosec 2016)](#polybius-square-cipher-qiwi-infosec-2016)
- [Substitution Cipher with Rotating Wheel](#substitution-cipher-with-rotating-wheel)
- [Kasiski Examination for Key Length](#kasiski-examination-for-key-length)
- [XOR Variants](#xor-variants)
  - [Multi-Byte XOR Key Recovery via Frequency Analysis](#multi-byte-xor-key-recovery-via-frequency-analysis)
  - [Cascade XOR (First-Byte Brute Force)](#cascade-xor-first-byte-brute-force)
  - [XOR with Rotation: Power-of-2 Bit Isolation (Pragyan 2026)](#xor-with-rotation-power-of-2-bit-isolation-pragyan-2026)
  - [Weak XOR Verification Brute Force (Pragyan 2026)](#weak-xor-verification-brute-force-pragyan-2026)
- [Deterministic OTP with Load-Balanced Backends (Pragyan 2026)](#deterministic-otp-with-load-balanced-backends-pragyan-2026)
- [OTP Key Reuse / Many-Time Pad XOR (BYPASS CTF 2025)](#otp-key-reuse--many-time-pad-xor-bypass-ctf-2025)
- [Book Cipher](#book-cipher)
- [Variable-Length Homophonic Substitution (ASIS CTF Finals 2013)](#variable-length-homophonic-substitution-asis-ctf-finals-2013)
- [Grid Permutation Cipher Keyspace Reduction (BSidesSF 2026)](#grid-permutation-cipher-keyspace-reduction-bsidessf-2026)
- [Image-Based Caesar Shift Ciphers (BSidesSF 2026)](#image-based-caesar-shift-ciphers-bsidessf-2026)
  - [Variant A — Vertical Strip Shift (caesar1)](#variant-a--vertical-strip-shift-caesar1)
  - [Variant B — Horizontal Shift with ASCII Encoding (caesar2)](#variant-b--horizontal-shift-with-ascii-encoding-caesar2)
- [XOR Key Recovery via File Format Headers (MetaCTF Flash 2026)](#xor-key-recovery-via-file-format-headers-metactf-flash-2026)

---

## Vigenere Cipher

**Known Plaintext Attack (most common in CTFs):**
```python
def vigenere_decrypt(ciphertext, key):
    result = []
    key_index = 0
    for c in ciphertext:
        if c.isalpha():
            shift = ord(key[key_index % len(key)].upper()) - ord('A')
            base = ord('A') if c.isupper() else ord('a')
            result.append(chr((ord(c) - base - shift) % 26 + base))
            key_index += 1
        else:
            result.append(c)
    return ''.join(result)

def derive_key(ciphertext, plaintext):
    """Derive key from known plaintext (e.g., flag format CCOI26{)"""
    key = []
    for c, p in zip(ciphertext, plaintext):
        if c.isalpha() and p.isalpha():
            c_val = ord(c.upper()) - ord('A')
            p_val = ord(p.upper()) - ord('A')
            key.append(chr((c_val - p_val) % 26 + ord('A')))
    return ''.join(key)
```

### Kasiski Examination for Key Length

When no known plaintext is available, determine the Vigenere key length using Kasiski examination: find repeated sequences in the ciphertext and compute the GCD of their distances.

```python
from math import gcd
from functools import reduce
from collections import Counter

def kasiski_examination(ciphertext, min_seq=3):
    """Find repeating sequences and compute likely key lengths."""
    ct = ''.join(c.upper() for c in ciphertext if c.isalpha())
    distances = []

    # Find repeated trigrams and their distances
    for seq_len in range(min_seq, 6):
        seen = {}
        for i in range(len(ct) - seq_len):
            seq = ct[i:i+seq_len]
            if seq in seen:
                for prev_pos in seen[seq]:
                    distances.append(i - prev_pos)
                seen[seq].append(i)
            else:
                seen[seq] = [i]

    # Key length is likely the GCD of distances
    if distances:
        key_len = reduce(gcd, distances)
        print(f"Likely key length: {key_len}")
        print(f"All distances: {sorted(set(distances))}")
        return key_len
    return None

def frequency_attack(ciphertext, key_length):
    """Break Vigenere by frequency analysis on each key-position group."""
    ct = [c.upper() for c in ciphertext if c.isalpha()]
    english_freq = [0.082,0.015,0.028,0.043,0.127,0.022,0.020,0.061,0.070,
                   0.002,0.008,0.040,0.024,0.067,0.075,0.019,0.001,0.060,
                   0.063,0.091,0.028,0.010,0.023,0.002,0.020,0.001]
    key = []

    for i in range(key_length):
        group = [ct[j] for j in range(i, len(ct), key_length)]
        # Try each shift, score by English letter frequency
        best_shift, best_score = 0, -1
        for shift in range(26):
            decrypted = [chr((ord(c) - ord('A') - shift) % 26 + ord('A')) for c in group]
            freq = Counter(decrypted)
            score = sum(freq.get(chr(j+65), 0) / len(group) * english_freq[j]
                       for j in range(26))
            if score > best_score:
                best_score = score
                best_shift = shift
        key.append(chr(best_shift + ord('A')))

    return ''.join(key)
```

**Key insight:** Repeated sequences in Vigenere ciphertext occur at distances that are multiples of the key length. The GCD of all such distances reveals the key length, after which each position becomes a simple Caesar cipher solvable by frequency analysis.

**When standard keys don't work:**
1. Key may not repeat - could be as long as message
2. Key derived from challenge theme (character names, phrases)
3. Key may have "padding" - repeated letters (IICCHHAA instead of ICHA)
4. Try guessing plaintext words from theme, derive full key

---

## Atbash Cipher

Simple substitution: A<->Z, B<->Y, C<->X, etc.

```python
def atbash(text):
    return ''.join(
        chr(ord('Z') - (ord(c.upper()) - ord('A'))) if c.isalpha() else c
        for c in text
    )
```

**Identification:** Challenge name hints ("Abashed" = Atbash), preserves spaces/punctuation, 1-to-1 substitution.

---

## Polybius Square Cipher (Qiwi-Infosec 2016)

5x5 grid cipher where each letter maps to a two-digit coordinate (row, column). I/J typically share a cell.

```python
import string

def polybius_decrypt(ciphertext, key="ABCDEFGHIKLMNOPQRSTUVWXYZ"):
    """Decrypt Polybius square cipher (pairs of digits 1-5)"""
    grid = {}
    for i, ch in enumerate(key):
        row, col = i // 5 + 1, i % 5 + 1
        grid[(row, col)] = ch

    digits = [int(d) for d in ciphertext if d.isdigit()]
    plaintext = ""
    for i in range(0, len(digits), 2):
        plaintext += grid.get((digits[i], digits[i+1]), '?')
    return plaintext

# Example: "5211251521531412" -> pairs (5,2)(1,1)(2,5)(1,5)(2,1)(5,3)(1,4)(1,2)
print(polybius_decrypt("5211251521531412"))
```

**Key insight:** Polybius ciphers produce digit-only ciphertext with values 1-5. The 5x5 grid merges I/J into one cell. Custom key alphabets change the grid layout but the two-digit coordinate structure remains constant.

---

## Substitution Cipher with Rotating Wheel

**Pattern (Wheel of Mystery):** Physical cipher wheel with inner/outer alphabets.

**Automated solver:** Use [quipqiup.com](https://quipqiup.com/) for general substitution ciphers — it uses word pattern matching and language entropy to solve without knowing the key.

**Brute force all rotations:**
```python
outer = "ABCDEFGHIJKLMNOPQRSTUVWXYZ{}"
inner = "QNFUVWLEZYXPTKMR}ABJICOSDHG{"  # Given

for rotation in range(len(outer)):
    rotated = inner[rotation:] + inner[:rotation]
    mapping = {outer[i]: rotated[i] for i in range(len(outer))}
    decrypted = ''.join(mapping.get(c, c) for c in ciphertext)
    if decrypted.startswith("METACTF{"):
        print(decrypted)
```

---

## XOR Variants

### Multi-Byte XOR Key Recovery via Frequency Analysis

**Pattern:** Ciphertext XOR'd with a repeating multi-byte key. Key length unknown.

**Step 1 — Determine key length:** Try each candidate length, split ciphertext into groups by position modulo key length, score each group's byte frequency against English text (space = 0x20 is the most common byte).

**Step 2 — Recover each key byte:** For each position, brute-force all 256 byte values and select the one producing the most English-like decrypted text.

```python
from collections import Counter

def score_english(data):
    """Score how English-like a byte sequence is."""
    freq = Counter(data)
    # Space is the most common character in English text
    return freq.get(ord(' '), 0) + sum(freq.get(c, 0) for c in range(ord('a'), ord('z')+1))

def find_key_length(ciphertext, max_len=40):
    """Test key lengths by scoring single-byte XOR on each column."""
    best_len, best_score = 1, 0
    for kl in range(1, max_len + 1):
        total = 0
        for col in range(kl):
            group = ciphertext[col::kl]
            best_col_score = max(
                score_english(bytes(b ^ k for b in group))
                for k in range(256)
            )
            total += best_col_score
        if total > best_score:
            best_score = total
            best_len = kl
    return best_len

def recover_key(ciphertext, key_length):
    """Recover each key byte via frequency analysis."""
    key = []
    for col in range(key_length):
        group = ciphertext[col::key_length]
        best_k = max(range(256), key=lambda k: score_english(bytes(b ^ k for b in group)))
        key.append(best_k)
    return bytes(key)

ct = open('encrypted.bin', 'rb').read()
kl = find_key_length(ct)
key = recover_key(ct, kl)
print(f"Key ({kl} bytes): {key}")
print(bytes(c ^ key[i % len(key)] for i, c in enumerate(ct)))
```

**Key insight:** Multi-byte repeating XOR splits into `key_length` independent single-byte XOR problems. English text frequency (especially space = 0x20) reliably identifies correct key bytes. Works best with ciphertext longer than ~100 bytes.

### Cascade XOR (First-Byte Brute Force)

**Pattern (Shifty XOR):** Each byte XORed with previous ciphertext byte.

```python
# c[i] = p[i] ^ c[i-1] (or similar cascade)
# Brute force first byte, rest follows deterministically
for first_byte in range(256):
    flag = [first_byte]
    for i in range(1, len(ct)):
        flag.append(ct[i] ^ flag[i-1])
    if all(32 <= b < 127 for b in flag):
        print(bytes(flag))
```

### XOR with Rotation: Power-of-2 Bit Isolation (Pragyan 2026)

**Pattern (R0tnoT13):** Given `S XOR ROTR(S, k)` for multiple rotation offsets k, recover S.

**Key insight:** When ALL rotation offsets are powers of 2 (2, 4, 8, 16, 32, 64), even-indexed and odd-indexed bits NEVER mix across any frame. This reduces N-bit recovery to just 2 bits of brute force.

**Algorithm:**
1. Express every bit of S in terms of two unknowns (s_0 for even bits, s_1 for odd bits) using the k=2 frame
2. Only 4 candidate states -> try all, verify against all frames
3. XOR valid state with ciphertext -> plaintext

### Weak XOR Verification Brute Force (Pragyan 2026)

**Pattern (Dor4_Null5):** Verification XORs all comparison bytes into a single byte instead of checking each individually.

**Vulnerability:** Any fixed response has 1/256 probability of passing. With enough interaction budget (e.g., 4919 attempts), brute-force succeeds with ~256 expected attempts.

```python
for attempt in range(3000):
    r.sendlineafter(b"prompt: ", b"00" * 8)  # Fixed zero response
    result = r.recvline()
    if b"successful" in result:
        break
```

---

## Deterministic OTP with Load-Balanced Backends (Pragyan 2026)

**Pattern (DumCows):** Service encrypts data with deterministic keystream that resets per connection. Multiple backends with different keystreams behind a load balancer.

**Attack:**
1. Send known plaintext (e.g., 18 bytes of 'A'), XOR with ciphertext -> recover keystream
2. XOR keystream with target ciphertext -> decrypt secret
3. **Backend matching:** Must connect to same backend for keystream to match. Retry connections until patterns align.

```python
def recover_keystream(known, ciphertext):
    return bytes(k ^ c for k, c in zip(known, ciphertext))

def decrypt(keystream, target_ct):
    return bytes(k ^ c for k, c in zip(keystream, target_ct))
```

**Key insight:** When encryption is deterministic per connection with no nonce/IV, known-plaintext attack is trivial. The challenge is matching backends.

---

## OTP Key Reuse / Many-Time Pad XOR (BYPASS CTF 2025)

**Pattern (Once More Unto the Same Wind):** Two ciphertexts encrypted with the same OTP key. Known plaintext for one message enables recovery of the other.

**XOR property:** `C1 XOR C2 = P1 XOR P2` (key cancels). When one plaintext (P1) is known, recover the other: `P2 = C1 XOR C2 XOR P1`.

```python
from pwn import xor

c1 = bytes.fromhex("7713283f5e9979...")
c2 = bytes.fromhex("740b393f4c8b67...")

# If one plaintext is known (or guessable, e.g., padded 'A' chars)
known_plaintext = b"A" * len(c1)
flag = xor(xor(c1, c2), known_plaintext)
print(flag)
```

**When plaintext is unknown — crib dragging:**
```python
def crib_drag(c1, c2, crib, max_pos=None):
    """Slide known word across XOR of two ciphertexts."""
    xored = xor(c1[:min(len(c1), len(c2))], c2[:min(len(c1), len(c2))])
    for pos in range(len(xored) - len(crib)):
        candidate = xor(xored[pos:pos+len(crib)], crib)
        if all(32 <= b < 127 for b in candidate):
            print(f"pos {pos}: {candidate}")
```

**Key insight:** OTP (One-Time Pad) XOR encryption is only secure when the key is truly one-time. Reusing the key on two messages leaks `P1 XOR P2` — exploit with known plaintext or crib dragging.

---

## Book Cipher

**Pattern (Booking Key, Nullcon 2026):** Book cipher with "steps forward" encoding. Brute-force starting position with charset filtering reduces ~56k candidates to 3-4.

See [historical.md](historical.md) for full implementation.

---

## Variable-Length Homophonic Substitution (ASIS CTF Finals 2013)

**Pattern (Rookie Agent):** Ciphertext uses alphanumeric characters grouped in blocks of 5. Single-character frequency analysis shows non-uniform distribution. N-gram analysis reveals repeated multi-character groups mapping to single plaintext characters, with different plaintext characters encoded by groups of different lengths (1-4 characters).

**Analysis workflow:**

1. Collapse whitespace and compute n-gram frequencies (1 through 6):
```python
from collections import Counter

ct = "6di16ovhtmnzslsxqcjo8fkdmtyrbn..."  # cleaned ciphertext
for n in range(1, 7):
    ngrams = [ct[i:i+n] for i in range(len(ct)-n+1)]
    freq = Counter(ngrams).most_common(20)
    print(f"{n}-grams: {freq[:10]}")
```

2. Identify constant-frequency groups — if `8f`, `fk`, and `kd` each appear exactly 36 times, check whether `8fkd` also appears 36 times. If so, it is a single substitution unit:
```python
# Iteratively replace most-frequent fixed groups with single symbols
substitutions = {
    '8fkd': 'E', '4bg9': 'I', 'lsxq': 'A', 'fmrk': 'B',
    '9gle': 'C', 'mtyr': 'D', 'cjo': 'F', 'htm': 'G',
    # ... continue for all identified groups
}
reduced = ct
for pattern, symbol in sorted(substitutions.items(), key=lambda x: -len(x[0])):
    reduced = reduced.replace(pattern, symbol)
```

3. The reduced text is now a monoalphabetic substitution — solve with [quipqiup.com](https://quipqiup.com/) or statistical analysis on English.

4. When some characters remain ambiguous after decryption, brute-force permutations against a known hash of the flag:
```python
from itertools import permutations
from hashlib import sha256

partial_flag = '3c6a1c371b381c943065864b95ae5546'
ambiguous_chars = '12456789x'  # chars with uncertain mapping
known_hash = '9f2a579716af14400c9ba1de8682ca52c17b3ed4235ea17ac12ae78ca24876ef'

for p in permutations(ambiguous_chars):
    mapping = dict(zip(ambiguous_chars, p))
    candidate = ''.join(mapping.get(c, c) for c in partial_flag)
    if sha256(('ASIS_' + candidate).encode()).hexdigest() == known_hash:
        print(f"Flag: ASIS_{candidate}")
        break
```

**Key insight:** Variable-length homophonic substitution hides letter frequencies by mapping common plaintext letters to longer codegroups. The attack reverses this: find n-grams that always appear as a unit (identical frequency for all sub-n-grams), replace them with single symbols, then solve the resulting monoalphabetic substitution. When the flag format provides a hash for verification, brute-force remaining ambiguous character permutations offline.

---

## Grid Permutation Cipher Keyspace Reduction (BSidesSF 2026)

**Pattern (ghostcrypt):** A substitution cipher built on a 5x5 grid where the key permutes rows and columns independently. Row permutations and column permutations commute — applying all row swaps then all column swaps gives the same result regardless of order. This collapses the keyspace from potentially huge to just 5! x 5! = 14,400 combinations, making brute-force trivial.

```python
from itertools import permutations

# 5x5 grid substitution cipher — brute force row+column permutations
grid_size = 5
ciphertext = "..."  # encrypted text
wordlist = set(open("/usr/share/dict/words").read().split())

for row_perm in permutations(range(grid_size)):
    for col_perm in permutations(range(grid_size)):
        # Apply inverse permutation to grid
        decrypted = apply_grid_permutation(ciphertext, row_perm, col_perm)
        words = decrypted.split()
        if sum(1 for w in words if w.lower() in wordlist) > len(words) * 0.5:
            print(f"Key: rows={row_perm}, cols={col_perm}")
            print(decrypted)
            break
```

**Key insight:** Row and column permutations on a grid are independent operations that commute. The total keyspace is the product of row permutations x column permutations (n!^2), NOT the factorial of total cells. For a 5x5 grid: 120 x 120 = 14,400 — brute-forceable in milliseconds.

**When to recognize:** Challenge uses a grid-based cipher, mentions "row/column shuffling", or provides a substitution table that looks like a permuted matrix. Any grid cipher where rows and columns are shuffled independently has this n!^2 keyspace property.

---

## Image-Based Caesar Shift Ciphers (BSidesSF 2026)

Two variants of applying Caesar cipher concepts to 2D image data:

### Variant A — Vertical Strip Shift (caesar1)

Each vertical strip of pixels is shifted downward by `(column / strip_width) * multiplier mod height`. The multiplier is a small integer (1-50), making it brute-forceable.

```python
from PIL import Image
import sys

img = Image.open("shifted.png")
w, h = img.size
pixels = img.load()
strip_width = 10  # Determined by visual inspection

for multiplier in range(1, 51):
    out = Image.new("RGB", (w, h))
    out_px = out.load()
    for x in range(w):
        shift = (x // strip_width) * multiplier % h
        for y in range(h):
            out_px[x, (y - shift) % h] = pixels[x, y]
    out.save(f"attempt_{multiplier}.png")
```

### Variant B — Horizontal Shift with ASCII Encoding (caesar2)

Each row is shifted horizontally by a different amount. The shift value for each strip directly encodes an ASCII character of the flag.

```python
from PIL import Image

original = Image.open("original.png")
shifted = Image.open("shifted.png")
w, h = original.size

flag = ""
prev_shift = -1
for y in range(h):
    orig_row = [original.getpixel((x, y)) for x in range(w)]
    shift_row = [shifted.getpixel((x, y)) for x in range(w)]
    # Find shift by comparing rows
    for offset in range(128):
        if all(orig_row[(x + offset) % w] == shift_row[x] for x in range(min(20, w))):
            if offset != prev_shift:
                flag += chr(offset)
                prev_shift = offset
            break
print(flag)
```

**Key insight:** Image pixel shifts are a visual form of Caesar cipher. When comparing an original and shifted image, the shift amount per row/column directly encodes hidden data. Always compare row-by-row or column-by-column when given two versions of the same image.

**When to recognize:** Challenge provides one or two image files with visible horizontal or vertical "shearing" artifacts. If an original image is provided alongside a shifted version, compute per-row or per-column offsets and check if they decode as ASCII.

---

## XOR Key Recovery via File Format Headers (MetaCTF Flash 2026)

**Pattern (In The Door):** A file claims to be a known format (e.g., PDF, PNG, ZIP) but `file` reports it as "data". The file has been XOR-encrypted with a repeating key. Recover the key by XOR-ing the encrypted bytes against the expected file format header, then extend the key using known structural elements at the end of the file.

```python
# Step 1: XOR first bytes against expected header to derive key start
encrypted = open('encrypted.pdf', 'rb').read()

# PDF files always start with %PDF-1.
expected_header = b'%PDF-1.'
key_start = bytes(a ^ b for a, b in zip(encrypted[:len(expected_header)], expected_header))
print(f"Key prefix: {key_start}")  # e.g., b'h4ck4ll'

# Step 2: Extend key using known trailer structures
# PDF files end with %%EOF (possibly followed by newline)
# Try known trailer patterns at the end of the file
pdf_trailers = [b'%%EOF\n', b'%%EOF\r\n', b'%%EOF']
for trailer in pdf_trailers:
    tail = encrypted[-len(trailer):]
    key_tail = bytes(a ^ b for a, b in zip(tail, trailer))
    print(f"Key tail candidate: {key_tail}")

# Step 3: Once key length is known, combine fragments
# Common structures to anchor: 'startxref', 'trailer', 'endobj'
key = b'h4ck4llth3cryp70'  # 16-byte repeating key
key_len = len(key)

# Step 4: Decrypt entire file
decrypted = bytes(encrypted[i] ^ key[i % key_len] for i in range(len(encrypted)))
with open('decrypted.pdf', 'wb') as f:
    f.write(decrypted)

# Verify
import subprocess
result = subprocess.run(['file', 'decrypted.pdf'], capture_output=True, text=True)
print(result.stdout)  # Should show: PDF document
```

**Key insight:** Every file format has known byte sequences at fixed positions -- magic bytes at the start, structural markers throughout, and trailer signatures at the end. XOR with a repeating key is fully recoverable when you know enough plaintext at known offsets. For a key of length N, you need N bytes of known plaintext at known positions (they need not be contiguous, but you must know their offset modulo the key length).

**Common file format anchors for key recovery:**

| Format | Header | Trailer/Footer |
|--------|--------|----------------|
| PDF | `%PDF-1.` | `%%EOF` |
| PNG | `\x89PNG\r\n\x1a\n` | `IEND\xaeB\x60\x82` |
| ZIP | `PK\x03\x04` | `PK\x05\x06` (EOCD) |
| JPEG | `\xff\xd8\xff\xe0` | `\xff\xd9` |
| ELF | `\x7fELF` | -- |
| GIF | `GIF89a` or `GIF87a` | `\x3b` (trailer) |

**When to recognize:** Challenge provides a file that should be a known format (filename extension or description says so) but `file` reports "data" or wrong type. Hex dump shows no recognizable magic bytes. XOR the first few bytes against the expected header -- if the result looks like an ASCII string or repeating pattern, it is a repeating XOR key.

**Determining key length:** If the header-derived key fragment repeats or the key is a readable string, try common lengths (8, 16, 32). Alternatively, XOR the file against itself shifted by candidate key lengths and look for low-entropy output (many null bytes indicate correct shift = key length).

**References:** MetaCTF Flash CTF 2026 "In The Door"


# ecc-attacks

# CTF Crypto - Elliptic Curve Attacks

## Table of Contents
- [Small Subgroup Attacks](#small-subgroup-attacks)
- [Invalid Curve Attacks](#invalid-curve-attacks)
- [Singular Curves](#singular-curves)
- [Smart's Attack (Anomalous Curves)](#smarts-attack-anomalous-curves)
- [ECC Fault Injection](#ecc-fault-injection)
- [Clock Group DLP via Pohlig-Hellman (LACTF 2026)](#clock-group-dlp-via-pohlig-hellman-lactf-2026)
- [ECDSA Nonce Reuse (BearCatCTF 2026)](#ecdsa-nonce-reuse-bearcatctf-2026)
- [Ed25519 Torsion Side Channel (BearCatCTF 2026)](#ed25519-torsion-side-channel-bearcatctf-2026)
- [DSA Nonce Reuse for Private Key Recovery (VolgaCTF 2016)](#dsa-nonce-reuse-for-private-key-recovery-volgactf-2016)
- [DSA Limited k-Value Brute Force (ASIS CTF Finals 2016)](#dsa-limited-k-value-brute-force-asis-ctf-finals-2016)
- [ECC Shared Prime Factor via GCD (ASIS CTF Finals 2016)](#ecc-shared-prime-factor-via-gcd-asis-ctf-finals-2016)
- [DSA Key Recovery via MD5 Collision on k-Generation (CONFidence CTF 2017)](#dsa-key-recovery-via-md5-collision-on-k-generation-confidence-ctf-2017)

---

## Small Subgroup Attacks

- Check curve order for small factors
- Pohlig-Hellman: solve DLP (Discrete Logarithm Problem) in small subgroups, combine with CRT (Chinese Remainder Theorem)

```python
# SageMath ECC basics
E = EllipticCurve(GF(p), [a, b])
G = E.gens()[0]  # generator
order = E.order()
```

**Key insight:** When the curve order has small prime factors, Pohlig-Hellman decomposes the DLP into small subgroup problems solvable independently, then combines results with CRT. Always factor the curve order first -- if it is smooth (all small factors), the DLP is trivially solvable.

---

## Invalid Curve Attacks

If point validation is missing, send points on weaker curves. Craft points with small-order subgroups to leak secret key bits.

**Key insight:** Invalid curve attacks exploit missing point-on-curve validation. Send crafted points that lie on a different curve with a small-order subgroup, and the server will compute scalar multiplication on the weak curve, leaking secret key bits modulo the small order.

---

## Singular Curves

If discriminant delta = 0, curve is singular. DLP becomes easy (maps to additive/multiplicative group).

**Key insight:** Check the discriminant `4a^3 + 27b^2 mod p` first. If it is zero, the curve is singular and the ECDLP reduces to a simple discrete log in the additive group (cusp) or multiplicative group (node) of the field, both solvable in polynomial time.

---

## Smart's Attack (Anomalous Curves)

**When to use:** Curve order equals field characteristic p (anomalous curve). Solves ECDLP in O(1) via p-adic lifting.

**Key insight:** Always check `E.order() == p` first. If the curve order equals the field prime, the ECDLP is solved instantly via p-adic lifting (Smart's attack). SageMath's `discrete_log` handles this automatically, but manual p-adic lift code is needed when the built-in method fails.

**Detection:** `E.order() == p` — always check this first!

**SageMath (automatic):**
```python
E = EllipticCurve(GF(p), [a, b])
G = E(Gx, Gy)
Q = E(Qx, Qy)
# Sage's discrete_log handles anomalous curves automatically
secret = G.discrete_log(Q)
```

**Manual p-adic lift (when Sage's auto method fails):**
```python
def smart_attack(p, a, b, G, Q):
    E = EllipticCurve(GF(p), [a, b])
    Qp = pAdicField(p, 2)  # p-adic field with precision 2
    Ep = EllipticCurve(Qp, [a, b])

    # Lift points to p-adics
    Gp = Ep.lift_x(ZZ(G[0]), all=True)  # try both lifts
    Qp_point = Ep.lift_x(ZZ(Q[0]), all=True)

    for gp in Gp:
        for qp in Qp_point:
            try:
                # Multiply by p to get points in kernel of reduction
                pG = p * gp
                pQ = p * qp
                # Extract p-adic logarithm
                x_G = ZZ(pG[0] / pG[1]) / p  # or pG.xy()
                x_Q = ZZ(pQ[0] / pQ[1]) / p
                secret = ZZ(x_Q / x_G) % p
                if E(G) * secret == E(Q):
                    return secret
            except (ZeroDivisionError, ValueError):
                continue
    return None
```

**Multi-layer decryption after key recovery:** Challenge may wrap flag in AES-CBC + DES-CBC or similar — just busywork once the ECC key is recovered. Derive keys with SHA-256 of shared secret.

---

## ECC Fault Injection

**Pattern (Faulty Curves):** Bit flip during ECC computation reveals private key bits.

**Attack:** Compare correct vs faulty ciphertext, recover key bit-by-bit:
```python
# For each key bit position:
# If fault at bit i changes output -> key bit i affects computation
# Binary distinguisher: faulty_output == correct_output -> bit is 0
```

---

## Clock Group DLP via Pohlig-Hellman (LACTF 2026)

**Pattern (the-clock):** Diffie-Hellman on unit circle group: x^2 + y^2 = 1 (mod p).

**Key facts:**
- Group law: (x1,y1) * (x2,y2) = (x1*y2 + y1*x2, y1*y2 - x1*x2)
- **Group order = p + 1** (not p - 1!)
- Isomorphic to GF(p^2)* elements of norm 1

**Group operations:**
```python
def clock_mul(P, Q, p):
    x1, y1 = P
    x2, y2 = Q
    return ((x1*y2 + y1*x2) % p, (y1*y2 - x1*x2) % p)

def clock_pow(P, n, p):
    result = (0, 1)  # identity
    base = P
    while n > 0:
        if n & 1:
            result = clock_mul(result, base, p)
        base = clock_mul(base, base, p)
        n >>= 1
    return result
```

**Recovering hidden prime p:**
```python
# Given points on the curve, p divides (x^2 + y^2 - 1)
from math import gcd
vals = [x**2 + y**2 - 1 for x, y in known_points]
p = reduce(gcd, vals)
# May need to remove small factors
```

**Attack when p+1 is smooth:**
```python
# 1. Recover p from points: gcd(x^2 + y^2 - 1) across known points
# 2. Factor p+1 into small primes
# 3. Pohlig-Hellman: solve DLP in each small subgroup, CRT combine
# 4. Compute shared secret, derive AES key (e.g., via MD5)
```

**Identification:** Challenge mentions "clock", "circle", or gives points satisfying x^2+y^2=1. Always check if p+1 (not p-1) is smooth.

---

## Ed25519 Torsion Side Channel (BearCatCTF 2026)

**Pattern (Curvy Wurvy):** Ed25519 signing oracle derives per-user keys as `user_key = MASTER_KEY * uid mod l` (where `l` is the Ed25519 subgroup order). Goal: recover `MASTER_KEY` from oracle queries.

**The attack exploits Ed25519's cofactor h=8:**
- Full curve order = `8*l`, but scalars are reduced mod `l`
- When `MASTER_KEY * 2^t` wraps around `l`, multiplication produces a torsion component visible as y-coordinate change

**Key extraction via binary decomposition:**
```python
# Query sign(uid=3, 2^t) for t = 0..255
# S_t = (MASTER_KEY * 2^t mod l) * P3
# Check: does doubling S_t match S_{t+1}?

bits = []
for t in range(255):
    S_t = query_sign(3, 2**t)
    S_t1 = query_sign(3, 2**(t+1))
    doubled = point_double(S_t)
    # Wrap occurred if doubled.y != S_{t+1}.y (torsion shift)
    bits.append(0 if doubled.y == S_t1.y else 1)

# Reconstruct: MASTER_KEY ≈ l * (0.bit0 bit1 bit2 ...)_binary
# Try all 8 torsion corrections for exact value
```

**Key insight:** Ed25519's cofactor creates an observable side channel: when scalar multiplication wraps around the subgroup order `l`, the result shifts by a torsion element (one of 8 points). By querying powers of 2 and checking y-coordinate consistency, each bit of the secret scalar is leaked. Libraries like `ecpy` that reduce mod `l` are vulnerable to this when used in multi-user key derivation schemes.

**Detection:** Ed25519 signing oracle with user-controlled UID or multiplier. Key derivation formula `key = master * uid mod l`.

---

## ECDSA Nonce Reuse (BearCatCTF 2026)

**Pattern (Chatroom):** ECDSA signatures on secp256k1 with constant nonce `k`. When two signatures share the same `r` value, the nonce and private key are recoverable.

**Recovery:**
```python
from hashlib import sha256

# Two signatures (r, s1) and (r, s2) with same r → same nonce k
h1 = int(sha256(msg1).hexdigest(), 16)
h2 = int(sha256(msg2).hexdigest(), 16)
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141  # secp256k1 order

k = ((h1 - h2) * pow(s1 - s2, -1, n)) % n
d = ((s1 * k - h1) * pow(r, -1, n)) % n  # private key
```

**Key insight:** Same `r` value across multiple ECDSA signatures means the nonce `k` was reused. This is the same class of bug that compromised the PlayStation 3 signing key. Always check for repeated `r` values in signature datasets.

**Detection:** Multiple ECDSA signatures with identical `r` component. Challenge mentions "nonce", "deterministic signing", or provides a signing oracle.

---

## DSA Nonce Reuse for Private Key Recovery (VolgaCTF 2016)

**Pattern:** Two DSA (Digital Signature Algorithm) signatures sharing the same nonce k (same r value) leak the private key. Identical in principle to ECDSA nonce reuse but uses DSA-specific group parameters.

```python
# Two signatures (r, s1, H(m1)) and (r, s2, H(m2)) with same r
k = ((H_m1 - H_m2) * pow(s1 - s2, -1, q)) % q
x = ((s1 * k - H_m1) * pow(r, -1, q)) % q  # private key
# Then forge signatures for arbitrary messages
```

**Key insight:** DSA nonce reuse is identical in principle to ECDSA nonce reuse. Look for repeated r values in any DSA/ECDSA signature set. The same recovery formula applies to both.

---

## DSA Limited k-Value Brute Force (ASIS CTF Finals 2016)

DSA implementation generates k from a restricted space (e.g., only 1024 possibilities). Given multiple signatures, brute-force k values and solve for the private key.

```python
from Crypto.Util.number import inverse

def recover_dsa_key(signatures, q, g, p):
    """Recover DSA private key when k has limited possible values"""
    (r1, s1, h1), (r2, s2, h2) = signatures[0], signatures[1]

    for k1 in range(1, 1024):
        for k2 in range(1, 1024):
            # From DSA: s = k^-1 * (h + x*r) mod q
            # With two signatures: x = (s2*k2*h1 - s1*k1*h2) / (s1*k1*r2 - s2*k2*r1) mod q
            num = (s2 * k2 * h1 - s1 * k1 * h2) % q
            den = (s1 * k1 * r2 - s2 * k2 * r1) % q
            if den == 0:
                continue
            x = (num * inverse(den, q)) % q
            # Verify: check if r1 == (g^k1 mod p) mod q
            if pow(g, k1, p) % q == r1:
                return x
    return None
```

**Key insight:** Standard DSA nonce reuse attacks require k1 == k2. When k values are drawn from a small space (e.g., 1024 values), brute-force all (k1, k2) pairs across two signatures to solve the linear system for private key x.

---

## ECC Shared Prime Factor via GCD (ASIS CTF Finals 2016)

Multiple ECC public keys generated with a flawed prime generator that filters `prime % 3 == 2`, reducing the keyspace enough for shared factors to appear.

```python
from math import gcd
from Crypto.Util.number import inverse

# Collect moduli from multiple ECC public keys
moduli = [key.n for key in public_keys]

# Find shared factors via pairwise GCD
for i in range(len(moduli)):
    for j in range(i + 1, len(moduli)):
        g = gcd(moduli[i], moduli[j])
        if 1 < g < moduli[i]:
            p = g
            q = moduli[i] // p
            print(f"Key {i} factored: p={p}, q={q}")
            # Now decrypt using recovered factors
```

**Key insight:** When a prime generator excludes primes based on modular conditions (e.g., `p % 3 == 2`), the reduced keyspace makes GCD collisions between independently generated keys much more likely. Always try pairwise GCD across multiple public keys.

---

## DSA Key Recovery via MD5 Collision on k-Generation (CONFidence CTF 2017)

**Pattern:** When DSA nonce `k` is derived from `MD5(prefix + counter)`, generate MD5 prefix collisions to force two different counter values to produce the same `k`, enabling the standard nonce-reuse private key recovery.

```python
# k = int(MD5("K = {n: " + str(counter) + ...))
# Use fastcoll to find MD5 collision on prefix "K = {n: "
# Two different counter values -> same MD5 -> same k -> nonce reuse

import subprocess
# Generate collision pair
subprocess.run(["fastcoll", "-p", prefix_file, "-o", "col1", "col2"])

# Get two signatures with same k (same r value)
sig1 = sign(msg1, counter1)  # uses MD5(prefix + counter1)
sig2 = sign(msg2, counter2)  # uses MD5(prefix + counter2) = same hash!

# Standard DSA nonce reuse recovery
k = (hash1 - hash2) * modinv(sig1.s - sig2.s, q) % q
private_key = (sig1.s * k - hash1) * modinv(sig1.r, q) % q
```

**Key insight:** MD5 collision generators like `fastcoll` produce pairs of inputs with identical hashes from a chosen prefix. When a signature scheme derives its nonce from an MD5 hash of controllable data, manufacturing a collision produces nonce reuse, enabling standard private key recovery.

**References:** CONFidence CTF 2017


# exotic-crypto

# CTF Crypto - Exotic Algebraic Structures

## Table of Contents
- [Braid Group DH — Alexander Polynomial Multiplicativity (DiceCTF 2026)](#braid-group-dh--alexander-polynomial-multiplicativity-dicectf-2026)
- [Monotone Function Inversion with Partial Output](#monotone-function-inversion-with-partial-output)
- [Tropical Semiring Residuation Attack (BearCatCTF 2026)](#tropical-semiring-residuation-attack-bearcatctf-2026)
- [Paillier Cryptosystem Attack (SECCON 2015)](#paillier-cryptosystem-attack-seccon-2015)
- [Hamming Code Error Correction with Helical Interleaving (Sharif CTF 2016)](#hamming-code-error-correction-with-helical-interleaving-sharif-ctf-2016)
- [ElGamal Universal Re-encryption (Sharif CTF 2016)](#elgamal-universal-re-encryption-sharif-ctf-2016)
- [Paillier Oracle Size Bypass via Ciphertext Factoring (BSidesSF 2025)](#paillier-oracle-size-bypass-via-ciphertext-factoring-bsidessf-2025)
- [Format-Preserving Encryption Feistel Brute-Force (BSidesSF 2026)](#format-preserving-encryption-feistel-brute-force-bsidessf-2026)
- [Icosahedral Symmetry Group Cipher (BSidesSF 2026)](#icosahedral-symmetry-group-cipher-bsidessf-2026)
- [Goldwasser-Micali Ciphertext Replication Oracle (BSidesSF 2026)](#goldwasser-micali-ciphertext-replication-oracle-bsidessf-2026)
- [BB-84 Quantum Key Distribution MITM Attack (PlaidCTF 2017)](#bb-84-quantum-key-distribution-mitm-attack-plaidctf-2017)
- [ElGamal Trivial DLP When B = p-1 (Hack.lu 2017)](#elgamal-trivial-dlp-when-b--p-1-hacklu-2017)
- [Paillier LSB Oracle via Homomorphic Doubling (CODE BLUE 2017)](#paillier-lsb-oracle-via-homomorphic-doubling-code-blue-2017)
- [Differential Privacy Laplace Noise Cancellation (Pwn2Win 2017)](#differential-privacy-laplace-noise-cancellation-pwn2win-2017)
- [Homomorphic Encryption Oracle Bit-Extraction (Tokyo Westerns 2017)](#homomorphic-encryption-oracle-bit-extraction-tokyo-westerns-2017)

---

## Braid Group DH — Alexander Polynomial Multiplicativity (DiceCTF 2026)

**Pattern (Plane or Exchange):** Diffie-Hellman key exchange built over mathematical braids. Public keys are derived by connecting a private braid to public info, then scrambled with Reidemeister-like moves. Shared secret = `sha256(normalize(calculate(connect(my_priv, their_pub))))`. The `calculate()` function computes the Alexander polynomial of the braid.

**Protocol structure:**
```python
import sympy as sp
import hashlib

t = sp.Symbol('t')

def compose(p1, p2):
    return [p1[p2[i]] for i in range(len(p1))]

def inverse(p):
    inv = [0] * len(p)
    for i, j in enumerate(p):
        inv[j] = i
    return inv

def connect(g1, g2):
    """Concatenate two braids with a swap at the junction."""
    x1, o1 = g1
    x2, o2 = g2
    l = len(x1)
    new_x = list(x1) + [v + l for v in x2]
    new_o = list(o1) + [v + l for v in o2]
    # Swap at junction
    new_x[l-1], new_x[l] = new_x[l], new_x[l-1]
    return (new_x, new_o)

def sweep(ap):
    """Compute winding number matrix from arc presentation."""
    l = len(ap)
    current_row = [0] * l
    matrix = []
    for pair in ap:
        c1, c2 = sorted(pair)
        diff = pair[1] - pair[0]
        s = 1 if diff > 0 else (-1 if diff < 0 else 0)
        for c in range(c1, c2):
            current_row[c] += s
        matrix.append(list(current_row))
    return matrix

def mine(point):
    x, o = point
    return sweep([*zip(x, o)])

def calculate(point):
    """Compute Alexander polynomial from braid."""
    mat = sp.Matrix([[t**(-x) for x in y] for y in mine(point)])
    return mat.det(method='bareiss') * (1 - t)**(1 - len(point[0]))

def normalize(calculation):
    """Convert Laurent polynomial to standard form."""
    poly = sp.expand(sp.simplify(calculation))
    all_exp = [term.as_coeff_exponent(t)[1] for term in poly.as_ordered_terms()]
    min_exp = min(all_exp)
    poly = sp.expand(sp.simplify(poly * t**(-min_exp)))
    if poly.coeff(t, 0) < 0:
        poly *= -1
    return poly

# Key exchange:
# alice_pub = scramble(connect(pub_info, alice_priv), 1000)
# bob_pub = scramble(connect(pub_info, bob_priv), 1000)
# shared = sha256(str(normalize(calculate(connect(alice_priv, bob_pub)))))
```

**The fatal vulnerability — Alexander polynomial multiplicativity:**

The Alexander polynomial satisfies `Δ(β₁·β₂) = Δ(β₁) × Δ(β₂)` under braid concatenation. This makes the scheme abelian:

```python
# Eve computes shared secret from public values only:
calc_pub = normalize(calculate(pub_info))
calc_alice = normalize(calculate(alice_pub))
calc_bob = normalize(calculate(bob_pub))

# Recover Alice's private polynomial
calc_alice_priv = sp.cancel(calc_alice / calc_pub)  # exact division

# Shared secret = calc(alice_priv) * calc(bob_pub) = calc(bob_priv) * calc(alice_pub)
shared_poly = normalize(sp.expand(calc_alice_priv * calc_bob))
shared_hex = hashlib.sha256(str(shared_poly).encode()).hexdigest()

# Decrypt XOR stream cipher
key = bytes.fromhex(shared_hex)
while len(key) < len(ciphertext):
    key += hashlib.sha256(key).digest()
plaintext = bytes(a ^ b for a, b in zip(ciphertext, key))
```

**Computational trick for large matrices:**

Direct sympy Bareiss on rational-function matrices (e.g., 30×30 with entries `t^(-w)`) is extremely slow. Clear denominators first:

```python
# Winding numbers range from w_min to w_max (e.g., -1 to 5)
# Multiply all entries by t^w_max to get polynomial matrix
k = max(abs(w) for row in winding_matrix for w in row)
n = len(winding_matrix)

# Original: M[i][j] = t^(-w[i][j])
# Scaled:   M'[i][j] = t^(k - w[i][j])  (all non-negative powers)
mat_poly = sp.Matrix([[t**(k - w) for w in row] for row in winding_matrix])
det_scaled = mat_poly.det(method='bareiss')  # Much faster!

# Recover true determinant: det(M) = det(M') / t^(k*n)
det_true = sp.cancel(det_scaled / t**(k * n))
# Then: (1-t)^(n-1) divides det_true (topological property)
result = sp.cancel(det_true * (1 - t)**(1 - n))
```

**Validation — palindromic property:**
All valid Alexander polynomials are palindromic (coefficients read the same forwards and backwards). Use this as a sanity check on intermediate results:
```python
def is_palindromic(poly, var=t):
    coeffs = sp.Poly(poly, var).all_coeffs()
    return coeffs == coeffs[::-1]
```

**When to recognize:** Challenge mentions braids, knots, permutation pairs, winding numbers, Reidemeister moves, or "topological key exchange." The key mathematical insight is that the Alexander polynomial — while a powerful knot/braid invariant — is multiplicative, making it fundamentally unsuitable as a one-way function for Diffie-Hellman.

**Key lessons:**
- **Diffie-Hellman requires non-abelian hardness.** If the invariant used for the shared secret is multiplicative/commutative under the group operation, Eve can compute it from public values.
- **Scrambling (Reidemeister moves) doesn't help** — the Alexander polynomial is an invariant, so scrambled braids produce the same polynomial.
- **Large symbolic determinants** need the denominator-clearing trick: multiply by `t^k` to get polynomials, compute det, divide back.

**References:** DiceCTF 2026 "Plane or Exchange"

---

## Monotone Function Inversion with Partial Output

**Pattern:** A flag is converted to a real number, pushed through an invertible/monotone function (e.g., iterated map, spiral), then some output digits are masked/erased. Recover the masked digits to invert and get the flag.

**Identification:**
- Output is a high-precision decimal number with some digits replaced by `?`
- The transformation is smooth/monotone (invertible via root-finding)
- Flag format constrains the input to a narrow range
- Challenge hints like "brute won't cut it" or "binary search"

**Key insight:** For a monotone function `f`, knowing the flag format (e.g., `0xL4ugh{...}`) constrains the output to a tiny interval. Many "unknown" output digits are actually **fixed** across all valid inputs and can be determined immediately.

**Attack: Hierarchical Digit Recovery**

1. **Determine fixed digits:** Compute `f(flag_min)` and `f(flag_max)` for all valid flags. Digits that are identical in both outputs are fixed regardless of flag content.

2. **Sequential refinement:** Determine remaining unknown digits one at a time (largest contribution first). For each candidate value (0-9), invert `f` and check if the result is a valid flag (ASCII, correct format).

3. **Validation:** The correct digit produces readable ASCII text; wrong digits produce garbage bytes in the flag.

```python
import mpmath

# Match SageMath's RealField(N) precision exactly:
# RealField(256) = 256-bit MPFR mantissa
mpmath.mp.prec = 256  # BINARY precision (not decimal!)
# For decimal: mpmath.mp.dps = N sets decimal places

phi = (mpmath.mpf(1) + mpmath.sqrt(mpmath.mpf(5))) / 2

def forward(x0):
    """The challenge's transformation (e.g., iterated spiral)."""
    x = x0
    for i in range(iterations):
        r = mpmath.mpf(i) / mpmath.mpf(iterations)
        x = r * mpmath.sqrt(x*x + 1) + (1 - r) * (x + phi)
    return x

def invert(y_target, x_guess):
    """Invert via root-finding (Newton's method)."""
    def f(x0):
        return forward(x0) - y_target
    return mpmath.findroot(f, x_guess, tol=mpmath.mpf(10)**(-200))

# Hierarchical search: determine unknown digits sequentially
masked = "?7086013?3756162?51694057..."
unknown_positions = [0, 8, 16, 25, 33, ...]

# Step 1: Fix digits that are constant across all valid flags
# (compute forward for min/max valid flag, compare)

# Step 2: For each remaining unknown (largest positional weight first):
for pos in remaining_unknowns:
    for digit in range(10):
        # Set this digit, others to middle value (5)
        output_val = construct_number(known_digits | {pos: digit})
        x_inv = invert(output_val, x_guess=0.335)
        flag_int = int(x_inv * mpmath.power(10, flag_digits))
        flag_bytes = flag_int.to_bytes(30, 'big')

        # Check: starts with prefix? Ends with suffix? All ASCII?
        if is_valid_flag(flag_bytes):
            known_digits[pos] = digit
            break
```

**Why it works:** Each unknown digit affects a different decimal scale in the output number. The largest unknown (earliest position) shifts the inverted value by the most, determining several bytes of the flag. Fixing it and moving to the next unknown reveals more bytes. Total work: `10 * num_unknowns` inversions (linear, not exponential).

**Precision matching:** SageMath's `RealField(N)` uses MPFR with N-bit mantissa. In mpmath, set `mp.prec = N` (NOT `mp.dps`). The last few output digits are precision-sensitive and will only match with the correct binary precision.

**Derivative analysis:** For the spiral-type map `x → r*sqrt(x²+1) + (1-r)*(x+φ)`, the per-step derivative is `r*x/sqrt(x²+1) + (1-r) ≈ 1`, so the total derivative stays near 1 across all 81 iterations. This means precision is preserved through inversion — 67 known output digits give ~67 digits of input precision.

**References:** 0xL4ugh CTF "SpiralFloats"

---

## Tropical Semiring Residuation Attack (BearCatCTF 2026)

**Pattern (Tropped):** Diffie-Hellman key exchange using tropical matrices (min-plus algebra). Per-character shared secret XOR'd with encrypted flag.

**Tropical algebra:**
- Addition = `min(a, b)`
- Multiplication = `a + b`
- Matrix multiply: `(A*B)[i,j] = min_k(A[i,k] + B[k,j])`

**Tropical residuation recovers shared secret from public data:**
```python
def tropical_residuate(M, Mb, aM, n):
    """Recover shared secret from public matrices.
    M = public matrix, Mb = M*b (Bob's public), aM = a*M (Alice's public)
    """
    # Right residual: b*[j] = max_i(Mb[i] - M[i][j])
    b_star = [max(Mb[i] - M[i][j] for i in range(n)) for j in range(n)]
    # Shared secret: aMb = min_j(aM[j] + b*[j])
    aMb = min(aM[j] + b_star[j] for j in range(n))
    return aMb

# Decrypt per-character: key = aMb % 32; plaintext = key ^ ciphertext
for i, enc_char in enumerate(encrypted):
    key = shared_secret % 32
    plaintext_char = chr(key ^ ord(enc_char))
```

**Key insight:** Tropical DH is broken because the min-plus semiring lacks cancellation — given `M` and `M*b`, the "residual" `b*` can be computed directly via `max(Mb[i] - M[i][j])`. Unlike standard DH where recovering `b` from `g^b` is hard, tropical residuation recovers enough of `b`'s effect to compute the shared secret. This makes tropical matrix DH insecure for any matrix size.

**Detection:** Challenge mentions "tropical", "min-plus", "exotic algebra", or defines custom matrix multiplication using `min` and `+`.

---

## Paillier Cryptosystem Attack (SECCON 2015)

The Paillier cryptosystem is a homomorphic encryption scheme where `c = g^m * r^n mod n^2`. When given oracle equations involving c, o, h values:

1. **Recover n:** Compute lower bound `sqrt(max(c, o, h))` to approximate n, then brute-force nearby values
2. **Validate n:** Check equation `h = (c * o) % (n^2)` for correctness
3. **Factor n:** Use standard methods (e.g., factordb) to find p, q
4. **Decrypt:** Apply Paillier decryption:

```python
from sympy import lcm, mod_inverse

# n = p * q (factored)
lam = lcm(p - 1, q - 1)  # Carmichael function
n2 = n * n

def L(x):
    return (x - 1) // n

# Compute mu
g_lam = pow(g, lam, n2)
mu = mod_inverse(L(g_lam), n)

# Decrypt
c_lam = pow(c, lam, n2)
m = (L(c_lam) * mu) % n
```

**Key insight:** Paillier operates mod n^2, so ciphertext values are much larger than RSA. The homomorphic property `E(m1) * E(m2) = E(m1 + m2)` can leak relationships between plaintexts.

---

## Hamming Code Error Correction with Helical Interleaving (Sharif CTF 2016)

When data is protected by Hamming(31,26) codes with helical scan interleaving:

1. **Determine matrix dimensions:** Brute-force width/height (30x30 search space) by testing which dimensions produce valid Hamming codewords
2. **Read data in helical pattern:** Extract bits diagonally from the interleaved matrix
3. **Apply Hamming parity check:** Multiply codeword by parity check matrix H to detect/correct errors

```python
import numpy as np

def check_hamming(codeword, H):
    """Syndrome = H * c^T; zero syndrome means valid codeword"""
    syndrome = np.dot(H, codeword) % 2
    return np.all(syndrome == 0)

# Brute-force dimensions
for w in range(1, 31):
    for h in range(1, 31):
        # Reshape data into w x h matrix
        matrix = data[:w*h].reshape(h, w)
        # Read diagonals (helical scan)
        bits = read_helical(matrix)
        # Check if bits form valid Hamming codewords
        if validate_hamming_stream(bits, H):
            print(f"Dimensions: {w}x{h}")
```

**Key insight:** Try 8 different bit alignment offsets when the start position is unknown. Valid Hamming codewords have zero syndrome under multiplication by the parity check matrix.

---

## ElGamal Universal Re-encryption (Sharif CTF 2016)

Given an ElGamal-like ciphertext tuple (a, b, c, d) = (g^r, h^r, g^s, m*h^s), produce a different valid ciphertext decrypting to the same message without knowing the private key:

Transform exponents r -> 2r, s -> r+s:

```python
def reencrypt(a, b, c, d, p):
    return [
        (a * a) % p,    # g^(2r)
        (b * b) % p,    # h^(2r)
        (a * c) % p,    # g^(r+s)
        (d * b) % p     # m*h^(r+s)
    ]
```

**Key insight:** ElGamal's homomorphic property allows re-randomizing ciphertexts by multiplying components. The relationship between exponents must remain consistent: both pairs must share the same exponent offset.

---

## Paillier Oracle Size Bypass via Ciphertext Factoring (BSidesSF 2025)

When a Paillier decryption oracle rejects messages exceeding a size limit (e.g., >2000 bits), exploit the homomorphic property to factor the encrypted flag into smaller pieces:

1. **Paillier additive homomorphism:** `E(m1) * E(m2) mod n^2 = E(m1 + m2 mod n)`
2. **Multiplicative (scalar):** `E(m)^k mod n^2 = E(k*m mod n)`
3. **Factoring ciphertext:** Divide n into small ranges, query oracle with `E(flag) * E(-offset)^1` to determine which range contains the flag
4. **Chunk extraction:** Split the flag value into pieces that each fit within the oracle's size limit, decrypt individually, sum to recover original

```python
from Crypto.Util.number import inverse

def paillier_sub(c, plaintext_sub, n):
    """Compute E(m - plaintext_sub) from E(m) using homomorphic property"""
    n2 = n * n
    # E(-plaintext_sub) = E(n - plaintext_sub) = (n+1)^(n-plaintext_sub) * r^n mod n^2
    neg_enc = pow(n + 1, n - plaintext_sub, n2)
    return (c * neg_enc) % n2

# Binary search for flag value using oracle
def recover_flag(enc_flag, n, oracle_decrypt):
    low, high = 0, n
    while high - low > 1:
        mid = (low + high) // 2
        test_ct = paillier_sub(enc_flag, mid, n)
        result = oracle_decrypt(test_ct)
        if result < n // 2:  # Positive (flag > mid)
            low = mid
        else:  # Negative (flag < mid, wraps around)
            high = mid
    return low
```

**Key insight:** Paillier's additive homomorphism allows computing `E(flag - offset)` without decryption. If the oracle reveals whether the decrypted value is "small" (within limit) or "large" (rejected/wraps), binary search recovers the flag in O(log n) queries.

---

## Format-Preserving Encryption Feistel Brute-Force (BSidesSF 2026)

**Pattern (tokencrypt):** Format-preserving encryption (FPE) using a Feistel network with a small round key. The 96-bit key splits into three components with different roles: a brute-forceable core, a GF(2) mixing matrix, and an affine offset.

**Key structure:**
- `s` (16 bits): Feistel round subkey — only 2^16 = 65536 possibilities
- `seed56` (56 bits): Generates an invertible GF(2) affine mixing matrix `M` (24x24)
- `b24` (24 bits): Affine offset applied after mixing

**Attack:**
1. **Collect encrypt pairs:** Get multiple `(plaintext, ciphertext)` pairs from the FPE oracle
2. **Brute-force `s`:** For each of 65536 candidate round keys, run the Feistel network on known plaintexts. If the Feistel core is correct, the remaining transformation is affine over GF(2)
3. **Solve linear system:** With correct `s`, the relationship `ciphertext = M * feistel_output XOR b24` is linear. Collect 24+ pairs, build a GF(2) matrix equation, solve for `M` and `b24` via Gaussian elimination

```python
import numpy as np

def feistel_encrypt(pt_24bit, s, rounds=3):
    """24-bit Feistel with 16-bit round key s."""
    L, R = pt_24bit >> 12, pt_24bit & 0xFFF
    for r in range(rounds):
        f = (R * s + r) & 0xFFF  # Round function (example)
        L, R = R, L ^ f
    return (L << 12) | R

# Brute-force s (16-bit)
for s_candidate in range(1 << 16):
    feistel_outputs = [feistel_encrypt(pt, s_candidate) for pt in known_pts]
    # Check if feistel_outputs -> known_cts is affine over GF(2)
    # Build system: for each bit position, collect equations
    # If consistent -> found correct s, solve for M and b24
```

**When to recognize:** Challenge mentions "format-preserving encryption", "FPE", or uses a Feistel structure with suspiciously small key components. Any round key under 32 bits is brute-forceable.

**Key lessons:**
- FPE with small Feistel round keys is trivially broken despite the total key looking large (96 bits)
- After recovering the Feistel core, the remaining affine layer is solvable as a linear system over GF(2)
- Collect enough plaintext-ciphertext pairs to overdetermine the linear system

**References:** BSidesSF 2026 "tokencrypt"

---

## Icosahedral Symmetry Group Cipher (BSidesSF 2026)

**Pattern (dodecacrypt):** Encryption maps message bytes to face permutations of a dodecahedron. The icosahedral symmetry group has order 120 (the rotation group of a regular dodecahedron/icosahedron), so each "digit" in base-120 encodes one group element as a specific arrangement of 12 face labels.

**How it works:**
1. Message is converted to a large integer and expressed in base 120
2. Each base-120 digit selects one of 120 possible face permutations
3. The dodecahedron is rendered from a fixed viewing angle, showing only 6 of 12 faces
4. Despite only 6 faces being visible, collisions between the 120 permutations are rare enough for unique recovery

**Attack:**
1. **Build lookup table:** Probe the encryption API with all 120 single-digit inputs (0-119 in base 120), capture the rendered face arrangement for each
2. **Match visible faces:** For each encrypted symbol in the ciphertext, compare the visible face pattern against the lookup table to recover the base-120 digit
3. **Reconstruct message:** Convert the sequence of base-120 digits back to an integer, then to bytes

```python
import itertools

# Build lookup: probe API with single-digit values
lookup = {}
for digit in range(120):
    # Send digit, capture 6 visible face labels from rendered image
    visible = get_visible_faces(encrypt_single(digit))
    lookup[tuple(visible)] = digit

# Decrypt ciphertext
base120_digits = []
for symbol in ciphertext_symbols:
    visible = get_visible_faces(symbol)
    base120_digits.append(lookup[tuple(visible)])

# Convert base-120 to bytes
value = sum(d * 120**i for i, d in enumerate(reversed(base120_digits)))
plaintext = value.to_bytes((value.bit_length() + 7) // 8, 'big')
```

**When to recognize:** Challenge involves polyhedra, dodecahedra, icosahedra, or mentions "120 rotations", "symmetry group", or shows 3D-rendered geometric objects with labeled faces.

**Key insight:** The icosahedral rotation group is small enough (order 120) that a complete lookup table fits easily in memory. Even with partial information (only 6 of 12 faces visible), the permutations are sufficiently distinct to avoid collisions in practice.

**References:** BSidesSF 2026 "dodecacrypt"

---

## Goldwasser-Micali Ciphertext Replication Oracle (BSidesSF 2026)

**Pattern (kproof):** A "proof of knowledge" protocol encrypts a user-chosen AES key using Goldwasser-Micali (GM) bit-by-bit encryption. The service decrypts GM ciphertext bits to reconstruct the AES key, then uses it to decrypt and hash a probe payload. The vulnerability: individual GM ciphertext values can be replayed, and 128 copies of the same GM-encrypted bit produce an AES key of either `0x00...00` or `0xFF...FF`.

**Goldwasser-Micali basics:**
- Encrypts one bit at a time: bit 0 → quadratic residue mod n, bit 1 → non-residue
- Decryption tests whether each ciphertext value is a quadratic residue
- Each ciphertext value independently encodes exactly one bit

**The vulnerability:**
The service accepts 128 GM ciphertext lines as the AES key. By sending the SAME GM ciphertext value 128 times, the decrypted key is either all-zeros (if the bit was 0) or all-ones (if the bit was 1). Since you control the probe plaintext and IV, you can precompute both possible SHA-256 hashes and compare against the service response.

**Attack (128 oracle queries for full key recovery):**

```python
from Crypto.Cipher import AES
import hashlib

def recover_bit(gm_ciphertext_line, probe_ct, probe_iv, oracle):
    """Determine if a single GM ciphertext encodes 0 or 1."""
    # Replicate the single GM bit 128 times as the AES key
    key_all_zero = b'\x00' * 16
    key_all_ones = b'\xff' * 16

    # Precompute expected hashes for both possible keys
    hash0 = hashlib.sha256(
        AES.new(key_all_zero, AES.MODE_CBC, probe_iv).decrypt(probe_ct)
    ).hexdigest()
    hash1 = hashlib.sha256(
        AES.new(key_all_ones, AES.MODE_CBC, probe_iv).decrypt(probe_ct)
    ).hexdigest()

    # Query oracle with replicated GM line
    result_hash = oracle.query(gm_ciphertext_line, copies=128)

    if result_hash == hash0:
        return 0
    elif result_hash == hash1:
        return 1

# Recover all 128 bits of the AES key
captured_gm_lines = parse_transcript(transcript)  # 128 GM ciphertext values
key_bits = [recover_bit(line, probe_ct, probe_iv, oracle)
            for line in captured_gm_lines]

# Reconstruct AES key and decrypt the captured payload
aes_key = bits_to_bytes(key_bits)
plaintext = AES.new(aes_key, AES.MODE_CBC, captured_iv).decrypt(captured_ct)
```

**Key insight:** Goldwasser-Micali's bit-by-bit encryption means each ciphertext value independently encodes one bit. If a protocol allows replaying individual GM values as components of a larger key, each bit can be isolated and determined via a distinguishing oracle (here, SHA-256 hash comparison). This reduces key recovery from 2^128 brute-force to 128 linear queries.

**When to recognize:** Challenge uses bit-by-bit public-key encryption (GM, Rabin) combined with a symmetric key derivation step. The service decrypts individual ciphertext values without binding them to a position or preventing replay.

**Broader principle:** Any protocol that (1) encrypts a key bit-by-bit and (2) provides an oracle on the reconstructed key is vulnerable to bit-by-bit recovery via replication. The specific oracle (hash, decryption check, timing) varies but the attack structure is the same.

**References:** BSidesSF 2026 "kproof"

---

## BB-84 Quantum Key Distribution MITM Attack (PlaidCTF 2017)

**Pattern:** In simulated BB-84 QKD without authentication, perform a full man-in-the-middle by independently negotiating with both Alice and Bob.

```python
# Strategy: Always use basis Z, always send value 1 to Bob
# Alice side: measure in random bases, record results
# Bob side: always receives 1 in basis Z
# Bob's key = all 1s (known to attacker)
# Alice's key = attacker's measured qbit values

# Heuristic: throttle Bob's correct-guess count to match Alice's
# Both parties verify by comparing subset of bits — attacker controls both sides
for qbit in alice_qbits:
    my_basis = 'Z'  # always measure in Z basis
    my_value = measure(qbit, my_basis)
    send_to_bob(basis='Z', value=1)  # always send 1

# After basis reconciliation:
# key_with_alice = [measured values where bases matched]
# key_with_bob = [all 1s]
```

**Key insight:** BB-84 QKD is secure only with authenticated classical channels. Without authentication, an attacker can independently negotiate keys with both parties. Forcing a constant value to one party makes their key entirely predictable, while the other party's key is captured through measurement.

**References:** PlaidCTF 2017

---

## ElGamal Trivial DLP When B = p-1 (Hack.lu 2017)

**Pattern:** ElGamal public key `B = g^key mod p`. If `B + 1 == p`, then `B = p-1 = -1 mod p`. By Euler's criterion, `g^((p-1)/2) ≡ -1 (mod p)` for any primitive root `g`. Therefore `g^key ≡ g^((p-1)/2) (mod p)`, so `key = (p-1)/2` directly. No DLP algorithm needed.

```python
# Check for trivial case
if (B + 1) == p:
    key = (p - 1) // 2
    # Verify
    assert pow(g, key, p) == B
    # Decrypt ElGamal: shared_secret = pow(ephemeral, key, p)
```

**Key insight:** The generator raised to `(p-1)/2` always equals `-1 mod p` (Euler's criterion for quadratic residues). When the public key `B` equals `p-1`, the private key is trivially `(p-1)/2`. Always check `B == p-1` (and `B == 1` for key=0) before attempting general DLP.

**References:** Hack.lu CTF 2017

---

## Paillier LSB Oracle via Homomorphic Doubling (CODE BLUE 2017)

**Pattern:** Paillier encryption is additively homomorphic: multiplying a ciphertext by itself (`ct^2 mod n^2`) doubles the plaintext. Doubling repeatedly and observing when the LSB changes (due to modular reduction by n) reveals plaintext bits one at a time — a binary search identical to the RSA LSB oracle.

**Attack (bit-by-bit recovery from MSB to LSB):**
```python
def paillier_double(ct, n):
    """Homomorphically double the plaintext."""
    return pow(ct, 2, n * n)

def recover_plaintext(ct, oracle_lsb, n):
    """Oracle returns LSB of decrypted plaintext."""
    lower, upper = 0, n
    current_ct = ct
    for _ in range(n.bit_length()):
        current_ct = paillier_double(current_ct)
        lsb = oracle_lsb(current_ct)
        mid = (lower + upper) // 2
        if lsb == 1:
            lower = mid  # plaintext > n/2, wraparound occurred
        else:
            upper = mid
    return lower

# Alternative: homomorphic subtraction to isolate each bit
def paillier_encrypt_scalar(m, n, g=None):
    """Encrypt scalar m under Paillier (with r=1 for known randomness)."""
    g = g or (n + 1)
    return pow(g, m, n * n)  # simplified (r=1)

def subtract_plaintext(ct, val, n):
    """Compute E(pt - val) = ct * E(-val) mod n^2."""
    neg_enc = paillier_encrypt_scalar(n - val, n)
    return (ct * neg_enc) % (n * n)
```

**Key insight:** Paillier's additive homomorphism enables a binary search oracle: doubling the plaintext via `ct^2` and observing LSB changes reveals one bit per query. Equivalently, use homomorphic subtraction of known masks to isolate each bit. Total queries: log2(n) ≈ 2048 for 2048-bit modulus.

**References:** CODE BLUE CTF 2017

---

## Differential Privacy Laplace Noise Cancellation (Pwn2Win 2017)

**Pattern:** Server implements differential privacy by adding Laplace noise (mean 0, scale λ) to character ordinals before returning them. Since Laplace noise has zero mean, querying the same position many times and averaging the results cancels the noise via the Law of Large Numbers.

```python
import requests
import statistics

def recover_char(position, num_queries=1000):
    """Average 1000 noisy responses to cancel Laplace noise."""
    samples = []
    for _ in range(num_queries):
        noisy_val = query_server(position)
        samples.append(noisy_val)
    # Mean converges to true value as queries → ∞
    true_val = round(statistics.mean(samples))
    return chr(true_val)

flag = ''.join(recover_char(i) for i in range(flag_length))
```

**Key insight:** Laplace differential privacy with zero mean is breakable with sufficient queries — averaging N samples reduces noise variance by factor N (standard error ∝ 1/sqrt(N)). With λ=1 and 1000 queries, the mean is within ±0.1 of the true value. Round to nearest integer to recover the exact character ordinal. This applies to any additive zero-mean noise mechanism.

**References:** Pwn2Win CTF 2017

---

## Homomorphic Encryption Oracle Bit-Extraction (Tokyo Westerns 2017)

**Pattern:** An encryption oracle has homomorphic properties — you can add 1 to the plaintext by performing a known operation on the ciphertext. Extract bits from an unknown plaintext by observing how the ciphertext changes as the plaintext value crosses power-of-2 boundaries.

**Low-bit extraction (observe overflow):**
```python
# Increment plaintext by 1 repeatedly via homomorphic add-1
# Detect when bit N overflows: ciphertext "wraps" at value 2^N
ct = target_ciphertext
for bit_pos in range(num_bits):
    threshold = 2 ** bit_pos
    # Add 1 repeatedly until bit flips
    increments = 0
    prev_ct = ct
    while True:
        ct = homomorphic_add_one(ct)
        increments += 1
        if bit_has_flipped(ct, prev_ct, bit_pos):
            low_bits = (threshold - increments) % threshold
            break
```

**High-bit extraction (divide by 2 on even values):**
```python
# Subtract recovered low bits to make value even
even_ct = homomorphic_subtract(target_ct, low_bits)
# Repeatedly divide by 2 and observe the resulting high bits
for i in range(high_bit_count):
    even_ct = homomorphic_halve(even_ct)
    high_bits = (high_bits << 1) | observe_lsb(even_ct)
```

**Key insight:** Homomorphic oracles enable bit-extraction: detect overflow in specific bit positions when incrementing for low bits; use division-by-2 on even numbers for high bits. The total number of queries scales linearly with the bit count of the plaintext.

**References:** Tokyo Westerns CTF 2017


# historical

# CTF Crypto - Historical Ciphers

## Table of Contents
- [Lorenz SZ40/42 (Tunny) Cipher](#lorenz-sz4042-tunny-cipher)
- [Book Cipher Brute Force (Nullcon 2026)](#book-cipher-brute-force-nullcon-2026)

---

## Lorenz SZ40/42 (Tunny) Cipher

The Lorenz cipher uses 12 wheels to encrypt 5-bit ITA2/Baudot characters. With known plaintext, a structured attack recovers all wheel settings.

**Machine structure:**
- 5 χ (chi) wheels: periods 41, 31, 29, 26, 23 — advance every step
- 5 Ψ (psi) wheels: periods 43, 47, 51, 53, 59 — advance only when μ37=1
- μ61 wheel: period 61 — advances every step, controls μ37 stepping
- μ37 wheel: period 37 — advances only when μ61=1, controls Ψ stepping

**Encryption:** `ciphertext[i] = plaintext[i] XOR chi[i] XOR psi[i]` (per 5-bit character)

**CRITICAL: The delta (Δ) approach is the fundamental technique:**

```python
# Step 1: Get keystream from known plaintext
key_stream = [pt[i] ^ ct[i] for i in range(N)]

# Step 2: Compute delta keystream (THE key insight)
delta_k = [key_stream[i] ^ key_stream[i+1] for i in range(N-1)]
# delta_k = delta_chi XOR delta_psi
# Since psi only moves ~25% of the time, delta_k BIASES toward delta_chi

# Step 3: Recover delta_chi via majority vote at each wheel position
# Assume wheels start at position 1
for bit in range(5):
    P = chi_periods[bit]  # [41, 31, 29, 26, 23]
    delta_chi = []
    for phase in range(P):
        # Collect all delta_k values at this wheel phase
        vals = [delta_k_bit[i] for i in range(phase, len(delta_k_bit), P)]
        delta_chi.append(1 if sum(vals) > len(vals)/2 else 0)

# Step 4: Integrate delta_chi to get chi (2 candidates per wheel, start 0 or 1)
chi = [start]  # start = 0 or 1
for i in range(P-1):
    chi.append(chi[-1] ^ delta_chi[i])
# Circular consistency: chi[0] ^ chi[-1] should equal delta_chi[P-1]

# Step 5: Subtract chi from keystream to get psi contribution
# Identify when psi steps: delta_psi = delta_k XOR delta_chi
# When ALL 5 bits of delta_psi are 0 → μ37 was off (psi didn't step)
# (Statistically very rare for all 5 cams to not change when stepping)

# Step 6: From stepping pattern, determine μ61 (period 61)
# μ61[pos] = 1 when we see psi resume stepping after being stopped

# Step 7: Cross-reference to get μ37 (period 37)
# μ37 position advances only when μ61=1

# Step 8: Determine psi wheels from delta_psi values when stepping occurs
# Look for repeating patterns with periods 43, 47, 51, 53, 59

# Step 9: Brute force remaining ambiguity
# Total candidates: 2^5 (chi) × 2^5 (psi) × 61×37 (μ positions) = 2,313,472
# Trivially brutable - decrypt and check if known plaintext matches
```

**Common mistakes to avoid:**
- Do NOT assume psi is "period 2" or just alternating — it has real wheels with periods 43-59
- Do NOT spend time on statistical period-finding for the motor — just use the structured Δ approach
- Do NOT try LFSR analysis on the step sequence — the stepping is from mechanical wheels, not LFSRs
- The "step rate" (~35%) is a consequence of μ37 being on ~50% and μ61 on ~50% = ~25% psi stepping
- Always assume standard wheel periods unless evidence says otherwise
- Total brute force space is tiny (<3M) — don't over-optimize

**ITA2/Baudot encoding (5-bit):**
```python
# Standard ITA2 mapping used in Lorenz challenges
char_to_code = {
    'A': 24, 'B': 19, 'C': 14, 'D': 18, 'E': 16, 'F': 22, 'G': 11,
    'H': 5,  'I': 12, 'J': 26, 'K': 30, 'L': 9,  'M': 7,  'N': 6,
    'O': 3,  'P': 13, 'Q': 29, 'R': 10, 'S': 20, 'T': 1,  'U': 28,
    'V': 15, 'W': 25, 'X': 23, 'Y': 21, 'Z': 17,
    '9': 4,  '5': 27, '8': 31, '3': 8,  '4': 2,  '/': 0,
}
# Code 27 = FIGS shift, Code 31 = LTRS shift
```

---

## Book Cipher Brute Force (Nullcon 2026)

**Pattern (Booking Key):** Book cipher encodes password as list of "steps forward" in reference text.

**Key insight:** Charset constraint drastically reduces candidate starting positions:
```python
def decode_book_cipher(cipher_distances, book_text, valid_chars):
    """Brute-force starting position; filter by charset."""
    candidates = []
    for start_key in range(len(book_text)):
        pos = start_key
        password = []
        valid = True
        for dist in cipher_distances:
            pos = (pos + dist) % len(book_text)
            ch = book_text[pos]
            if ch not in valid_chars:
                valid = False
                break
            password.append(ch)
        if valid:
            candidates.append((start_key, ''.join(password)))
    return candidates  # Typically 3-4 candidates out of ~56k positions
```


# lattice-and-lwe

# CTF Crypto - Lattice and LWE Attacks

## Table of Contents
- [Quick Triage: Is This a Lattice Problem?](#quick-triage-is-this-a-lattice-problem)
- [Core Tools: LLL, BKZ, Babai, CVP, SVP](#core-tools-lll-bkz-babai-cvp-svp-asis-ctf-finals-2015-ctfzone-2017)
  - [LLL](#lll)
  - [BKZ](#bkz)
  - [Babai nearest plane](#babai-nearest-plane)
  - [CVP vs SVP](#cvp-vs-svp)
- [Hidden Number Problem (HNP): Partial Nonce / Biased Nonce](#hidden-number-problem-hnp-partial-nonce--biased-nonce-nullcon-hackim-2020-ledger-donjon-ctf-2020)
  - [Minimal ECDSA partial-nonce workflow](#minimal-ecdsa-partial-nonce-workflow)
- [LCG and Truncated Output as a Lattice Problem](#lcg-and-truncated-output-as-a-lattice-problem-x-mas-ctf-2018-fwordctf-2020)
  - [Minimal truncated-LCG workflow](#minimal-truncated-lcg-workflow)
- [LWE via Embedding and CVP](#lwe-via-embedding-and-cvp-plaidctf-2016-aero-ctf-2020)
  - [Embedding-style lattice](#embedding-style-lattice)
  - [For ternary or sparse secrets](#for-ternary-or-sparse-secrets)
- [Ring-LWE / Module-LWE Recognition Notes](#ring-lwe--module-lwe-recognition-notes-plaidctf-2016-dicectf-2022)
  - [Flattening Ring-LWE to plain LWE](#flattening-ring-lwe-to-plain-lwe)
- [Orthogonal Lattices: HSSP / AHSSP Style Recovery](#orthogonal-lattices-hssp--ahssp-style-recovery-zer0pts-ctf-2022)
- [Subset Sum / Knapsack via Lattice Reduction](#subset-sum--knapsack-via-lattice-reduction-hitcon-ctf-2017-backdoorctf-2023)
- [Common Failure Modes](#common-failure-modes)
- [Quick Checklist Before You Commit to Lattices](#quick-checklist-before-you-commit-to-lattices)

---

## Quick Triage: Is This a Lattice Problem?

Use lattice tools when the challenge gives you:

- many modular equations plus a promise that the hidden values are small, sparse, or close to each other
- partial leakage of a secret nonce, seed, or state bits
- linear relations with bounded error terms
- vectors or matrices over `Z_q` where the true solution should be unusually short
- a subset-sum or knapsack instance that "looks too structured"

Typical CTF phrasing:

- "high bits of k are known"
- "the error is small"
- "the secret coefficients are in {-1,0,1}"
- "recover seed from truncated outputs"
- "find a short vector"
- "solve noisy linear equations modulo q"

**First question to ask:** what is supposed to be small?

- the secret itself
- the error vector
- the nonce difference
- a subset indicator vector in `{0,1}^n`
- a correction term caused by modular wraparound

That "small thing" is usually what the lattice is trying to expose.

---

## Core Tools: LLL, BKZ, Babai, CVP, SVP (ASIS CTF Finals 2015, CTFZone 2017)

### LLL

Default first move. Fast, easy, often enough for CTF-sized parameters.

Use it when:

- dimensions are moderate
- the hidden vector is very short
- the challenge author clearly expects a standard embedding attack
- you want structure first, exact recovery second

```python
from sage.all import Matrix, ZZ

M = Matrix(ZZ, basis_rows)
R = M.LLL()
print(R[0])
```

### BKZ

Use when LLL almost works but not quite.

- better for harder CVP/SVP instances
- useful when the gap between the target vector and random lattice vectors is small
- in CTFs, `BKZ(block_size=20..35)` is often already enough

```python
R = M.BKZ(block_size=25)
```

### Babai nearest plane

Good for approximate CVP after reduction.

- reduce basis with `LLL` or `BKZ` first
- then apply Babai to recover the nearby vector
- often enough for ternary or small-error LWE

```python
from fpylll import IntegerMatrix, CVP

# After building and reducing the lattice basis:
closest = CVP.babai(B, target)
```

### CVP vs SVP

- **SVP:** "find an unusually short non-zero lattice vector"
- **CVP:** "find the lattice vector closest to a target"

Rule of thumb:

- if you only know "some relation must be very short", think SVP / embedding
- if you already have a target vector and want the nearest valid lattice point, think CVP / Babai

---

## Hidden Number Problem (HNP): Partial Nonce / Biased Nonce (nullcon HackIM 2020, Ledger Donjon CTF 2020)

**Pattern:** signatures or RNG equations leak a few bits of a hidden value `k`, or `k` is sampled from a small / biased range.

This is the classic route from:

- ECDSA partial nonce leakage
- Schnorr biased nonce leakage
- custom congruence systems where only high bits or low bits are known

Generic shape:

`a_i * x + b_i ≡ e_i (mod q)`

where:

- `x` is the secret key
- `e_i` is small or partially known

That "small error" is what turns the problem into a lattice instance.

**When to use:**

- repeated signatures with leaked high bits / low bits of `k`
- same signing scheme with biased or short nonces
- LCG-like recurrence where each output leaks only part of the internal state

**Practical workflow:**

1. normalize all equations so the secret key is the same unknown in every row
2. isolate the bounded error term
3. scale rows so all coordinates have comparable size
4. run `LLL`
5. test the candidate secret against the original equations

Skeleton:

```python
from sage.all import Matrix, ZZ

def build_hnp_lattice(q, coeffs, bounds):
    n = len(coeffs)
    rows = []
    for i in range(n):
        row = [0] * (n + 1)
        row[i] = q
        rows.append(row)

    last = [c for c in coeffs] + [bounds]
    rows.append(last)
    return Matrix(ZZ, rows)
```

**Key insight:** HNP attacks usually do not require a perfect lattice model. In CTFs, once the true secret produces a vector much shorter than random noise, `LLL` often exposes it directly or gets you close enough to brute-force the last few bits.

### Minimal ECDSA partial-nonce workflow

If a challenge leaks the top bits of each nonce `k_i`, write:

`k_i = leaked_i * 2^t + delta_i`

where `delta_i` is small. For ECDSA:

`s_i * k_i - h_i ≡ r_i * d (mod q)`

Substitute the leaked form of `k_i`:

`r_i * d - s_i * delta_i ≡ s_i * leaked_i * 2^t - h_i (mod q)`

Now the unknowns are:

- the private key `d`
- a set of small corrections `delta_i`

That is the lattice hook.

Minimal starter code:

```python
from sage.all import Matrix, ZZ

def build_ecdsa_partial_nonce_lattice(q, rs, ss, hs, leaked, t):
    n = len(rs)
    M = Matrix(ZZ, n + 2, n + 2)

    for i in range(n):
        M[i, i] = q

    for i in range(n):
        M[n, i] = ss[i]
        M[n + 1, i] = (hs[i] - ss[i] * leaked[i] * (1 << t)) % q

    M[n, n] = 1
    M[n + 1, n + 1] = q // (1 << t)
    return M
```

What to do next:

1. build the lattice
2. run `LLL`
3. inspect short rows for a plausible `d`
4. verify `d` against all signatures
5. if one or two bits are off, brute-force the remaining uncertainty

**When this works best:** many signatures, enough leaked bits per nonce, and a single long-term signing key shared across all samples.

---

## LCG and Truncated Output as a Lattice Problem (X-MAS CTF 2018, FwordCTF 2020)

**Pattern:** internal state follows an affine recurrence, but you only see:

- high bits
- low bits
- several states with unknown parameters
- several consecutive outputs plus a small hidden correction

Typical examples:

- unknown seed, known modulus
- known modulus, known `a`, known `b`, only top bits of outputs
- unknown `a`, unknown `b`, several exact or truncated outputs

The trick is to rewrite:

`state_i = observed_i * 2^t + hidden_i`

where `hidden_i` is small. Then the recurrence becomes a modular linear relation in those small hidden values.

**When to use:**

- high-bit leakage from LCG states
- recurrence modulo a large prime
- multiple consecutive outputs
- exact algebra seems messy but every step differs only by a small hidden remainder

**Key insight:** truncated-state recovery is often just HNP wearing different clothes. If the unknown carries per row are small enough, the lattice will expose them.

### Minimal truncated-LCG workflow

Suppose:

`x_{i+1} = a*x_i + b (mod m)`

but the service leaks only the high bits:

`y_i = x_i >> t`

Then write:

`x_i = y_i * 2^t + z_i`

where `z_i` is the hidden low-bit part and is small.

Plugging into the recurrence gives:

`y_{i+1} * 2^t + z_{i+1} ≡ a*(y_i * 2^t + z_i) + b (mod m)`

Rearrange:

`z_{i+1} - a*z_i ≡ a*y_i*2^t + b - y_{i+1}*2^t (mod m)`

Now the unknowns are the small `z_i`. That is exactly the kind of bounded modular relation lattices like.

Minimal starter code:

```python
from sage.all import Matrix, ZZ

def build_truncated_lcg_lattice(m, a, b, ys, t):
    n = len(ys) - 1
    M = Matrix(ZZ, n + 1, n + 1)

    for i in range(n):
        M[i, i] = m

    for i in range(n):
        rhs = (a * ys[i] * (1 << t) + b - ys[i + 1] * (1 << t)) % m
        M[n, i] = rhs

    M[n, n] = 1 << t
    return M
```

What to do next:

1. use several consecutive outputs
2. run `LLL`
3. recover candidate low bits `z_i`
4. reconstruct full states `x_i`
5. verify the recurrence exactly

**When this works best:** modulus is known, leakage is consecutive, and the hidden low part is much smaller than the modulus.

---

## LWE via Embedding and CVP (PlaidCTF 2016, Aero CTF 2020)

**Pattern:** given `A`, `b`, modulus `q`, and the promise:

`b = A*s + e (mod q)`

where:

- `s` is small or sparse
- `e` is small

This is the standard LWE shape.

**Immediate checks:**

- are coefficients of `s` in `{-1,0,1}` or a tiny range?
- is the error noticeably smaller than `q`?
- does the challenge give many rows and only a few columns?
- does solving over the integers almost work except for modular wraparound?

### Embedding-style lattice

```python
from sage.all import Matrix, ZZ, identity_matrix, zero_matrix, block_matrix

def lwe_embedding(A, q):
    m, n = A.nrows(), A.ncols()
    top = block_matrix([[q * identity_matrix(m), zero_matrix(ZZ, m, n)]])
    bottom = block_matrix([[A.transpose(), identity_matrix(n)]])
    return block_matrix([[top], [bottom]])
```

Then:

- reduce the basis
- use Babai / nearest-plane on the target
- recover the short secret / error pair

### For ternary or sparse secrets

After CVP:

- map near-zero values back into `{-1,0,1}`
- test both endian choices
- test both "row vectors" and "column vectors" conventions

**Key insight:** many CTF LWE instances are intentionally below the "real cryptography" hardness line. The challenge is usually not defeating production-grade LWE, but noticing that the secret or error was chosen tiny enough for `LLL + Babai` to work.

---

## Ring-LWE / Module-LWE Recognition Notes (PlaidCTF 2016, DiceCTF 2022)

You should suspect Ring-LWE / Module-LWE when:

- objects are polynomials modulo `x^n ± 1`
- multiplication is cyclic or negacyclic convolution
- samples look like `(a(x), b(x)=a(x)s(x)+e(x))`
- coefficients are reduced modulo `q`

In many CTFs, the intended shortcut is not a full Ring-LWE attack, but one of these:

- coefficients are tiny enough to lift to integers directly
- the ring structure decouples into easier scalar problems
- the service leaks enough evaluations to turn the problem into plain LWE
- one representation bug breaks the intended hardness

**Practical advice:**

- first try to flatten the polynomial problem into vectors
- test coefficient embedding before chasing deeper algebra
- check whether NTT / inverse NTT is used incorrectly
- check sign conventions, endian order, and whether coefficients were centered into `[-q/2, q/2]`

### Flattening Ring-LWE to plain LWE

```python
from sage.all import Matrix, ZZ, vector

def ring_lwe_to_matrix(a_poly, n, q):
    """Flatten a(x) in Z_q[x]/(x^n+1) to its negacyclic rotation matrix."""
    coeffs = list(a_poly) + [0] * (n - len(list(a_poly)))
    rows = []
    for i in range(n):
        row = [0] * n
        for j in range(n):
            idx = (i - j) % n
            sign = -1 if (i - j) < 0 and ((i - j) % n) != 0 else 1
            # negacyclic: x^n = -1
            if j <= i:
                row[j] = coeffs[i - j]
            else:
                row[j] = -coeffs[n + i - j]
        rows.append(row)
    return Matrix(ZZ, rows)
# After flattening, treat as plain LWE: b_vec = A_mat * s_vec + e_vec (mod q)
```

**Key insight:** most Ring-LWE / Module-LWE CTF challenges are weakened by implementation mistakes, tiny errors, or over-structured secrets. Flatten to plain LWE first and check whether standard lattice tools solve it before pursuing ring-specific attacks.

---

## Orthogonal Lattices: HSSP / AHSSP Style Recovery (zer0pts CTF 2022)

**Pattern:** you do not directly know the secret matrix or subset, but you can construct vectors that should be orthogonal to it modulo `M` or `p`.

This often appears in hidden-subset style problems:

- recover a hidden binary matrix
- recover a hidden low-weight subspace
- reconstruct unknown rows from modular inner-product relations

Core workflow:

1. build a lattice whose short vectors represent orthogonal relations
2. reduce it
3. recover the orthogonal lattice
4. take the kernel / orthogonal complement
5. reduce again to expose the hidden binary or short basis

```python
from sage.all import Matrix, ZZ, identity_matrix, block_matrix

def orthogonal_lattice_recovery(H, M):
    """Recover hidden binary basis from h = alpha * A (mod M).

    H: observed matrix (k x n) over Z_M
    M: modulus
    Returns: LLL-reduced orthogonal lattice whose kernel reveals A.
    """
    k, n = H.nrows(), H.ncols()
    # Build lattice: [M*I_k | 0; H^T | I_n]
    top = block_matrix([[M * identity_matrix(k), Matrix(ZZ, k, n)]])
    bot = block_matrix([[H.change_ring(ZZ).transpose(), identity_matrix(n)]])
    L = block_matrix([[top], [bot]])
    L_reduced = L.LLL()
    # Short rows in the bottom-right block are orthogonal to the hidden basis
    return L_reduced
```

**When to use:**

- challenge gives `h = αA` or affine variants of that relation
- unknown matrix entries are in `{0,1}` or another tiny alphabet
- direct solving fails because the structure lives in an unknown subspace

**Key insight:** in these problems, the shortest vectors are not the answer itself. They are the doorway to the answer: first recover the orthogonal space, then turn back and reconstruct the hidden basis.

---

## Subset Sum / Knapsack via Lattice Reduction (HITCON CTF 2017, BackdoorCTF 2023)

**Pattern:** recover a binary vector `x_i ∈ {0,1}` such that:

`sum(a_i * x_i) = target`

This is the classic subset-sum / knapsack lattice setup.

Use it when:

- the instance is intentionally low-density
- the hidden vector is binary
- direct meet-in-the-middle is still too large

Skeleton:

```python
from sage.all import Matrix, ZZ

def knapsack_lattice(weights, target):
    n = len(weights)
    M = Matrix(ZZ, n + 1, n + 1)
    for i in range(n):
        M[i, i] = 1
        M[i, n] = weights[i]
    M[n, n] = -target
    return M
```

Then:

- run `LLL`
- look for a row whose last coordinate is `0`
- check whether the remaining coordinates are in `{0,1}` or `{−1,0,1}`

**Key insight:** the lattice is built so that the correct subset produces a vector with an abnormally small final coordinate. In easy CTF instances, that vector survives reduction.

---

## Common Failure Modes

- **Wrong scaling:** one coordinate dominates the basis and hides the short vector.
- **Wrong centering:** values should be mapped to `[-q/2, q/2]`, not kept in `[0, q)`.
- **Wrong orientation:** rows vs columns are swapped.
- **Too few samples:** the lattice exists, but not enough equations pin the secret down.
- **Noise too large:** `LLL` is not enough; try `BKZ`, better scaling, or a different embedding.
- **Mistaken problem type:** what looks like LWE may actually be plain linear algebra, CRT, or a bugged encoding problem.
- **Forgot brute-force finish:** lattice often gets you "almost correct"; the last few bits or signs may still need a tiny brute force.

---

## Quick Checklist Before You Commit to Lattices

- Can I write the unknown as "small secret" or "small error"?
- Is there a bounded term that should make one vector much shorter than random?
- Did I try centering coefficients?
- Did I test both row/column conventions?
- Did I try `LLL` first before building something more exotic?
- If `LLL` almost works, did I try `BKZ` or Babai?
- If the instance is polynomial-based, did I first flatten it into coefficient vectors?

If most answers are "yes", the challenge is very likely meant to be solved with lattice reduction.


# modern-ciphers-2

# CTF Crypto - Modern Cipher Attacks (Continued)

Hash-based attacks, protocol-level exploits, ECB oracles, Rabin/RSA parity attacks, and specialized cipher weaknesses. For core AES/CBC/padding oracle techniques, see [modern-ciphers.md](modern-ciphers.md). For stream cipher attacks (LFSR, RC4, XOR), see [stream-ciphers.md](stream-ciphers.md).

## Table of Contents
- [Blum-Goldwasser Bit-Extension Oracle (PlaidCTF 2013)](#blum-goldwasser-bit-extension-oracle-plaidctf-2013)
- [Hash Length Extension Attack (PlaidCTF 2014)](#hash-length-extension-attack-plaidctf-2014)
- [Compression Oracle / CRIME-Style Attack (BCTF 2015)](#compression-oracle--crime-style-attack-bctf-2015)
- [Hash Function Time Reversal via Cycle Detection (BSidesSF 2025)](#hash-function-time-reversal-via-cycle-detection-bsidessf-2025)
- [OFB Mode with Invertible RNG Backward Decryption (BSidesSF 2026)](#ofb-mode-with-invertible-rng-backward-decryption-bsidessf-2026)
- [Weak Key Derivation via Public Key Hash XOR (BSidesSF 2026)](#weak-key-derivation-via-public-key-hash-xor-bsidessf-2026)
- [HMAC-CRC Linearity Attack (Boston Key Party 2016)](#hmac-crc-linearity-attack-boston-key-party-2016)
- [DES Weak Keys in OFB Mode (Boston Key Party 2016)](#des-weak-keys-in-ofb-mode-boston-key-party-2016)
- [SRP (Secure Remote Password) Protocol Bypass via Modular Arithmetic (ASIS CTF Finals 2016)](#srp-secure-remote-password-protocol-bypass-via-modular-arithmetic-asis-ctf-finals-2016)
- [Modified AES S-Box Brute-Force Recovery (H4ckIT CTF 2016)](#modified-aes-s-box-brute-force-recovery-h4ckit-ctf-2016)
- [Square Attack on Reduced-Round AES (0CTF 2016)](#square-attack-on-reduced-round-aes-0ctf-2016)
- [AES-ECB Byte-at-a-Time Chosen Plaintext (ABCTF 2016)](#aes-ecb-byte-at-a-time-chosen-plaintext-abctf-2016)
- [AES-ECB Cut-and-Paste Block Manipulation (NDH Quals 2016)](#aes-ecb-cut-and-paste-block-manipulation-ndh-quals-2016)
- [AES-CBC IV Bit-Flip Authentication Bypass (Google CTF 2016)](#aes-cbc-iv-bit-flip-authentication-bypass-google-ctf-2016)
- [Rabin Cryptosystem LSB Parity Oracle (PlaidCTF 2016)](#rabin-cryptosystem-lsb-parity-oracle-plaidctf-2016)
- [PBKDF2 Pre-Hash Bypass for Long Passwords (BackdoorCTF 2016)](#pbkdf2-pre-hash-bypass-for-long-passwords-backdoorctf-2016)
- [MD5 Multi-Collision via Fastcol (BackdoorCTF 2016)](#md5-multi-collision-via-fastcol-backdoorctf-2016)
- [Custom Hash State Reversal via Known Intermediates (BackdoorCTF 2016)](#custom-hash-state-reversal-via-known-intermediates-backdoorctf-2016)
- [CRC32 Brute-Force for Small Payloads (BackdoorCTF 2016)](#crc32-brute-force-for-small-payloads-backdoorctf-2016)
- [Noisy RSA LSB Oracle with Post-Hoc Error Correction (SharifCTF 7 2016)](#noisy-rsa-lsb-oracle-with-post-hoc-error-correction-sharifctf-7-2016)
- [Sponge Hash Collision via Meet-in-the-Middle on Partial State (BKP 2017)](#sponge-hash-collision-via-meet-in-the-middle-on-partial-state-bkp-2017)
- [CBC IV Forgery + Block Truncation for Authentication Bypass (0CTF 2017)](#cbc-iv-forgery--block-truncation-for-authentication-bypass-0ctf-2017)
- [Padding Oracle to CBC Bitflip Command Injection (BSidesSF 2017)](#padding-oracle-to-cbc-bitflip-command-injection-bsidessf-2017)
- [SPN Cipher Partial Key Recovery via S-box Intersection (SharifCTF 7 2016)](#spn-cipher-partial-key-recovery-via-s-box-intersection-sharifctf-7-2016)
- [AES-CFB IV Recovery from Timestamp-Seeded PRNG (SHA2017)](#aes-cfb-iv-recovery-from-timestamp-seeded-prng-sha2017)
- [Three-Round XOR Protocol Key Cancellation (HITB 2017)](#three-round-xor-protocol-key-cancellation-hitb-2017)
- [AES-CBC UnicodeDecodeError Side-Channel Oracle (Kaspersky 2017)](#aes-cbc-unicodedecodeerror-side-channel-oracle-kaspersky-2017)

---

## Blum-Goldwasser Bit-Extension Oracle (PlaidCTF 2013)

**Pattern:** Exploit a decryption oracle for Blum-Goldwasser-style encryption by extending ciphertext length by one bit per query to leak plaintext via parity.

**Key insight:** Extend ciphertext by one bit (L+1), shift ciphertext left (`c << 1`), and submit a modified `y` value. The oracle reveals the LSB (parity) of each decrypted chunk. The squaring sequence `y = pow(y, 2, N)` can be manipulated to produce valid extended ciphertexts the server hasn't seen.

```python
# Iterative plaintext recovery via bit-extension
for i in range(msg_length):
    extended_c = original_c << 1        # Shift ciphertext left by 1
    new_y = pow(original_y, 2, N)       # Advance squaring sequence
    response = oracle(extended_c, new_y, msg_length + 1)
    leaked_bit = response & 1           # LSB reveals one plaintext bit
    plaintext_bits.append(leaked_bit)
    original_y = new_y
```

**When to use:** Blum-Goldwasser or BBS-based (Blum Blum Shub) encryption with a decryption oracle that accepts variable-length ciphertexts. The parity leak accumulates one bit per query.

---

## Hash Length Extension Attack (PlaidCTF 2014)

**Pattern:** Server computes `hash(SECRET || user_data)` using MD5, SHA-1, or SHA-256 (Merkle-Damgard constructions). Given a valid hash and the original data, extend it with arbitrary appended data and compute a valid hash — without knowing the secret.

```bash
# Using HashPump (install: apt install hashpump)
hashpump --keylength 8 \
  --signature 'ef16c2bffbcf0b7567217f292f9c2a9a50885e01e002fa34db34c0bb916ed5c3' \
  --data 'original_data' \
  --additional ';admin=true'
# Outputs: new_signature and new_data (with padding bytes)
```

```python
# Python: hashpumpy
import hashpumpy
new_hash, new_data = hashpumpy.hashpump(
    original_hash, original_data, append_data, secret_length
)
```

**Key insight:** Merkle-Damgard hashes (MD5, SHA-1, SHA-256) process data in blocks, and the hash output IS the internal state. Given `H(secret || msg)`, you can compute `H(secret || msg || padding || extension)` without knowing `secret` — just initialize the hash state from the known output and continue hashing. Only HMAC (`H(K XOR opad || H(K XOR ipad || msg))`) is immune. If the secret length is unknown, try lengths 1-32.

---

## Compression Oracle / CRIME-Style Attack (BCTF 2015)

**Pattern:** Server compresses plaintext (LZW, zlib, etc.) before encrypting. By observing ciphertext length changes with chosen plaintexts, leak the unknown plaintext character-by-character.

```python
import base64

def oracle(plaintext):
    """Send chosen plaintext, get ciphertext length."""
    resp = send_to_server(plaintext)
    return len(base64.b64decode(resp))

# Baseline: empty input
base_len = oracle("")

# Recover secret byte-by-byte
known = ""
for pos in range(secret_length):
    for c in string.printable:
        candidate = known + c
        length = oracle(candidate)
        if length <= base_len + len(known):  # Compressed = match
            known += c
            break
```

**Key insight:** Compression algorithms (LZW, DEFLATE, zlib) replace repeated sequences with back-references. If `SALT + user_input` is compressed before encryption, sending input that matches part of the salt produces shorter ciphertext (the match compresses). This is the same class as CRIME (TLS), BREACH (HTTP), and HEIST attacks. The oracle is ciphertext length.

---

## Hash Function Time Reversal via Cycle Detection (BSidesSF 2025)

When a system uses iterated hashing as a "time" function (`state_t = H(state_{t-1})`), reverse time by exploiting the finite cycle structure:

1. **Detect cycle:** Use Floyd's tortoise-and-hare or Brent's algorithm to find cycle length L
2. **Compute backward steps:** To go from time T to earlier time T_goal: iterate forward `(L - (T - T_goal)) % L` steps

```python
import hashlib

def hash_step(state):
    return hashlib.md5(state).digest()[:8]  # Truncated hash

def find_cycle(start):
    """Brent's cycle detection: returns (cycle_length, start_of_cycle)"""
    power = lam = 1
    tortoise = start
    hare = hash_step(start)
    while tortoise != hare:
        if power == lam:
            tortoise = hare
            power *= 2
            lam = 0
        hare = hash_step(hare)
        lam += 1
    # lam = cycle length; find cycle start
    tortoise = hare = start
    for _ in range(lam):
        hare = hash_step(hare)
    mu = 0
    while tortoise != hare:
        tortoise = hash_step(tortoise)
        hare = hash_step(hare)
        mu += 1
    return lam, mu  # cycle_length, cycle_start_offset

# Reverse from T_known to T_goal
cycle_len, _ = find_cycle(known_state)
forward_steps = (cycle_len - (t_known - t_goal)) % cycle_len
state = known_state
for _ in range(forward_steps):
    state = hash_step(state)
# state is now the value at t_goal
```

**Key insight:** For truncated hashes (e.g., MD5 -> 64 bits), the expected cycle length is ~2^32, making cycle detection feasible. Going "backward" N steps is equivalent to going forward (cycle_length - N) steps. Assumes the target state is within the main cycle, not on a tail.

---

## OFB Mode with Invertible RNG Backward Decryption (BSidesSF 2026)

**Pattern (randcrypt):** A custom block cipher uses OFB (Output Feedback) mode with a homemade RNG as the keystream generator. The last plaintext block is known (zero padding), leaking one RNG state. If the RNG's state transition function is invertible (bijective), all previous states can be recovered by running the RNG backwards, decrypting the entire ciphertext from the end to the beginning.

```python
def rng_forward(state):
    """Custom RNG state transition (from challenge)."""
    # Example: linear congruential or reversible mixing
    return (state * A + B) % M

def rng_inverse(state):
    """Inverted RNG — recover previous state."""
    return ((state - B) * pow(A, -1, M)) % M

# Last block is zero-padded → ciphertext XOR 0 = keystream = RNG state
leaked_state = int.from_bytes(ciphertext_blocks[-2], 'big')

# Decrypt backwards
state = leaked_state
plaintext_blocks = []
for i in range(len(ciphertext_blocks) - 3, -1, -1):
    state = rng_inverse(state)
    pt = xor_bytes(ciphertext_blocks[i], state.to_bytes(block_size, 'big'))
    plaintext_blocks.insert(0, pt)
```

**Key insight:** OFB mode decouples encryption from the plaintext — the keystream is deterministic from the initial state. If ANY block's plaintext is known (padding, headers, magic bytes), the corresponding RNG state is leaked. An invertible RNG then reveals ALL states. Always check if the RNG transition function has a mathematical inverse.

**When to recognize:** Custom OFB/CTR mode with a non-standard PRNG. Look for: (1) XOR-based encryption, (2) a state-update function that's bijective (no information loss), (3) predictable plaintext in any block position. Files with known padding (PKCS#7 zero-fill, null-terminated strings) are ideal leak points.

---

## Weak Key Derivation via Public Key Hash XOR (BSidesSF 2026)

**Pattern (ran-somewhere):** Hybrid RSA+AES encryption where the AES key is derived as `SHA256(DER_encoded_public_key) XOR seed`, with the seed hardcoded or predictable. Since the public key is public, the AES key is fully recoverable without the RSA private key.

```python
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES
from hashlib import sha256

# Public key is available
pubkey = RSA.import_key(open("public.pem").read())
der_bytes = pubkey.export_key("DER")

# Seed from challenge (hardcoded/predictable)
seed = b'BSidesSFCTF2026!'

# Derive AES key the same way the encryptor did
key_hash = sha256(der_bytes).digest()
aes_key = bytes(a ^ b for a, b in zip(key_hash, seed.ljust(32, b'\x00')))

# Decrypt
ct = open("flag.enc", "rb").read()
iv, ct_body = ct[:16], ct[16:]
cipher = AES.new(aes_key, AES.MODE_CBC, iv)
plaintext = cipher.decrypt(ct_body)
```

**Key insight:** Key derivation that incorporates only public information (public keys, known constants) provides zero security regardless of the hash function used. The "hybrid" design creates a false sense of security — RSA protects nothing if the AES key doesn't depend on the RSA private key.

**When to recognize:** Challenge provides both a public key AND an encrypted file, but no private key or ciphertext for RSA. Look for key derivation code that hashes the public key, uses the public key's modulus/exponent as seed material, or XORs with a constant.

---

## HMAC-CRC Linearity Attack (Boston Key Party 2016)

**Pattern:** HMAC constructed with CRC as the hash function is completely broken because CRC is linear over GF(2). The key is directly recoverable from a single message-MAC pair via polynomial arithmetic over GF(2^64).

```python
# CRC is linear: CRC(a XOR b) = CRC(a) XOR CRC(b)
# HMAC-CRC(key, msg) = CRC(key_opad || CRC(key_ipad || msg))
# Rewrite as polynomial in GF(2): K = known_terms * inverse(x^(128+M) + x^128) mod CRC_POLY
```

**Key insight:** CRC's linearity over GF(2) means HMAC-CRC provides zero security. Always verify the underlying hash function is non-linear before trusting HMAC.

---

## DES Weak Keys in OFB Mode (Boston Key Party 2016)

**Pattern:** DES has 4 weak keys where `E(E(P,K),K) = P` (encryption is self-inverse). In OFB (Output Feedback) mode this causes the keystream to cycle with period 2: even blocks XOR with IV, odd blocks with E(IV,K). Reduces to a 16-byte repeating XOR key.

```python
# DES weak keys: 0x0000000000000000, 0xFFFFFFFFFFFFFFFF,
#                0xE1E1E1E1F0F0F0F0, 0x1E1E1E1E0F0F0F0F
# OFB with weak key: keystream = [IV, E(IV,K), IV, E(IV,K), ...]
# Recovery: try all 4 weak keys; or treat as 16-byte repeating XOR
```

**Key insight:** DES weak keys cause OFB keystream to cycle with period 2. When you see DES+OFB, always try the 4 weak keys first.

---

## Square Attack on Reduced-Round AES (0CTF 2016)

**Pattern:** 4-round AES is vulnerable to the square (integral) attack. Choose 256 plaintexts differing in one byte (a "lambda set"). After 3 rounds, the XOR sum at any byte position equals 0. Guess one byte of the last round key and partially decrypt -- if XOR sum is 0, the guess is correct.

```python
# For each byte position in the last round key:
for candidate in range(256):
    xor_sum = 0
    for ct in ciphertexts:
        xor_sum ^= inv_sub_bytes(ct[pos] ^ candidate)
    if xor_sum == 0:
        key_byte = candidate  # correct guess
# Reduces 2^128 key recovery to ~16 * 256 = 4096 operations
```

**Key insight:** Integral cryptanalysis exploits the "balanced" property (XOR-sum = 0) that propagates through AES rounds. Effective against 4-round AES; 5+ rounds require more sophisticated variants.

---

## SRP (Secure Remote Password) Protocol Bypass via Modular Arithmetic (ASIS CTF Finals 2016)

SRP implementations that only check `A != 0` and `A != N` can be bypassed by sending `A = 2*N`, causing the server to compute a zero session key.

```python
from hashlib import sha256
import hmac

# SRP protocol: server computes session key from A (client's public value)
# S = (A * v^u) ^ b mod N
# If A = 2*N: S = (2*N * v^u) ^ b mod N = 0 (since 2*N mod N = 0)

N = server_modulus
# Send A = 2*N (bypasses checks for A != 0 and A != N)
A_malicious = 2 * N

# Server computes S = 0, so session key K = SHA256(0)
K = sha256(b'\x00').digest()

# Now compute valid HMAC proof with known K
proof = hmac.new(K, salt, sha256).hexdigest()
```

**Key insight:** SRP implementations must validate `A % N != 0`, not just `A != 0` and `A != N`. Sending `A = k*N` for any integer k forces the shared secret to zero, allowing authentication without knowing the password.

---

## Modified AES S-Box Brute-Force Recovery (H4ckIT CTF 2016)

AES implementation with a custom S-Box created by swapping 3 elements of the standard S-Box. Brute-force all C(256,3) * 2 = 5,527,040 possible permutations.

```cpp
// Three elements swapped from standard AES S-Box
// Total permutations: C(256,3) * 2 = ~5.5 million (feasible to brute-force)
#include <openssl/aes.h>

void bruteforce_sbox(uint8_t ciphertext[], uint8_t key[], int ct_len) {
    uint8_t standard_sbox[256]; // standard AES S-Box
    // Try all 3-element swaps
    for (int i = 0; i < 256; i++)
        for (int j = i+1; j < 256; j++)
            for (int k = j+1; k < 256; k++) {
                // Swap pairs: (i,j), (i,k), (j,k)
                uint8_t sbox[256];
                memcpy(sbox, standard_sbox, 256);
                swap(sbox[i], sbox[j]); // try each 2-element swap from the triple
                // Decrypt and check for valid plaintext
                if (try_decrypt_with_sbox(sbox, ciphertext, key, ct_len))
                    return; // found it
            }
}
```

**Key insight:** When a custom AES S-Box differs from standard by only a few element swaps, the search space is small enough to brute-force. For 3 swapped elements: C(256,3) permutation groups times the swap combinations within each group.

---

## AES-ECB Byte-at-a-Time Chosen Plaintext (ABCTF 2016)

**Pattern (Encryption Service):** Server encrypts `user_input || secret_suffix` under AES-ECB. Recover the secret suffix one byte at a time by controlling the input length.

1. Send inputs of decreasing length to push one unknown byte into a known block position
2. For each position, try all 256 byte values and compare the encrypted block:

```python
from pwn import *
import cryptanalib as ca  # FeatherDuster's cryptanalib

def oracle(pt):
    """Send plaintext, receive ECB-encrypted ciphertext."""
    r = remote('target', 7765)
    r.recvuntil('Send me some hex-encoded data to encrypt:\n')
    r.sendline(pt.hex())
    r.recvuntil('Here you go:')
    ct = bytes.fromhex(r.recvline().strip().decode())
    r.close()
    return ct

# Automated byte-at-a-time recovery
flag = ca.ecb_cpa_decrypt(oracle, block_size=16, verbose=True)
print(flag)
```

**Manual approach without library:**
```python
block_size = 16
known = b''

for i in range(len(secret)):
    # Pad so next unknown byte is at end of a block
    pad_len = block_size - 1 - (len(known) % block_size)
    pad = b'A' * pad_len

    # Get target block
    target_ct = oracle(pad)
    target_block_idx = (pad_len + len(known)) // block_size
    target_block = target_ct[target_block_idx*16:(target_block_idx+1)*16]

    # Try all 256 byte values
    for byte_val in range(256):
        test = pad + known + bytes([byte_val])
        test_ct = oracle(test)
        if test_ct[target_block_idx*16:(target_block_idx+1)*16] == target_block:
            known += bytes([byte_val])
            break
```

**Key insight:** ECB mode encrypts identical plaintext blocks to identical ciphertext blocks. By controlling the prefix length, the attacker shifts one unknown byte at a time to a position where it completes a known block prefix. Comparing the target ciphertext block against all 256 possibilities recovers each byte in at most 256 queries. Total queries: ~256 * secret_length. Tool: FeatherDuster's `cryptanalib.ecb_cpa_decrypt()` automates this completely.

---

## AES-ECB Cut-and-Paste Block Manipulation (NDH Quals 2016)

**Pattern (Toil33t):** Server encrypts JSON session data in AES-ECB mode. Fields like `is_admin: false` span predictable block boundaries. Construct chosen plaintext blocks via registration, then splice ciphertext blocks to change `false` to `true`.

1. Detect ECB mode: register with repeating username (e.g., 'A' * 64), look for identical ciphertext blocks
2. Map block boundaries by varying username length until block count changes
3. Determine field ordering by independently varying username and email lengths
4. Craft target block containing `true` by aligning it at a block boundary via padding:

```python
# Align "true" at start of a block using space padding (JSON ignores whitespace)
# Original:  {"username": "AA", "is_admin": false, "email": ""}
# Target:    {"username": "AA", "is_admin":            true, "email": ""}
#                                              ^-- 16-byte block boundary

# Get the "            true" block from:
username = "AAA" + " " * 12 + "true"
# Extract block 2 of the resulting ciphertext

# Get prefix blocks from a short username
# Get suffix block from a padded username
# Concatenate: prefix_blocks + true_block + suffix_block
```

**Key insight:** AES-ECB encrypts each 16-byte block independently with no chaining. Identical plaintext blocks produce identical ciphertext blocks, allowing block-level cut-and-paste. JSON's tolerance for extra whitespace enables block alignment without breaking parsing. The attack requires: (a) detecting ECB via repeated blocks, (b) mapping field layout via length probing, (c) crafting and splicing blocks.

---

## AES-CBC IV Bit-Flip Authentication Bypass (Google CTF 2016)

**Pattern (Eucalypt Forest):** Server encrypts JSON session blob under AES-CBC and returns both IV and ciphertext as a cookie. No integrity check (no MAC/HMAC). Flip bits in the IV to change the first plaintext block.

1. Register with username one bit away from target (e.g., `` `dmin `` instead of `admin` — flip LSB of 'a')
2. Identify the IV byte position corresponding to the target character in the first block
3. Flip the same bit in the IV byte — XOR propagates directly to the plaintext:

```python
import binascii
cookie = binascii.unhexlify(auth_cookie)
iv = bytearray(cookie[:16])
ciphertext = cookie[16:]

# Flip LSB of byte at position where 'a'/'`' appears in first block
# Position depends on JSON structure: {"username":"`dmin"}
# 'a' (0x61) vs '`' (0x60) differ only in bit 0
target_pos = 13  # position of first char of username in block
iv[target_pos] ^= 0x01

forged = binascii.hexlify(bytes(iv) + ciphertext)
```

**Key insight:** AES-CBC decryption XORs the previous ciphertext block (or IV for block 0) with the AES-decrypted block. Flipping bit `i` in the IV flips bit `i` in the first plaintext block with no other side effects. This only works when the server performs no integrity verification (no HMAC, AEAD, or authenticated encryption).

---

## Rabin Cryptosystem LSB Parity Oracle (PlaidCTF 2016)

**Pattern (rabit):** Server encrypts flag with the Rabin cryptosystem (`c = m^2 mod n`) and provides an LSB oracle — for any ciphertext, it returns the least significant bit of the decrypted plaintext. Binary search recovers the full plaintext in `log2(n)` queries.

```python
from Crypto.Util.number import long_to_bytes

def lsb_oracle_attack(enc_flag, N, oracle_fn):
    """Recover plaintext from Rabin/RSA LSB oracle via binary search."""
    lower = 0
    upper = N
    C = enc_flag
    # Rabin: encrypt(2,N) = 4; multiplying ciphertext by 4 doubles plaintext
    e2 = pow(2, 2, N)  # For Rabin; use pow(2, e, N) for RSA

    for i in range(N.bit_length()):
        C = (e2 * C) % N  # Multiply plaintext by 2
        lsb = oracle_fn(C)
        if lsb == 1:
            # 2*m > N (odd remainder after mod), increase lower bound
            lower = (upper + lower) // 2
        else:
            # 2*m < N (even remainder), decrease upper bound
            upper = (upper + lower) // 2
        # Progressive decryption visible:
        print(long_to_bytes(upper))
    return upper
```

**Key insight:** Rabin (and textbook RSA) are multiplicatively homomorphic: multiplying ciphertext by `2^e mod N` doubles the plaintext mod N. Since N is odd, doubling causes a modular wraparound iff the plaintext exceeds `N/2`, which changes the LSB parity. This creates a binary search: each oracle query halves the candidate range, recovering the full plaintext in exactly `log2(N)` queries (~1024 for RSA-1024).

---

## PBKDF2 Pre-Hash Bypass for Long Passwords (BackdoorCTF 2016)

**Pattern (Mindblown):** PBKDF2 (and HMAC generally) pre-hashes passwords longer than the hash block size (64 bytes for SHA-1/SHA-256). If the target password exceeds 64 bytes, `PBKDF2(password)` equals `PBKDF2(SHA1(password))`, enabling authentication with the hash instead of the original password.

```python
import hashlib

original_password = "complexPasswordWhichContainsManyCharactersWithRandomSuffixeghjrjg"
# len > 64, so HMAC pre-hashes it
equivalent = hashlib.sha1(original_password.encode()).digest()
# Login with equivalent — PBKDF2 produces the same derived key
```

**Key insight:** HMAC's inner construction is `H((K XOR ipad) || message)`. When the key (password) exceeds the hash block size, HMAC first reduces it via `K = H(password)`. This means `HMAC(long_password, ...)` equals `HMAC(H(long_password), ...)`. Any system using PBKDF2/HMAC with a `!==` identity check after hash comparison is vulnerable when passwords exceed 64 bytes. This is a HMAC specification behavior, not an implementation bug.

---

## MD5 Multi-Collision via Fastcol (BackdoorCTF 2016)

**Pattern (Forge):** Generate 2^k files with identical MD5 hashes by chaining `fastcol` (Marc Stevens' tool). Each run produces two suffixes (A, B) that when appended yield the same MD5. Chain 3 runs to produce 8 collisions:

```text
[prefix][suffix1A][suffix2A][suffix3A]  \
[prefix][suffix1A][suffix2A][suffix3B]   |
[prefix][suffix1A][suffix2B][suffix3A]   |-- all have same MD5
[prefix][suffix1A][suffix2B][suffix3B]   |
[prefix][suffix1B][suffix2A][suffix3A]   |
[prefix][suffix1B][suffix2B][suffix3B]  /
```

```bash
# Install: git clone https://github.com/cr-marcstevens/hashclash
# Generate one collision pair (~minutes on modern CPU):
./fastcol -o suffix1A.bin suffix1B.bin < prefix.bin
# Chain: append suffix1A to prefix, run fastcol again for suffix2A/2B, etc.
```

**Key insight:** MD5 collision generation is practical with `fastcol` (~minutes per pair). Because MD5 uses Merkle-Damgard construction, collisions compose: if `H(A||X) == H(A||Y)`, then `H(A||X||Z) == H(A||Y||Z)` for any suffix Z. Chaining k collision pairs produces 2^k files with identical MD5. For CRC32 collisions, append bytes after PNG IEND chunk (parsers ignore trailing data) and brute-force the 4-byte CRC adjustment.

---

## Custom Hash State Reversal via Known Intermediates (BackdoorCTF 2016)

**Pattern (Collision Course):** Custom hash processes 4-byte blocks, updating state with XOR and rotations. If intermediate states are printed, reverse each block's hash by computing `hash(block) = s(i) XOR ROL(s(i+1), 7)`. Then brute-force 4-byte printable inputs matching each hash value.

```python
def reverse_hash_states(states):
    """Given intermediate hash states, recover per-block hash values."""
    blocks = []
    for i in range(len(states) - 1):
        # state_update: s(i+1) = ROR(s(i) ^ hash(block), 7)
        # Therefore:    hash(block) = s(i) ^ ROL(s(i+1), 7)
        h = states[i] ^ rol32(states[i+1], 7)
        blocks.append(h)
    return blocks

def rol32(val, n):
    return ((val << n) | (val >> (32 - n))) & 0xFFFFFFFF

# Brute-force printable 4-byte blocks matching each hash
import itertools, string
for target_hash in block_hashes:
    for chars in itertools.product(string.printable, repeat=4):
        block = bytes(ord(c) for c in chars)
        if custom_hash(block) == target_hash:
            print(f"Found: {block}")
            break
```

**Key insight:** When a custom hash function leaks intermediate states (after each block), each block becomes an independent 4-byte brute-force problem (~2^32 worst case, reduced to ~10^8 for printable ASCII). Inverting the state update equation isolates per-block targets. This pattern appears whenever iterative hashes expose partial state.

---

## CRC32 Brute-Force for Small Payloads (BackdoorCTF 2016)

**Pattern (CRC):** Encrypted ZIP files store CRC32 of uncompressed contents. For very small files (5 bytes), brute-force all printable 5-character strings, compute CRC32, and match against the stored value. Multiple matches are common but context resolves ambiguity.

```python
import binascii, itertools, string, zipfile

# Extract CRC from ZIP without decrypting
with zipfile.ZipFile('encrypted.zip') as z:
    crc = z.infolist()[0].CRC

# Brute-force 5-byte printable content
for chars in itertools.product(string.printable[:95], repeat=5):
    candidate = ''.join(chars).encode()
    if binascii.crc32(candidate) & 0xFFFFFFFF == crc:
        print(f"Match: {candidate}")
```

**Key insight:** CRC32 stored in ZIP headers is not encrypted — it's always accessible even for password-protected ZIPs. For small files (≤ 6 bytes of printable ASCII), the search space is feasible. A C implementation is ~100x faster than Python. Multiple CRC collisions are expected for 5+ byte payloads; combine with language analysis or cross-reference multiple encrypted files to disambiguate.

---

## Noisy RSA LSB Oracle with Post-Hoc Error Correction (SharifCTF 7 2016)

**Pattern:** Extension of the RSA LSB oracle binary search when the oracle occasionally returns incorrect results. Run the standard LSB oracle attack, then inspect decoded bytes. Non-ASCII or unexpected charset values indicate an oracle error within the last ~8 bits. Try single bit-flips at nearby oracle positions; the correct flip fixes the entire remaining decryption.

```python
def lsb_oracle_attack(ciphertext, e, n, oracle_fn, flips=None):
    """Recover plaintext from RSA LSB oracle, with optional error correction."""
    flips = flips or []
    lower, upper = 0, n
    mult = 1
    for i in range(n.bit_length()):
        ciphertext = (ciphertext * pow(2, e, n)) % n
        result = oracle_fn(ciphertext)
        if i in flips:
            result = not result  # correct known oracle error
        mid = (lower + upper) // 2
        if result == 0:
            upper = mid
        else:
            lower = mid
    return lower
```

**Key insight:** Sparse oracle errors produce localized corruption in the recovered plaintext. By inspecting character validity (e.g., expecting hex digits), the error position can be identified and corrected by flipping the oracle result at that query index.

---

## Sponge Hash Collision via Meet-in-the-Middle on Partial State (BKP 2017)

**Pattern:** A custom sponge hash uses AES with a known key, XORing 10-byte message blocks into a 16-byte state. Since only 10 of 16 state bytes are controllable per block, a direct preimage requires ~2^48 work. Meet-in-the-middle reduces this: precompute 2^24 forward AES encryptions keyed on their last 6 bytes, then search backward decryptions for matches in those 6 bytes.

```python
from Crypto.Cipher import AES
import os

aes = AES.new(b'\x00' * 16, AES.MODE_ECB)
forward = {}

# Forward: compute AES(random_10_bytes || 0x00*6), key on last 6 bytes
for _ in range(2**24):
    block = os.urandom(10) + b'\x00' * 6
    enc = aes.encrypt(block)
    forward[enc[-6:]] = block

# Backward: compute AES_dec(target XOR random_c), check last 6 bytes
target_state = b'\x77\x40\x56\x0a\x1d\x64'  # target hash
for _ in range(2**40):
    c_block = os.urandom(10) + target_state
    dec = aes.decrypt(c_block)
    if dec[-6:] in forward:
        a_block = forward[dec[-6:]]
        b_block = xor(aes.encrypt(a_block), dec)  # middle block
        break
```

**Key insight:** When a sponge rate is smaller than the state size, the uncontrolled bytes create a meet-in-the-middle opportunity. Precompute one direction, search the other — reducing 2^48 to 2^24 space + 2^24 time.

---

## CBC IV Forgery + Block Truncation for Authentication Bypass (0CTF 2017)

**Pattern:** Service encrypts `MD5(padded_name) || padded_name` with AES-CBC. The MD5 serves as an integrity check on login. Two attacks combine: (1) IV manipulation: XOR IV bytes to change the decrypted first block from the source MD5 to the target MD5. (2) Block truncation: register with `pad("admin") + 16_junk_bytes`, then strip trailing ciphertext blocks — AES-CBC has no length field, so shorter ciphertext decrypts validly if PKCS7 padding is correct.

```python
# Forge IV to flip MD5 from registered user to "admin"
source_md5 = md5(pad("admin") + b"A"*16)
target_md5 = md5(pad("admin"))
new_iv = bytes(a ^ b ^ c for a, b, c in zip(original_iv, source_md5, target_md5))

# Strip last 2 blocks (junk + PKCS padding block)
forged_token = new_iv + ciphertext[16:-32]
```

**Key insight:** AES-CBC decryption has no built-in length integrity. Truncating ciphertext blocks from the end is valid as long as the new last block decrypts to valid PKCS7 padding. Combined with IV manipulation of block 0, this forges arbitrary first-block content.

---

## Padding Oracle to CBC Bitflip Command Injection (BSidesSF 2017)

**Pattern:** Encrypted commands passed via URL parameter. Error messages reveal padding validity (padding oracle). Chain two attacks: (1) Padding oracle recovers the plaintext of the encrypted command. (2) CBC bitflipping modifies a ciphertext block to inject shell metacharacters (`;$(cmd)`) into the decrypted command, achieving RCE through crypto manipulation alone.

```python
# Step 1: Padding oracle recovers plaintext
plaintext = padding_oracle_decrypt(ciphertext, oracle_fn)

# Step 2: CBC bitflip — modify block N-1 to change decrypted block N
target_block = 5
desired = b';$(cat *.txt)   '  # 16 bytes, pad with spaces
original = plaintext[target_block * 16:(target_block + 1) * 16]
ct = bytearray(bytes.fromhex(ciphertext))
for i in range(16):
    ct[(target_block - 1) * 16 + i] ^= original[i] ^ desired[i]
forged = ct.hex()
```

**Key insight:** Padding oracle and CBC bitflipping are usually taught separately. Chaining them converts a pure cryptographic weakness into full command injection: the oracle recovers plaintext needed to compute the XOR mask, and the bitflip injects the payload.

---

## SPN Cipher Partial Key Recovery via S-box Intersection (SharifCTF 7 2016)

**Pattern:** A 3-round substitution-permutation network with 36-bit blocks and 6-bit S-boxes. Attack using chosen-plaintext pairs: for each pair of 6-bit sub-keys (rounds 2 and 3), partially decrypt through the last two rounds and check if the intermediate S-box input matches. Intersecting candidate key sets across ~200 plaintext-ciphertext pairs uniquely identifies each 6-bit sub-key, reducing a 108-bit brute force to six independent 12-bit searches.

```python
def recover_subkeys(pairs, sbox, perm):
    """Recover 6-bit subkeys via intersection across plaintext-ciphertext pairs."""
    for sbox_pos in range(6):  # 6 S-boxes per round
        candidates = None
        for pt, ct in pairs:
            valid = set()
            for k2 in range(64):  # 6-bit subkey round 2
                for k3 in range(64):  # 6-bit subkey round 3
                    # Partial decrypt through rounds 3 and 2
                    intermediate = inv_sbox[ct_bits[sbox_pos] ^ k3]
                    intermediate = inv_perm(intermediate)
                    if inv_sbox[intermediate ^ k2] == expected_from_pt:
                        valid.add((k2, k3))
            candidates = valid if candidates is None else candidates & valid
        assert len(candidates) == 1  # unique key pair
```

**Key insight:** SPN structures allow divide-and-conquer key recovery. Each S-box position can be attacked independently, and the intersection of valid key candidates across multiple plaintext-ciphertext pairs converges to a unique solution.

---

## AES-CFB IV Recovery from Timestamp-Seeded PRNG (SHA2017)

**Pattern:** Ransomware encrypts files with AES-CFB using a hardcoded password from bash_history. The IV is derived from `random.choice()` seeded with `int(time())` at encryption time. The file's mtime (preserved by the filesystem) equals the exact seed used, enabling full decryption without the private key.

```python
import random, os, string, base64
from Crypto.Cipher import AES

password = b'hardcoded_password_from_bash_history'
img = 'encrypted_file.enc'

# File mtime IS the random seed used at encryption time
random.seed(int(os.stat(img).st_mtime))
iv = ''.join(random.choice(string.letters + string.digits) for _ in range(16))

aes = AES.new(password, AES.MODE_CFB, iv.encode())
with open(img, 'rb') as f:
    ciphertext = base64.b64decode(f.read())
plaintext = aes.decrypt(ciphertext)
```

**Key insight:** PRNG seeded with `time()` at encryption time leaks the seed via the filesystem mtime. Always check Python version compatibility — Python 2 and Python 3 have different `random` module implementations producing different sequences from the same seed. The `-it` flag on `cp`/`mv` may reset mtime; work from the original unmodified file.

**References:** SHA2017

---

## Three-Round XOR Protocol Key Cancellation (HITB 2017)

**Pattern:** A custom protocol performs a three-message XOR key exchange:
1. Client sends `c1 = msg XOR clientKey`
2. Server responds `c2 = c1 XOR serverKey`
3. Client sends `c3 = c2 XOR clientKey`

All three ciphertexts are observable in a PCAP or network capture. Computing `c1 XOR c2 XOR c3` directly recovers the original `msg` because all key material cancels:

```python
# c1 = msg ^ clientKey
# c2 = msg ^ clientKey ^ serverKey
# c3 = msg ^ serverKey
# c1 ^ c2 ^ c3 = msg ^ clientKey ^ msg ^ clientKey ^ serverKey ^ msg ^ serverKey
#              = msg   (all keys cancel via XOR)
plaintext = bytes(a ^ b ^ c for a, b, c in zip(c1, c2, c3))
```

**Key insight:** Three-message XOR key exchange where the client applies its key twice creates an algebraic weakness: XOR of all three ciphertexts directly recovers the original message without knowledge of either key. Any protocol where the same key is applied an even number of times is trivially broken.

**References:** HITB 2017

---

## AES-CBC UnicodeDecodeError Side-Channel Oracle (Kaspersky 2017)

**Pattern:** Server decrypts AES-CBC ciphertext and attempts to UTF-8 decode the result. Invalid UTF-8 sequences raise a `UnicodeDecodeError` (or equivalent). This error is distinguishable from other errors (e.g., application-level errors), creating a decryption oracle analogous to a padding oracle.

**Attack:** Standard CBC bit-flip oracle technique, using UTF-8 validity as the distinguisher:
1. For each target plaintext byte at position `i` in block `b`, modify byte `i` in block `b-1`
2. Cycle through all 256 XOR values; when the decrypted byte produces valid UTF-8 in context, the server returns a non-`UnicodeDecodeError` response
3. From the XOR value that passes and the known modification to `c[b-1][i]`, recover `plaintext[b][i]`

```python
# CBC bit-flip oracle using UTF-8 validity
for guess in range(256):
    modified = bytearray(prev_block)
    modified[pos] = known_intermediate[pos] ^ guess  # produce desired output byte
    if not unicode_error(modified_block + target_block):
        plaintext_byte = guess  # valid UTF-8 at this position
        break
```

**Key insight:** Any error that distinguishes valid from invalid plaintext content serves as a decryption oracle — not just PKCS#7 padding errors. UTF-8 validity, base64 decodability, JSON parsability, and ASCII-only constraints are all valid oracle conditions. The only requirement is a server-side distinguishable response.

**References:** Kaspersky CTF 2017


# modern-ciphers

# CTF Crypto - Modern Cipher Attacks

Block cipher attacks, MAC forgery, padding oracles, and authenticated encryption. For hash/signature attacks (hash extension, PBKDF2, MD5 collision, Rabin, ECB oracles), see [modern-ciphers-2.md](modern-ciphers-2.md). For stream cipher attacks (LFSR, RC4, XOR), see [stream-ciphers.md](stream-ciphers.md).

## Table of Contents
- [AES-CFB-8 Static IV State Forging](#aes-cfb-8-static-iv-state-forging)
- [ECB Pattern Leakage on Images](#ecb-pattern-leakage-on-images)
- [Padding Oracle Attack](#padding-oracle-attack)
- [CBC-MAC vs OFB-MAC Vulnerability](#cbc-mac-vs-ofb-mac-vulnerability)
- [Non-Permutation S-box Collision Attack](#non-permutation-s-box-collision-attack)
- [LCG Partial Output Recovery (0xFun 2026)](#lcg-partial-output-recovery-0xfun-2026)
- [Weak Hash Functions / GF(2) Gaussian Elimination](#weak-hash-functions--gf2-gaussian-elimination)
- [Affine Cipher over Composite Modulus (Nullcon 2026)](#affine-cipher-over-composite-modulus-nullcon-2026)
- [AES-GCM with Derived Keys (EHAX 2026)](#aes-gcm-with-derived-keys-ehax-2026)
- [AES-GCM Nonce Reuse / Forbidden Attack](#aes-gcm-nonce-reuse--forbidden-attack)
- [Ascon-like Reduced-Round Differential Cryptanalysis (srdnlenCTF 2026)](#ascon-like-reduced-round-differential-cryptanalysis-srdnlenctf-2026)
- [Custom Linear MAC Forgery (Nullcon 2026)](#custom-linear-mac-forgery-nullcon-2026)
- [CBC Padding Oracle Attack](#cbc-padding-oracle-attack)
- [Bleichenbacher / PKCS#1 v1.5 RSA Padding Oracle](#bleichenbacher--pkcs1-v15-rsa-padding-oracle)
- [Birthday Attack / Meet-in-the-Middle](#birthday-attack--meet-in-the-middle)
- [CRC32 Collision-Based Signature Forgery (iCTF 2013)](#crc32-collision-based-signature-forgery-ictf-2013)
- [AES Key Recovery via Byte-by-Byte Zeroing Oracle (CONFidence CTF 2017)](#aes-key-recovery-via-byte-by-byte-zeroing-oracle-confidence-ctf-2017)
- [AES-CTR Constant Counter / Repeating Keystream (SHA2017)](#aes-ctr-constant-counter--repeating-keystream-sha2017)
- [Custom SPN Column-Wise XOR Brute-Force (Hack Dat Kiwi 2017)](#custom-spn-column-wise-xor-brute-force-hack-dat-kiwi-2017)

See also [modern-ciphers-2.md](modern-ciphers-2.md) for CRC32 forgery, Blum-Goldwasser, hash length extension, compression oracle, hash time reversal, OFB invertible RNG, weak key derivation, HMAC-CRC, DES weak keys, SRP bypass, modified AES S-Box, square attack, AES-ECB byte-at-a-time, AES-ECB cut-and-paste, AES-CBC IV bit-flip, Rabin LSB parity oracle, PBKDF2 pre-hash bypass, MD5 multi-collision, custom hash state reversal, and CRC32 brute-force.

---

## AES-CFB-8 Static IV State Forging

**Pattern (Cleverly Forging Breaks):** AES-CFB with 8-bit feedback and reused IV allows state reconstruction.

**Key insight:** After encrypting 16 known bytes, the AES internal shift register state is fully determined by those ciphertext bytes. Forge new ciphertexts by continuing encryption from known state.

---

## ECB Pattern Leakage on Images

**Pattern (Electronic Christmas Book):** AES-ECB on BMP/image data preserves visual patterns.

**Exploitation:** Identical plaintext blocks produce identical ciphertext blocks, revealing image structure even when encrypted. Rearrange or identify patterns visually.

---

## Padding Oracle Attack

**Pattern (The Seer):** Server reveals whether decrypted padding is valid.

**Byte-by-byte decryption:**
```python
def decrypt_byte(block, prev_block, position, oracle, known):
    """known = bytearray(16) tracking recovered intermediate bytes for this block."""
    for guess in range(256):
        modified = bytearray(prev_block)
        # Set known bytes to produce valid padding
        pad_value = 16 - position
        for j in range(position + 1, 16):
            modified[j] = known[j] ^ pad_value
        modified[position] = guess
        if oracle(bytes(modified) + block):
            return guess ^ pad_value
```

---

## CBC-MAC vs OFB-MAC Vulnerability

OFB mode creates a keystream that can be XORed for signature forgery.

**Attack:** If you have signature for known plaintext P1, forge for P2:
```text
new_sig = known_sig XOR block2_of_P1 XOR block2_of_P2
```

**Important:** Don't forget PKCS#7 padding in calculations! Small bruteforce space? Just try all combinations (e.g., 100 for 2 unknown digits).

**Key insight:** OFB-MAC generates a keystream independent of the plaintext, so knowing one (message, MAC) pair lets you forge MACs for arbitrary messages by XORing the known plaintext blocks out and XORing the new ones in. CBC-MAC does not have this weakness because each block's encryption depends on the previous ciphertext block.

---

## Non-Permutation S-box Collision Attack

**Pattern (Tetraes, Nullcon 2026):** Custom AES-like cipher with S-box collisions.

**Detection:** `len(set(sbox)) < 256` means collisions exist. Find collision pairs and their XOR delta.

**Attack:** For each key byte, try 256 plaintexts differing by delta. When `ct1 == ct2`, S-box input was in collision set. 2-way ambiguity per byte, 2^16 brute-force. Total: 4,097 oracle queries.

See [advanced-math.md](advanced-math.md) for full S-box collision analysis code.

---

## LCG Partial Output Recovery (0xFun 2026)

**Known parameters:** If LCG (Linear Congruential Generator) constants (M, A, C) are known and output is `state mod N`, iterate by N through modulus to find state:
```python
# output = state % N, state = (A * prev + C) % M
for candidate in range(output, M, N):
    # Check if candidate is consistent with next output
    next_state = (A * candidate + C) % M
    if next_state % N == next_output:
        print(f"State: {candidate}")
```

**Upper bits only (e.g., upper 32 of 64):** Brute-force lower 32 bits:
```python
for low in range(2**32):
    state = (observed_upper << 32) | low
    next_state = (A * state + C) % M
    if (next_state >> 32) == next_observed_upper:
        print(f"Full state: {state}")
```

**Key insight:** LCG output truncation (modulo or upper bits only) hides part of the state, but consecutive outputs constrain it. When output is `state mod N`, iterate candidates by N through the modulus. When only upper bits are visible, brute-force the hidden lower bits and validate against the next output.

---

## Weak Hash Functions / GF(2) Gaussian Elimination

Linear permutations (only XOR, rotations) are algebraically attackable. Build transformation matrix and solve over GF(2).

```python
import numpy as np

def solve_gf2(A, b):
    """Solve Ax = b over GF(2)."""
    m, n = A.shape
    Aug = np.hstack([A, b.reshape(-1, 1)]) % 2
    pivot_cols, row = [], 0
    for col in range(n):
        pivot = next((r for r in range(row, m) if Aug[r, col]), None)
        if pivot is None: continue
        Aug[[row, pivot]] = Aug[[pivot, row]]
        for r in range(m):
            if r != row and Aug[r, col]: Aug[r] = (Aug[r] + Aug[row]) % 2
        pivot_cols.append((row, col)); row += 1
    if any(Aug[r, -1] for r in range(row, m)): return None
    x = np.zeros(n, dtype=np.uint8)
    for r, c in reversed(pivot_cols):
        x[c] = Aug[r, -1] ^ sum(Aug[r, c2] * x[c2] for c2 in range(c+1, n)) % 2
    return x
```

**Key insight:** Hash functions built from only XOR and rotations (no S-boxes or modular addition) are linear over GF(2). Build the transformation as a binary matrix, then invert it with Gaussian elimination to recover the preimage directly. This breaks any "custom hash" that avoids non-linear operations.

---

## Affine Cipher over Composite Modulus (Nullcon 2026)

Affine encryption `c = A*x + b (mod M)` with composite M: split into prime factor fields, invert independently, CRT recombine. See [advanced-math.md](advanced-math.md#affine-cipher-over-non-prime-modulus-nullcon-2026) for full chosen-plaintext key recovery and implementation.

---

## AES-GCM with Derived Keys (EHAX 2026)

**Pattern:** Final decryption step after recovering a secret (e.g., from LWE, key exchange). Session nonce and AES key derived via SHA-256 hashing of the recovered secret.

```python
import hashlib
from Cryptodome.Cipher import AES

# Common key derivation chain:
# 1. Recover secret bytes (s_bytes) from crypto challenge
# 2. Unwrap session nonce: nonce = wrapped_nonce XOR SHA256(s_bytes)[:nonce_len]
# 3. Derive AES key: key = SHA256(s_bytes + session_nonce)
# 4. Decrypt AES-GCM

def decrypt_with_derived_key(s_bytes, wrapped_nonce, ciphertext, aes_nonce, tag, nonce_len=16):
    secret_hash = hashlib.sha256(s_bytes).digest()
    session_nonce = bytes(a ^ b for a, b in zip(wrapped_nonce, secret_hash[:nonce_len]))
    aes_key = hashlib.sha256(s_bytes + session_nonce).digest()
    cipher = AES.new(aes_key, AES.MODE_GCM, nonce=aes_nonce)
    return cipher.decrypt_and_verify(ciphertext, tag)
```

**Key insight:** When AES-GCM authentication fails (`ValueError: MAC check failed`), the derived key is wrong — usually means the upstream secret recovery was incorrect or endianness is swapped.

---

## AES-GCM Nonce Reuse / Forbidden Attack

AES-GCM (Galois/Counter Mode) combines AES-CTR encryption with a GHASH polynomial authentication tag. Reusing a nonce with the same key is catastrophic -- it enables both plaintext recovery AND authentication key recovery.

**CTR keystream reuse:** Same nonce = same keystream. XOR two ciphertexts to cancel the keystream: `C1 XOR C2 = P1 XOR P2`. With known plaintext in one message, recover the other.

**GHASH authentication key recovery:** The authentication tag is a polynomial evaluation over GF(2^128). Two messages with the same nonce produce two equations in the same authentication key H. XOR the tag polynomials and factor over GF(2^128) to recover H. With H, forge valid tags for arbitrary messages.

```python
from Crypto.Cipher import AES
from sage.all import GF, PolynomialRing

# Given: two (ciphertext, tag, nonce) pairs with same nonce
# Step 1: Recover plaintext via CTR keystream reuse
keystream = xor(known_plaintext, ciphertext1)
plaintext2 = xor(keystream, ciphertext2)

# Step 2: Recover GHASH auth key H
# Construct tag difference polynomial in GF(2^128)
F = GF(2**128, 'x', modulus=...)  # GCM polynomial
# T1 XOR T2 = P(H) where P is polynomial from ciphertext difference
# Factor P(H) = 0 to find H candidates
# Verify H against known tags

# Step 3: Forge tags for arbitrary messages
# GHASH(H, aad, ciphertext) computed with recovered H
```

**Tool:** [nonce-disrespect](https://github.com/nonce-disrespect/nonce-disrespect) automates GHASH key recovery and tag forgery from nonce-reused GCM ciphertexts.

**Short nonce brute-force:** When GCM uses a short nonce (1-4 bytes), brute-force all nonce values if the key is known. AES-GCM with 1-byte nonce = only 256 candidates.

**Key insight:** AES-GCM is a "one-time nonce" scheme -- a single nonce reuse breaks both confidentiality (CTR keystream reuse) AND authenticity (GHASH key recovery). Always check for repeated nonces in GCM challenge traffic.

---

## Ascon-like Reduced-Round Differential Cryptanalysis (srdnlenCTF 2026)

**Pattern (Lightweight):** 4-round Ascon-like permutation with reduced diffusion. Key-dependent biases in output-bit differentials allow key recovery via chosen input differences.

**Attack:**
1. Reproduce the permutation exactly (critical: post-S-box x4 assignment order matters)
2. Invert the linear layer of x0 using a precomputed 64×64 GF(2) inverse matrix
3. For each bit position i, query with `diff = (1<<i, 1<<i)` across multiple samples
4. Measure empirical biases at output bits `j1 = (i+1) mod 64` and `j2 = (i+14) mod 64`
5. Classify key bits `(k0[i], k1[i])` via centroid-based clustering with sign-pattern mask
6. Verify candidate key in-session; refine low-margin bits with additional samples

**GF(2) linear layer inversion:**
```python
def build_inverse(shifts=(19, 28)):
    """Construct GF(2) inverse matrix for Ascon-like linear layer: x ^= rot(x,19) ^ rot(x,28)."""
    # Build 64x64 matrix over GF(2)
    M = [[0]*64 for _ in range(64)]
    for out_bit in range(64):
        M[out_bit][out_bit] = 1
        for shift in shifts:
            M[out_bit][(out_bit + shift) % 64] ^= 1
    # Gaussian elimination to find inverse
    aug = [row + [1 if i == j else 0 for j in range(64)] for i, row in enumerate(M)]
    for col in range(64):
        pivot = next(r for r in range(col, 64) if aug[r][col])
        aug[col], aug[pivot] = aug[pivot], aug[col]
        for r in range(64):
            if r != col and aug[r][col]:
                aug[r] = [a ^ b for a, b in zip(aug[r], aug[col])]
    return [row[64:] for row in aug]
```

**Centroid clustering for key classification:**
```python
# For each bit position, measure bias at two output positions
# 4 possible (k0[i], k1[i]) pairs → 4 centroid patterns
# Uses sign-pattern mask CMASK=0x73 to account for bit-position-dependent behavior
# Classify by minimum Euclidean distance in 2D bias space
CMASK = 0x73
for i in range(64):
    bias_j1, bias_j2 = measure_biases(i, samples)
    mask_bit = (CMASK >> (i % 8)) & 1
    centroids = centroid_table[mask_bit]  # Precomputed per-position centroids
    k0_bit, k1_bit = min(range(4), key=lambda c: euclidean_dist(
        (bias_j1, bias_j2), centroids[c]))
```

**Key insight:** Reduced-round lightweight ciphers (Ascon, GIFT, etc.) have exploitable biases when the number of rounds is insufficient for full diffusion. The linear layer's inverse can be computed algebraically, and differential biases measured across chosen-plaintext queries reveal individual key bits. This is practical even with noisy measurements if you collect enough samples.

---

## Custom Linear MAC Forgery (Nullcon 2026)

**Pattern (Pasty):** Server signs paste IDs with a custom SHA-256-based construction. The signature is linear in three 8-byte secret blocks derived from the key.

**Structure:** For each 8-byte output block `i`:
- `selector = SHA256(id)[i*8] % 3` → chooses which secret block to use
- `out[i] = hash_block[i] XOR secret[selector] XOR chain[i-1]`

**Recovery:** Create ~10 pastes to collect `(id, sig)` pairs. Each pair reveals `secret[selector]` for 4 selectors. With ~4-5 pairs, all 3 secret blocks are recovered. Then forge for target ID.

**Key insight:** Linearity in custom crypto constructions (XOR-based signing) makes them trivially forgeable. Always check if the MAC has the property: knowing the secret components lets you compute valid signatures for arbitrary inputs.

---

## CBC Padding Oracle Attack

**Pattern:** Server reveals whether CBC-mode ciphertext has valid PKCS#7 padding (via error messages, timing, or status codes). Decrypt any ciphertext block-by-block without the key.

```python
from pwn import *

def padding_oracle(iv, ct):
    """Returns True if server accepts padding."""
    resp = requests.post(URL, data={'iv': iv.hex(), 'ct': ct.hex()})
    return 'padding' not in resp.text.lower()  # or check status code

def decrypt_block(prev_block, target_block):
    """Decrypt one 16-byte block using padding oracle."""
    intermediate = bytearray(16)
    plaintext = bytearray(16)

    for byte_pos in range(15, -1, -1):
        pad_val = 16 - byte_pos
        # Set already-known bytes to produce correct padding
        crafted = bytearray(16)
        for k in range(byte_pos + 1, 16):
            crafted[k] = intermediate[k] ^ pad_val

        for guess in range(256):
            crafted[byte_pos] = guess
            if padding_oracle(bytes(crafted), target_block):
                intermediate[byte_pos] = guess ^ pad_val
                plaintext[byte_pos] = intermediate[byte_pos] ^ prev_block[byte_pos]
                break

    return bytes(plaintext)
```

**Tools:**
```bash
# PadBuster — automated padding oracle exploitation
padbuster http://target/decrypt.php ENCRYPTED_B64 16 \
  -encoding 0 -error "Invalid padding"

# Python: pip install padding-oracle
from padding_oracle import PaddingOracle
oracle = PaddingOracle(block_size=16, oracle_fn=check_padding)
plaintext = oracle.decrypt(ciphertext, iv=iv)
```

**Key insight:** The oracle only needs to distinguish "valid padding" from "invalid padding." This can be a different HTTP status code, error message, response time, or even whether the application processes the request further. A single bit of information per query is sufficient. Decryption requires at most 256 x 16 = 4096 queries per block.

**Detection:** CBC mode encryption + any distinguishable behavior difference on padding errors. Common in cookie encryption, token systems, and encrypted API parameters.

---

## Bleichenbacher / PKCS#1 v1.5 RSA Padding Oracle

**Pattern:** RSA encryption with PKCS#1 v1.5 padding where the server reveals whether decrypted plaintext has valid `0x00 0x02` prefix. Adaptive chosen-ciphertext attack recovers the plaintext.

```python
import gmpy2

def bleichenbacher_oracle(c, n, e):
    """Returns True if RSA decryption has valid PKCS#1 v1.5 padding (0x00 0x02 prefix)."""
    resp = send_to_server(c)
    return resp.status_code != 400  # Server returns 400 on bad padding

def bleichenbacher_attack(c0, n, e, oracle, k):
    """
    c0: target ciphertext (integer)
    k: byte length of modulus (e.g., 256 for RSA-2048)
    """
    B = pow(2, 8 * (k - 2))

    # Step 1: Start with s1 = ceil(n / 3B)
    s = (n + 3 * B - 1) // (3 * B)

    # Step 2: Search for s where oracle(c0 * s^e mod n) is True
    while True:
        c_prime = (c0 * pow(s, e, n)) % n
        if oracle(c_prime, n, e):
            break
        s += 1

    # Step 3: Narrow interval [a, b] using s values
    # Repeat: find new s, narrow interval, until a == b
    # When interval collapses, plaintext = a * modinv(s, n) % n
    # (Full implementation requires interval tracking — use existing tools)
```

**Tools:**
```bash
# ROBOT attack scanner (modern Bleichenbacher variant)
python3 robot-detect.py -H target.com

# TLS-Attacker framework
java -jar TLS-Attacker.jar -connect target:443 -workflow_type BLEICHENBACHER
```

**Key insight:** The attack is adaptive — each oracle response narrows the range of possible plaintexts. Typically requires ~10,000 oracle queries for RSA-2048. The ROBOT attack (Return Of Bleichenbacher's Oracle Threat) showed this affects modern TLS implementations through subtle timing differences. Any server that distinguishes "bad padding" from "bad content" is vulnerable.

---

## Birthday Attack / Meet-in-the-Middle

**Pattern:** Find collisions in hash functions or MACs using the birthday paradox. With an n-bit hash, expect a collision after ~2^(n/2) random inputs.

```python
import hashlib, os

def birthday_collision(hash_fn, output_bits, prefix=b''):
    """Find two inputs with the same truncated hash."""
    target_bytes = output_bits // 8
    seen = {}

    while True:
        msg = prefix + os.urandom(16)
        h = hash_fn(msg).digest()[:target_bytes]
        if h in seen:
            return seen[h], msg  # Collision found!
        seen[h] = msg

# Example: find collision on first 4 bytes of SHA-256 (~65536 attempts)
msg1, msg2 = birthday_collision(hashlib.sha256, 32)
```

**Meet-in-the-Middle (2DES, double encryption):**
```python
def meet_in_the_middle(encrypt_fn, decrypt_fn, plaintext, ciphertext, keyspace):
    """Break double encryption E(k2, E(k1, pt)) = ct."""
    # Forward: encrypt plaintext with all possible k1
    forward = {}
    for k1 in keyspace:
        intermediate = encrypt_fn(k1, plaintext)
        forward[intermediate] = k1

    # Backward: decrypt ciphertext with all possible k2
    for k2 in keyspace:
        intermediate = decrypt_fn(k2, ciphertext)
        if intermediate in forward:
            return forward[intermediate], k2  # Found k1, k2!
```

**Key insight:** Birthday attack: n-bit hash needs ~2^(n/2) queries for 50% collision probability. 32-bit hash -> ~65K, 64-bit -> ~4 billion. Meet-in-the-middle reduces double encryption from O(2^(2k)) to O(2^k) time + O(2^k) space — this is why 2DES provides only 1 extra bit of security over DES.

---

## CRC32 Collision-Based Signature Forgery (iCTF 2013)

**Pattern:** CRC32 is linear — appending 4 carefully chosen bytes to any message produces a target CRC32 value, enabling signature forgery without knowing the secret key.

**Key insight:** `CRC32(msg || secret)` is not a secure MAC. Given any signed response `(msg, sig)`, compute 4 suffix bytes that force `CRC32(forged_msg || suffix || secret) == target_sig`. The linearity of CRC32 means the suffix computation is deterministic and instant.

```python
import struct, binascii

def crc32_forge(data, target_crc):
    """Append 4 bytes to data so CRC32(data + suffix) == target_crc"""
    current = binascii.crc32(data) & 0xFFFFFFFF
    # CRC32 polynomial table lookup to find suffix bytes
    # that transform current CRC into target_crc
    suffix = b''
    crc = target_crc ^ 0xFFFFFFFF
    for _ in range(4):
        byte = (crc & 0xFF)
        crc = (crc >> 8)
        suffix = bytes([byte]) + suffix
    return data + suffix  # Simplified — full implementation requires polynomial division
```

**When to use:** Any protocol using CRC32 as a message authentication code (MAC). CRC32 is a checksum, not a cryptographic hash — it provides no integrity guarantees against adversarial modification.

---

## AES Key Recovery via Byte-by-Byte Zeroing Oracle (CONFidence CTF 2017)

**Pattern:** When a service allows selective zeroing of key bytes (e.g., via integer overflow in key slot indexing), recover the full AES key by testing one byte at a time.

```python
# Service has key slots and a "regenerate" function with integer overflow
# offset = index * ENTRY_SIZE wraps around, allowing arbitrary byte zeroing

# Strategy: zero bytes progressively, brute-force each unknown byte
for byte_pos in range(16):
    # Zero all bytes EXCEPT byte_pos (by overflowing index calculation)
    zero_index = (target_offset * modinv(ENTRY_SIZE, 2**32)) % 2**32
    regenerate(zero_index)

    # Key is now: [0,0,...,key[byte_pos],...,0,0]
    # Brute-force the single non-zero byte (256 possibilities)
    known_ct = encrypt(known_pt)
    for guess in range(256):
        test_key = bytes([0]*byte_pos + [guess] + [0]*(15-byte_pos))
        if AES.new(test_key, AES.MODE_ECB).encrypt(known_pt) == known_ct:
            recovered_key[byte_pos] = guess
            break
```

**Key insight:** Integer overflow in `index * ENTRY_SIZE` calculations can target arbitrary memory offsets. By selectively zeroing all-but-one key bytes, the key becomes trivially brute-forceable one byte at a time (256 attempts per byte, 4096 total vs 2^128 for the full key).

**References:** CONFidence CTF 2017

---

## AES-CTR Constant Counter / Repeating Keystream (SHA2017)

**Pattern:** When an AES-CTR implementation uses `counter=lambda: secret` (a constant function), the counter never increments. AES-CTR with a fixed counter produces the same 16-byte block on every call — equivalent to Vigenère cipher at the byte level with a 16-byte repeating key.

```python
# Constant counter makes CTR equivalent to repeating-key XOR
key_byte = ciphertext_byte ^ known_plaintext_byte
# Apply recovered key bytes across all 16-byte-aligned blocks
for i, ct_byte in enumerate(ciphertext):
    plaintext_byte = ct_byte ^ keystream[i % 16]
```

**Exploit using file format headers:**
1. Identify the file format from context (e.g., `%PDF-1.` for PDF files)
2. XOR the known header bytes against the ciphertext to recover `keystream[0:len(header)]`
3. Iteratively extend: use recovered plaintext to guess the next structural keyword (`endobj`, `/Page`, `stream`, etc.), verify XOR produces consistent ASCII, and extend the keystream further
4. Tool: `otp_pwn` supports interactive block-aligned crib-dragging for this workflow

**Key insight:** Constant AES-CTR counter = repeating 16-byte Vigenère key. Known file format magic bytes bootstrap iterative key recovery via crib-dragging. Any known-plaintext at block-aligned positions reveals the full keystream byte at that position.

**References:** SHA2017

---

## Custom SPN Column-Wise XOR Brute-Force (Hack Dat Kiwi 2017)

**Pattern:** SPN (Substitution-Permutation Network) cipher with a seed-based sbox/pbox and a final XOR key layer. If the XOR key is applied column-wise (each key byte affects one column position independently), each key byte can be brute-forced separately using printable-text consistency as an oracle.

**Attack:**
1. Collect multiple ciphertext blocks (same key, different plaintexts)
2. For each column position `c` (0-15), try all 256 candidate key bytes `k`
3. Apply the inverse pbox and sbox to undo the SPN rounds, then XOR with candidate `k`
4. Keep only candidates where ALL blocks produce printable ASCII at position `c`
5. The intersection of valid candidates across blocks recovers each key byte

**Multi-round variant:** Peel one round at a time. After recovering the outermost XOR key, apply the inverse pbox/sbox for that round using the recovered bytes, then repeat for the next inner round.

**Seed-based permutation dependency:** When sbox and pbox are generated from a shared seed, recovering partial key bytes constrains the seed (and thus the remaining permutation entries). Use this to propagate partial solutions across columns with cross-column dependencies.

**Key insight:** Column-aligned XOR layers in SPN ciphers allow independent per-byte brute-force using printable-text consistency as an oracle. Cross-column key reuse from seed-based permutations propagates partial solutions.

**References:** Hack Dat Kiwi 2017


# prng

# CTF Crypto - PRNG & Key Recovery

## Table of Contents
- [Mersenne Twister (MT19937) State Recovery](#mersenne-twister-mt19937-state-recovery)
- [MT State Recovery from random.random() Floats via GF(2) Matrix (PHD CTF Quals 2012)](#mt-state-recovery-from-randomrandom-floats-via-gf2-matrix-phd-ctf-quals-2012)
- [Time-Based Seed Attacks](#time-based-seed-attacks)
- [C srand/rand Synchronization via Python ctypes](#c-srandrand-synchronization-via-python-ctypes)
- [Layered Encryption Recovery](#layered-encryption-recovery)
- [LCG Parameter Recovery Attack](#lcg-parameter-recovery-attack)
- [ChaCha20 Key Recovery](#chacha20-key-recovery)
- [GF(2) Matrix PRNG Seed Recovery (0xFun 2026)](#gf2-matrix-prng-seed-recovery-0xfun-2026)
- [Middle-Square PRNG Brute Force (UTCTF 2024)](#middle-square-prng-brute-force-utctf-2024)
- [Deterministic RNG from Flag Bytes + Hill Climbing (VuwCTF 2025)](#deterministic-rng-from-flag-bytes--hill-climbing-vuwctf-2025)
- [Byte-by-Byte Oracle with Random Mode Matching (VuwCTF 2025)](#byte-by-byte-oracle-with-random-mode-matching-vuwctf-2025)
- [RSA Key Reuse / Replay (UTCTF 2024)](#rsa-key-reuse--replay-utctf-2024)
- [Password Cracking Strategy](#password-cracking-strategy)
- [Logistic Map / Chaotic PRNG Seed Recovery (BYPASS CTF 2025)](#logistic-map--chaotic-prng-seed-recovery-bypass-ctf-2025)
- [V8 XorShift128+ State Recovery (Math.random Prediction)](#v8-xorshift128-state-recovery-mathrandom-prediction)
- [Mersenne Twister Seed Recovery from Subset Sum (Tokyo Westerns 2017)](#mersenne-twister-seed-recovery-from-subset-sum-tokyo-westerns-2017)
- [MT19937 State Recovery via Constraint Propagation (HITCON 2017)](#mt19937-state-recovery-via-constraint-propagation-hitcon-2017)

---

## Mersenne Twister (MT19937) State Recovery

Python's `random` module uses Mersenne Twister. If you can observe outputs, you can recover the state and predict future values.

**Key properties:**
- 624 × 32-bit internal state
- Each output is tempered from state
- After 624 outputs, state is twisted (regenerated)

**Basic untemper (reverse single output):**
```python
def untemper(y):
    y ^= y >> 18
    y ^= (y << 15) & 0xefc60000
    for _ in range(7):
        y ^= (y << 7) & 0x9d2c5680
    y ^= y >> 11
    y ^= y >> 22
    return y

# Given 624 consecutive outputs, recover state
state = [untemper(output) for output in outputs]
```

**Python's randrange(maxsize) on 64-bit:**
- `maxsize = 2^63 - 1`, so `getrandbits(63)` is used
- Each 63-bit output uses 2 MT outputs: `(mt1 << 31) | (mt2 >> 1)`
- One bit lost per output → need symbolic solving

**Symbolic approach with z3:**
```python
from z3 import *

def symbolic_temper(y):
    y = y ^ (LShR(y, 11))
    y = y ^ ((y << 7) & 0x9d2c5680)
    y = y ^ ((y << 15) & 0xefc60000)
    y = y ^ (LShR(y, 18))
    return y

# Create symbolic MT state
mt = [BitVec(f'mt_{i}', 32) for i in range(624)]
solver = Solver()

# For each observed 63-bit output
for i, out63 in enumerate(outputs):
    if 2*i + 1 >= 624: break
    y1 = symbolic_temper(mt[2*i])
    y2 = symbolic_temper(mt[2*i + 1])
    combined = Concat(Extract(31, 0, y1), Extract(31, 1, y2))
    solver.add(combined == out63)

if solver.check() == sat:
    state = [solver.model()[mt[i]].as_long() for i in range(624)]
```

**Applications:**
- MIME boundary prediction (email libraries)
- Session token prediction
- CAPTCHA bypass (predictable codes)
- Game RNG exploitation

## MT State Recovery from random.random() Floats via GF(2) Matrix (PHD CTF Quals 2012)

**Pattern:** Server exposes `random.random()` float outputs (e.g., via an API endpoint). Standard MT untemper requires 624 × 32-bit integer outputs, but `random.random()` produces 53-bit floats — truncating each to 8 usable bits per observation. A precomputed GF(2) magic matrix maps observed byte values back to the 624-word MT state.

**Key insight:** `random.random()` returns `(a*2^27+b)/2^53` where `a` = 27 bits from one MT output and `b` = 26 bits from the next. Truncating `int(float * 256)` yields only 8 bits per float, so 3360+ observations are needed (vs. 624 for integer outputs). The `not_random` library precomputes the GF(2) relationship between observed bits and state bits.

```python
import random, gzip, hashlib

# Load precomputed GF(2) magic matrix (from github.com/fx5/not_random)
f = gzip.GzipFile("magic_data", "r")
magic = eval(f.read())
f.close()

def rebuild_from_floats(floats):
    """Convert float observations to byte values, then recover MT state."""
    vals = [int(f * 256) for f in floats]  # truncate to 8-bit
    return rebuild_random(vals)

def rebuild_random(vals):
    """Recover MT19937 state from 3360+ byte observations using GF(2) matrix."""
    def getbit(bit):
        assert bit >= 0
        return (vals[bit // 8] >> (7 - bit % 8)) & 1
    state = []
    for i in range(624):
        val = 0
        data = magic[i % 2]
        for bit in data:
            val <<= 1
            for b in bit:
                val ^= getbit(b + (i // 2) * 8 - 8)
        state.append(val)
    state.append(0)
    ran = random.Random()
    ran.setstate((3, tuple(state), None))
    # Advance past consumed outputs
    for i in range(len(vals) - 3201 + 394):
        ran.randint(0, 255)
    return ran

# Collect 3360+ random.random() floats from the target
floats = [...]  # observed values from server API

# Recover state and predict future outputs
my_random = rebuild_from_floats(floats[:3360])

# Verify predictions match remaining observations
for observed, predicted in zip(floats[3360:], [my_random.random() for _ in range(40)]):
    assert '%.16f' % observed == '%.16f' % predicted

# Forge password reset token (same hash the server computes)
token = hashlib.md5(('%.16f' % my_random.random()).encode()).hexdigest()
reset_url = f'http://target/reset/{user_id}-{token}/'
```

**Attack flow (password reset token prediction):**
1. Request 3360+ random float values from an API endpoint that exposes them (e.g., `/?count=3360`)
2. Simultaneously trigger a password reset (the reset token is `md5(random.random())`)
3. Recover the MT state from the observed floats
4. Predict the `random.random()` call used for the reset token
5. Construct the reset URL with the predicted token

**When to use:** Server uses Python's `random.random()` for security-sensitive tokens (session IDs, password resets, CSRF tokens) and also exposes random values through another endpoint. The `not_random` library handles the bit-level math — focus on collecting enough float observations and synchronizing timing with the target operation.

---

## Time-Based Seed Attacks

When encryption uses time-based PRNG seed:
```python
seed = f"{username}_{timestamp}_{random_bits}"
```

**Attack approach:**
1. **Username:** Extract from metadata, email headers, challenge context
2. **Timestamp:** Get from file metadata (ZIP, exiftool)
3. **Random bits:** Check for hardcoded seed in binary, or bruteforce if small range

**Timestamp extraction:**
```bash
# Set timezone to match target
TZ=Pacific/Galapagos exiftool file.enc
# Look for File Modification Date/Time
```

**Bruteforce milliseconds:**
```python
from datetime import datetime
import random

for ms in range(1000):
    ts = f"2021-02-09!07:23:54.{ms:03d}"
    seed = f"{username}_{ts}_{rdata}"
    rng = random.Random()
    rng.seed(seed)
    key = bytes(rng.getrandbits(8) for _ in range(32))
    if try_decrypt(ciphertext, key):
        print(f"Found seed: {seed}")
        break
```

## C srand/rand Synchronization via Python ctypes

**Pattern:** Binary seeds C's PRNG with `srand(time(NULL))` at startup and uses `rand()` for encryption keys, random challenges, or XOR masks. Python's `random` module uses Mersenne Twister (different algorithm), so calling `random.seed(t)` produces wrong outputs. Use `ctypes` to load the same libc and call C's `srand()`/`rand()` directly.

**Basic synchronization (L3akCTF 2024, MireaCTF):**
```python
from ctypes import CDLL
from time import time

# Load the SAME libc used by the target binary
libc = CDLL('./libc.so.6')  # or CDLL('libc.so.6') for system libc

# Seed at the same second as the binary starts
libc.srand(int(time()))

# Generate the same sequence as the binary's rand() calls
for i in range(16):
    value = libc.rand() & 0xff  # match binary's truncation (e.g., & 0xff for byte)
    print(value)
```

**Decrypting XOR-encrypted data (L3akCTF 2024 chonccfile):**
```python
from ctypes import CDLL
from time import time
from pwn import u32, p32

libc_imp = CDLL('./libc.so.6')
libc_imp.srand(int(time()))

# Binary XORs each 4-byte block with rand() output
encrypted_data = b'...'  # read from heap/memory
result = b''
for i in range(0, len(encrypted_data), 4):
    block = u32(encrypted_data[i:i+4])
    libc_imp.rand()       # skip delay-related rand() call if binary does extra calls
    key = libc_imp.rand()
    block ^= key
    result += p32(block)
```

**Timing considerations:**
- `time(NULL)` has 1-second granularity — start the exploit within the same second as the binary
- Remote targets may have startup delay — try offsets of `+1` or `+2` seconds
- Account for any `rand()` calls between `srand()` and the target usage (e.g., random delays)
- Not 100% reliable on first try — retry with adjacent seeds if needed

**Key insight:** Python's `random` and C's `rand()` are completely different PRNGs. When a C binary uses `srand(time(NULL))`, the only way to reproduce the sequence from Python is `ctypes.CDLL` calling the same libc's `srand`/`rand`. Load the challenge's provided `libc.so.6` for exact compatibility. This works for any C PRNG output prediction — XOR keys, random challenges, token generation, or encrypted heap data.

**Alternative — custom shared library (MireaCTF):**
```c
// random_lib.c — compile with: gcc -shared -o random_lib.so random_lib.c
#include <stdlib.h>
void setseed(int seed) { srand(seed); }
int generate() { return rand() & 0xff; }
```
```python
from ctypes import CDLL
lib = CDLL('./random_lib.so')
lib.setseed(int(time()) + 1)  # +1 for remote delay
numbers = [lib.generate() for _ in range(16)]
```

---

## Layered Encryption Recovery

When binary uses multiple encryption layers:
1. Identify encryption order (e.g., Serpent → TEA)
2. Find seed derivation (e.g., sum of flag chars)
3. Keys often derived from `srand()` sequence
4. Bruteforce seed range (sum of printable ASCII is limited)

## LCG Parameter Recovery Attack

Linear Congruential Generators are weak PRNGs. Given consecutive outputs, recover parameters:

**LCG formula:** `x_{n+1} = (a * x_n + c) mod m`

**Recovery from output sequence (SageMath):**
```python
# Given sequence: [s0, s1, s2, s3, ...]
# crypto-attacks library: github.com/jvdsn/crypto-attacks
from attacks.lcg import parameter_recovery

sequence = [
    72967016216206426977511399018380411256993151454761051136963936354667101207529,
    49670218548812619526153633222605091541916798863041459174610474909967699929824,
    # ... more outputs
]

m, a, c = parameter_recovery.attack(sequence)
print(f"Modulus m: {m}")
print(f"Multiplier a: {a}")
print(f"Increment c: {c}")
```

**Weak RSA from LCG primes:**
- If RSA primes are generated from LCG, recover LCG params first
- Use known plaintext XOR ciphertext to extract LCG outputs
- Regenerate same prime sequence to factor N

```python
# Recover XOR key (which is LCG output)
def recover_lcg_output(plaintext, ciphertext, timestamp):
    pt_bytes = plaintext.encode('utf-8').ljust(32, b'\0')
    ct_int = int.from_bytes(bytes.fromhex(ciphertext), 'big')
    return timestamp ^ int.from_bytes(pt_bytes, 'big') ^ ct_int

# After recovering LCG params, generate RSA primes
lcg = LCG(a, c, m, seed)
primes = []
while len(primes) < 8:
    candidate = lcg.next()
    if is_prime(candidate) and candidate.bit_length() == 256:
        primes.append(candidate)

n = prod(primes)
phi = prod(p - 1 for p in primes)
d = pow(65537, -1, phi)
```

## ChaCha20 Key Recovery

When ChaCha20 key is derived from recoverable data:

```python
from Crypto.Cipher import ChaCha20

# If key derived from predictable source (timestamp, PID, etc.)
for candidate_key in generate_candidates():
    cipher = ChaCha20.new(key=candidate_key, nonce=nonce)
    plaintext = cipher.decrypt(ciphertext)
    if is_valid(plaintext):  # Check for expected format
        print(f"Key found: {candidate_key.hex()}")
        break
```

**Ghidra emulator for key extraction:**
When key is computed by complex function, emulate it rather than reimplementing.

## GF(2) Matrix PRNG Seed Recovery (0xFun 2026)

**Pattern (BitStorm):** PRNG using only XOR, shifts, and rotations is linear over GF(2).

**Key insight:** Express entire PRNG as matrix multiplication: `output_bits = M * seed_bits (mod 2)`. With enough outputs, Gaussian elimination recovers the seed.

```python
import numpy as np

def build_prng_matrix(prng_func, seed_bits=2048, output_bits=2048):
    """Build GF(2) matrix by running PRNG on unit vectors."""
    M = np.zeros((output_bits, seed_bits), dtype=np.uint8)
    for i in range(seed_bits):
        # Set bit i of seed
        seed = 1 << (seed_bits - 1 - i)
        output = prng_func(seed)
        for j in range(output_bits):
            M[j, i] = (output >> (output_bits - 1 - j)) & 1
    return M

# Given output, solve: M * seed = output (mod 2)
# Use GF(2) Gaussian elimination (see modern-ciphers.md solve_gf2)
seed = solve_gf2(M, output_bits_array)
```

**Identification:** Any PRNG using only `^`, `<<`, `>>`, bitwise rotate. DON'T try iterative state recovery — go straight to the matrix.

---

## Middle-Square PRNG Brute Force (UTCTF 2024)

**Pattern (numbers go brrr):** Middle-square method with small seed space.

```python
# PRNG: seed = int(str(seed * seed).zfill(12)[3:9])  — 6-digit seed
# Seed source: int(time.time() * 1000) % (10**6) — only 1M possibilities
# AES key: 8 rounds of PRNG, each produces seed % 2^16 as 2-byte fragment

def middle_square_keygen(seed):
    key = b''
    for _ in range(8):
        seed = int(str(seed * seed).zfill(12)[3:9])
        key += (seed % (2**16)).to_bytes(2, 'big')
    return key

# Brute-force: encrypt known plaintext, compare
for seed in range(10**6):
    key = middle_square_keygen(seed)
    if try_decrypt(ciphertext, key):
        print(f"Seed: {seed}")
        break
```

**Even with time-limited interactions:** 1 known-plaintext pair suffices for offline brute force.

---

## Deterministic RNG from Flag Bytes + Hill Climbing (VuwCTF 2025)

**Pattern (Totally Random Art):** Flag bytes seed Python `random.Random()`. First N bytes of flag are known format, remaining bytes produce deterministic output.

**Attack:** When PRNG seed is known/derivable from flag format, hill-climb unknown characters:
```python
import random

def render(flag_bytes):
    rng = random.Random()
    rng.seed(flag_bytes)
    grid = [[0]*10 for _ in range(5)]
    for b in flag_bytes:
        steps, stroke = divmod(b, 16)
        x, y = 0, 0
        for _ in range(steps):
            dx, dy = rng.choice([(0,1),(0,-1),(1,0),(-1,0)])
            x = (x + dx) % 10
            y = (y + dy) % 5
        grid[y][x] = (grid[y][x] + stroke) % 16
    return grid

# Hill climb: try each byte value, keep the one that maximizes grid match
target = parse_target_art()
flag = list(b'VuwCTF{')
for pos in range(7, 17):
    best_score, best_char = -1, 0
    for c in range(32, 127):
        candidate = bytes(flag + [c])
        score = sum(1 for y in range(5) for x in range(10)
                    if render(candidate)[y][x] == target[y][x])
        if score > best_score:
            best_score, best_char = score, c
    flag.append(best_char)
```

---

## Byte-by-Byte Oracle with Random Mode Matching (VuwCTF 2025)

**Pattern (Unorthodox IV):** Server encrypts with one of N random modes/IVs per encryption. Can submit own plaintexts.

**Attack strategy:**
1. Connect, get encrypted flag
2. Probe with known prefix to check if connection can "reach" the flag's mode (same mode = same ciphertext prefix). ~50 probes, if no match, reconnect.
3. Once reachable, test candidate characters. Mode match AND next byte match = correct char. Mode match but byte mismatch = eliminate candidate permanently.
4. Elimination persists across reconnections.

**Key insight:** Probe for mode reachability first to avoid wasting attempts. Elimination-based search is more efficient than confirmation-based when modes are randomized.

---

## RSA Key Reuse / Replay (UTCTF 2024)

**Pattern (simple signature):** RSA keys reused across rounds with alternating inputs.

**Attack:** Submit previously captured encrypted output back to the server. If keys are static across interactions, replay attacks are trivial. Always check if crypto keys change between rounds.

---

## Logistic Map / Chaotic PRNG Seed Recovery (BYPASS CTF 2025)

**Pattern (Chaotic Trust):** Stream cipher using the logistic map `x_{n+1} = r * x * (1 - x)` as PRNG. Keystream generated by packing iterated float values.

**Key insight:** Logistic map with `r ≈ 4.0` is chaotic but deterministic — recovering the seed (initial x value) enables full keystream reconstruction. Seed is usually a decimal between 0 and 1, such as 0.123456789.

```python
import struct

def logistic_map(x, r=3.99):
    return r * x * (1 - x)

def decrypt_logistic(cipher_hex, seed):
    cipher = bytes.fromhex(cipher_hex)
    x = seed
    stream = b""

    while len(stream) < len(cipher):
        x = logistic_map(x)
        # Pack float as bytes for keystream (check endianness)
        stream += struct.pack("<f", x)[-2:]  # or full 4 bytes

    stream = stream[:len(cipher)]
    return bytes(a ^ b for a, b in zip(cipher, stream))

# Brute-force seed precision
for precision in range(6, 12):
    for base in [123456, 234567, 314159, 271828]:
        seed = base / (10 ** precision)
        result = decrypt_logistic(cipher_hex, seed)
        if b"FLAG" in result or b"CTF" in result:
            print(f"Seed: {seed}, Flag: {result}")
```

**Variations:**
- **r parameter:** Usually `r = 3.99` or `r = 4.0` (full chaos regime)
- **Packing:** `struct.pack("<f", x)` (4 bytes), `struct.pack("<d", x)` (8 bytes), or `[-2:]` for 2-byte fragments
- **Seed range:** Often a recognizable decimal like `0.123456789` or derived from challenge hints

**Identification:** Challenge mentions "chaos", "logistic", "butterfly effect", or provides `r` parameter. Look for source code containing `x = r * x * (1 - x)` iteration.

---

## V8 XorShift128+ State Recovery (Math.random Prediction)

**Pattern:** Web challenge uses `Math.floor(CONST * Math.random())` to generate tokens, codes, or game values. V8's `Math.random()` uses XorShift128+ (xs128p) PRNG. Given consecutive floored outputs, recover the internal state (state0, state1) with Z3, then predict future values.

**V8 internals:**
1. xs128p produces 64-bit state; V8 uses `state0 >> 12 | 0x3FF0000000000000` to create a double in [1.0, 2.0), then subtracts 1.0
2. `Math.random()` reads from a **64-value LIFO cache**. When the cache is empty, `RefillCache()` generates 64 new values. Values are consumed in reverse order from the cache
3. Only `state0` is used for the output (not `state1`)

**xs128p algorithm:**
```python
def xs128p(state0, state1):
    s1 = state0 & 0xFFFFFFFFFFFFFFFF
    s0 = state1 & 0xFFFFFFFFFFFFFFFF
    s1 ^= (s1 << 23) & 0xFFFFFFFFFFFFFFFF
    s1 ^= (s1 >> 17) & 0xFFFFFFFFFFFFFFFF
    s1 ^= s0 & 0xFFFFFFFFFFFFFFFF
    s1 ^= (s0 >> 26) & 0xFFFFFFFFFFFFFFFF
    state0 = state1 & 0xFFFFFFFFFFFFFFFF
    state1 = s1 & 0xFFFFFFFFFFFFFFFF
    return state0, state1, state0  # output is new state0
```

**Z3 solver for `Math.floor(CONST * Math.random())`:**
```python
from z3 import *
from decimal import Decimal
import struct

def to_double(value):
    double_bits = (value >> 12) | 0x3FF0000000000000
    return struct.unpack('d', struct.pack('<Q', double_bits))[0] - 1

def from_double(dbl):
    return struct.unpack('<Q', struct.pack('d', dbl + 1))[0] & 0x7FFFFFFFFFFFFFFF

def sym_xs128p(s0, s1):
    s1_ = s0
    s0_ = s1
    s1_ ^= (s1_ << 23)
    s1_ ^= LShR(s1_, 17)
    s1_ ^= s0_
    s1_ ^= LShR(s0_, 26)
    return s1, s1_  # new state0, state1

def solve_v8_random(observed_values, multiple):
    """Recover xs128p state from consecutive Math.floor(multiple * Math.random()) outputs.
    observed_values must be in REVERSE order (oldest first after tac)."""
    ostate0, ostate1 = BitVecs('ostate0 ostate1', 64)
    sym_s0, sym_s1 = ostate0, ostate1
    slvr = SolverFor("QF_BV")

    for val in observed_values:
        sym_s0, sym_s1 = sym_xs128p(sym_s0, sym_s1)
        calc = LShR(sym_s0, 12)  # V8's ToDouble mantissa bits
        # Constrain: floor(multiple * to_double(state0)) == val
        lower = from_double(Decimal(val) / Decimal(multiple))
        upper = from_double(Decimal(val + 1) / Decimal(multiple))
        lower_m = lower & 0x000FFFFFFFFFFFFF
        upper_m = upper & 0x000FFFFFFFFFFFFF
        upper_e = (upper >> 52) & 0x7FF
        slvr.add(And(lower_m <= calc, Or(upper_m >= calc, upper_e == 1024)))

    if slvr.check() == sat:
        m = slvr.model()
        return m[ostate0].as_long(), m[ostate1].as_long()
    return None, None

# Predict next values after state recovery
def predict_next(state0, state1, multiple, count):
    results = []
    for _ in range(count):
        state0, state1, output = xs128p(state0, state1)
        import math
        results.append(math.floor(multiple * to_double(output)))
    return results
```

**Usage (tool: d0nutptr/v8_rand_buster):**
```bash
# Collect observed values, reverse them (LIFO cache order), pipe to solver
cat observed_codes.txt | tac | python3 xs128p.py --multiple 100000

# Generate predictions from recovered state
python3 xs128p.py --multiple 100000 --gen <state0>,<state1>,<count>
```

**Key insight:** The LIFO cache means observed values are in reverse generation order — reverse them with `tac` before solving. The Z3 `QF_BV` (quantifier-free bitvector) theory efficiently handles the bitwise operations. Typically 5-10 consecutive outputs suffice for a unique solution.

**Common pitfalls:**
- Forgetting to reverse the observation order (cache is LIFO)
- Multiple browser tabs or web workers may have separate PRNG states
- Cache boundary (every 64 calls) can introduce discontinuities if observations span a refill

**Inverse xorshift128+ (backward prediction):** After recovering state, step the PRNG backward to predict values generated *before* the observed sequence. Essential when the target value was generated earlier than observations (e.g., predicting another user's 2FA code). (Midnight Flag 2026)

```python
def undo_rshift_xor(val, shift):
    """Invert val ^= (val >> shift)"""
    result = val
    for _ in range(3):  # 3 iterations sufficient for 64-bit
        result = val ^ (result >> shift)
    return result & 0xFFFFFFFFFFFFFFFF

def undo_lshift_xor(val, shift):
    """Invert val ^= (val << shift)"""
    result = val
    for _ in range(3):
        result = val ^ ((result << shift) & 0xFFFFFFFFFFFFFFFF)
    return result & 0xFFFFFFFFFFFFFFFF

def reverse_step(s0, s1):
    """Run xs128p one step backward: (s0, s1) → (old_s0, old_s1)"""
    old_s1 = s0
    known = (s1 ^ s0 ^ ((s0 >> 26) & 0xFFFFFFFFFFFFFFFF)) & 0xFFFFFFFFFFFFFFFF
    x = undo_rshift_xor(known, 17)
    old_s0 = undo_lshift_xor(x, 23)
    return old_s0, old_s1

# Usage: step backward N times from recovered state
for _ in range(N):
    state0, state1 = reverse_step(state0, state1)
    predicted = math.floor(CONST * to_double(state0))
```

**When to use:** Web challenge where JavaScript generates predictable-looking random values (tokens, verification codes, game rolls) using `Math.random()`. Look for patterns like `Math.floor(N * Math.random())` or `Math.random().toString(36).substr(2)` in client-side or server-side Node.js code.

---

## Password Cracking Strategy

**Attack order for unknown passwords:**
1. Common wordlists: `rockyou.txt`, `10k-common.txt`
2. Theme-based wordlist (usernames, challenge keywords)
3. Rules attack: wordlist + `best66.rule`, `dive.rule`
4. Hybrid: `word + ?d?d?d?d` (word + 4 digits)
5. Brute force: start at 4 chars, increase

**SHA256 with hex salt (VuwCTF 2025, Delicious Cooking):** Format `hash$hex_salt`. Salt must be hex-decoded before `SHA256(password + salt_bytes)`. Password often derivable from security questions (e.g., "fav movie + PIN" = "ratatouille0000"-"ratatouille9999").

**CTF password patterns:**
```text
base_password + year     → actnowonclimatechange2026
username + digits        → nemo123, admin2026
theme + numbers          → flag2026, ctf2025
leet speak               → p@ssw0rd, s3cr3t
```

**Hashcat modes reference:**
```bash
# Common modes
-m 0      # MD5
-m 1000   # NTLM
-m 5600   # NTLMv2
-m 13600  # WinZip AES
-m 13000  # RAR5
-m 11600  # 7-Zip

# Attack modes
-a 0      # Dictionary
-a 3      # Brute force mask
-a 6      # Hybrid (word + mask)
-a 7      # Hybrid (mask + word)
```

**When password relates to another in challenge:**
- Try variations: `password + year`, `password + 123`
- Try reversed: `drowssap`
- Try with common suffixes: `!`, `@`, `#`, `1`, `123`
- If SMB/FTP password known, ZIP password often related

---

## Mersenne Twister Seed Recovery from Subset Sum (Tokyo Westerns 2017)

**Pattern:** MT19937 seeded with a 32-bit value generates subset-sum problems (e.g., "which elements from this set sum to target?"). Solving small subset-sum problems leaks specific MT output values. Two recovered outputs at indices 0 and 227 are sufficient to invert the MT seeding process.

**MT twist function relationship:**
```text
mt[i] = mt[i-624] XOR twist(mt[i-624], mt[i-623])
```
At the wrap-around: `mt[624]` depends on `mt[0]` (new cycle) and `mt[397]` (old cycle). Recovering `mt[0]` and `mt[227]` (which is related to `mt[624-227] = mt[397]`) via subset-sum solutions reveals enough to invert the twist recurrence.

```python
import random

def crack_seed_from_two_outputs(mt0_val, mt227_val):
    """Try all 2^32 seeds until MT outputs match recovered values."""
    for seed in range(2**32):
        r = random.Random()
        r.seed(seed)
        # Generate enough to reach indices 0 and 227
        outputs = [r.getrandbits(32) for _ in range(228)]
        if outputs[0] == mt0_val and outputs[227] == mt227_val:
            return seed
    return None

# After recovering seed, all future (and past) outputs are predictable
r = random.Random()
r.seed(recovered_seed)
```

**Key insight:** MT19937 seeds recoverable from as few as two state values (indices 0 and 227) via the twist function's wrap-around relationship. Any challenge that exposes MT state values through solvable mathematical puzzles is vulnerable to full seed recovery.

**References:** Tokyo Westerns CTF 2017

---

## MT19937 State Recovery via Constraint Propagation (HITCON 2017)

**Pattern:** Server generates problems that leak 24-120 bits of PRNG output per round (e.g., partial bit-patterns, subset sums, modular reductions). Rather than collecting 624 full 32-bit outputs, model the MT state as an array of per-cell candidate sets and propagate constraints bidirectionally through the MT recurrence.

**MT recurrence dependencies:**
```text
state[i] = state[i-624] XOR twist(state[i-624], state[i-623])
```
This means `state[x]` depends on `state[x-624]`, `state[x-623]`, and `state[x-227]` (via the generate step). Partial knowledge at any index propagates in both directions.

**Constraint propagation approach:**
```python
# Model: each state word starts as a set of 2^32 candidates
# Partial observation: narrow candidates for observed indices
# Propagate: for each constrained cell, narrow related cells

def propagate_forward(state_candidates, idx):
    """MT: state[idx+624] = f(state[idx], state[idx+1])"""
    for s0 in state_candidates[idx]:
        for s1 in state_candidates[idx + 1]:
            new_val = mt_twist(s0, s1)
            state_candidates[idx + 624].add(new_val)

def propagate_backward(state_candidates, idx):
    """Invert MT twist to constrain earlier states from later ones."""
    for val in state_candidates[idx]:
        # Recover state[idx-624] given state[idx] and state[idx-623]
        for s1 in state_candidates[idx - 623]:
            s0 = mt_untwist(val, s1)
            state_candidates[idx - 624].add(s0)

# After ~20 partial observations across different positions:
# Most cells converge to single candidates → full state determined
```

**Key insight:** MT19937's recurrence dependencies allow bidirectional constraint propagation — partial knowledge at multiple positions narrows candidates until the full 624-word state is determined. The number of partial observations needed scales inversely with bits leaked per observation: ~20 observations of 24+ bits each typically suffice.

**References:** HITCON CTF 2017


# rsa-attacks-2

# CTF Crypto - RSA Attacks (Part 2: Specialized Techniques)

## Table of Contents
- [RSA p=q Validation Bypass (BearCatCTF 2026)](#rsa-pq-validation-bypass-bearcatctf-2026)
- [RSA Cube Root CRT when gcd(e, phi) > 1 (BearCatCTF 2026)](#rsa-cube-root-crt-when-gcde-phi--1-bearcatctf-2026)
- [Factoring n from Multiple of phi(n) (BearCatCTF 2026)](#factoring-n-from-multiple-of-phin-bearcatctf-2026)
- [RSA Signature Forgery via Multiplicative Homomorphism (MMA CTF 2015)](#rsa-signature-forgery-via-multiplicative-homomorphism-mma-ctf-2015)
- [Weak RSA Key Generation via Base Representation (Sharif CTF 2016)](#weak-rsa-key-generation-via-base-representation-sharif-ctf-2016)
- [RSA with gcd(e, phi(n)) > 1 (CSAW 2015)](#rsa-with-gcde-phin--1-csaw-2015)
- [Batch GCD for Shared Prime Factoring (BSidesSF 2025)](#batch-gcd-for-shared-prime-factoring-bsidessf-2025)
- [RSA Partial Key Recovery from dp dq qinv (0CTF 2016)](#rsa-partial-key-recovery-from-dp-dq-qinv-0ctf-2016)
- [RSA-CRT Fault Attack / Bit-Flip Recovery (CSAW CTF 2016)](#rsa-crt-fault-attack--bit-flip-recovery-csaw-ctf-2016)
- [RSA Homomorphic Decryption Oracle Bypass (ECTF 2016)](#rsa-homomorphic-decryption-oracle-bypass-ectf-2016)
- [RSA with Small Prime Factors and CRT Decomposition (Hack The Vote 2016)](#rsa-with-small-prime-factors-and-crt-decomposition-hack-the-vote-2016)
- [RSA Timing Attack on Montgomery Reduction (DEF CON 2017)](#rsa-timing-attack-on-montgomery-reduction-def-con-2017)
- [Bleichenbacher Low-Exponent RSA Signature Forgery (Google CTF 2017)](#bleichenbacher-low-exponent-rsa-signature-forgery-google-ctf-2017)
- [Coppersmith Small Roots for Linearly Related Primes (Tokyo Westerns 2017)](#coppersmith-small-roots-for-linearly-related-primes-tokyo-westerns-2017)

See also: [rsa-attacks.md](rsa-attacks.md) for foundational RSA attacks (small e, Wiener, Fermat, Pollard, Hastad, common modulus, Manger oracle, Coppersmith).

---

## RSA p=q Validation Bypass (BearCatCTF 2026)

**Pattern (Pickme):** Server validates user-submitted RSA key (checks `n`, `e`, `d`, `p*q=n`, `e*d ≡ 1 mod phi`), encrypts the flag, then tries test decryption. If decryption fails, leaks ciphertext in error message.

**Exploit:** Set `p = q`. The server computes `phi = (p-1)*(q-1) = (p-1)^2` (incorrect — real totient of `p^2` is `p*(p-1)`). All validation checks pass, but decryption with the wrong `d` fails, leaking the ciphertext.

```python
from Crypto.Util.number import getPrime, inverse

p = getPrime(512)
q = p  # p = q!
n = p * q  # = p^2
e = 65537
wrong_phi = (p - 1) * (q - 1)  # = (p-1)^2
d = inverse(e, wrong_phi)  # passes server validation

# Server encrypts flag with our key, test decryption fails → leaks ciphertext c
# Decrypt with correct totient:
real_phi = p * (p - 1)
real_d = inverse(e, real_phi)
flag = pow(c, real_d, n)
```

**Key insight:** `phi(p^2) = p*(p-1)`, NOT `(p-1)^2`. When a server validates RSA parameters but uses `(p-1)*(q-1)` without checking `p != q`, setting `p=q` creates a working key that the server will miscompute the private exponent for, causing decryption failure and error-path data leakage.

---

## RSA Cube Root CRT when gcd(e, phi) > 1 (BearCatCTF 2026)

**Pattern (Kidd's Crypto):** RSA with `e=3`, modulus composed of many small primes all ≡ 1 (mod 3). Since each `p-1` is divisible by 3, `gcd(e, phi(n)) = 3^k` and the standard modular inverse `d = e^-1 mod phi` doesn't exist.

**Solution:** Compute cube roots per-prime via CRT:
```python
from sympy.ntheory.residues import nthroot_mod
from sympy.ntheory.modular import crt

primes = [p1, p2, ..., p13]  # All ≡ 1 mod 3

# For each prime, find all 3 cube roots of c mod p
roots_per_prime = []
for p in primes:
    roots = nthroot_mod(c % p, 3, p, all_roots=True)
    roots_per_prime.append(roots)

# Try all 3^13 = 1,594,323 combinations
from itertools import product
for combo in product(*roots_per_prime):
    result, mod = crt(primes, list(combo))
    try:
        text = long_to_bytes(result).decode('ascii')
        if text.isprintable():
            print(f"Flag: {text}")
            break
    except:
        continue
```

**Key insight:** When `gcd(e, phi(n)) > 1`, standard RSA decryption fails. Factor `n`, compute eth roots modulo each prime separately (each prime ≡ 1 mod e gives `e` roots), then enumerate all CRT combinations. Feasible when the number of primes is small (3^13 ≈ 1.6M combinations).

---

## Factoring n from Multiple of phi(n) (BearCatCTF 2026)

**Pattern (Twisted Pair):** Given RSA `n` and a leaked pair `(re, rd)` where `re * rd ≡ 1 (mod k*phi(n))`. The value `re*rd - 1` is a multiple of `phi(n)`, enabling probabilistic factoring.

```python
import random
from math import gcd

def factor_from_phi_multiple(n, phi_multiple):
    """Factor n given any multiple of phi(n) using Miller-Rabin variant."""
    # Write phi_multiple = 2^s * d where d is odd
    s, d = 0, phi_multiple
    while d % 2 == 0:
        s += 1
        d //= 2

    for _ in range(100):  # 100 attempts
        a = random.randrange(2, n - 1)
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(s - 1):
            prev = x
            x = pow(x, 2, n)
            if x == n - 1:
                break
            if x == 1:
                # prev is non-trivial square root of 1
                p = gcd(prev - 1, n)
                if 1 < p < n:
                    return p, n // p
        # Check final
        if x != n - 1:
            p = gcd(x - 1, n)
            if 1 < p < n:
                return p, n // p
    return None

phi_mult = re * rd - 1
p, q = factor_from_phi_multiple(n, phi_mult)
```

**Key insight:** Any multiple of `phi(n)` — not just `phi(n)` itself — enables factoring via the Miller-Rabin square root technique. If a server leaks `e*d` for any key pair, or if `re*rd - 1` is given, compute `gcd(a^(m/2) - 1, n)` for random `a` values. Succeeds with probability ≥ 1/2 per attempt.

---

## RSA Signature Forgery via Multiplicative Homomorphism (MMA CTF 2015)

**Pattern:** Signing oracle refuses to sign the target message `m` but will sign other values. Unpadded RSA is multiplicatively homomorphic: `S(a) * S(b) mod n == S(a * b) mod n`.

```python
# Factor target message and sign each factor separately
divisor = 2
assert target_msg % divisor == 0
sig_a = sign_oracle(target_msg // divisor)
sig_b = sign_oracle(divisor)
forged_sig = (sig_a * sig_b) % n
```

**Key insight:** Textbook RSA signatures are homomorphic: `m^d mod n` preserves multiplication. If the oracle blacklists `m` but signs its factors, multiply the partial signatures. To find a suitable factorization, try small divisors (2, 3, ...) until `m / divisor` also passes the blacklist check. This is why PKCS#1 padding is essential — padded messages cannot be factored into other valid padded messages.

---

## Weak RSA Key Generation via Base Representation (Sharif CTF 2016)

When RSA primes are generated as `p = kp * B + tp` where B = product_of_small_primes * 2^400 and kp is small (< 2^12):

1. **Compute n mod B^2:** Since n = p*q and both p,q have form k*B + t, expansion gives: `n = kp*kq*B^2 + (kp*tq + kq*tp)*B + tp*tq`
2. **Recover kp*kq:** Brute-force 2^24 possibilities for (kp, kq) where each < 2^12
3. **Solve quadratic:** From known kp*kq and the middle coefficient, recover tp and tq

```python
B = product_of_first_443_primes * (2**400)
B2 = B * B

# n = A*B^2 + C*B + D where A=kp*kq, D=tp*tq
A = n // B2
D = n % B

# Brute-force kp, kq such that kp*kq == A
for kp in range(1, 2**12):
    if A % kp == 0:
        kq = A // kp
        # Solve for tp, tq from remaining equations
```

**Key insight:** Structured prime generation creates a mixed-radix representation of n, allowing efficient factorization by reducing the search space from exponential to polynomial.

---

## RSA with gcd(e, phi(n)) > 1 (CSAW 2015)

When `gcd(e, phi(n)) = g > 1`, standard RSA decryption fails because `d = e^(-1) mod phi(n)` doesn't exist. Instead:

1. Compute `e' = e / g` (reduced exponent)
2. Compute `d' = e'^(-1) mod phi(n)` (now coprime)
3. Compute `m^g = pow(c, d', n)` (partial decryption)
4. Take g-th root: iterate candidate m values where `pow(m, g, n) == m^g`

```python
from sympy import factorint, mod_inverse
from gmpy2 import iroot

g = gcd(e, phi_n)
e_prime = e // g
d_prime = mod_inverse(e_prime, phi_n)
m_g = pow(c, d_prime, n)

# For small g, try integer root first
m, is_exact = iroot(m_g, g)
if is_exact:
    plaintext = int(m)
else:
    # Brute-force: m_g + k*n for small k
    for k in range(10000):
        m, exact = iroot(m_g + k * n, g)
        if exact:
            plaintext = int(m)
            break
```

**Key insight:** Reduce e by the GCD to make decryption possible, then recover the g-th root. Filter candidates by checking plaintext length or ASCII validity.

---

## Batch GCD for Shared Prime Factoring (BSidesSF 2025)

When multiple RSA moduli share a common prime factor (due to faulty hardware RNG, smartcard bugs, or weak seeding):

```python
from math import gcd
from functools import reduce

def batch_gcd(moduli):
    """Find shared factors among a list of RSA moduli"""
    # Product tree
    product = reduce(lambda a, b: a * b, moduli)

    factors = {}
    for n in moduli:
        g = gcd(n, product // n)
        if g != 1 and g != n:
            p = g
            q = n // p
            factors[n] = (p, q)
    return factors

# Usage: given list of public keys from smartcards
moduli = [key.n for key in public_keys]
shared = batch_gcd(moduli)
for n, (p, q) in shared.items():
    phi = (p - 1) * (q - 1)
    d = pow(e, -1, phi)  # Private exponent
```

For keys with patterned primes (hardware RNG faults producing primes with fixed bit patterns), combine with Coppersmith's method to recover remaining random bits. See [advanced-math.md](advanced-math.md) for Coppersmith.

**Key insight:** A single shared prime compromises both keys. Batch GCD runs in O(n log n) time via product/remainder trees, making it feasible for thousands of keys. Real-world incidents: Taiwanese citizen smartcards (2013), many IoT device certificates.

---

## RSA Partial Key Recovery from dp dq qinv (0CTF 2016)

**Pattern:** Given only the CRT (Chinese Remainder Theorem) exponents (dp, dq, qinv) from a partial PEM (Privacy Enhanced Mail) key leak (e.g., bottom portion of private key file), recover the full key. Since `dp = d mod (p-1)`, iterate k and check if `p = (dp * e - 1) / k + 1` is prime.

```python
import gmpy2
# dp, dq, qinv extracted from partial PEM; e is known (usually 65537)
for k in range(3, e):
    p_candidate = (dp * e - 1) // k + 1
    if gmpy2.is_prime(p_candidate):
        p = p_candidate
        break
# Similarly recover q from dq; verify qinv * q % p == 1
```

**Key insight:** Leaking just the CRT exponents from an RSA private key is sufficient to fully recover p and q. Recovery is O(e) -- essentially instant for e=65537.

---

## RSA-CRT Fault Attack / Bit-Flip Recovery (CSAW CTF 2016)

RSA signing service with intermittent single-bit errors in private exponent d during CRT computation. Collect valid and faulty signatures, then detect which bit flipped.

```python
from Crypto.Util.number import inverse

def recover_d_bits(n, e, valid_sig, faulty_sigs, msg):
    """Recover private key d bit-by-bit from CRT fault signatures"""
    d_bits = [0] * 1024
    m = pow(msg, 1, n)
    s_good = valid_sig
    for s_bad in faulty_sigs:
        # ratio reveals which bit was flipped
        ratio = (s_bad * inverse(s_good, n)) % n
        for k in range(1024):
            if ratio == pow(2, pow(2, k, n), n) or ratio == pow(inverse(2, n), pow(2, k, n), n):
                d_bits[k] = 1
                break
    return d_bits
```

**Key insight:** When RSA-CRT has a single-bit fault in d, the ratio `faulty_sig * valid_sig^(-1) mod n` equals `2^(2^k) mod n` for the flipped bit position k, enabling bit-by-bit private key recovery.

---

## RSA Homomorphic Decryption Oracle Bypass (ECTF 2016)

Service decrypts any ciphertext except the target flag ciphertext. Exploit RSA's multiplicative homomorphism: `Dec(a * b mod n) = Dec(a) * Dec(b) mod n`.

```python
from Crypto.Util.number import long_to_bytes, inverse

# Server refuses to decrypt enc_flag directly
# But RSA is homomorphic: Dec(A*B) = Dec(A) * Dec(B) mod n
enc_2 = pow(2, e, n)  # encrypt the number 2
enc_flag_times_2 = (enc_flag * enc_2) % n  # = Enc(flag * 2)

dec_flag_times_2 = oracle_decrypt(enc_flag_times_2)  # server allows this
dec_2 = oracle_decrypt(enc_2)                         # server allows this

# Recover flag: (flag * 2) * inverse(2) mod n = flag
flag = (dec_flag_times_2 * inverse(dec_2, n)) % n
print(long_to_bytes(flag))
```

**Key insight:** RSA without padding is multiplicatively homomorphic. Multiply the forbidden ciphertext by `Enc(r)` for any `r`, decrypt the product, then divide by `r` to recover the original plaintext.

---

## RSA with Small Prime Factors and CRT Decomposition (Hack The Vote 2016)

RSA modulus composed of many small prime factors (primes < 251, each appearing ~1500 times). Factor n, then use CRT to decompose decryption.

```python
from sympy import factorint
from sympy.ntheory.residues import primitive_root
from functools import reduce

n = ...  # modulus with small factors
e = 65537
c = ...  # ciphertext

factors = factorint(n)  # {p1: k1, p2: k2, ...} where pi are small primes

# Decrypt modulo each prime power, then combine with CRT
from sympy.ntheory.modular import crt as chinese_remainder_theorem

remainders = []
moduli = []
for p, k in factors.items():
    pk = p ** k
    phi_pk = (p - 1) * p ** (k - 1)  # Euler's totient for prime power
    d_pk = pow(e, -1, phi_pk)
    m_pk = pow(c, d_pk, pk)
    remainders.append(m_pk)
    moduli.append(pk)

# Combine using CRT
m = chinese_remainder_theorem(moduli, remainders)[0]
```

**Key insight:** When n has many small prime factors, compute `d mod phi(p^k)` for each prime power independently, decrypt mod each, then combine via CRT. Much faster than computing `d mod phi(n)` directly.

---

## RSA Timing Attack on Montgomery Reduction (DEF CON 2017)

**Pattern:** Recover RSA private key bits via Kocher's timing attack when the number of modular subtractions during Montgomery reduction is leaked.

```python
# Montgomery multiplication: extra subtraction when result >= modulus
# Leaked: count of extra subtractions per signature operation
# Attack: predict subtraction count for each private key bit guess

# For each bit position i (MSB to LSB):
#   Guess bit = 0: predict timing for square only
#   Guess bit = 1: predict timing for square + multiply
#   Compare predictions against observed timing data
#   Correct guess produces statistically significant correlation

# ~200K signatures needed for 768-bit key recovery
# Attacking squaring reduction is more effective than multiply
import numpy as np
for bit_pos in range(key_bits):
    for guess in [0, 1]:
        predicted = predict_reductions(known_bits + [guess], messages)
        correlation = np.corrcoef(predicted, observed)[0, 1]
    known_bits.append(0 if corr_0 > corr_1 else 1)
```

**Key insight:** Montgomery multiplication performs an extra conditional subtraction when the intermediate result exceeds the modulus. If this count leaks (via timing, power, or as in this CTF -- directly), each bit of the private exponent can be determined by comparing predicted vs. observed subtraction patterns across many operations.

**References:** DEF CON 2017

---

## Bleichenbacher Low-Exponent RSA Signature Forgery (Google CTF 2017)

**Pattern:** Forge PKCS#1 v1.5 RSA signatures when e=3 by constructing a value whose cube root produces valid padding without knowing the private key.

```python
# PKCS#1 v1.5 signature format:
# 00 01 FF FF ... FF 00 [DigestInfo] [Hash]
# With e=3, forge signature s where s^3 has correct prefix

# Construct target block (2048-bit key, SHA-256):
# 00 01 FF ... FF 00 [SHA-256 DigestInfo] [hash] [garbage]
import gmpy2
prefix = b'\x00\x01' + b'\xff' * padding_len + b'\x00' + digest_info + hash_value
# Convert to integer, append zeros for garbage bytes
target = int.from_bytes(prefix + b'\x00' * garbage_len, 'big')
# Cube root (rounds down, garbage absorbs the remainder)
forged_sig = gmpy2.iroot(target, 3)[0] + 1  # +1 to round up
# Verify: forged_sig^3 starts with correct PKCS#1 prefix
```

**Key insight:** PKCS#1 v1.5 signature verification checks that `sig^e mod n` starts with `00 01 FF...FF 00 DigestInfo Hash`. With e=3, an attacker computes the cube root of a carefully constructed value with the correct prefix and ignores trailing bytes. Implementations that don't verify the padding extends to the full block length (CVE-2006-4339) accept the forgery.

**References:** Google CTF 2017

---

## Coppersmith Small Roots for Linearly Related Primes (Tokyo Westerns 2017)

**Pattern:** RSA where `q = k*p + delta` for a known small constant `k` and unknown small `delta`. Since `p ≈ sqrt(N/k)`, approximate `q_approx = k * isqrt(N // k) + 2^512` as an upper bound. The univariate polynomial `F(x) = q_approx - x` has `delta` as a small root modulo `q` (which divides N). Coppersmith's method finds this root when `delta < N^(1/4)`.

```python
from sage.all import *

N, e, c = ...  # RSA parameters
k = 19  # known relationship: q = k*p + delta

# Approximate q from sqrt(N/k)
q_approx = k * isqrt(N // k) + 2**512

# Build univariate polynomial with q_approx as approximate root of N mod q
R.<x> = PolynomialRing(Zmod(N))
f = q_approx - x  # root is delta = q_approx - q

# Coppersmith: find small root x = delta < N^0.25
roots = f.small_roots(X=2**512, beta=0.5)
if roots:
    q = int(q_approx - roots[0])
    p = N // q
    assert p * q == N
    phi = (p - 1) * (q - 1)
    d = pow(e, -1, phi)
    flag = long_to_bytes(pow(c, d, N))
```

**Key insight:** When `q ≈ k*p`, approximately half the bits of `p` (and `q`) are recoverable from `sqrt(N/k)`. The remaining unknown `delta` is small enough for Coppersmith when `delta < N^(1/4)`. The upper bound `q_approx` must exceed `q`; add a safety margin of `2^(bitlen/2)` to ensure the root is captured.

**References:** Tokyo Westerns CTF 2017


# rsa-attacks

# CTF Crypto - RSA Attacks

## Table of Contents
- [Small Public Exponent (Cube Root)](#small-public-exponent-cube-root)
- [Common Modulus Attack](#common-modulus-attack)
- [Wiener's Attack (Small Private Exponent)](#wieners-attack-small-private-exponent)
- [Pollard's p-1 Factorization](#pollards-p-1-factorization)
- [Hastad's Broadcast Attack](#hastads-broadcast-attack)
- [RSA with Consecutive Primes (Fermat Factorization)](#rsa-with-consecutive-primes-fermat-factorization)
- [Multi-Prime RSA](#multi-prime-rsa)
- [RSA with Restricted-Digit Primes (LACTF 2026)](#rsa-with-restricted-digit-primes-lactf-2026)
- [Coppersmith for Structured RSA Primes (LACTF 2026)](#coppersmith-for-structured-rsa-primes-lactf-2026)
- [Manger's RSA Padding Oracle Attack (Nullcon 2026)](#mangers-rsa-padding-oracle-attack-nullcon-2026)
- [Manger's Attack on RSA-OAEP via Timing Oracle (HTB Early Bird)](#mangers-attack-on-rsa-oaep-via-timing-oracle-htb-early-bird)
- [Polynomial Hash with Trivial Root (Pragyan 2026)](#polynomial-hash-with-trivial-root-pragyan-2026)
- [Polynomial CRT in GF(2)[x] (Nullcon 2026)](#polynomial-crt-in-gf2x-nullcon-2026)
- [Affine Cipher over Non-Prime Modulus (Nullcon 2026)](#affine-cipher-over-non-prime-modulus-nullcon-2026)
- [Hastad Broadcast Attack with Linear Padding -- Coppersmith (PlaidCTF 2017)](#hastad-broadcast-attack-with-linear-padding----coppersmith-plaidctf-2017)
- [rsa-attacks-2.md: RSA p=q Validation Bypass (BearCatCTF 2026)](rsa-attacks-2.md#rsa-pq-validation-bypass-bearcatctf-2026)
- [rsa-attacks-2.md: RSA Cube Root CRT when gcd(e, phi) > 1 (BearCatCTF 2026)](rsa-attacks-2.md#rsa-cube-root-crt-when-gcde-phi-1-bearcatctf-2026)
- [rsa-attacks-2.md: Factoring n from Multiple of phi(n) (BearCatCTF 2026)](rsa-attacks-2.md#factoring-n-from-multiple-of-phin-bearcatctf-2026)
- [rsa-attacks-2.md: RSA Signature Forgery via Multiplicative Homomorphism (MMA CTF 2015)](rsa-attacks-2.md#rsa-signature-forgery-via-multiplicative-homomorphism-mma-ctf-2015)
- [rsa-attacks-2.md: Weak RSA Key Generation via Base Representation (Sharif CTF 2016)](rsa-attacks-2.md#weak-rsa-key-generation-via-base-representation-sharif-ctf-2016)
- [rsa-attacks-2.md: RSA with gcd(e, phi(n)) > 1 (CSAW 2015)](rsa-attacks-2.md#rsa-with-gcde-phin-1-csaw-2015)
- [rsa-attacks-2.md: Batch GCD for Shared Prime Factoring (BSidesSF 2025)](rsa-attacks-2.md#batch-gcd-for-shared-prime-factoring-bsidessf-2025)
- [rsa-attacks-2.md: RSA Partial Key Recovery from dp dq qinv (0CTF 2016)](rsa-attacks-2.md#rsa-partial-key-recovery-from-dp-dq-qinv-0ctf-2016)
- [rsa-attacks-2.md: RSA-CRT Fault Attack / Bit-Flip Recovery (CSAW CTF 2016)](rsa-attacks-2.md#rsa-crt-fault-attack-bit-flip-recovery-csaw-ctf-2016)
- [rsa-attacks-2.md: RSA Homomorphic Decryption Oracle Bypass (ECTF 2016)](rsa-attacks-2.md#rsa-homomorphic-decryption-oracle-bypass-ectf-2016)
- [rsa-attacks-2.md: RSA with Small Prime Factors and CRT Decomposition (Hack The Vote 2016)](rsa-attacks-2.md#rsa-with-small-prime-factors-and-crt-decomposition-hack-the-vote-2016)

---

## Small Public Exponent (Cube Root)

**Pattern:** Small `e` (typically 3) with small message. When `m^e < n`, the ciphertext is just `m^e` without modular reduction — take the integer eth root.

```python
import gmpy2

def small_e_attack(c, e):
    """Recover plaintext when m^e < n (no modular wrap)."""
    m, exact = gmpy2.iroot(c, e)
    if exact:
        return int(m)
    return None

# Usage
m = small_e_attack(c, e=3)
print(bytes.fromhex(hex(m)[2:]))
```

**When it fails:** If `m^e > n` (message padded or large), the modular reduction destroys the simple root. In that case, try Hastad's broadcast attack or Coppersmith's short-pad attack.

---

## Common Modulus Attack

**Pattern:** Same message encrypted with same `n` but two different public exponents `e1`, `e2` where `gcd(e1, e2) = 1`. Recover plaintext without factoring `n`.

```python
from math import gcd

def common_modulus_attack(c1, c2, e1, e2, n):
    """Recover plaintext from two encryptions with same n, coprime e1/e2."""
    # Extended GCD: find a, b such that a*e1 + b*e2 = 1
    def extended_gcd(a, b):
        if a == 0: return b, 0, 1
        g, x, y = extended_gcd(b % a, a)
        return g, y - (b // a) * x, x

    g, a, b = extended_gcd(e1, e2)
    assert g == 1, "e1 and e2 must be coprime"

    # m = c1^a * c2^b mod n
    # Handle negative exponent by using modular inverse
    if a < 0:
        c1 = pow(c1, -1, n)
        a = -a
    if b < 0:
        c2 = pow(c2, -1, n)
        b = -b
    m = (pow(c1, a, n) * pow(c2, b, n)) % n
    return m
```

**Key insight:** Two encryptions of the same message under the same modulus but different exponents leak the plaintext via Bezout's identity. No factoring required.

---

## Wiener's Attack (Small Private Exponent)

**Pattern:** Private exponent `d` is small (d < N^0.25). The continued fraction expansion of `e/n` reveals `d`.

```python
def wiener_attack(e, n):
    """Recover d when d < N^0.25 using continued fraction expansion of e/n."""
    def continued_fraction(num, den):
        cf = []
        while den:
            q, r = divmod(num, den)
            cf.append(q)
            num, den = den, r
        return cf

    def convergents(cf):
        convs = []
        h0, h1 = 0, 1
        k0, k1 = 1, 0
        for a in cf:
            h0, h1 = h1, a * h1 + h0
            k0, k1 = k1, a * k1 + k0
            convs.append((h1, k1))
        return convs

    cf = continued_fraction(e, n)
    for k, d in convergents(cf):
        if k == 0:
            continue
        # Check if d is valid: phi = (e*d - 1) / k must be integer
        if (e * d - 1) % k != 0:
            continue
        phi = (e * d - 1) // k
        # phi = (p-1)(q-1) = n - p - q + 1, so p+q = n - phi + 1
        s = n - phi + 1
        # p and q are roots of x^2 - s*x + n = 0
        discriminant = s * s - 4 * n
        if discriminant < 0:
            continue
        from math import isqrt
        t = isqrt(discriminant)
        if t * t == discriminant:
            return d
    return None

# Usage
d = wiener_attack(e, n)
m = pow(c, d, n)
```

**When to use:** Very large `e` (close to `n`) often indicates small `d`. Also try `owiener` Python package: `pip install owiener`.

---

## Pollard's p-1 Factorization

**Pattern:** One prime factor `p` has a smooth `p-1` (all prime factors of `p-1` are small). Compute `a^(B!) mod n`; GCD with `n` reveals `p`.

```python
from math import gcd

def pollard_p1(n, B=100000):
    """Factor n when p-1 is B-smooth for some prime factor p."""
    a = 2
    for j in range(2, B + 1):
        a = pow(a, j, n)
        d = gcd(a - 1, n)
        if 1 < d < n:
            return d, n // d
    return None

# Usage
result = pollard_p1(n)
if result:
    p, q = result
```

**Key insight:** By Fermat's little theorem, if `p-1` divides `B!`, then `a^(B!) ≡ 1 (mod p)`, so `gcd(a^(B!) - 1, n)` gives `p`. Increase `B` for larger smooth bounds. CTF primes generated with `getStrongPrime()` or similar are resistant.

---

## Hastad's Broadcast Attack

**Pattern:** Same plaintext `m` encrypted with `e` different public keys (all with exponent `e`, typically `e=3`). Use CRT to reconstruct `m^e`, then take the eth root.

```python
from functools import reduce

def hastad_broadcast(ciphertexts, moduli, e):
    """Recover m from e encryptions with the same exponent e."""
    assert len(ciphertexts) >= e and len(moduli) >= e

    # Chinese Remainder Theorem
    def crt(remainders, moduli):
        N = reduce(lambda a, b: a * b, moduli)
        result = 0
        for r, m in zip(remainders, moduli):
            Ni = N // m
            Mi = pow(Ni, -1, m)
            result += r * Ni * Mi
        return result % N

    # CRT gives m^e (mod N1*N2*...*Ne)
    # Since m < each Ni, m^e < N1*N2*...*Ne, so no modular reduction occurred
    me = crt(ciphertexts[:e], moduli[:e])

    import gmpy2
    m, exact = gmpy2.iroot(me, e)
    if exact:
        return int(m)
    return None

# Usage (e=3, three encryptions)
m = hastad_broadcast([c1, c2, c3], [n1, n2, n3], e=3)
print(bytes.fromhex(hex(m)[2:]))
```

**Key insight:** CRT reconstructs `m^e` exactly (no modular reduction) because `m < min(n_i)` and therefore `m^e < n_1 * n_2 * ... * n_e`. Taking the integer eth root recovers `m`.

---

## Hastad Broadcast Attack with Linear Padding -- Coppersmith (PlaidCTF 2017)

**Pattern:** Extension of Hastad's broadcast attack when each recipient applies a known linear transform `c_i = (a_i * m + b_i)^e mod n_i` before encryption.

```python
# Standard Hastad requires identical plaintext
# With linear padding: each ciphertext encrypts a_i*m + b_i
# Use CRT + Coppersmith's small_roots on the resulting polynomial

from sage.all import *
# Combine via CRT
N = prod(n_values)
T = [crt_coefficient(i, n_values) for i in range(e)]

P = PolynomialRing(Zmod(N), 'x')
x = P.gen()
poly = sum(T[i] * ((a[i]*x + b[i])**e - c[i]) for i in range(e))
poly = poly.monic()

# Coppersmith's method finds small root
roots = poly.small_roots(epsilon=1/30)
flag = int(roots[0])
```

**Key insight:** When the same message is encrypted with `e` different moduli but each applies a known affine transform `a_i * m + b_i`, CRT combines the congruences into a single polynomial of degree `e` over `Z/NZ`. Coppersmith's method recovers `m` as a small root, generalizing Hastad's attack beyond identical plaintexts.

**References:** PlaidCTF 2017

---

## RSA with Consecutive Primes (Fermat Factorization)

**Pattern (Loopy Primes):** q = next_prime(p), making p ~ q ~ sqrt(N). Also known as Fermat factorization — works whenever `|p - q|` is small.

**Factorization:** Find first prime below sqrt(N):
```python
from sympy import nextprime, prevprime, isqrt

root = isqrt(n)
p = prevprime(root + 1)
while n % p != 0:
    p = prevprime(p)
q = n // p
```

**Multi-layer variant:** 1024 nested RSA encryptions, each with consecutive primes of increasing bit size. Decrypt in reverse order.

---

## Multi-Prime RSA

When N is product of many small primes (not just p*q):
```python
# Factor N (easier when many primes)
from sympy import factorint
factors = factorint(n)  # Returns {p1: e1, p2: e2, ...}

# Compute phi using all factors
phi = 1
for p, e in factors.items():
    phi *= (p - 1) * (p ** (e - 1))

d = pow(e, -1, phi)
plaintext = pow(ciphertext, d, n)
```

---

## RSA with Restricted-Digit Primes (LACTF 2026)

**Pattern (six-seven):** RSA primes p, q composed only of digits {6, 7}, ending in 7.

**Digit-by-digit factoring from LSB:**
```python
# At each step k, we know p mod 10^k -> compute q mod 10^k = n * p^{-1} mod 10^k
# Prune: only keep candidates where digit k of both p and q is in {6, 7}
candidates = [(6,), (7,)]  # p ends in 6 or 7
for k in range(1, num_digits):
    new_candidates = []
    for p_digits in candidates:
        for d in [6, 7]:
            p_val = sum(p_digits[i] * 10**i for i in range(len(p_digits))) + d * 10**k
            q_val = (n * pow(p_val, -1, 10**(k+1))) % 10**(k+1)
            q_digit_k = (q_val // 10**k) % 10
            if q_digit_k in {6, 7}:
                new_candidates.append(p_digits + (d,))
    candidates = new_candidates
```

**General lesson:** When prime digits are restricted to a small set, digit-by-digit recovery from LSB with modular arithmetic prunes exponentially. Works for any restricted character set.

---

## Coppersmith for Structured RSA Primes (LACTF 2026)

**Pattern (six-seven-again):** p = base + 10^k * x where base is fully known and x is small (x < N^0.25).

**Attack via SageMath:**
```python
# Construct f(x) such that f(x_secret) = 0 (mod p) and thus (mod N)
# p = base + 10^k * x -> x + base * (10^k)^{-1} = 0 (mod p)
R.<x> = PolynomialRing(Zmod(N))
f = x + (base * inverse_mod(10**k, N)) % N
roots = f.small_roots(X=2**70, beta=0.5)  # x < N^0.25
```

**When to use:** Whenever part of a prime is known and the unknown part is small enough for Coppersmith bounds (< N^{1/e} for degree-e polynomial, approximately N^0.25 for linear).

---

## Manger's RSA Padding Oracle Attack (Nullcon 2026)

**Pattern (TLS, Nullcon 2026):** RSA-encrypted key with threshold oracle. Phase 1: double f until `k*f >= threshold`. Phase 2: binary search. ~128 total queries for 64-bit key.

See [advanced-math.md](advanced-math.md) for full implementation.

---

## Manger's Attack on RSA-OAEP via Timing Oracle (HTB Early Bird)

**Pattern:** Flask app implements RSA-OAEP with custom hash (PBKDF2, 2M iterations). Python's short-circuit `or` evaluation creates a timing oracle: if the first byte Y != 0, PBKDF2 is never called (~0.6s). If Y == 0, PBKDF2 runs (~2s).

**Vulnerable code pattern:**
```python
if Y != 0 or not self.H_verify(self.L, DB[:self.hLen]) or self.os2ip(PS) != 0:
    return {"ok": False, "error": "decryption error"}
```

**Oracle mapping:** Fast response → Y != 0 (decrypted message >= B). Slow response → Y == 0 (decrypted message < B = 2^(8*(k-1))).

**Calibration for network reliability:**
```python
def calibrate(n, e, k):
    B = pow(2, 8 * (k - 1))
    slow_times, fast_times = [], []
    for i in range(5):
        # Known-slow: encrypt values < B
        enc = pow(B - 1 - i*100, e, n).to_bytes(k, 'big')
        slow_times.append(measure(enc))
        # Known-fast: encrypt values > B
        enc = pow(B + 1 + i*100, e, n).to_bytes(k, 'big')
        fast_times.append(measure(enc))
    FAST_UPPER = max(fast_times) * 1.5
    SLOW_LOWER = min(slow_times) * 0.9
```

**Oracle with retry for ambiguous results:**
```python
def padding_oracle(c_int):
    while True:
        total = measure_response_time(c_int)
        if SLOW_LOWER < total < SLOW_UPPER:
            return True   # Y == 0 (below B)
        elif total < FAST_UPPER:
            return False  # Y != 0 (above B)
        # Ambiguous: retry
```

**Full 3-step Manger's attack (~1024 iterations for 1024-bit RSA):**
```python
# Step 1: Find f1 where f1 * m >= B
f1 = 2
while oracle((pow(f1, e, n) * c) % n):
    f1 *= 2

# Step 2: Find f2 where n <= f2 * m < n + B
f2 = (n + B) // B * f1 // 2
while not oracle((pow(f2, e, n) * c) % n):
    f2 += f1 // 2

# Step 3: Binary search narrowing m to exact value
mmin, mmax = ceil_div(n, f2), floor_div(n + B, f2)
while mmin < mmax:
    f = floor_div(2 * B, mmax - mmin)
    i = floor_div(f * mmin, n)
    f3 = ceil_div(i * n, mmin)
    if oracle((pow(f3, e, n) * c) % n):
        mmax = floor_div(i * n + B, f3)
    else:
        mmin = ceil_div(i * n + B, f3)
m = mmin
```

**Post-recovery OAEP decode:**
```python
from Crypto.Signature.pss import MGF1
maskedSeed = EM[1:hLen+1]
maskedDB = EM[hLen+1:]
seed = bytes(a ^ b for a, b in zip(maskedSeed, MGF1(maskedDB, hLen, HF)))
DB = bytes(a ^ b for a, b in zip(maskedDB, MGF1(seed, k - hLen - 1, HF)))
# DB[:hLen] should match lHash; rest is 0x00...0x01 || message
```

**Key insight:** Python's `or` short-circuits left-to-right. When expensive operations (PBKDF2, bcrypt, argon2) appear in chained conditions, the first condition becomes a timing oracle. RFC 8017 explicitly warns implementations must not let attackers distinguish error conditions — timing differences violate this.

**Detection:** RSA-OAEP with custom hash or slow KDF. Flask/Python backend. `/verify-token` or similar decryption endpoint returning generic errors. Timing differences between responses.

---

## Polynomial Hash with Trivial Root (Pragyan 2026)

**Pattern (!!Cand1esaNdCrypt0!!):** RSA signature scheme using polynomial hash `g(x,a,b) = x(x^2 + ax + b) mod P`.

**Vulnerability:** `g(0) = 0` for all parameters `a,b`. RSA signature of 0 is always 0 (`0^d mod n = 0`).

**Exploitation:** Craft message suffix so `bytes_to_long(prefix || suffix) = 0 (mod P)`:
```python
P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF61  # 128-bit prime
# Compute required suffix value mod P
req = (-prefix_val * pow(256, suffix_len, P)) % P
# Brute-force partial bytes until all printable ASCII
while True:
    high = os.urandom(32).translate(printable_table)
    low_val = (req - int.from_bytes(high, 'big') * shift) % P
    low = low_val.to_bytes(16, 'big')
    if all(32 <= b <= 126 for b in low):
        suffix = high + low
        break
# Signature is simply 0
```

**General lesson:** Always check if hash function has trivial inputs (0, 1, -1). Factoring the polynomial often reveals these.

---

## Polynomial CRT in GF(2)[x] (Nullcon 2026)

**Pattern (Going in Circles, Nullcon 2026):** `r = flag mod f` where f is random GF(2) polynomial. Collect ~20 pairs, filter coprime, CRT combine.

See [advanced-math.md](advanced-math.md) for GF(2)[x] polynomial arithmetic and CRT implementation.

---

## Affine Cipher over Non-Prime Modulus (Nullcon 2026)

**Pattern (Matrixfun, Nullcon 2026):** `c = A @ p + b (mod m)` with composite m. Chosen-plaintext difference attack. For composite modulus, solve via CRT in each prime factor field separately.

See [advanced-math.md](advanced-math.md) for CRT approach and Gauss-Jordan implementation.

See also: [rsa-attacks-2.md](rsa-attacks-2.md) for specialized RSA techniques (p=q bypass, cube root CRT, phi(n) multiple factoring, signature forgery, weak keygen, batch GCD, partial key recovery, CRT fault attack, homomorphic bypass).


# stream-ciphers

# CTF Crypto - Stream Cipher Attacks

LFSR, RC4, and XOR-based stream cipher attacks. For block cipher attacks (AES, padding oracle, MAC forgery), see [modern-ciphers.md](modern-ciphers.md).

## Table of Contents
- [LFSR Stream Cipher Attacks](#lfsr-stream-cipher-attacks)
  - [Berlekamp-Massey Algorithm](#berlekamp-massey-algorithm)
  - [Correlation Attack](#correlation-attack)
  - [Known-Plaintext on LFSR Keystream](#known-plaintext-on-lfsr-keystream)
  - [Galois vs Fibonacci LFSR](#galois-vs-fibonacci-lfsr)
  - [Common LFSR Lengths and Polynomials](#common-lfsr-lengths-and-polynomials)
  - [Galois LFSR Tap Recovery via Autocorrelation (BSidesSF 2026)](#galois-lfsr-tap-recovery-via-autocorrelation-bsidessf-2026)
- [RC4 Second-Byte Bias Distinguisher (Hackover CTF 2015)](#rc4-second-byte-bias-distinguisher-hackover-ctf-2015)
- [XOR Consecutive Byte Correlation Attack (Defcamp 2015)](#xor-consecutive-byte-correlation-attack-defcamp-2015)
- [Fibonacci Stream Cipher Position-Shifting Oracle (EKOPARTY 2017)](#fibonacci-stream-cipher-position-shifting-oracle-ekoparty-2017)
- [Z3 Constraint Solving for Custom Stream Ciphers (Tokyo Westerns 2017)](#z3-constraint-solving-for-custom-stream-ciphers-tokyo-westerns-2017)

---

## LFSR Stream Cipher Attacks

Linear Feedback Shift Registers generate keystreams from an initial state and feedback polynomial. Common in CTF crypto challenges and lightweight/custom ciphers.

**Detection:** Look for bit-level operations (XOR, shift, AND with tap mask), short repeating keystreams, or challenge descriptions mentioning "stream cipher", "LFSR", "shift register", or "linear recurrence".

### Berlekamp-Massey Algorithm

**Pattern:** Given a portion of known keystream (from known plaintext XOR), recover the minimal LFSR that generates it. Once you have the feedback polynomial and state, predict all future (and past) output.

**Key insight:** Berlekamp-Massey finds the shortest LFSR producing a given sequence in O(n^2). If you have 2L consecutive keystream bits (where L is the LFSR length), you can fully recover the LFSR.

```python
from sage.all import *

# Known keystream bits (from known plaintext XOR ciphertext)
keystream = [1, 0, 1, 1, 0, 0, 1, 0, 1, 1, 1, 0, 0, 1]

# Berlekamp-Massey in SageMath
F = GF(2)
seq = [F(b) for b in keystream]
R = berlekamp_massey(seq)  # Returns the feedback polynomial
print(f"LFSR polynomial: {R}")
print(f"LFSR length: {R.degree()}")

# Recover initial state from first L bits
L = R.degree()
state = keystream[:L]

# Generate future keystream
def lfsr_next(state, taps):
    """taps = list of tap positions from polynomial"""
    new_bit = 0
    for t in taps:
        new_bit ^= state[t]
    return state[1:] + [new_bit]
```

### Correlation Attack

**Pattern:** Combined LFSR generator (multiple LFSRs combined through a nonlinear function). If the combining function has correlation bias toward one LFSR's output, attack that LFSR independently.

**Key insight:** If `P(output = LFSR_i output) > 0.5`, brute-force LFSR_i's initial state (2^L candidates for length-L LFSR) and check correlation with known keystream. Much faster than brute-forcing the full combined state.

```python
# Correlation attack on a single biased LFSR
def correlation_attack(keystream_bits, lfsr_length, taps, threshold=0.6):
    """Try all 2^L initial states, keep those with high correlation"""
    best_corr, best_state = 0, None
    for seed in range(2**lfsr_length):
        state = [(seed >> i) & 1 for i in range(lfsr_length)]
        matches = 0
        s = state[:]
        for i, bit in enumerate(keystream_bits):
            if s[0] == bit:
                matches += 1
            s = lfsr_next(s, taps)
        corr = matches / len(keystream_bits)
        if corr > best_corr:
            best_corr, best_state = corr, seed
    return best_state, best_corr
```

### Known-Plaintext on LFSR Keystream

**Pattern:** XOR known plaintext with ciphertext to get keystream. With >=2L keystream bits, solve the linear system directly.

```python
import numpy as np

# Given 2L keystream bits, solve for L-bit state + L feedback taps
# Keystream relation: k[i+L] = c[0]*k[i] + c[1]*k[i+1] + ... + c[L-1]*k[i+L-1] (mod 2)
def solve_lfsr(keystream, L):
    """Solve for LFSR feedback from 2L keystream bits over GF(2)"""
    # Build matrix: each row is [k[i], k[i+1], ..., k[i+L-1]] = k[i+L]
    A = []
    b = []
    for i in range(L):
        A.append(keystream[i:i+L])
        b.append(keystream[i+L])
    # Solve over GF(2) using SageMath
    from sage.all import matrix, vector, GF
    M = matrix(GF(2), A)
    v = vector(GF(2), b)
    coeffs = M.solve_right(v)
    return list(coeffs)
```

### Galois vs Fibonacci LFSR

Two equivalent representations — same keystream, different wiring:
- **Fibonacci:** feedback from multiple taps XOR'd into last position (most common in CTFs)
- **Galois:** feedback distributed across the register (faster in hardware)

Conversion: Galois polynomial is the reciprocal of Fibonacci polynomial. Most CTF tools assume Fibonacci form.

### Common LFSR Lengths and Polynomials

| Bits | Common primitive polynomial | Period |
|------|---------------------------|--------|
| 16 | x^16 + x^14 + x^13 + x^11 + 1 | 65535 |
| 32 | x^32 + x^22 + x^2 + x + 1 | 2^32 - 1 |
| 64 | x^64 + x^4 + x^3 + x + 1 | 2^64 - 1 |

**Maximal-length LFSR:** Primitive polynomial -> period = 2^L - 1 (visits all nonzero states).

### Galois LFSR Tap Recovery via Autocorrelation (BSidesSF 2026)

**Pattern (lfstream):** A PNG file is encrypted by XORing each N-bit block with the current state of a Galois LFSR (right-shift model). The LFSR length, seed, and tap mask are unknown. Recover all three from the known 16-byte PNG header.

**Step 1 — Recover keystream via known plaintext:**

```bash
# PNG header is always: 89 50 4e 47 0d 0a 1a 0a 00 00 00 0d 49 48 44 52
# XOR first 16 encrypted bytes with this header to get 128 keystream bits
```

**Step 2 — Find LFSR length via autocorrelation sliding:**

Slide the 128-bit keystream against itself at increasing offsets. The offset where most bits align reveals the LFSR period. For a right-shift Galois LFSR, the keystream repeats with a one-bit shift per step, so the autocorrelation peak occurs at offset = LFSR length + 1.

```python
def find_lfsr_length(bits, min_len=8, max_len=64, step=8):
    """Slide keystream bits against themselves to find LFSR period."""
    best = None
    for n in range(min_len, max_len + 1, step):
        # Split keystream into n-bit state windows
        states = [int(bits[i*n:(i+1)*n], 2) for i in range(len(bits) // n)]
        if len(states) < 2:
            continue

        # For each transition, check Galois right-shift consistency
        mask_votes = {}
        mismatches = 0
        for i in range(len(states) - 1):
            s, nxt = states[i], states[i + 1]
            base = s >> 1  # Right-shift without feedback
            if s & 1:      # LSB was 1 → feedback applied
                derived_mask = base ^ nxt
                mask_votes[derived_mask] = mask_votes.get(derived_mask, 0) + 1
            else:           # LSB was 0 → no feedback, next = base
                if nxt != base:
                    mismatches += 1

        if mask_votes:
            best_mask, support = max(mask_votes.items(), key=lambda kv: kv[1])
            if mismatches == 0:
                print(f"Length {n}: tap_mask=0x{best_mask:0{n//4}x}, "
                      f"support={support}, mismatches=0 ← MATCH")
```

**Step 3 — Decrypt with recovered parameters:**

```python
def galois_lfsr_step(state, tap_mask, bits):
    """Single step of right-shift Galois LFSR."""
    out = state & 1
    state >>= 1
    if out:
        state ^= tap_mask
    return state & ((1 << bits) - 1)

# Seed = first keystream block (LFSR state before first step)
seed = int(keystream_bits[:lfsr_bits], 2)
state = seed

with open("flag.png.enc_lfsr", "rb") as f_in, open("flag.png", "wb") as f_out:
    block_size = lfsr_bits // 8
    while True:
        chunk = f_in.read(block_size)
        if not chunk:
            break
        key = state.to_bytes(block_size, "big")
        f_out.write(bytes(b ^ k for b, k in zip(chunk, key)))
        state = galois_lfsr_step(state, tap_mask, lfsr_bits)
```

**Key insight:** For a Galois right-shift LFSR (`state >>= 1; if lsb: state ^= tap_mask`), the tap mask is directly computable from any two consecutive states where the outgoing LSB is 1: `tap_mask = (state >> 1) XOR next_state`. This is more direct than Berlekamp-Massey (which assumes Fibonacci form) and requires no algebraic libraries. The autocorrelation approach to find the LFSR length works because correct-length windows produce consistent tap masks with zero mismatches, while incorrect lengths produce contradictory masks.

**When to recognize:** Challenge encrypts a file with known headers (PNG, PDF, ZIP, ELF) using XOR with an unknown "stream cipher" or "PRNG". Filename or description mentions "LFSR", "shift register", or "stream". The encrypted file preserves the original length (no padding), indicating a stream cipher. Try Galois tap recovery first — it's faster and simpler than Berlekamp-Massey for right-shift implementations.

**Known file headers for keystream recovery:**

| Format | Header bytes | Usable bits |
|--------|-------------|-------------|
| PNG | `89 50 4e 47 0d 0a 1a 0a 00 00 00 0d 49 48 44 52` | 128 |
| PDF | `25 50 44 46 2d` ("%PDF-") | 40 |
| ZIP | `50 4b 03 04` | 32 |
| ELF | `7f 45 4c 46` | 32 |
| JFIF | `ff d8 ff e0` | 32 |

---

## RC4 Second-Byte Bias Distinguisher (Hackover CTF 2015)

**Pattern:** Distinguish RC4 output from true random data by exploiting RC4's second-byte bias. The second output byte of RC4 is biased toward `0x00` with probability 1/128 (vs expected 1/256).

```python
count_zero = 0
for sample in all_samples:
    if sample[1] == 0x00:  # second byte
        count_zero += 1

# Expected: random = N/256, RC4 = N/128 (2x more zeros)
if count_zero > threshold:
    print("RC4")
else:
    print("Random")
```

**Key insight:** RC4's key scheduling creates a well-known bias where `P(second_byte == 0) = 1/128` instead of `1/256`. With ~2048 samples, RC4 produces ~16 zero second-bytes vs ~8 for random. Other RC4 biases: bytes 3-255 show weaker biases; long-term biases exist at every 256th position.

---

## XOR Consecutive Byte Correlation Attack (Defcamp 2015)

When a cipher XORs consecutive ciphertext bytes, the relationship between two ciphertexts reveals plaintext differences without knowing the key:

```python
# Observation: xorct[i] = ct[i] ^ ct[i+1]
# For two ciphertext/plaintext pairs:
# plain2[i] ^ plain1[i] == xorct1[i] ^ xorct2[i]

# With one known plaintext, decrypt the other:
for i in range(len(ct2)):
    xorct1 = ct1[i] ^ ct1[i+1]
    xorct2 = ct2[i] ^ ct2[i+1]
    plain2_char = xorct1 ^ xorct2 ^ plain1[i]
```

**Key insight:** XOR of consecutive bytes cancels key material, leaving only plaintext-dependent differences. One known plaintext breaks all subsequent messages.

---

## Fibonacci Stream Cipher Position-Shifting Oracle (EKOPARTY 2017)

**Pattern:** Custom cipher encrypts byte at position `k` as `Fib(seed + k) + plaintext_byte`. The seed is encoded in the first byte of each query. Incrementing the first byte by N shifts the Fibonacci starting position by 1, turning the server into an oracle: given any 2-byte query, the server returns the Fibonacci value at an arbitrary position XOR'd with the corresponding plaintext byte.

**Attack (flag recovery via oracle):**
1. Send queries of the form `[seed_offset][target_byte_position]` to request specific positions in the target ciphertext
2. For each position, try all 256 candidate plaintext values: `candidate_byte + Fib(adjusted_seed + pos)` should match the observed server output
3. Compare against the known target ciphertext byte to identify the correct plaintext

```python
# Oracle: server returns Fib(seed + k) XOR plaintext[k]
# Shift seed by 1 per byte offset increment
for pos in range(flag_length):
    for candidate in range(256):
        # Query with adjusted seed to reach this position
        oracle_output = query(seed_offset=pos, position=0)
        fib_val = oracle_output ^ candidate
        if matches_target_ciphertext(fib_val, pos):
            flag_bytes.append(candidate)
            break
```

**Key insight:** When keystream depends on position in a predictable mathematical way and the starting position is controllable, the server becomes a decryption oracle. Complexity is O(n * 256) queries where n is the flag length — linear in the target size.

**References:** EKOPARTY CTF 2017

---

## Z3 Constraint Solving for Custom Stream Ciphers (Tokyo Westerns 2017)

**Pattern:** Custom stream cipher with algebraic mixing: `encrypted[i] = (message[i] + key[i%13] + encrypted[i-1]) % 128`. Known plaintext prefix (e.g., `TWCTF{`) anchors the first several constraints. Z3 solver encodes each step as an integer constraint and directly recovers both the unknown key and the remaining flag characters.

```python
from z3 import *

key_len = 13
flag_len = len(encrypted)

key = [Int(f'k{i}') for i in range(key_len)]
flag = [Int(f'f{i}') for i in range(flag_len)]

s = Solver()

# Cipher recurrence: enc[i] = (flag[i] + key[i%13] + enc[i-1]) % 128
for i in range(flag_len):
    prev = encrypted[i-1] if i > 0 else 0
    s.add(encrypted[i] == (flag[i] + key[i % key_len] + prev) % 128)

# Key and flag must be printable ASCII
for k in key:
    s.add(k >= 32, k <= 126)
for f in flag:
    s.add(f >= 32, f <= 126)

# Anchor with known plaintext prefix
for i, c in enumerate(b'TWCTF{'):
    s.add(flag[i] == c)

if s.check() == sat:
    m = s.model()
    recovered = bytes([m[flag[i]].as_long() for i in range(flag_len)])
    print(recovered)
```

**Key insight:** Stream ciphers with algebraic (addition-based) mixing are directly amenable to Z3 constraint solving. Encode each step as an integer constraint, add known-plaintext anchors for the flag prefix, and let the solver recover key and remaining plaintext simultaneously. This avoids any manual analysis of the cipher structure.

**References:** Tokyo Westerns CTF 2017


# zkp-and-advanced

# CTF Crypto - ZKP, Solvers & Advanced Techniques

## Table of Contents
- [ZKP Attacks](#zkp-attacks)
- [Graph 3-Coloring](#graph-3-coloring)
- [Z3 SMT Solver Guide](#z3-smt-solver-guide)
- [Garbled Circuits: Free XOR Delta Recovery (LACTF 2026)](#garbled-circuits-free-xor-delta-recovery-lactf-2026)
- [Bigram/Trigram Substitution -> Constraint Solving (LACTF 2026)](#bigramtrigram-substitution---constraint-solving-lactf-2026)
- [Shamir Secret Sharing with Deterministic Coefficients (LACTF 2026)](#shamir-secret-sharing-with-deterministic-coefficients-lactf-2026)
- [Race Condition in Crypto-Protected Endpoints (LACTF 2026)](#race-condition-in-crypto-protected-endpoints-lactf-2026)
- [Garbled Circuits: AES Key Recovery via Metadata Leakage (srdnlenCTF 2026)](#garbled-circuits-aes-key-recovery-via-metadata-leakage-srdnlenctf-2026)
- [Post-Quantum Signature Fault Injection: MAYO (srdnlenCTF 2026)](#post-quantum-signature-fault-injection-mayo-srdnlenctf-2026)
- [Lattice-Based Threshold Signature Attack: FROST (srdnlenCTF 2026)](#lattice-based-threshold-signature-attack-frost-srdnlenctf-2026)
- [Groth16 Broken Trusted Setup — delta == gamma (DiceCTF 2026)](#groth16-broken-trusted-setup--delta--gamma-dicectf-2026)
- [Groth16 Proof Replay — Unconstrained Nullifier (DiceCTF 2026)](#groth16-proof-replay--unconstrained-nullifier-dicectf-2026)
- [DV-SNARG Forgery via Verifier Oracle (DiceCTF 2026)](#dv-snarg-forgery-via-verifier-oracle-dicectf-2026)
- [KZG Pairing Oracle for Permutation Recovery (UNbreakable 2026)](#kzg-pairing-oracle-for-permutation-recovery-unbreakable-2026)
- [Shamir Secret Sharing with Reused Polynomial Coefficients (PoliCTF 2017)](#shamir-secret-sharing-with-reused-polynomial-coefficients-polictf-2017)

---

## ZKP Attacks

- Look for information leakage in proofs
- If proving IMPOSSIBLE problem (e.g., 3-coloring K4), you must cheat
- Find hash collisions to commit to one value but reveal another
- PRNG state recovery: salts generated from seeded PRNG can be predicted
- Small domain brute force: if you know `commit(i) = sha256(salt(i), color(i))` and have salt, brute all colors

---

## Graph 3-Coloring

```python
import networkx as nx
nx.coloring.greedy_color(G, strategy='saturation_largest_first')
```

---

## Z3 SMT Solver Guide

Z3 solves constraint satisfaction - useful when crypto reduces to finding values satisfying conditions.

**Basic usage:**
```python
from z3 import *

# Boolean variables (for bit-level problems)
bits = [Bool(f'b{i}') for i in range(64)]

# Integer/bitvector variables
x = BitVec('x', 32)  # 32-bit bitvector
y = Int('y')         # arbitrary precision int

solver = Solver()
solver.add(x ^ 0xdeadbeef == 0x12345678)
solver.add(y > 100, y < 200)

if solver.check() == sat:
    model = solver.model()
    print(model.eval(x))
```

**BPF/SECCOMP filter solving:**

When challenges use BPF bytecode for flag validation (e.g., custom syscall handlers):

```python
from z3 import *

# Model flag as array of 4-byte chunks (how BPF sees it)
flag = [BitVec(f'f{i}', 32) for i in range(14)]
s = Solver()

# Constraint: printable ASCII
for f in flag:
    for byte in range(4):
        b = (f >> (byte * 8)) & 0xff
        s.add(b >= 0x20, b < 0x7f)

# Extract constraints from BPF dump (seccomp-tools dump ./binary)
mem = [BitVec(f'm{i}', 32) for i in range(16)]

# Example BPF constraint reconstruction
s.add(mem[0] == flag[0])
s.add(mem[1] == mem[0] ^ flag[1])
s.add(mem[4] == mem[0] + mem[1] + mem[2] + mem[3])
s.add(mem[8] == 4127179254)  # From BPF if statement

if s.check() == sat:
    m = s.model()
    flag_bytes = b''
    for f in flag:
        val = m[f].as_long()
        flag_bytes += val.to_bytes(4, 'little')
    print(flag_bytes.decode())
```

**Converting bits to flag:**
```python
from Crypto.Util.number import long_to_bytes

if solver.check() == sat:
    model = solver.model()
    flag_bits = ''.join('1' if model.eval(b) else '0' for b in bits)
    print(long_to_bytes(int(flag_bits, 2)))
```

**When to use Z3:**
- Type system constraints (OCaml GADTs, Haskell types)
- Custom hash/cipher with algebraic structure
- Equation systems over finite fields
- Boolean satisfiability encoded in challenge
- Constraint propagation puzzles

---

## Garbled Circuits: Free XOR Delta Recovery (LACTF 2026)

**Pattern (sisyphus):** Yao's garbled circuit with free XOR optimization. Circuit designed so normal evaluation only reaches one wire label, but the other is needed.

**Free XOR property:** Wire labels satisfy `W_0 XOR W_1 = delta` for global secret delta.

**Attack:** XOR three of four encrypted truth table entries to cancel AES terms:
```python
# Encrypted rows: E_i = AES(key_a_i XOR key_b_i, G_out_f(a,b))
# XOR of three rows where AES inputs differ by delta causes cancellation
# Reveals delta directly, then compute: W_1 = W_0 XOR delta
```

**General lesson:** In garbled circuits, if you can obtain any two labels for the same wire, you recover delta and can compute all labels.

---

## Bigram/Trigram Substitution -> Constraint Solving (LACTF 2026)

**Pattern (lazy-bigrams):** Bigram substitution cipher where plaintext has known structure (NATO phonetic alphabet).

**OR-Tools CP-SAT approach:**
1. Model substitution as injective mapping (IntVar per bigram)
2. Add crib constraints from known flag prefix
3. Add **regular language constraint** (automaton) for valid NATO word sequences
4. Solver finds unique solution

**Pattern (not-so-lazy-trigrams):** "Trigram substitution" that decomposes into three independent monoalphabetic ciphers on positions mod 3.

**Decomposition insight:** If cipher uses `shuffle[pos % n][char]`, each residue class `pos = k (mod n)` is an independent monoalphabetic substitution. Solve each separately with frequency analysis or known-plaintext.

---

## Shamir Secret Sharing with Deterministic Coefficients (LACTF 2026)

**Pattern (spreading-secrets):** Coefficients `a_1...a_9` are deterministic functions of secret s (via RNG seeded with s). One share (x_0, y_0) is revealed.

**Vulnerability:** Given one share, the equation `y_0 = s + g(s)*x_0 + g^2(s)*x_0^2 + ... + g^9(s)*x_0^9` is **univariate** in s.

**Root-finding via Frobenius:**
```python
# In GF(p), find roots of h(s) via gcd with x^p - x
# h(s) = s + g(s)*x_0 + ... + g^9(s)*x_0^9 - y_0
# Compute x^p mod h(x) via binary exponentiation with polynomial reduction
# gcd(x^p - x, h(x)) = product of (x - root_i) for all roots
R.<x> = PolynomialRing(GF(p))
h = construct_polynomial(x0, y0)
xp = pow(x, p, h)  # Fast modular exponentiation
g = gcd(xp - x, h)  # Extract linear factors
roots = [-g[0]/g[1]] if g.degree() == 1 else g.roots()
```

**General lesson:** If ALL Shamir coefficients are derived from the secret, a single share creates a univariate equation. This completely breaks the (k,n) threshold scheme.

---

## Race Condition in Crypto-Protected Endpoints (LACTF 2026)

**Pattern (misdirection):** Endpoint has TOCTOU vulnerability: `if counter < 4` check happens before increment, allowing concurrent requests to all pass the check.

**Exploitation:**
1. **Cache-bust signatures:** Modify each request slightly (e.g., prepend zeros to nonce) so server can't use cached verification results
2. **Synchronize requests:** Use multiprocessing with barrier to send ~80 simultaneous requests
3. All pass `counter < 4` check before any increments -> counter jumps past limit

```python
from multiprocessing import Process, Barrier
barrier = Barrier(80)

def make_request(barrier, modified_sig):
    barrier.wait()  # Synchronize all processes
    requests.post(url, json={"sig": modified_sig})

# Launch 80 processes with unique signature modifications
processes = [Process(target=make_request, args=(barrier, modify_sig(i))) for i in range(80)]
```

**Key insight:** TOCTOU in `check-then-act` patterns. Look for read-modify-write without atomicity/locking.

---

## Garbled Circuits: AES Key Recovery via Metadata Leakage (srdnlenCTF 2026)

**Pattern (FHAES):** Service evaluates AES via garbled circuits with a fixed per-connection key. Exploit garbling metadata rather than AES cryptanalysis.

**Attack:**
1. Construct a custom circuit with one attacker-controlled AND gate that leaks the global Free-XOR offset delta
2. Use delta to locally evaluate the key-schedule section (first 1360 AND gates) as the evaluator
3. For each of the first 16 key-schedule S-box calls, brute-force the input byte by re-garbling the S-box chunk and comparing observed AND tables
4. Reconstruct key words from S-box outputs and recover the full 128-bit key through algebraic manipulation of the AES-128 schedule recurrence

```python
def garble_and(A, B, D, and_idx):
    """Reproduce garbling with proper parity handling."""
    r = B & 1
    alpha = A & 1
    beta = B & 1
    # Computes gate0, gate1, z output via hash-based approach
    return gate0, gate1, z

def evaluator_and(A, B, gate0, gate1, and_idx):
    """Evaluate AND gate using hash-based approach."""
    hashA = h_wire(A, and_idx)
    hashB = h_wire(B, and_idx)
    L = hashA if (A & 1) == 0 else (hashA ^ gate0)
    R = hashB if (B & 1) == 0 else (hashB ^ gate1)
    return L ^ R ^ (A * (B & 1))
```

**Key insight:** Garbled circuits that use free XOR optimization with fixed keys across sessions leak key material through the AND gate truth tables. Each S-box has a small enough input space (256 values) to brute-force when you know delta. This extends the LACTF technique from "recovering delta" to "recovering the entire AES key."

---

## Post-Quantum Signature Fault Injection: MAYO (srdnlenCTF 2026)

**Pattern (Faulty Mayo):** One-byte fault injection window in `mayo_sign_signature` before final `s = v + O*x` construction. Controlled bit flips across 64 signature queries recover the secret matrix O row by row.

**Attack:**
1. Reverse binary to map fault offsets to `mayo_sign_signature` instructions
2. For each of 64 rows of secret matrix O, use faulted signatures to extract linear equations over GF(16)
3. Solve 17-variable linear systems over GF(16) for each row using Gaussian elimination
4. Rebuild equivalent signer using recovered O and public seed from compressed public key
5. Forge valid signature for challenge message

**GF(16) Gaussian elimination:**
```python
# Precompute multiplication and inverse tables for GF(16)
# GF(16) = GF(2)[x] / (x^4 + x + 1), elements 0-15
INV = [0] * 16  # multiplicative inverses
MUL = [[0]*16 for _ in range(16)]  # multiplication table

def solve_linear_gf16(equations, nvars=17):
    """Gaussian elimination over GF(16)."""
    A = [x[:] + [y] for x, y in equations]
    m, row = len(A), 0
    for col in range(nvars):
        piv = next((r for r in range(row, m) if A[r][col] != 0), None)
        if piv is None: continue
        A[row], A[piv] = A[piv], A[row]
        invp = INV[A[row][col]]
        A[row] = [MUL[invp][v] for v in A[row]]
        for r in range(m):
            if r != row and A[r][col] != 0:
                f = A[r][col]
                A[r] = [A[r][c] ^ MUL[f][A[row][c]] for c in range(nvars + 1)]
        row += 1
    return [A[i][nvars] for i in range(nvars)]
```

**Key insight:** Post-quantum signature schemes like MAYO can be broken with fault injection if you can cause controlled bit flips during signing. Each fault creates a linear equation over GF(16), and 17+ equations per row suffice to recover the secret. This is analogous to DFA on classical schemes but over extension fields.

---

## Lattice-Based Threshold Signature Attack: FROST (srdnlenCTF 2026)

**Pattern (Threshold):** Preprocessing queue capacity allows collecting many signatures. Fixed challenge construction enables solving 1D noisy linear equations per coefficient.

**Attack:**
1. Exploit queue-depth cap (≤8 active) rather than total-usage cap by alternating menu options
2. Force fixed challenge `c` by choosing commitment `w₀` each query to zero aggregate commitment before high-bit extraction
3. With fixed `c`, each coefficient becomes: `z = λ·u + noise (mod q)`
4. Select multiple signer subsets to obtain different Lagrange coefficient scales (small/mid/huge) for each target signer
5. Solve via interval intersection and maximum-likelihood selection
6. Recover 7 signer shares; combine with own share; reconstruct master secret via Lagrange interpolation

**Interval intersection algorithm:**
```python
from math import ceil, floor

def intersect_intervals(intervals, lam, z, q, B):
    """Refine candidate intervals using one (λ, z) observation with noise bound B."""
    out = []
    for lo, hi in intervals:
        if lam > 0:
            kmin = ceil((lam * lo - z - B) / q)
            kmax = floor((lam * hi - z + B) / q)
            for k in range(kmin, kmax + 1):
                a = (z + q * k - B) / lam
                b = (z + q * k + B) / lam
                lo2, hi2 = max(lo, a), min(hi, b)
                if lo2 <= hi2:
                    out.append((lo2, hi2))
    # Merge overlapping intervals
    out.sort()
    merged = [out[0]] if out else []
    for lo, hi in out[1:]:
        if lo <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], hi))
        else:
            merged.append((lo, hi))
    return merged
```

**Key insight:** Threshold signature schemes can leak individual shares when the challenge value is controlled. By querying with different signer subsets, you get different Lagrange coefficient scales for the same unknown share, allowing iterative interval refinement. With enough observations, the interval converges to a unique value.

---

## Groth16 Broken Trusted Setup — delta == gamma (DiceCTF 2026)

**Pattern (Housing Crisis):** Groth16 verifier has `vk_delta_2 == vk_gamma_2`, which breaks soundness entirely. Proofs are trivially forgeable.

**Forgery:**
```python
from py_ecc.bn128 import G1, G2, multiply, add, neg, pairing
from py_ecc.bn128 import curve_order as q

# When delta == gamma, the pairing equation simplifies:
# e(A, B) = e(alpha, beta) * e(vk_x + C, gamma)
# Set A = vk_alpha1, B = vk_beta2, then:
# e(alpha, beta) * e(vk_x + C, gamma) = e(alpha, beta)
# → e(vk_x + C, gamma) = 1 → C = -vk_x (point negation)

forged_A = vk_alpha1   # alpha point from verification key
forged_B = vk_beta2    # beta point from verification key
forged_C = neg(vk_x)   # negate the public input accumulator

# This proof verifies for ANY public inputs
```

**Detection:** Compare `vk_delta_2` and `vk_gamma_2` in the verifier contract. If equal, the entire Groth16 scheme collapses — any statement can be "proven."

**When to check:** Always inspect Groth16 verification key constants before attempting complex attacks. A broken trusted setup makes everything else unnecessary.

---

## Groth16 Proof Replay — Unconstrained Nullifier (DiceCTF 2026)

**Pattern (Housing Crisis):** DAO governance never tracks used `proposalNullifierHash` values, and the circuit leaves the nullifier unconstrained. A valid proof from the setup transaction can be replayed infinitely.

**Attack:**
1. Find the DAO contract's deployment/setup transaction
2. Extract constructor arguments containing valid Groth16 proof
3. Replay the same proof for every proposal — it always verifies
4. Use proposals to control DAO actions (betting, market creation, resolution)

**Key insight:** ZK circuits that leave inputs unconstrained and systems that don't track nullifiers are vulnerable to replay. Always check: does the verifier contract track proof nullifiers? Does the circuit actually constrain all declared public inputs?

---

## DV-SNARG Forgery via Verifier Oracle (DiceCTF 2026)

**Pattern (Dot):** DV-SNARG (Designated Verifier Succinct Non-interactive ARGument) for an adder circuit. Must produce 20 valid proofs for **wrong** answers.

**Key insight:** DV-SNARGs explicitly lose soundness when the prover has oracle access to the verifier (ePrint 2024/1138). The verifier's secret randomness can be extracted through query patterns.

**DPP (Dot Product Proof) structure:**
```text
q[i] = v[i] + b*(tensor[i] - constraint[i])
where b = fixed constant (e.g., 162817)
      v[i] = random in [-256, 256]
      constraint weights r = random in [-2^40, 2^40]
```

**Forgery via CRS entry cancellation:**
For a wrong answer, only the output constraint (wire N) is violated. Find two CRS entries whose constraint contributions cancel:

1. Wire N is touched by gate G AND the output constraint
2. `pair(input1, input2)` of gate G is touched ONLY by gate G
3. Adding `CRS[wire_N]` and subtracting `CRS[pair]` to the wrong proof cancels `b*r_G` terms
4. The remaining deficit `b*r_output` also cancels
5. Adjust `delta = -v[N] + 2*b*v[input1]*v[input2]` via `delta*G` on h2

**Learning secret v values via oracle:**
```python
# At streak=0, submitting correct answer is "safe" — doesn't reset streak
# Use oracle to learn |v[i]| from unconstrained diagonal pairs:

for guess in range(257):  # v[i] in [-256, 256], |v[i]| in [0, 256]
    # Set pair(i,i) coefficient to guess^2
    # If guess == |v[i]|, specific oracle response differs
    response = oracle_query(guess)
    if response == "hit":
        abs_v_i = guess
        break

# Learn signs from off-diagonal unconstrained pairs (1 query each)
# Learn product sign: v[a]*v[b] sign from pair(a,b)
```

**Performance:** ~364 oracle queries for Phase 1 (~97s), ~300s for 20 forged proofs ≈ 400s total.

**Key insight:** When attacking DV-SNARGs with oracle access, the strategy is: (1) learn a small number of secret values from the verifier's randomness, (2) use algebraic cancellation between CRS entries to forge proofs. Unconstrained pair indices expose pure tensor products of the secret vector.

---

## KZG Pairing Oracle for Permutation Recovery (UNbreakable 2026)

**Pattern (toxicwaste):** KZG commitment scheme publishes shuffled points `{alpha^i * G1}` for i=0..n. The shuffle hides which point corresponds to which exponent. Recover the exponent ordering using bilinear pairings as an oracle, then extract the toxic waste `alpha`.

**Distortion map technique:** On supersingular pairing-friendly curves, a distortion map `psi((x,y)) = (zeta*x, y)` (where `zeta^3 = 1`) enables additive exponent comparisons:

```python
from sage.all import *

# For points P_i = alpha^a_i * G1 and P_j = alpha^a_j * G1:
# e(P_i, psi(P_j)) = e(G1, psi(G1))^(alpha^(a_i + a_j))
# If e(P_i, psi(P_j)) == e(P_k, psi(G1)), then a_i + a_j == a_k

# Step 1: Identify G1 (alpha^0) — the only point where e(P, psi(P)) == e(G1, psi(G1))
g1 = None
base_pairing = None
for P in shuffled_points:
    val = P.weil_pairing(psi(P), order)
    if base_pairing is None:
        base_pairing = val
        g1 = P
    elif val == base_pairing:
        g1 = P
        break

# Step 2: Walk the chain — find alpha*G1 via e(P_?, psi(G1)) comparisons
# Then alpha^2*G1 via e(alpha*G1, psi(alpha*G1)) == e(alpha^2*G1, psi(G1))
# Continue until full ordering recovered

# Step 3: With ordered points, solve A(x) = 0 over GF(q) to get alpha
# Step 4: Forge KZG opening proofs using recovered alpha
```

**Key insight:** Bilinear pairings reveal additive relationships between exponents without solving discrete log. The pairing `e(P_i, psi(P_j))` depends on `alpha^(a_i + a_j)`, so comparing against known pairing values identifies which shuffled point has which exponent. This turns a cryptographic shuffle into a solvable ordering problem.

---

## Shamir Secret Sharing with Reused Polynomial Coefficients (PoliCTF 2017)

**Pattern:** When a Shamir SSS implementation reuses the same random polynomial coefficients for every character of the secret, share subtraction cancels the higher-order terms.

```python
# Standard Shamir: y_i = f_i + a1*x + a2*x^2 + ... (different a_j per character)
# Broken: y_i = f_i + a1*x + a2*x^2 + ... (SAME a_j for all characters)
# Since higher-order terms are identical:
# y_1[i] - y_1[0] = f[i] - f[0]  (for share x=1)
# If f[0] is known (e.g., 'f' from flag prefix):
flag = ''.join(chr(shares[i] - shares[0] + ord('f')) for i in range(len(shares)))
```

**Key insight:** In correct Shamir SSS, each secret byte uses independent random coefficients. When coefficients are reused, subtracting any two shares at the same evaluation point cancels all randomness, leaving only the difference between the corresponding secret bytes.

**References:** PoliCTF 2017

