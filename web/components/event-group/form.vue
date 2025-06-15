<template>
    <app-form
        full-height
        :headline="group_id ? 'Редактирование группы' : 'Создание группы'"
    >
        <template #top>
            <UBreadcrumb :items="sections" />
        </template>
        <div class="flex flex-col gap-2">
            <app-input v-model="name" label="Название" required white />
            <app-input
                v-model="description"
                label="Описание"
                type="textarea"
                white
            />
            <div class="flex gap-1 w-full">
                <app-input
                    v-model="link"
                    label="Ссылка"
                    white
                    :validator="() => linkIsValid"
                />
                <component
                    :is="link && linkIsValid ? 'a' : 'div'"
                    :href="link"
                    target="_blank"
                    class="link"
                    :class="{ disabled: !linkIsValid || !link }"
                    rel="noopener noreferrer"
                >
                    <UIcon name="material-symbols:open-in-new" />
                </component>
            </div>
            <app-input v-model="organizer" label="Контакт организатора" white />
            <app-button :active="saveButtonActive" @click="handleSave">
                Сохранить
            </app-button>
            <app-button active red @click="deleteGroupModalOpen = true">
                Удалить группу
            </app-button>
        </div>
    </app-form>
    <UModal
        v-model:open="deleteGroupModalOpen"
        v-if="group"
        title="Удаление группы мероприятий"
    >
        <template #body>
            <div class="flex flex-col gap-2">
                <p></p>
                <div class="text-md">
                    Вы действительно хотите удалить группу "{{ group.name }}"?
                </div>
                <UCheckbox
                    v-model="deleteGroupEvents"
                    variant="card"
                    color="neutral"
                    label="Удалить все мероприятия в группе"
                />
                <div class="grid grid-cols-2 gap-2 mt-4">
                    <app-button active red @click="deleteGroup">
                        Подтвердить
                    </app-button>
                    <app-button
                        @click="deleteGroupModalOpen = false"
                        class="cursor-pointer"
                    >
                        Отмена
                    </app-button>
                </div>
            </div>
        </template>
    </UModal>
</template>

<script setup>
import { routesNames } from "@typed-router";
import { EventsGroupsService } from "~/client";

const { group_id } = defineProps({
    group_id: {
        type: String,
        default: null,
    },
});
const deleteGroupModalOpen = ref(false);
const deleteGroupEvents = ref(false);
watch(deleteGroupModalOpen, (newValue) => {
    if (!newValue) {
        deleteGroupEvents.value = false;
    }
});
const group = ref(
    group_id
        ? await EventsGroupsService.getEventGroupEventsGroupsGroupIdGet(
              group_id
          )
        : null
);
useSeoMeta({
    title: group.value
        ? `Группа: ${group.value.name} - Редактирование`
        : "Создание группы мероприятий",
});

const sections = computed(() => {
    const base = [
        {
            label: "Группы",
            to: {
                name: routesNames.eventsGroups,
            },
        },
    ];

    if (group.value) {
        base.push(
            {
                label: group.value.name,
                to: {
                    name: routesNames.eventsGroupsGroupId,
                    params: { group_id },
                },
            },
            {
                label: "Редактирование",
                to: {
                    name: routesNames.eventsGroupsGroupIdEdit,
                    params: { group_id },
                },
            }
        );
    } else {
        base.push({
            label: "Создание группы",
            to: {
                name: routesNames.eventsGroupsNew,
            },
        });
    }

    return base;
});
const name = ref(group.value ? group.value.name : "");
const description = ref(group.value ? group.value.description : "");
const link = ref(group.value ? group.value.link : "");
const linkIsValid = computed(() => {
    if (!link.value) return true;
    return validateUrl(link.value);
});
const organizer = ref(group.value ? group.value.organizer : "");
const saveButtonActive = computed(() => {
    return (
        name.value.length > 0 &&
        linkIsValid.value &&
        (group.value
            ? name.value !== group.value.name ||
              description.value !== group.value.description ||
              link.value !== group.value.link ||
              organizer.value !== group.value.organizer
            : true)
    );
});
const { $toast } = useNuxtApp();
const handleSave = async () => {
    if (!saveButtonActive.value) return;

    try {
        if (!group.value) {
            const newGroup =
                await EventsGroupsService.createEventGroupEventsGroupsPost({
                    name: name.value,
                    description: description.value,
                    link: link.value,
                    organizer: organizer.value,
                });
            const router = useRouter();
            router.push({
                name: routesNames.eventsGroupsGroupIdEdit,
                params: { group_id: newGroup.id },
            });
        } else {
            group.value =
                await EventsGroupsService.updateEventGroupEventsGroupsGroupIdPut(
                    group_id,
                    {
                        name: name.value,
                        description: description.value,
                        link: link.value,
                        organizer: organizer.value,
                    }
                );
        }
    } catch (error) {
        console.error("Error updating group:", error);
        $toast.error(HandleOpenApiError(error).message);
    }
};
const deleteGroup = async () => {
    try {
        await EventsGroupsService.deleteEventGroupEventsGroupsGroupIdDelete(
            group_id,
            deleteGroupEvents.value
        );
        const router = useRouter();
        router.push({ name: routesNames.eventsGroups });
        deleteGroupModalOpen.value = false;
    } catch (error) {
        $toast.error(HandleOpenApiError(error).message);
    }
};
</script>
<style scoped lang="scss">
.link {
    height: 40px;
    max-width: 40px;
    margin-top: auto;
    background-color: $text-color;
    width: 100%;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: background-color 0.3s ease;
    cursor: pointer;
    &:hover {
        background-color: $text-color-secondary;
    }

    &.disabled {
        background-color: $text-color-tertiary;
        cursor: not-allowed;
    }

    .iconify {
        color: white;
    }
}
</style>
