![logo do cheat.sh](http://cheat.sh/files/big-logo-v2-fixed.png)

Acesso unificado aos melhores repositórios de cheat sheets orientados pela comunidade no mundo.

Vamos imaginar por um momento que exista um cheat sheet ideal.
Como ele deveria ser?
Quais funcionalidades ele deveria ter?

* **Conciso** — Deve conter apenas o essencial, e nada mais.
* **Rápido** — Deve ser possível utilizá-lo instantaneamente.
* **Abrangente** — Deve conter respostas para todas as perguntas possíveis.
* **Universal** — Deve estar disponível em qualquer lugar, a qualquer momento, sem preparativos.
* **Não intrusivo** — Não deve distraí-lo de sua tarefa principal.
* **Tutor** — Deve ajudá-lo a aprender o assunto.
* **Discreto** — Deve ser possível utilizá-lo de forma totalmente despercebida.

Essa ferramenta existe! É fácil de [instalar](#instalação) e conta até com [autocompletar](#autocompletar-tab-completion).

## Funcionalidades

**cheat.sh**

* Possui uma interface simples via curl, navegador ou editor de texto.
* Cobre 56 linguagens de programação, diversos SGBDs e mais de 1000 comandos UNIX/Linux fundamentais.
* Oferece acesso aos melhores repositórios de cheat sheets mantidos pela comunidade no mundo, em nível de equivalência com o StackOverflow.
* Disponível em qualquer lugar, sem necessidade de instalação, mas pode ser instalado para uso offline.
* Extremamente rápido, retornando respostas geralmente em menos de 100 ms.
* Possui um cliente de linha de comando conveniente, `cht.sh`, que oferece grandes vantagens e facilidades, embora seja opcional.
* Pode ser usado diretamente de editores de código, sem abrir o navegador e sem alternar seu contexto mental.
* Suporta um modo stealth especial, permitindo uso totalmente invisível sem tocar no teclado ou emitir sons.

<p align="center">
  <img src='https://cheat.sh/files/demo-curl.gif'/>
</p>

## Conteúdo

* [Funcionalidades](#funcionalidades)
* [Uso](#uso)
* [Cliente de linha de comando, cht.sh](#cliente-de-linha-de-comando-chtsh)
  * [Instalação](#instalação)
  * [Uso do cliente](#uso-do-cliente)
  * [Autocompletar (Tab-completion)](#autocompletar-tab-completion)
    - [Autocompletar no Bash](#autocompletar-no-bash)
    - [Autocompletar no ZSH](#autocompletar-no-zsh)
  * [Modo stealth](#modo-stealth)
  * [Cliente de linha de comando para Windows](#cliente-de-linha-de-comando-para-windows)
* [Hospedagem própria (Self-Hosting)](#hospedagem-própria-self-hosting)
  * [Docker](#docker)
* [Integração com editores](#integração-com-editores)
  * [Vim](#vim)
  * [Emacs](#emacs)
  * [Visual Studio Code](#visual-studio-code)
  * [Sublime](#sublime)
  * [IntelliJ IDEA](#intellij-idea)
  * [QT Creator](#qtcreator)
* [Páginas especiais](#páginas-especiais)
* [Busca](#busca)
* [Cheat sheets de linguagens de programação](#cheat-sheets-de-linguagens-de-programação)
* [Fontes dos cheat sheets](#fontes-dos-cheat-sheets)
* [Como contribuir](#como-contribuir)
  * [Como editar um cheat sheet](#como-editar-um-cheat-sheet)
  * [Como adicionar um cheat sheet](#como-adicionar-um-cheat-sheet)
  * [Como adicionar um repositório de cheat sheets](#como-adicionar-um-repositório-de-cheat-sheets)

## Uso

Para obter o cheat sheet de um comando UNIX/Linux pela linha de comando, faça uma requisição ao serviço usando `curl` ou qualquer outro cliente HTTP/HTTPS informando o nome do comando:

```
    curl cheat.sh/tar
    curl cht.sh/curl
    curl https://cheat.sh/rsync
    curl https://cht.sh/tr
```

Como pode ver, você pode usar tanto HTTPS quanto HTTP para acessar o serviço, e tanto o nome longo (cheat.sh) quanto o curto (cht.sh).

Aqui `tar`, `curl`, `rsync` e `tr` são nomes dos comandos UNIX/Linux para os quais você deseja obter cheat sheets.

Se não souber o nome do comando necessário, você pode pesquisar utilizando a notação `~PALAVRA_CHAVE`.
Por exemplo, para ver como criar `snapshots` de um sistema de arquivos ou volume:

```
    curl cht.sh/~snapshot
```

<p align="center">
  <img src='https://cheat.sh/files/cht.sh-url-structure.png'/>
</p>

Os cheat sheets de linguagens de programação ficam em namespaces dedicados a elas.

```
    curl cht.sh/go/Pointers
    curl cht.sh/scala/Functions
    curl cht.sh/python/lambda
```

Para listar os cheat sheets disponíveis de uma linguagem, use a consulta especial `:list`:

```
    curl cht.sh/go/:list
```

Quase todas as linguagens possuem uma página especial chamada `:learn` que descreve os conceitos básicos do idioma (mapeamento direto do projeto *"Learn X in Y"*). Pode ser um ótimo ponto de partida para quem está começando a aprender uma linguagem.

Caso não exista um cheat sheet pronto para a consulta (o que ocorre na maioria dos casos), ele é gerado dinamicamente com base em cheat sheets disponíveis e respostas do StackOverflow. Claro que não há garantia de resposta 100% precisa, mas quase sempre é exatamente o que você procura.

Experimente estas consultas (e as suas próprias) para ver como são as respostas:

```
    curl cht.sh/go/reverse+a+list
    curl cht.sh/python/random+list+elements
    curl cht.sh/js/parse+json
    curl cht.sh/lua/merge+tables
    curl cht.sh/clojure/variadic+function
```

Se não gostar da resposta recebida, você pode escolher outra adicionando `/1`, `/2`, etc. ao final da consulta:

```
    curl cht.sh/python/random+string
    curl cht.sh/python/random+string/1
    curl cht.sh/python/random+string/2
```

Os cheat sheets são formatados como código da linguagem consultada (fazemos o possível para isso) para que possam ser colados diretamente no seu programa. Comentários em texto são formatados conforme a sintaxe da linguagem.

```lua
    $ curl cht.sh/lua/table+keys
    -- lua: retrieve list of keys in a table

    local keyset={}
    local n=0

    for k,v in pairs(tab) do
      n=n+1
      keyset[n]=k
    end

    --[[
       [ Note that you cannot guarantee any order in keyset. If you want the
       [ keys in sorted order, then sort keyset with table.sort(keyset).
       [ 
       [ [lhf] [so/q/12674345] [cc by-sa 3.0]
       ]]
```

Se não precisar dos comentários na resposta, é possível removê-los com a opção `\?Q`:

```lua
    $ curl cht.sh/lua/table+keys\?Q
    local keyset={}
    local n=0

    for k,v in pairs(tab) do
      n=n+1
      keyset[n]=k
    end
```

E para desativar o destaque de sintaxe, use `\?T`. Você pode combinar opções:

```
    curl cht.sh/go/reverse+a+list\?Q
    curl cht.sh/python/random+list+elements\?Q
    curl cht.sh/js/parse+json\?Q
    curl cht.sh/lua/merge+tables\?QT
    curl cht.sh/clojure/variadic+function\?QT
```

A lista completa de opções está detalhada abaixo e em `/:help`.

Siga estas regras ao realizar suas consultas:

1. Seja o mais específico possível (`/python/append+file` é melhor que `/python/file` e `/python/append`).
2. Faça perguntas práticas sempre que possível (embora perguntas teóricas também funcionem).
3. Faça apenas perguntas sobre linguagens de programação, especificando o nome da linguagem na seção.
4. Separe as palavras com `+` em vez de espaços.
5. Não use caracteres especiais, pois eles são ignorados.
6. Para excluir resultados com determinada palavra, adicione `+-` antes dela: `python/multiply+matrices+-numpy`

Leia mais sobre consultas de linguagens de programação abaixo.

---

## Cliente de linha de comando, cht.sh

O serviço cheat.sh possui um cliente próprio (`cht.sh`) que oferece recursos adicionais ao uso direto do `curl`:

* Modo shell especial com contexto de consultas persistente e suporte a readline.
* Histórico de consultas.
* Integração com a área de transferência.
* Autocompletar via Tab para shells (bash, fish, zsh).
* Modo stealth.

### Instalação

Para instalar o cliente:

```bash
PATH_DIR="$HOME/bin"  # ou outro diretório presente no seu $PATH
mkdir -p "$PATH_DIR"
curl https://cht.sh/:cht.sh > "$PATH_DIR/cht.sh"
chmod +x "$PATH_DIR/cht.sh"
```

ou para instalar globalmente (para todos os usuários):

```bash
curl -s https://cht.sh/:cht.sh | sudo tee /usr/local/bin/cht.sh && sudo chmod +x /usr/local/bin/cht.sh
```

Nota: O pacote "rlwrap" é uma dependência necessária para o modo shell. Instale usando `sudo apt install rlwrap`.

### Uso do cliente

Agora você pode usar `cht.sh` no lugar de `curl` e escrever consultas com espaços:

```
    $ cht.sh go reverse a list
    $ cht.sh python random list elements
    $ cht.sh js parse json
```

É ainda mais conveniente iniciar no modo shell:

```
    $ cht.sh --shell
    cht.sh> go reverse a list
```

Se todas as suas consultas forem sobre a mesma linguagem, mude o contexto para evitar repetir o nome da linguagem:

```
    $ cht.sh --shell
    cht.sh> cd go
    cht.sh/go> reverse a list
```

ou inicie o cliente já no contexto desejado:

```
    $ cht.sh --shell go
    cht.sh/go> reverse a list
    ...
    cht.sh/go> join a list
    ...
```

Para mudar de contexto use o comando `cd`. Para fazer uma consulta pontual em outra linguagem sem sair do contexto atual, adicione `/` no início:

```
    $ cht.sh --shell go
    ...
    cht.sh/go> /python dictionary comprehension
    ...
```

Para copiar a última resposta para a área de transferência, use `c` (`copy`) ou `C` (`ccopy`, sem comentários).

```
    cht.sh/python> append file
    #  python - How do you append to a file?

    with open("test.txt", "a") as myfile:
        myfile.write("appended text")
    cht.sh/python> C
    copy: 2 lines copied to the selection
```

Digite `help` para ver os comandos internos do `cht.sh`.

```
	cht.sh> help
	help    - exibe esta ajuda
	hush    - desativa a exibição da mensagem inicial de ajuda
	cd LANG - altera o contexto da linguagem
	copy    - copia a última resposta para a área de transferência (atalhos: yank, y, c)
	ccopy   - copia a última resposta sem comentários (atalhos: cc, Y, C)
	exit    - sai do cheat shell (atalhos: quit, ^D)
	id [ID] - define/exibe um ID de sessão único ("reset" para reiniciar, "remove" para remover)
	stealth - modo stealth (consultas automáticas do texto selecionado)
	update  - auto-atualização (apenas se o arquivo de script tiver permissão de escrita)
	version - exibe a versão atual do cht.sh
	/:help  - ajuda do serviço
	QUERY   - consulta separada por espaços (exemplos abaixo)
				  cht.sh> python zip list
				  cht.sh/python> zip list
				  cht.sh/go> /python zip list
```

O cliente `cht.sh` possui um arquivo de configuração localizado em `~/.cht.sh/cht.sh.conf` (o caminho pode ser sobrescrito pela variável de ambiente `CHTSH_CONF`). Use-o para definir opções padrão aplicadas a todas as consultas. Por exemplo, para desativar o destaque de sintaxe crie o arquivo com o seguinte conteúdo:

```bash
CHTSH_QUERY_OPTIONS="T"
```

Ou para usar um tema específico de destaque de sintaxe:

```bash
CHTSH_QUERY_OPTIONS="style=native"
```

(`curl cht.sh/:styles-demo` para ver todos os temas suportados).

Outros parâmetros de configuração do cht.sh:

```bash
CHTSH_CURL_OPTIONS="-A curl"        # opções do curl usadas nas consultas do cht.sh
CHTSH_URL=https://cht.sh            # URL do servidor cheat.sh
```

### Autocompletar (Tab completion)

#### Autocompletar no Bash

Para ativar o autocompletar no `cht.sh`, adicione o script `:bash_completion` ao seu `~/.bashrc`:

```bash
    curl https://cheat.sh/:bash_completion > ~/.bash.d/cht.sh
    . ~/.bash.d/cht.sh
    # e adicione . ~/.bash.d/cht.sh ao ~/.bashrc
```

#### Autocompletar no ZSH

Para ativar o autocompletar no `cht.sh`, adicione o script `:zsh` ao *fpath* no seu `~/.zshrc`:

```zsh
    curl https://cheat.sh/:zsh > ~/.zsh.d/_cht
    echo 'fpath=(~/.zsh.d/ $fpath)' >> ~/.zshrc
    # Abra um novo shell para carregar o plugin
```

---

### Modo stealth

Usar o recurso de forma totalmente imperceptível é um dos aspectos fundamentais do cheat.sh.

O cliente `cht.sh` possui um modo especial chamado **modo stealth**. Com ele, você não precisa sequer tocar no teclado para consultar um cheat sheet.

Neste modo, assim que um texto é selecionado com o mouse (entrando na seleção do X Window System ou na área de transferência), ele é enviado automaticamente como consulta ao cheat.sh e o resultado é exibido na tela.

Imagine uma entrevista técnica online onde o entrevistador faz perguntas em um documento compartilhado (como o Google Docs) e você deve escrever as respostas. Ao selecionar o texto da pergunta com o mouse, o cheat sheet correspondente é exibido automaticamente. Caso precise apenas do código sem explicações em texto, use a opção `Q` ao iniciar o modo stealth.

<p align="center">
  <img src='https://cheat.sh/files/stealth-mode.gif'/>
</p>

```
Você: Olá!                                          | $ cht.sh --shell python
Ela: Olá!                                           | cht.sh/python> stealth Q
Ela: Pronto para uma breve entrevista técnica?      | stealth: você está no modo stealth; selecione qualquer texto
Ela: Apenas algumas perguntas                       | stealth: seleções com mais de 5 palavras são ignoradas
Ela: Vamos falar sobre Python                       | stealth: argumentos da consulta: ?Q
Ela: Vamos começar com algo simples.                | stealth: use ^C para sair deste modo
Ela: Você sabe como inverter uma lista em Python?   |
Você: Com certeza                                   |
Você: (selecionando "reverse a list")               | stealth: reverse a list
                                                    | reverse_lst = lst[::-1]
Você: lst[::-1]?                                    |
Ela: Muito bem.                                     |
Ela: E como concatenar uma lista de listas?         |
Você: (selecionando "chain a list of lists")        | stealth: chain a list of lists
                                                    | import itertools
                                                    | a = [["a","b"], ["c"]]
                                                    | print list(itertools.chain.from_iterable(a))
Você: Posso usar módulos externos?                  |
Ela: Qual módulo você quer usar?                    |
Você: itertools                                     |
Ela: Sim, pode usar.                                |
Você: Certo, então:                                 |
Você: itertools.chain.from_iterable(a)              |
Ela: Ótimo. Vamos a algo mais avançado.             |
Ela: Como seria a implementação do quicksort?       |
Você: (selecionando "quicksort implementation")     | stealth: quicksort implementation
Você: Deixe-me pensar um pouco.                     | (exibe uma implementação longa e detalhada)
Você: Bom...(começando a digitar)                   | def sort(array=[12,4,5,6,7,3,1,15]):
                                                    |     less = []
Ela: (vendo seu código em estilo pascal)            |     equal = []
Ela: Consegue fazer de forma mais concisa?          |     greater = []
                                                    |     if len(array) > 1:
Você: Como assim?                                   |         pivot = array[0]
                                                    |         for x in array:
Ela: Quero dizer,                                   |             if x < pivot: less.append(x)
Ela: precisa mesmo de todos esses ifs e fors?       |             if x == pivot: equal.append(x)
Ela: Que tal usar filter?                           |             if x > pivot: greater.append(x)
                                                    |         return sort(less)+equal+sort(greater)
Você: quicksort com filter?                         |     else:
                                                    |         return array
Ela: Isso.                                          |
Você: (selecionando "quicksort with filter")        | stealth: quicksort with filter
Você: Certo, vou tentar.                            | return qsort(filter(lt, L[1:]))+[pivot] \
Você: Algo assim?                                   |     +qsort(filter(ge, L[1:]))
Você: qsort(filter(lt, L[1:]))+[pivot] \            |
       + qsort(filter(ge, L[1:]))                   |
                                                    |
Ela: Perfeito! Exatamente o que eu queria ver!      |
                                                    |
```

![quando você mente na entrevista](http://cheat.sh/files/when-you-lie-katze.png)

### Cliente de linha de comando para Windows

É possível acessar o cheat.sh também pelo terminal do Windows utilizando o cliente [`cht.exe`](https://github.com/tpanj/cht.exe). Ele oferece suporte a:

* Saída colorida.
* Opções de linha de comando.
* Arquivo de configuração próprio.

Também pode ser instalado via [`scoop`](https://github.com/lukesampson/scoop):

```batch
scoop install cht
```

---

## Hospedagem própria (Self-Hosting)

### Docker

Atualmente, a maneira mais fácil de executar uma instância local é utilizando o arquivo `docker-compose.yml`:

    docker-compose up

Isso compila e executa a imagem com os cheat sheets embutidos, iniciando a aplicação e uma instância do Redis para suporte no endereço http://localhost:8002. Esta implementação é inicial e recomendada prioritariamente para uso interno, pessoal ou de desenvolvimento.

## Integração com editores

Você pode usar o *cheat.sh* diretamente do seu editor (*Emacs*, *Sublime*, *Vim* e *Visual Studio Code* são suportados atualmente). Em vez de abrir o navegador, pesquisar, navegar no Stack Overflow e copiar trechos de código, é possível obter a resposta instantaneamente sem sair do ambiente de desenvolvimento.

Veja o funcionamento no Vim:

1. Ao ter uma dúvida durante a edição, digite a pergunta no buffer e pressione `<leader>KK` para abrir a resposta no pager (ou `<leader>KB` para abrir em um buffer separado).
2. Para colar a resposta, use `<leader>KP` (cola abaixo da pergunta) ou `<leader>KR` (substitui a pergunta). Para alternar a exibição de comentários, use `<leader>KC`.

Se você usa plugins de análise estática como o *syntastic* (para Vim), pode usar mensagens de aviso e erro como consultas no cheat.sh posicionando o cursor sobre a linha do problema e pressionando `<leader>KE`.

Recursos suportados pelos plugins em diferentes editores:

|Recurso            |Emacs|Sublime|Vim|VSCode|IDEA|QtCreator|
|-------------------|-----|-------|---|------|----|---------|
|Consultas por comando|✓    |✓      |✓  |✓     |✓   |✓        |
|Consultas do buffer|     |       |✓  |✓     |    |✓        |
|Alternar comentários|     |       |✓  |✓     |✓   |✓        |
|Resposta anterior/seguinte|     |       |✓  |✓     |✓   |✓        |
|Múltiplas respostas|     |✓      |   |      |✓   |         |
|Avisos como consultas|     |       |✓  |      |    |         |
|Histórico de consultas|     |       |✓  |✓     |    |         |
|ID de sessão       |     |       |✓  |      |    |         |
|Servidor configurável|✓    |       |✓  |✓     |    |✓        |

### Vim

* [cheat.sh-vim](https://github.com/dbeniamine/cheat.sh-vim) — Suporte ao Vim

Exemplo de configuração no Vim:

```vim
" configurações anteriores ...

let mapleader=" "

call vundle#begin()
Bundle 'gmarik/vundle'
Bundle 'scrooloose/syntastic'
Bundle 'dbeniamine/cheat.sh-vim'
call vundle#end()

let g:syntastic_javascript_checkers = [ 'jshint' ]
let g:syntastic_ocaml_checkers = ['merlin']
let g:syntastic_python_checkers = ['pylint']
let g:syntastic_shell_checkers = ['shellcheck']

" configurações posteriores ...
```

Assista à demonstração dos principais recursos do plugin para Vim (5 min):

<p align="center">
  <img src='https://cheat.sh/files/vim-demo.gif'/>
</p>

Ou assista no YouTube:

<p align="center">
  <a href="http://www.youtube.com/watch?feature=player_embedded&v=xyf6MJ0y-z8" target="_blank">
    <img src="http://img.youtube.com/vi/xyf6MJ0y-z8/0.jpg" alt="cheat.sh-vim: Uso no Vim" width="700" height="490" border="10" />
  </a>
</p>

### Emacs

* [cheat-sh.el](https://github.com/davep/cheat-sh.el) — Suporte ao Emacs (disponível também em cheat.sh/:emacs)
* cheat.sh/:emacs-ivy — Suporte ao Emacs para usuários do ivy

[![asciicast](https://asciinema.org/a/3xvqwrsu9g4taj5w526sb2t35.png)](https://asciinema.org/a/3xvqwrsu9g4taj5w526sb2t35)

### Visual Studio Code

* [vscode-snippet](https://github.com/mre/vscode-snippet)
* Instale pelo [VSCode Marketplace](https://marketplace.visualstudio.com/items?itemName=vscode-snippet.Snippet)

Uso:

1. Pressione <kbd>⌘ Command</kbd> + <kbd>⇧ Shift</kbd> + <kbd>p</kbd>
2. Execute `Snippet: Find`.
3. Digite a consulta e pressione Enter.

[![vscode-snippet](https://cheat.sh/files/vscode-snippet-demo.gif)](https://github.com/mre/vscode-snippet)

### Sublime

* [cheat.sh-sublime-plugin](https://github.com/gauravk-in/cheat.sh-sublime-plugin/)

Uso:

1. Digite o texto da consulta.
2. Selecione o texto.
3. Pressione <kbd>Cmd</kbd> + <kbd>⇧ Shift</kbd> + <kbd>B</kbd> para substituir o texto selecionado pela resposta do `cht.sh`.

[![cheat.sh-sublime-plugin-demo](https://cheat.sh/files/demo-sublime.gif)](https://github.com/gauravk-in/cheat.sh-sublime-plugin)

### IntelliJ IDEA

* [idea-cheatsh-plugin](https://github.com/szymonprz/idea-cheatsh-plugin)
* Instale pelo [Marketplace de plugins do IDEA](https://plugins.jetbrains.com/plugin/11942-cheat-sh-code-snippets)

Uso:

1. Digite a consulta.
2. Selecione o texto da consulta.
3. Pressione o atalho <kbd>Alt</kbd> + <kbd>C</kbd> , <kbd>S</kbd> para substituir a seleção pela resposta.

[![idea-cheatsh-plugin](https://cheat.sh/files/idea-demo.gif)](https://github.com/szymonprz/idea-cheatsh-plugin)

### QtCreator

* [cheatsh-qtcreator](https://github.com/pozemka/cheatsh-qtcreator)

Recursos atuais:

* Buscar palavra sob o cursor
* Buscar texto selecionado
* Busca por consulta
* Desativar comentários
* Colar resposta (versão ?TQ)
* URL de servidor personalizada
* Contexto de busca personalizado (padrão é cpp)
* Atalhos e menu

[![cheatsh-qtcreator](https://user-images.githubusercontent.com/1259724/73876361-ecce5d00-4867-11ea-9f75-c5b127a9739c.gif)](https://github.com/pozemka/cheatsh-qtcreator)

## Páginas especiais

Existem várias páginas especiais que não são cheat sheets. Seus nomes começam com dois-pontos e possuem significados específicos.

Primeiros passos:

```
    :help               descrição de todas as páginas especiais e opções
    :intro              introdução ao cheat.sh, cobrindo as principais dúvidas de uso
    :list               lista todos os cheat sheets (pode ser usado em subseções: /go/:list)
```

Cliente de linha de comando `cht.sh` e suporte a shells:

```
    :cht.sh             código-fonte do cliente cht.sh
    :bash_completion    função bash para autocompletar
    :bash               função e configuração de autocompletar para bash
    :fish               função e configuração de autocompletar para fish
    :zsh                função e configuração de autocompletar para zsh
```

Suporte a editores:

```
    :vim                suporte do cheat.sh para Vim
    :emacs              função do cheat.sh para Emacs
    :emacs-ivy          função do cheat.sh para Emacs (usando ivy)
```

Outras páginas:

```
    :post               como publicar um novo cheat sheet
    :styles             lista de esquemas de cores
    :styles-demo        exibe exemplos de uso dos esquemas de cores
    :random             busca uma página aleatória (pode ser usado em subseções: /go/:random)
```

## Busca

Para buscar por uma palavra-chave, use a consulta:

```
    /~palavra-chave
```

Neste caso a busca não é recursiva, sendo realizada apenas na página do nível especificado. Por exemplo:

```
    /~snapshot          busca "snapshot" nos cheat sheets de primeiro nível
    /scala/~currying     busca "currying" nos cheat sheets de Scala
```

Para busca recursiva em todos os cheat sheets, use duas barras:

```
    /~snapshot/r         busca "snapshot" em todos os cheat sheets
```

Opções de busca podem ser adicionadas após a barra final:

```
    /~shot/bi           insensível a maiúsculas/minúsculas (i), limites de palavra (b)
```

Lista de opções de busca:

```
    i   busca insensível a maiúsculas/minúsculas
    b   limites de palavra
    r   busca recursiva
```

## Cheat sheets de linguagens de programação

Os cheat sheets relativos a linguagens de programação são organizados em namespaces (subdiretórios) nomeados conforme a linguagem.

Para cada linguagem suportada existem páginas especiais: a página principal, `hello`, `:list` e `:learn`. Por exemplo, para Lua:

```
    lua
    lua/hello
    lua/:list
    lua/:learn
```

Algumas linguagens possuem a seção de uma linha, `1line`:

```
    perl/1line
```

* `hello` descreve como começar na linguagem (instalação, compilação, execução e o exemplo "Hello world").
* `:list` exibe todos os tópicos relacionados à linguagem.
* `:learn` exibe o cheat sheet no formato learn-x-in-minutes.
* `1line` é uma coleção de rotinas de uma linha na linguagem.
* `weirdness` reúne exemplos de comportamentos atípicos ou incomuns da linguagem.

![uso do cheat.sh](http://cheat.sh/files/supported-languages-c++.png)

Atualmente o cheat.sh cobre 58 linguagens de programação (em ordem alfabética):

|Prefixo    |Linguagem |Conceitos Básicos|Uma linha|Comportamentos Atípicos|StackOverflow|
|-----------|----------|-----------------|---------|-----------------------|-------------|
|`arduino/` |Arduino   |                 |         |                       |✓            |
|`assembly/`|Assembly  |                 |         |                       |✓            |
|`awk/`     |AWK       |✓                |         |                       |✓            |
|`bash/`    |Bash      |✓                |         |                       |✓            |
|`basic/`   |BASIC     |                 |         |                       |✓            |
|`bf/`      |Brainfuck |✓                |         |                       |✓            |
|`c/`       |C         |✓                |         |                       |✓            |
|`chapel/`  |Chapel    |✓                |         |                       |✓            |
|`clean/`   |Clean     |                 |         |                       |✓            |
|`clojure/` |Clojure   |✓                |         |                       |✓            |
|`coffee/`  |CoffeeScript|✓              |         |                       |✓            |
|`cpp/`     |C++       |✓                |         |                       |✓            |
|`csharp/`  |C#        |✓                |         |                       |✓            |
|`d/`       |D         |✓                |         |                       |✓            |
|`dart/`    |Dart      |✓                |         |                       |✓            |
|`delphi/`  |Delphi    |                 |         |                       |✓            |
|`dylan/`   |Dylan     |✓                |         |                       |✓            |
|`eiffel/`  |Eiffel    |                 |         |                       |✓            |
|`elixir/`  |Elixir    |✓                |         |                       |✓            |
|`elisp/`   |ELisp     |✓                |         |                       |✓            |
|`elm/`     |Elm       |✓                |         |                       |✓            |
|`erlang/`  |Erlang    |✓                |         |                       |✓            |
|`factor/`  |Factor    |✓                |         |                       |✓            |
|`fortran/` |Fortran   |✓                |         |                       |✓            |
|`forth/`   |Forth     |✓                |         |                       |✓            |
|`fsharp/`  |F#        |✓                |         |                       |✓            |
|`go/`      |Go        |✓                |         |                       |✓            |
|`groovy/`  |Groovy    |✓                |         |                       |✓            |
|`haskell/` |Haskell   |✓                |         |                       |✓            |
|`java/`    |Java      |✓                |         |                       |✓            |
|`js/`      |JavaScript|✓                |✓        |✓                      |✓            |
|`julia/`   |Julia     |✓                |         |                       |✓            |
|`kotlin/`  |Kotlin    |✓                |         |                       |✓            |
|`latex/`   |LaTeX     |✓                |         |                       |✓            |
|`lisp/`    |Lisp      |✓                |         |                       |✓            |
|`lua/`     |Lua       |✓                |         |                       |✓            |
|`matlab/`  |MATLAB    |✓                |         |                       |✓            |
|`nim/`     |Nim       |✓                |         |                       |✓            |
|`ocaml/`   |OCaml     |✓                |         |                       |✓            |
|`octave/`  |Octave    |✓                |         |                       |✓            |
|`perl/`    |Perl      |✓                |✓        |                       |✓            |
|`perl6/`   |Perl 6    |✓                |✓        |                       |✓            |
|`php/`     |PHP       |✓                |         |                       |✓            |
|`pike/`    |Pike      |                 |         |                       |✓            |
|`python/`  |Python    |✓                |✓        |                       |✓            |
|`python3/` |Python 3  |✓                |         |                       |✓            |
|`r/`       |R         |✓                |         |                       |✓            |
|`racket/`  |Racket    |✓                |         |                       |✓            |
|`ruby/`    |Ruby      |✓                |         |                       |✓            |
|`rust/`    |Rust      |✓                |         |                       |✓            |
|`scala/`   |Scala     |✓                |         |                       |✓            |
|`scheme/`  |Scheme    |✓                |         |                       |✓            |
|`solidity/`|Solidity  |✓                |         |                       |✓            |
|`swift/`   |Swift     |✓                |         |                       |✓            |
|`tcsh/`    |Tcsh      |✓                |         |                       |✓            |
|`tcl/`     |Tcl       |✓                |         |                       |✓            |
|`objective-c/`|Objective-C|✓            |         |                       |✓            |
|`vb/`      |VisualBasic|✓               |         |                       |✓            |
|`vbnet/`   |VB.Net    |✓                |         |                       |✓            |

Outros tópicos relacionados à programação:

|Prefixo    |Tópico    |Conceitos Básicos|StackOverflow|
|-----------|----------|-----------------|-------------|
|`cmake/`   |CMake     |✓                |✓            |
|`django/`  |Django    |                 |✓            |
|`flask/`   |Flask     |                 |✓            |
|`git/`     |Git       |✓                |✓            |

## Fontes dos cheat sheets

Focamos nossos esforços na criação de um mecanismo unificado de acesso a repositórios consolidados de cheat sheets sobre programação e sistemas operacionais.

O *cheat.sh* utiliza fontes mantidas por milhares de colaboradores ao redor do mundo:

| Cheat sheets            | Repositório                                                                         | C/U*                                                                                                                    | Estrelas                                                                                                 | Data de Criação |
|-------------------------|-------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------|-----------------|
| UNIX/Linux, programação | [cheat.sheets](https://github.com/chubin/cheat.sheets)                              | ![](https://img.shields.io/github/contributors-anon/chubin/cheat.sheets?label=%F0%9F%91%A5&labelColor=white)            | ![](https://img.shields.io/github/stars/chubin/cheat.sheets?label=%E2%AD%90&labelColor=white)            | 01/05/2017      |
| Comandos UNIX/Linux     | [tldr-pages/tldr](https://github.com/tldr-pages/tldr)                               | ![](https://img.shields.io/github/contributors-anon/tldr-pages/tldr?label=%F0%9F%91%A5&labelColor=white)                | ![](https://img.shields.io/github/stars/tldr-pages/tldr?label=%E2%AD%90&labelColor=white)                | 08/12/2013      |
| Comandos UNIX/Linux     | [cheat/cheat](https://github.com/cheat/cheat)                                       | ![](https://img.shields.io/github/contributors-anon/cheat/cheat?label=%F0%9F%91%A5&labelColor=white)                    | ![](https://img.shields.io/github/stars/cheat/cheat?label=%E2%AD%90&labelColor=white)                    | 28/07/2013      |
| Linguagens de programação| [adambard/learnxinyminutes-docs](https://github.com/adambard/learnxinyminutes-docs) | ![](https://img.shields.io/github/contributors-anon/adambard/learnxinyminutes-docs?label=%F0%9F%91%A5&labelColor=white) | ![](https://img.shields.io/github/stars/adambard/learnxinyminutes-docs?label=%E2%AD%90&labelColor=white) | 23/06/2013      |
| Go                      | [a8m/go-lang-cheat-sheet](https://github.com/a8m/go-lang-cheat-sheet)               | ![](https://img.shields.io/github/contributors-anon/a8m/go-lang-cheat-sheet?label=%F0%9F%91%A5&labelColor=white)        | ![](https://img.shields.io/github/stars/a8m/go-lang-cheat-sheet?label=%E2%AD%90&labelColor=white)        | 09/02/2014      |
| Perl                    | [pkrumnis/perl1line.txt](https://github.com/pkrumins/perl1line.txt)                 | ![](https://img.shields.io/github/contributors-anon/pkrumins/perl1line.txt?label=%F0%9F%91%A5&labelColor=white)         | ![](https://img.shields.io/github/stars/pkrumins/perl1line.txt?label=%E2%AD%90&labelColor=white)         | 04/11/2011      |
| Linguagens de programação| [StackOverflow](https://stackoverflow.com)                                          | [14M](https://stackexchange.com/leagues/1/alltime/stackoverflow)                                                        | N/A                                                                                                      | 15/09/2008      |

<sup>(*) C/U — Contribuidores para repositórios do GitHub, Usuários para o StackOverflow</sup>

Gráfico de pizza indicando a distribuição das fontes dos cheat sheets:

![repositórios de cheat sheets do cheat.sh](http://cheat.sh/files/stat-2017-06-05.png)

## Como contribuir

### Como editar um cheat sheet

Para editar um cheat sheet, as alterações devem ser feitas no repositório de origem (upstream). O nome do repositório original é exibido na parte inferior da página ao abrir o cheat sheet no navegador.

Você pode editar diretamente pelo navegador (requer conta no GitHub) usando o botão de edição no canto superior direito. Ao clicar, o editor será exibido para submissão das alterações via Pull Request.

![repositórios de cheat sheets do cheat.sh](http://cheat.sh/files/edit-cheat-sheet.png)

### Como adicionar um cheat sheet

Para incluir um novo cheat sheet, utilize um dos seguintes caminhos:

* Adicionar a um repositório externo compatível.
* Submeter ao repositório local do cheat.sh ([cheat.sheets](https://github.com/chubin/cheat.sheets)) no GitHub via fork e Pull Request.
* Publicar via curl ou navegador em ([cheat.sh/:post](http://cheat.sh/:post)).

### Como adicionar um repositório de cheat sheets

Para solicitar a inclusão de um novo repositório de cheat sheets, abra uma issue:

* [Adicionar novo repositório](https://github.com/chubin/cheat.sh/issues/new)

Informe o nome do repositório e uma breve descrição.

## Instalação e uso autônomo

Não é necessário instalar nada para usar o *cheat.sh*.

A instalação local é recomendada principalmente para:

1. Uso off-line (sem acesso à Internet).
2. Adição ou substituição por cheat sheets próprios.

O processo completo de instalação está detalhado em: [Instalação autônoma do cheat.sh](doc/standalone.md)