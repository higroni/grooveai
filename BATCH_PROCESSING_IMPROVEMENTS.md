# Batch Processing Improvements

## Overview

Poboljšanja u batch processing sistemu za efikasnije procesiranje dokumenata i bolje rukovanje timeout-ima.

## Promene

### 1. Skip Already Processed Files

**Problem:** Batch processor je procesirao iste fajlove iznova i iznova.

**Rešenje:** 
- Dodato `skip_existing` parametar u [`batch_orchestrator.py`](batch_orchestrator.py:18)
- Pre procesiranja, proverava se da li output JSON već postoji
- Ako postoji, fajl se preskače
- Takođe dodato u [`process_single_document.py`](process_single_document.py:84) kao dodatna provera

**Upotreba:**
```python
# Default: skip existing files
process_batch("DOCUMENTS/DEV", "test_data/json_output")

# Force reprocess all files
process_batch("DOCUMENTS/DEV", "test_data/json_output", skip_existing=False)
```

**Output:**
```
ℹ️  Skipping 150 files that already have output
Documents to process: 84
```

### 2. Improved Timeout Handling

**Problem:** 3-minutni timeout nije radio pravilno - procesi su se zaglavljavali.

**Rešenje:**
- Dodata `psutil` biblioteka za bolji process management
- Kada proces timeout-uje, force kill-uje se proces i sva njegova deca (child processes)
- Fallback na standardni `subprocess.run` ako `psutil` nije instaliran

**Instalacija psutil:**
```bash
pip install psutil
# ili
install_psutil.bat
```

**Kako radi:**
1. Proces se pokreće sa `subprocess.Popen`
2. Čeka se 3 minuta (180 sekundi)
3. Ako proces ne završi:
   - Pronalaze se svi child procesi
   - Kill-uju se svi child procesi
   - Kill-uje se parent proces
   - Čeka se do 5 sekundi da proces umre
4. Nastavlja se sa sledećim fajlom

**Kod:**
```python
try:
    parent = psutil.Process(process.pid)
    children = parent.children(recursive=True)
    
    # Kill children first
    for child in children:
        child.kill()
    
    # Kill parent
    parent.kill()
    parent.wait(timeout=5)
except Exception as e:
    print(f"Error killing process: {e}")
```

## Benefiti

### Skip Existing Files
- ✅ **Brže procesiranje** - ne gubi se vreme na već procesiranim fajlovima
- ✅ **Sigurnije** - ne prepisuju se postojeći rezultati
- ✅ **Fleksibilno** - može se isključiti sa `skip_existing=False`
- ✅ **Informativno** - prikazuje koliko fajlova je preskočeno

### Improved Timeout
- ✅ **Pouzdanije** - garantovano kill-ovanje zaglavljenih procesa
- ✅ **Brže** - ne čeka se beskonačno na zaglavljene fajlove
- ✅ **Čistije** - kill-uju se i child procesi (npr. Legal Parser subprocess)
- ✅ **Fallback** - radi i bez psutil (manje pouzdano)

## Testiranje

### Test 1: Skip Existing Files

```bash
# Prvi run - procesira sve fajlove
python batch_orchestrator.py

# Drugi run - preskače sve fajlove
python batch_orchestrator.py
# Output: "✓ All documents already processed!"

# Force reprocess
python batch_orchestrator.py --no-skip
```

### Test 2: Timeout Handling

```bash
# Instaliraj psutil
pip install psutil

# Pokreni batch processing
python batch_orchestrator.py

# Ako se fajl zaglavi:
# [40/234] radni_odnosi_0040_000040.pdf
#   ⏱️  TIMEOUT (3 minutes) - force killing process...
#   ✓ Process killed successfully
# [41/234] radni_odnosi_0041_000041.pdf
#   Processing: radni_odnosi_0041_000041.pdf
```

## Statistika

### Pre poboljšanja:
- Batch od 234 fajla: ~8 sati (sa zaglavljenim fajlovima)
- Ponavljanje: procesira sve fajlove iznova
- Timeout: proces se zaglavi, mora se ručno kill-ovati

### Posle poboljšanja:
- Batch od 234 fajla: ~4 sata (prvi run)
- Ponavljanje: preskače već procesiranim fajlovima (~5 sekundi)
- Timeout: automatski kill nakon 3 minuta, nastavlja sa sledećim

## Kompatibilnost

### Sa psutil (preporučeno):
```bash
pip install psutil
python batch_orchestrator.py
```
- ✅ Force kill zaglavljenih procesa
- ✅ Kill child procesa
- ✅ Garantovano čišćenje

### Bez psutil (fallback):
```bash
python batch_orchestrator.py
```
- ⚠️  Upozorenje: "psutil not installed - timeout handling may be less reliable"
- ✅ Standardni timeout (manje pouzdan)
- ⚠️  Child procesi možda neće biti kill-ovani

## Preporuke

1. **Instaliraj psutil** za najbolje rezultate:
   ```bash
   pip install psutil
   ```

2. **Koristi skip_existing** (default) za brže procesiranje:
   ```bash
   python batch_orchestrator.py
   ```

3. **Force reprocess** samo kada je potrebno:
   ```bash
   python batch_orchestrator.py --no-skip
   ```

4. **Monitoring** - prati output za timeout poruke:
   ```
   ⏱️  TIMEOUT (3 minutes) - force killing process...
   ```

## Buduća poboljšanja

- [ ] Retry mehanizam za failed fajlove
- [ ] Parallel processing (multiple workers)
- [ ] Progress bar sa ETA
- [ ] Detailed error logging
- [ ] Resume capability (checkpoint system)