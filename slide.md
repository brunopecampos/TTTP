---
author:
  - André Souza Abreu
  - Bruno Pereira Campos
date: 04/06/2022
title: MAC0352 — EP 2
theme: Copenhagen
fonttheme: structurebold
---

# TTTP

Para implementar o jogo da velha utilizando um sistema hibrído (P2P +
client-servidor) criamos o TTTP — TikTakToe Protocol (_Protocolo do Jogo da
Velha_).

Todas as mensagens trocadas (servidor-cliente, cliente-cliente) são em
_plain text_. Existem dois tipos de mensagens: `requests` (requisições)
e `replies` (respostas).

O protocolo foi implementado totalmente em `Python` por ser uma linguagem
de desenvolvimento rápido e com suporte de várias bibliotecas, tais como
`API` de sockets, `threading`, manipulação de arquivos, etc.

\footnotesize

**Nota**: pelo fato de ser _plaintext_, é possível olhar as mensagens no
_Wireshark_ e até mesmo simular um cliente TCP usando o _telnet_ (basta saber o
protocolo).

# requests

Os `requests`, também chamado de comandos, seguem sempre o seguinte formato:

```
<CMD> <ARGS>
```

Onde `CMD` é um comando de 4 letras (para facilitar a padronização) e
`ARGS` são o conjunto de argumentos (se houver) passado junto com o comando.

Alguns comandos (`HELO`, `PING`, `PINL`) não precisam de argumentos, já outros
precisam de um ou mais argumentos, os quais devem ser separados por **espaços**
e devem conter **somente** caracteres ASCII.

# replies

Já os `replies` seguem o formato:

```
<CMD> <RETURN CODE>
<PAYLOAD>
```

Onde `CMD` é o comando original, `RETURN CODE` é um código (inteiro) utilizado
para indicar o _status_ da requisição, e `PAYLOAD` contém dados da resposta.
Apenas alguns comandos devolvem um _payload_:

- `MSTR` devolve o ID da partida para ser usado posteriormente pelo cliente para
  especificar o resultado da partida
- `GTIP` devolve o endereço do usuário usado para partidas.
- `UHOF` lista a pontuação dos usuários, um por lista.
- `USRL` devolve a lista de usuários conectados, 1 usuário por linha.

# códigos

Nós nos baseamos nos `status code` do protocolo _HTTP_ e eis alguns códigos:

- **200**: sucesso ao executar o comando
- **201**: comando executado resultou em um novo recurso
- **400**: comando mal formatado
- **401**: usuário não autentificado
- **403**: ação proibida
- **404**: recurso não encontrado

Neste contexto _recurso_ significa um _usuário_ ou _match_ (partida).
Alguns exemplos de mensagens:

# exemplos de requisições

\small

- `HELO`: Handshake usado para iniciar comunicação (_Hello_)
- `PING`: Ping utilizado para _heartbeat_
- `PINL`: Ping utilizado para medir latência (_PING Latency_)
- `USRL`: Lista usuários ativos (_User List_)
- `NUSR <USER> <PASS>`: Cria novo usuário (_New User_)
- `LOGN <USER> <PASS>`: Usuário entra (_Log In_)
- `LOUT`: Usuário sai (_Log Out_)
- `CPWD <OLD> <NEW>`: Muda a senha (_Change Password_)
- `MSTR <OPPONENT>`: Início de partida (_Match Start_)
- `MEND <ID> <WINNER>`: Resultado da partida `<ID>` (_Match End_)
- `GBYE`: Desconecta clinete (_Good Bye_)
- `GTIP <USER>`: Obtém IP e porta de outro usuário (_Get IP_)
- `SADR <PORT>`: Cliente anuncia sua porta (_Set Address_)
- `UHOF`: Lista pontuação dos usuários (_User Hall Of Fame_)

# Mensagens

Alguns comandos só podem ser executado se o usuário estiver logado (`CPWD`,
`MSTR`, `LOUT`), deslogado (`LOGN`, `GBYE`), ou jogando (`MEND`). Para isso,
utilizamos máquinas de estados no servidor e no cliente, as quais indicam se o
comando pode ou não ser executado.

Algumas mensagens são enviadas no _background_ (`HELO`, `PING`, `PINL`, `SADR`,
`GTIP`) sem a intervenção do usuáiro. Na verdade, estas mensagens não podem ser
enviadas pelo usuário.

Em vez disso, os comandos digitados pelo usuários são transformados em
mensagens especificadas pelo protocolo. Estes comandos adotam a especificação
que está no PDF do enunciado deste EP.

# Ciclo de vida do cliente

Após o cliente inciar sua conexão com o servidor, ele envia as mensagens `HELO`
(handshake) e `SADR` (especificação da porta pública do cliente para partidas).
O cliente então entra em modo REPL (_Read-Eval-Print Loop_), recebendo comandos
do usuário e devolvendo respostas.

O cliente envia no background um _PING_ para o servidor a cada 2 minutos para
indicar que ainda está ativo. Durante uma partida, há algo semelhante: o
cliente envia uma requisição _PINL_ para o outro cliente para medir a latência.

A partir daí o comportamento do cliente dependerá dos comandos do usuário,
que poderá criar novos usuários, logar/deslogar, mudar a senha do próprio
usuário, listas os usuários ativos, listas a pontuação dos usuários, entrar
numa partida, sair do programa.

# Partidas

Para iniciar uma partida, o cliente envia um `GTIP` ao servidor para conseguir o
endereço público de partida do oponente. Então, envia uma requisição `CALL` para
chamar o cliente para a partida (que pode ser aceita ou recusada).

Se for aceita, ambos os clientes trocaram mensagens até a partida a acabar,
enviando o tabuleiro e suas jogadas.

O cliente que chama a partida é sempre o jogador X (jogador 1) e é ele que deverá
informar o resultado para o servidor.

Caso o servidor tenha caído durante este intervalo, o cliente tentará
reconectar-se com o servidor para enviar uma mensagem informando o ganhador da
partida. Esta tentativa de reconexão durará no máximo 3 minutos (do contrário,
o cliente desiste).

# Servidor

O servidor fica esperando por conexões TCP e UDP nas portas 5000 e 5001 por
padrão (é possível mudar isto).

Conexões TCP e UDP são tratadas de forma igual do ponto de vista do cliente
(não há diferença de tratamento na troca de mensagens), porém internamente o
servidor têm uma array dos _sockets_ dos clientes TCP.

Para cada cliente (TCP ou UDP), o servidor mantém seu endereço IP e porta da
conexão, sua porta pública para partidas, o nome do usuário logado (se houver),
e o estado atual do cliente (logado, deslogado, jogando, etcr.

# Servidor

Eventos importantes (inicialização/termino do servidr, conexão/desconexão de
cliente, tentativas de login, início/finalização de partidas, etc) são
registrados em um arquivo de texto (`log.txt` por padrão) e imprimidos no
console também.

Alguns dados são armazenados de forma persistente (tais como dados sobre
usuários e partidas) em um arquivo JSON para fácil leitura. Outros dados
(endereço IP e estado de execução do cliente) são dados efêmeros que estão
presentes somente durante o tempo de vida do servidor.

O servidor também realiza _heartbeats_ períodicos, no qual checa qual foi a última
vez que recebeu mensagem de um cliente. Para isso, toda vez que o cliente envia
qualquer mensagem (incluindo _PING_), o servidor atualiza um timestamp associado
ao cliente em questão. Se passar de 5 minutos, o cliente é desconectado.

# Servidor

Aqui também utilizamos máquinas de estado para verificar se o usuário pode
executar determinados comandos. Também utilizamos outros mecanismos de validação
(tais como verificar se o usuário pode alterar a senha, se suas credenciais estão
certas, etc).

Criamos interfaces específicas para cada tarefa do servidor (`Database`, `Logger`,
`ClienteSocket`) para deixar o código mais modular. Assim, o código principal do servidor
só cuida da lógica por trás das requisições, enquanto o resto é delegado para as outras
classes de objetos.

É importante frisar que estamos detalhando nossa implementação do servidor, mas
o servidor poderia ser implementado de várias formas diferentes desde que ele
utilize o protocolo especificado pelo TTTP.

teste1:
medias:
cpu: 0
rede: 0
desvios padrao:
cpu: 0
rede: 0

teste2:
avg cpu server: 0
avg net server: 2.48
avg cpu client: 99.97
avg net client: 700.03
dp cpu server: 0
dp net server: 0.09
dp cpu client: 0.35
dp net client: 15.90

teste3:
avg cpu server: 0
avg net server: 2.66
avg cpu client: 99.40
avg net client: 1300.01
dp cpu server: 0
dp net server: 1.03
dp cpu client: 0.33
dp net client: 19.39
