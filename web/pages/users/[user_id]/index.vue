<template>
    <user-form :user-id="user_id" @deleted="onDeleted" />
</template>
<script setup>
import { routesNames } from "@typed-router";
definePageMeta({
    middleware: ["admin"],
});
const { user_id } = useRoute().params;
const onDeleted = () => {
    useRouter().push({ name: routesNames.users });
};
</script>
