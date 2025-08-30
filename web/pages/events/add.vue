<template>
    <app-form full-height headline="Создание мероприятия" max-width="900px">
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-2">
            <div class="flex flex-col gap-2 w-full">
                <app-input
                    v-model="name"
                    label="Название мероприятия"
                    required
                    white
                />
                <app-input
                    v-model="date"
                    type="date"
                    label="Дата мероприятия"
                    required
                    white
                />
                <div class="flex gap-1">
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
                    v-model="location"
                    label="Место проведения"
                    required
                    white
                />
            </div>
            <div class="flex flex-col">
                <app-input
                    v-model="description"
                    label="Описание мероприятия"
                    type="textarea"
                    white
                    rows="3"
                    class="max-h-[150px]"
                />
                <div class="flex flex-col gap-1 w-full">
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
                    <app-input
                        v-model="organizer"
                        label="Контакт организатора"
                        required
                        white
                    />
                </div>
            </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-2 gap-2">
            <event-group-selector
                v-model="selectedGroup"
                v-model:open="selectGroupOpen"
            />

            <div
                :class="['button', { active: tasksSettingsOpen }]"
                @click="tasksSettingsOpen = !tasksSettingsOpen"
            >
                <span class="text"> Настройки подзадач </span>
                <Icon name="i-lucide-chevron-down" />
            </div>
        </div>
        <UCollapsible
            v-model:open="tasksSettingsOpen"
            class="flex flex-col gap-[10px] hide-if-child-empty"
        >
            <template #content>
                <div
                    class="flex flex-col gap-[10px] p-2 border border-solid rounded-[10px]"
                >
                    <USwitch
                        label="Создать подзадачу для фотографов"
                        v-model="createPhotographersSubTask"
                        color="neutral"
                    />
                    <USwitch
                        label="Создать подзадачу для копирайтеров"
                        v-model="createCopywritersSubTask"
                        color="neutral"
                    />
                    <USwitch
                        label="Создать подзадачу для дизайнеров"
                        v-model="createDesignersSubTask"
                        color="neutral"
                    />
                </div>
            </template>
        </UCollapsible>

        <div class="flex gap-2">
            <UDropdownMenu
                :items="items"
                :content="{
                    align: 'start',
                    side: 'top',
                    sideOffset: 8,
                }"
            >
                <app-button active>
                    <Icon name="material-symbols:attach-file" />
                </app-button>
                <template #item="{ item }">
                    <app-button active class="!rounded-sm">
                        <div class="flex items-center gap-1">
                            <Icon :name="item.icon" />
                            {{ item.label }}
                        </div>
                    </app-button>
                </template>
            </UDropdownMenu>

            <app-button
                :active="buttonActive"
                @click="createEvent"
                class="w-full"
            >
                Создать мероприятие
            </app-button>
        </div>
    </app-form>
</template>
<script setup>
import { useAppSettingsStore } from "~/stores/app-settings";
import { EventsService, EventsGroupsService } from "~/client";
import { routesNames } from "@typed-router";
const appSettingsStore = useAppSettingsStore();
definePageMeta({
    middleware: ["admin"],
});

const tasksSettingsOpen = ref(false);
const selectGroupOpen = ref(false);

const { $toast } = useNuxtApp();
const name = ref("");
const date = ref("");
const description = ref("");
const timeStart = ref("");
const timeEnd = ref("");
const currentDate = ref(new Date().toISOString().slice(0, 10));
const location = ref("");
const organizer = ref("");
const createPhotographersSubTask = ref(true);
const createCopywritersSubTask = ref(true);
const createDesignersSubTask = ref(true);
const items = ref([
    [
        {
            label: "Изображения",
            icon: "material-symbols:photo",
        },
        {
            label: "Документы",
            icon: "material-symbols:description",
        },
    ],
]);
const eventLevels = appSettingsStore.eventsLevels.map((level) => ({
    id: level.id,
    label: level.name,
}));
const event_level = ref(
    eventLevels.find(
        (level) => level.id === appSettingsStore.settings.default_event_level_id
    )
);

const selectedGroup = ref(null);
const buttonActive = computed(() => {
    return (
        name.value.length > 0 &&
        date.value.length > 0 &&
        timeStart.value.length > 0 &&
        timeEnd.value.length > 0 &&
        location.value.length > 0 &&
        event_level.value !== null
    );
});
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

const createEvent = async () => {
    if (!buttonActive.value) return;
    if (selectedGroup.value && !selectedGroup.value.id) {
        searchGroup.value =
            await EventsGroupsService.createEventGroupEventsGroupsPost({
                name: selectedGroup.value.name,
                description: selectedGroup.value.description,
                organizer: selectedGroup.value.organizer,
                link: "",
            });
    }
    try {
        const event = await EventsService.createEventEventsPost({
            name: name.value,
            date: date.value,
            start_time: `${timeStart.value}:00Z`,
            end_time: `${timeEnd.value}:00Z`,
            name_approved: false,
            location: location.value,
            link: "",
            organizer: organizer.value,
            required_photographers: 1,
            group_id: selectedGroup.value ? selectedGroup.value.id : null,
            description: description.value,
            level_id: event_level.value.id,
            photographer_description: "",
            copywriter_description: "",
            designer_description: "",
            photographers_deadline: createPhotographersSubTask.value
                ? addDaysToDate(
                      date.value,
                      appSettingsStore.settings.photographers_deadline
                  )
                : null,
            copywriters_deadline: createCopywritersSubTask.value
                ? addDaysToDate(
                      date.value,
                      appSettingsStore.settings.copywriters_deadline
                  )
                : null,
            designers_deadline: createDesignersSubTask.value
                ? addDaysToDate(
                      date.value,
                      appSettingsStore.settings.photographers_deadline +
                          appSettingsStore.settings.designers_deadline
                  )
                : null,
        });
        const router = useRouter();
        $toast.success("Мероприятие успешно создано");
        router.push({
            name: routesNames.tasksTaskId,
            params: { task_id: event.task.id },
        });
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
.button {
    background-color: black;
    color: white;
    padding: 10px;
    border-radius: 10px;
    font-size: 14px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 10px;
    cursor: pointer;
    user-select: none;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    position: relative;

    &.active .iconify {
        transform: rotate(-180deg);
    }
    &.group-select {
        justify-content: center;
        text-align: center;
        flex-grow: 1;
    }
    &:not(.group-select) {
        height: 40px;
        .text {
            position: absolute;
            left: 50%;
            transform: translateX(-50%);
            font-weight: 500;
        }
        .iconify {
            position: absolute;
            right: 32px;
        }
    }
}
.groups-list {
    display: flex;
    flex-direction: column;
    gap: 10px;
    max-height: 500px;
    height: 100%;

    .group {
        border: 1px solid $text-color-tertiary;
        border-radius: 10px;
        padding: 10px;
        cursor: pointer;
        user-select: none;

        &:hover {
            background-color: $tertiary-bg;
        }

        &.selected {
            background-color: black;
            color: white;
        }
    }
    .empty {
        text-align: center;
        color: $text-color-secondary;
        font-size: 14px;
        display: flex;
        align-items: center;
        justify-content: center;
        height: 100%;
    }
}
.hide-if-child-empty:has(> :empty) {
    display: none;
}
</style>
