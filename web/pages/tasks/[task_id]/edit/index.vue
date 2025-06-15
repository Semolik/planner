<template>
    <div class="flex flex-col gap-2 w-full">
        <div class="flex gap-1">
            <app-input
                v-model="name"
                :label="`Название ${task.event ? 'мероприятия' : 'задачи'}`"
                required
                white
            />
        </div>

        <template v-if="task.event">
            <UCheckbox
                v-model="nameApproved"
                color="neutral"
                label="Название утверждено"
                class="ml-1"
            />
            <div class="flex gap-1">
                <app-input
                    v-model="location"
                    label="Место проведения"
                    required
                    white
                /><app-input
                    v-model="organizer"
                    label="Контакт организатора"
                    required
                    white
                />
            </div>

            <div class="flex gap-1">
                <app-input
                    v-model="date"
                    type="date"
                    label="Дата мероприятия"
                    required
                    white
                />
                <app-input
                    v-model="timeStart"
                    type="time"
                    label="Время начала"
                    required
                    white
                />
                <app-input
                    v-model="timeEnd"
                    type="time"
                    label="Время окончания"
                    required
                    white
                />
            </div>
            <app-input
                v-model="description"
                label="Описание мероприятия"
                type="textarea"
                white
                rows="3"
                class="max-h-[150px]"
            />
            <div class="flex gap-1">
                <div class="flex gap-1 w-full">
                    <app-input
                        v-model="link"
                        label="Ссылка на публикацию"
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
                <app-input
                    v-model="required_photographers"
                    type="number"
                    label="Требуемое количество фотографов"
                    required
                    white
                    min="1"
                />
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-2">
                <div class="flex flex-col">
                    <div class="event-form-label">Уровень мероприятия</div>
                    <client-only>
                        <USelectMenu
                            v-model="event_level"
                            :items="eventLevels"
                            class="select-menu"
                            color="neutral"
                            size="lg"
                            :content="{
                                align: 'start',
                                side: 'bottom',
                                sideOffset: 8,
                            }"
                            :search-input="{
                                placeholder: 'Поиск',
                            }"
                        />
                    </client-only>
                </div>
                <event-group-selector
                    v-model="selectedGroup"
                    v-model:open="selectGroupOpen"
                    class="h-min mt-auto"
                />
            </div>
        </template>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-2 mt-auto">
            <app-button red active @click="deleteTaskModalOpen = true">
                Удалить
            </app-button>
            <app-button :active="saveButtonActive" @click="updateTask">
                Сохранить
            </app-button>
        </div>
    </div>
    <UModal
        v-model:open="deleteTaskModalOpen"
        :title="`Удалить ${task.event ? 'мероприятие' : 'задачу'}`"
    >
        <template #body>
            <div class="text-md">
                Вы действительно хотите удалить
                {{ task.event ? "мероприятие" : "задачу" }} "{{
                    task.event ? task.event.name : task.name
                }}"?
            </div>
            <div class="grid grid-cols-2 gap-2 mt-4">
                <app-button active red @click="deleteTask">
                    Подтвердить
                </app-button>
                <app-button
                    @click="deleteTaskModalOpen = false"
                    class="cursor-pointer"
                >
                    Отмена
                </app-button>
            </div>
        </template>
    </UModal>
</template>
<script setup>
import { useAppSettingsStore } from "~/stores/app-settings";
import { TasksService, EventsService, EventsGroupsService } from "~/client";
import { routesNames } from "@typed-router";
const appSettingsStore = useAppSettingsStore();
definePageMeta({
    middleware: ["admin"],
});
const { task_id } = useRoute().params;
const task = ref(await TasksService.getTaskByIdTasksTaskIdGet(task_id));
const selectGroupOpen = ref(false);
const selectedGroup = ref(task.value.event ? task.value.event.group : null);

const currentDate = ref(new Date().toISOString().slice(0, 10));

const name = ref(task.value.event ? task.value.event.name : task.value.name);
const date = ref(task.value.event ? task.value.event.date : "");
const description = ref(task.value.event ? task.value.event.description : "");
const timeStart = ref(task.value.event ? task.value.event.start_time : "");
const timeEnd = ref(task.value.event ? task.value.event.end_time : "");
const required_photographers = ref(
    task.value.event ? task.value.event.required_photographers : 0
);
const deleteTaskModalOpen = ref(false);
const location = ref(task.value.event ? task.value.event.location : "");
const organizer = ref(task.value.event ? task.value.event.organizer : "");
const nameApproved = ref(
    task.value.event ? task.value.event.name_approved : false
);
const link = ref(task.value.event ? task.value.event.link : "");
const eventLevels = appSettingsStore.eventsLevels.map((level) => ({
    id: level.id,
    label: level.name,
}));
const event_level = ref(
    task.value.event
        ? eventLevels.find((l) => l.id === task.value.event.level_id)
        : null
);
const linkIsValid = computed(() => {
    if (!link.value) return true;
    return validateUrl(link.value);
});
const saveButtonActive = computed(() => {
    if (task.value.event) {
        if (
            required_photographers.value < 1 ||
            name.value.trim() === "" ||
            !linkIsValid.value ||
            !timeStart.value ||
            !timeEnd.value ||
            !date.value ||
            !location.value
        ) {
            return false;
        }
        return (
            date.value !== task.value.event.date ||
            description.value !== task.value.event.description ||
            name.value !== task.value.event.name ||
            timeStart.value !== task.value.event.start_time ||
            timeEnd.value !== task.value.event.end_time ||
            required_photographers.value !==
                task.value.event.required_photographers ||
            location.value !== task.value.event.location ||
            organizer.value !== task.value.event.organizer ||
            nameApproved.value !== task.value.event.name_approved ||
            link.value !== task.value.event.link ||
            event_level.value?.id !== task.value.event.level_id ||
            (selectedGroup.value
                ? selectedGroup.value.id == null
                    ? true
                    : selectedGroup.value.id !== task.value.event.group_id
                : task.value.event.group_id != null)
        );
    } else {
        return name.value !== task.value.name;
    }
});
const emit = defineEmits(["update:task"]);
watch(timeStart, (value) => {
    if (
        new Date(`${currentDate.value}T${value}`) >=
        new Date(`${currentDate.value}T${timeEnd.value}`)
    ) {
        const endTime = new Date(`${currentDate.value}T${value}`);
        if (endTime.getHours() < 23) {
            endTime.setHours(endTime.getHours() + 1);
        } else {
            if (endTime.getMinutes() < 59) {
                endTime.setMinutes(endTime.getMinutes() + 1);
            } else {
                endTime.setHours(0);
                endTime.setMinutes(0);
            }
        }
        timeEnd.value = endTime.toTimeString().slice(0, 5);
    }
});
watch(timeEnd, (value) => {
    if (
        new Date(`${currentDate.value}T${value}`) <=
        new Date(`${currentDate.value}T${timeStart.value}`)
    ) {
        const startTime = new Date(`${currentDate.value}T${value}`);
        if (startTime.getHours() > 0) {
            startTime.setHours(startTime.getHours() - 1);
        } else {
            if (startTime.getMinutes() > 0) {
                startTime.setMinutes(startTime.getMinutes() - 1);
            } else {
                startTime.setHours(23);
                startTime.setMinutes(59);
            }
        }
        timeStart.value = startTime.toTimeString().slice(0, 5);
    }
});
const { $toast } = useNuxtApp();
const updateTask = async () => {
    try {
        if (!saveButtonActive.value) return;
        if (task.value.event) {
            if (selectedGroup.value && selectedGroup.value.id === null) {
                selectedGroup.value =
                    await EventsGroupsService.createEventGroupEventsGroupsPost({
                        ...selectedGroup.value,
                    });
            }
            const updatedEvent = {
                id: task.value.event.id,
                name: name.value,
                date: date.value,
                description: description.value,
                start_time: timeStart.value,
                end_time: timeEnd.value,
                required_photographers: required_photographers.value,
                location: location.value,
                organizer: organizer.value,
                name_approved: nameApproved.value,
                link: link.value,
                level_id: event_level.value?.id || null,
                group_id: selectedGroup.value?.id || null,
            };
            task.value.event = await EventsService.updateEventEventsEventIdPut(
                task.value.event.id,
                updatedEvent
            );
            timeStart.value = task.value.event.start_time;
            timeEnd.value = task.value.event.end_time;
            emit("update:task", task.value);
        }
    } catch (error) {
        $toast.error(HandleOpenApiError(error).message);
    }
};
const deleteTask = async () => {
    try {
        await TasksService.deleteTaskTasksTaskIdDelete(task_id);
        useRouter().push({ name: routesNames.tasks });
    } catch (error) {
        $toast.error(HandleOpenApiError(error).message);
    }
};
</script>
<style lang="scss">
.select-menu {
    --ui-border-accented: transparent !important;
}
</style>
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
