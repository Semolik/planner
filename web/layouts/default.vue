<template>
    <NuxtLoadingIndicator />
    <div class="default-layout">
        <Aside />
        <div class="default-layout__content">
            <slot />
        </div>
    </div>
</template>
<style lang="scss">
.default-layout {
    display: flex;
    height: 100%;
    max-width: 100%;

    &__content {
        flex: 1;
        min-width: 0;
        max-height: 100%;
        overflow-y: auto;
    }
}
</style>
