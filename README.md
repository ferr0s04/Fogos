# Fogos - Alerta de Incêndios Próximos

## Descrição
Este projeto monitoriza incêndios ativos em Portugal usando a API do Fogos.pt e envia alertas por email caso haja incêndios próximos de locais definidos pelo utilizador.

## Funcionalidades
- Consulta automática à API de incêndios ativos (Fogos.pt).
- Suporte a múltiplos locais.
- Raio de procura customizado por local.
- Email com detalhes dos incêndios próximos, incluindo coordenadas que redirecionam para o Google Maps.
- Execução automática a cada 15 minutos via supercronic (com Docker).

## Instalação e Uso

### 1. Pré-requisitos
- Docker
- (Opcional) Python 3.11+ para execução local

### Execução local
```sh
pip install -r requirements.txt
python main.py
```

### 5. Execução com Docker
```sh
docker build -t fogos .
docker run -d --name fogos fogos
```

Ou usando docker-compose:
```sh
docker-compose up -d
```

O script será executado automaticamente a cada 15 minutos e enviará email se houver incêndios próximos.
