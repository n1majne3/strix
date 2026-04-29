# Strix Skills

Skills are specialized knowledge packages in standard `SKILL.md` format.

## Structure

Each skill is a directory containing a `SKILL.md` file:

```
strix/skills/
  xss/SKILL.md
  sql-injection/SKILL.md
  kubernetes/SKILL.md
```

## Format

```yaml
---
name: sql-injection
description: One-line description
category: vulnerabilities
essential: true          # optional; auto-loads at startup
---

# Skill Title

Content here...
```

**Frontmatter fields:**
- `name` — must match directory name, use hyphens
- `description` — one-line summary
- `category` — vulnerabilities, tooling, frameworks, cloud, technologies, protocols, ctf, scan-modes, coordination, custom
- `essential` — set `true` to auto-load at startup (omit for on-demand skills)

## Categories

| Category | Description |
|----------|-------------|
| vulnerabilities | SQL injection, XSS, SSRF, etc. |
| tooling | nmap, nuclei, ffuf, etc. |
| frameworks | FastAPI, Next.js, NestJS |
| cloud | Kubernetes, AWS, GCP |
| technologies | Supabase, Firebase |
| protocols | GraphQL |
| ctf | CTF challenge types |
| scan-modes | quick, standard, deep |
| coordination | Root agent orchestration |
| custom | User-contributed skills |

## Creating Skills

1. Create directory: `strix/skills/<name>/`
2. Add `SKILL.md` with frontmatter and content
3. Set `category` to the appropriate classification
4. Set `essential: true` only if the skill must load at startup

Skills are discovered automatically. No registration needed.
