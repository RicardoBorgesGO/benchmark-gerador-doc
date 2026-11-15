# body-parser

[![NPM Version][npm-version-image]][npm-url]
[![NPM Downloads][npm-downloads-image]][npm-url]
[![Build Status][ci-image]][ci-url]
[![Test Coverage][coveralls-image]][coveralls-url]
[![OpenSSF Scorecard Badge][ossf-scorecard-badge]][ossf-scorecard-visualizer]

Middleware de parsing de corpo para Node.js.

Realiza o parse dos corpos de requisições recebidas em um middleware antes dos seus manipuladores (handlers), disponibilizando os dados na propriedade `req.body`.

**Nota** Como o formato de `req.body` é baseado em dados fornecidos pelo usuário, todas as propriedades e valores neste objeto devem ser considerados não confiáveis e precisam ser validados antes do uso. Por exemplo, `req.body.foo.toString()` pode falhar de várias maneiras, como a propriedade `foo` não existir, não ser uma string, ou `toString` não ser uma função e sim uma string ou outro tipo de dado enviado pelo usuário.

[Saiba mais sobre a anatomia de uma transação HTTP no Node.js](https://nodejs.org/en/learn/http/anatomy-of-an-http-transaction).

_Este módulo não lida com corpos multipart_, devido à sua natureza complexa e tipicamente grande. Para corpos multipart, você pode se interessar pelos seguintes módulos:

  * [busboy](https://www.npmjs.com/package/busboy#readme) e [connect-busboy](https://www.npmjs.com/package/connect-busboy#readme)
  * [multiparty](https://www.npmjs.com/package/multiparty#readme) e [connect-multiparty](https://www.npmjs.com/package/connect-multiparty#readme)
  * [formidable](https://www.npmjs.com/package/formidable#readme)
  * [multer](https://www.npmjs.com/package/multer#readme)

Este módulo fornece os seguintes parsers:

  * [Parser de corpo JSON](#bodyparserjsonoptions)
  * [Parser de corpo Raw](#bodyparserrawoptions)
  * [Parser de corpo Texto](#bodyparsertextoptions)
  * [Parser de corpo URL-encoded](#bodyparserurlencodedoptions)

Todos os parsers suportam descompactação automática das codificações `gzip`, `br` (brotli), `deflate` e `zstd`. O suporte a `zstd` está disponível no Node.js a partir das versões `^22.15.0` e `>=23.8.0`.

Outros parsers de corpo que podem ser do seu interesse:

- [body](https://www.npmjs.com/package/body#readme)
- [co-body](https://www.npmjs.com/package/co-body#readme)

## Instalação

```sh
$ npm install body-parser
```

## API

```js
// Importa todos os parsers
const bodyParser = require('body-parser')

// Ou importa parsers individuais diretamente
const json = require('body-parser/json')
const urlencoded = require('body-parser/urlencoded')
const raw = require('body-parser/raw')
const text = require('body-parser/text')
```

O objeto `bodyParser` expõe várias funções factory para criar middlewares. Todos os middlewares preenchem a propriedade `req.body` com o corpo analisado quando o cabeçalho `Content-Type` da requisição corresponde à opção `type`.

**Nota** A partir da v2, `req.body` permanece como `undefined` quando nenhum corpo é analisado (por exemplo, quando a requisição não possui `Content-Length` nem `Transfer-Encoding`, ou quando o `Content-Type` não corresponde). Na v1, `req.body` era sempre inicializado como `{}`. Códigos que assumem que `req.body` é sempre um objeto devem usar encadeamento opcional (por exemplo, `req.body?.username`) ou definir um valor padrão.

Os diversos erros retornados por este módulo estão descritos na [seção de erros](#erros).

### bodyParser.json([options])

Retorna um middleware que analisa apenas o formato `json` e analisa requisições cujo cabeçalho `Content-Type` corresponda à opção `type`. Este parser aceita qualquer codificação Unicode no corpo da requisição.

Um novo objeto `body` contendo os dados analisados é populado no objeto `request` após a execução do middleware (ou seja, `req.body`).

#### Opções

A função `json` aceita um objeto opcional `options` que pode conter qualquer uma das seguintes chaves:

##### defaultCharset

Especifica o conjunto de caracteres padrão para o conteúdo json caso o charset não seja especificado no cabeçalho `Content-Type` da requisição. O valor padrão é `utf-8`.

##### inflate

Quando definido como `true`, corpos compactados serão descompactados; quando `false`, corpos compactados serão rejeitados. O valor padrão é `true`.

##### limit

Controla o tamanho máximo do corpo da requisição. Se for um número, especifica a quantidade de bytes; se for uma string, o valor é passado para a biblioteca [bytes](https://www.npmjs.com/package/bytes) para parsing. O valor padrão é `'100kb'`.

> Recomenda-se não configurar um limite muito alto e usar o valor padrão sempre que possível. Permitir payloads maiores aumenta o uso de memória devido aos recursos necessários para decodificação e transformações, além de poder levar a tempos de resposta mais longos à medida que mais dados são processados. Por 'muito alto', entende-se valores acima do padrão, como payloads de 5 MB ou mais, que já podem introduzir esses riscos. Com os limites padrão, esses problemas não ocorrem.

##### reviver

A opção `reviver` é passada diretamente para `JSON.parse` como o segundo argumento. Você pode encontrar mais informações sobre este argumento [na documentação MDN sobre JSON.parse](https://developer.mozilla.org/pt-BR/docs/Web/JavaScript/Reference/Global_Objects/JSON/parse#o_parâmetro_reviver).

##### strict

Quando definido como `true`, aceita apenas arrays e objetos; quando `false`, aceita qualquer valor válido para `JSON.parse`. O valor padrão é `true`.

##### type

A opção `type` é usada para determinar qual tipo de mídia o middleware irá analisar. Esta opção pode ser uma string, um array de strings ou uma função. Se não for uma função, a opção `type` é passada diretamente para a biblioteca [type-is](https://www.npmjs.com/package/type-is#readme), podendo ser um nome de extensão (como `json`), um tipo MIME (como `application/json`), ou um tipo MIME com caractere curinga (como `*/*` ou `*/json`). Se for uma função, a opção `type` é chamada como `fn(req)` e a requisição é analisada se ela retornar um valor verdadeiro. O valor padrão é `application/json`.

##### verify

A opção `verify`, se fornecida, é chamada como `verify(req, res, buf, encoding)`, onde `buf` é um `Buffer` do corpo bruto da requisição e `encoding` é a codificação da requisição. O parsing pode ser abortado lançando um erro.

### bodyParser.raw([options])

Retorna um middleware que analisa todos os corpos como um `Buffer` e analisa apenas requisições cujo cabeçalho `Content-Type` corresponda à opção `type`.

Um novo objeto `body` contendo os dados analisados é populado no objeto `request` após o middleware (ou seja, `req.body`). Este será um objeto `Buffer` contendo o corpo.

#### Opções

A função `raw` aceita um objeto opcional `options` que pode conter qualquer uma das seguintes chaves:

##### inflate

Quando definido como `true`, corpos compactados serão descompactados; quando `false`, corpos compactados serão rejeitados. O valor padrão é `true`.

##### limit

Controla o tamanho máximo do corpo da requisição. Se for um número, especifica o número de bytes; se for uma string, o valor é passado para a biblioteca [bytes](https://www.npmjs.com/package/bytes) para parsing. O valor padrão é `'100kb'`.

> Recomenda-se não configurar um limite muito alto e usar o valor padrão sempre que possível. Permitir payloads maiores aumenta o uso de memória devido aos recursos necessários para decodificação e transformações, além de poder levar a tempos de resposta mais longos à medida que mais dados são processados. Por 'muito alto', entende-se valores acima do padrão, como payloads de 5 MB ou mais, que já podem introduzir esses riscos. Com os limites padrão, esses problemas não ocorrem.

##### type

A opção `type` é usada para determinar qual tipo de mídia o middleware irá analisar. Esta opção pode ser uma string, array de strings ou uma função. Se não for uma função, a opção `type` é passada diretamente para a biblioteca [type-is](https://www.npmjs.com/package/type-is#readme), podendo ser um nome de extensão (como `bin`), um tipo MIME (como `application/octet-stream`), ou um tipo MIME com caractere curinga (como `*/*` ou `application/*`). Se for uma função, a opção `type` é chamada como `fn(req)` e a requisição é analisada se retornar um valor verdadeiro. O valor padrão é `application/octet-stream`.

##### verify

A opção `verify`, se fornecida, é chamada como `verify(req, res, buf, encoding)`, onde `buf` é um `Buffer` do corpo bruto da requisição e `encoding` é a codificação da requisição. O parsing pode ser abortado lançando um erro.

### bodyParser.text([options])

Retorna um middleware que analisa todos os corpos como uma string e analisa apenas requisições cujo cabeçalho `Content-Type` corresponda à opção `type`.

Uma nova string `body` contendo os dados analisados é populada no objeto `request` após o middleware (ou seja, `req.body`). Esta será uma string contendo o corpo da requisição.

#### Opções

A função `text` aceita um objeto opcional `options` que pode conter qualquer uma das seguintes chaves:

##### defaultCharset

Especifica o conjunto de caracteres padrão para o conteúdo de texto caso o charset não seja especificado no cabeçalho `Content-Type` da requisição. O valor padrão é `utf-8`.

##### inflate

Quando definido como `true`, corpos compactados serão descompactados; quando `false`, corpos compactados serão rejeitados. O valor padrão é `true`.

##### limit

Controla o tamanho máximo do corpo da requisição. Se for um número, especifica o número de bytes; se for uma string, o valor é passado para a biblioteca [bytes](https://www.npmjs.com/package/bytes) para parsing. O valor padrão é `'100kb'`.

> Recomenda-se não configurar um limite muito alto e usar o valor padrão sempre que possível. Permitir payloads maiores aumenta o uso de memória devido aos recursos necessários para decodificação e transformações, além de poder levar a tempos de resposta mais longos à medida que mais dados são processados. Por 'muito alto', entende-se valores acima do padrão, como payloads de 5 MB ou mais, que já podem introduzir esses riscos. Com os limites padrão, esses problemas não ocorrem.

##### type

A opção `type` é usada para determinar qual tipo de mídia o middleware irá analisar. Esta opção pode ser uma string, array de strings ou uma função. Se não for uma função, a opção `type` é passada diretamente para a biblioteca [type-is](https://www.npmjs.com/package/type-is#readme), podendo ser um nome de extensão (como `txt`), um tipo MIME (como `text/plain`), ou um tipo MIME com caractere curinga (como `*/*` ou `text/*`). Se for uma função, a opção `type` é chamada como `fn(req)` e a requisição é analisada se retornar um valor verdadeiro. O valor padrão é `text/plain`.

##### verify

A opção `verify`, se fornecida, é chamada como `verify(req, res, buf, encoding)`, onde `buf` é um `Buffer` do corpo bruto da requisição e `encoding` é a codificação da requisição. O parsing pode ser abortado lançando um erro.

### bodyParser.urlencoded([options])

Retorna um middleware que analisa apenas corpos `urlencoded` e analisa apenas requisições cujo cabeçalho `Content-Type` corresponda à opção `type`. Este parser aceita apenas as codificações UTF-8 e ISO-8859-1 para o corpo.

Um novo objeto `body` contendo os dados analisados é populado no objeto `request` após o middleware (ou seja, `req.body`). Este objeto conterá pares chave-valor, onde o valor pode ser uma string ou array (quando `extended` for `false`), ou qualquer tipo (quando `extended` for `true`).

#### Opções

A função `urlencoded` aceita um objeto opcional `options` que pode conter qualquer uma das seguintes chaves:

##### extended

A sintaxe "extended" permite que objetos complexos e arrays sejam codificados no formato URL-encoded, oferecendo uma experiência semelhante ao JSON com URL-encoded. Para mais informações, consulte a [biblioteca qs](https://www.npmjs.com/package/qs#readme).

O valor padrão é `false`.

##### inflate

Quando definido como `true`, corpos compactados serão descompactados; quando `false`, corpos compactados serão rejeitados. O valor padrão é `true`.

##### limit

Controla o tamanho máximo do corpo da requisição. Se for um número, especifica a quantidade de bytes; se for uma string, o valor é passado para a biblioteca [bytes](https://www.npmjs.com/package/bytes) para parsing. O valor padrão é `'100kb'`.

> Recomenda-se não configurar um limite muito alto e usar o valor padrão sempre que possível. Permitir payloads maiores aumenta o uso de memória devido aos recursos necessários para decodificação e transformações, além de poder levar a tempos de resposta mais longos à medida que mais dados são processados. Por 'muito alto', entende-se valores acima do padrão, como payloads de 5 MB ou mais, que já podem introduzir esses riscos. Com os limites padrão, esses problemas não ocorrem.

##### parameterLimit

A opção `parameterLimit` controla a quantidade máxima de parâmetros permitidos nos dados URL-encoded. Se uma requisição mantiver mais parâmetros do que este valor, um código 413 será retornado ao cliente. O valor padrão é `1000`.

##### type

A opção `type` é usada para determinar qual tipo de mídia o middleware irá analisar. Esta opção pode ser uma string, array de strings ou uma função. Se não for uma função, a opção `type` é passada diretamente para a biblioteca [type-is](https://www.npmjs.com/package/type-is#readme), podendo ser um nome de extensão (como `urlencoded`), um tipo MIME (como `application/x-www-form-urlencoded`), ou um tipo MIME com caractere curinga (como `*/x-www-form-urlencoded`). Se for uma função, a opção `type` é chamada como `fn(req)` e a requisição é analisada se retornar um valor verdadeiro. O valor padrão é `application/x-www-form-urlencoded`.

##### verify

A opção `verify`, se fornecida, é chamada como `verify(req, res, buf, encoding)`, onde `buf` é um `Buffer` do corpo bruto da requisição e `encoding` é a codificação da requisição. O parsing pode ser abortado lançando um erro.

##### defaultCharset

O charset padrão para o parsing, caso não seja especificado no Content-Type. Deve ser `utf-8` ou `iso-8859-1`. O valor padrão é `utf-8`.

##### charsetSentinel

Define se o valor do parâmetro `utf8` deve ter precedência como seletor de charset. Requer que o formulário contenha um parâmetro chamado `utf8` com o valor `✓`. O valor padrão é `false`.

##### interpretNumericEntities

Define se entidades numéricas como `&#9786;` devem ser decodificadas ao analisar um formulário iso-8859-1. O valor padrão é `false`.

##### depth

A opção `depth` é usada para configurar a profundidade máxima da biblioteca `qs` quando `extended` estiver definido como `true`. Isso permite limitar a quantidade de chaves analisadas, sendo útil para prevenir certos tipos de abuso. O valor padrão é `32`. Recomenda-se manter este valor o mais baixo possível.

## Erros

Os middlewares fornecidos por este módulo criam erros utilizando o módulo [`http-errors`](https://www.npmjs.com/package/http-errors). Os erros geralmente possuem uma propriedade `status`/`statusCode` contendo o código de resposta HTTP sugerido, uma propriedade `expose` para determinar se a propriedade `message` deve ser exibida ao cliente, uma propriedade `type` para determinar o tipo do erro sem a necessidade de comparar a `message`, e uma propriedade `body` contendo o corpo lido, quando disponível.

Abaixo estão os erros comuns gerados pelo módulo, embora qualquer erro possa ocorrer por razões diversas.

### content encoding unsupported

Este erro ocorre quando a requisição possui um cabeçalho `Content-Encoding` com uma codificação definida, mas a opção "inflate" foi configurada como `false`. A propriedade `status` é definida como `415`, a propriedade `type` como `'encoding.unsupported'` e a propriedade `charset` conterá a codificação não suportada.

### entity parse failed

Este erro ocorre quando a requisição contém uma entidade que não pôde ser analisada pelo middleware. A propriedade `status` é definida como `400`, a propriedade `type` como `'entity.parse.failed'` e a propriedade `body` conterá a entidade que falhou no parsing.

### entity verify failed

Este erro ocorre quando a requisição contém uma entidade que não pôde ser verificada pela opção `verify` definida. A propriedade `status` é definida como `403`, a propriedade `type` como `'entity.verify.failed'` e a propriedade `body` conterá a entidade que falhou na verificação.

### request aborted

Este erro ocorre quando a requisição é abortada pelo cliente antes que a leitura do corpo seja finalizada. A propriedade `received` conterá a quantidade de bytes recebidos antes do cancelamento e a propriedade `expected` conterá o número de bytes esperados. A propriedade `status` é definida como `400` e a propriedade `type` como `'request.aborted'`.

### request entity too large

Este erro ocorre quando o tamanho do corpo da requisição é maior do que a opção "limit". A propriedade `limit` conterá o limite em bytes e a propriedade `length` conterá o tamanho real do corpo. A propriedade `status` é definida como `413` e a propriedade `type` como `'entity.too.large'`.

### request size did not match content length

Este erro ocorre quando o tamanho da requisição não corresponde ao valor indicado no cabeçalho `Content-Length`. Isso costuma acontecer quando a requisição está malformada, como nos casos em que o cabeçalho `Content-Length` foi calculado com base em caracteres em vez de bytes. A propriedade `status` é definida como `400` e a propriedade `type` como `'request.size.invalid'`.

### stream encoding should not be set

Este erro ocorre quando algum código chama o método `req.setEncoding` antes da execução deste middleware. Este módulo opera diretamente sobre bytes e não é permitido chamar `req.setEncoding` ao utilizá-lo. A propriedade `status` é definida como `500` e a propriedade `type` como `'stream.encoding.set'`.

### stream is not readable

Este erro ocorre quando a requisição deixa de ser legível no momento em que este middleware tenta lê-la. Isso geralmente indica que outro middleware (não pertencente a este módulo) já leu o corpo da requisição e o middleware atual também estava configurado para a mesma leitura. A propriedade `status` é definida como `500` e a propriedade `type` como `'stream.not.readable'`.

### too many parameters

Este erro ocorre quando o conteúdo da requisição excede o valor configurado em `parameterLimit` para o parser `urlencoded`. A propriedade `status` é definida como `413` e a propriedade `type` como `'parameters.too.many'`.

### unsupported charset "BOGUS"

Este erro ocorre quando a requisição contém um parâmetro de charset no cabeçalho `Content-Type`, mas a biblioteca `iconv-lite` não o suporta OU o parser não o suporta. O charset é informado na mensagem e na propriedade `charset`. A propriedade `status` é definida como `415`, a propriedade `type` como `'charset.unsupported'` e a propriedade `charset` conterá o charset não suportado.

### unsupported content encoding "bogus"

Este erro ocorre quando a requisição possui um cabeçalho `Content-Encoding` contendo uma codificação não suportada. A codificação é informada na mensagem e na propriedade `encoding`. A propriedade `status` é definida como `415`, a propriedade `type` como `'encoding.unsupported'` e a propriedade `encoding` conterá a codificação não suportada.

### The input exceeded the depth

Este erro ocorre ao utilizar `bodyParser.urlencoded` com a propriedade `extended` definida como `true` e a entrada exceder a opção `depth` configurada. A propriedade `status` é definida como `400`. Recomenda-se revisar a opção `depth` e avaliar a necessidade de um valor maior. Com o padrão de `depth` igual a `32`, entradas com 33 ou mais níveis de aninhamento receberão este erro.

## Exemplos

### Genérico de nível superior no Express/Connect

Este exemplo demonstra a adição de um parser genérico para JSON e URL-encoded como middleware de nível superior, que analisará o corpo de todas as requisições recebidas. Esta é a configuração mais simples.

```js
const express = require('express')
const bodyParser = require('body-parser')

const app = express()

// parse application/x-www-form-urlencoded
app.use(bodyParser.urlencoded())

// parse application/json
app.use(bodyParser.json())

app.use(function (req, res) {
  res.setHeader('Content-Type', 'text/plain')
  res.write('you posted:\n')
  res.end(String(JSON.stringify(req.body, null, 2)))
})
```

### Específico por rota no Express

Este exemplo demonstra a adição de parsers de corpo especificamente nas rotas que necessitam deles. Em geral, esta é a forma mais recomendada de utilizar o `body-parser` com Express.

```js
const express = require('express')
const bodyParser = require('body-parser')

const app = express()

// cria o parser application/json
const jsonParser = bodyParser.json()

// cria o parser application/x-www-form-urlencoded
const urlencodedParser = bodyParser.urlencoded()

// POST /login recebe corpos urlencoded
app.post('/login', urlencodedParser, function (req, res) {
  if (!req.body || !req.body.username) res.sendStatus(400)
  res.send('welcome, ' + req.body.username)
})

// POST /api/users recebe corpos JSON
app.post('/api/users', jsonParser, function (req, res) {
  if (!req.body) res.sendStatus(400)
  // cria usuário em req.body
})
```

### Alterar tipo aceito pelos parsers

Todos os parsers aceitam a opção `type`, permitindo alterar o `Content-Type` que o middleware irá analisar.

```js
const express = require('express')
const bodyParser = require('body-parser')

const app = express()

// analisa vários tipos JSON personalizados diferentes como JSON
app.use(bodyParser.json({ type: 'application/*+json' }))

// analisa algum formato personalizado como Buffer
app.use(bodyParser.raw({ type: 'application/vnd.custom-type' }))

// analisa um corpo HTML como string
app.use(bodyParser.text({ type: 'text/html' }))
```

## Licença

[MIT](LICENSE)

[ci-image]: https://img.shields.io/github/actions/workflow/status/expressjs/body-parser/ci.yml?branch=master&label=ci
[ci-url]: https://github.com/expressjs/body-parser/actions/workflows/ci.yml
[coveralls-image]: https://img.shields.io/coverallsCoverage/github/expressjs/body-parser?branch=master
[coveralls-url]: https://coveralls.io/r/expressjs/body-parser?branch=master
[npm-downloads-image]: https://img.shields.io/npm/dm/body-parser
[npm-url]: https://npmjs.com/package/body-parser
[npm-version-image]: https://img.shields.io/npm/v/body-parser
[ossf-scorecard-badge]: https://api.scorecard.dev/projects/github.com/expressjs/body-parser/badge
[ossf-scorecard-visualizer]: https://ossf.github.io/scorecard-visualizer/#/projects/github.com/expressjs/body-parser