# Opis projektu

Aplikacja do generowania miniaturek do filmów na YouTube na podstawie przesłanego filmu. Projekt wykorzystuje modele AI do następujących zadań:

1. **Transkrypcja wideo** - Tworzenie transkrypcji tekstowej z przesłanego pliku wideo.
2. **Streszczanie transkrypcji** - Generowanie zwięzłego streszczenia z transkrypcji wideo.
3. **Generowanie grafiki miniaturki** - Tworzenie obrazu miniaturki na podstawie wygenerowanego streszczenia i zadanych parametrów wizualnych (styl i kolor)

Projekt składa się z:
- Frontendu napisanego w JavaScript przy użyciu frameworka Next.js, odpowiedzialengo za interfejs aplikacji
- Backend napisany w Pythonie przy użyciu frameworka FastAPI, który obsługuje modele AI oraz logikę aplikacji

# Wymagane biblioteki systemowe

Przed rozpoczęciem instalacji oraz uruchomienia projektu należy upewnić się, że zainstalowne są następujące biblioteki i narzędzia systemowe:
- **Python 3.9 lub nowszy**
- **Node.js 16 lub nowszy**
- **CUDA**
- **ffmpeg** (do obsługi przetwarzania wideo)

# Instalacja oraz uruchomienie projektu

## Backend (Python)

1. Sklonuj lub pobierz repozytorium.
2. Utwórz i aktywuj wirtualne środowisko:

```
python -m venv venv
source venv/bin/activate  # Linux/MacOS
venv\Scripts\activate   # Windows
```
3. Zainstaluj wymagane biblioteki Python:

```
pip install -r requirements.txt
```
4. Upewnij się, że wymagane biblioteki systemowe są poprawnie zainstalowane.
5. Uruchom serwer backendu:

```
uvicorn main:app --reload
```
## Frontend (JavaScript)

1. Przejdź do folderu frontendu
2. Zainstaluj zależności:

```
npm install
```
3. Uruchom aplikację frontendową:

```
npm run dev
```
4. Frontend będzie dostępny pod adresem `http://localhost:3000`.

# Uwaga

Jeśli korzystasz z GPU, upewnij się, że zainstalowałeś PyTorch z obsługą CUDA:

```
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```
# Autorzy

- Piotr Kaliński
- Andrzej Kaliński
- Łukasz Staniszewski
