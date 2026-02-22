<template>
    <app-aside :blocks="asideBlocks" mobile/>
</template>
<script setup>
import { useAuthStore } from "~/stores/auth";

const authStore = useAuthStore();
const { getMenuBlocks, filterBlocksForMobile } = useMenuBlocks();

const asideBlocks = computed(() => {
    const blocks = getMenuBlocks();
    return filterBlocksForMobile(blocks, true); // всегда мобильный фильтр для меню
});
</script>
