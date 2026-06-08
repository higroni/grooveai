# Memory Monitor - Uputstvo za korišćenje

## Opis
Skripta za praćenje memorije sistema i top 5 procesa po zauzetoj memoriji, kao u Task Manager-u.

## Instalacija zavisnosti
```bash
pip install psutil
```

## Pokretanje

### Osnovno pokretanje (2s interval)
```bash
python monitor_memory.py
```

ili

```bash
monitor_memory.bat
```

### Sa custom intervalom (npr. 5 sekundi)
```bash
python monitor_memory.py --interval 5
```

ili

```bash
monitor_memory.bat 5
```

### Sa praćenjem specifičnog procesa (npr. python.exe)
```bash
python monitor_memory.py --interval 2 --process python.exe
```

ili

```bash
monitor_memory.bat 2 python.exe
```

## Šta prikazuje

### 1. Sistemska memorija
- **Total**: Ukupna RAM memorija
- **Available**: Dostupna memorija
- **Used**: Iskorišćena memorija (procenat)
- **Free**: Slobodna memorija
- **Vizuelni bar**: Grafički prikaz zauzetosti

### 2. Top 5 procesa
Prikazuje 5 procesa koji zauzimaju najviše memorije:
- **PID**: Process ID
- **Memory**: Zauzeće memorije u MB
- **Process Name**: Ime procesa

### 3. Target proces (opciono)
Ako je specificiran proces (npr. `python.exe`), prikazuje:
- Sve instance tog procesa
- Zauzeće memorije za svaku instancu
- CPU korišćenje

## Primeri korišćenja

### Praćenje batch processora
```bash
# Pokreni batch processor u jednom terminalu
python batch_processor.py --input-dir "D:\POSAO\ZAKON_O_RADU\ZAKON_O_RADU_DOCX" --output-dir batch_output --workers 2

# Pokreni memory monitor u drugom terminalu
monitor_memory.bat 2 python.exe
```

### Dijagnostika memory leak-a
1. Pokreni monitor pre batch processora
2. Prati kako raste memorija tokom procesiranja
3. Identifikuj koji proces zauzima memoriju
4. Ako je `python.exe` na vrhu liste sa rastućom memorijom → memory leak u Python kodu
5. Ako su drugi procesi na vrhu → eksterni problem

## Zaustavljanje
Pritisni `Ctrl+C` za zaustavljanje monitora.

## Interpretacija rezultata

### Normalno ponašanje
```
🖥️  SYSTEM MEMORY:
   Used:      8.5 GB (53.1%)
   
🔝 TOP 5 PROCESSES:
   PID      Memory       Process Name
   12345    450.2 MB     chrome.exe
   67890    320.5 MB     python.exe ⭐
   11111    280.1 MB     Code.exe
```

### Memory leak (problem)
```
🖥️  SYSTEM MEMORY:
   Used:      15.2 GB (95.0%)  ← PROBLEM: Raste do 99%
   
🔝 TOP 5 PROCESSES:
   PID      Memory       Process Name
   67890    8500.5 MB    python.exe ⭐  ← PROBLEM: Python zauzima 8.5GB
   12345    450.2 MB     chrome.exe
```

### Eksterni problem
```
🖥️  SYSTEM MEMORY:
   Used:      15.2 GB (95.0%)  ← PROBLEM: Raste do 99%
   
🔝 TOP 5 PROCESSES:
   PID      Memory       Process Name
   12345    8500.5 MB    some_other.exe  ← Drugi proces je problem
   67890    320.5 MB     python.exe ⭐   ← Python je OK
```

## Troubleshooting

### "Module 'psutil' not found"
```bash
pip install psutil
```

### Monitor ne prikazuje target proces
- Proveri da li je ime procesa tačno (npr. `python.exe`, ne `python`)
- Proveri da li proces radi (Task Manager)

### Ekran treperi
- Povećaj interval: `monitor_memory.bat 5`

## Napomene
- Monitor koristi `psutil` biblioteku za pristup sistemskim informacijama
- Radi na Windows, Linux i macOS
- Ne utiče na performanse sistema (minimalno CPU korišćenje)