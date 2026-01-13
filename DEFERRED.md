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

#### 2.1. Feedback система - упрощенная реализация rewards (v1.0.0) ✅

**Файлы:**
- [src/feedback/mod.rs:261](src/core_rust/src/feedback/mod.rs#L261) - `apply_positive()`
- [src/feedback/mod.rs:290](src/core_rust/src/feedback/mod.rs#L290) - `apply_negative()`

**Статус v1.0.0:** РЕАЛИЗОВАНО с упрощением

**Реализация:**
```rust
async fn apply_positive(&self, _signal_id: u64, strength: f32) -> Result<String, FeedbackError> {
    use crate::experience_stream::AppraiserType;
    let stream = self.experience_stream.read();
    let total = stream.total_written();
    let start_seq = if total > 1000 { total - 1000 } else { 0 };

    let mut updated_count = 0;
    for seq in start_seq..total {
        if let Some(_event) = stream.get_event(seq) {
            let new_reward = strength;
            if let Err(_) = stream.set_appraiser_reward(seq, AppraiserType::Goal, new_reward) {
                continue;
            }
            updated_count += 1;
        }
    }

    Ok(format!("Applied positive feedback (strength: {:.2}) to {} recent events", strength, updated_count))
}
```

**Упрощение:**
- Обновляет последние 1000 событий вместо точного события
- Не требует signal_id tracking (архитектурное ограничение)
- Работает с существующим ExperienceStream API

**Для v1.1.0:**
1. Добавить HashMap<signal_id, Vec<sequence_number>> для точного отслеживания
2. Или добавить поле signal_id в ExperienceEvent
3. Обновлять только релевантные события

**Приоритет:** 🟡 СРЕДНИЙ (работает, но неточно)
**Оценка:** 3-4 часа для полной реализации
**Блокирует:** Точное reinforcement learning (текущая реализация функциональна)

---

#### 2.2. Feedback система - не создает связи (ОБНОВЛЕНО после анализа) ⚠️

**Файлы:**
- [src/feedback/mod.rs:319](src/core_rust/src/feedback/mod.rs#L319) - `apply_correction()`
- [src/feedback/mod.rs:333](src/core_rust/src/feedback/mod.rs#L333) - `apply_association()`

**Статус v1.0.0:** ЗАГЛУШКА

**КРИТИЧЕСКОЕ ОТКРЫТИЕ (2026-01-13):**

После детального анализа обнаружено:
1. **Graph не используется** в production коде (только в tests/benchmarks)
2. **Spreading activation** - мертвая feature (SignalSystem v1.1 не реализован)
3. **IntuitionEngine, ActionController, Gateway** - НЕ используют Graph
4. **Картина мира строится через:** Bootstrap HashMap + Grid + ExperienceStream + ADNA

**Вывод:** Graph можно удалить без последствий для работающей системы!

**П2 становится ТРИВИАЛЬНОЙ задачей** - просто HashMap с ConnectionV3.

---

### Варианты реализации П2 (от простого к продвинутому)

#### Вариант 1: Минимальный (2-3 часа) ⭐ РЕКОМЕНДУЕТСЯ для v1.0.0

**Что делаем:**
```rust
pub struct FeedbackProcessor {
    // ... existing fields ...

    /// User-created connections (runtime)
    user_connections: Arc<RwLock<HashMap<(u32, u32), ConnectionV3>>>,
}

async fn apply_association(&self, signal_id: u64, related_word: &str, strength: f32)
    -> Result<String, FeedbackError>
{
    // 1. Найти token_a через signal_id (упрощение: последний токен в последних 1000 событий)
    let token_a = self.find_recent_token(signal_id)?;

    // 2. Найти или создать token_b через Bootstrap
    let bootstrap = self.bootstrap.read();
    let token_b = match bootstrap.get_concept(related_word) {
        Some(concept) => concept.id,
        None => {
            // Новое слово - генерируем temporary ID (> 1_000_000)
            let temp_id = 1_000_000 + related_word.len() as u32;
            temp_id
        }
    };

    // 3. Создать ConnectionV3 (просто struct, не требует Graph!)
    let mut conn = ConnectionV3::new(token_a, token_b);
    conn.set_connection_type(ConnectionType::AssociatedWith);
    conn.pull_strength = strength;
    conn.mutability = ConnectionMutability::Hypothesis as u8;

    // 4. Сохранить в HashMap
    let mut conns = self.user_connections.write();
    conns.insert((token_a, token_b), conn);

    Ok(format!("Created association: {} <-> {} (strength: {:.2})", token_a, token_b, strength))
}
```

**Преимущества:**
- ✅ Простая реализация
- ✅ НЕ требует Graph
- ✅ Работает сразу
- ✅ ConnectionV3 можно обучать через proposals

**Недостатки:**
- ❌ signal_id → token_id mapping упрощенный
- ❌ Новые слова не имеют embeddings
- ❌ Connections не видны из других модулей

**Оценка:** 2-3 часа
**Риск:** Низкий
**Для v1.0.0:** ДА ✅

---

#### Вариант 2: С query API (1-2 дня)

**Что добавляем к Варианту 1:**

```rust
impl FeedbackProcessor {
    /// Получить все connections для токена (user + bootstrap)
    pub fn get_all_connections(&self, token_id: u32) -> Vec<ConnectionV3> {
        let mut connections = Vec::new();

        // User-created connections
        let user_conns = self.user_connections.read();
        for ((a, b), conn) in user_conns.iter() {
            if *a == token_id || *b == token_id {
                connections.push(*conn);
            }
        }

        // TODO: Добавить connections из Bootstrap (если есть)

        connections
    }

    /// Экспорт для других модулей
    pub fn export_connections(&self) -> HashMap<(u32, u32), ConnectionV3> {
        self.user_connections.read().clone()
    }
}
```

**Интеграция с IntuitionEngine:**
```rust
// IntuitionEngine может получать user connections для proposals
let user_conns = feedback_processor.export_connections();

for ((a, b), mut conn) in user_conns {
    // Генерировать proposals на основе experience
    if let Some(proposal) = stats.generate_confidence_proposal(&conn, 20) {
        conn.apply_proposal_with_guardian(&proposal)?;
    }
}
```

**Преимущества:**
- ✅ Все из Варианта 1
- ✅ Интеграция с IntuitionEngine
- ✅ Query API для других модулей

**Недостатки:**
- ❌ Те же что в Варианте 1

**Оценка:** 1-2 дня
**Риск:** Низкий
**Для v1.0.0:** Можно, но не критично

---

#### Вариант 3: С signal_id tracking (3-5 дней)

**Что добавляем к Варианту 2:**

```rust
pub struct FeedbackProcessor {
    // ... existing ...

    /// Mapping signal_id → token_ids для точного отслеживания
    signal_to_tokens: Arc<RwLock<HashMap<u64, Vec<u32>>>>,
}

impl FeedbackProcessor {
    /// Регистрировать signal_id при обработке события
    pub fn register_signal(&mut self, signal_id: u64, tokens: Vec<u32>) {
        let mut mapping = self.signal_to_tokens.write();
        mapping.insert(signal_id, tokens);
    }

    /// Точный поиск токена по signal_id
    fn find_token_by_signal(&self, signal_id: u64) -> Result<u32, FeedbackError> {
        let mapping = self.signal_to_tokens.read();

        mapping.get(&signal_id)
            .and_then(|tokens| tokens.first().copied())
            .ok_or(FeedbackError::SignalNotFound(signal_id))
    }
}
```

**Интеграция с Gateway:**
```rust
// При обработке сигнала Gateway регистрирует mapping
let token_ids = normalizer.normalize(&signal.text)?;
feedback_processor.register_signal(signal.id, token_ids);
```

**Преимущества:**
- ✅ Все из Варианта 2
- ✅ Точное отслеживание signal → tokens
- ✅ П1 (rewards) становится точным тоже!

**Недостатки:**
- ❌ Требует интеграции с Gateway
- ❌ Расход памяти на HashMap

**Оценка:** 3-5 дней
**Риск:** Средний
**Для v1.0.0:** Слишком много для RC

---

#### Вариант 4: С runtime embeddings (1-2 недели)

**Что добавляем к Варианту 3:**

```rust
pub struct FeedbackProcessor {
    // ... existing ...

    /// Runtime токены с embeddings
    runtime_tokens: Arc<RwLock<HashMap<String, RuntimeToken>>>,
}

struct RuntimeToken {
    id: u32,
    word: String,
    embedding: Vec<f32>,  // 300-1536 dimensions
    created_at: SystemTime,
}

impl FeedbackProcessor {
    /// Создать токен с embedding через sentence transformer
    async fn create_token_with_embedding(&mut self, word: &str) -> Result<u32, FeedbackError> {
        // 1. Генерировать embedding через ML модель (sentence-transformers)
        let embedding = self.embedding_model.encode(word).await?;

        // 2. Создать RuntimeToken
        let token_id = self.next_runtime_id;
        self.next_runtime_id += 1;

        let token = RuntimeToken {
            id: token_id,
            word: word.to_string(),
            embedding,
            created_at: SystemTime::now(),
        };

        // 3. Сохранить
        let mut tokens = self.runtime_tokens.write();
        tokens.insert(word.to_string(), token);

        Ok(token_id)
    }
}
```

**Преимущества:**
- ✅ Все из Варианта 3
- ✅ Новые слова имеют настоящие embeddings
- ✅ Можно использовать в Grid search
- ✅ Полноценная расширяемость словаря

**Недостатки:**
- ❌ Требует ML модель (sentence-transformers)
- ❌ Сложная интеграция
- ❌ Производительность (embedding generation ~10-100ms)

**Оценка:** 1-2 недели
**Риск:** Высокий
**Для v1.0.0:** НЕТ, для v1.1.0+

---

#### Вариант 5: Полноценный RuntimeGraph (3-4 недели)

**Архитектура:**
```rust
pub struct RuntimeGraph {
    /// Статический граф из Bootstrap (read-only)
    static_bootstrap: Arc<RwLock<BootstrapLibrary>>,

    /// Runtime токены
    runtime_tokens: HashMap<String, RuntimeToken>,

    /// Runtime connections
    runtime_connections: HashMap<(u32, u32), ConnectionV3>,

    /// Unified query layer
    query_cache: LruCache<u32, Vec<ConnectionV3>>,
}

impl RuntimeGraph {
    /// Unified query - объединяет static + runtime
    pub fn get_connections(&mut self, token_id: u32) -> Vec<ConnectionV3> {
        // Check cache
        if let Some(cached) = self.query_cache.get(&token_id) {
            return cached.clone();
        }

        let mut connections = Vec::new();

        // 1. Static connections from Bootstrap
        // (Bootstrap не хранит connections, только concepts)

        // 2. Runtime connections
        for ((a, b), conn) in &self.runtime_connections {
            if *a == token_id || *b == token_id {
                connections.push(*conn);
            }
        }

        // Cache result
        self.query_cache.put(token_id, connections.clone());

        connections
    }

    /// Persistence - сохранить runtime данные
    pub fn save_to_file(&self, path: &Path) -> Result<(), Error> {
        let data = RuntimeGraphData {
            tokens: self.runtime_tokens.clone(),
            connections: self.runtime_connections.clone(),
        };

        let json = serde_json::to_string(&data)?;
        std::fs::write(path, json)?;

        Ok(())
    }
}
```

**Преимущества:**
- ✅ Все из Варианта 4
- ✅ Unified API для статических + runtime данных
- ✅ Persistence (save/load)
- ✅ Query cache для производительности
- ✅ Полноценная архитектура для будущего

**Недостатки:**
- ❌ Очень сложная реализация
- ❌ Много интеграционных точек
- ❌ Требует тестирования и отладки

**Оценка:** 3-4 недели
**Риск:** Очень высокий
**Для v1.0.0:** НЕТ, для v1.2.0+

---

## Рекомендация для v1.0.0:

**Вариант 1 (Минимальный)** - 2-3 часа работы, низкий риск, работает сразу.

**Обоснование:**
- v1.0.0 - это Release Candidate, нужна стабильность
- П2 будет работать (пусть и упрощенно)
- Можно улучшить в v1.1.0 без breaking changes
- Пользователи получат feedback на corrections/associations
- IntuitionEngine сможет обучать user connections

**Для v1.1.0:** Вариант 3 (с signal_id tracking)
**Для v1.2.0:** Вариант 4-5 (с embeddings и RuntimeGraph)

**Приоритет для v1.0.0:** 🟡 СРЕДНИЙ (можно оставить как stub с хорошей документацией)
**Приоритет для v1.1.0:** 🔴 ВЫСОКИЙ (важная feature)
**Оценка для v1.0.0:** 2-3 часа (Вариант 1)
**Блокирует:** User-driven vocabulary expansion (некритично для v1.0.0)

---

### Что необходимо для полноценной работы П2 (Checklist для v1.1.0)

#### Блокер #1: signal_id → token_id mapping ⚠️

**Проблема:**
`FeedbackSignal` содержит `reference_id: u64` (signal_id), но не знаем какой токен был в этом сигнале.

**Текущая ситуация:**
```rust
// Gateway обрабатывает сигнал:
let signal_id = generate_signal_id();
let tokens = normalizer.normalize(&text)?;  // Vec<TokenId>

// Но mapping НЕ сохраняется!
// Позже FeedbackProcessor не может найти токены по signal_id
```

**Решение для v1.1.0:**

**Вариант 1A: Добавить в FeedbackProcessor**
```rust
pub struct FeedbackProcessor {
    // ... existing ...

    /// Mapping signal_id → token_ids
    signal_to_tokens: Arc<RwLock<HashMap<u64, Vec<u32>>>>,
}

// Gateway должен вызывать после обработки:
feedback_processor.register_signal(signal_id, token_ids);
```

**Вариант 1B: Добавить в ExperienceEvent**
```rust
pub struct ExperienceEvent {
    // ... existing 128 bytes ...

    pub signal_id: u64,  // NEW: 8 bytes
    // Requires: увеличить размер до 136 bytes или убрать padding
}
```

**Рекомендуется:** Вариант 1A (проще, не меняет ExperienceEvent)

**Оценка:** 2-3 часа
**Файлы:**
- `src/feedback/mod.rs` - добавить HashMap
- `src/gateway/` - интеграция с Gateway

---

#### Блокер #2: ExperienceEvent не хранит token_id ⚠️

**Проблема:**
```rust
pub struct ExperienceEvent {
    pub coordinates: [[i16; 3]; 8],  // 48 bytes - coordinates
    // ❌ НЕТ поля token_id!
}
```

При обработке feedback мы можем найти события через ExperienceStream, но не знаем какие токены там были.

**Решение для v1.1.0:**

**Вариант 2A: Добавить token_id в ExperienceEvent (breaking change)**
```rust
pub struct ExperienceEvent {
    // ... existing ...
    pub token_id: u32,  // NEW: 4 bytes
    pub _padding: u32,  // Выравнивание
}
```

**Преимущества:**
- ✅ Прямой доступ к токену из события
- ✅ П1 (rewards) становится точнее
- ✅ П2 получает нужную информацию

**Недостатки:**
- ❌ Breaking change (структура 128 → 136 bytes)
- ❌ Нужно обновить все места создания событий

**Вариант 2B: Signal-to-tokens mapping (НЕ breaking)**

Использовать Блокер #1 (HashMap), не менять ExperienceEvent.

**Рекомендуется:** Вариант 2B для v1.1.0, 2A для v1.2.0

**Оценка:** 1 день (если 2A), 0 часов (если 2B)

---

#### Требование #3: Runtime токены для новых слов

**Проблема:**
Пользователь говорит: "X связано с 'новое_слово'"
- ❌ Bootstrap не знает 'новое_слово'
- ❌ Нет token_id для создания Connection

**Решение для v1.1.0 (минимальное):**

```rust
pub struct FeedbackProcessor {
    // ... existing ...

    /// Runtime токены (без embeddings)
    runtime_tokens: Arc<RwLock<HashMap<String, u32>>>,
    next_runtime_id: AtomicU32,  // Starts at 1_000_000
}

impl FeedbackProcessor {
    fn get_or_create_token(&self, word: &str) -> u32 {
        // Сначала проверяем Bootstrap
        if let Some(concept) = self.bootstrap.read().get_concept(word) {
            return concept.id;
        }

        // Если нет - создаем runtime token
        let mut tokens = self.runtime_tokens.write();
        if let Some(&id) = tokens.get(word) {
            return id;
        }

        let new_id = self.next_runtime_id.fetch_add(1, Ordering::SeqCst);
        tokens.insert(word.to_string(), new_id);
        new_id
    }
}
```

**Ограничения минимального решения:**
- ❌ Нет embeddings (не работает в Grid search)
- ❌ Нет coordinates (не участвует в spatial operations)
- ✅ НО connections работают!
- ✅ IntuitionEngine может обучать connections

**Для v1.2.0:** Добавить embeddings через ML модель (см. Вариант 4)

**Оценка:** 1-2 часа
**Приоритет:** 🔴 ВЫСОКИЙ

---

#### Требование #4: Persistence для runtime данных

**Проблема:**
User connections и runtime токены живут только в памяти. При перезапуске - теряются.

**Решение для v1.1.0:**

```rust
impl FeedbackProcessor {
    /// Сохранить runtime данные
    pub fn save_runtime_data(&self, path: &Path) -> Result<(), Error> {
        let data = RuntimeFeedbackData {
            user_connections: self.user_connections.read().clone(),
            runtime_tokens: self.runtime_tokens.read().clone(),
        };

        let json = serde_json::to_string(&data)?;
        std::fs::write(path, json)?;
        Ok(())
    }

    /// Загрузить runtime данные
    pub fn load_runtime_data(&mut self, path: &Path) -> Result<(), Error> {
        let json = std::fs::read_to_string(path)?;
        let data: RuntimeFeedbackData = serde_json::from_str(&json)?;

        *self.user_connections.write() = data.user_connections;
        *self.runtime_tokens.write() = data.runtime_tokens;
        Ok(())
    }
}
```

**Интеграция с системой:**
- Вызывать `save_runtime_data()` при shutdown
- Вызывать `load_runtime_data()` при startup
- Опционально: автосохранение каждые N минут

**Оценка:** 2-3 часа
**Приоритет:** 🟡 СРЕДНИЙ

---

#### Опционально #5: Query API для других модулей

**Зачем:**
IntuitionEngine должен видеть user connections для генерации proposals.

**Решение:**

```rust
impl FeedbackProcessor {
    /// Получить все connections для токена
    pub fn get_connections(&self, token_id: u32) -> Vec<ConnectionV3> {
        let conns = self.user_connections.read();
        conns.iter()
            .filter(|((a, b), _)| *a == token_id || *b == token_id)
            .map(|(_, conn)| *conn)
            .collect()
    }

    /// Экспорт всех user connections
    pub fn export_connections(&self) -> HashMap<(u32, u32), ConnectionV3> {
        self.user_connections.read().clone()
    }
}
```

**Интеграция с IntuitionEngine:**
```rust
// В IntuitionEngine slow path:
let user_conns = feedback_processor.export_connections();

for ((a, b), mut conn) in user_conns {
    // Собрать статистику из ExperienceStream
    let stats = self.collect_connection_stats(a, b)?;

    // Сгенерировать proposal
    if let Some(proposal) = stats.generate_confidence_proposal(&conn, 20) {
        // Применить через FeedbackProcessor
        feedback_processor.apply_connection_proposal(proposal)?;
    }
}
```

**Оценка:** 3-4 часа
**Приоритет:** 🟡 СРЕДНИЙ

---

### Итоговый план для v1.1.0

**Минимальный набор (1-2 дня):**
1. ✅ Блокер #1: signal_id → token_id mapping (Вариант 1A)
2. ✅ Требование #3: Runtime токены без embeddings
3. ✅ Базовая реализация apply_correction/association

**Полный набор (3-5 дней):**
4. ✅ Требование #4: Persistence
5. ✅ Опционально #5: Query API
6. ✅ Интеграция с IntuitionEngine
7. ✅ Tests + документация

**Для v1.2.0:**
- Блокер #2: token_id в ExperienceEvent (breaking change)
- Embeddings для runtime токенов (ML модель)
- Grid integration для runtime токенов

**Статус v1.0.0:** Оставить как заглушку с подробной документацией

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

## 5. Архитектурные открытия

### 5.1. Graph является мертвым кодом (КРИТИЧНО) 🔴

**Дата открытия:** 2026-01-13
**Статус:** Требует решения перед v1.0.0

**Обнаружено:**

После детального анализа зависимостей выяснено:

1. **Graph не используется в production коде**
   - ❌ IntuitionEngine - использует ExperienceStream + ADNA + Reflex Layer
   - ❌ ActionController - не зависит от Graph
   - ❌ Gateway/Normalizer - использует Bootstrap HashMap, не Graph
   - ❌ FeedbackProcessor - не использует Graph
   - ❌ HybridLearning - работает с ConnectionV3 proposals, не с Graph

2. **Graph используется ТОЛЬКО в:**
   - ✅ Tests (unit tests, integration tests)
   - ✅ Benchmarks (измерение производительности)
   - ✅ Bootstrap (создает edges при инициализации, но они не читаются)
   - ✅ RuntimeStorage (вызывает add_node, но результат не используется)
   - ✅ SignalExecutor (spreading_activation) - **НЕ ВЫЗЫВАЕТСЯ НИГДЕ**

3. **Spreading Activation - orphan feature**
   ```
   graph.spreading_activation() вызывается только в:
   - Benchmarks (graph_bench.rs)
   - Tests (graph.rs, bootstrap.rs)
   - SignalExecutor::execute() - но сам SignalExecutor НЕ используется!
   ```

4. **Картина мира строится БЕЗ Graph:**
   ```
   Signal → Gateway → Bootstrap.get_concept() (HashMap!)
                   ↓
                   Token → Grid.find_neighbors() (spatial search)
                   ↓
                   IntuitionEngine (Fast Path: Reflex, Slow Path: ADNA)
                   ↓
                   ExperienceStream (rewards, learning)
   ```

**Файлы для анализа:**
- [src/graph.rs](src/core_rust/src/graph.rs) - 1400 строк кода
- [src/executors/signal_executor.rs](src/core_rust/src/executors/signal_executor.rs) - SignalExecutor
- [src/bootstrap.rs:505](src/core_rust/src/bootstrap.rs#L505) - weave_connections()
- [docs/specs/SignalSystem_v1_1.md](docs/specs/SignalSystem_v1_1.md) - нереализованная спека

**Метрики:**
- Graph code: ~1400 LOC
- Tests/benchmarks: ~800 LOC
- **Production usage: 0 LOC**

**Почему это произошло:**

1. Название проекта "NeuroGraph" → граф казался важным
2. Spreading activation планировалась для SignalSystem v1.1 (не реализована)
3. Graph как кеш для Grid KNN - но Grid сам делает эту работу
4. Bootstrap создает edges, но потом использует только concepts (HashMap)

**Варианты решения:**

#### Вариант A: Удалить Graph (рекомендуется для v1.1.0)

**Что удалить:**
```rust
// src/graph.rs - полностью
// src/executors/signal_executor.rs - полностью
// src/bootstrap.rs:
//   - graph: Graph field
//   - weave_connections() метод
//   - spreading activation tests
// src/runtime_storage.rs:
//   - graph.add_node() calls
```

**Что сохранить:**
- ConnectionV3 (структура данных, НЕ зависит от Graph!)
- Grid (spatial indexing, основа системы)
- Bootstrap (concepts HashMap + PCA)

**Преимущества:**
- ✅ Убрать 1400+ строк мертвого кода
- ✅ Упростить архитектуру
- ✅ П2 (Feedback connections) становится тривиальным
- ✅ Честность перед пользователями

**Недостатки:**
- ❌ Название "NeuroGraph" без графа (но Grid есть!)
- ❌ Нужно обновить документацию

**Оценка:** 1-2 дня
**Риск:** Низкий (код не используется)

#### Вариант B: Реализовать SignalSystem v1.1 (НЕ рекомендуется)

**Что делать:**
- Реализовать спеку SignalSystem v1.1
- Интегрировать SignalExecutor в Gateway
- Добавить API endpoints для spreading activation
- Написать документацию

**Преимущества:**
- ✅ Граф начнет использоваться
- ✅ Spreading activation как feature

**Недостатки:**
- ❌ 2-3 недели работы
- ❌ Неясная ценность для пользователей
- ❌ Grid уже делает похожую работу (spatial neighbors)

**Оценка:** 2-3 недели
**Риск:** Высокий

#### Вариант C: Оставить как есть (для v1.0.0)

**Что делать:**
- Ничего
- Задокументировать в DEFERRED.md
- Отметить в Release Notes как "unused code"

**Преимущества:**
- ✅ Нулевые затраты
- ✅ Не ломаем ничего перед релизом

**Недостатки:**
- ❌ 1400+ строк мертвого кода в v1.0.0
- ❌ Путаница для контрибьюторов

**Оценка:** 0 дней
**Риск:** Нулевой

---

**Рекомендация:**

**Для v1.0.0:** Вариант C (оставить как есть)
- Release Candidate не время для больших изменений
- Задокументировать открытие
- Пометить Graph как @deprecated в комментариях

**Для v1.1.0:** Вариант A (удалить Graph)
- После стабильного релиза
- С обновлением документации
- С миграцией на HashMap connections для П2

**Приоритет:** 🔴 ВЫСОКИЙ (архитектурное решение)
**Блокирует:** П2 (Feedback connections) - упрощение
**Решение:** Отложить до v1.1.0, задокументировать

---

## 6. Metrics & Tracking

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
