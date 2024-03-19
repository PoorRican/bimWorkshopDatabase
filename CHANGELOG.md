# CHANGELOG

## 0.0.3-1 (2023-03-19)

- Handle 4XX errors in `BaseSearchHandler` by retrying.
- If errors persist in `BaseSearchHandler`, `RuntimeError` is raised.