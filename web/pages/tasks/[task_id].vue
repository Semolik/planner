<template>
    <page-container :items="sections" full-height>
        <div class="task-card-container">
            <div class="task-card shadow-lg">
                <div class="head">
                    {{ task.event ? task.event.name : task.name }}
                </div>
                <div class="badges">
                    <template v-if="task.event">
                        <UBadge
                            color="neutral"
                            variant="outline"
                            size="lg"
                            icon="material-symbols:calendar-today"
                        >
                            {{ dateTextFormat(task.event.date) }}
                        </UBadge>
                        <UBadge
                            color="neutral"
                            variant="outline"
                            size="lg"
                            icon="material-symbols:nest-clock-farsight-analog-outline"
                        >
                            {{ getTime(task.event.start_time) }} -
                            {{ getTime(task.event.end_time) }}
                        </UBadge>
                        <UBadge
                            color="neutral"
                            variant="outline"
                            size="lg"
                            icon="material-symbols:location-on"
                        >
                            {{ task.event.location }}
                        </UBadge>
                        <UBadge
                            color="neutral"
                            variant="outline"
                            size="lg"
                            icon="material-symbols:hourglass-bottom"
                        >
                            {{ getWaitingTime(task.event) }}
                        </UBadge>
                    </template>
                </div>
            </div>
        </div>
    </page-container>
</template>
<script setup>
import { routesNames } from "@typed-router";
import { TasksService } from "~/client";
const { task_id } = useRoute().params;
const task = await TasksService.getTaskByIdTasksTaskIdGet(task_id);
const sections = [
    {
        label: "Мероприятия и задачи",
        to: {
            name: routesNames.tasks,
        },
    },
    {
        label: task.name + (task.event ? ` (${task.event.name})` : ""),
        to: {
            name: routesNames.tasksTaskId,
            params: { task_id: task_id },
        },
    },
];
const dateTextFormat = (date) => {
    const options = { year: "numeric", month: "long", day: "numeric" };
    return new Date(date).toLocaleDateString(undefined, options);
};

const getTime = (time) => {
    if (!time) return "";
    const [hours, minutes] = time.split(":");
    return `${hours}:${minutes}`;
};

const getWaitingTime = (event) => {
    if (!event) return "";
    const eventDate = new Date(event.date);
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
</script>
<style scoped lang="scss">
.task-card-container {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100%;

    .task-card {
        width: 100%;
        max-width: 500px;
        border: 1px solid $border-color;
        border-radius: 8px;
        padding: 16px;
        display: flex;
        flex-direction: column;
        gap: 8px;
        .head {
            font-size: 1.5rem;
            color: $text-color;
        }
        .badges {
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
        }
    }
}
</style>
