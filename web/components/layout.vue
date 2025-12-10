<template>
    <UApp>
        <NuxtLoadingIndicator />

        <div class="default-layout">
            <template v-if="authStore.logined">
                <app-head v-if="$viewport.isLessThan('lg')" />
                <app-aside :blocks="asideBlocks" v-else>
                    <template #head>
                        <app-head />
                    </template>
                </app-aside>
            </template>

            <div id="teleports"></div>
            <div :class="['default-layout__content', { padding: !noPadding }]">
                <slot />
            </div>
            <div
                class="bottom-bar"
                v-if="authStore.logined && $viewport.isLessThan('lg')"
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
const { $viewport } = useNuxtApp();
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
    @include lg(true) {
        flex-direction: column;
    }

    &__content {
        flex: 1;
        min-width: 0;
        max-height: 100%;
        width: 100%;
        overflow-y: auto;
        margin: 0 auto;
        z-index: 0;
        &.padding {
            padding: 13px;
        }
        @include lg(true) {
            overflow: auto;
            padding: 8px !important;
        }
    }
    .bottom-bar {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 10px;
        padding: 8px;
        border-top: 1px solid $border-color;
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
