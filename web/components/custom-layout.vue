<template>
    <UApp>
        <NuxtLoadingIndicator />

        <div
            class="default-layout"
            :class="[
                { 'use-max-width': useMaxWidth },
                { 'use-max-height': useMaxHeight },
            ]"
        >
            <Header />
            <slot name="for-teleports" />
            <div id="asidebar"></div>
            <div id="teleports"></div>
            <div class="default-layout__content">
                <slot />
            </div></div
    ></UApp>
</template>
<script setup>
defineProps({
    useMaxWidth: {
        type: Boolean,
        default: true,
    },
    useMaxHeight: {
        type: Boolean,
        default: false,
    },
});
</script>
<style lang="scss">
body {
    padding-top: 60px;
}
.default-layout {
    display: flex;
    flex-direction: column;
    height: 100%;
    max-width: 100%;
    overflow-y: auto;
    isolation: isolate;

    &.use-max-height .default-layout__content {
        max-height: calc(100vh - 60px);
        overflow-y: auto;
    }
    &:has(#asidebar:not(:empty)) {
        display: grid;
        grid-template-columns: min-content 1fr;
        &:has(#teleports:empty) {
            #asidebar {
                grid-column: 1;
                grid-row: 1;
                min-width: min-content;
                height: 100%;
                z-index: -1;
            }

            .default-layout__content {
                grid-column: 2;
                grid-row: 1;
            }

            #teleports {
                display: none;
            }
        }
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
