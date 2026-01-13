# Graph Analysis - Критическое открытие

**Дата:** 2026-01-13
**Версия:** v0.68.0
**Статус:** ТРЕБУЕТ РЕШЕНИЯ

---

## TL;DR

**Graph - мертвый код.** 1400+ строк не используются в production. Можно безопасно удалить в v1.1.0.

---

## Быстрые факты

### ❌ Кто НЕ использует Graph:

- IntuitionEngine
- ActionController
- Gateway/Normalizer
- FeedbackProcessor
- HybridLearning
- API endpoints
- WebSocket handlers

### ✅ Кто использует Graph:

- Tests (unit tests)
- Benchmarks
- SignalExecutor (который сам не используется!)

### Как РЕАЛЬНО работает система:

```
Signal
  ↓
Gateway → Bootstrap.get_concept() [HashMap, НЕ Graph!]
  ↓
Token → Grid.find_neighbors() [Spatial search, НЕ Graph!]
  ↓
IntuitionEngine [ExperienceStream + ADNA + Reflex]
  ↓
Learning [Rewards, proposals, ConnectionV3]
```

---

## Что делать?

### Для v1.0.0 (Release Candidate):

**НИЧЕГО.** Оставить как есть, задокументировать.

**Причина:**
- Не время для больших изменений
- Код не мешает работе системы
- Можно спокойно удалить после релиза

### Для v1.1.0:

**УДАЛИТЬ Graph полностью.**

**Удалить:**
```
src/graph.rs                          (1400 LOC)
src/executors/signal_executor.rs     (300 LOC)
src/bootstrap.rs::weave_connections() (100 LOC)
```

**Выгоды:**
- Убрать ~1800 строк мертвого кода
- Упростить архитектуру
- П2 (Feedback connections) становится тривиальным - просто HashMap!

---

## Влияние на П2 (Feedback connections)

### Было (ошибочное понимание):

❌ "Нужен RuntimeGraph поверх статического Graph"
❌ "Требует 2-3 недели разработки"
❌ "Сложная интеграция с мутабельностью"

### Стало (после открытия):

✅ Просто HashMap<(u32, u32), ConnectionV3> в FeedbackProcessor
✅ 2-3 часа работы
✅ Никаких архитектурных проблем

### Минимальная реализация П2:

```rust
pub struct FeedbackProcessor {
    user_connections: Arc<RwLock<HashMap<(u32, u32), ConnectionV3>>>,
}

async fn apply_association(&self, signal_id: u64, word: &str, strength: f32) {
    let token_a = self.find_recent_token(signal_id)?;
    let token_b = self.bootstrap.read().get_concept(word)?.id;

    let mut conn = ConnectionV3::new(token_a, token_b);
    conn.set_connection_type(ConnectionType::AssociatedWith);
    conn.pull_strength = strength;

    self.user_connections.write().insert((token_a, token_b), conn);
}
```

**Готово!** ConnectionV3 можно обучать через proposals, как и статические связи.

---

## Почему это произошло?

1. **Название проекта** - "NeuroGraph" → граф казался обязательным
2. **Legacy feature** - Spreading activation планировалась для SignalSystem v1.1 (так и не реализована)
3. **Переоценка роли** - Граф как "кеш" для Grid KNN, но Grid сам это делает
4. **Bootstrap confusion** - Создает edges, но использует только concepts HashMap

---

## Решение

| Версия | Действие | Оценка | Риск |
|--------|----------|--------|------|
| v1.0.0 | Оставить + документация | 0 дней | Нулевой |
| v1.1.0 | Удалить Graph | 1-2 дня | Низкий |
| v1.1.0 | Реализовать П2 (Вариант 1) | 2-3 часа | Низкий |

---

## Ссылки

- Детальный анализ: [CONNECTION_ANALYSIS.md](CONNECTION_ANALYSIS.md)
- Варианты реализации П2: [DEFERRED.md секция 2.2](DEFERRED.md)
- Архитектурные открытия: [DEFERRED.md секция 5.1](DEFERRED.md)

---

**Вывод:** Graph можно спокойно удалить. Система работает на Grid + ExperienceStream + ADNA, граф не нужен.
