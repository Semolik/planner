<template>
    <div class="time-range-slider space-y-4">
        <label class="block mb-2 text-sm font-medium">{{ label }}</label>
        <USlider
            v-model="internalValue"
            :min="minMinutes"
            :max="maxMinutes"
            :step="step"
            :min-steps-between-thumbs="1"
            color="neutral"
            @change="(value) => emit('change')"
        />
        <div
            class="flex justify-between text-sm text-gray-500 dark:text-gray-400"
        >
            <span>{{ formattedMin }}</span>
            <span>{{ formattedMax }}</span>
        </div>
    </div>
</template>

<script setup lang="ts">
interface Props {
    modelValue?: number[];
    minTime?: string;
    maxTime?: string;
    step?: number;
    label?: string;
}
const formattedMax = computed(() => {
    return props.maxTime.split(":").slice(0, 2).join(":");
});
const formattedMin = computed(() => {
    return props.minTime.split(":").slice(0, 2).join(":");
});
const props = withDefaults(defineProps<Props>(), {
    modelValue: () => [] as number[],
    minTime: "10:00",
    maxTime: "18:00",
    step: 10,
    label: "Выберите временной диапазон",
});

const emit = defineEmits<{
    (e: "update:modelValue", value: number[]): void;
    (e: "change"): void;
}>();

function timeToMinutes(timeStr: string): number {
    const [hours, minutes] = timeStr.split(":").map(Number);
    return hours * 60 + minutes;
}

const minMinutes = timeToMinutes(props.minTime);
const maxMinutes = timeToMinutes(props.maxTime);

const internalValue = ref<number[]>(
    props.modelValue.length ? [...props.modelValue] : [minMinutes, maxMinutes]
);

watch(internalValue, (newVal) => {
    emit("update:modelValue", newVal);
});
</script>
