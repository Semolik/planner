<template>
    <nuxt-link :key="task.id" class="card">
        <div class="text-md font-semibold text-gray-800">
            {{ task.event ? task.event.name : task.name }}
        </div>
        <template v-if="task.event">
            <div class="flex gap-2">
                <div class="text-sm text-gray-500 flex items-center gap-1">
                    <Icon name="material-symbols:calendar-today-rounded" />

                    {{ getDateString(task.event.date) }}
                </div>

                <div class="text-sm text-gray-500 flex items-center gap-1">
                    <Icon
                        name="material-symbols:nest-clock-farsight-analog-outline-rounded"
                    />
                    {{ startTime }} - {{ endTime }}
                </div>
            </div>
            <div class="inline-flex gap-1 text-sm text-gray-500">
                <Icon
                    name="material-symbols:location-on-rounded"
                    class="mt-[2px]"
                />

                <span>
                    {{ task.event.location }}
                </span>
            </div>
        </template>
    </nuxt-link>
</template>
<script setup>
const { task } = defineProps({
    task: {
        type: Object,
        required: true,
    },
});
const startTime = computed(() => {
    if (!task.event) return;
    return task.event.start_time.split(":").slice(0, 2).join(":");
});
const endTime = computed(() => {
    if (!task.event) return;
    return task.event.end_time.split(":").slice(0, 2).join(":");
});
</script>
<style scoped lang="scss">
.card {
    display: flex;
    flex-direction: column;
    gap: 5px;
    padding: 10px;
    border: 1px solid var(--ui-border);
    padding: calc(0.25rem * 4);
    border-radius: 0.5rem;

    &:hover {
        border-color: var(--ui-primary);
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }
    .badges {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;

        .badge {
            font-size: 14px;
            border-radius: 20px;
            text-align: center;
            display: flex;
            align-items: center;
            gap: 3px;
            justify-content: center;
        }
    }
}
</style>
