<template>
    <div class="flex gap-1 text-center" v-bind="$attrs">
        <div
            :class="[
                'button group-select',
                {
                    'border-error animate-pulse': required && !modelValue,
                    'border-success': modelValue && modelValue.id
                }
            ]"
            @click="openModal"
        >
            {{
                modelValue
                    ? (modelValue.id ? `Группа: ${modelValue.name}` : `Новая группа: ${modelValue.name}`)
                    : aggregateMode ? "Обязательно: выберите группу *" : "Добавить в группу"
            }}
        </div>
        <app-button
            active
            :to="{
                name: routesNames.eventsGroupsGroupIdEdit,
                params: { group_id: modelValue.id },
            }"
            target="_blank"
            v-if="modelValue && modelValue.id"
            class="aspect-square"
        >
            <div class="flex items-center justify-center">
                <Icon name="material-symbols:edit" />
            </div>
        </app-button>
        <app-button
            red
            active
            class="aspect-square"
            @click="clearSelection"
            v-if="modelValue"
        >
            <div class="flex items-center justify-center">
                <Icon name="material-symbols:delete" />
            </div>
        </app-button>
    </div>

    <!-- Модалка выбора группы -->
    <UModal
        v-model:open="modalOpen"
        :title="aggregateMode ? 'Выбрать группу с агрегированной задачей' : 'Выбрать группу мероприятий'"
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
                <div class="groups-list overflow-y-auto" v-auto-animate>
                    <div
                        :class="[
                            'group',
                            { selected: modelValue?.id === group.id },
                        ]"
                        v-for="group in searchGroupsResult"
                        :key="group.id"
                        @click="selectGroup(group)"
                    >
                        {{ group.name }}
                    </div>
                    <div class="empty" v-if="searchGroupsResult.length === 0">
                        {{ aggregateMode ? 'Группы с агрегированной задачей не найдены' : 'Группы не найдены' }}
                    </div>
                </div>
                <app-button active @click="openCreateGroup">
                    Создать группу
                </app-button>
            </div>
        </template>
    </UModal>

    <!-- Модалка для создания новой группы -->
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

                <!-- Параметры агрегированной задачи -->
                <div v-if="aggregateMode" class="flex flex-col gap-2 p-2 border border-solid rounded-[10px] bg-gray-50">
                    <div class="font-medium text-sm text-gray-800">Параметры агрегированной публикации</div>

                    <app-input
                        v-model="aggregateCopywriterDescription"
                        label="Описание задачи для копирайтера"
                        type="textarea"
                        rows="2"
                        border-radius="10px"
                    />



                    <div class="flex flex-col gap-1">
                        <app-input
                            v-model="aggregateCopywritersDeadline"
                            type="date"
                            label="Дедлайн для копирайтера"
                            border-radius="10px"
                        />
                        <div class="text-xs text-gray-600">
                            {{ getCopywriterDeadlineHint() }}
                        </div>
                    </div>

                    <USwitch
                        label="Создать задачу для дизайнера"
                        v-model="createAggregateDesignerTask"
                        color="neutral"
                    />

                    <div v-if="createAggregateDesignerTask" class="flex flex-col gap-1">
                        <app-input
                            v-model="aggregateDesignersDeadline"
                            type="date"
                            label="Дедлайн для дизайнера"
                            border-radius="10px"
                        />
                        <div class="text-xs text-gray-600">
                            {{ getDesignerDeadlineHint() }}
                        </div>
                    </div>  <app-input
                        v-model="aggregateDesignerDescription"
                        v-if="createAggregateDesignerTask"
                        label="Описание задачи для дизайнера"
                        type="textarea"
                        rows="2"
                        border-radius="10px"
                    />
                </div>

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
import { routesNames } from "@typed-router";
import { EventsGroupsService } from "~/client";
import { useAppSettingsStore } from "~/stores/app-settings";

const appConfig = useAppConfig();
const modalUi = appConfig.ui;
const contentClass =
    modalUi.modal.variants.fullscreen.false.content + " h-full !max-h-[500px]";

const props = defineProps({
    modelValue: {
        type: Object,
        default: null,
    },
    open: {
        type: Boolean,
        default: false,
    },
    aggregateMode: {
        type: Boolean,
        default: false,
    },
    required: {
        type: Boolean,
        default: false,
    },
    eventDate: {
        type: String,
        default: null,
    },
});

const emit = defineEmits(["update:open", "update:modelValue"]);

const modalOpen = computed({
    get: () => props.open,
    set: (value) => emit("update:open", value),
});

const createGroupOpen = ref(false);

// Поиск группы
const searchGroup = ref("");
const searchGroupsResult = ref([]);

// Данные для создания новой группы
const createGroupName = ref("");
const createGroupDescription = ref("");
const createGroupOrganizer = ref("");

// Параметры агрегированной задачи
const aggregateCopywriterDescription = ref("");
const aggregateDesignerDescription = ref("");
const aggregateCopywritersDeadline = ref("");
const aggregateDesignersDeadline = ref("");
const createAggregateDesignerTask = ref(false);

const createGroupButtonActive = computed(() => {
    return createGroupName.value.length > 0;
});

const saveGroupCreation = () => {
    if (!createGroupButtonActive.value) return;

    const newGroup = {
        id: null,
        name: createGroupName.value,
        description: createGroupDescription.value,
        organizer: createGroupOrganizer.value,
        link: "",
    };

    // Добавляем параметры агрегированной задачи если режим включен
    if (props.aggregateMode) {
        const appSettingsStore = useAppSettingsStore();
        const baseDate = props.eventDate ? new Date(props.eventDate) : new Date();

        // Если дедлайн копирайтеров не задан - вычисляем автоматически
        let copywritersDeadline = aggregateCopywritersDeadline.value;
        if (!copywritersDeadline) {
            const copywritersDate = new Date(baseDate);
            copywritersDate.setDate(copywritersDate.getDate() + appSettingsStore.settings.copywriters_deadline);
            copywritersDeadline = copywritersDate.toISOString().split('T')[0];
        }

        // Если дедлайн дизайнеров не задан - вычисляем автоматически
        let designersDeadline = aggregateDesignersDeadline.value;
        if (!designersDeadline && createAggregateDesignerTask.value) {
            const designersDate = new Date(baseDate);
            designersDate.setDate(designersDate.getDate() +
                appSettingsStore.settings.photographers_deadline +
                appSettingsStore.settings.designers_deadline);
            designersDeadline = designersDate.toISOString().split('T')[0];
        }

        newGroup.aggregate_task_params = {
            copywriter_description: aggregateCopywriterDescription.value,
            designer_description: aggregateDesignerDescription.value,
            copywriters_deadline: copywritersDeadline,
            designers_deadline: createAggregateDesignerTask.value ? designersDeadline : null,
        };
    }

    emit("update:modelValue", newGroup);
    createGroupOpen.value = false;
    modalOpen.value = false;
};

const resetCreation = () => {
    createGroupName.value = "";
    createGroupDescription.value = "";
    createGroupOrganizer.value = "";
    aggregateCopywriterDescription.value = "";
    aggregateDesignerDescription.value = "";
    aggregateCopywritersDeadline.value = "";
    aggregateDesignersDeadline.value = "";
    createAggregateDesignerTask.value = false;
};

// Загрузка результатов поиска с учетом режима агрегации
watch(
    [searchGroup, () => props.aggregateMode],
    async ([value, aggregateMode]) => {
        try {
            searchGroupsResult.value =
                await EventsGroupsService.searchEventGroupsEventsGroupsSearchGet(
                    value || undefined,
                    1,
                    'all',
                    aggregateMode
                );
        } catch (error) {
            console.error("Failed to fetch event groups:", error);
            searchGroupsResult.value = [];
        }
    },
    { immediate: true }
);

watch(modalOpen, (isOpen) => {
    if (!isOpen) {
        searchGroup.value = "";
    }
});

// Автоматически устанавливаем дедлайн дизайнеров при включении переключателя
watch(createAggregateDesignerTask, (isEnabled) => {
    if (isEnabled && props.aggregateMode) {
        const appSettingsStore = useAppSettingsStore();
        const baseDate = props.eventDate ? new Date(props.eventDate) : new Date();
        const designersDate = new Date(baseDate);
        designersDate.setDate(designersDate.getDate() +
            appSettingsStore.settings.photographers_deadline +
            appSettingsStore.settings.designers_deadline);
        aggregateDesignersDeadline.value = designersDate.toISOString().split('T')[0];
    }
});

// Выбор существующей группы
const selectGroup = (group) => {
    emit("update:modelValue", group);
    modalOpen.value = false;
};

// Очистка выбора
const clearSelection = () => {
    emit("update:modelValue", null);
    resetCreation();
};

// Функция для склонения слов
const pluralize = (count, one, two, five) => {
    count = Math.abs(count) % 100;
    const n1 = count % 10;
    if (count > 10 && count < 20) return five;
    if (n1 > 1 && n1 < 5) return two;
    if (n1 === 1) return one;
    return five;
};

// Функции для получения подсказок
const getCopywriterDeadlineHint = () => {
    const appSettingsStore = useAppSettingsStore();
    const days = appSettingsStore.settings.copywriters_deadline;

    if (props.eventDate) {
        return `Обычно ставится через ${days} ${pluralize(days, 'день', 'дня', 'дней')} после даты мероприятия. Если не указано, будет установлено автоматически.`;
    }
    return `Обычно ставится через ${days} ${pluralize(days, 'день', 'дня', 'дней')} после даты мероприятия. Если не указано, будет установлено от текущей даты.`;
};

const getDesignerDeadlineHint = () => {
    const appSettingsStore = useAppSettingsStore();
    const days = appSettingsStore.settings.photographers_deadline + appSettingsStore.settings.designers_deadline;

    if (props.eventDate) {
        return `Обычно ставится через ${days} ${pluralize(days, 'день', 'дня', 'дней')} после даты мероприятия. Если не указано, будет установлено автоматически.`;
    }
    return `Обычно ставится через ${days} ${pluralize(days, 'день', 'дня', 'дней')} после даты мероприятия. Если не указано, будет установлено от текущей даты.`;
};

// Открытие модалки создания группы
const openCreateGroup = () => {
    resetCreation();

    // Устанавливаем дефолтные дедлайны на основе настроек и даты мероприятия
    if (props.aggregateMode && props.eventDate) {
        const appSettingsStore = useAppSettingsStore();
        const eventDate = new Date(props.eventDate);

        // Дедлайн для копирайтеров
        const copywritersDate = new Date(eventDate);
        copywritersDate.setDate(copywritersDate.getDate() + appSettingsStore.settings.copywriters_deadline);
        aggregateCopywritersDeadline.value = copywritersDate.toISOString().split('T')[0];

        // Дедлайн для дизайнеров (если включен)
        if (createAggregateDesignerTask.value) {
            const designersDate = new Date(eventDate);
            designersDate.setDate(designersDate.getDate() +
                appSettingsStore.settings.photographers_deadline +
                appSettingsStore.settings.designers_deadline);
            aggregateDesignersDeadline.value = designersDate.toISOString().split('T')[0];
        }
    }

    createGroupOpen.value = true;
};

// Открытие основной модалки
const openModal = () => {
    modalOpen.value = true;
};
</script>

<style lang="scss" scoped>
.button {
    background-color: black;
    color: white;
    padding: 10px;
    border-radius: 10px;
    font-size: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    user-select: none;
    flex-grow: 1;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    transition: all 0.2s ease;
    border: 2px solid transparent;

    &.border-error {
        border-color: #ef4444 !important;
        animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
    }

    &.border-success {
        border-color: #10b981;
    }
}

.aspect-square {
    height: 100%;
    padding: 0 !important;
    aspect-ratio: 1;
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

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: .5; }
}
</style>
