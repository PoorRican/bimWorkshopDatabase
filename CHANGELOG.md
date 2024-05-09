# CHANGELOG

## 0.0.6 (2024-05-9)

- Change `generate_all_values` to generate `Parameter` objects instead of dictionaries

## 0.0.5 (2024-05-5)

- Make `Omniclass.number` optional

## 0.0.4-3 (2024-04-6)

- Added parts to `EXCLUDE_LIST` which were identifying false-positives based on database analysis

## 0.0.4-2 (2024-04-6)

- HOT FIX: Refine part in `EXCLUDE_LIST` which was identifying false-positives

---

## 0.0.4-1 (2024-04-6)

- HOT FIX: Refine part in `EXCLUDE_LIST` which was identifying false-positives

---

## 0.0.4 (2024-04-6)

### Bug fixes

- Fix part in `EXCLUDE_LIST` which was identifying false-positives

---

## 0.0.3-3 (2024-04-5)

### Bug fixes

- Fixed a bug in `builder_functions.generate_values` where numbers were not being parsed as strings

---

## 0.0.3-2 (2024-03-19)

- Handle 429 errors in `BaseSearchHandler` by retrying, instead of retrying for all 4XX errors.
- Handle other errors in `BaseSearchHandler` by raising `RuntimeError`.

---

## 0.0.3-1 (2024-03-19)

- Handle 4XX errors in `BaseSearchHandler` by retrying.
- If errors persist in `BaseSearchHandler`, `RuntimeError` is raised.