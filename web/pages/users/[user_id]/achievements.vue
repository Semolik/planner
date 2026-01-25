<script setup lang="ts">
const route = useRoute();
const userId = computed(() => (route.params as any).user_id as string);

definePageMeta({

    layout: "no-padding",
});

useHead({
    title: "ПГАС пользователя",
});
</script>

<template>
    <UserPgas :user-id="userId" />
</template>

