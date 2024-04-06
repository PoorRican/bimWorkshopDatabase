# CHANGELOG

## 0.0.4 (2023-04-6)

### Bug fixes

- Fix part in `EXCLUDE_LIST` which was identifying false-positives

---

## 0.0.3-3 (2023-04-5)

### Bug fixes

- Fixed a bug in `builder_functions.generate_values` where numbers were not being parsed as strings

---

## 0.0.3-2 (2023-03-19)

- Handle 429 errors in `BaseSearchHandler` by retrying, instead of retrying for all 4XX errors.
- Handle other errors in `BaseSearchHandler` by raising `RuntimeError`.

---

## 0.0.3-1 (2023-03-19)

- Handle 4XX errors in `BaseSearchHandler` by retrying.
- If errors persist in `BaseSearchHandler`, `RuntimeError` is raised.