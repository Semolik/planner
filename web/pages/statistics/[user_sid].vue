<template>
    <user-statistics :userId="params.user_sid" />
</template>

<script setup>
definePageMeta({
    layout: "no-padding",
});
const {params} = useRoute();
</script>