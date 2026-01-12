# Rust Binaries Compilation Status

**Date:** 2026-01-12
**Version:** v0.47.0
**Status Check:** Phase 4 - Final Polish

---

## ✅ Enabled Bins (All Compile Successfully)

All enabled binaries compile without errors, only warnings about unused code:

| Binary | Features Required | Status | Notes |
|--------|-------------------|--------|-------|
| **experience-stream-demo** | demo-tokio | ✅ Compiles | ExperienceStream v2.1 demonstration |
| **intuition-demo** | demo-tokio | ✅ Compiles | IntuitionEngine pattern detection |
| **learning-loop-demo** | demo-tokio | ✅ Compiles | Learning feedback loop |
| **action-controller-demo** | demo-tokio | ✅ Compiles | Action execution system |
| **persistence-demo** | demo-tokio, persistence | ✅ Compiles | PostgreSQL persistence layer |
| **check_sizes** | none | ✅ Compiles | Memory size verification tool |

### Common Warnings (Non-Critical)

All enabled bins generate 11 common warnings about unused code:
- Unused methods (e.g., `BucketKey::neighbors`)
- Unused struct fields (config fields, module IDs)
- Unused functions (e.g., `edit_distance` in normalizer)

These warnings don't affect functionality and can be cleaned up in v1.1.0+.

---

## ⏸️ Disabled Bins (Need API Updates for v1.1.0+)

### Disabled Because of API Changes

The disabled bins use old API that has evolved. They were intentionally disabled during development when APIs changed.

**Note:** All bins use `neurograph_core` for imports (correct). The library exports this name for Rust bins, while using `_core` as internal library name in Cargo.toml for Python FFI compatibility.

### Issues by Binary

#### 1. **demo.rs** (token-demo)
**Status:** 4 errors - Packed field references
**Cargo.toml Comment:** "Temporarily disabled due to packed struct reference errors"

```rust
error[E0793]: reference to packed field is unaligned
  --> src/bin/demo.rs:87:41
   |
87 |     println!("   Weight preserved: {}", token_copy.weight);
   |                                         ^^^^^^^^^^^^^^^^^
```

**Root Cause:** Token struct uses `#[repr(packed)]` for memory efficiency. Direct field references create unaligned pointers, which is UB.

**Fix Required:** Copy packed fields to local variables before printing:
```rust
let weight = token_copy.weight;  // Copy to aligned local
println!("   Weight preserved: {}", weight);
```

**Estimated Effort:** 1-2 hours (4 locations to fix)

---

#### 2. **grid-demo.rs**
**Status:** 1 error - Type mismatch
**Cargo.toml Comment:** "Temporarily disabled due to compilation errors"

```rust
error[E0308]: mismatched types
```

**Root Cause:** Grid field calculation API has evolved since this demo was written.

**Fix Required:** Update to use current Grid API (check working examples in tests/).

**Estimated Effort:** 1-2 hours

---

#### 3. **api.rs** (neurograph-api)
**Status:** 2 errors - Type mismatches
**Cargo.toml Comment:** Not listed (implicitly disabled)

**Root Cause:** The Rust REST API in `src/api/` module has been replaced/updated with FastAPI Python implementation. This demo uses old API.

**Decision:**
- Option A: Update to match current Rust API module
- Option B: Mark as deprecated (FastAPI is primary API now)
- **Recommended:** Option B - Document that FastAPI (src/api/) is the production API

**Estimated Effort:** 4-6 hours (or mark as deprecated)

---

#### 4. **repl.rs** (neurograph-repl)
**Status:** 2 errors - Type mismatches
**Cargo.toml Comment:** "Temporarily disabled due to RwLock migration"

**Root Cause:** CuriosityDrive and Gateway APIs have evolved. REPL uses outdated interfaces.

**Fix Required:** Update to current API signatures (check action-controller-demo for reference).

**Estimated Effort:** 3-4 hours

---

#### 5. **integration-demo.rs**
**Status:** 10 errors - Multiple API changes
**Cargo.toml Comment:** "Temporarily disabled due to compilation errors"

**Issues:**
- E0432: Unresolved imports (`connection_flags`, `active_levels` no longer exported)
- E0308: Type mismatches
- E0599: `ConnectionV3::set_flag()` method removed
- E0609: Field access changed from tuples to arrays

**Root Cause:** Major API evolution:
- Connection v3.0 API redesign
- Flag management internalized
- Coordinate representation changed

**Fix Required:** Extensive rewrite to use current Connection v3.0 API.

**Estimated Effort:** 6-8 hours (most complex)

---

#### 6. **connection-demo.rs** & **graph-demo.rs**
**Status:** Missing files
**Cargo.toml Comment:** "Temporarily disabled", "Missing file"

**Issue:** Source files don't exist in src/bin/ directory.

**Options:**
- Create new demos for these features
- Remove from Cargo.toml comments

**Estimated Effort:** N/A (files don't exist)

---

## 📊 Summary

| Category | Count | Status |
|----------|-------|--------|
| **Working Bins** | 6 | ✅ All compile successfully |
| **Disabled Bins** | 5 | ⏸️ Need API updates |
| **Missing Bins** | 2 | ❌ Files don't exist |
| **Total Bins** | 13 | 46% functional |

---

## 🎯 Recommendations

### For v1.0.0 Release
- ✅ **Keep current status** - 6 working demos are sufficient
- ✅ **Document disabled bins** - This file serves as documentation
- ✅ **No critical issues** - All production functionality works via Python API

### For v1.1.0+ (Future Maintenance)
1. **Priority 1:** Fix demo.rs (4 errors, 1-2 hours) - Simple packed field fixes
2. **Priority 2:** Fix grid-demo.rs (1 error, 1-2 hours) - Single API update
3. **Priority 3:** Decide on api.rs (deprecated or update?) - 4-6 hours
4. **Priority 4:** Fix repl.rs (2 errors, 3-4 hours) - Curiosity API updates
5. **Priority 5:** Fix integration-demo.rs (10 errors, 6-8 hours) - Major rewrite

**Total Estimated Effort:** 15-20 hours across all disabled bins

---

## 🚀 Testing Commands

### Test All Working Bins
```bash
cd src/core_rust

# Basic demos
cargo build --bin check_sizes
cargo build --bin experience-stream-demo --features demo-tokio
cargo build --bin intuition-demo --features demo-tokio
cargo build --bin learning-loop-demo --features demo-tokio
cargo build --bin action-controller-demo --features demo-tokio

# Persistence demo (requires PostgreSQL)
cargo build --bin persistence-demo --features "demo-tokio,persistence"
```

### Test Disabled Bins (Will Fail)
```bash
# These will fail with documented errors:
cargo build --bin demo
cargo build --bin grid-demo
cargo build --bin api
cargo build --bin repl
cargo build --bin integration-demo
```

---

## 📝 Notes

- **Library Name:** The crate uses `name = "_core"` in [lib] section of Cargo.toml for Python FFI
- **Rust Module Name:** Bins use `neurograph_core` (re-exported from `_core`)
- **Python Module:** PyO3 exports as `neurograph_core` via `#[pymodule]` attribute
- **Working bins:** Use standard `use neurograph_core::*` imports
- **Disabled bins:** Also use `neurograph_core` (imports are correct, API changes are the issue)

---

**Generated:** 2026-01-12
**Author:** Claude Sonnet 4.5
**Phase:** 4 - Final Polish & Release Preparation
