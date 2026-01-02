Dependabot (opcional)

Este repositório está configurado para usar o Dependabot no GitHub para
monitorar e propor atualizações de dependências. Observações importantes:

- O Dependabot roda no GitHub e não é uma dependência do projeto. Ele não deve
  ser adicionado ao `requirements.txt` ou imposto a quem instala a biblioteca.
- Configurações relevantes:
  - `.github/dependabot.yml` — regras de atualização (pip, GitHub Actions, etc.).
  - `.github/workflows/dependabot-pr-tests.yml` — workflow que executa testes
    nas PRs do Dependabot antes do merge.
  - `.github/workflows/dependabot-auto-merge.yml` — política de auto-merge para
    updates patch/minor (configurada neste repositório).

Se preferir, posso inserir este conteúdo diretamente no `README.md`.
