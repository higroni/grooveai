# Legal Parser - Problem Analysis

## Date: 2026-06-06

## Overview
Integration test revealed that the Legal Parser (Module 4) is not correctly parsing the document structure. The parser successfully identifies 312 articles but fails to capture proper headings and content.

## Identified Problems

### 1. Incorrect Heading Assignment

**Example: Član 1**

**Source Text (latinized):**
```
1. Predmet
Član 1.
Mišljenja, modeli i literaturaSudska praksa
Prava, obaveze i odgovornosti iz radnog odnosa, odnosno po osnovu rada, uređuju se ovim
zakonom i posebnim zakonom, u skladu sa ratifikovanim međunarodnim konvencijama.
```

**Current Parser Output:**
```json
{
  "number": "1",
  "heading": "Mišljenja, modeli i literaturaSudska praksa",
  "content_text": ""
}
```

**Expected Output:**
```json
{
  "number": "1",
  "heading": "Predmet",
  "content_text": "Prava, obaveze i odgovornosti iz radnog odnosa, odnosno po osnovu rada, uređuju se ovim zakonom i posebnim zakonom, u skladu sa ratifikovanim međunarodnim konvencijama.\nPrava, obaveze i odgovornosti iz radnog odnosa uređuju se i kolektivnim ugovorom i ugovorom o radu, a pravilnikom o radu, odnosno ugovorom o radu – samo kada je to ovim zakonom određeno."
}
```

### 2. Empty Content Text

All parsed articles have `content_text: ""`, meaning the parser is not capturing the actual article content.

### 3. Truncated Headings

**Example: Član 179**

**Source Text:**
```
član 179. stav 3. tačka 2) Zakona o radu – u delu koji se odnosi na obavezu osiguranog lica da
obavesti poslodavca o oceni lekarske komisije o privremenoj sprečenosti za rad
```

**Current Parser Output:**
```json
{
  "number": "179",
  "heading": "stav 3. tačka 2) Zakona o radu – u delu koji se odnosi na obavezu osiguranog lica da"
}
```

The heading is cut off mid-sentence.

## Root Causes

### 1. Document Structure Misunderstanding

The Serbian legal document has this structure:
```
[Section Number]. [Section Title]
Član [N].
[Metadata/References - optional]
[Article Content - multiple paragraphs]
```

Current parser assumes:
```
Član [N].
[Next line is heading]
```

### 2. Multi-line Heading Logic Issue

The parser's multi-line heading logic (lookahead) is capturing the wrong lines:
- It captures "Mišljenja, modeli i literaturaSudska praksa" (metadata)
- It should capture "Predmet" (actual section title from line BEFORE "Član N.")

### 3. Content Extraction Not Implemented

The parser identifies article boundaries but doesn't extract the content between articles.

## Document Structure Analysis

### Actual Structure Pattern:

```
[Optional: Section number and title]
Član [number].
[Optional: Metadata line - "Mišljenja, modeli i literaturaSudska praksa"]
[Content paragraph 1]
[Content paragraph 2]
...
[Next article starts]
```

### Key Observations:

1. **Section titles** appear BEFORE "Član N." (e.g., "1. Predmet")
2. **Metadata lines** appear AFTER "Član N." and are NOT part of content
3. **Content** starts after metadata and continues until next "Član" or document end
4. **Paragraphs** within articles are not marked with "(1)", "(2)" - they're just text blocks

## Required Fixes

### 1. Heading Extraction Logic

Need to look BACKWARD from "Član N." to find section title:
- Check previous 1-3 lines for pattern: `^\d+\.\s+(.+)$`
- If found, use as heading
- If not found, heading is empty or use first line of content

### 2. Content Extraction

After identifying article start ("Član N."):
1. Skip metadata line if present (pattern: `^Mišljenja.*praksa$`)
2. Collect all lines until next "Član" or end of document
3. Store as `content_text`

### 3. Multi-line Handling

Current multi-line logic needs revision:
- Don't use lookahead for heading (it captures wrong lines)
- Use lookbehind for section titles
- Use lookahead for content collection

## Test Cases Needed

1. Article with section title (Član 1 - "Predmet")
2. Article without section title
3. Article with metadata line
4. Article with multiple paragraphs
5. Article with sub-items (stavovi, tačke)
6. Last article in document

## Implementation Priority

1. **HIGH**: Fix heading extraction (lookbehind for section titles)
2. **HIGH**: Implement content extraction
3. **MEDIUM**: Handle metadata lines properly
4. **MEDIUM**: Improve multi-line content handling
5. **LOW**: Add paragraph/point detection within articles

## Next Steps

1. Review `modules/legal_parser/service.py` - `_parse_hierarchical()` method
2. Modify article detection logic to:
   - Look backward for section titles
   - Skip metadata lines
   - Extract content until next article
3. Update tests to verify correct heading and content extraction
4. Re-run integration test
