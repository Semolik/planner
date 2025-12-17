<template>
    <app-form
        full-height
        max-width="1000px"
        no-padding
        :class="{ 'min-h-[650px]': task.event }"
    >
        <template #top>
            <UBreadcrumb
                v-if="$viewport.isGreaterThan('md')"
                :items="sections"
            />
        </template>
        <div class="edit-form">
            <div class="form-header">
                {{ task.event ? task.event.name : task.displayed_name }}
            </div>
            <aside>
                <nuxt-link
                    :to="{
                        name: routesNames.tasksTaskIdEdit.index,
                        params: { task_id: task_id },
                    }"
                >
                    Основная информация
                </nuxt-link>
                <nuxt-link
                    :to="{
                        name: routesNames.tasksTaskIdEdit.taskIdEditTypedTasks,
                        params: { task_id: task_id },
                    }"
                >
                    Подзадачи
                </nuxt-link>
                <nuxt-link
                    :to="{
                        name: routesNames.tasksTaskIdEdit.taskIdEditHistory,
                        params: { task_id: task_id },
                    }"
                >
                    История изменений
                </nuxt-link>
            </aside>
            <div class="form-content">
                <nuxt-page @update:task="task = $event" />
            </div>
            <app-button
                active
                class="lg:!hidden"
                :to="{
                    name: routesNames.tasksTaskId,
                    params: { task_id: task_id },
                }"
            >
                Назад к задаче
            </app-button>
        </div>
    </app-form>
</template>
<script setup>
import { routesNames } from "@typed-router";
import { TasksService } from "~/client";
const { task_id } = useRoute().params;
const task = ref(await TasksService.getTaskByIdTasksTaskIdGet(task_id));
provide("task", task);
definePageMeta({
    middleware: ["admin"],
});

useHead({
    title:
        (task.value.event ? task.value.event.name : task.value.displayed_name) +
        " - Редактирование",
});

const sections = computed(() => [
    {
        label: "Мероприятия и задачи",
        to: {
            name: routesNames.tasks,
        },
    },
    {
        label:
            task.value.displayed_name +
            (task.value.event ? ` (${task.value.event.name})` : ""),
        to: {
            name: routesNames.tasksTaskId,
            params: { task_id: task_id },
        },
    },
    {
        label: "Редактирование",
        to: {
            name: routesNames.tasksTaskIdEdit.index,
            params: { task_id: task_id },
        },
    },
]);
</script>
<style scoped lang="scss">
.edit-form {
    display: grid;
    grid-template-columns: 250px 1fr;
    grid-template-rows: min-content 1fr;
    height: 100%;
    @include lg(true) {
        grid-template-columns: 1fr;
        grid-template-rows: min-content min-content 1fr;

        gap: 8px;
    }
    .form-header {
        font-size: 1.5rem;
        grid-column: 1 / -1;
        @include lg {
            padding: 10px;
            border-bottom: 1px solid $border-color;
            text-align: center;
        }
    }
    .form-content {
        display: flex;
        flex-direction: column;
        gap: 20px;
        @include lg {
            padding: 10px;
            grid-column: 2;
        }
    }
    aside {
        display: flex;

        gap: 5px;

        @include lg {
            flex-direction: column;
            padding: 10px;
            border-right: 1px solid $border-color;
            height: 100%;
        }
        @include lg(true) {
            flex-wrap: wrap;
        }
        a {
            display: flex;
            padding: 5px 10px;
            text-decoration: none;
            align-items: center;
            gap: 10px;
            border-radius: 10px;
            border: 1px solid $text-color-secondary;
            cursor: pointer;
            color: $text-color-secondary;
            word-wrap: break-word;
            overflow-wrap: anywhere;
            @include lg(true) {
                flex-grow: 1;
                text-align: center;
                align-items: center;
                justify-content: center;
            }
            &.router-link-exact-active {
                color: white;
                background-color: black;
                border-color: transparent;

                .iconify {
                    color: white;
                }
            }
        }
    }
}
</style>
