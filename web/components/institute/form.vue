<template>
    <app-form
        :headline="institute ? 'Редактировать институт' : 'Создать институт'"
        full-height
        @submit="submit"
    >
        <template #top>
            <UBreadcrumb :items="items" />
        </template>
        <app-input v-model="name" label="Название" required white />
        <app-button :active="buttonActive" type="submit">
            {{ institute ? "Сохранить" : "Создать" }}
        </app-button>
        <app-button
            v-if="institute"
            active
            red
            @click="deleteInstitute"
            type="button"
        >
            Удалить
        </app-button>
    </app-form>
</template>
<script setup>
import { InstitutesService } from "~/client";
import { routesNames } from "@typed-router";

const { institute_id } = defineProps({
    institute_id: {
        type: String,
        required: false,
    },
});
const institute = ref(null);

const name = ref("");
if (institute_id) {
    institute.value =
        await InstitutesService.getInstituteInstitutesInstituteIdGet(
            institute_id
        );
    name.value = institute.value.name;
}
const items = [
    {
        label: "Институты",
        to: {
            name: routesNames.institutes,
        },
    },
    institute.value
        ? {
              label: institute.value.name,
              to: {
                  name: routesNames.institutesInstituteId,
                  params: { institute_id: institute_id },
              },
          }
        : { label: "Создание института" },
];
const buttonActive = computed(() => {
    return (
        name.value.length > 0 &&
        (institute.value ? institute.value.name !== name.value : true)
    );
});
const emit = defineEmits(["deleted", "created"]);
const { $toast } = useNuxtApp();
const submit = async () => {
    try {
        if (institute_id) {
            institute.value =
                await InstitutesService.updateInstituteInstitutesInstituteIdPut(
                    institute_id,
                    { name: name.value }
                );
        } else {
            institute.value =
                await InstitutesService.createInstituteInstitutesPost({
                    name: name.value,
                });
            emit("created", institute.value);
        }
    } catch (e) {
        $toast.error(HandleOpenApiError(e).message);
    }
};
const deleteInstitute = async () => {
    try {
        await InstitutesService.deleteInstituteInstitutesInstituteIdDelete(
            institute_id
        );

        emit("deleted", institute.value);
    } catch (e) {
        $toast.error(HandleOpenApiError(e).message);
    }
};
</script>
