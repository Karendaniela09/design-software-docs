# Authorization — Daniel Salazar / Quality Normalization

> Status: AUTHORIZED FOR PULL REQUEST REVIEW  
> Date: 2026-10-21  
> Repository: `code-sena/design-software-docs`  
> Pull Request: [#328](https://github.com/code-sena/design-software-docs/pull/328)  
> Authorized developer: Daniel Salazar

## Decision

Daniel Salazar is authorized to normalize `11-quality/` in PR #328. This includes removing the non-standard `11-quality/plan-mejoramiento/` directory and only the files contained exclusively in that directory, which was previously introduced by Kevin Andrey Culma.

The change must preserve canonical QA documents. In particular, `qa-report-r4-security-scheduling.md` and its entry in `11-quality/README.md` remain part of the repository.

## Required final state

- `11-quality/` contains the established quality strategy, code-review guidance, templates, and canonical QA reports.
- No personal, learner-specific, or `plan-mejoramiento` subdirectories exist in `11-quality/`.
- Future Improvement Plan reports are added directly to `11-quality/` as `qa-report-<challenge>-<domain>.md`.
- Every report is written in technical English, includes verifiable test or audit evidence, and is indexed in `11-quality/README.md`.
- Administrative notes, screenshots, and personal presentation material remain outside `11-quality/`.

## Authorized actions

1. Delete `11-quality/plan-mejoramiento/` and its non-canonical contents.
2. Keep the existing quality templates and canonical reports.
3. Register every new QA report in `11-quality/README.md`.
4. Perform the change only through branch `docs/sch-r4-security-hardening` and PR #328; direct commits to `main` are not authorized.

## Evidence reviewed

The submitted before/after screenshots show the removal of the non-standard directory while retaining `qa-report-r4-security-scheduling.md`. The repository policy is detailed in [Improvement Plan documentation guide](../improvement-plan-documentation-guide.md).

## Completion criteria

The directory is absent, quality-report links are valid, PR #328 targets `main`, and the required review is completed before merge.