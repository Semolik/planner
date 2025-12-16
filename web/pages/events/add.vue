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
                        white
                    />
                    <app-input
                        v-model="timeEnd"
                        type="time"
                        label="Время окончания"
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
                            required
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

        <div class="flex flex-wrap gap-2">
            <!-- Чекбокс агрегированной публикации -->
            <UCheckbox
                v-model="useAggregatePublication"
                color="neutral"
                variant="card"
                label="Одна публикация на несколько мероприятий"
                class="flex-1"
            />

            <!-- Чекбокс учитывать в ПГАС -->
            <UCheckbox
                v-model="useInPgas"
                color="neutral"
                variant="card"
                label="Учитывать в ПГАС"
                class="flex-1"
            />
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-2 gap-2">
            <event-group-selector
                v-model="selectedGroup"
                v-model:open="selectGroupOpen"
                      :only-aggregated="useAggregatePublication"
                :required="useAggregatePublication"
                :event-date="date"
            />

            <div
                :class="['button', { active: tasksSettingsOpen }, {'pointer-events-none opacity-50': useAggregatePublication}]"
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
                    :class="{ 'opacity-50 pointer-events-none': useAggregatePublication }"
                >
                    <USwitch
                        v-model="createCopywritersSubTask"
                        label="Создать подзадачу для копирайтеров"
                        color="neutral"
                        :disabled="useAggregatePublication"
                    />
                    <app-input
                        v-if="createCopywritersSubTask"
                        v-model="copywriterDescription"
                        label="Описание для копирайтеров"
                        type="textarea"
                        white
                        rows="2"
                    />
                    <USwitch
                        v-model="createDesignersSubTask"
                        label="Создать подзадачу для дизайнеров"
                        color="neutral"
                        :disabled="useAggregatePublication"
                    />
                    <app-input
                        v-if="createDesignersSubTask"
                        v-model="designerDescription"
                        label="Описание для дизайнеров"
                        type="textarea"
                        white
                        rows="2"
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
                class="w-full"
                @click="createEvent"
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
await appSettingsStore.getSettings();
definePageMeta({
    middleware: ["admin"],
});

const tasksSettingsOpen = ref(false);
const selectGroupOpen = ref(false);
const useAggregatePublication = ref(false);
const useInPgas = ref(true);

const { $toast } = useNuxtApp();
const name = ref("");
const date = ref("");
const description = ref("");
const timeStart = ref("");
const timeEnd = ref("");
const currentDate = ref(new Date().toISOString().slice(0, 10));
const location = ref("");
const organizer = ref("");
const createCopywritersSubTask = ref(true);
const createDesignersSubTask = ref(false);
const copywriterDescription = ref("");
const designerDescription = ref("");
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
console.log("Event levels:", eventLevels);
const event_level = ref(
    eventLevels.find(
        (level) => level.id === appSettingsStore.settings.default_event_level_id
    )
);
console.log("Default event level:", event_level.value);

const selectedGroup = ref(null);

const buttonActive = computed(() => {
    const baseValidation =
        name.value.length > 0 &&
        date.value.length > 0 &&
        location.value.length > 0 &&
        event_level.value !== null;
    console.log("Base validation:", baseValidation);

    // Группа обязательна только при aggregate_task
    if (useAggregatePublication.value) {
        return baseValidation && selectedGroup.value !== null;
    }

    return baseValidation;
});

// Блокируем подзадачи при агрегированном режиме
watch(useAggregatePublication, (value) => {
    if (value) {
        tasksSettingsOpen.value = false; // Закрываем секцию настроек
        createCopywritersSubTask.value = false;
        createDesignersSubTask.value = false;
    }
    selectedGroup.value = null; // Сбрасываем группу при изменении режима
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

    // Создаем группу если она новая (только для агрегированного режима)
    if (selectedGroup.value && !selectedGroup.value.id) {
        try {
            selectedGroup.value = await EventsGroupsService.createEventGroupEventsGroupsPost({
                name: selectedGroup.value.name,
                description: selectedGroup.value.description,
                organizer: selectedGroup.value.organizer,
                link: "",
                aggregate_task_params: selectedGroup.value.aggregate_task_params || null,
            });
        } catch (error) {
            $toast.error("Ошибка создания группы: " + HandleOpenApiError(error).message);
            return;
        }
    }

    try {
        const event = await EventsService.createEventEventsPost({
            name: name.value,
            date: date.value,
            start_time: timeStart.value ? `${timeStart.value}:00Z` : null,
            end_time: timeEnd.value ? `${timeEnd.value}:00Z` : null,
            name_approved: false,
            location: location.value,
            link: "",
            organizer: organizer.value,
            required_photographers: 1,
            group_id: selectedGroup.value ? selectedGroup.value.id : null,
            description: description.value,
            level_id: event_level.value.id,
            photographer_description: "",
            copywriter_description: createCopywritersSubTask.value ? copywriterDescription.value : "",
            designer_description: createDesignersSubTask.value ? designerDescription.value : "",
            photographers_deadline: addDaysToDate(
                date.value,
                appSettingsStore.settings.photographers_deadline
            ),
            copywriters_deadline: useAggregatePublication.value ? null :
                createCopywritersSubTask.value ?
                addDaysToDate(date.value, appSettingsStore.settings.copywriters_deadline) : null,
            designers_deadline: useAggregatePublication.value ?
                // Если в группе создается задача для дизайнеров - не отправляем дедлайн
                (selectedGroup.value?.aggregate_task_params?.designers_deadline ? null :
                // Если в группе НЕ создается задача для дизайнеров - отправляем дедлайн
                (createDesignersSubTask.value ?
                addDaysToDate(date.value,
                    appSettingsStore.settings.photographers_deadline +
                    appSettingsStore.settings.designers_deadline
                ) : null))
                :
                // Для обычных мероприятий
                (createDesignersSubTask.value ?
                addDaysToDate(date.value,
                    appSettingsStore.settings.photographers_deadline +
                    appSettingsStore.settings.designers_deadline
                ) : null),
            aggregate_task: useAggregatePublication.value,
            use_in_pgas: useInPgas.value,
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
    transition: all 0.2s ease;

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

.hide-if-child-empty:has(> :empty) {
    display: none;
}
</style>
