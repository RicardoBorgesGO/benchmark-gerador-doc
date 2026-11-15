# Colorama

Faz com que sequências de caracteres de escape ANSI (utilizadas para produzir texto colorido no terminal e posicionamento de cursor) funcionem no MS Windows.

[PyPI para lançamentos](https://pypi.org/project/colorama/) | [GitHub para código-fonte](https://github.com/tartley/colorama) | [Colorama corporativo no Tidelift](https://github.com/tartley/colorama/blob/master/ENTERPRISE.md)

Se você considera o Colorama útil, por favor faça uma doação aos autores. Obrigado!

## Instalação

Testado em CPython 3.9, 3.10, 3.11, 3.12, 3.13 e PyPy 3.11.

Sem requisitos adicionais além da biblioteca padrão.

```bash
pip install colorama
# ou
conda install -c anaconda colorama
```

## Descrição

Sequências de caracteres de escape ANSI são usadas há muito tempo para produzir texto colorido no terminal e posicionamento de cursor em sistemas Unix e Mac. O Colorama faz com que isso também funcione no Windows encapsulando o `stdout`, removendo as sequências ANSI encontradas (que apareceriam como caracteres ilegíveis na saída) e convertendo-as nas chamadas Win32 apropriadas para modificar o estado do terminal. Em outras plataformas, o Colorama não realiza alterações.

Isso traz como benefício fornecer uma API multiplataforma simples para imprimir texto colorido no terminal a partir do Python. Além disso, traz o efeito positivo de permitir que aplicações ou bibliotecas existentes que usam sequências ANSI em Linux ou Mac passem a funcionar também no Windows, bastando chamar `colorama.just_fix_windows_console()` (a partir da v0.4.6) ou `colorama.init()` (todas as versões, mas pode conter outros efeitos colaterais – veja abaixo).

Uma abordagem alternativa é instalar o `ansi.sys` em máquinas Windows, o que fornece o mesmo comportamento para todas as aplicações executadas em terminais. O Colorama é destinado a situações em que essa instalação não é simples (por exemplo, quando sua aplicação não possui um instalador).

Os scripts de demonstração no repositório do código-fonte imprimem textos coloridos usando sequências ANSI. Compare a saída no tratamento ANSI nativo do Gnome-terminal com o Prompt de Comando do Windows usando Colorama.

*Nota:* No Windows, o Colorama não suporta o efeito ANSI de 'texto fraco/esmaecido' (dim text), exibindo-o da mesma forma que o 'texto normal'.

## Uso

### Inicialização

Se a única funcionalidade desejada do Colorama for fazer com que os escapes ANSI funcionem no Windows, execute:

```python
from colorama import just_fix_windows_console
just_fix_windows_console()
```

Se você estiver em uma versão recente do Windows 10 ou superior, e o seu stdout/stderr estiver apontando para um console Windows, esta instrução ativará a chave de configuração para habilitar o suporte ANSI nativo do Windows.

Se estiver em uma versão antiga do Windows e o seu stdout/stderr estiver apontando para um console Windows, a instrução encapsulará `sys.stdout` e/ou `sys.stderr` em um objeto de arquivo especial que intercepta as sequências de escape ANSI e emite as chamadas Win32 correspondentes para emulá-las.

Em qualquer outra circunstância, a função não realiza alterações. A ideia principal é fazer o Windows se comportar como o Unix no tratamento de escapes ANSI.

É seguro chamar esta função múltiplas vezes. É seguro chamá-la em plataformas não-Windows (onde não terá efeito). Também é seguro chamá-la quando o stdout/stderr estiver redirecionado para um arquivo (esses fluxos não serão alterados).

Alternativamente, você pode usar a interface antiga que possui mais recursos (embora apresente maiores riscos de uso incorreto):

```python
from colorama import init
init()
```

Esta chamada realiza o mesmo que `just_fix_windows_console`, com as seguintes diferenças:

- Não é seguro chamar `init` múltiplas vezes, pois isso pode resultar em camadas duplicadas de encapsulamento e falha no suporte ANSI.

- O Colorama aplicará uma heurística para adivinhar se stdout/stderr suportam ANSI. Caso conclua que não suportam, encapsulará `sys.stdout` e `sys.stderr` em um objeto de arquivo especial que remove as sequências de escape ANSI antes de imprimi-las. Isso ocorre em todas as plataformas e pode ser conveniente caso você deseje escrever código emitindo sequências ANSI incondicionalmente e deixar que o Colorama decida se elas devem ser exibidas. No entanto, note que a heurística do Colorama não é excessivamente complexa.

- A função `init` também aceita argumentos nomeados explícitos para ativar ou desativar funcionalidades (veja abaixo).

Para interromper o uso do Colorama antes do encerramento do programa, chame `deinit()`. Isso restaurará `stdout` e `stderr` aos seus valores originais. Para retomar o uso, chame `reinit()`, o que é computacionalmente mais leve do que chamar `init()` novamente.

A maioria dos usuários deve utilizar `colorama >= 0.4.6` e optar por `just_fix_windows_console`. A interface antiga `init` continuará mantida por compatibilidade retroativa, mas não há planejamento para correção de problemas nela.

### Saída Colorida

A impressão de texto colorido de forma multiplataforma pode ser feita usando as constantes de atalho do Colorama para sequências de escape ANSI:

```python
from colorama import Fore, Back, Style
print(Fore.RED + 'texto em vermelho')
print(Back.GREEN + 'com fundo verde')
print(Style.DIM + 'e texto esmaecido')
print(Style.RESET_ALL)
print('de volta ao normal')
```

...ou imprimindo manualmente sequências ANSI a partir do seu próprio código:

```python
print('\033[31m' + 'texto em vermelho')
print('\033[39m') # restaura a cor padrao
```

...ou ainda combinando o Colorama com bibliotecas ANSI existentes como [Termcolor](https://pypi.org/project/termcolor/), [Blessings](https://pypi.org/project/blessings/) ou [_Rich](https://pypi.org/project/rich/).

Caso você precise de mais recursos do que as constantes Fore, Back e Style oferecem, considere utilizar uma das bibliotecas acima para a geração de cores e mantenha o Colorama focado em seu propósito primário: converter essas sequências ANSI para funcionarem no Windows.

Da mesma forma, não envie Pull Requests adicionando a geração de novos tipos ANSI ao Colorama. O escopo do projeto é estritamente converter códigos ANSI em chamadas da API win32.

```python
from colorama import just_fix_windows_console
from termcolor import colored

# usa o Colorama para fazer o Termcolor funcionar tambem no Windows
just_fix_windows_console()

# usa o Termcolor para todas as saidas de texto colorido
print(colored('Hello, World!', 'green', 'on_red'))
```

As constantes de formatação disponíveis são:

```text
Fore: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
Back: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
Style: DIM, NORMAL, BRIGHT, RESET_ALL
```

`Style.RESET_ALL` restaura cor de primeiro plano, plano de fundo e brilho. O Colorama realiza este reset automaticamente ao encerrar o programa.

As seguintes constantes possuem suporte amplo, embora não façam parte do padrão estrito:

```text
Fore: LIGHTBLACK_EX, LIGHTRED_EX, LIGHTGREEN_EX, LIGHTYELLOW_EX, LIGHTBLUE_EX, LIGHTMAGENTA_EX, LIGHTCYAN_EX, LIGHTWHITE_EX
Back: LIGHTBLACK_EX, LIGHTRED_EX, LIGHTGREEN_EX, LIGHTYELLOW_EX, LIGHTBLUE_EX, LIGHTMAGENTA_EX, LIGHTCYAN_EX, LIGHTWHITE_EX
```

### Posicionamento do Cursor

Códigos ANSI para reposicionamento de cursor são suportados. Veja `demos/demo06.py` para exemplos de geração.

### Argumentos Nomeados do Init

`init()` aceita argumentos `**kwargs` para sobrescrever o comportamento padrão.

- `init(autoreset=False)`:
  Se você precisa enviar sequências de reset constantemente ao final de cada impressão, `init(autoreset=True)` automatizará esse processo:

  ```python
  from colorama import init
  init(autoreset=True)
  print(Fore.RED + 'texto em vermelho')
  print('retorna automaticamente para a cor padrao')
  ```

- `init(strip=None)`:
  Passe `True` ou `False` para definir se os códigos ANSI devem ser removidos da saída. O comportamento padrão remove os códigos no Windows ou quando a saída está redirecionada (não é um tty).

- `init(convert=None)`:
  Passe `True` ou `False` para definir se os códigos ANSI devem ser convertidos em chamadas win32. O comportamento padrão converte no Windows quando a saída é um tty (terminal).

- `init(wrap=True)`:
  No Windows, o Colorama funciona substituindo `sys.stdout` e `sys.stderr` por objetos proxy que sobrescrevem o método `.write()`. Caso esse encapsulamento gere conflitos, pode ser desativado com `init(wrap=False)`. O padrão é encapsular se `autoreset`, `strip` ou `convert` forem verdadeiros.

  Com o encapsulamento desativado, a impressão colorida em plataformas não-Windows continuará funcionando normalmente. Para saídas coloridas multiplataforma, você pode utilizar o proxy `AnsiToWin32` do Colorama diretamente:

  ```python
  import sys
  from colorama import init, AnsiToWin32
  init(wrap=False)
  stream = AnsiToWin32(sys.stderr).stream

  print(Fore.BLUE + 'texto azul no stderr', file=stream)
  ```

### Sequências ANSI Reconhecidas

Sequências ANSI geralmente seguem o formato:

```text
ESC [ <parametro> ; <parametro> ... <comando>
```

Onde `<parametro>` é um número inteiro e `<comando>` é uma letra única. Zero ou mais parâmetros são passados para o `<comando>`. A ausência de parâmetros é equivalente a passar o valor zero. Não existem espaços na sequência (foram adicionados apenas para facilitar a leitura).

As únicas sequências ANSI convertidas em chamadas win32 pelo Colorama são:

```text
ESC [ 0 m       # restaura tudo (cores e brilho)
ESC [ 1 m       # brilho / negrito
ESC [ 2 m       # esmaecido (exibido como brilho normal no Windows)
ESC [ 22 m      # brilho normal

# PRIMEIRO PLANO (FOREGROUND):
ESC [ 30 m      # preto
ESC [ 31 m      # vermelho
ESC [ 32 m      # verde
ESC [ 33 m      # amarelo
ESC [ 34 m      # azul
ESC [ 35 m      # magenta
ESC [ 36 m      # ciano
ESC [ 37 m      # branco
ESC [ 39 m      # restaurar padrao

# PLANO DE FUNDO (BACKGROUND):
ESC [ 40 m      # preto
ESC [ 41 m      # vermelho
ESC [ 42 m      # verde
ESC [ 43 m      # amarelo
ESC [ 44 m      # azul
ESC [ 45 m      # magenta
ESC [ 46 m      # ciano
ESC [ 47 m      # branco
ESC [ 49 m      # restaurar padrao

# posicionamento de cursor:
ESC [ y;x H     # posiciona o cursor na coluna x, linha y
ESC [ y;x f     # posiciona o cursor na coluna x, linha y
ESC [ n A       # move o cursor n linhas para cima
ESC [ n B       # move o cursor n linhas para baixo
ESC [ n C       # move o cursor n caracteres para a frente
ESC [ n D       # move o cursor n caracteres para tras

# limpar a tela:
ESC [ modo J    # limpa a tela

# limpar a linha:
ESC [ modo K    # limpa a linha
```

Múltiplos parâmetros numéricos para o comando `'m'` podem ser combinados em uma única sequência:

```text
ESC [ 36 ; 45 ; 1 m     # texto ciano brilhante em fundo magenta
```

Todas as outras sequências ANSI no formato `ESC [ <parametro> ; <parametro> ... <command>` são silenciosamente removidas da saída no Windows.

Qualquer outra variação de sequência ANSI, como códigos de caractere único ou caracteres iniciais alternativos, não é reconhecida nem removida.

## Status e Problemas Conhecidos

Testado em Windows XP (CMD, Console2), Ubuntu (gnome-terminal, xterm) e OS X.

Algumas sequências ANSI válidas não são reconhecidas.

Consulte os problemas em aberto e solicitações no repositório do projeto: https://github.com/tartley/colorama/issues

## Licença

Copyright Jonathan Hartley & Arnon Yaari, 2013-2020. Licença BSD 3-Clause; consulte o arquivo LICENSE.

## Suporte Profissional

Suporte profissional para o Colorama está disponível como parte do Tidelift Subscription. O Tidelift oferece às equipes de desenvolvimento uma fonte única para compra e manutenção de software, com garantias profissionais de especialistas.

## Agradecimentos

Consulte o CHANGELOG para ver a lista completa de agradecimentos aos contribuidores do projeto.