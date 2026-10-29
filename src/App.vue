<script setup lang="ts">
import { ref } from 'vue';
import {
  ClerkLoaded,
  ClerkLoading,
  Show,
  SignIn,
  UserButton,
} from '@clerk/vue';
import {
  Dumbbell,
  Clock,
  Target,
  Award,
  Loader2,
  Sparkles,
  AlertCircle,
  CheckCircle2,
} from 'lucide-vue-next';
import type {
  Objetivo,
  Nivel,
  Equipamiento,
  WorkoutRequest,
  RutinaResponse,
} from './types/workout';
import { useApi } from './composables/useApi';

interface EquipamientoOpcion {
  id: Equipamiento;
  label: string;
}

const OPCIONES_EQUIPAMIENTO: EquipamientoOpcion[] = [
  { id: 'mancuernas', label: 'Mancuernas' },
  { id: 'maquinas', label: 'Máquinas' },
  { id: 'poleas', label: 'Poleas' },
  { id: 'barras_discos', label: 'Barras y Discos' },
  { id: 'peso_corporal', label: 'Peso Corporal' },
];

const objetivo = ref<Objetivo>('hipertrofia');
const tiempoMinutos = ref<number>(45);
const equipamiento = ref<Equipamiento[]>(['mancuernas', 'maquinas']);
const nivel = ref<Nivel>('intermedio');

const generatedFor = ref<WorkoutRequest | null>(null);
const loading = ref<boolean>(false);
const error = ref<string | null>(null);
const rutina = ref<RutinaResponse | null>(null);

const toggleEquipamiento = (id: Equipamiento): void => {
  if (equipamiento.value.includes(id)) {
    if (equipamiento.value.length > 1) {
      equipamiento.value = equipamiento.value.filter((item) => item !== id);
    }
  } else {
    equipamiento.value.push(id);
  }
};

const { fetchWithAuth } = useApi();

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
  <ClerkLoading>
    <div class="min-h-screen bg-slate-950 flex items-center justify-center">
      <Loader2 class="w-8 h-8 text-emerald-400 animate-spin" />
    </div>
  </ClerkLoading>

  <ClerkLoaded>
    <Show when="signed-out">
      <div class="min-h-screen bg-slate-950 flex items-center justify-center px-4">
        <SignIn />
      </div>
    </Show>

    <Show when="signed-in">
      <div class="fitadapt-shell min-h-screen overflow-x-hidden">
        <nav class="sticky top-0 z-50 border-b border-white/5 bg-[#09090f]/80 backdrop-blur-xl">
          <div class="max-w-screen-xl mx-auto px-4 sm:px-6 h-14 flex items-center justify-between">
            <div class="flex items-center gap-3">
              <div class="inline-flex items-center justify-center p-2 bg-emerald-500/10 text-emerald-400 rounded-xl border border-emerald-500/20">
                <Dumbbell class="w-5 h-5" />
              </div>
              <span class="text-sm sm:text-base font-bold tracking-tight text-white">
                Fit<span class="text-emerald-400">Adapt</span> AI
              </span>
            </div>
            <div class="flex items-center gap-4">
              <UserButton afterSignOutUrl="/" />
            </div>
          </div>
        </nav>
        <main class="min-h-screen bg-slate-950 text-slate-100 py-10 px-4 sm:px-6 lg:px-8">
          <div class="max-w-4xl mx-auto space-y-8">
            <header class="text-center space-y-2">
              <div class="inline-flex items-center justify-center p-3 bg-emerald-500/10 text-emerald-400 rounded-2xl mb-2 border border-emerald-500/20">
                <Dumbbell class="w-8 h-8" />
              </div>
              <h1 class="text-3xl sm:text-4xl font-extrabold tracking-tight text-white">
                Fit<span class="text-emerald-400">Adapt</span> AI
              </h1>
              <p class="text-slate-400 max-w-2xl mx-auto">
                Genera una rutina personalizada con IA según tu objetivo, tiempo disponible y equipamiento.
              </p>
            </header>

            <section class="rounded-2xl border border-slate-800 bg-slate-900/60 shadow-xl shadow-emerald-500/5 backdrop-blur">
              <div class="p-6 sm:p-8 space-y-6">
                <div class="flex items-center gap-2">
                  <Sparkles class="w-5 h-5 text-emerald-400" />
                  <h2 class="text-lg font-semibold">Configura tu sesión</h2>
                </div>

                <div class="grid gap-6 sm:grid-cols-2">
                  <div class="space-y-2">
                    <label class="text-sm font-medium text-slate-200">Objetivo</label>
                    <select v-model="objetivo" class="w-full rounded-xl bg-slate-950/80 border border-slate-800 px-3 py-2 text-slate-100 focus:outline-none focus:ring-2 focus:ring-emerald-500/60">
                      <option value="hipertrofia">Hipertrofia (ganar masa muscular)</option>
                      <option value="fuerza">Fuerza</option>
                      <option value="perdida_grasa">Pérdida de grasa</option>
                      <option value="resistencia">Resistencia</option>
                    </select>
                  </div>

                  <div class="space-y-2">
                    <label class="text-sm font-medium text-slate-200">Nivel</label>
                    <select v-model="nivel" class="w-full rounded-xl bg-slate-950/80 border border-slate-800 px-3 py-2 text-slate-100 focus:outline-none focus:ring-2 focus:ring-emerald-500/60">
                      <option value="principiante">Principiante</option>
                      <option value="intermedio">Intermedio</option>
                      <option value="avanzado">Avanzado</option>
                    </select>
                  </div>
                </div>

                <div class="space-y-2">
                  <label class="text-sm font-medium text-slate-200">Tiempo disponible (minutos)</label>
                  <input v-model.number="tiempoMinutos" type="number" min="20" max="75" step="5" class="w-full rounded-xl bg-slate-950/80 border border-slate-800 px-3 py-2 text-slate-100 focus:outline-none focus:ring-2 focus:ring-emerald-500/60" />
                  <p class="text-xs text-slate-400">Entre 20 y 75 minutos, en incrementos de 5.</p>
                </div>

                <div class="space-y-3">
                  <label class="text-sm font-medium text-slate-200">Equipamiento disponible</label>
                  <div class="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
                    <button
                      v-for="opcion in OPCIONES_EQUIPAMIENTO"
                      :key="opcion.id"
                      type="button"
                      @click="toggleEquipamiento(opcion.id)"
                      :class="[
                        'flex items-center gap-2 rounded-xl border px-3 py-2 text-sm transition',
                        equipamiento.includes(opcion.id)
                          ? 'border-emerald-500/70 bg-emerald-500/10 text-emerald-200'
                          : 'border-slate-800 bg-slate-950/60 text-slate-300 hover:border-slate-700'
                      ]"
                    >
                      <span>{{ opcion.label }}</span>
                    </button>
                  </div>
                </div>

                <button
                  type="button"
                  @click="handleSubmit"
                  :disabled="loading"
                  class="w-full sm:w-auto inline-flex items-center justify-center gap-2 rounded-xl bg-emerald-500 px-6 py-2.5 text-sm font-semibold text-slate-950 transition hover:bg-emerald-400 disabled:cursor-not-allowed disabled:opacity-60"
                >
                  <Loader2 v-if="loading" class="w-4 h-4 animate-spin" />
                  <Sparkles v-else class="w-4 h-4" />
                  {{ loading ? 'Generando rutina...' : 'Generar rutina' }}
                </button>

                <div v-if="error" class="flex items-start gap-2 rounded-xl border border-rose-500/40 bg-rose-500/10 p-3 text-sm text-rose-200">
                  <AlertCircle class="w-4 h-4 mt-0.5" />
                  <p>{{ error }}</p>
                </div>
              </div>
            </section>

            <section v-if="rutina" class="rounded-2xl border border-slate-800 bg-slate-900/60 shadow-xl backdrop-blur">
              <div class="p-6 sm:p-8 space-y-6">
                <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
                  <div class="flex items-center gap-2">
                    <CheckCircle2 class="w-5 h-5 text-emerald-400" />
                    <h2 class="text-lg font-semibold">Tu rutina personalizada</h2>
                  </div>
                  <div class="flex flex-wrap gap-2 text-xs text-slate-300">
                    <span class="rounded-full border border-slate-700 px-3 py-1">Modo: {{ rutina.modo }}</span>
                    <span class="rounded-full border border-slate-700 px-3 py-1">Tiempo estimado: {{ rutina.tiempo_total_estimado }} min</span>
                    <span v-if="generatedFor" class="rounded-full border border-slate-700 px-3 py-1">Objetivo: {{ generatedFor.objetivo }}</span>
                  </div>
                </div>

                <div class="space-y-2">
                  <div class="flex items-center gap-2 text-slate-200">
                    <Clock class="w-4 h-4 text-emerald-400" />
                    <h3 class="font-medium">Calentamiento</h3>
                  </div>
                  <p class="rounded-xl border border-slate-800 bg-slate-950/60 p-4 text-sm text-slate-300 whitespace-pre-line">{{ rutina.calentamiento }}</p>
                </div>

                <div class="space-y-4">
                  <div class="flex items-center gap-2 text-slate-200">
                    <Target class="w-4 h-4 text-emerald-400" />
                    <h3 class="font-medium">Ejercicios</h3>
                  </div>
                  <div class="grid gap-3">
                    <article v-for="(ejercicio, index) in rutina.ejercicios" :key="index" class="rounded-xl border border-slate-800 bg-slate-950/60 p-4 space-y-2">
                      <div class="flex items-start justify-between gap-3">
                        <div>
                          <p class="text-sm font-semibold text-white">{{ index + 1 }}. {{ ejercicio.nombre }}</p>
                          <p class="text-xs text-slate-400">{{ ejercicio.consejo_tecnico }}</p>
                        </div>
                        <div class="flex items-center gap-1 text-xs text-emerald-300">
                          <Award class="w-3.5 h-3.5" />
                          <span>RPE {{ ejercicio.rpe_sugerido }}</span>
                        </div>
                      </div>
                      <div class="grid grid-cols-3 gap-2 text-center text-xs">
                        <div class="rounded-lg border border-slate-800 py-2">
                          <p class="text-slate-400">Series</p>
                          <p class="text-slate-100 font-medium">{{ ejercicio.series }}</p>
                        </div>
                        <div class="rounded-lg border border-slate-800 py-2">
                          <p class="text-slate-400">Repeticiones</p>
                          <p class="text-slate-100 font-medium">{{ ejercicio.repeticiones }}</p>
                        </div>
                        <div class="rounded-lg border border-slate-800 py-2">
                          <p class="text-slate-400">Descanso</p>
                          <p class="text-slate-100 font-medium">{{ ejercicio.descanso_segundos }}s</p>
                        </div>
                      </div>
                    </article>
                  </div>
                </div>

                <div class="space-y-2">
                  <h3 class="font-medium text-slate-200">Alternativa rápida</h3>
                  <p class="rounded-xl border border-slate-800 bg-slate-950/60 p-4 text-sm text-slate-300 whitespace-pre-line">{{ rutina.alternativa_rapida }}</p>
                </div>
              </div>
            </section>

            <footer class="text-center text-xs text-slate-400 pb-4">FitAdaptAI · Una sesión a tu medida.<br>Propuesta orientativa. Ajusta la carga a tu capacidad y detente si aparece dolor.<br>RPE indica el esfuerzo percibido en una escala del 1 al 10.</footer>
          </div>
        </main>
      </div>
    </Show>
  </ClerkLoaded>
</template>
