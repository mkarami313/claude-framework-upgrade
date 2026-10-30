#!/usr/bin/env python3
"""detect_versions.py — list frameworks, runtimes and package managers in a repo, with versions.

Usage: python3 detect_versions.py [path] [--all]

Scans package.json, *.csproj / *.fsproj / Directory.Packages.props / global.json, pyproject.toml,
requirements*.txt, go.mod, composer.json, Gemfile.lock, pom.xml, build.gradle(.kts) and runtime
pins (.nvmrc, .node-version, .python-version, .tool-versions). Prints one line per finding:
    <ecosystem>  <package>  <declared version>  <file>
By default only well-known frameworks/tooling are shown; --all shows every dependency.
Python 3 standard library only.
"""
import json
import os
import re
import sys

SKIP = {"node_modules", ".git", "bin", "obj", "dist", "build", ".next", ".venv", "venv", "vendor",
        "target", ".gradle", "__pycache__", ".tox", "coverage", ".nuxt", ".svelte-kit"}
KEY_NPM = re.compile(r"^(react|react-dom|next|vue|nuxt|@angular/core|@angular/cli|svelte|@sveltejs/kit|vite|webpack|"
                     r"typescript|tailwindcss|eslint|jest|vitest|@playwright/test|express|@nestjs/core|"
                     r"react-router|react-router-dom|@remix-run/\w+|astro|@tanstack/react-query|redux|@reduxjs/toolkit|"
                     r"@mui/material|antd|prisma|@prisma/client|typeorm|mongoose|electron|react-native|expo|"
                     r"storybook|@storybook/react|graphql|@apollo/client|zod|node)$")
KEY_NUGET = re.compile(r"^(Microsoft\.AspNetCore\.|Microsoft\.EntityFrameworkCore|Microsoft\.Extensions\.|"
                       r"Swashbuckle|MediatR|AutoMapper|FluentValidation|xunit|NUnit|MSTest|Serilog|Newtonsoft\.Json|"
                       r"Npgsql|Dapper|MassTransit|Hangfire)", re.I)
KEY_PY = re.compile(r"^(django|djangorestframework|flask|fastapi|pydantic|sqlalchemy|alembic|celery|pandas|numpy|"
                    r"pytest|starlette|uvicorn|gunicorn|requests|httpx|tensorflow|torch|scikit-learn|python)$", re.I)
KEY_PHP = re.compile(r"^(php|laravel/framework|symfony/framework-bundle|symfony/symfony|livewire/livewire|"
                     r"phpunit/phpunit|doctrine/orm)$")
KEY_RB = re.compile(r"^(rails|ruby|rspec-core|sidekiq|devise)$")
KEY_JVM = re.compile(r"(spring-boot|spring-framework|kotlin|hibernate-core|junit)", re.I)

rows = []


def add(eco, pkg, ver, path, root):
    rows.append((eco, pkg, (ver or "?").strip(), os.path.relpath(path, root)))


def scan_package_json(p, root, show_all):
    try:
        d = json.load(open(p, encoding="utf-8"))
    except (OSError, ValueError):
        return
    for sec in ("dependencies", "devDependencies", "peerDependencies"):
        for k, v in (d.get(sec) or {}).items():
            if show_all or KEY_NPM.match(k):
                add("npm", k, str(v), p, root)
    eng = d.get("engines") or {}
    for k in ("node", "npm", "pnpm", "yarn"):
        if k in eng:
            add("runtime", f"engines.{k}", eng[k], p, root)
    if d.get("packageManager"):
        add("tool", "packageManager", d["packageManager"], p, root)


def scan_dotnet(p, root, show_all):
    try:
        txt = open(p, encoding="utf-8", errors="replace").read()
    except OSError:
        return
    for m in re.finditer(r"<TargetFrameworks?>([^<]+)</TargetFrameworks?>", txt):
        add("dotnet", "TargetFramework", m.group(1), p, root)
    for m in re.finditer(r'<Package(?:Reference|Version)\s+(?:Include|Update)="([^"]+)"(?:\s+Version="([^"]*)")?', txt):
        if show_all or KEY_NUGET.match(m.group(1)):
            add("nuget", m.group(1), m.group(2) or "(central)", p, root)
    for m in re.finditer(r'<Project\s+Sdk="([^"]+)"', txt):
        add("dotnet", "Sdk", m.group(1), p, root)


def scan_global_json(p, root):
    try:
        d = json.load(open(p, encoding="utf-8"))
        add("runtime", "dotnet-sdk", (d.get("sdk") or {}).get("version", "?"), p, root)
    except (OSError, ValueError):
        pass


def scan_pyproject(p, root, show_all):
    try:
        txt = open(p, encoding="utf-8", errors="replace").read()
    except OSError:
        return
    data = None
    try:
        import tomllib  # Python 3.11+
        data = tomllib.loads(txt)
    except Exception:
        data = None
    deps = []
    if data:
        proj = data.get("project", {})
        deps += proj.get("dependencies", []) or []
        for grp in (proj.get("optional-dependencies") or {}).values():
            deps += grp
        if proj.get("requires-python"):
            add("runtime", "python", proj["requires-python"], p, root)
        poetry = data.get("tool", {}).get("poetry", {})
        for k, v in (poetry.get("dependencies") or {}).items():
            deps.append(f"{k} {v if isinstance(v, str) else v.get('version', '?') if isinstance(v, dict) else v}")
    else:
        deps = re.findall(r'^\s*"([A-Za-z0-9_.\-\[\]]+\s*[<>=!~^ ][^"]*)"', txt, re.M)
    for dep in deps:
        m = re.match(r"\s*([A-Za-z0-9_.\-]+)(\[[^\]]*\])?\s*(.*)", str(dep))
        if m and (show_all or KEY_PY.match(m.group(1))):
            add("pypi", m.group(1).lower(), m.group(3) or "*", p, root)


def scan_requirements(p, root, show_all):
    try:
        for line in open(p, encoding="utf-8", errors="replace"):
            line = line.split("#")[0].strip()
            m = re.match(r"([A-Za-z0-9_.\-]+)(\[[^\]]*\])?\s*([<>=!~].*)?$", line)
            if m and (show_all or KEY_PY.match(m.group(1))):
                add("pypi", m.group(1).lower(), m.group(3) or "*", p, root)
    except OSError:
        pass


def scan_go(p, root, show_all):
    try:
        txt = open(p, encoding="utf-8").read()
    except OSError:
        return
    m = re.search(r"^go\s+(\S+)", txt, re.M)
    if m:
        add("runtime", "go", m.group(1), p, root)
    if show_all:
        for m in re.finditer(r"^\s*([\w./-]+\.[\w./-]+)\s+(v\S+)", txt, re.M):
            add("go", m.group(1), m.group(2), p, root)


def scan_composer(p, root, show_all):
    try:
        d = json.load(open(p, encoding="utf-8"))
    except (OSError, ValueError):
        return
    for sec in ("require", "require-dev"):
        for k, v in (d.get(sec) or {}).items():
            if show_all or KEY_PHP.match(k):
                add("composer", k, v, p, root)


def scan_gemfile_lock(p, root, show_all):
    try:
        for line in open(p, encoding="utf-8", errors="replace"):
            m = re.match(r"^    ([a-z0-9_\-]+) \(([^)]+)\)", line)
            if m and (show_all or KEY_RB.match(m.group(1))):
                add("gem", m.group(1), m.group(2), p, root)
            m = re.match(r"^\s+ruby (\S+)", line)
            if m:
                add("runtime", "ruby", m.group(1), p, root)
    except OSError:
        pass


def scan_jvm(p, root, show_all):
    try:
        txt = open(p, encoding="utf-8", errors="replace").read()
    except OSError:
        return
    if p.endswith("pom.xml"):
        for m in re.finditer(r"<artifactId>([^<]+)</artifactId>\s*<version>([^<]+)</version>", txt):
            if show_all or KEY_JVM.search(m.group(1)):
                add("maven", m.group(1), m.group(2), p, root)
        m = re.search(r"<java\.version>([^<]+)</java\.version>", txt)
        if m:
            add("runtime", "java", m.group(1), p, root)
    else:
        for m in re.finditer(r"""id\s*\(?\s*["']([\w.\-]+)["']\s*\)?\s*version\s*\(?\s*["']([^"']+)["']""", txt):
            if show_all or KEY_JVM.search(m.group(1)):
                add("gradle", m.group(1), m.group(2), p, root)
        for m in re.finditer(r"""["']([\w.\-]+):([\w.\-]+):([^"']+)["']""", txt):
            if show_all or KEY_JVM.search(m.group(2)):
                add("gradle", f"{m.group(1)}:{m.group(2)}", m.group(3), p, root)


def scan_pin(p, root, name):
    try:
        txt = open(p, encoding="utf-8").read().strip()
    except OSError:
        return
    if name == ".tool-versions":
        for line in txt.splitlines():
            parts = line.split()
            if len(parts) >= 2:
                add("runtime", parts[0], parts[1], p, root)
    else:
        add("runtime", {".nvmrc": "node", ".node-version": "node", ".python-version": "python"}[name], txt, p, root)


LOCKS = {"package-lock.json": "npm", "pnpm-lock.yaml": "pnpm", "yarn.lock": "yarn", "bun.lockb": "bun",
         "bun.lock": "bun", "poetry.lock": "poetry", "uv.lock": "uv", "Pipfile.lock": "pipenv",
         "packages.lock.json": "nuget-lock", "composer.lock": "composer", "Gemfile.lock": "bundler", "go.sum": "go"}


def main(argv):
    show_all = "--all" in argv
    args = [a for a in argv if not a.startswith("--")]
    root = os.path.abspath(args[0] if args else ".")
    if not os.path.isdir(root):
        print(f"not a directory: {root}")
        return 2
    locks = set()
    for d, dirs, files in os.walk(root):
        dirs[:] = [x for x in dirs if x not in SKIP and not x.startswith(".")]
        for f in files:
            p = os.path.join(d, f)
            if f in LOCKS:
                locks.add(f"{LOCKS[f]} ({os.path.relpath(p, root)})")
            if f == "package.json":
                scan_package_json(p, root, show_all)
            elif f.endswith((".csproj", ".fsproj", ".vbproj")) or f in ("Directory.Packages.props", "Directory.Build.props"):
                scan_dotnet(p, root, show_all)
            elif f == "global.json":
                scan_global_json(p, root)
            elif f == "pyproject.toml":
                scan_pyproject(p, root, show_all)
            elif re.match(r"requirements.*\.(txt|in)$", f):
                scan_requirements(p, root, show_all)
            elif f == "go.mod":
                scan_go(p, root, show_all)
            elif f == "composer.json":
                scan_composer(p, root, show_all)
            elif f == "Gemfile.lock":
                scan_gemfile_lock(p, root, show_all)
            elif f in ("pom.xml", "build.gradle", "build.gradle.kts"):
                scan_jvm(p, root, show_all)
        for f in (".nvmrc", ".node-version", ".python-version", ".tool-versions"):
            if f in files:
                scan_pin(os.path.join(d, f), root, f)

    print(f"root={root} findings={len(rows)}")
    print("lockfiles: " + (", ".join(sorted(locks)) if locks else "none found"))
    seen = set()
    for r in sorted(rows, key=lambda r: (r[0] != "runtime", r[0], r[1].lower(), r[3])):
        if r in seen:
            continue
        seen.add(r)
        print(f"{r[0]:<8} {r[1]:<40} {r[2]:<22} {r[3]}")
    if not rows:
        print("no known manifests found (try --all, or point at the app folder)")
    # same package with different versions across manifests → worth knowing before an upgrade
    vers = {}
    for eco, pkg, ver, _ in rows:
        vers.setdefault((eco, pkg), set()).add(ver)
    drift = [(e, p, sorted(v)) for (e, p), v in vers.items() if len(v) > 1 and e != "runtime"]
    if drift:
        print("\nversion drift across manifests:")
        for e, p, v in drift:
            print(f"  {e} {p}: {', '.join(v)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
