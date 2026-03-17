# Input Detection Heuristics

> Version: v1.0 | Feature: FEATURE-050-A | Last Updated: 03-17-2026

---

## Purpose

This document defines the heuristic rules used by the Application Knowledge Extractor to classify input sources. The extractor analyzes the target path or URL and determines: **input type**, **format**, and **app type**.

---

## Input Type Detection

### Classification Rules

| Signal | Input Type | Confidence |
|--------|-----------|------------|
| Directory with `package.json`, `Cargo.toml`, `pyproject.toml`, `go.mod`, `pom.xml`, `build.gradle` | `source_code_repo` | High |
| Directory with only `.md`, `.rst`, `.txt`, `.adoc` files (no code files) | `documentation_folder` | High |
| URL matching `localhost:*` or `127.0.0.1:*` or `0.0.0.0:*` | `running_web_app` | High |
| URL matching `https?://[^localhost].*` | `public_url` | High |
| Single file path (not a directory) | `single_file` | High |
| Directory with mix of code + docs | `source_code_repo` | Medium |
| Path does not exist | Error | — |

---

## Format Detection

| File Extension(s) | Format |
|-------------------|--------|
| `.md`, `.markdown` | `markdown` |
| `.py` | `python` |
| `.js`, `.jsx`, `.ts`, `.tsx` | `javascript` |
| `.html`, `.htm` | `html` |
| `.yaml`, `.yml` | `yaml` |
| `.json` | `json` |
| Multiple extensions | `mixed` |
| No recognized extension | `unknown` |

---

## App Type Detection

| Signal | App Type | Priority |
|--------|----------|----------|
| Flask/Django/Express/Rails markers | `web` | 1 |
| argparse, click, commander, clap | `cli` | 2 |
| React Native, Flutter, Swift, Kotlin | `mobile` | 3 |
| No framework markers | `unknown` | 4 |

### Framework Detection

**Web Frameworks:**
- Flask: `from flask import` in .py files OR `Flask` in requirements.txt
- Django: `from django` in .py files OR `Django` in requirements.txt
- Express: `require('express')` in .js files OR `"express"` in package.json
- Rails: `require 'rails'` in .rb files OR `gem 'rails'` in Gemfile

**CLI Frameworks:**
- argparse: `import argparse` in .py files
- click: `import click` OR `Click` in requirements.txt
- commander: `require('commander')` OR `"commander"` in package.json
- clap: `use clap` in .rs files OR `clap` in Cargo.toml

**Mobile Frameworks:**
- React Native: `"react-native"` in package.json
- Flutter: `pubspec.yaml` with `flutter` dependency
- Swift/iOS: `.swift` files + Xcode project
- Kotlin/Android: `.kt` files + Gradle build files

---

## Priority Resolution

When multiple app types detected: web (1) > cli (2) > mobile (3) > unknown (4)

---

## References

- **Technical Design:** `x-ipe-docs/requirements/EPIC-050/FEATURE-050-A/technical-design.md`
- **Specification:** `x-ipe-docs/requirements/EPIC-050/FEATURE-050-A/specification.md`
