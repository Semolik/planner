<template>
    <TimeRangeSlider
        v-model="selectedRange"
        min-time="10:00:00"
        max-time="18:00:00"
        :step="15"
    />
    <p>Выбранный диапазон: {{ selectedRange.map(minutesToTime) }}</p>
</template>

<script setup lang="ts">
import { ref } from "vue";

const selectedRange = ref([
    timeToMinutes("11:00:00"),
    timeToMinutes("15:00:00"),
]);

function timeToMinutes(timeStr: string): number {
    const [hours, minutes] = timeStr.split(":").map(Number);
    return hours * 60 + minutes;
}

function minutesToTime(minutes: number): string {
    const h = Math.floor(minutes / 60);
    const m = minutes % 60;
    return `${h.toString().padStart(2, "0")}:${m.toString().padStart(2, "0")}:00`;
}
</script>
