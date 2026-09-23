# Roteiro do primeiro experimento

## Objetivo

Validar se o pipeline consegue gerar um Guia de Projeto tecnicamente útil
a partir de um repositório público.

## Variáveis para registrar

- modelo;
- quantização, quando aplicável;
- número de arquivos do repositório;
- número de arquivos efetivamente analisados;
- linhas de código, quando disponível;
- tamanho do contexto enviado;
- tempo de geração;
- tempo por arquivo;
- tamanho do documento gerado;
- erros observados;
- quantidade de correções humanas.

## Rodada inicial sugerida

1. Escolher 3 repositórios pequenos/médios.
2. Executar com o mesmo modelo e prompt.
3. Registrar os tempos.
4. Avaliar manualmente:
   - cobertura;
   - correção factual;
   - utilidade para onboarding;
   - qualidade da arquitetura descrita;
   - omissões;
   - informações inventadas.
5. Depois repetir com outro modelo.

## Importante

Este piloto usa uma estratégia hierárquica simples: primeiro são produzidos
resumos dos arquivos e depois um documento consolidado. Isso reduz o problema
de tentar colocar o repositório inteiro no contexto de uma única chamada.

Para a avaliação formal da pesquisa, recomenda-se evoluir posteriormente para
um pipeline com controle de contexto, amostragem, repetição de experimentos,
registro de parâmetros e avaliação automática/humana.
