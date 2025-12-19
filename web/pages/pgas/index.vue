<script setup lang="ts">
import { h, resolveComponent, ref, computed } from "vue";
import type { TableColumn } from "@nuxt/ui";
import {
    CustomAchievementsService,
    EventsLevelsService,
    type CustomAchievementRead,
    type CustomAchievementCreate,
    type CustomAchievementUpdate,
    type EventLevelRead,
} from "~/client";
import { useAuthStore } from "@/stores/auth";
import { storeToRefs } from "pinia";
import {validateUrl } from '@/composables/url'

definePageMeta({
    layout: "no-padding",
});

useHead({
    title: "ПГАС",
});

const UButton = resolveComponent("UButton");
const UBadge = resolveComponent("UBadge");
const Icon = resolveComponent("Icon");
const AppInput = resolveComponent("AppInput");

const { $toast } = useNuxtApp();
const authStore = useAuthStore();
const { userData } = storeToRefs(authStore);

const data = ref<CustomAchievementRead[]>([]);
const eventLevels = ref<EventLevelRead[]>([]);
const isLoading = ref(false);
const showOnlyCustom = ref(false);

// Модалка создания
const createModalOpen = ref(false);
const createForm = ref<CustomAchievementCreate>({
    name: "",
    date_from: "",
    date_to: null,
    level_of_participation: null,
    link: null,
    achievement_level: null,
});

// Модалка подтверждения закрытия
const confirmCloseModalOpen = ref(false);
const pendingClose = ref(false);

// Редактирование в таблице
const editingRowId = ref<string | null>(null);
const editForm = ref<CustomAchievementUpdate>({
    name: "",
    date_from: "",
    date_to: null,
    level_of_participation: null,
    link: null,
    achievement_level: null,
});

// Оригинальные данные для сравнения
const originalEditForm = ref<CustomAchievementUpdate | null>(null);

// Модалка удаления
const deleteModalOpen = ref(false);
const selectedAchievement = ref<CustomAchievementRead | null>(null);

// Предустановленные варианты уровня участия
const participationLevels = [
    "Организатор",
    "Помощь в организации",
    "Волонтер",
    "Победитель",
    "Призер",
    "Без присуждения мест",
    "Фотограф",
    "Видеограф",
    "Журналист",
    "Дизайнер",
    "Руководитель проекта",
    "Команда проекта",
    "Поданная, но не поддержанная заявка на грантовый конкурс",
];

// Фильтрация уровней мероприятий (убираем "другое" и "Другое")
const filteredEventLevels = computed(() => {
    return eventLevels.value.filter(
        (level) => level.name.toLowerCase() !== "другое"
    );
});

// Проверка, изменена ли форма
const isFormDirty = computed(() => {
    return (
        createForm.value.name !== "" ||
        createForm.value.date_from !== "" ||
        createForm.value.date_to !== null ||
        createForm.value.level_of_participation !== null ||
        createForm.value.link !== null ||
        createForm.value.achievement_level !== null
    );
});

// Валидация ссылки для формы создания
const createLinkIsValid = computed(() => {
    if (!createForm.value.link) return true;
    return validateUrl(createForm.value.link);
});

// Валидация ссылки для формы редактирования
const editLinkIsValid = computed(() => {
    if (!editForm.value.link) return true;
    return validateUrl(editForm.value.link);
});

// Проверка валидности формы создания
const isCreateFormValid = computed(() => {
    return !!(
        createForm.value.name &&
        createForm.value.name.trim().length > 0 &&
        createForm.value.date_from &&
        createLinkIsValid.value
    );
});

// Проверка изменений в режиме редактирования
const isEditFormChanged = computed(() => {
    if (!originalEditForm.value) return false;

    return (
        editForm.value.name !== originalEditForm.value.name ||
        editForm.value.date_from !== originalEditForm.value.date_from ||
        editForm.value.date_to !== originalEditForm.value.date_to ||
        editForm.value.level_of_participation !== originalEditForm.value.level_of_participation ||
        editForm.value.link !== originalEditForm.value.link ||
        editForm.value.achievement_level !== originalEditForm.value.achievement_level
    );
});

// Проверка валидности формы редактирования
const isEditFormValid = computed(() => {
    return !!(
        editForm.value.name &&
        editForm.value.name.trim().length > 0 &&
        editForm.value.date_from &&
        editLinkIsValid.value
    );
});

// Сортировка по дате (от новых к старым)
const sortedData = computed(() => {
    return [...data.value].sort((a, b) => {
        const dateA = new Date(a.date_from).getTime();
        const dateB = new Date(b.date_from).getTime();
        return dateB - dateA; // Сортировка от новых к старым
    });
});

const columns: TableColumn<CustomAchievementRead>[] = [
    {
        accessorKey: "name",
        header: "Название мероприятия",
        cell: ({ row }) => {
            if (editingRowId.value === row.original.id) {
                return h("div", { class: "py-2 w-full" }, [
                    h(AppInput, {
                        modelValue: editForm.value.name,
                        "onUpdate:modelValue": (value: string) => {
                            editForm.value.name = value;
                        },
                        white: true,
                        height: "32px",
                        required: true,
                        validator: (value: string) => {
                            return value && value.trim().length > 0;
                        },
                    }),
                ]);
            }
            return row.original.name;
        },
    },
    {
        accessorKey: "date_from",
        header: "Дата проведения",
        cell: ({ row }) => {
            if (editingRowId.value === row.original.id) {
                return h("div", { class: "py-2 flex gap-1 w-full min-w-[260px]" }, [
                    h(AppInput, {
                        modelValue: editForm.value.date_from,
                        "onUpdate:modelValue": (value: string) => {
                            editForm.value.date_from = value;
                        },
                        type: "date",
                        white: true,
                        height: "32px",
                        required: true,
                        validator: (value: any) => {
                            return !!value;
                        },
                    }),
                    h(AppInput, {
                        modelValue: editForm.value.date_to || "",
                        "onUpdate:modelValue": (value: string) => {
                            editForm.value.date_to = value || null;
                        },
                        type: "date",
                        white: true,
                        height: "32px",
                    }),
                ]);
            }
            const dateFrom = row.original.date_from;
            const dateTo = row.original.date_to;
            if (!dateFrom) return "-";

            const fromFormatted = new Date(dateFrom).toLocaleDateString("ru-RU");
            if (!dateTo) return fromFormatted;

            const toFormatted = new Date(dateTo).toLocaleDateString("ru-RU");
            return `${fromFormatted} - ${toFormatted}`;
        },
    },
    {
        accessorKey: "level_of_participation",
        header: "Уровень участия",
        cell: ({ row }) => {
            if (editingRowId.value === row.original.id) {
                return h("div", { class: "py-2 w-full min-w-[180px]" }, [
                    h(AppInput, {
                        modelValue: editForm.value.level_of_participation || "",
                        "onUpdate:modelValue": (value: string) => {
                            editForm.value.level_of_participation = value || null;
                        },
                        white: true,
                        height: "32px",
                        validator: (value: string) => {
                            return value && value.trim().length > 0;
                        },
                    }),
                ]);
            }
            return row.original.level_of_participation || "-";
        },
    },
    {
        accessorKey: "achievement_level",
        header: "Уровень мероприятия",
        cell: ({ row }) => {
            if (editingRowId.value === row.original.id) {
                return h("div", { class: "py-2 w-full min-w-[180px]" }, [
                    h(AppInput, {
                        modelValue: editForm.value.achievement_level || "",
                        "onUpdate:modelValue": (value: string) => {
                            editForm.value.achievement_level = value || null;
                        },
                        white: true,
                        height: "32px",
                        validator: (value: string) => {
                            return value && value.trim().length > 0;
                        },
                    }),
                ]);
            }
            return row.original.achievement_level || "-";
        },
    },
    {
        accessorKey: "link",
        header: "Ссылка на подтверждение",
        cell: ({ row }) => {
            if (editingRowId.value === row.original.id) {
                return h("div", { class: "py-2 w-full min-w-[200px]" }, [
                    h(AppInput, {
                        modelValue: editForm.value.link || "",
                        "onUpdate:modelValue": (value: string) => {
                            editForm.value.link = value || null;
                        },
                        placeholder: "https://...",
                        white: true,
                        height: "32px",
                        validator: () => {
                            return editLinkIsValid.value;
                        },
                    }),
                ]);
            }
            if (row.original.link) {
                return h(
                    "a",
                    {
                        href: row.original.link,
                        target: "_blank",
                        class: "text-blue-600 hover:underline",
                    },
                    "Открыть"
                );
            }
            return "-";
        },
    },
    {
        id: "actions",
        enableHiding: false,
        header: "Действия",
        meta: {
            class: {
                th: "text-right",
            },
        },
        cell: ({ row }) => {
            const isEditing = editingRowId.value === row.original.id;

            if (isEditing) {
                const canSave = isEditFormValid.value && isEditFormChanged.value;

                return h(
                    "div",
                    { class: "text-right flex gap-1 justify-end" },
                    [
                        h(
                            "div",
                            {
                                class: [
                                    "flex w-9 h-9 items-center justify-center rounded-xl transition-colors",
                                    canSave
                                        ? "bg-green-600 hover:bg-green-700 cursor-pointer"
                                        : "bg-gray-400 cursor-not-allowed"
                                ],
                                onClick: canSave ? () => updateAchievement(row.original.id) : undefined,
                            },
                            [
                                h(Icon, {
                                    name: "material-symbols:check",
                                    class: "text-white",
                                }),
                            ]
                        ),
                        h(
                            "div",
                            {
                                class: "flex w-9 h-9 items-center justify-center bg-gray-600 rounded-xl hover:bg-gray-700 transition-colors cursor-pointer",
                                onClick: cancelEdit,
                            },
                            [
                                h(Icon, {
                                    name: "material-symbols:close",
                                    class: "text-white",
                                }),
                            ]
                        ),
                    ]
                );
            }

            return h("div", { class: "text-right flex gap-1 justify-end" }, [
                h(
                    "div",
                    {
                        class: "flex w-9 h-9 items-center justify-center bg-black rounded-xl hover:bg-gray-800 transition-colors cursor-pointer",
                        onClick: () => startEdit(row.original),
                    },
                    [
                        h(Icon, {
                            name: "material-symbols:edit-outline",
                            class: "text-white",
                        }),
                    ]
                ),
                h(
                    "div",
                    {
                        class: "flex w-9 h-9 items-center justify-center bg-red-600 rounded-xl hover:bg-red-700 transition-colors cursor-pointer",
                        onClick: () => {
                            selectedAchievement.value = row.original;
                            deleteModalOpen.value = true;
                        },
                    },
                    [
                        h(Icon, {
                            name: "material-symbols:delete-outline",
                            class: "text-white",
                        }),
                    ]
                ),
            ]);
        },
    },
];

const filteredData = computed(() => {
    if (showOnlyCustom.value) {
        return sortedData.value.filter((item) => item.is_custom);
    }
    return sortedData.value;
});

async function loadAchievements() {
    try {
        isLoading.value = true;
        // TODO: Замените на правильный метод API когда он будет доступен
        // const achievements = await CustomAchievementsService.getCustomAchievements();
        // data.value = achievements;
        data.value = [];
    } catch (error) {
        $toast.error(HandleOpenApiError(error).message);
    } finally {
        isLoading.value = false;
    }
}

async function loadEventLevels() {
    try {
        const levels = await EventsLevelsService.getEventLevelsEventsLevelsGet();
        eventLevels.value = levels;
    } catch (error) {
        console.error("Ошибка загрузки уровней мероприятий:", error);
    }
}

async function createAchievement() {
    if (!createForm.value.name || !createForm.value.date_from) {
        $toast.error("Заполните обязательные поля");
        return;
    }

    if (!createLinkIsValid.value) {
        $toast.error("Введите корректную ссылку");
        return;
    }

    try {
        isLoading.value = true;
        const newAchievement = await CustomAchievementsService.createCustomAchievementCustomAchievementsPost(
            createForm.value
        );

        // Добавляем новое достижение в массив
        data.value.push(newAchievement);

        pendingClose.value = true;
        createModalOpen.value = false;
    } catch (error) {
        $toast.error(HandleOpenApiError(error).message);
    } finally {
        isLoading.value = false;
    }
}

function startEdit(achievement: CustomAchievementRead) {
    editingRowId.value = achievement.id;
    editForm.value = {
        name: achievement.name,
        date_from: achievement.date_from,
        date_to: achievement.date_to,
        level_of_participation: achievement.level_of_participation,
        link: achievement.link,
        achievement_level: achievement.achievement_level,
    };
    // Сохраняем оригинальные данные для сравнения
    originalEditForm.value = { ...editForm.value };
}

function cancelEdit() {
    editingRowId.value = null;
    originalEditForm.value = null;
    editForm.value = {
        name: "",
        date_from: "",
        date_to: null,
        level_of_participation: null,
        link: null,
        achievement_level: null,
    };
}

async function updateAchievement(id: string) {
    if (!editForm.value.name || !editForm.value.date_from) {
        $toast.error("Заполните обязательные поля");
        return;
    }

    if (!editLinkIsValid.value) {
        $toast.error("Введите корректную ссылку");
        return;
    }

    try {
        isLoading.value = true;
        const updatedAchievement = await CustomAchievementsService.updateCustomAchievementCustomAchievementsCustomAchievementIdPut(
            id,
            editForm.value
        );

        // Обновляем запись в массиве
        const index = data.value.findIndex((item) => item.id === id);
        if (index !== -1) {
            data.value[index] = updatedAchievement;
        }

        editingRowId.value = null;
        originalEditForm.value = null;
    } catch (error) {
        $toast.error(HandleOpenApiError(error).message);
    } finally {
        isLoading.value = false;
    }
}

async function deleteAchievement() {
    if (!selectedAchievement.value?.id) return;

    try {
        isLoading.value = true;
        await CustomAchievementsService.deleteCustomAchievementCustomAchievementsCustomAchievementIdDelete(
            selectedAchievement.value.id
        );

        // Удаляем из массива
        data.value = data.value.filter(
            (item) => item.id !== selectedAchievement.value!.id
        );

        deleteModalOpen.value = false;
    } catch (error) {
        $toast.error(HandleOpenApiError(error).message);
    } finally {
        isLoading.value = false;
    }
}

function resetCreateForm() {
    createForm.value = {
        name: "",
        date_from: "",
        date_to: null,
        level_of_participation: null,
        link: null,
        achievement_level: null,
    };
    pendingClose.value = false;
}

function selectParticipationLevel(level: string) {
    createForm.value.level_of_participation = level;
}

function selectAchievementLevel(level: string) {
    createForm.value.achievement_level = level;
}

// Обработчик попытки закрытия модалки
function handleClosePrevent() {
    if (isFormDirty.value) {
        pendingClose.value = true;
        confirmCloseModalOpen.value = true;
    }
}

// Обработчик изменения состояния модалки
function handleModalUpdate(value: boolean) {
    if (!value && isFormDirty.value && !pendingClose.value) {
        // Предотвращаем закрытие
        nextTick(() => {
            createModalOpen.value = true;
            confirmCloseModalOpen.value = true;
        });
    } else if (!value && pendingClose.value) {
        // Разрешаем закрытие
        pendingClose.value = false;
    } else {
        createModalOpen.value = value;
    }
}

// Подтверждение закрытия с потерей данных
function confirmClose() {
    confirmCloseModalOpen.value = false;
    pendingClose.value = true;
    createModalOpen.value = false;
}

// Отмена закрытия
function cancelClose() {
    confirmCloseModalOpen.value = false;
    pendingClose.value = false;
}

onMounted(() => {
    loadAchievements();
    loadEventLevels();
});
</script>

<template>
    <div class="flex-1 md:divide-accented w-full">
        <div
            class="flex md:items-center gap-2 min-h-[60px] overflow-x-auto px-2 head md:flex-row flex-col-reverse justify-between"
        >
            <div class="text-lg font-semibold">ПГАС</div>
            <div class="flex gap-2 items-center">
                <app-button
                    :active="showOnlyCustom"
                    :outline="!showOnlyCustom"
                    mini
                    @click="showOnlyCustom = !showOnlyCustom"
                >
                    Только мои достижения
                </app-button>
                <app-button active mini @click="createModalOpen = true">
                    Добавить достижение
                </app-button>
            </div>
        </div>

        <div class="overflow-auto">
            <UTable
                :data="filteredData"
                :columns="columns"
                :loading="isLoading"
                sticky
            />
        </div>
    </div>

    <!-- Модалка создания -->
    <UModal
        :open="createModalOpen"
        title="Добавить достижение"
        @update:open="handleModalUpdate"
        @after-leave="resetCreateForm"
        @close:prevent="handleClosePrevent"
    >
        <template #body>
            <div class="flex flex-col gap-2">
                <app-input
                    v-model="createForm.name"
                    label="Название мероприятия *"
                    required
                    white
                    :validator="(value) => value && value.trim().length > 0"
                />

                <div class="grid grid-cols-2 gap-2">
                    <app-input
                        v-model="createForm.date_from"
                        type="date"
                        label="Дата начала *"
                        required
                        white
                        :validator="(value) => !!value"
                    />
                    <app-input
                        v-model="createForm.date_to"
                        type="date"
                        label="Дата окончания"
                        white
                    />
                </div>

                <app-input
                    v-model="createForm.level_of_participation"
                    label="Уровень участия *"
                    white
                    :validator="(value) => value && value.trim().length > 0"
                />

                <div class="flex flex-wrap gap-1">
                    <UBadge
                        v-for="level in participationLevels"
                        :key="level"
                        :color="
                            createForm.level_of_participation === level
                                ? 'primary'
                                : 'neutral'
                        "
                        variant="subtle"
                        class="cursor-pointer"
                        @click="selectParticipationLevel(level)"
                    >
                        {{ level }}
                    </UBadge>
                </div>

                <app-input
                    v-model="createForm.achievement_level"
                    label="Уровень мероприятия *"
                    white
                    :validator="(value) => value && value.trim().length > 0"
                />

                <div class="flex flex-wrap gap-1">
                    <UBadge
                        v-for="level in filteredEventLevels"
                        :key="level.id"
                        :color="
                            createForm.achievement_level === level.name
                                ? 'primary'
                                : 'neutral'
                        "
                        variant="subtle"
                        class="cursor-pointer"
                        @click="selectAchievementLevel(level.name)"
                    >
                        {{ level.name }}
                    </UBadge>
                </div>

                <app-input
                    v-model="createForm.link"
                    label="Ссылка на подтверждение *"
                    placeholder="https://..."
                    white
                    :validator="() => createLinkIsValid"
                />

                <div class="flex gap-2 mt-1">
                    <app-button
                        @click="createAchievement"
                        :active="isCreateFormValid"
                        :disabled="!isCreateFormValid || isLoading"
                    >
                        Создать
                    </app-button>
                    <app-button @click="handleModalUpdate(false)">
                        Отмена
                    </app-button>
                </div>
            </div>
        </template>
    </UModal>

    <!-- Модалка подтверждения закрытия -->
    <UModal
        v-model:open="confirmCloseModalOpen"
        title="Несохраненные изменения"
    >
        <template #body>
            <div>
                <p class="text-sm mb-2">
                    У вас есть несохраненные изменения. Вы уверены, что хотите закрыть окно? Все изменения будут потеряны.
                </p>
                <div class="flex gap-2 mt-2">
                    <app-button active red @click="confirmClose">
                        Закрыть
                    </app-button>
                    <app-button active @click="cancelClose">
                        Продолжить
                    </app-button>
                </div>
            </div>
        </template>
    </UModal>

    <!-- Модалка удаления -->
    <UModal v-model:open="deleteModalOpen" title="Удалить достижение">
        <template #body>
            <div>
                <div class="text-md mb-2">
                    <p v-if="selectedAchievement">
                        Вы уверены, что хотите удалить достижение
                        <strong>{{ selectedAchievement.name }}</strong
                        >?
                    </p>
                </div>
                <div class="grid grid-cols-2 gap-2">
                    <app-button active red @click="deleteAchievement">
                        Удалить
                    </app-button>
                    <app-button @click="deleteModalOpen = false">
                        Отмена
                    </app-button>
                </div>
            </div>
        </template>
    </UModal>
</template>

<style scoped lang="scss">
.head {
    @include md {
        border-bottom: 1px solid $border-color;
    }
}
</style>
