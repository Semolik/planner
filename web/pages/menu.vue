<template>
    <app-aside :blocks="asideBlocks"/>
</template>
<script setup>
import { routesNames } from "@typed-router";
import { useAuthStore } from "~/stores/auth";

const authStore = useAuthStore();
const asideBlocks = computed(() => {
    const blocks = [
        {
            name: null,
            items: [
                {
                    name: "Профиль",
                    path: routesNames.usersMe,
                    icon: "material-symbols:person-rounded",
                },
                {
                    name: "Мои задачи",
                    icon: "material-symbols:task-alt-rounded",
                    path: routesNames.tasksMy,
                },
                   {
                  name: "Моя статистика",
                  icon: "material-symbols:bar-chart-rounded",
                  path: routesNames.statisticsMe,
                }
            ],
        },
        {
            name: "Мероприятия",
            items: [
                {
                    name: "Мероприятия и задачи",
                    path: routesNames.tasks,
                    icon: "material-symbols:calendar-month",
                },
                {
                    name: "Группы мероприятий",
                    path: routesNames.eventsGroups,
                    icon: "material-symbols:folder-rounded",
                },
            ],
        },
    ];
    if (authStore.isAdmin) {
        blocks.push({
            name: "Администрирование",
            items: [
                {
                    name: "Пользователи",
                    path: routesNames.users,
                    icon: "material-symbols:person-rounded",
                },

                {
                    name: "Статистика",
                    icon: "material-symbols:analytics-outline-rounded",
                    path: routesNames.statistics,
                },
                {
                    name: "Институты",
                    path: routesNames.institutes,
                    icon: "material-symbols:account-balance-rounded",
                },
                {
                    name: "Привязанные чаты",
                    icon: "material-symbols:chat-rounded",
                    path: routesNames.chats,
                },
                {
                    name: "Настройки",
                    icon: "material-symbols:settings-rounded",
                    path: routesNames.settings,
                },
            ],
        });
    }

    return blocks;
});
</script>
