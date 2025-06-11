<template>
    <div class="page-container">
        <UBreadcrumb :items="items" v-if="items" />
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
});
</script>
<style scoped lang="scss">
.page-container {
    display: flex;
    flex-direction: column;
    padding: 10px;
    width: 100%;
    gap: 10px;
    box-sizing: border-box;

    .header {
        font-size: 24px;
        font-weight: bold;
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
