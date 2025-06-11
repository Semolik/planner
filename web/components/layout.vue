<template>
    <UApp>
        <NuxtLoadingIndicator />

        <div class="default-layout">
            <app-aside :blocks="asideBlocks" v-if="authStore.logined">
            </app-aside>
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

const asideBlocks = [
    {
        name: null,
        items: [
            {
                name: "Главная",
                path: routesNames.index,
                icon: "material-symbols:home-rounded",
            },
            {
                name: "Мероприятия",
                path: routesNames.events,
                icon: "material-symbols:list-rounded",
            },
        ],
    },
];
if (authStore.isAdmin) {
    asideBlocks.push({
        name: "Администрирование",
        items: [
            {
                name: "Институты",
                path: routesNames.institutes,
                icon: "material-symbols:account-balance-rounded",
            },
            {
                name: "Пользователи",
                path: routesNames.users,
                icon: "material-symbols:person-rounded",
            },
        ],
    });
}
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
