<template>
    <nuxt-link
        :key="task.id"
        class="card"
        :to="{
            name: routesNames.tasksTaskId,
            params: { task_id: task.id },
        }"
    >
        <div class="head">
            <div class="name">
                {{ task.event ? task.event.name : task.name }}
            </div>
            <div v-if="task.event" class="date">
                {{ getDateString(task.event.date) }}
            </div>
        </div>
        <div class="typed-tasks">
            <div
                v-for="typed_task in task.typed_tasks"
                :key="typed_task.id"
                class="typed-task"
                :class="[
                    typed_task.task_states[0].state,
                    getTypedTaskDeadlineClass(typed_task),
                ]"
            >
                <template v-if="!task.event">
                    <div class="name">{{ typed_task.description }}</div>
                </template>
                <template v-else>
                    <div class="name">
                        <template
                            v-if="
                                typed_task.task_type === UserRole.PHOTOGRAPHER
                            "
                        >
                            Обработать репортаж
                        </template>
                        <template
                            v-if="typed_task.task_type === UserRole.COPYWRITER"
                        >
                            Написать пост
                        </template>
                        <template
                            v-if="typed_task.task_type === UserRole.DESIGNER"
                        >
                            Сделать обложку альбома
                        </template>
                    </div>
                </template>
                <div class="value">
                    Дедлайн
                    {{ getTypedTaskDeadline(typed_task) }}
                </div>
            </div>
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

const getTimeDiff = (date) => {
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

const getTypedTaskDeadline = (typed_task) => {
    return getTimeDiff(typed_task.due_date);
};
const getTypedTaskDeadlineClass = (typed_task) => {
    const diff = new Date(typed_task.due_date) - new Date();
    if (diff < 0) return "red";
    if (diff < 24 * 2 * 60 * 60 * 1000) return "yellow";
    return "";
};
</script>
<style scoped lang="scss">
.card {
    display: flex;
    flex-direction: column;
    gap: 5px;
    .typed-tasks {
        display: flex;
        flex-direction: column;
        gap: 5px;
    }
    &:hover .head {
        background-color: $text-color;
        color: white;
    }
    .typed-task,
    .head {
        padding: 10px;
        border: 1px solid var(--ui-border);
        padding: calc(0.25rem * 4);
        border-radius: 0.5rem;

        display: flex;
        justify-content: space-between;
        align-items: center;
        &.head {
            border: 1px solid $text-color;
        }

        .name,
        .value,
        .date {
            font-size: 14px;
        }
        &.typed-task {
            display: flex;

            .name {
                display: flex;
                align-items: center;
                gap: 5px;
                &::before {
                    content: "";
                    display: inline-block;
                    width: 8px;
                    height: 8px;
                    border-radius: 50%;
                    background-color: $accent;
                }
            }
            &.pending .name::before {
                background-color: $accent-warning;
            }
            &.completed .name::before {
                background-color: $accent-success;
            }
            &.cancelled .name::before {
                background-color: $accent-red;
            }

            &.red {
                background-color: $accent-red;
                color: black;
                .name::before {
                    display: none;
                }
            }
            &.yellow {
                background-color: $accent-warning;
                color: black;

                .name::before {
                    display: none;
                }
            }
            &.green {
                background-color: $accent-success;
                color: black;

                .name::before {
                    display: none;
                }
            }
        }
    }
}
</style>
