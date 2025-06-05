<template>
    <UApp>
        <NuxtLoadingIndicator />

        <div class="default-layout">
            <Header />
            <app-aside :blocks="asideBlocks" v-if="authStore.logined">
            </app-aside>
            <div id="teleports"></div>
            <div class="default-layout__content">
                <slot />
            </div>
        </div>
    </UApp>
</template>
<script setup>
import { routesNames } from "@typed-router";
import { useAuthStore } from "~/stores/auth";

const authStore = useAuthStore();

const asideBlocks = [
    {
        name: null,
        items: [
            {
                name: "Главная",
                path: routesNames.index,
                icon: "material-symbols:home",
            },
            {
                name: "Мероприятия",
                path: routesNames.events,
                icon: "material-symbols:list-rounded",
            },
        ],
    },
];
</script>
<style lang="scss">
body {
    padding-top: 60px;
}
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
        padding: 13px;
        z-index: 0;
    }
}
</style>
