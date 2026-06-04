# Maintenance Plan

This document records suggested follow-up issues for the OSS cleanup. These can be copied into GitHub issues when the repository maintenance workflow is ready.

## [Roadmap] Improve MLLCV documentation and quick-start tutorials

MLLCV is being reorganized into a more maintainable educational computer vision repository.

This issue tracks documentation improvements, including:

- Project overview
- Installation guide
- Module descriptions
- Beginner-friendly tutorials
- Chinese and English documentation
- Reproducible examples

## [Security] Review file loading, model loading, and dependency risks

This issue tracks security review work for MLLCV, including:

- Unsafe file loading
- Model loading risks
- Dependency vulnerabilities
- Accidental secret exposure
- Insecure path handling
- Unsafe deserialization
- Large model file policy

## [Testing] Add smoke tests for main examples

This issue tracks the addition of lightweight smoke tests to verify that major examples can be imported or executed with minimal sample inputs.

The goal is not to run full training, but to catch broken paths, missing files, and basic syntax errors.

## [Docs] Add bilingual documentation for Chinese-speaking CV learners

This issue tracks bilingual documentation improvements so that Chinese-speaking developers and students can better understand the project structure, examples, and learning path.

## [Cleanup] Remove legacy IDE files and reorganize modules

This issue tracks repository cleanup tasks, including:

- Removing IDE files
- Improving directory structure
- Adding `.gitignore`
- Clarifying module purpose
- Making the project easier to navigate
