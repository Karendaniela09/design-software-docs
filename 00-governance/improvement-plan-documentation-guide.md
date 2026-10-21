# Improvement Plan Documentation Guide

> Status: ACTIVE  
> Last updated: 2026-10-21  
> Scope: `design-software-docs`

## Purpose

This guide defines how developers document Improvement Plan work without mixing administrative evidence, personal folders, and technical quality reports.

## Repository boundaries

- Service repositories contain executable code and automated tests.
- `design-software-docs` is the canonical location for technical documentation.
- Documentation uses technical English and kebab-case filenames.
- Every new document is registered in the README of its section.

## Where each document belongs

| Need | Location | Required content |
|---|---|---|
| Cross-service architectural decision | `05-architecture/decisions/records/` | ADR and decisions index update |
| Service-specific design, operations, or security | `09-microservices/services/<service>/` | Service decision, runbook, security model, or equivalent technical document |
| Improvement Plan quality evidence | `11-quality/` | `qa-report-<challenge>-<domain>.md`, test matrix, audit/checklist, and README entry |
| Personal presentation notes or administrative material | Outside the technical repository | Personal material; never a `11-quality/` subdirectory |

## Quality reports

`11-quality/` accepts canonical quality documents, templates, and QA reports. Do not create personal, learner-specific, historical-delivery, or `plan-mejoramiento` folders there.

Each Improvement Plan report must:

1. use the name `qa-report-<challenge>-<domain>.md`;
2. be written in technical English;
3. identify the tested system and date;
4. contain a traceable test matrix or audit checklist;
5. distinguish verified results from pending evidence; and
6. be linked from `11-quality/README.md`.

## Pull request flow

1. Update from `main`.
2. Create an ephemeral `docs/` branch.
3. Make only scoped documentation changes.
4. Use a Conventional Commit message.
5. Open a Pull Request to `main`.
6. Complete review before merge; never commit directly to `main`.

## Control rule

A report is canonical only when it is in the correct section, indexed by that section's README, and reviewable through a Pull Request. Screenshots are supporting evidence; they do not replace a QA report or justify creating a non-standard folder.