<template>
    <UApp>
        <NuxtLoadingIndicator />

        <div class="default-layout">
            <template v-if="authStore.logined">
                <app-head v-if="$viewport.isLessThan('lg')" />
                <app-aside v-else :blocks="asideBlocks">
                    <template #head>
                        <app-head />
                    </template>
                </app-aside>
            </template>

            <div id="teleports"/>
            <div :class="['default-layout__content', { padding: !noPadding, 'has-bottom-bar': authStore.logined && $viewport.isLessThan('lg') }]">
                <slot />
            </div>
            <div
                v-if="authStore.logined && $viewport.isLessThan('lg')"
                class="bottom-bar"
            >
                <nuxt-link class="bottom-bar-item" to="/">
                    <Icon name="material-symbols:home-rounded" />
                </nuxt-link>
                <nuxt-link class="bottom-bar-item" to="/tasks">
                    <Icon name="material-symbols:calendar-month" />
                </nuxt-link>
                <nuxt-link class="bottom-bar-item" to="/menu">
                    <Icon
                        name="material-symbols:format-list-bulleted-rounded"
                    />
                </nuxt-link>
            </div>
        </div>
    </UApp>
</template>
<script setup>
import { routesNames } from "@typed-router";
import {storeToRefs} from "pinia";
import { useAuthStore } from "~/stores/auth";
const { $viewport } = useNuxtApp();
const { noPadding } = defineProps({
    noPadding: {
        type: Boolean,
        default: false,
    },
});
const authStore = useAuthStore();
const {userData} = storeToRefs(authStore);

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
        {
            name: "Отчеты",
            items: [

                {
                  name: "Моя статистика",
                  icon: "material-symbols:bar-chart-rounded",
                  path: routesNames.statisticsMe,
                },
                {
                    name: "Планерки",
                    path: routesNames.meetings,
                    icon: "material-symbols:meeting-room-rounded",
                },
                {
                    name: "ПГАС",
                    path: routesNames.usersUserIdAchievements,
                    params: {
                        user_id: userData.value?.id,
                    },
                    icon: "material-symbols:attach-money-rounded",
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
                    name: "Дни рождения",
                    path: routesNames.birthdays,
                    icon: "material-symbols:cake-rounded",
                },
                {
                    name: "Статистика",
                    icon: "material-symbols:analytics-outline-rounded",
                    path: routesNames.statistics,
                },
                {
                    name: "Отчетные периоды",
                    icon: "material-symbols:date-range-rounded",
                    path: routesNames.periods,
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
                    name: "GigaChat",
                    icon: "material-symbols:smart-toy-rounded",
                    path: routesNames.gigachat,
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
    display: grid;
    grid-template-columns: 280px 1fr;
    max-width: 100vw;
    min-height: 100vh;
    height: 100vh;
    overflow: hidden;
    isolation: isolate;
    
    & > .aside-fixed {
        grid-row: 1 / span 2;
        grid-column: 1 / 2;
        position: fixed;
        left: 0;
        top: 0;
        width: 280px;
        height: 100vh;
        z-index: 10;
        background: white;
        border-right: 1px solid $border-color;
        display: flex;
        flex-direction: column;
    }
    &__content {
        grid-column: 2 / 3;
        grid-row: 1 / 2;
        min-width: 0;
        max-height: 100vh;
        width: 100%;
        height: 100vh;
        overflow-y: auto;
        margin: 0;
        z-index: 0;
        &.padding {
            padding: 13px;
        }
        // На мобильных: контент занимает всю ширину и имеет безопасный отступ снизу под нижний бар
        &.has-bottom-bar {
            padding-bottom: calc(64px + env(safe-area-inset-bottom));
        }
        @include lg {
            margin-left: 0;
        }
        @include lg(true) {
            overflow: auto;
            padding: 8px !important;
            grid-column: 1 / -1; // одна колонка на мобильных
        }
    }
    .bottom-bar {
        position: fixed;
        left: 0;
        right: 0;
        bottom: 0;
        background: white;
        border-top: 1px solid $border-color;
        z-index: 20;
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 10px;
        padding: 8px calc(8px + env(safe-area-inset-left)) calc(8px + env(safe-area-inset-bottom)) calc(8px + env(safe-area-inset-right));

        .bottom-bar-item {
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 10px 8px;
            background: $secondary-bg;
            border: 1px solid $border-color;
            border-radius: 8px;
            .iconify {
                width: 20px;
                height: 20px;
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