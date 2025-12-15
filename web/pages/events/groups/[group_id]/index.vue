<template>
    <page-container :items="sections">
        <div class="header">
            <div class="headline">{{ group.name }}</div>
            <div class="badges">
                <UBadge
                    v-if="group.period_start && group.period_end"
                    color="neutral"
                    icon="material-symbols:calendar-today"
                    variant="outline"
                    size="lg"
                >
                    <template v-if="group.period_start !== group.period_end">
                        {{ getDateString(group.period_start) }} -
                        {{ getDateString(group.period_end) }}
                    </template>
                    <template v-else>
                        {{ getDateString(group.period_start) }}
                    </template>
                </UBadge>
                <UBadge
                    v-if="group.link"
                    color="neutral"
                    icon="material-symbols:link"
                    size="lg"
                    as="a"
                    :href="group.link"
                    rel="noopener noreferrer"
                    target="_blank"
                >
                    Ссылка на публикацию
                </UBadge>
                <UBadge
                    v-if="group.aggregate_task"
                    color="info"
                    icon="material-symbols:assignment"
                    size="lg"
                    as="nuxt-link"
                    @click="()=> $router.push({
                        name: routesNames.tasksTaskId,
                        params: { task_id: group.aggregate_task.id },
                    })"
                    class="cursor-pointer"
                >
                    Общая публикация
                </UBadge>
            </div>
            <div v-if="group.description" class="description">
                {{ group.description }}
            </div>
        </div>

        <div class="tasks-grid">
            <task-card v-for="task in tasks" :key="task.id" :task="task" />
        </div>
        <template v-if="authStore.isAdmin" #header>
            <app-button
                active
                mini
                :to="{
                    name: routesNames.eventsGroupsGroupIdEdit,
                    params: { group_id },
                }"
            >
                Редактировать
            </app-button>
        </template>
        <app-button
            v-if="authStore.isAdmin"
            active
            :to="{
                name: routesNames.eventsGroupsGroupIdEdit,
                params: { group_id },
            }"
            class="lg:!hidden mt-auto"
        >
            Редактировать
        </app-button>
    </page-container>
</template>
<script setup>
import { routesNames } from "@typed-router";
import { EventsGroupsService } from "~/client";
import { useAuthStore } from "~/stores/auth";
const { group_id } = useRoute().params;

const authStore = useAuthStore();
const group =
    await EventsGroupsService.getEventGroupEventsGroupsGroupIdGet(group_id);
useSeoMeta({
    title: `Группа: ${group.name}`,
});
const tasks = group.events.map((event) => {
    const eventCopy = { ...event };
    delete eventCopy.task;
    const task = { ...event.task, event: eventCopy };
    return task;
});
const sections = [
    {
        label: "Группы",
        to: {
            name: routesNames.eventsGroups,
        },
    },
    {
        label: group.name,
        to: {
            name: routesNames.eventsGroupsGroupId,
            params: { group_id },
        },
    },
];
</script>
<style scoped lang="scss">
.tasks-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
    gap: 16px;
}
.header {
    display: flex;
    flex-direction: column;
    gap: 8px;

    .badges {
        display: flex;
        gap: 5px;
    }
    .description {
        font-size: 14px;
        color: $text-color-secondary;
    }
    .headline {
        font-size: 24px;
        font-weight: bold;
    }
}
</style>
