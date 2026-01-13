# NeuroGraph - Отложенные задачи и заглушки

**Версия:** 1.0
**Создан:** 2026-01-13
**Цель:** Систематический учет всех заглушек, закомментированного кода и отложенных функций

---

## Принцип ведения

Этот файл содержит ВСЕ отложенные задачи, которые были сознательно отложены для будущих версий.
Каждая запись содержит:
- Где находится заглушка (файл:строка)
- Что отложено
- Почему отложено
- Планируемая версия реализации

---

## 1. Dead Code (закомментирован через #[allow(dead_code)])

### Версия для реализации: v1.1.0

#### 1.1. Grid::neighbors() - [src/grid.rs:70](src/core_rust/src/grid.rs#L70)
**Что:** Метод для поиска соседних bucket'ов в Grid
**Почему отложено:** Не используется в текущей версии, но может понадобиться для spatial queries
**Приоритет:** 🟡 Средний
**Действие:** Либо реализовать использование, либо удалить в v1.1.0

#### 1.2. Grid.config - [src/grid.rs:148](src/core_rust/src/grid.rs#L148)
**Что:** Поле GridConfig в структуре Grid
**Почему отложено:** Конфигурация не используется после инициализации
**Приоритет:** 🟢 Низкий
**Действие:** Рассмотреть возможность использования для dynamic reconfiguration

#### 1.3. Graph.config - [src/graph.rs:367](src/core_rust/src/graph.rs#L367)
**Что:** Поле GraphConfig в структуре Graph
**Почему отложено:** Конфигурация не используется после инициализации
**Приоритет:** 🟢 Низкий
**Действие:** Рассмотреть возможность использования для runtime tuning

#### 1.4. Subscription.module_id - [src/guardian.rs:118](src/core_rust/src/guardian.rs#L118)
**Что:** Идентификатор модуля в Subscription
**Почему отложено:** Пока не используется для routing, но нужен для будущей multi-module архитектуры
**Приоритет:** 🟡 Средний
**Действие:** Реализовать module-based routing в Guardian v1.1.0

#### 1.5. EvolutionManager.cdna - [src/evolution_manager.rs:134](src/core_rust/src/evolution_manager.rs#L134)
**Что:** Ссылка на CDNA в EvolutionManager
**Почему отложено:** CDNA не используется напрямую после инициализации
**Приоритет:** 🟡 Средний
**Действие:** Реализовать CDNA-based evolution strategies

#### 1.6. HybridLearning.guardian - [src/hybrid_learning.rs:143](src/core_rust/src/hybrid_learning.rs#L143)
**Что:** Ссылка на Guardian в HybridLearning
**Почему отложено:** Guardian integration не реализована в текущей версии
**Приоритет:** 🟡 Средний
**Действие:** Добавить Guardian-based safety checks для learning proposals

#### 1.7. edit_distance() - [src/gateway/normalizer.rs:182](src/core_rust/src/gateway/normalizer.rs#L182)
**Что:** Функция вычисления edit distance (Levenshtein)
**Почему отложено:** Не используется в текущей нормализации, но полезна для fuzzy matching
**Приоритет:** 🟢 Низкий
**Действие:** Либо использовать в normalization, либо удалить

#### 1.8. ConsoleOutputAdapter.config - [src/adapters/console.rs:33](src/core_rust/src/adapters/console.rs#L33)
**Что:** ConsoleConfig в ConsoleOutputAdapter
**Почему отложено:** Конфигурация не используется после инициализации
**Приоритет:** 🟢 Низкий
**Действие:** Использовать для форматирования вывода (colorize, max_results, show_confidence)

#### 1.9. FeedbackProcessor.intuition_engine - [src/feedback/mod.rs:143](src/core_rust/src/feedback/mod.rs#L143)
**Что:** Ссылка на IntuitionEngine в FeedbackProcessor
**Почему отложено:** Feedback пока не обновляет intuition reflexes
**Приоритет:** 🔴 Высокий (см. раздел 2.1)
**Действие:** Реализовать reflex updates на основе feedback

#### 1.10. WalReader.path - [src/wal.rs:244](src/core_rust/src/wal.rs#L244)
**Что:** Путь к WAL файлу в WalReader
**Почему отложено:** Не используется после открытия файла
**Приоритет:** 🟢 Низкий
**Действие:** Использовать для логирования или удалить

#### 1.11. RuntimeStorage.label_to_id, id_to_label - [src/runtime_storage.rs:112](src/core_rust/src/runtime_storage.rs#L112)
**Что:** Двусторонние маппинги label ↔ id
**Почему отложено:** Не используются в текущей версии RuntimeStorage
**Приоритет:** 🟡 Средний
**Действие:** Либо реализовать label-based token queries, либо удалить

---

## 2. TODO комментарии - СРЕДНИЙ ПРИОРИТЕТ

### Версия для реализации: v1.1.0 (критично)

Эти TODO блокируют полноценную работу ключевых систем и должны быть реализованы в первой минорной версии после релиза.

### ⚠️ АРХИТЕКТУРНОЕ ОГРАНИЧЕНИЕ (требует refactoring)

**Проблема:** Нет связи между signal_id (u64) и ExperienceEvent (event_id: u128)

**Контекст:**
- FeedbackSignal содержит `reference_id: u64` (это signal_id из Gateway)
- ExperienceEvent содержит `event_id: u128` (сейчас просто 0)
- ActionController создает события, но не связывает их с signal_id
- Невозможно найти события по signal_id для обновления rewards

**Возможные решения для v1.1.0:**
1. **Простое:** Добавить HashMap<u64, Vec<u64>> (signal_id → sequence_numbers) в FeedbackProcessor
2. **Среднее:** Использовать signal_id как часть event_id (например, event_id = (signal_id << 64) | local_id)
3. **Правильное:** Добавить поле `signal_id: u64` в ExperienceEvent (требует изменения структуры 128 байт)

**Для v1.0.0:**
- Feedback API работает (валидация, tracking), но не обновляет rewards
- Все TODO помечены и задокументированы
- Пользователи могут использовать базовый API
- Полноценная реализация будет в v1.1.0 после архитектурного refactoring

**Оценка работы для v1.1.0:** 1-2 недели (включая refactoring ExperienceStream)

#### 2.1. Feedback система - не обновляет rewards ⚠️

**Файлы:**
- [src/feedback/mod.rs:263](src/core_rust/src/feedback/mod.rs#L263) - `apply_positive()`
- [src/feedback/mod.rs:275](src/core_rust/src/feedback/mod.rs#L275) - `apply_negative()`

**Что не работает:**
```rust
async fn apply_positive(&self, signal_id: u64, strength: f32) -> Result<String, FeedbackError> {
    let _stream = self.experience_stream.write();
    // TODO: Implement actual reward update in ExperienceStream
    Ok(format!("Applied positive feedback (strength: {:.2}) to signal {}", strength, signal_id))
}
```

**Проблема:**
Feedback API принимает положительные/отрицательные оценки от пользователя, но не обновляет rewards в ExperienceStream. Система не учится на feedback!

**Что нужно сделать:**
1. Найти Experience событие по signal_id
2. Обновить reward компоненты (homeostasis/curiosity/efficiency/goal)
3. Пересчитать Q-values в соответствующих bins
4. Записать обновленное событие обратно в stream

**Приоритет:** 🔴 ВЫСОКИЙ
**Оценка:** 4-6 часов работы
**Блокирует:** Reinforcement learning from user feedback

---

#### 2.2. Feedback система - не создает связи ⚠️

**Файлы:**
- [src/feedback/mod.rs:292](src/core_rust/src/feedback/mod.rs#L292) - `apply_correction()`
- [src/feedback/mod.rs:303](src/core_rust/src/feedback/mod.rs#L303) - `apply_association()`

**Что не работает:**
```rust
async fn apply_correction(&self, signal_id: u64, correct_value: &str) -> Result<String, FeedbackError> {
    // ...
    // TODO: Create actual connection between original and corrected
    Ok(format!("Applied correction: '{}' for signal {}", correct_value, signal_id))
}

async fn apply_association(&self, signal_id: u64, related_word: &str, strength: f32) -> Result<String, FeedbackError> {
    // ...
    // TODO: Create actual connection with specified strength
    Ok(format!("Applied association: '{}' (strength: {:.2}) for signal {}", related_word, strength, signal_id))
}
```

**Проблема:**
Когда пользователь говорит "X это на самом деле Y" или "X связано с Y", система не создает связи в Graph. Correction и Association feedback игнорируются!

**Что нужно сделать:**
1. Найти или создать token для correct_value / related_word
2. Создать Connection в Graph между original token и new token
3. Установить правильную strength для connection
4. Для correction: пометить old interpretation как менее релевантный

**Приоритет:** 🔴 ВЫСОКИЙ
**Оценка:** 3-5 часов работы
**Блокирует:** Learning from corrections, semantic association building

---

#### 2.3. Gateway - примитивный nearest neighbor search ⚠️

**Файл:** [src/gateway/normalizer.rs:142](src/core_rust/src/gateway/normalizer.rs#L142)

**Что не работает:**
```rust
// TODO: Implement proper nearest neighbor search
// For now, just return the first match
if let Some(first_token) = similar_tokens.first() {
    debug!("Using first similar token: {} (score: {:.3})", first_token.word, first_token.score);
    return Some(first_token.token_id);
}
```

**Проблема:**
Semantic search просто берет первый попавшийся токен вместо того, чтобы найти наиболее релевантный. Это влияет на quality semantic queries.

**Что нужно сделать:**
1. Реализовать kNN search в embedding space
2. Использовать Grid.neighbors() для spatial locality
3. Учитывать не только similarity score, но и usage frequency, recency
4. Возможно использовать approximate NN (HNSW) для производительности

**Приоритет:** 🟡 СРЕДНИЙ
**Оценка:** 6-8 часов работы
**Блокирует:** High-quality semantic search

---

#### 2.4. HybridLearning - не применяет ADNA proposals ⚠️

**Файлы:**
- [src/hybrid_learning.rs:242](src/core_rust/src/hybrid_learning.rs#L242) - `apply_proposal()`
- [src/hybrid_learning.rs:372](src/core_rust/src/hybrid_learning.rs#L372) - `update_weights()`

**Что не работает:**
```rust
pub fn apply_proposal(&mut self, proposal: ADNAProposal) -> Result<(), String> {
    // TODO: Implement ADNA proposal application
    // For now, just track proposals
    self.pending_proposals.push(proposal);
    Ok(())
}

async fn update_weights(&self, _update: WeightUpdate) -> Result<(), String> {
    // TODO: Implement ADNA weight update
    Ok(())
}
```

**Проблема:**
IntuitionEngine генерирует ADNA proposals (изменения в весах ActionPolicy), но HybridLearning их не применяет. Система не эволюционирует!

**Что нужно сделать:**
1. Валидировать proposal через Guardian
2. Применять weight updates к ADNA policies
3. Логировать изменения для отката (если что-то пойдет не так)
4. Реализовать Create/Delete/Promote операции для policies

**Приоритет:** 🔴 ВЫСОКИЙ
**Оценка:** 8-10 часов работы
**Блокирует:** Autonomous evolution, self-improvement

---

## 3. TODO комментарии - НИЗКИЙ ПРИОРИТЕТ

### Версия для реализации: v1.2.0+

Эти TODO не блокируют базовую функциональность и могут быть реализованы позже.

#### 3.1. Оптимизации

**[bootstrap.rs:335](src/core_rust/src/bootstrap.rs#L335)** - Implement proper PCA with SVD
- Сейчас используется простое усреднение для dimensionality reduction
- SVD-based PCA даст более точные результаты
- Приоритет: 🟢 Низкий
- Версия: v1.2.0

**[reflex_layer.rs:515](src/core_rust/src/reflex_layer.rs#L515)** - Implement LRU eviction
- Сейчас рефлексы не удаляются при переполнении кеша
- LRU eviction предотвратит memory leaks
- Приоритет: 🟢 Низкий (пока кеш не переполняется)
- Версия: v1.2.0

**[persistence/postgres.rs:285](src/core_rust/src/persistence/postgres.rs#L285)** - Optimize with bulk insert
- Сейчас каждое событие пишется отдельным INSERT
- Bulk insert ускорит persistence в 10-100 раз
- Приоритет: 🟢 Низкий (persistence опциональна)
- Версия: v1.2.0

#### 3.2. Будущие интеграции

**[intuition_engine.rs:212](src/core_rust/src/intuition_engine.rs#L212)** - Leverage token_similarity()
- Использовать semantic similarity для лучшего state clustering
- Приоритет: 🟢 Низкий
- Версия: v1.3.0

**[curiosity/autonomous.rs:153, 206](src/core_rust/src/curiosity/autonomous.rs#L153)** - ActionController integration
- Интегрировать curiosity-driven exploration с ActionController
- Приоритет: 🟢 Низкий
- Версия: v1.3.0

**[signal_system/system.rs:177](src/core_rust/src/signal_system/system.rs#L177)** - Grid/Graph/Guardian integration
- Полная интеграция SignalSystem с core компонентами
- Приоритет: 🟢 Низкий
- Версия: v1.3.0

**[gateway/normalizer.rs:127](src/core_rust/src/gateway/normalizer.rs#L127)** - Add to curiosity queue
- Добавлять unknown слова в curiosity queue для autonomous learning
- Приоритет: 🟢 Низкий
- Версия: v1.3.0

#### 3.3. Недореализованные фичи

**[python/runtime.rs:272, 335, 372](src/core_rust/src/python/runtime.rs#L272)** - Python runtime features
- Feedback processing из Python
- token_dict применение
- Приоритет: 🟢 Низкий
- Версия: v1.2.0

**[signal_system/py_bindings.rs:139](src/core_rust/src/signal_system/py_bindings.rs#L139)** - Implement poll() method
- Polling mode для SignalSystem
- Приоритет: 🟢 Низкий
- Версия: v1.2.0

**[signal_system/registry.rs:172](src/core_rust/src/signal_system/registry.rs#L172)** - Full glob matching
- Полноценный glob syntax для pattern matching
- Приоритет: 🟢 Низкий
- Версия: v1.2.0

**[hybrid_learning.rs:314](src/core_rust/src/hybrid_learning.rs#L314)** - Create/Delete/Promote operations
- Операции для ADNA policy lifecycle management
- Приоритет: 🟡 Средний (связано с 2.4)
- Версия: v1.1.0

**[api/websocket.rs:124, 127, 130](src/core_rust/src/api/websocket.rs#L124)** - WebSocket features
- Subscription/unsubscription logic
- Feedback через WebSocket
- Приоритет: 🟢 Низкий
- Версия: v1.2.0

#### 3.4. Мелочи

**[graph.rs:1178](src/core_rust/src/graph.rs#L1178)** - Populate edges in token_details
- Сейчас edges пустой массив в GraphTokenDetails
- Нужно заполнять реальными connections
- Приоритет: 🟢 Низкий
- Версия: v1.1.0

**[gateway/mod.rs:293](src/core_rust/src/gateway/mod.rs#L293)** - Meaningful state from tick/timestamp
- Сейчас state = [0.0; 8], можно использовать tick_number для создания temporal patterns
- Приоритет: 🟢 Низкий
- Версия: v1.2.0

---

## 4. План реализации

### v1.1.0 - "Feedback & Evolution" (приоритет 🔴 ВЫСОКИЙ)

**Фокус:** Сделать feedback систему и ADNA evolution полностью функциональными

**Задачи:**
1. ✅ Реализовать reward updates в feedback (2.1)
2. ✅ Реализовать connection creation в feedback (2.2)
3. ✅ Реализовать ADNA proposal application (2.4)
4. ✅ Реализовать Create/Delete/Promote для policies (3.3)
5. ✅ Populate edges в token_details (3.4)
6. ✅ Решить судьбу dead_code полей (использовать или удалить)

**Оценка времени:** 2-3 недели
**Критерии успеха:**
- Feedback реально обновляет систему
- ADNA proposals применяются автоматически
- Система эволюционирует на основе опыта

### v1.2.0 - "Performance & Polish" (приоритет 🟡 СРЕДНИЙ)

**Фокус:** Оптимизации и недореализованные фичи

**Задачи:**
1. Better nearest neighbor search (2.3)
2. Bulk insert для PostgreSQL (3.1)
3. LRU eviction для reflexes (3.1)
4. Python runtime features (3.3)
5. WebSocket features (3.3)

**Оценка времени:** 2-3 недели

### v1.3.0 - "Advanced Features" (приоритет 🟢 НИЗКИЙ)

**Фокус:** Продвинутые интеграции и AI features

**Задачи:**
1. Curiosity integration (3.2)
2. Semantic similarity в state clustering (3.2)
3. Full SignalSystem integration (3.2)
4. PCA with SVD (3.1)

**Оценка времени:** 3-4 недели

---

## 5. Metrics & Tracking

### Статистика отложенных задач

**По приоритетам:**
- 🔴 Высокий: 4 задачи (раздел 2)
- 🟡 Средний: 7 задач (dead_code + TODO)
- 🟢 Низкий: 14 задач (оптимизации и fичи)

**По версиям:**
- v1.1.0: 10 задач (критичные)
- v1.2.0: 9 задач (улучшения)
- v1.3.0: 6 задач (advanced)

**По категориям:**
- Dead code: 11 элементов
- Feedback система: 4 TODO
- Evolution система: 2 TODO
- Оптимизации: 3 TODO
- Интеграции: 5 TODO
- Недореализованные фичи: 7 TODO
- Мелочи: 2 TODO

---

## 6. Review Process

**Периодичность review:** После каждого минорного релиза

**Действия при review:**
1. Отметить реализованные задачи как ✅
2. Переоценить приоритеты оставшихся
3. Добавить новые обнаруженные заглушки
4. Обновить оценки времени

**Следующий review:** После релиза v1.0.0

---

**Последнее обновление:** 2026-01-13
**Автор:** NeuroGraph Development Team
