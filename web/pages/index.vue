<template>
    <div class="index-page"></div>
</template>
<script setup>
useSeoMeta({
    title: "Главная",
});
definePageMeta({
    middleware: ["user"],
});
</script>
<style lang="scss" scoped>
.index-page {
    display: flex;
    flex-direction: column;
    padding: 10px;
    gap: 10px;
}
</style>
