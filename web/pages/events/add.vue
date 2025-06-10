<template>
    <app-form full-height headline="Создание мероприятия">
        <app-input v-model="name" label="Название мероприятия" required white />
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
        <app-input v-model="location" label="Место проведения" required white />
        <app-input
            v-model="organizer"
            label="Контакт организатора"
            required
            white
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
        </div>
        <div class="flex gap-1 text-center">
            <div
                class="button group-select"
                @click="
                    () => {
                        if (selectedGroup && !searchGroup.id) {
                            createGroupOpen = true;
                        } else {
                            selectGroupOpen = true;
                        }
                    }
                "
            >
                {{
                    selectedGroup
                        ? (selectedGroup.id ? `Группа` : `Новая группа`) +
                          ": " +
                          selectedGroup.name
                        : "Добавить в группу"
                }}
            </div>
            <app-button
                red
                active
                @click="
                    () => {
                        selectedGroup = null;
                        resetCreation();
                    }
                "
                v-if="selectedGroup"
            >
                <div class="flex items-center justify-center">
                    <Icon name="material-symbols:delete" />
                </div>
            </app-button>
        </div>
        <UCollapsible
            v-model:open="tasksSettingsOpen"
            class="flex flex-col gap-[10px]"
        >
            <div :class="['button', { active: tasksSettingsOpen }]">
                <span class="text"> Настройки подзадач </span>
                <Icon name="i-lucide-chevron-down" />
            </div>
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
        <app-button :active="buttonActive" @click="createEvent">
            Создать мероприятие
        </app-button>
    </app-form>
    <UModal
        v-model:open="selectGroupOpen"
        title="Выбор группы мероприятий"
        :ui="{
            content: contentClass,
            body: 'flex-1 overflow-y-auto p-3 sm:p-3',
        }"
    >
        <template #body>
            <div class="flex flex-col gap-2 h-full">
                <app-input
                    v-model="searchGroup"
                    placeholder="Введите название группы"
                    border-radius="10px"
                />
                <div class="groups-list" v-auto-animate>
                    <div
                        :class="[
                            'group',
                            { selected: selectedGroup?.id === group.id },
                        ]"
                        v-for="group in searchGroupsResult"
                        :key="group.id"
                        @click="
                            selectedGroup = group;
                            selectGroupOpen = false;
                        "
                    >
                        {{ group.name }}
                    </div>
                    <div class="empty" v-if="searchGroupsResult.length === 0">
                        Группы не найдены
                    </div>
                </div>

                <app-button active @click="createGroupOpen = true">
                    Создать группу
                </app-button>
            </div>
        </template>
    </UModal>
    <UModal
        v-model:open="createGroupOpen"
        title="Создание группы мероприятий"
        :ui="{
            content: contentClass,
            body: 'flex-1 overflow-y-auto p-3 sm:p-3',
        }"
    >
        <template #body>
            <form
                class="flex flex-col gap-2 h-full"
                @submit.prevent="saveGroupCreation"
            >
                <app-input
                    v-model="createGroupName"
                    label="Название группы"
                    required
                    border-radius="10px"
                />
                <app-input
                    v-model="createGroupDescription"
                    label="Описание группы"
                    type="textarea"
                    border-radius="10px"
                />
                <app-input
                    v-model="createGroupOrganizer"
                    label="Контакт организатора группы"
                    border-radius="10px"
                />
                <app-button
                    :active="createGroupButtonActive"
                    type="submit"
                    class="mt-auto"
                >
                    Создать группу
                </app-button>
            </form>
        </template>
    </UModal>
</template>
<script setup>
import "vue-virtual-scroller/dist/vue-virtual-scroller.css";
import { useAppSettingsStore } from "~/stores/app-settings";
import { EventsService, EventsGroupsService } from "~/client";
import { routesNames } from "@typed-router";
const appSettingsStore = useAppSettingsStore();
definePageMeta({
    middleware: ["admin"],
});
const appConfig = useAppConfig();
const modalUi = appConfig.ui;
const contentClass =
    modalUi.modal.variants.fullscreen.false.content + " h-full !max-h-[500px]";
const tasksSettingsOpen = ref(false);
const selectGroupOpen = ref(false);
const searchGroup = ref("");
const searchGroupsResult = ref([]);

const name = ref("");
const date = ref("");
const timeStart = ref("");
const timeEnd = ref("");
const currentDate = ref(new Date().toISOString().slice(0, 10));
const location = ref("");
const organizer = ref("");
const createPhotographersSubTask = ref(true);
const createCopywritersSubTask = ref(true);
const createDesignersSubTask = ref(true);

const createGroupOpen = ref(false);
const createGroupName = ref("");
const createGroupDescription = ref("");
const createGroupOrganizer = ref("");

const createGroupButtonActive = computed(
    () => createGroupName.value.length > 0
);
const saveGroupCreation = () => {
    if (!createGroupButtonActive.value) return;
    selectedGroup.value = {
        id: null,
        name: createGroupName.value,
        description: createGroupDescription.value,
        organizer: createGroupOrganizer.value,
        link: "",
    };
    createGroupOpen.value = false;
    selectGroupOpen.value = false;
};
const resetCreation = () => {
    createGroupName.value = "";
    createGroupDescription.value = "";
    createGroupOrganizer.value = "";
};
const eventLevels = appSettingsStore.eventsLevels.map((level) => ({
    id: level.id,
    label: level.name,
}));
const event_level = ref(
    eventLevels.find(
        (level) => level.id === appSettingsStore.settings.default_event_level_id
    )
);
watch(
    searchGroup,
    async (value) => {
        try {
            searchGroupsResult.value =
                await EventsGroupsService.searchEventGroupsEventsGroupsSearchGet(
                    value
                );
        } catch (error) {
            console.error("Failed to fetch event groups:", error);
        }
    },
    { immediate: true }
);
watch(selectGroupOpen, () => {
    searchGroup.value = "";
});
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
            endTime.setHours(0);
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
            startTime.setHours(23);
        }
        timeStart.value = startTime.toTimeString().slice(0, 5);
    }
});
const getDeadlineDateString = (days) => {
    const deadlineDate = new Date(date.value);
    deadlineDate.setDate(deadlineDate.getDate() + days);
    return deadlineDate.toISOString().split("T")[0];
};
const { $toast } = useNuxtApp();

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
            description: "",
            level_id: event_level.value.id,
            photographer_description: "",
            copywriter_description: "",
            designer_description: "",
            photographers_deadline: createPhotographersSubTask.value
                ? getDeadlineDateString(
                      appSettingsStore.settings.photographers_deadline
                  )
                : null,
            copywriters_deadline: createCopywritersSubTask.value
                ? getDeadlineDateString(
                      appSettingsStore.settings.copywriters_deadline
                  )
                : null,
            designers_deadline: createDesignersSubTask.value
                ? getDeadlineDateString(
                      appSettingsStore.settings.designers_deadline
                  )
                : null,
        });
        const router = useRouter();
        $toast.success("Мероприятие успешно создано");
        router.push({
            name: routesNames.eventsEventId,
            params: { event_id: event.id },
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
.event-form-label {
    font-size: 14px;
    color: $text-color;
    text-decoration: none;
    margin-left: 3px;
}
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
</style>
