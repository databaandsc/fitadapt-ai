<script setup lang="ts">
import { ref, computed } from 'vue';
import { SignInButton, UserButton, useAuth } from '@clerk/vue';
import { useApi } from './composables/useApi';
const { isSignedIn } = useAuth();
const { fetchWithAuth } = useApi();

import {
  Dumbbell,


  Brain,
  Clock,
  Target,
  Award,
  Loader2,
  Zap,
  AlertCircle,
  CheckCircle2,
  ChevronRight,
  Activity,
  Lightbulb,
  ShieldAlert,
} from 'lucide-vue-next';

import type {
  Objetivo,
  Nivel,
  Equipamiento,
  WorkoutRequest,
  RutinaResponse,
} from './types/workout';

interface EquipamientoOpcion {
  id: Equipamiento;
  label: string;
  icon: string;
}

const OPCIONES_EQUIPAMIENTO: EquipamientoOpcion[] = [
  { id: 'mancuernas', label: 'Mancuernas', icon: '🏋️' },
  { id: 'maquinas', label: 'Máquinas', icon: '⚙️' },
  { id: 'poleas', label: 'Poleas', icon: '🔁' },
  { id: 'barras_discos', label: 'Barras y Discos', icon: '🔩' },
  { id: 'peso_corporal', label: 'Peso Corporal', icon: '🧍' },
];

const OBJETIVO_META: Record<string, { label: string; color: string; desc: string }> = {
  hipertrofia:   { label: 'Hipertrofia (Masa Muscular)',       color: 'text-violet-300', desc: 'Aumenta volumen muscular' },
  fuerza:        { label: 'Fuerza Pura',                       color: 'text-rose-300',   desc: 'Máxima carga por rep' },
  perdida_grasa: { label: 'Pérdida de Grasa / Definición',     color: 'text-sky-300',    desc: 'Quema y define' },
  resistencia:   { label: 'Resistencia Muscular',              color: 'text-emerald-300', desc: 'Aguanta más y más' },
};

// Estado Reactivo
const objetivo = ref<Objetivo>('hipertrofia');
const tiempoMinutos = ref<number>(45);
const equipamiento = ref<Equipamiento[]>(['mancuernas', 'maquinas']);
const nivel = ref<Nivel>('intermedio');

const generatedFor = ref<WorkoutRequest | null>(null);
const loading = ref<boolean>(false);
const error = ref<string | null>(null);
const rutina = ref<RutinaResponse | null>(null);

const sliderPercent = computed(() => ((tiempoMinutos.value - 20) / (75 - 20)) * 100);

const toggleEquipamiento = (id: Equipamiento): void => {
  if (equipamiento.value.includes(id)) {
    if (equipamiento.value.length > 1) {
      equipamiento.value = equipamiento.value.filter((item) => item !== id);
    }
  } else {
    equipamiento.value.push(id);
  }
};

const handleSubmit = async (): Promise<void> => {
  if (loading.value) return;
  if (!Number.isInteger(tiempoMinutos.value) || tiempoMinutos.value < 20 || tiempoMinutos.value > 75 || tiempoMinutos.value % 5 !== 0 || !equipamiento.value.length) {
    error.value = 'Revisa la duración y selecciona al menos un equipamiento.';
    return;
  }
  loading.value = true;
  error.value = null;
  rutina.value = null;
  generatedFor.value = null;

  const payload: WorkoutRequest = {
    objetivo: objetivo.value,
    tiempo_minutos: Number(tiempoMinutos.value),
    equipamiento: [...equipamiento.value],
    nivel: nivel.value,
  };

  const controller = new AbortController();
  const timeout = window.setTimeout(() => controller.abort(), 55000);
  try {
    const response = await fetchWithAuth('/api/generate-routine', {
      method: 'POST',
      signal: controller.signal,
      body: JSON.stringify(payload),
    });


    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(typeof errorData.detail === 'string' ? errorData.detail : 'Revisa los datos del formulario y vuelve a intentarlo.');
    }

    const data: RutinaResponse = await response.json();
    rutina.value = data;
    generatedFor.value = payload;
  } catch (err: unknown) {
    if (err instanceof Error || err instanceof DOMException) {
      error.value = err.name === 'AbortError' ? 'La petición ha tardado demasiado. Vuelve a intentarlo.' : err instanceof TypeError ? 'No se pudo conectar. Comprueba que el servidor local está en marcha.' : err.message;
    } else {
      error.value = 'Ocurrió un error inesperado.';
    }
  } finally {
    window.clearTimeout(timeout);
    loading.value = false;
  }
};
</script>

<template>
  <!-- ════════════════════════════════════════════════════════════
       SHELL: fondo oscuro con malla y luces ambientales
  ═════════════════════════════════════════════════════════════ -->
  <header class="sticky top-0 z-50 w-full border-b border-white/5 bg-slate-950/80 backdrop-blur-xl">
    <div class="max-w-screen-xl mx-auto px-4 sm:px-6 h-14 flex items-center justify-between">
      <div class="flex items-center gap-2">
        <div class="inline-flex items-center justify-center p-1.5 bg-violet-500/10 text-violet-400 rounded-lg border border-violet-500/20">
          <Dumbbell class="w-4 h-4" />
        </div>
        <span class="text-sm font-semibold tracking-tight text-white">FitAdaptAI</span>
      </div>
      <div class="flex items-center gap-2">
        <template v-if="!isSignedIn">
          <SignInButton mode="modal" class="px-3 py-1.5 rounded-md bg-violet-500 text-white text-sm font-medium hover:bg-violet-400 transition-colors">
            Iniciar sesión
          </SignInButton>
        </template>
        <template v-else>
          <UserButton />
        </template>
      </div>
    </div>
  </header>
  <div class="fitadapt-shell min-h-screen overflow-x-hidden">


    <!-- Luces de fondo decorativas -->
    <div class="fixed inset-0 -z-10 overflow-hidden" aria-hidden="true">
      <div class="absolute -top-40 -left-40 w-[600px] h-[600px] rounded-full bg-violet-600/10 blur-[120px]"></div>
      <div class="absolute top-1/2 -right-60 w-[500px] h-[500px] rounded-full bg-indigo-600/10 blur-[100px]"></div>
      <div class="absolute -bottom-20 left-1/3 w-[400px] h-[400px] rounded-full bg-purple-700/8 blur-[90px]"></div>
      <!-- Rejilla sutil -->
      <div class="absolute inset-0 bg-[linear-gradient(rgba(99,102,241,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(99,102,241,0.03)_1px,transparent_1px)] bg-[size:64px_64px]"></div>
    </div>

    <template v-if="!isSignedIn">
      <main class="relative min-h-[calc(100vh-3.5rem)] flex items-center justify-center px-4">
        <div class="max-w-md w-full text-center space-y-6">
          <div class="flex justify-center">
            <div class="inline-flex items-center justify-center p-3 bg-violet-500/10 text-violet-400 rounded-2xl border border-violet-500/20">
              <Dumbbell class="w-8 h-8" />
            </div>
          </div>
          <div class="space-y-2">
            <h1 class="text-3xl sm:text-4xl font-black tracking-tight text-white">
              Fit<span class="text-violet-400">Adapt</span> AI
            </h1>
            <p class="text-slate-400">Inicia sesión para generar tu rutina personalizada con IA</p>
          </div>
          <div class="flex justify-center">
            <SignInButton mode="modal" class="cta-btn max-w-xs">
              <span>Iniciar sesión para continuar</span>
              <ChevronRight class="w-4 h-4" />
            </SignInButton>
          </div>
        </div>
      </main>
    </template>

    <template v-else>


    <!-- ── TOP NAV BAR ── -->
    <nav class="sticky top-0 z-50 border-b border-white/5 bg-[#09090f]/80 backdrop-blur-xl">
      <div class="max-w-screen-xl mx-auto px-4 sm:px-6 h-14 flex items-center justify-between">
        <!-- Logo -->
        <div class="flex items-center gap-2.5">
          <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-violet-500 to-indigo-600 flex items-center justify-center shadow-lg shadow-violet-500/30">
            <Brain class="w-4.5 h-4.5 text-white w-[18px] h-[18px]" />
          </div>
          <span class="font-black text-white tracking-tight text-lg">
            Fit<span class="text-violet-400">Adapt</span><span class="text-slate-500 font-light ml-1 text-sm">AI</span>
          </span>
        </div>
        <!-- Stepper -->
        <div class="hidden sm:flex items-center gap-1 text-[11px] font-semibold text-slate-500">
          <span class="px-2.5 py-1 rounded-md bg-violet-500/15 text-violet-400 border border-violet-500/25">01 · Configura</span>
          <ChevronRight class="w-3 h-3 mx-0.5" />
          <span class="px-2.5 py-1 rounded-md">02 · Genera</span>
          <ChevronRight class="w-3 h-3 mx-0.5" />
          <span class="px-2.5 py-1 rounded-md">03 · Entrena</span>
        </div>
        <!-- Badge IA -->
        <div class="flex items-center gap-1.5 px-2.5 py-1 rounded-full border border-violet-500/25 bg-violet-500/10 text-violet-300 text-[11px] font-semibold">
          <span class="w-1.5 h-1.5 rounded-full bg-violet-400 animate-pulse"></span>
          IA activa
        </div>
      </div>
    </nav>

    <!-- ── HERO SECTION ── -->
    <header class="max-w-screen-xl mx-auto px-4 sm:px-6 pt-12 pb-8 text-center">
      <p class="inline-flex items-center gap-2 text-xs font-semibold uppercase tracking-widest text-violet-400/80 mb-4">
        <Activity class="w-3.5 h-3.5" />
        Entrenamiento personalizado con LLM
      </p>
      <h1 class="text-4xl sm:text-5xl lg:text-6xl font-black tracking-tight text-white leading-[1.1] mb-4">
        Tu sesión.<br>
        <span class="bg-gradient-to-r from-violet-400 via-fuchsia-400 to-indigo-400 bg-clip-text text-transparent">
          Diseñada por IA.
        </span>
      </h1>
      <p class="max-w-xl mx-auto text-slate-400 text-base sm:text-lg leading-relaxed">
        Indica tu objetivo, tiempo disponible y material. La IA generará tu rutina completa en segundos.
      </p>
    </header>

    <!-- ── MAIN LAYOUT: 2 columnas en desktop ── -->
    <main class="max-w-screen-xl mx-auto px-4 sm:px-6 pb-16">
      <div class="flex flex-col lg:flex-row gap-6 lg:gap-8 lg:items-start">

        <!-- ╔══════════════════════════════╗
             ║  SIDEBAR — CONFIGURADOR      ║
             ╚══════════════════════════════╝ -->
        <aside class="w-full lg:w-[340px] xl:w-[380px] flex-shrink-0">
          <div class="glass-card p-6 space-y-6">
            <div class="flex items-center gap-2 mb-1">
              <div class="w-6 h-6 rounded-md bg-violet-500/20 flex items-center justify-center">
                <Zap class="w-3.5 h-3.5 text-violet-400" />
              </div>
              <span class="text-xs font-bold uppercase tracking-widest text-slate-400">Configuración</span>
            </div>

            <form @submit.prevent="handleSubmit" :aria-busy="loading">
              <fieldset :disabled="loading" class="space-y-5">
                <legend class="sr-only">Configura tu entrenamiento</legend>

                <!-- ── 1. Objetivo ── -->
                <div class="form-group">
                  <label class="form-label">
                    <Target class="w-3.5 h-3.5 text-violet-400" />
                    1. Objetivo Principal
                  </label>
                  <select
                    v-model="objetivo"
                    aria-label="Objetivo Principal"
                    class="form-select"
                  >
                    <option value="hipertrofia">Hipertrofia (Masa Muscular)</option>
                    <option value="fuerza">Fuerza Pura</option>
                    <option value="perdida_grasa">Pérdida de Grasa / Definición</option>
                    <option value="resistencia">Resistencia Muscular</option>
                  </select>
                  <!-- Chip descriptivo dinámico -->
                  <p class="mt-1.5 text-[11px]" :class="OBJETIVO_META[objetivo]?.color">
                    → {{ OBJETIVO_META[objetivo]?.desc }}
                  </p>
                </div>

                <!-- ── 2. Duración ── -->
                <div class="form-group">
                  <div class="flex items-center justify-between mb-1">
                    <label class="form-label mb-0">
                      <Clock class="w-3.5 h-3.5 text-violet-400" />
                      2. Duración de la Sesión
                    </label>
                    <span class="font-black text-white text-lg leading-none tabular-nums">
                      {{ tiempoMinutos }}<span class="text-slate-400 text-xs font-normal ml-0.5">min</span>
                    </span>
                  </div>
                  <!-- Slider container: barra visual + input invisible superpuesto -->
                  <div class="relative w-full" style="height: 28px;">
                    <!-- Track de fondo -->
                    <div class="absolute left-0 right-0 top-1/2 -translate-y-1/2 h-1.5 bg-slate-800 rounded-full pointer-events-none">
                      <!-- Fill de progreso -->
                      <div
                        class="absolute left-0 top-0 h-full rounded-full bg-gradient-to-r from-violet-500 to-indigo-500 transition-all duration-150"
                        :style="{ width: sliderPercent + '%' }"
                      ></div>
                    </div>
                    <!-- Input range invisible encima, ocupa todo el área -->
                    <input
                      v-model.number="tiempoMinutos"
                      type="range"
                      aria-label="Tiempo de Sesión"
                      min="20"
                      max="75"
                      step="5"
                      class="slider-hidden"
                    />
                  </div>
                  <div class="flex justify-between text-[11px] text-slate-500 font-medium mt-1">
                    <span>20m</span><span>45m</span><span>75m</span>
                  </div>
                </div>

                <!-- ── 3. Nivel ── -->
                <div class="form-group">
                  <label class="form-label">
                    <Award class="w-3.5 h-3.5 text-violet-400" />
                    3. Nivel de Experiencia
                  </label>
                  <select
                    v-model="nivel"
                    aria-label="Nivel de Experiencia"
                    class="form-select"
                  >
                    <option value="principiante">Principiante (&lt; 6 meses)</option>
                    <option value="intermedio">Intermedio (6 meses a 2 años)</option>
                    <option value="avanzado">Avanzado (&gt; 2 años)</option>
                  </select>
                </div>

                <!-- ── 4. Equipamiento ── -->
                <div class="form-group">
                  <label class="form-label">
                    <Dumbbell class="w-3.5 h-3.5 text-violet-400" />
                    4. Equipamiento Disponible
                  </label>
                  <div class="grid grid-cols-2 gap-2 sm:grid-cols-3 lg:grid-cols-2 xl:grid-cols-3">
                    <button
                      v-for="opcion in OPCIONES_EQUIPAMIENTO"
                      :key="opcion.id"
                      :aria-pressed="equipamiento.includes(opcion.id)"
                      type="button"
                      @click="toggleEquipamiento(opcion.id)"
                      :class="[
                        'equip-btn',
                        equipamiento.includes(opcion.id) ? 'equip-btn--active' : 'equip-btn--idle'
                      ]"
                    >
                      <span class="text-base leading-none">{{ opcion.icon }}</span>
                      <span class="text-xs font-semibold leading-tight">{{ opcion.label }}</span>
                    </button>
                  </div>
                </div>

                <!-- ── CTA ── -->
                <button
                  type="submit"
                  :disabled="loading"
                  class="cta-btn w-full"
                >
                  <template v-if="loading">
                    <Loader2 class="w-4 h-4 animate-spin flex-shrink-0" />
                    <span>Preparando tu entrenamiento...</span>
                  </template>
                  <template v-else>
                    <Zap class="w-4 h-4 flex-shrink-0" />
                    <span>Generar mi rutina</span>
                  </template>
                </button>

              </fieldset>
            </form>
          </div>
        </aside>

        <!-- ╔══════════════════════════════╗
             ║  PANEL DERECHO — RESULTADO   ║
             ╚══════════════════════════════╝ -->
        <div class="flex-1 min-w-0 space-y-4">

          <!-- ── Error ── -->
          <section
            v-if="error"
            role="alert"
            class="glass-card p-4 flex items-start gap-3 border-rose-700/40 bg-rose-950/20"
          >
            <AlertCircle class="w-5 h-5 text-rose-400 mt-0.5 flex-shrink-0" />
            <div>
              <h2 class="font-bold text-rose-200 text-sm mb-0.5">Error en la petición</h2>
              <p class="text-sm text-rose-300/80">{{ error }}</p>
            </div>
          </section>

          <!-- ── Loading placeholder ── -->
          <div v-if="loading" class="glass-card p-8 flex flex-col items-center justify-center gap-4 min-h-[300px]">
            <div class="w-14 h-14 rounded-2xl bg-violet-500/15 border border-violet-500/30 flex items-center justify-center">
              <Loader2 class="w-7 h-7 text-violet-400 animate-spin" />
            </div>
            <p role="status" class="text-slate-300 font-semibold text-center">Preparando tu sesión…</p>
            <p class="text-slate-500 text-sm text-center">La IA está generando tu rutina personalizada</p>
          </div>

          <!-- ── Empty state (sin rutina ni loading) ── -->
          <div v-if="!rutina && !loading && !error" class="glass-card p-8 flex flex-col items-center justify-center gap-4 min-h-[300px] border-dashed">
            <div class="w-16 h-16 rounded-2xl bg-slate-800/60 flex items-center justify-center">
              <Dumbbell class="w-8 h-8 text-slate-600" />
            </div>
            <p class="text-slate-500 font-semibold text-center">Tu sesión aparecerá aquí</p>
            <p class="text-slate-600 text-sm text-center max-w-xs">Configura los parámetros en el panel izquierdo y pulsa <strong class="text-slate-400">Generar mi rutina</strong></p>
          </div>

          <!-- ── Resultado de la Rutina ── -->
          <article v-if="rutina" class="space-y-4">

            <!-- Cabecera del resultado -->
            <div class="glass-card p-5">
              <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div class="flex items-start gap-3">
                  <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-violet-500 to-indigo-600 flex items-center justify-center shadow-lg shadow-violet-500/25 flex-shrink-0">
                    <CheckCircle2 class="w-5 h-5 text-white" />
                  </div>
                  <div>
                    <h2 class="text-lg font-black text-white leading-tight">Tu Sesión Personalizada</h2>
                    <p class="text-sm text-slate-400 mt-0.5">
                      Objetivo: <span class="text-violet-300 font-semibold">{{ generatedFor?.objetivo.replace("_", " ") }}</span>
                      &nbsp;·&nbsp; Nivel: <span class="text-violet-300 font-semibold">{{ generatedFor?.nivel }}</span>
                    </p>
                  </div>
                </div>
                <div class="flex items-center gap-2 flex-wrap">
                  <span class="px-3 py-1.5 rounded-lg bg-violet-500/15 border border-violet-500/30 text-violet-300 text-xs font-bold">
                    ⏱ {{ rutina.tiempo_total_estimado }} min
                  </span>
                  <span class="px-3 py-1.5 rounded-lg bg-slate-800 border border-slate-700 text-slate-300 text-xs font-medium">
                    {{ rutina.modo === 'demo' ? 'Demostración local · Rutina creada con reglas predefinidas, sin IA ni conexión externa.' : 'Rutina generada con IA · Revisa la propuesta antes de entrenar.' }}
                  </span>
                </div>
              </div>
            </div>

            <!-- Calentamiento -->
            <div class="glass-card p-5">
              <div class="flex items-center gap-2 mb-3">
                <span class="phase-badge">FASE 1</span>
                <h3 class="text-sm font-bold text-white">Activación y Calentamiento</h3>
              </div>
              <p class="text-sm text-slate-300 leading-relaxed">{{ rutina.calentamiento }}</p>
            </div>

            <!-- Ejercicios -->
            <div class="glass-card p-5">
              <div class="flex items-center gap-2 mb-4">
                <span class="phase-badge">FASE 2</span>
                <h3 class="text-sm font-bold text-white">Ejercicios Principales</h3>
              </div>
              <div class="space-y-3">
                <div
                  v-for="(ejercicio, index) in rutina.ejercicios"
                  :key="index"
                  class="exercise-card"
                >
                  <!-- Número y nombre -->
                  <div class="flex items-start gap-3 mb-3">
                    <span class="exercise-num">{{ index + 1 }}</span>
                    <div>
                      <h4 class="font-bold text-white text-sm leading-tight">{{ ejercicio.nombre }}</h4>
                      <p class="text-[11px] text-slate-500 mt-0.5 flex items-center gap-1">
                        <Lightbulb class="w-3 h-3 flex-shrink-0" />
                        {{ ejercicio.consejo_tecnico }}
                      </p>
                    </div>
                  </div>
                  <!-- Métricas -->
                  <div class="grid grid-cols-4 divide-x divide-slate-800/80 bg-[#0d0d18] rounded-xl border border-slate-800/80 overflow-hidden">
                    <div class="metric-cell">
                      <span class="metric-label">Series</span>
                      <span class="metric-value">{{ ejercicio.series }}</span>
                    </div>
                    <div class="metric-cell">
                      <span class="metric-label">Reps</span>
                      <span class="metric-value">{{ ejercicio.repeticiones }}</span>
                    </div>
                    <div class="metric-cell">
                      <span class="metric-label">Descanso</span>
                      <span class="metric-value">{{ ejercicio.descanso_segundos }}s</span>
                    </div>
                    <div class="metric-cell">
                      <span class="metric-label">Esfuerzo</span>
                      <span class="metric-value text-violet-400">{{ ejercicio.rpe_sugerido }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Alternativa rápida -->
            <div class="glass-card p-5 border-slate-700/40 bg-slate-900/30">
              <div class="flex items-center gap-2 mb-2">
                <ShieldAlert class="w-4 h-4 text-slate-400 flex-shrink-0" />
                <h3 class="text-xs font-bold uppercase tracking-widest text-slate-400">¿Máquina ocupada? (Alternativa rápida)</h3>
              </div>
              <p class="text-sm text-slate-300 leading-relaxed">{{ rutina.alternativa_rapida }}</p>
            </div>

          </article>
        </div>
      </div>
    </main>

    <!-- ── FOOTER ── -->
    <footer class="border-t border-white/5 py-6 text-center text-[11px] text-slate-600">
      FitAdaptAI · Una sesión a tu medida.<br>
      Propuesta orientativa. Ajusta la carga a tu capacidad y detente si aparece dolor.<br>
      RPE indica el esfuerzo percibido en una escala del 1 al 10.
    </footer>
    </template>

  </div>
</template>


<style scoped>
/* ─── SHELL ─── */
.fitadapt-shell {
  background-color: #09090f;
  color: #e2e8f0;
  font-family: ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif;
  -webkit-font-smoothing: antialiased;
}

/* ─── GLASS CARD ─── */
.glass-card {
  @apply rounded-2xl border border-white/[0.07] bg-white/[0.035] backdrop-blur-md shadow-xl;
}

/* ─── FORM ELEMENTS ─── */
.form-group {
  @apply space-y-1.5;
}
.form-label {
  @apply flex items-center gap-1.5 text-xs font-bold uppercase tracking-widest text-slate-400 mb-2;
}
.form-select {
  @apply w-full rounded-xl px-3.5 py-2.5 text-sm text-slate-100 bg-slate-900/80 border border-slate-700/80
         focus:outline-none focus:ring-2 focus:ring-violet-500/70 focus:border-violet-500/50
         transition appearance-none cursor-pointer;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%236b7280' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 12px center;
  padding-right: 36px;
}

/* ─── EQUIPMENT BUTTONS ─── */
.equip-btn {
  @apply flex flex-col items-center justify-center gap-1 py-2.5 px-2 rounded-xl border text-center
         transition duration-150 select-none cursor-pointer;
}
.equip-btn--idle {
  @apply bg-slate-900/60 border-slate-700/60 text-slate-400 hover:border-slate-600 hover:bg-slate-800/60;
}
.equip-btn--active {
  @apply bg-violet-600/20 border-violet-500/60 text-violet-200 shadow-sm shadow-violet-500/10;
}

/* ─── CTA BUTTON ─── */
.cta-btn {
  @apply flex items-center justify-center gap-2.5 w-full py-3 px-5 rounded-xl font-bold text-sm
         bg-gradient-to-r from-violet-600 to-indigo-600
         hover:from-violet-500 hover:to-indigo-500
         text-white shadow-lg shadow-violet-600/30
         disabled:opacity-50 disabled:cursor-not-allowed
         transition active:scale-[0.98];
}

/* ─── PHASE BADGE ─── */
.phase-badge {
  @apply inline-flex items-center px-2 py-0.5 rounded text-[10px] font-black tracking-widest
         bg-violet-500/20 text-violet-400 border border-violet-500/30;
}

/* ─── EXERCISE CARD ─── */
.exercise-card {
  @apply p-4 rounded-xl bg-slate-950/60 border border-slate-800/70 hover:border-slate-700/60 transition;
}
.exercise-num {
  @apply flex-shrink-0 w-6 h-6 rounded-lg bg-violet-500/20 border border-violet-500/40
         text-violet-300 text-xs font-black flex items-center justify-center;
}

/* ─── METRIC CELLS ─── */
.metric-cell {
  @apply flex flex-col items-center justify-center py-2.5 gap-0.5;
}
.metric-label {
  @apply text-[9px] uppercase font-bold tracking-widest text-slate-500;
}
.metric-value {
  @apply text-sm font-black text-white;
}

/* ─── SLIDER OCULTO ─── */
/* El input cubre todo el contenedor padre (height: 28px) y es transparente.
   La barra visual de debajo reacciona al valor reactivo de Vue. */
.slider-hidden {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  opacity: 0;
  cursor: pointer;
  appearance: none;
  -webkit-appearance: none;
  margin: 0;
  padding: 0;
  z-index: 10;
}
</style>
