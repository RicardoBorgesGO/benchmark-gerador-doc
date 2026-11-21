[(experimente aqui)](https://obamify.com/)

# obamify

Nova tecnologia revolucionária que transforma qualquer imagem no Obama.

# Como usar

**Use a interface no topo da janela para controlar a animação, escolher entre transformações salvas e gerar novas.** É possível alterar a imagem de origem e a imagem de destino, além de escolher como elas serão cortadas em formato quadrado (dica: se ambas as imagens forem rostos, tente fazer os olhos se sobreporem). Você também pode alterar estas configurações avançadas:

| Configuração | Descrição |
| --- | --- |
| resolução | Em quantas células as imagens serão divididas. Resoluções mais altas capturam mais detalhes de alta frequência. |
| importância da proximidade | O quanto o algoritmo altera a imagem original para fazê-la parecer com a imagem de destino. Aumente este valor se desejar uma transformação mais sutil. |
| algoritmo | O algoritmo usado para calcular a atribuição de cada pixel. O método Ótimo (Optimal) encontrará a solução matematicamente ideal, porém é extremamente lento para resoluções altas. |

# Instalação

Baixe a versão mais recente na seção de [releases](https://github.com/Spu7Nix/obamify/releases). Descompacte e execute o arquivo .exe contido na pasta!

**Nota para usuários do macOS:**
Execute `xattr -C <caminho/para/app.app>` no seu terminal para remover o aviso de aplicativo danificado.

### Compilando a partir do código-fonte

1. Instale o [Rust](https://www.rust-lang.org/tools/install)

2. Execute `cargo run --release` na pasta do projeto

#### Executando a versão web localmente

1. Instale o [Rust](https://www.rust-lang.org/tools/install)

2. Instale o target necessário com `rustup target add wasm32-unknown-unknown`

3. Instale o Trunk com `cargo install --locked trunk`

4. Execute `trunk serve --release --open`

# Como contribuir

Abra uma issue ou um pull request caso tenha sugestões ou encontre algum problema :)

# Como funciona

mágica