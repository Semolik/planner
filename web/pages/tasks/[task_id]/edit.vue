<template>
    <app-form
        full-height
        max-width="1000px"
        no-padding
        :class="{ 'min-h-[650px]': task.event }"
    >
        <template #top>
            <UBreadcrumb :items="sections" />
        </template>
        <div class="edit-form">
            <div class="form-header">
                {{ task.event ? task.event.name : task.name }}
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
        (task.value.event ? task.value.event.name : task.value.name) +
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
            task.value.name +
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
    .form-header {
        padding: 10px;
        font-size: 20px;
        text-align: center;
        grid-column: 1 / -1;
        border-bottom: 1px solid $border-color;
    }
    .form-content {
        grid-column: 2;
        padding: 10px;
        display: flex;
        flex-direction: column;
        gap: 20px;
    }
    aside {
        display: flex;
        flex-direction: column;
        gap: 5px;
        padding: 10px;
        height: 100%;
        border-right: 1px solid $border-color;
        a {
            display: flex;
            padding: 5px 10px;
            text-decoration: none;
            align-items: center;
            gap: 10px;
            border-radius: 10px;
            // font-size: 15px;
            border: 1px solid $text-color-secondary;
            cursor: pointer;
            color: $text-color-secondary;
            word-wrap: break-word;
            overflow-wrap: anywhere;
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
