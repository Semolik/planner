<template>
    <UApp>
        <NuxtLoadingIndicator />

        <div class="default-layout use-max-width">
            <Header />
            <app-aside :blocks="asideBlocks" />
            <div id="teleports"></div>
            <div class="default-layout__content">
                <slot />
            </div>
        </div>
    </UApp>
</template>
<script setup>
import { routesNames } from "@typed-router";

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

    &.use-max-height .default-layout__content {
        max-height: calc(100vh - 60px);
        overflow-y: auto;
    }

    &.use-max-width &__content {
        max-width: 1250px;
    }
    &__content {
        flex: 1;
        min-width: 0;
        max-height: 100%;
        width: 100%;
        margin: 0 auto;
        z-index: 0;
    }
}
</style>
