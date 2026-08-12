# Del 1 — Sätt upp ett repo med CI/CD

**Beräknad tid:** cirka 120 minuter.

## Syfte

I den här övningen ska ni skapa ett eget GitHub-repository och bygga en CI/CD-pipeline för JensenStore API.

Fokus ligger på att konfigurera repot och automatisera flödet — inte på att skriva tester. Applikationen, Dockerfile och testerna är redan färdiga. De befintliga testerna används som en kvalitetskontroll i pipelinen.

När ni är klara ska en push automatiskt:

1. hämta koden
2. installera dependencies
3. köra den befintliga kvalitetskontrollen
4. bygga en Docker-image
5. publicera imagen till GitHub Container Registry (GHCR)

```text
Kod → push → verifiera → bygg → publicera
          CI                    CD
```

I den här övningen betyder:

- **Continuous Integration:** varje förändring hämtas och verifieras automatiskt.
- **Continuous Delivery:** en godkänd förändring paketeras och publiceras som en körbar image.
- **Deployment:** att imagen faktiskt startas i en miljö. Det görs lokalt här och blir huvudfokus i del 2 med Kubernetes.

## Lärandemål

Efter övningen ska ni kunna:

- skapa ett repo med rätt filer och kataloger
- förklara vad som startar ett GitHub Actions-workflow
- skilja mellan CI, continuous delivery och deployment
- läsa en Actions-logg och hitta steget som misslyckades
- använda `GITHUB_TOKEN` utan att skapa eller skriva in ett eget lösenord
- koppla en publicerad image till den commit som skapade den

## Arbetssätt

Använd samma återkopplingsloop i varje moment:

```text
Ändra → kontrollera lokalt → commit → push → läs Actions-loggen
```

En grön pipeline betyder bara att de steg som faktiskt finns i pipelinen lyckades. Kontrollera därför alltid vilka steg som kördes.

## Tidsplan

| Tid | Moment |
| --- | --- |
| 0–20 min | Skapa repo och filer |
| 20–35 min | Förstå starter-workflowet och göra första push |
| 35–50 min | Koppla befintlig verifiering till CI |
| 50–65 min | Skapa och felsöka ett pipelinefel |
| 65–85 min | Bygga Docker-image lokalt och i CI |
| 85–105 min | Publicera imagen till GHCR |
| 105–115 min | Göra en ny förändring och följa leveransen |
| 115–120 min | Sammanfatta CI/CD-flödet |

## Förberedelser

Ni behöver GitHub-konto, Git, Docker och en kodeditor.

```bash
git --version
docker version
```

**Kontrollpunkt:** båda kommandona visar ett versionsnummer. Om Docker inte kan ansluta till Docker Engine, starta Docker Desktop.

### Windows PowerShell

På Windows rekommenderas PowerShell och Docker Desktop. Kontrollera även Python Launcher:

```powershell
py --version
```

När guiden visar `python -m ...` använder ni följande i PowerShell:

```powershell
py -m pip install -r requirements.txt
py -m pytest -q
```

GitHub Actions använder fortfarande `python` i `ci.yml`, eftersom workflowet körs på en Linux-runner. Ändra därför inte pipelinekommandot till `py`.

---

## 1. Skapa ett eget repository

1. Välj **New repository** på GitHub.
2. Döp repot till `jensenstore-api`.
3. Välj **Public**.
4. Lägg till en README.
5. Skapa och klona repot.

```bash
git clone https://github.com/DITT-ANVANDARNAMN/jensenstore-api.git
cd jensenstore-api
```

Alla följande kommandon körs från roten av ert eget repo. Kontrollera platsen med:

```bash
pwd
git status
```

Arbeta inte direkt i `jensen-devops-exercise`. Det är underlaget; CI/CD-pipelinen ska finnas i ert eget repo.

---

## 2. Skapa filerna

Skapa följande struktur i ert repo:

```text
jensenstore-api/
├── .github/
│   └── workflows/
│       └── ci.yml
├── .dockerignore
├── Dockerfile
├── README.md
├── app.py
├── requirements.txt
└── test_app.py
```

Använd filerna i `del-1` som underlag och kopiera innehållet manuellt.

Viktigt:

- `Dockerfile` saknar filändelse
- `.dockerignore` börjar med en punkt
- workflowet måste ligga i `.github/workflows/ci.yml`
- YAML använder mellanslag, inte tabbar
- ni ska inte ändra eller bygga ut `test_app.py`

Kontrollera att den färdiga starterkoden fungerar:

```bash
python -m pip install -r requirements.txt
python -m pytest -q
```

**Förväntat resultat:** `2 passed`. Testerna är en färdig kontroll som pipelinen senare ska använda.

---

## 3. Starta det första workflowet

```bash
git add .
git commit -m "Add JensenStore application and workflow"
git push
```

Öppna **Actions** på GitHub, välj körningen och öppna jobbet `verify-build-deliver`.

**Förväntat resultat:** checkout, Python-setup och installation av dependencies är gröna. TODO-delarna gör ännu ingenting.

Fundera:

- Vad i `ci.yml` gjorde att workflowet startade?
- Vilken runner kör jobbet?
- Bevisar denna gröna pipeline att en image har byggts eller levererats?

---

## 4. Koppla befintlig verifiering till CI

Ni ska inte skapa några tester. Er uppgift är att göra den befintliga kontrollen obligatorisk i pipelinen.

Ersätt TODO 1 i `ci.yml` med:

```yaml
      - name: Verify application
        run: python -m pytest -q
```

```bash
git add .github/workflows/ci.yml
git commit -m "Verify application in CI"
git push
```

Öppna steget `Verify application` i Actions-loggen.

**Förväntat resultat:** `2 passed`. Samma färdiga kontroll körs nu automatiskt vid varje push.

---

## 5. Skapa och felsök ett pipelinefel

Bryt installationen tillfälligt genom att ändra detta i `ci.yml`:

```yaml
pip install -r requirements.txt
```

till:

```yaml
pip install -r requirements-missing.txt
```

Commit och push:

```bash
git add .github/workflows/ci.yml
git commit -m "Introduce pipeline configuration error"
git push
```

Öppna den röda körningen och kontrollera:

1. Vilket steg misslyckades?
2. Vilken fil säger loggen att den inte hittar?
3. Kördes verifieringen efter felet?
4. Varför ska build och leverans inte fortsätta?

Återställ `requirements.txt`, commit och push igen.

**Förväntat resultat:** den nya körningen blir grön. Ni har felsökt pipelinekonfigurationen utan att ändra applikationen eller testerna.

---

## 6. Bygg imagen lokalt och i CI

Bygg först lokalt:

```bash
docker build -t jensenstore-api:local .
docker images jensenstore-api
```

**Förväntat resultat:** imagen `jensenstore-api:local` visas.

Ersätt TODO 2 i `ci.yml` med:

```yaml
      - name: Build Docker image
        run: docker build -t ghcr.io/${{ github.repository }}:${{ github.sha }} .
```

Commit och push. Kontrollera sedan Actions-loggen.

**Förväntat resultat:** `Build Docker image` körs efter verifieringen och avslutas utan fel. Taggen innehåller commitens SHA.

---

## 7. Leverera imagen till GHCR

Workflowets `permissions` ska innehålla:

```yaml
permissions:
  contents: read
  packages: write
```

`packages: write` ger jobbets inbyggda `GITHUB_TOKEN` rätt att publicera paket. Ni ska inte lägga in lösenord eller egna tokens i filen.

Ersätt TODO 3 med följande steg efter Docker-build:

```yaml
      - name: Log in to GitHub Container Registry
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Push Docker image
        run: docker push ghcr.io/${{ github.repository }}:${{ github.sha }}
```

```bash
git add .github/workflows/ci.yml
git commit -m "Deliver image to GitHub Container Registry"
git push
```

Kontrollera i Actions:

```text
Checkout
Setup Python
Install dependencies
Verify application
Build Docker image
Log in to GitHub Container Registry
Push Docker image
```

**Förväntat resultat:** alla steg är gröna och ett paket visas på GitHub under repots eller profilens **Packages**.

Öppna `Push Docker image` och hitta den fullständiga imagereferensen. Den ska likna:

```text
ghcr.io/ditt-anvandarnamn/jensenstore-api:COMMIT_SHA
```

---

## 8. Kör applikationen lokalt

```bash
docker run --name jensenstore-api -p 8000:8000 jensenstore-api:local
```

Testa i en annan terminal eller öppna adresserna i webbläsaren:

```bash
curl http://localhost:8000/
curl http://localhost:8000/health
```

I Windows PowerShell använder ni:

```powershell
curl.exe http://localhost:8000/
curl.exe http://localhost:8000/health
```

**Förväntat svar från `/`:**

```json
{"application":"JensenStore API","status":"running","version":"1.0.0"}
```

**Förväntat svar från `/health`:**

```json
{"status":"healthy"}
```

Stoppa med `Ctrl+C` och ta bort containern:

```bash
docker rm jensenstore-api
```

Detta är en lokal deployment. I del 2 ska en plattform ansvara för att starta och övervaka containern.

---

## 9. Följ en ny leverans

Gör en liten, säker förändring utan att röra applikationen eller testerna. Lägg exempelvis till följande i README-filen i ert eget repo:

```markdown
## Pipeline

Varje push verifierar applikationen och publicerar en Docker-image till GHCR.
```

```bash
git add README.md
git commit -m "Document CI/CD pipeline"
git push
```

Öppna den nya Actions-körningen och kontrollera att den publicerar en image med den nya commitens SHA. Jämför med SHA-taggen från föregående körning.

**Förväntat resultat:** den tidigare imagen finns kvar och den nya commiten får en egen image. Det visar att leveranserna är spårbara även när testerna och applikationskoden inte ändras.

---

## Avslutande reflektion

Diskutera gärna två och två:

- Vilka steg i workflowet tillhör CI?
- Vilket steg gör resultatet leveransbart?
- Varför används commit-SHA som image-tagg?
- Varför publiceras ingen image när ett tidigare steg misslyckas?
- Vad saknas fortfarande för att detta ska vara continuous deployment?

## Klart när

- ert eget repo innehåller applikation och workflow
- en push startar workflowet automatiskt
- ni har felsökt en röd pipelinekörning
- befintlig verifiering körs före build
- en Docker-image byggs och publiceras till GHCR
- ni kan koppla den publicerade imagen till en commit

## Felsökning

### Workflowet syns inte

Kontrollera att filen är pushad till `.github/workflows/ci.yml` i ert eget repo.

### YAML-fel

Kontrollera indenteringen och använd mellanslag i stället för tabbar.

### `pytest` eller Flask saknas

```bash
python -m pip install -r requirements.txt
python -m pytest -q
```

### Docker kan inte bygga

Kontrollera att Docker Desktop körs och att kommandot avslutas med punkten som anger build context:

```bash
docker build -t jensenstore-api:local .
```

### GHCR svarar med `permission_denied`

Kontrollera att workflowet har `packages: write`, att login-steget använder `GITHUB_TOKEN` och att push-steget körs efter login.

### Port 8000 används

```bash
docker run --name jensenstore-api-2 -p 8001:8000 jensenstore-api:local
```

## Extra om ni blir klara tidigt

- lägg till `workflow_dispatch` om det saknas och starta pipelinen manuellt
- lägg till en läsbar image-tagg som `latest` utöver commit-SHA
- undersök paketets visibility och koppling till repot på GitHub
- lägg till en branchregel som kräver en grön kontroll före merge

## Avsluta

Kontrollera och ta bort eventuell testcontainer:

```bash
docker ps -a --filter name=jensenstore-api
```

Om kommandot visar containern, ta bort den med `docker rm -f jensenstore-api`.

Behåll images. De kan användas som underlag i del 2.
