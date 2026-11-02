# =========================================================
# Etapa 1: Compilación del frontend (Vue 3 + TS + Tailwind)
# =========================================================
FROM node:22-alpine AS frontend-builder

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY index.html postcss.config.js tailwind.config.js tsconfig.json tsconfig.node.json vite.config.ts ./
COPY src ./src

# Clave PUBLICABLE de Clerk 
ARG VITE_CLERK_PUBLISHABLE_KEY
ENV VITE_CLERK_PUBLISHABLE_KEY=$VITE_CLERK_PUBLISHABLE_KEY

RUN npm run build

# ========================================================
# Etapa 2: Imagen final de ejecución (FastAPI + estáticos)
# ========================================================
FROM python:3.14-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Instalar dependencias de Python
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código del backend y el frontend ya compilado
COPY api ./api
COPY --from=frontend-builder /app/dist ./dist

# Ejecutar con usuario sin privilegios por seguridad
RUN useradd --create-home appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# Escuchar en 0.0.0.0 para permitir conexiones desde fuera del contenedor
CMD ["uvicorn", "api.index:app", "--host", "0.0.0.0", "--port", "8000"]