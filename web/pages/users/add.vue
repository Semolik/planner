<template>
    <user-form createMode @created="onCreated" />
</template>
<script setup>
import { routesNames } from "@typed-router";
definePageMeta({
    middleware: ["admin"],
});

const onCreated = (user) => {
    useRouter().push({
        name: routesNames.usersUserId,
        params: { user_id: user.id },
    });
};
</script>
