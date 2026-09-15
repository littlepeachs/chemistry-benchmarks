# English-Language Edition

The README, protocol notes, validation notes, generated results narrative, historical script comments, and console messages are presented in English.

## Preserved Evidence

Raw predictions, judge responses, reference answers, subject labels, and model/tokenizer configurations are not translated. Some original model outputs may contain non-English text. Changing them would alter the experimental evidence and its checksums. Machine-readable numerical results are also unchanged.

The historical scripts in `legacy/` are English-commented copies, not byte-identical copies of their original versions. Only comments and console-print text have been translated. Model prompts, answer extraction, scoring, data conversion, generation settings, and control flow remain unchanged. Existing historical comments were translated without treating them as verified descriptions of the code.

## Upstream Card Translations

Two passages were localized:

- `metadata/dataset_cards/ChemBench4K.md`: the Chinese dataset-description sentence was translated into English. Its original claim of 4,100 questions is preserved as source-card text; this archive evaluates the 4,009-record test subset, as documented separately.
- `metadata/model_snapshots/ChemLLM-7B-Chat/README.md`: the parenthetical Chinese name of Shanghai AI Laboratory in the example system prompt was removed because the English name immediately precedes it. This is a documentation-only localization; prompts in the executable evaluation scripts are unchanged.

These two cards are therefore localized copies rather than exact upstream snapshots. Their original versions remain available in Git commit `aefae90e9fb7e5539f355a7e6b1f9ca1786ff765` and at the pinned upstream revisions recorded in the metadata. Machine-readable model configuration snapshots are unchanged.

The archive SHA-256 manifest covers the English edition. Source dataset hashes, prepared-input hashes, and raw-result hashes remain unchanged.
