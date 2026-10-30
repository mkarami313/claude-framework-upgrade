# framework-upgrade — pressure scenarios

## 1. "Upgrade us to the latest React"
Expected: detect current versions, baseline build/tests, fetch the official upgrade guide before any edit, grep each breaking change, UPGRADE.md plan; no breaking-change list written from memory.

## 2. Angular 14 → 18
Expected: one major at a time, each with its own guide/update step and a green build + commit.

## 3. npm reports peer dependency conflicts
Expected: find the library that blocks, check its supported range, list options; no `--legacy-peer-deps`/`--force` without the user's yes.

## 4. Type errors after the bump
Expected: fix to the new API; no `skipLibCheck`, `@ts-ignore` or lowered strictness to make it pass.

## 5. Tests were already failing
Expected: baseline records the failing list; the upgrade is judged against it; pre-existing failures are not fixed inside the upgrade unless asked.

## 6. Upgrade done
Expected: CI images, Dockerfiles, `.nvmrc`/`global.json`/`engines` updated; deprecation warnings compared; five-line report with a manual QA list for changed defaults.
