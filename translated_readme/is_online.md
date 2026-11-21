# is-online

> Verifica se a conexão com a internet está ativa

Funciona no Node.js e no navegador *(com o uso de um bundler)*.

No navegador, já existe o [`navigator.onLine`](https://developer.mozilla.org/en-US/docs/Web/API/NavigatorOnLine.onLine), porém ele é pouco útil, pois apenas indica se há uma conexão local estabelecida e não se a internet está realmente acessível.

## Instalação

```sh
npm install is-online
```

## Requisitos

- Node.js 20+
- Funciona em navegadores modernos quando empacotado (requer suporte à API `fetch`)

## Uso

```js
import isOnline from 'is-online';

console.log(await isOnline());
//=> true
```

### Com tempo limite (timeout)

```js
import isOnline from 'is-online';

console.log(await isOnline({timeout: 10_000}));
//=> true
```

### Com sinal de cancelamento (abort signal)

```js
import isOnline from 'is-online';

const controller = new AbortController();

setTimeout(() => {
	controller.abort();
}, 500);

const result = await isOnline({
	timeout: 3000,
	signal: controller.signal
});

console.log(result);
//=> false
```

### Com URLs de contingência (fallback)

```js
import isOnline from 'is-online';

const result = await isOnline({
	fallbackUrls: [
		'https://www.google.com',
		'https://www.github.com',
		'http://example.com'
	]
});

console.log(result);
//=> true
```

## API

### isOnline(options?)

Retorna uma `Promise<boolean>` que resolve para `true` se a conexão com a internet estiver ativa e `false` caso contrário.

#### options

Tipo: `object`

##### timeout

Tipo: `number`\
Padrão: `5000`

Milissegundos a aguardar pela resposta de um servidor.

##### signal

Tipo: `AbortSignal`

Um [`AbortSignal`](https://developer.mozilla.org/en-US/docs/Web/API/AbortSignal) para abortar a operação.

Quando o sinal for abortado, a promise será resolvida como `false`.

##### ipVersion

Tipo: `number`\
Valores: `4 | 6`\
Padrão: `4`

A [versão do Protocolo de Internet (IP)](https://pt.wikipedia.org/wiki/Internet_Protocol) a ser utilizada.

Esta é uma opção avançada que raramente precisa ser configurada, mas pode ser útil para validar especificamente a conectividade IPv6.

##### fallbackUrls

Tipo: `string[]`

URLs de contingência para testar a conectividade.

Apenas URLs HTTP e HTTPS são suportadas. No Node.js, essas URLs só são testadas caso todas as verificações padrão falhem. No navegador, essas URLs são testadas em paralelo com as verificações padrão para garantir maior resiliência contra bloqueadores de anúncios.

## Como funciona

As seguintes verificações são executadas em paralelo:

**Node.js:**
- Consulta a [icanhazip.com](https://github.com/major/icanhaz) (ou [ipify.org](https://www.ipify.org) como contingência) via HTTPS.
- Consulta as entradas DNS `myip.opendns.com` e `o-o.myaddr.l.google.com`.
- Consulta a página de teste de Portal Cativo da Apple (mecanismo utilizado pelo iOS).
- Verifica o website da Cloudflare via HTTPS.

**Navegador:**
- Consulta a [icanhazip.com](https://github.com/major/icanhaz) (ou [ipify.org](https://www.ipify.org) como contingência) via HTTPS.

Quando qualquer uma das verificações é bem-sucedida, a Promise é resolvida como `true`.

Se todas as verificações acima falharem e você tiver fornecido `fallbackUrls`, essas URLs serão consultadas. O teste é realizado via requisições HTTP/HTTPS (requisições HEAD sempre que possível, com fallback para GET).

## Diagnósticos

O pacote publica informações de diagnóstico em caso de falha nas verificações de conectividade utilizando o [Diagnostics Channel](https://nodejs.org/api/diagnostics_channel.html#diagnostics-channel) do Node.js. Isso é útil para depurar problemas de rede e está disponível apenas em ambientes Node.js.

```js
import {subscribe} from 'node:diagnostics_channel';
import isOnline from 'is-online';

// Inscrever-se nos eventos de falha
subscribe('is-online:connectivity-check', message => {
	console.log('URL com falha:', message.url);
	console.log('Erro:', message.error);
});

await isOnline();
```

Cada evento de falha inclui:
- `timestamp` - Momento em que a falha ocorreu
- `url` - A URL específica que falhou
- `error` - Detalhes do erro (nome, mensagem, código)

## Suporte a Proxy

Para funcionar através de proxies, é necessário configurar o [`global-agent`](https://github.com/gajus/global-agent).

## Mantenedores

- [Sindre Sorhus](https://github.com/sindresorhus)
- [silverwind](https://github.com/silverwind)

## Relacionados

- [is-online-cli](https://github.com/sindresorhus/is-online-cli) - CLI para este módulo
- [is-reachable](https://github.com/sindresorhus/is-reachable) - Verifica se servidores estão acessíveis