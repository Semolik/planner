<template>
    <event-group-form :group_id="group_id" />
</template>

<script setup>
const { group_id } = useRoute().params;
definePageMeta({
    middleware: ["admin"],
});
</script>
