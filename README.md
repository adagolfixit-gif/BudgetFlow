# BudgetFlow v0.3.0 Web

Wersja przygotowana bezpośrednio pod GitHub Pages.

## Publikacja
1. Utwórz na GitHub nowe repozytorium, np. `budgetflow`.
2. Ustaw je jako Public, jeśli używasz GitHub Free.
3. Wejdź do repozytorium i użyj `Add file` → `Upload files`.
4. Wgraj:
   - `index.html`
   - `.nojekyll`
   - opcjonalnie `README.md`
5. Zatwierdź commit do gałęzi `main`.
6. Wejdź w `Settings` → `Pages`.
7. W `Build and deployment` wybierz:
   - Source: `Deploy from a branch`
   - Branch: `main`
   - Folder: `/ (root)`
8. Kliknij `Save`.

Po publikacji GitHub pokaże adres w rodzaju:
`https://TWOJ_LOGIN.github.io/budgetflow/`

Ten adres możesz dodać do zakładek Chrome.

## Ważne
GitHub Pages publikuje zawartość strony publicznie. Nie umieszczaj w repozytorium pliku `.bfdb` ani żadnych prywatnych danych finansowych.

Dane aplikacji są szyfrowane i przechowywane lokalnie w przeglądarce. Zaszyfrowany backup `.bfdb` możesz eksportować ręcznie.

## Następny etap
Wersja v0.3.x może dostać integrację z Google Drive API, dzięki której zaszyfrowana baza będzie synchronizowana z Dyskiem Google bez instalowania Google Drive for desktop.
