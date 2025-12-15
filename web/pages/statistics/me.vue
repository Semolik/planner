<template>
    <user-statistics :user-id="authStore.userData?.id" />

</template>

<script setup>
import { useAuthStore } from "~/stores/auth";
definePageMeta({
    layout: "no-padding",
});
const authStore = useAuthStore();
</script>