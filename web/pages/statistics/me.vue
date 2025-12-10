<template>
    <user-statistics :userId="authStore.userData?.id" />

</template>

<script setup>
definePageMeta({
    layout: "no-padding",
});
import { useAuthStore } from "~/stores/auth";
const authStore = useAuthStore();
</script>