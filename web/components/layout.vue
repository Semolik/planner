<template>
    <UApp>
        <NuxtLoadingIndicator />

        <div class="default-layout">
            <app-aside :blocks="asideBlocks" v-if="authStore.logined" />

            <div id="teleports"></div>
            <div :class="['default-layout__content', { padding: !noPadding }]">
                <slot />
            </div>
        </div>
    </UApp>
</template>
<script setup>
import { routesNames } from "@typed-router";

import { useAuthStore } from "~/stores/auth";
const { noPadding } = defineProps({
    noPadding: {
        type: Boolean,
        default: false,
    },
});
const authStore = useAuthStore();

const asideBlocks = computed(() => {
    const blocks = [
        {
            name: null,
            items: [
                {
                    name: "Главная",
                    path: routesNames.index,
                    icon: "material-symbols:home-rounded",
                },
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
            ],
        },
        {
            name: "Мероприятия",
            items: [
                {
                    name: "Мероприятия и задачи",
                    path: routesNames.tasks,
                    icon: "material-symbols:list-rounded",
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
<style lang="scss">
.default-layout {
    display: flex;

    height: 100%;
    max-width: 100%;
    overflow-y: auto;
    isolation: isolate;

    &__content {
        flex: 1;
        min-width: 0;
        max-height: 100%;
        width: 100%;
        margin: 0 auto;
        z-index: 0;

        &.padding {
            padding: 13px;
        }
    }
}
</style>
