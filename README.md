# framework-upgrade

Upgrade frameworks and runtimes with Claude Code from the official guides, one green step at a time.

A [Claude skill](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview) for Claude Code — Python 3 standard library only, no dependencies. Part of the [mkarami313/Claude-skill](https://github.com/mkarami313/Claude-skill) collection.

Claude's knowledge of breaking changes is frozen at training time, so upgrades go wrong the same ways: breaking changes guessed from memory, everything bumped at once, codemods skipped, warnings silenced and peer deps forced. `framework-upgrade` makes an upgrade **evidence-driven and incremental**.

**Use it when** you upgrade or migrate a framework, runtime or major dependency (React, Next.js, Angular, Vue, Node, TypeScript, .NET / EF Core, Django, Laravel, Rails, Spring Boot…), fix breakage after one, or want a plan first.

## How it works
| Step | What happens |
|---|---|
| Detect | `detect_versions.py` lists frameworks, runtimes, package managers, lockfiles and version drift across manifests (npm, NuGet, PyPI, Go, Composer, Gems, Maven/Gradle). |
| Baseline | Clean branch; build, tests, lint once; record exact pass/fail counts. |
| Research | Fetch the **official** guide for every major in between; grep each breaking change in your code (zero hits → dropped); check runtime and ecosystem compatibility; find official codemods. Plan goes to `UPGRADE.md`. |
| Execute | Tooling → codemods → bump with your package manager → fix compile → tests → deprecations; one commit per green step. |
| Verify | Compare with the baseline, count deprecations, run the app, update CI/Docker/runtime pins; QA list for changed defaults. |

Hard rules: no `--legacy-peer-deps`/`--force`, `skipLibCheck`, `@ts-ignore`, disabled warnings, skipped tests or old-version pins without your explicit yes.

## What's inside
```
skills/framework-upgrade/
├── SKILL.md                     scope, baseline, research, plan, execute, verify, report
├── scripts/
│   └── detect_versions.py       frameworks, runtimes, lockfiles, version drift
└── references/
    └── playbooks.md             where the official guides and codemods are, per ecosystem
```

## Installation

### Claude Code — plugin marketplace (recommended)
```
/plugin marketplace add mkarami313/claude-framework-upgrade
/plugin install framework-upgrade@claude-framework-upgrade
```
Update later with `/plugin marketplace update claude-framework-upgrade`.

### Claude Code — copy the skill folder
```bash
git clone https://github.com/mkarami313/claude-framework-upgrade
cp -r claude-framework-upgrade/skills/framework-upgrade <your-repo>/.claude/skills/     # this project only
cp -r claude-framework-upgrade/skills/framework-upgrade ~/.claude/skills/               # all your projects
```

### Claude.ai / Claude desktop app
Zip the folder so that `framework-upgrade/SKILL.md` is at the root of the archive and upload it in Claude's skills settings:
```bash
cd claude-framework-upgrade/skills && zip -r framework-upgrade.zip framework-upgrade
```

## Testing
`tests/framework-upgrade/scenarios.md` lists pressure scenarios. After changing the skill, walk through each one with the new `SKILL.md` (or give it to a fresh Claude session) and check the expected behaviour still follows.

## Contributing
Issues and PRs welcome. Keep `SKILL.md` lean (long material → `references/`, code → `scripts/`), scripts stdlib-only with LF endings, and add a scenario for every behaviour you change.

## License
[MIT](LICENSE)
