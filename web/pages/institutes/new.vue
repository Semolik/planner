<template>
    <institute-form @created="onCreate" />
</template>
<script setup>
import { routesNames } from "@typed-router";
definePageMeta({
    middleware: ["admin"],
});

const onCreate = (institute) => {
    const router = useRouter();

    router.push({
        name: routesNames.institutesInstituteId,
        params: { institute_id: institute.id },
    });
};
</script>
