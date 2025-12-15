<template>
    <user-statistics :user-id="params.user_sid" />
</template>

<script setup>
definePageMeta({
    layout: "no-padding",
});
const {params} = useRoute();
</script>