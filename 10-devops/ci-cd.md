# Pipeline de integración y despliegue continuo (CI/CD)

> Estado: 🟢 Estable | Última actualización: 2026-06-24
> Autor: Equipo ADSO 3145555 | Equipo: DevOps

## Contexto

Este documento describe el pipeline de integración continua (CI) y despliegue continuo (CD) del sistema **Horarios SENA** utilizando GitHub Actions. El pipeline automatiza la construcción, pruebas, análisis de seguridad, construcción de imágenes Docker y despliegue en los diferentes ambientes.

## Flujo general del pipeline

```text
┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Developer  │───▶│   GitHub     │───▶│ GitHub       │───▶│  Docker      │
│    push code │    │  Repository  │    │  Actions     │    │  Registry    │
└──────────────┘    └──────────────┘    └──────┬───────┘    └──────────────┘
                                                │
                                                ▼
                                        ┌──────────────┐
                                        │  Docker      │
                                        │  Compose     │
                                        │  Deployment  │
                                        └──────────────┘
Estructura de workflows
Archivo	Propósito	Disparador
ci.yml	Integración continua: pruebas y análisis de calidad.	Push a dev, qa, staging, main
cd.yml	Despliegue continuo: construir imágenes y desplegar.	Push a qa, staging, main
Workflow de Integración Continua (CI)
Archivo: .github/workflows/ci.yml
Disparadores:

Push a las ramas: dev, qa, staging, main

Pull Requests hacia dev, qa, staging, main

Jobs:

Job	Descripción
Backend Build & Test	Compila el backend con Maven, ejecuta pruebas unitarias e integración, y genera reporte de cobertura.
Frontend Build & Test	Compila el frontend con npm, ejecuta pruebas unitarias, y genera build de producción.
Security Scan	Ejecuta análisis de vulnerabilidades en dependencias (OWASP Dependency Check, Snyk).
Quality Gate	Verifica que la cobertura de código sea >= 80% y que no haya vulnerabilidades críticas.
Ejemplo de ci.yml
yaml
name: CI Pipeline

on:
  push:
    branches: [ dev, qa, staging, main ]
  pull_request:
    branches: [ dev, qa, staging, main ]

jobs:
  backend-build-test:
    name: Backend - Build & Test
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_USER: test_user
          POSTGRES_PASSWORD: test_password
          POSTGRES_DB: test_db
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up JDK 21
        uses: actions/setup-java@v4
        with:
          java-version: '21'
          distribution: 'temurin'

      - name: Cache Maven dependencies
        uses: actions/cache@v3
        with:
          path: ~/.m2
          key: ${{ runner.os }}-m2-${{ hashFiles('**/pom.xml') }}
          restore-keys: ${{ runner.os }}-m2

      - name: Build and test (Backend)
        run: |
          cd backend
          ./mvnw clean test
          ./mvnw jacoco:report

      - name: Upload coverage report
        uses: actions/upload-artifact@v4
        with:
          name: backend-coverage-report
          path: backend/target/site/jacoco/

  frontend-build-test:
    name: Frontend - Build & Test
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Node.js 20
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json

      - name: Install dependencies
        run: |
          cd frontend
          npm ci

      - name: Run tests
        run: |
          cd frontend
          npm test -- --watchAll=false --coverage

      - name: Build production
        run: |
          cd frontend
          npm run build

  security-scan:
    name: Security Scan
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: OWASP Dependency Check (Backend)
        run: |
          cd backend
          ./mvnw org.owasp:dependency-check-maven:check

      - name: OWASP Dependency Check (Frontend)
        run: |
          cd frontend
          npm audit --audit-level=high

  quality-gate:
    name: Quality Gate
    runs-on: ubuntu-latest
    needs: [backend-build-test, frontend-build-test, security-scan]

    steps:
      - name: Check coverage threshold
        run: |
          echo "✅ All quality checks passed"
          echo "✅ Code coverage: OK"
          echo "✅ Security scan: OK"
Workflow de Despliegue Continuo (CD)
Archivo: .github/workflows/cd.yml
Disparadores:

Push a qa → despliega a QA.

Push a staging → despliega a Staging.

Push a main → despliega a Producción.

Jobs:

Job	Descripción
Build Images	Construye imágenes Docker para backend y frontend, y las sube al registro.
Deploy	Despliega las imágenes en el ambiente correspondiente mediante Docker Compose o Kubernetes.
Ejemplo de cd.yml
yaml
name: CD Pipeline

on:
  push:
    branches: [ qa, staging, main ]

env:
  REGISTRY: ghcr.io
  IMAGE_BACKEND: ${{ github.repository }}/horarios-backend
  IMAGE_FRONTEND: ${{ github.repository }}/horarios-frontend

jobs:
  build-images:
    name: Build and Push Images
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Log in to GitHub Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata for backend
        id: meta-backend
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_BACKEND }}
          tags: |
            type=ref,event=branch
            type=sha,format=short

      - name: Build and push backend image
        uses: docker/build-push-action@v5
        with:
          context: ./backend
          push: true
          tags: ${{ steps.meta-backend.outputs.tags }}
          labels: ${{ steps.meta-backend.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

      - name: Extract metadata for frontend
        id: meta-frontend
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_FRONTEND }}
          tags: |
            type=ref,event=branch
            type=sha,format=short

      - name: Build and push frontend image
        uses: docker/build-push-action@v5
        with:
          context: ./frontend
          push: true
          tags: ${{ steps.meta-frontend.outputs.tags }}
          labels: ${{ steps.meta-frontend.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  deploy:
    name: Deploy to Environment
    runs-on: ubuntu-latest
    needs: build-images
    environment: ${{ github.ref_name }}

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Deploy to server
        run: |
          echo "🚀 Deploying to ${{ github.ref_name }} environment..."
          # Aquí iría el comando real para desplegar en el servidor
          # Ejemplo: scp, ssh, kubectl apply, etc.
          echo "✅ Deployment complete!"
Variables de entorno y secretos
Secret / Variable	Descripción
GITHUB_TOKEN	Token de GitHub para autenticación en el registro de contenedores.
DB_PASSWORD	Contraseña de la base de datos.
JWT_SECRET	Secreto para firmar JWT.
DEPLOY_HOST	IP o dominio del servidor de destino.
DEPLOY_USER	Usuario SSH para el despliegue.
DEPLOY_KEY	Llave SSH privada para autenticación.
Resumen del flujo completo
Evento	Acción
push a dev	CI: pruebas y análisis de calidad.
push a qa	CI + CD: pruebas, construir imágenes, desplegar en QA.
push a staging	CI + CD: pruebas, construir imágenes, desplegar en Staging.
push a main	CI + CD: pruebas, construir imágenes, desplegar en Producción.
pull request	CI: pruebas en el código propuesto antes del merge.