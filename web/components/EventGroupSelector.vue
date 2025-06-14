<template>
    <div class="flex gap-1 text-center" v-bind="$attrs">
        <div class="button group-select" @click="openModal">
            {{
                modelValue
                    ? (modelValue.id ? `Группа` : `Новая группа`) +
                      ": " +
                      modelValue.name
                    : "Добавить в группу"
            }}
        </div>
        <app-button red active @click="clearSelection" v-if="modelValue">
            <div class="flex items-center justify-center">
                <Icon name="material-symbols:delete" />
            </div>
        </app-button>
    </div>

    <!-- Модалка выбора группы -->
    <UModal
        v-model:open="modalOpen"
        title="Выбрать группу мероприятий"
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
                            { selected: modelValue?.id === group.id },
                        ]"
                        v-for="group in searchGroupsResult"
                        :key="group.id"
                        @click="selectGroup(group)"
                    >
                        {{ group.name }}
                    </div>
                    <div class="empty" v-if="searchGroupsResult.length === 0">
                        Группы не найдены
                    </div>
                </div>
                <app-button active @click="openCreateGroup"
                    >Создать группу</app-button
                >
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
import { ref, computed, watch } from "vue";
import { EventsGroupsService } from "~/client";
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

const createGroupButtonActive = computed(
    () => createGroupName.value.length > 0
);

const saveGroupCreation = () => {
    if (!createGroupButtonActive.value) return;

    const newGroup = {
        id: null,
        name: createGroupName.value,
        description: createGroupDescription.value,
        organizer: createGroupOrganizer.value,
        link: "",
    };

    emit("update:modelValue", newGroup);
    createGroupOpen.value = false;
    modalOpen.value = false;
};

const resetCreation = () => {
    createGroupName.value = "";
    createGroupDescription.value = "";
    createGroupOrganizer.value = "";
};

// Загрузка результатов поиска
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

watch(modalOpen, (isOpen) => {
    if (!isOpen) {
        searchGroup.value = "";
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

// Открытие модалки создания группы
const openCreateGroup = () => {
    resetCreation();
    createGroupOpen.value = true;
};

// Открытие основной модалки
const openModal = () => {
    modalOpen.value = true;
};
</script>

<style lang="scss">
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
    width: 100%;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
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
