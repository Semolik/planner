<template>
    <nuxt-link
        :key="task.id"
        class="card"
        :to="{
            name: routesNames.tasksTaskId,
            params: { task_id: task.id },
        }"
    >
        <div class="text-md font-semibold text-gray-800">
            {{ task.event ? task.event.name : task.name }}
        </div>
        <template v-if="task.event">
            <div class="flex gap-2">
                <div class="text-sm text-gray-500 flex items-center gap-1">
                    <Icon name="material-symbols:calendar-today-rounded" />

                    {{ getDateString(task.event.date) }} ({{ daysLeft }})
                </div>

                <div v-if="timeRange" class="text-sm text-gray-500 flex items-center gap-1">
                    <Icon
                        name="material-symbols:nest-clock-farsight-analog-outline-rounded"
                    />
                    {{ timeRange }}
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
        <template v-else>
            <div class="flex gap-2 flex-col">
                <div
                    v-for="typed_task in task.typed_tasks"
                    class="text-sm text-gray-500 flex items-center gap-1"
                >
                    <Icon
                        :name="icons[typed_task.task_type]"
                        class="mt-[2px]"
                    />
                    {{ typedTasksLabels[typed_task.task_type] }}:
                    {{ getDateString(typed_task.due_date) }} ({{
                        getDaysLeft(typed_task.due_date)
                    }})
                </div>
            </div>
        </template>

        <div v-if="showLabels" class="flex gap-1 flex-wrap">
            <template v-for="typed_task in task.typed_tasks">
                <UBadge
                    v-if="
                        typed_task.task_states.length === 0 ||
                        (task.event
                            ? task.event.required_photographers !==
                              typed_task.task_states.length
                            : false)
                    "
                    color="error"
                >
                    Нуж{{ typed_task.for_single_user ? "ен" : "ны" }}
                    {{ typedTasksLabels[typed_task.task_type].toLowerCase() }}
                </UBadge>
            </template>
        </div>
    </nuxt-link>
</template>
<script setup>
import { routesNames } from "@typed-router";
import { UserRole } from "~/client";
const { task } = defineProps({
    task: {
        type: Object,
        required: true,
    },
});
const showLabels = computed(() => {
    if (task.event) {
        const photographer = task.typed_tasks.find(
            (t) => t.task_type === UserRole.PHOTOGRAPHER
        );
        if (
            photographer &&
            photographer.task_states.length == 0 &&
            task.event.is_passed
        ) {
            return false;
        }
    }
    return true;
});
const typedTasksLabels = computed(() => {
    const labels = {};
    for (const typed_task of task.typed_tasks) {
        const role = typed_task.task_type;
        labels[role] = typed_task.for_single_user
            ? {
                  [UserRole.PHOTOGRAPHER]: "Фотограф",
                  [UserRole.DESIGNER]: "Дизайнер",
                  [UserRole.COPYWRITER]: "Копирайтер",
              }[role]
            : {
                  [UserRole.PHOTOGRAPHER]: "Фотографы",
                  [UserRole.DESIGNER]: "Дизайнеры",
                  [UserRole.COPYWRITER]: "Копирайтеры",
              }[role];
    }
    return labels;
});

const icons = {
    [UserRole.PHOTOGRAPHER]: "material-symbols:photo-camera",
    [UserRole.DESIGNER]: "material-symbols:design-services",
    [UserRole.COPYWRITER]: "material-symbols:edit",
};

const formatTime = (time) => {
    if (!time) return null;
    return time.split(":").slice(0, 2).join(":");
};

const timeRange = computed(() => {
    if (!task.event) return null;
    const start = formatTime(task.event.start_time);
    const end = formatTime(task.event.end_time);

    if (start && end) return `${start} - ${end}`;
    if (start) return `с ${start}`;
    if (end) return `до ${end}`;
    return null;
});
const getDaysLeft = (date) => {
    const eventDate = new Date(date);
    const today = new Date();
    const diffTime = eventDate - today;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    if (diffDays > 0) {
        return `через ${diffDays} ${usePluralize(diffDays, [
            "день",
            "дня",
            "дней",
        ])}`;
    } else if (diffDays < 0) {
        return `${Math.abs(diffDays)} ${usePluralize(Math.abs(diffDays), [
            "день",
            "дня",
            "дней",
        ])} назад`;
    } else {
        return "Сегодня";
    }
};
const daysLeft = computed(() => {
    if (!task.event) return;
    return getDaysLeft(task.event.date);
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
