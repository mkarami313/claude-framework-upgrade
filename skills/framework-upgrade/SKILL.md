---
name: framework-upgrade
description: Upgrade a framework, runtime or major dependency safely — React, Next.js, Angular, Vue, Node, TypeScript, .NET / ASP.NET Core / EF Core, Django, Laravel, Rails, Spring Boot and similar. Use when asked to upgrade, migrate or bump to a new major version, fix breakage after an upgrade, plan an upgrade, or check what an upgrade would take. Forces reading the official upgrade guide instead of guessing breaking changes from memory.
---

# Framework upgrade

Claude's knowledge of breaking changes is frozen at training time and often wrong about the newest versions. Upgrades also fail the same ways: everything bumped at once, codemods skipped, warnings silenced, peer deps forced. This skill makes the upgrade **evidence-driven and incremental**.

## 0. Scope (ask only what you can't detect)
- What, from → to, and why (security fix, EOL, a needed feature). Detect "from" yourself.
- Multiple majors (e.g. Angular 15 → 18): go **one major at a time** when the official guide says so (Angular, Django feature releases); otherwise read every intermediate guide anyway.
- One framework per branch. Unrelated dependency bumps go in a separate step or PR.

## 1. Detect
`python3 <skill-dir>/scripts/detect_versions.py [path]` → frameworks, runtimes, package managers, lockfiles, and version drift between manifests (`--all` for every dependency). Note the package manager — use it, never mix (`npm` in a `pnpm` repo rewrites the lockfile).

## 2. Baseline (before touching anything)
- Clean working tree; new branch `upgrade/<framework>-<to>`.
- Build, tests, lint, type-check once; save the exact pass/fail counts and failing test names. If it is already red, the baseline is the red list — don't fix it inside the upgrade unless asked.
- Long builds/tests: run them through the `task-observer` skill if available, so logs stay out of context.

## 3. Research — mandatory, never from memory
For **each** major between from and to:
1. Fetch the **official** upgrade/migration guide and release notes (WebFetch/WebSearch on the project's own domain or repo). Third-party blogs only to fill gaps, labelled as such.
2. From the guide, list every breaking change, removed/renamed API and changed default. For each, **grep the codebase** and record hit counts. Changes with zero hits are dropped from the plan.
3. Check runtime/tooling requirements (Node, .NET SDK, Python, Java, TypeScript, bundler versions).
4. Check ecosystem compatibility: the libraries that integrate with the framework (routers, UI kits, ORMs, test runners, auth libs, type packages). Look up their supported version range; list blockers.
5. Find the **official codemods / migration tools** and how the guide says to run them (see `references/playbooks.md` for where to look per ecosystem; confirm the exact command in the guide).

Write the plan to `UPGRADE.md` (in the repo root or `.claude/`), ≤80 lines:
```
# Upgrade <framework> <from> → <to>
Sources: <official guide URLs>
Runtime/tooling: <changes>
Blockers: <lib X supports up to Y — options>
Steps: 1. … (each step builds and is committed)
Breaking changes that apply: <change> — <n> hits — <how: codemod | manual | config>
Behaviour changes to QA manually: <changed defaults, caching, rendering, timezones…>
Baseline: build ok, tests 812/815 (3 known failures: …)
```
Show the user the plan before step 4 when there are blockers, more than ~20 manual changes, or a behaviour change that affects users. Otherwise continue.

## 4. Execute — small steps, each one green
Order: runtime/tooling → official codemods → version bump (manifest + lockfile with the repo's package manager) → fix compile/type errors → fix tests → fix new deprecation warnings → remove compatibility shims that the guide marks temporary.
- **Commit after each step** with a message naming the step, so a bad step can be reverted alone.
- Fix code to the new API; don't wrap old APIs in local shims unless the guide recommends a transitional package (e.g. a compat build).
- After codemods, review the diff — codemods miss dynamic usages and sometimes produce code that compiles but behaves differently.

**Never, without telling the user and getting a yes:**
- `--legacy-peer-deps`, `--force`, `overrides`/`resolutions` to force incompatible peers;
- `skipLibCheck`, `// @ts-ignore`, `#pragma warning disable`, `-W ignore`, or lowering lint/analyzer levels to make it pass;
- pinning back to the old version of a transitive dependency;
- deleting or skipping failing tests.

## 5. Verify
- Full build, type-check, lint, tests — compare to the baseline counts; new failures are upgrade bugs until proven otherwise.
- Deprecation warnings: count before/after; zero new ones is the target.
- Run the app (dev server / start command) and hit a few main pages or endpoints; for behaviour changes listed in the plan, verify each or hand them to the user as a QA checklist.
- Lockfile committed; CI config (Node/.NET/Python versions in workflows, Dockerfiles, `global.json`, `.nvmrc`, `engines`) updated to match.

## 6. Report
Five lines: from → to, steps done (commits), what needed manual changes, what the user must QA, what was left (blockers, deferred deprecations). Update `UPGRADE.md` with the result.

## When NOT to use
Patch/minor bumps with no breaking changes (just bump, build and test), security patches that only change a lockfile, or adding a new dependency.
