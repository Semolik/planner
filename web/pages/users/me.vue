<template>
    <user-form :user-id="authStore.userData?.id" view-mode />
</template>
<script setup>
import { useAuthStore } from "~/stores/auth";
const authStore = useAuthStore();
useSeoMeta({
    title: "Мой профиль",
});
</script>
