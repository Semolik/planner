<template>
    <page-container
        :items="[
            {
                label: 'Институты',
                to: {
                    name: routesNames.institutes,
                },
            },
        ]"
    >
        <app-button active :to="{ name: routesNames.institutesNew }">
            Создать институт
        </app-button>
        <list
            :items="institutes"
            :link-builder="
                (item) => ({
                    name: routesNames.institutesInstituteId,
                    params: { institute_id: item.id },
                })
            "
        />
    </page-container>
</template>
<script setup>
import { routesNames } from "@typed-router";
import { InstitutesService } from "~/client";
definePageMeta({
    middleware: ["admin"],
});
const institutes = await InstitutesService.getInstitutesInstitutesGet();
</script>
