# Where to look, per ecosystem

These point to the **kind** of official source and tool to use. Commands change between versions — always confirm the exact command in the current official guide before running it.

## JavaScript / TypeScript
- Outdated & why: `npm outdated` / `pnpm outdated` / `yarn outdated`; `npm ls <pkg>` / `pnpm why <pkg>` to see who pulls a version.
- **React**: the upgrade guide on react.dev's blog for the target major; official codemods are run through the `codemod` CLI (react.dev lists the recipe), and TypeScript type changes through `types-react-codemod`. Check router, state, UI-kit and testing-library compatibility.
- **Next.js**: the "Upgrading" section of the Next.js docs per major; `@next/codemod` provides codemods (the docs give the exact `npx @next/codemod …` invocation). Watch changed defaults (caching, async request APIs, minimum React version).
- **Angular**: update.angular.dev generates a step list for from → to; upgrade **one major at a time** with `ng update @angular/core@<n> @angular/cli@<n>` (then other `@angular/*` and libraries like Material).
- **Vue 2 → 3**: the official migration guide and the migration build (`@vue/compat`) to run in compatibility mode while fixing warnings.
- **Node runtime**: Node release notes for removed APIs; update `.nvmrc`, `engines`, CI images and Dockerfiles together.
- **TypeScript**: the release notes' "Breaking changes" section per version; new strictness often surfaces real bugs — fix, don't silence.
- **ESLint 8 → 9**: flat config migration guide (`eslint.config.*`); the docs include a config migrator.

## .NET
- Microsoft Learn has a "Breaking changes in .NET <n>" page, plus separate pages for ASP.NET Core and EF Core per version — read all that apply.
- Bump `TargetFramework`, `global.json` SDK, and `Microsoft.*` packages together (they version in lockstep). `dotnet list package --outdated` (and `--vulnerable`) lists candidates; with central package management edit `Directory.Packages.props`.
- EF Core majors can change query translation and defaults — run integration tests against a real database, not only in-memory.
- Docker base images (`mcr.microsoft.com/dotnet/...:<n>`) and CI `setup-dotnet` versions must match.

## Python
- **Django**: upgrade one feature release at a time; first run tests with deprecation warnings visible (`python -Wd manage.py test`) on the current version and fix them; then bump. The `django-upgrade` tool rewrites many deprecated patterns; release notes list "Backwards incompatible changes".
- General: `pip list --outdated`; `pyupgrade` for syntax; check `requires-python` of every key dependency against the target Python.
- Pydantic 1 → 2, SQLAlchemy 1.4 → 2.0: both have official migration guides and transitional modes/flags — use them.

## PHP / Ruby / JVM
- **Laravel**: the official upgrade guide per major lists changes with "likelihood of impact" — handle High first.
- **Symfony**: fix all deprecations on the last minor of the current major before the major bump (deprecations log / PHPUnit bridge).
- **Rails**: one minor at a time; `bin/rails app:update` for config diffs; `new_framework_defaults_*` initializers to flip defaults gradually.
- **Spring Boot**: the GitHub wiki "Spring Boot <n> Migration Guide"; `spring-boot-properties-migrator` reports renamed properties at startup. OpenRewrite has recipes for Spring Boot and Java upgrades.

## Mobile
- **React Native**: the community Upgrade Helper diffs template files between versions; native files (Gradle, Podfile) must be updated by hand.
- **Expo**: upgrade one SDK at a time with the documented `expo install --fix` flow.
