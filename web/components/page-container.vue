<template>
    <div class="page-container" :class="{ 'full-height': fullHeight }">
        <div class="header">
            <UBreadcrumb :items="items" v-if="items" class="breadcrumb" />
            <slot name="header" />
        </div>
        <div class="content">
            <slot />
        </div>
    </div>
</template>
<script setup>
defineProps({
    items: {
        type: Array,
    },
    fullHeight: {
        type: Boolean,
        default: false,
    },
});
</script>
<style scoped lang="scss">
.page-container {
    display: flex;
    flex-direction: column;
    height: 100%;
    width: 100%;
    gap: 10px;
    box-sizing: border-box;
    @include lg(true) {
        gap: 8px;
        .header {
            padding-bottom: 0px;

            display: none !important;
        }
    }
    .header {
        display: flex;
        align-items: center;
        flex-wrap: wrap;
        &:empty {
            display: none;
        }
        .breadcrumb {
            margin-right: auto;
        }
    }

    &.full-height {
        height: 100%;
    }

    .content {
        flex: 1;
        display: flex;
        flex-direction: column;
        gap: 10px;
        overflow-y: auto;
    }
}
</style>
