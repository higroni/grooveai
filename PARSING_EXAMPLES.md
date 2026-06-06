# Legal Parser - Detailed Examples Analysis

## Example 1: Article with Section Title and Metadata

**Source:**
```
1. Predmet
Član 1.
Mišljenja, modeli i literaturaSudska praksa
Prava, obaveze i odgovornosti iz radnog odnosa, odnosno po osnovu rada, uređuju se ovim
zakonom i posebnim zakonom, u skladu sa ratifikovanim međunarodnim konvencijama.
Prava, obaveze i odgovornosti iz radnog odnosa uređuju se i kolektivnim ugovorom i ugovorom
o radu, a pravilnikom o radu, odnosno ugovorom o radu – samo kada je to ovim zakonom
određeno.
```

**Expected Parse:**
```json
{
  "number": "1",
  "heading": "Predmet",
  "content_text": "Prava, obaveze i odgovornosti iz radnog odnosa, odnosno po osnovu rada, uređuju se ovim zakonom i posebnim zakonom, u skladu sa ratifikovanim međunarodnim konvencijama.\nPrava, obaveze i odgovornosti iz radnog odnosa uređuju se i kolektivnim ugovorom i ugovorom o radu, a pravilnikom o radu, odnosno ugovorom o radu – samo kada je to ovim zakonom određeno.",
  "metadata": {
    "references": "Mišljenja, modeli i literaturaSudska praksa"
  }
}
```

## Example 2: Article with Section Title, No Metadata

**Source:**
```
2. Značenje pojedinih pojmova
Član 5.
Mišljenja, modeli i literaturaSudska praksa
Zaposleni, u smislu ovog zakona, jeste fizičko lice koje je u radnom odnosu kod poslodavca.
Poslodavac, u smislu ovog zakona, jeste domaće, odnosno strano pravno ili fizičko lice koje
zapošljava, odnosno radno angažuje, jedno ili više lica.
```

**Expected Parse:**
```json
{
  "number": "5",
  "heading": "Značenje pojedinih pojmova",
  "content_text": "Zaposleni, u smislu ovog zakona, jeste fizičko lice koje je u radnom odnosu kod poslodavca.\nPoslodavac, u smislu ovog zakona, jeste domaće, odnosno strano pravno ili fizičko lice koje zapošljava, odnosno radno angažuje, jedno ili više lica."
}
```

## Example 3: Article WITHOUT Section Title, NO Metadata

**Source:**
```
Član 7.
Udruženjem poslodavaca, u smislu ovog zakona, smatra se samostalna, demokratska i nezavisna
organizacija u koju poslodavci dobrovoljno stupaju radi predstavljanja, unapređenja i
zaštite svojih poslovnih interesa, u skladu sa zakonom.
```

**Expected Parse:**
```json
{
  "number": "7",
  "heading": "",
  "content_text": "Udruženjem poslodavaca, u smislu ovog zakona, smatra se samostalna, demokratska i nezavisna organizacija u koju poslodavci dobrovoljno stupaju radi predstavljanja, unapređenja i zaštite svojih poslovnih interesa, u skladu sa zakonom."
}
```

## Example 4: Article with Metadata

**Source:**
```
Član 4.
Mišljenja, modeli i literaturaSudska praksa
Opšti i poseban kolektivni ugovor moraju biti u saglasnosti sa zakonom.
Kolektivni ugovor kod poslodavca, pravilnik o radu i ugovor o radu moraju biti u
saglasnosti sa zakonom, a kod poslodavca iz čl. 256. i 257. ovog zakona – i sa opštim i
posebnim kolektivnim ugovorom.
```

**Expected Parse:**
```json
{
  "number": "4",
  "heading": "",
  "content_text": "Opšti i poseban kolektivni ugovor moraju biti u saglasnosti sa zakonom.\nKolektivni ugovor kod poslodavca, pravilnik o radu i ugovor o radu moraju biti u saglasnosti sa zakonom, a kod poslodavca iz čl. 256. i 257. ovog zakona – i sa opštim i posebnim kolektivnim ugovorom."
}
```

## Pattern Recognition Rules

### 1. Section Title Detection (Lookbehind)
```python
# Check 1-3 lines BEFORE "Član N." for pattern:
section_title_pattern = r'^\d+\.\s+(.+)$'

# Example matches:
"1. Predmet" -> heading = "Predmet"
"2. Značenje pojedinih pojmova" -> heading = "Značenje pojedinih pojmova"
```

### 2. Metadata Line Detection (Skip)
```python
# Line immediately AFTER "Član N." matching:
metadata_pattern = r'^Mišljenja.*praksa$'

# If matched, skip this line and start content from next line
```

### 3. Content Extraction
```python
# After article marker and optional metadata:
# Collect all lines until:
# - Next "Član N." pattern
# - End of document
# - Empty line followed by section marker (^\d+\.\s+)
```

### 4. Article Marker
```python
article_pattern = r'^[ČC]lan\s+(\d+[a-z]?)\.?\s*$'
# Note: Heading on SAME line is rare, usually on separate line
```

## Algorithm Pseudocode

```python
def parse_articles(lines):
    articles = []
    i = 0
    
    while i < len(lines):
        # Check if current line is article marker
        if matches_article_pattern(lines[i]):
            article_number = extract_number(lines[i])
            
            # Look backward for section title (1-3 lines)
            heading = find_section_title_backward(lines, i)
            
            # Move to next line
            i += 1
            
            # Check if next line is metadata (skip if yes)
            if i < len(lines) and is_metadata_line(lines[i]):
                i += 1
            
            # Collect content until next article or end
            content_lines = []
            while i < len(lines) and not matches_article_pattern(lines[i]):
                # Stop if we hit a new section marker
                if matches_section_marker(lines[i]):
                    break
                content_lines.append(lines[i])
                i += 1
            
            content_text = '\n'.join(content_lines).strip()
            
            articles.append({
                'number': article_number,
                'heading': heading,
                'content_text': content_text
            })
        else:
            i += 1
    
    return articles
```

## Current vs Expected Behavior

### Current Behavior:
- ❌ Uses lookahead for heading (captures metadata line)
- ❌ Doesn't extract content
- ❌ Doesn't handle section titles
- ✅ Correctly identifies article markers

### Expected Behavior:
- ✅ Use lookbehind for section titles
- ✅ Skip metadata lines
- ✅ Extract full content until next article
- ✅ Handle articles with/without section titles

## Implementation Changes Needed

### File: `modules/legal_parser/service.py`

1. **Add section title pattern:**
```python
SECTION_TITLE_PATTERN = re.compile(r'^\d+\.\s+(.+)$')
```

2. **Add metadata pattern:**
```python
METADATA_PATTERN = re.compile(r'^Mišljenja.*praksa$')
```

3. **Modify `_parse_hierarchical()` method:**
   - Add lookbehind logic for section titles
   - Add metadata line detection and skipping
   - Implement content extraction loop
   - Store content in `content_text` field

4. **Update tests:**
   - Add test for section title extraction
   - Add test for metadata line skipping
   - Add test for content extraction
   - Add test for articles without section titles
