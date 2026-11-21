# Requests

**Requests** é uma biblioteca HTTP simples, porém elegante, desenvolvida em Python.

```python
>>> import requests
>>> r = requests.get('https://httpbin.org/basic-auth/user/pass', auth=('user', 'pass'))
>>> r.status_code
200
>>> r.headers['content-type']
'application/json; charset=utf8'
>>> r.encoding
'utf-8'
>>> r.text
'{"authenticated": true, ...'
>>> r.json()
{'authenticated': True, ...}
```

O Requests permite enviar requisições HTTP/1.1 de forma extremamente simples. Não há necessidade de adicionar query strings manualmente às suas URLs ou de codificar seus dados `PUT` e `POST` em formato de formulário — atualmente, basta utilizar o método `json`!

O Requests é um dos pacotes Python mais baixados da atualidade, alcançando cerca de `300 milhões de downloads / semana` — de acordo com o GitHub, mais de `4.000.000` de repositórios possuem [dependência direta](https://github.com/psf/requests/network/dependents?package_id=UGFja2FnZS01NzA4OTExNg%3D%3D) do Requests.

## Instalação e Versões Suportadas

O Requests está disponível no PyPI:

```console
$ python -m pip install requests
```

O Requests oferece suporte oficial ao Python 3.10+.

## Recursos Suportados e Boas Práticas

O Requests está preparado para atender às exigências de desenvolvimento de aplicações robustas e confiáveis que se comunicam via HTTP.

- Keep-Alive e Pool de Conexões (Connection Pooling)
- Domínios e URLs Internacionais
- Sessões com Persistência de Cookies
- Verificação TLS/SSL no estilo dos navegadores
- Autenticação Básica e Digest
- Cookies no formato familiar de dicionário (`dict`)
- Descompactação e Decodificação Automática de Conteúdo
- Upload de Arquivos em Múltiplas Partes (Multi-part)
- Suporte a Proxy SOCKS
- Timeouts de Conexão
- Downloads via Streaming
- Respeito automático às configurações do `.netrc`
- Requisições HTTP em Pedaços (Chunked HTTP Requests)

## Clonando o repositório

Ao clonar o repositório do Requests, pode ser necessário adicionar a flag `-c fetch.fsck.badTimezone=ignore` para evitar erros relacionados a timestamps de commit inválidos (consulte [esta issue](https://github.com/psf/requests/issues/2690) para mais contexto):

```shell
git clone -c fetch.fsck.badTimezone=ignore https://github.com/psf/requests.git
```

Você também pode aplicar essa configuração globalmente no seu Git:

```shell
git config --global fetch.fsck.badTimezone ignore
```