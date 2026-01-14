# NeuroGraph Grafana Dashboards

Готовые Grafana dashboards для мониторинга NeuroGraph платформы.

## Доступные Dashboard'ы

### 1. System Overview (`01-system-overview.json`)
Общий обзор состояния системы:
- CPU и Memory usage (gauges)
- Request rate (requests/sec)
- Request latency (p95/p99)
- HTTP status codes (2xx/4xx/5xx)

### 2. WebSocket Metrics (`02-websocket-metrics.json`)
Мониторинг WebSocket соединений:
- Active connections (gauge)
- Message rate (sent/received по каналам)
- Channel subscribers
- Buffered events

### 3. Token & Grid Metrics (`03-token-grid-metrics.json`)
Операции с токенами и Grid:
- Total tokens в storage
- Token CRUD операции (Create/Read/Update/Delete)
- Grid query операции (Spatial search, Neighbors, Field influence)
- Grid query latency (p95)

## Быстрый старт

### 1. Запуск с мониторингом

```bash
# Запустить полный стек с Prometheus + Grafana
docker-compose --profile monitoring up -d

# Проверить статус
docker-compose ps
```

### 2. Доступ к Grafana

- URL: http://localhost:3000
- Username: `admin` (можно изменить через `GRAFANA_USER`)
- Password: `admin` (можно изменить через `GRAFANA_PASSWORD`)

Dashboard'ы будут автоматически загружены при первом запуске.

### 3. Доступ к Prometheus

- URL: http://localhost:9090
- Alerts: http://localhost:9090/alerts

## Структура директорий

```
grafana/
├── README.md                          # Этот файл
├── dashboards/                        # JSON конфигурации dashboards
│   ├── 01-system-overview.json
│   ├── 02-websocket-metrics.json
│   └── 03-token-grid-metrics.json
└── provisioning/                      # Grafana provisioning конфигурация
    ├── dashboards/
    │   └── default.yml                # Auto-load dashboards
    └── datasources/
        └── prometheus.yml             # Prometheus datasource
```

## Кастомизация

### Добавление нового Dashboard

1. Создайте dashboard в Grafana UI
2. Экспортируйте JSON (Share → Export → Save to file)
3. Сохраните в `grafana/dashboards/`
4. Dashboard будет автоматически загружен при перезапуске

### Изменение существующих Dashboard'ов

Вы можете редактировать dashboard'ы напрямую в Grafana UI. Для сохранения изменений:

1. Экспортируйте обновленный JSON
2. Замените файл в `grafana/dashboards/`
3. Перезапустите Grafana: `docker-compose restart grafana`

## Alert Rules

Alert rules настроены в `prometheus-alerts.yml`:

- **HighErrorRate** - HTTP 5xx error rate > 5%
- **HighLatency** - p95 latency > 1s
- **HighMemoryUsage** - Memory > 1.5GB
- **HighCPUUsage** - CPU > 80%
- **WebSocketConnectionsDrop** - Резкое падение connections
- **ServiceDown** - API service недоступен
- **UnusuallyHighRequestRate** - Request rate > 1000 req/s
- **HighTokenCount** - Token count > 90k
- **HighBufferedEvents** - Buffered events > 500

### Просмотр активных alerts

Prometheus Alerts UI: http://localhost:9090/alerts

## Метрики

### Стандартные метрики (FastAPI/Prometheus)

- `http_requests_total` - Total HTTP requests
- `http_request_duration_seconds` - Request duration histogram
- `process_cpu_seconds_total` - CPU usage
- `process_resident_memory_bytes` - Memory usage

### Кастомные метрики NeuroGraph

- `websocket_connections_active` - Active WebSocket connections
- `websocket_messages_sent_total` - Sent messages counter
- `websocket_messages_received_total` - Received messages counter
- `websocket_channel_subscribers` - Subscribers per channel
- `websocket_buffered_events` - Buffered events count
- `token_storage_count` - Total tokens in storage
- `token_operations_total` - Token CRUD operations counter
- `grid_query_operations_total` - Grid query operations counter
- `grid_query_duration_seconds` - Grid query duration histogram

## Production Recommendations

1. **Enable authentication**: Измените дефолтные credentials для Grafana
2. **Configure alerting**: Настройте Alertmanager для отправки уведомлений
3. **Data retention**: Настройте retention policy в Prometheus (дефолт: 7 дней)
4. **Backup dashboards**: Регулярно экспортируйте и делайте backup dashboard JSON
5. **Monitor disk usage**: Prometheus data может быстро расти на высоких нагрузках

## Troubleshooting

### Dashboard'ы не загружаются

```bash
# Проверьте logs Grafana
docker-compose logs grafana

# Проверьте права доступа к файлам
ls -la grafana/dashboards/
ls -la grafana/provisioning/
```

### Нет данных в dashboard'ах

```bash
# Проверьте что Prometheus scraping работает
curl http://localhost:9090/api/v1/targets

# Проверьте что API экспортирует метрики
curl http://localhost:8080/metrics
```

### Alerts не срабатывают

```bash
# Проверьте что alert rules загрузились
curl http://localhost:9090/api/v1/rules

# Проверьте Prometheus logs
docker-compose logs prometheus
```

## Версия

Dashboard версия: v0.67.0
Совместимость: NeuroGraph v0.67.0+
