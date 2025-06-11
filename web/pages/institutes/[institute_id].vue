<template>
    <institute-form :institute_id="institute_id" @deleted="onDelete" />
</template>
<script setup>
import { routesNames } from "@typed-router";
definePageMeta({
    middleware: ["admin"],
});
const { institute_id } = useRoute().params;

const onDelete = () => {
    const router = useRouter();

    router.push({ name: routesNames.institutes });
};
</script>
