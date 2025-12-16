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
            <div v-if="group && group.aggregate_task" class="flex gap-1 w-full">
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
            <app-button
                v-if="group && !group.aggregate_task && group.events && group.events.length > 0"
                active
                @click="convertToAggregatedModalOpen = true"
            >
                Преобразовать в группу с единой публикацией
            </app-button>
            <app-button
                v-if="group && group.aggregate_task"
                active
                red
                @click="removeAggregationModalOpen = true"
            >
                Отменить агрегацию
            </app-button>
            <app-button
                v-if="group && group.aggregate_task"
                active
                :to="{
                    name: routesNames.tasksTaskId,
                    params: { task_id: group.aggregate_task.id }
                }"
            >
                Перейти к задаче публикации
            </app-button>
            <app-button
                v-if="group"
                active
                red
                @click="deleteGroupModalOpen = true"
            >
                Удалить группу
            </app-button>
        </div>
    </app-form>
    <UModal
        v-if="group"
        v-model:open="deleteGroupModalOpen"
        title="Удаление группы мероприятий"
    >
        <template #body>
            <div class="flex flex-col gap-2">
                <p/>
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
                        class="cursor-pointer"
                        @click="deleteGroupModalOpen = false"
                    >
                        Отмена
                    </app-button>
                </div>
            </div>
        </template>
    </UModal>

    <UModal
        v-if="group && !group.aggregate_task"
        v-model:open="convertToAggregatedModalOpen"
        title="Преобразование в группу с единой публикацией"
        :ui="{ width: 'sm:max-w-3xl' }"
    >
        <template #body>
            <div class="flex flex-col gap-3">
                <UCheckbox
                    v-model="isSingleAlbum"
                    variant="card"
                    color="neutral"
                    label="Один альбом на все мероприятия (создать общую задачу для дизайнера)"
                />

                <div class="text-md font-semibold">Что произойдет при преобразовании:</div>

                <div class="flex flex-col gap-2 text-sm">
                    <div class="p-3 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg border border-yellow-200 dark:border-yellow-800">
                        <div class="font-medium mb-2">Будут удалены:</div>
                        <ul class="list-disc list-inside space-y-1">
                            <li v-if="isSingleAlbum">Все подзадачи дизайнеров во всех мероприятиях группы</li>
                            <li>Все подзадачи копирайтеров во всех мероприятиях группы</li>
                        </ul>
                    </div>

                    <div v-if="affectedUsers.length > 0" class="p-3 bg-red-50 dark:bg-red-900/20 rounded-lg border border-red-200 dark:border-red-800">
                        <div class="font-medium mb-2">Пользователи, которые будут сняты с задач:</div>
                        <div class="space-y-2 max-h-60 overflow-y-auto">
                            <div v-for="user in affectedUsers" :key="user.userId" class="pl-2">
                                <div class="font-medium">{{ user.userName }}</div>
                                <ul class="list-disc list-inside pl-4 text-xs">
                                    <li v-for="task in user.tasks" :key="task.id">
                                        {{ task.eventName }} - {{ task.taskType }}
                                    </li>
                                </ul>
                            </div>
                        </div>
                    </div>

                    <div class="p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
                        <div class="font-medium mb-2">Будет создано:</div>
                        <ul class="list-disc list-inside space-y-1">
                            <li>Общая задача для копирайтера (дедлайн: {{ aggregatedCopywriterDeadline }})</li>
                            <li v-if="isSingleAlbum">Общая задача для дизайнера (дедлайн: {{ aggregatedDesignerDeadline }})</li>
                        </ul>
                    </div>
                </div>

                <div class="grid grid-cols-2 gap-2 mt-2">
                    <app-button active @click="convertToAggregated">
                        Преобразовать
                    </app-button>
                    <app-button @click="convertToAggregatedModalOpen = false">
                        Отмена
                    </app-button>
                </div>
            </div>
        </template>
    </UModal>

    <UModal
        v-if="group && group.aggregate_task"
        v-model:open="removeAggregationModalOpen"
        title="Отмена агрегации"
        :ui="{ width: 'sm:max-w-2xl' }"
    >
        <template #body>
            <div class="flex flex-col gap-3">
                <div class="text-md">
                    Вы действительно хотите отменить агрегацию группы "{{ group.name }}"?
                </div>

                <div class="flex flex-col gap-2 text-sm">
                    <div class="p-3 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg border border-yellow-200 dark:border-yellow-800">
                        <div class="font-medium mb-2">Что произойдет:</div>
                        <ul class="list-disc list-inside space-y-1">
                            <li>Общая задача публикации будет удалена</li>
                            <li v-if="aggregateTaskUsers.length > 0">С задачи будут сняты следующие пользователи:</li>
                        </ul>
                        <div v-if="aggregateTaskUsers.length > 0" class="mt-2 ml-6 space-y-1">
                            <div v-for="user in aggregateTaskUsers" :key="user.userId">
                                <div class="font-medium text-xs">{{ user.userName }}</div>
                                <ul class="list-disc list-inside pl-4 text-xs text-gray-600">
                                    <li v-for="task in user.tasks" :key="task.id">
                                        {{ task.taskType }}
                                    </li>
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="grid grid-cols-2 gap-2 mt-2">
                    <app-button active red @click="removeAggregation">
                        Подтвердить
                    </app-button>
                    <app-button @click="removeAggregationModalOpen = false">
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
import { useAppSettingsStore } from "~/stores/app-settings";

const { group_id } = defineProps({
    group_id: {
        type: String,
        default: null,
    },
});

const appSettingsStore = useAppSettingsStore();
const deleteGroupModalOpen = ref(false);
const deleteGroupEvents = ref(false);
const convertToAggregatedModalOpen = ref(false);
const removeAggregationModalOpen = ref(false);
const isSingleAlbum = ref(false);
const aggregateTaskFull = ref(null);
watch(deleteGroupModalOpen, (newValue) => {
    if (!newValue) {
        deleteGroupEvents.value = false;
    }
});

watch(convertToAggregatedModalOpen, (newValue) => {
    if (!newValue) {
        isSingleAlbum.value = false;
    }
});

watch(removeAggregationModalOpen, async (newValue) => {
    if (newValue && group.value?.aggregate_task) {
        try {
            const { TasksService } = await import('~/client');
            aggregateTaskFull.value = await TasksService.getTaskByIdTasksTaskIdGet(group.value.aggregate_task.id);
        } catch (error) {
            console.error('Ошибка загрузки агрегированной задачи:', error);
        }
    } else {
        aggregateTaskFull.value = null;
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

// Computed для преобразования в агрегированную группу
const latestEventDate = computed(() => {
    if (!group.value || !group.value.events || group.value.events.length === 0) {
        return new Date();
    }
    const dates = group.value.events.map(e => new Date(e.date));
    return new Date(Math.max(...dates));
});

const aggregatedCopywriterDeadline = computed(() => {
    const deadline = new Date(latestEventDate.value);
    deadline.setDate(deadline.getDate() + appSettingsStore.settings.copywriters_deadline);
    return deadline.toLocaleDateString('ru-RU', { year: 'numeric', month: '2-digit', day: '2-digit' });
});

const aggregatedDesignerDeadline = computed(() => {
    const deadline = new Date(latestEventDate.value);
    deadline.setDate(deadline.getDate() +
        appSettingsStore.settings.photographers_deadline +
        appSettingsStore.settings.designers_deadline);
    return deadline.toLocaleDateString('ru-RU', { year: 'numeric', month: '2-digit', day: '2-digit' });
});

const affectedUsers = computed(() => {
    if (!group.value || !group.value.events) return [];

    const usersMap = new Map();

    group.value.events.forEach(event => {
        if (!event.task || !event.task.typed_tasks) return;

        event.task.typed_tasks.forEach(typedTask => {
            // Собираем копирайтеров всегда, дизайнеров только если isSingleAlbum
            const shouldInclude = typedTask.task_type === 'copywriter' ||
                                  (typedTask.task_type === 'designer' && isSingleAlbum.value);

            if (shouldInclude) {
                typedTask.task_states.forEach(state => {
                    if (state.state !== 'canceled') {
                        const userId = state.user.id;
                        const userName = `${state.user.first_name} ${state.user.last_name}`;

                        if (!usersMap.has(userId)) {
                            usersMap.set(userId, {
                                userId,
                                userName,
                                tasks: []
                            });
                        }

                        usersMap.get(userId).tasks.push({
                            id: typedTask.id,
                            eventName: event.name,
                            taskType: typedTask.task_type === 'copywriter' ? 'Копирайтер' : 'Дизайнер'
                        });
                    }
                });
            }
        });
    });

    return Array.from(usersMap.values());
});

const aggregateTaskUsers = computed(() => {
    if (!aggregateTaskFull.value || !aggregateTaskFull.value.typed_tasks) return [];

    const usersMap = new Map();

    aggregateTaskFull.value.typed_tasks.forEach(typedTask => {
        typedTask.task_states?.forEach(state => {
            if (state.state !== 'canceled') {
                const userId = state.user.id;
                const userName = `${state.user.first_name} ${state.user.last_name}`;

                if (!usersMap.has(userId)) {
                    usersMap.set(userId, {
                        userId,
                        userName,
                        tasks: []
                    });
                }

                usersMap.get(userId).tasks.push({
                    id: typedTask.id,
                    taskType: typedTask.task_type === 'copywriter' ? 'Копирайтер' : 'Дизайнер'
                });
            }
        });
    });

    return Array.from(usersMap.values());
});


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
                    aggregate_task_params: null,
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

const convertToAggregated = async () => {
    try {
        group.value = await EventsGroupsService.convertEventGroupToAggregatedEventsGroupsGroupIdConvertToAggregatedPost(
            group_id,
            isSingleAlbum.value
        );
        convertToAggregatedModalOpen.value = false;
        $toast.success('Группа успешно преобразована в группу с единой публикацией');
    } catch (error) {
        $toast.error(HandleOpenApiError(error).message);
    }
};

const removeAggregation = async () => {
    try {
        group.value = await EventsGroupsService.removeAggregationFromEventGroupEventsGroupsGroupIdRemoveAggregationPost(
            group_id
        );
        removeAggregationModalOpen.value = false;
        $toast.success('Агрегация успешно отменена');
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
