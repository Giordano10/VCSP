# Changelog
All notable changes to this project will be documented in this file.
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


