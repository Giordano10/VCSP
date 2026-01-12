# Changelog
All notable changes to this project will be documented in this file.
## [Unreleased]

### Documentation

- Update security trend chart (b59f34f)

- Update security trend chart (1fd6473)

- Update security trend chart (62dfbaa)

- Update security trend chart (19b30ae)

- Update security trend chart (61a269e)

- Update security trend chart (c166f89)

- Update security trend chart (97072ad)

- Update security trend chart (a042935)

- Update security trend chart (7dc8f34)

- Update security trend chart (47b2758)

- Update security trend chart (6fa1cb7)

- Update security trend chart (858d6c0)

- Update security trend chart (61adf33)

- Update security trend chart (fa8fde2)

- Update security trend chart (b4dc574)

- Update security trend chart (625f567)

- Update security trend chart (a1ff128)

- Update security trend chart (326d3ec)

- Update security trend chart (17cb541)

- Update security trend chart (8900541)


### Miscellaneous Tasks

- Update changelog and version to v1.0.3.4 (3b69620)

- Chore (e6c9461)

- Ajusta workflow para usar requirements separados (f8d4ef2)

- Bump actions/setup-python from 5 to 6 (177195b)

- Ajusta workflow para usar requirements separados (14bebe5)

- Bump pillow from 12.0.0 to 12.1.0 (690bb90)

- Update changelog and version to v1.0.3.5 (4edbba1)

- Update changelog and version to v1.0.3.5 (39d9bcb)


### Att

- README melhorado com informações mais pertinentes (0bf59de)


## [1.0.3.4] - 2026-01-05

### Bug Fixes

- Corrige conflito de git e regex de versao no release (8ec0247)


### Documentation

- Update security trend chart (9abc9d9)

- Update security trend chart (88a1fee)


### Miscellaneous Tasks

- Update changelog and version to v1.0.3.3 (6ca1b5e)


## [1.0.3.3] - 2026-01-05

### Bug Fixes

- Fix (f1885ed)

- Version of vcsp-guard incorrect on pyproject.toml (08cee43)

- Corrige conflito de git e regex de versao no release (06b27c8)


### Documentation

- Update security trend chart (d0cc7b4)

- Update security trend chart (503b46f)

- Update security trend chart (bffcfb9)

- Update security trend chart (613d320)


### Fix

- Version (992c6e4)

- Version (7f643d2)


### Miscellaneous Tasks

- Update changelog and version to v1.0.3.2 (b2be7b3)


## [1.0.3.2] - 2026-01-02

### Bug Fixes

- Update .gitignore to allow committing metrics directory and its assets (f816cdc)

- Correct syntax for Python script execution and update regex in README update logic (9a3cf9e)

- Ensure pytest is installed and run with the correct Python interpreter (f969aa4)

- Enhance dependency installation and logging output in CI workflow (9715ce8)

- Streamline dependency installation in Dependabot PR workflow (901917e)

- Separate pip upgrade and dependency installation in Dependabot PR workflow (4f4b515)

- Improve dependency installation and verification in Dependabot PR workflow (fee5503)

- Streamline Dependabot PR test workflow and improve dependency installation (8c1c337)

- Update requirements files to include missing dependencies and improve formatting (5e4e5bc)

- Remove unused dependencies from requirements.txt (3aa808b)


### Documentation

- Update security trend chart (bbd5ed9)

- Update CHANGELOG.md (ec8478b)

- Update security trend chart (cbdb9c5)

- Update security trend chart (f80b794)

- Update security trend chart (38ff6e8)

- Update security trend chart (428e8b5)

- Update security trend chart (c3b031d)

- Update security trend chart (46565fa)

- Update security trend chart (a081a80)

- Update security trend chart (e598c4c)

- Update security trend chart (0a27c4f)

- Update security trend chart (1b7eb69)

- Update security trend chart (82c30ca)

- Update security trend chart (6c3384e)

- Update security trend chart (d70d72f)

- Update security trend chart (1ff5b5a)

- Update security trend chart (40fbe07)

- Update security trend chart (dd45890)

- Update security trend chart (1c50b39)

- Update security trend chart (d7b86b5)

- Update security trend chart (9af6411)


### Features

- Improve linter execution handling (22310d4)

- Add GitHub workflows for release publishing and security auditing (56ca7af)

- Add Dependabot configuration and documentation (89fb56b)

- Add Vibe Coding Security Protocol (VCSP) guidelines (4a3a69f)


### Miscellaneous Tasks

- Update GitHub Actions workflows and dependencies; improve security checks and documentation (d78b25d)

- Downgrade Python version from 3.13 to 3.12 in security scan workflows (8663633)

- Update Python version to 3.11 in workflows for consistency (0b63c36)

- Remove deprecated GitHub workflows and security instructions (1b387d8)

- Remove deprecated GitHub workflows and security instructions (3048683)

- Remove obsolete Copilot instructions for VCSP (9ae9955)

- Update Dependabot PR Tests workflow name and improve dependency installation comments (68593cb)

- Remove suggestion to add Dependabot content to README.md (1c71e73)

- Bump actions/setup-python from 4 to 6 (c2ea40a)

- Bump pascalgn/automerge-action from 0.14.3 to 0.16.4 (d540206)

- Bump actions/upload-artifact from 4 to 6 (5205b01)

- Bump stefanzweifel/git-auto-commit-action from 5 to 7 (1d07ffb)


### Refactor

- Enhance test readability and update assertions for security tools (60a3ca1)

- Add noqa comments for improved linting in test cases (ea76c5a)


### Testing

- Update security tool checks and module import behavior; replace bandit with ruff (eb224dc)

- Enhance function signature checks for scanner module (f2d02bf)


## [1.0.3.1] - 2025-12-27

### Bug Fixes

- Remove tomli dependency from requirements.in and update requirements.txt references (48138f6)

- Remove unused dependencies from requirements.txt (8fce063)

- Update output directory for generated graphs in generate_stats.py (5b30d80)

- Update asset paths for security trend chart in workflow (a7e1cad)

- Handle missing 'semgrep' data in vulnerability trend graph (34d823a)

- Update README.md for cache busting of bug trend image (3e94bcf)


### Documentation

- Update CHANGELOG.md (53c76df)

- Update security trend chart (db8968b)


### Features

- Add dependency file detection and unused libraries check in scan_project.py (ac13457)


## [1.0.3] - 2025-12-27

### Bug Fixes

- Remove unused import of sys in test_sample.py (939bfc1)

- Add error handling for pip-audit installation failures in CI/CD environments (aea1f43)

- Specify platform dependency for pywin32 in requirements.txt (ed6111b)


### Documentation

- Update CHANGELOG.md (473f5e7)


### Features

- Add Checkov infrastructure analysis and enhance security tool tests (7ce8739)

- Add Semgrep support for IaC scanning and update security audit workflow (bb5bbab)

- Add Semgrep to security scan workflow for enhanced vulnerability detection (70e1f2a)

- Upgrade semgrep version in dependencies and installation scripts (d158856)


## [1.0.2.1] - 2025-12-22

### Bug Fixes

- Update filelock and ruff versions in requirements.txt (767006b)


### Documentation

- Update CHANGELOG.md (0a381a9)


### Features

- Add command --version (07162d9)


## [1.0.2] - 2025-12-16

### Bug Fixes

- Fix (75ada5e)

- Fix (0b0edca)


### Documentation

- Update CHANGELOG.md (8cb84f9)


### Add

- Instrução para ajustar o horario de verificação no github actions dentro do arquivo security_scan.yml (916c831)


## [1.0.1.10] - 2025-12-16

### Bug Fixes

- Fix (e5600d8)

- Upgrade CI python version to 3.11 to support modern dependencies (43e636b)


### Documentation

- Update CHANGELOG.md (3f9a534)


## [1.0.1.9] - 2025-12-16

### Bug Fixes

- Remove heavy dependencies (pandas) from production build and the requirements.in file was created to refactor the requirements.txt file. (5afa389)


### Documentation

- Update CHANGELOG.md (b010125)


## [1.0.1.8] - 2025-12-15

### Bug Fixes

- Fix (8c4a637)


### Documentation

- Update CHANGELOG.md (1208247)


## [1.0.1.7] - 2025-12-15

### Bug Fixes

- Add git pull rebase to security workflow to prevent race conditions (dc2b0fb)


### Documentation

- Update CHANGELOG.md (530c1e4)

- Update security trend chart (25ce1c2)


## [1.0.1.6] - 2025-12-15

### Bug Fixes

- Fix (247dbd9)


### Documentation

- Update CHANGELOG.md (e435aa9)

- Update security trend chart (3add28c)


### Features

- New command to generate the bug evolution graph. (136403e)


## [1.0.1.5] - 2025-12-15

### Bug Fixes

- Corrigido um argumento para ignorar senhas em arquivos de teste com parametro declarado "nosec" (d84d1d6)


### Documentation

- Update security trend chart (de1c963)

- Update CHANGELOG.md (0d060dd)


## [1.0.1.4] - 2025-12-15

### Bug Fixes

- .env file verification fixed. (ce2c6d5)


### Documentation

- Update security trend chart (fa50aa2)

- Update CHANGELOG.md (ebe3152)


## [1.0.1.3] - 2025-12-15

### Documentation

- Update security trend chart (e6e8882)

- Update CHANGELOG.md (b99257c)


### Ix

- Regenerate source files with f-strings (b0ed9ea)


## [1.0.1.2] - 2025-12-15

### Bug Fixes

- Corrigido problema de prefixo no inicio de alguns strings, o que causava um problema de ausencia de exibição de alguns textos ao rodar a lib em outros projetos (92cbb56)


### Documentation

- Update CHANGELOG.md (0804576)


## [1.0.1.1] - 2025-12-15

### Bug Fixes

- Fix (f518ae9)

- Fix (cc62b9d)


### Documentation

- Update security trend chart (4a420e1)

- Update CHANGELOG.md (0fe4fd8)

- Update security trend chart (1984a69)

- Update security trend chart (f121add)

- Update security trend chart (84f94cd)


### Att

- Readme atualizado (3c7f285)


## [1.0.1] - 2025-12-15

### "docs

- Add MIT License" (6921e9c)


### Att

- Readme Corrigido (6abd58f)

- Assinatura do readme (c954633)


### Bug Fixes

- Fix (dbd1a46)

- Fix (4d89d0d)

- Fix readme (471f83a)

- Fix (f162547)

- Lib descontinuada (1e139b0)

- Fix (2554fb2)

- Ignore asserts in tests for bandit scan (d075ed7)

- Fix (e7cf1fb)

- Fix (627dc50)

- Improved readme to include more details on how it works. (b6c2dec)

- Improved audit rules for more accurate error testing. (8058307)

- Fix (5100b0b)

- Improved readme (720d48f)

- Fix (2f0ea34)

- Obsolete version of git-cliff fixed (fb286e2)

- Fix (6438a80)

- Branch master on archive changelog fixed (7751f18)


### Documentation

- Improve README for beginners (9cf6062)

- Update security trend chart (8c23921)

- Update security trend chart (884540e)

- Update security trend chart (e8eaf53)

- Update security trend chart (0d44a09)

- Update security trend chart (e9ffde9)

- Update security trend chart (128ed71)

- Update security trend chart (1347825)

- Update security trend chart (23df37d)


### Feat

- Adicionado proteção contra pentest (3781ce5)

- Adicionada verificação de pentest usando bandit (3ba6232)

- Adicionada teste de sanitização e verificação de dependencias maliciosas (0c7fd2d)

- Adicionada uma pasta de logs para historico futuro e consulta (baab531)

- Added an AI-powered file selection intelligence feature to avoid cluttering the main project folder with unused code. (0a63a2f)

- Add changelog (cb5afe8)


### Features

- Add support for Cline and Qodo Gen + Update README (c5360d2)

- A verification routine has been added every Monday, via GitHub Actions, for better management of pushes and weekly reports before the release of new features, and is documented in the readme file. (bb59620)

- Added scan graph to display errors found in the project where this repository is running. The readme has been updated to reflect these changes and is documented in the changelog file. (2bc77e4)


### Fix

- Corrigido o erro que causava a falha no github. O erro foi corrigido substituindo o antigo arquivo de erros propositais pelo arquivo pytest. alem disso, o proprio ruff havia detectado algumas vulnerabilidades no proprio codigo, de identação e sanitização, que aproveitei para corrigir junto. (36724ce)


### Miscellaneous Tasks

- Setup project structure for pypi release (228d97c)


### Refact

- Creating a folder to centralize all public AI configuration files. (4d264ea)


### Add

- The readme has been refactored and a new section has been added for contributing to the project. (235ea88)

- New text for readme and auditoria_ia.md (12af521)

- The individual configuration files for each AI have been refactored and improved to adequately address each AI's specific scenario, using the audit file as a basis. (f2bad4d)

- Graph description (0aaf26c)


### Att

- Project name on readme (9d84717)

- Licence (925eb32)


### Refact

- Fix (313bc3c)


