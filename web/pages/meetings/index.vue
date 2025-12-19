<script setup lang="ts">
import { h, resolveComponent, ref } from "vue";
import type { TableColumn } from "@nuxt/ui";
import {
    MeetingsService,
    type MeetingRead,
    type MeetingCreate,
} from "~/client";
import { useAuthStore } from "@/stores/auth";
import { storeToRefs } from "pinia";

definePageMeta({
    layout: "no-padding",
});

useHead({
    title: "Планерки",
});

const UButton = resolveComponent("UButton");
const Icon = resolveComponent("Icon");

const { $toast } = useNuxtApp();
const authStore = useAuthStore();
const { userData } = storeToRefs(authStore);

const data = ref<MeetingRead[]>([]);
const isLoading = ref(false);
const tableContainer = ref<HTMLElement>();

// Состояния модалок
const createModalOpen = ref(false);
const editModalOpen = ref(false);
const deleteModalOpen = ref(false);
const selectedMeeting = ref<MeetingRead | null>(null);

// Формы
const createForm = ref<MeetingCreate>({
    date: "",
});

const editForm = ref<MeetingCreate>({
    date: "",
});

// Проверка прав администратора
const isAdmin = computed(() => userData.value?.is_superuser ?? false);

const columns: TableColumn<MeetingRead>[] = [
    {
        accessorKey: "date",
        header: "Дата",
        cell: ({ row }) => {
            const date = row.original.date;
            if (!date) return "Не указана";

            const parsedDate = new Date(date);
            return isNaN(parsedDate.getTime())
                ? "Не указана"
                : parsedDate.toLocaleDateString("ru-RU", {
                      year: "numeric",
                      month: "long",
                      day: "numeric",
                  });
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
            if (!isAdmin.value) return null;

            return h("div", { class: "text-right flex gap-1 justify-end" }, [
                h(
                    "div",
                    {
                        class: "flex w-9 h-9 items-center justify-center bg-black rounded-xl hover:bg-gray-800 transition-colors cursor-pointer",
                        onClick: () => {
                            selectedMeeting.value = row.original;
                            editForm.value = {
                                date: row.original.date,
                            };
                            editModalOpen.value = true;
                        },
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
                            selectedMeeting.value = row.original;
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

async function loadMeetings() {
    try {
        isLoading.value = true;
        const meetings = await MeetingsService.getMeetingsMeetingsGet();
        data.value = meetings;
    } catch (error) {
        $toast.error(HandleOpenApiError(error).message);
    } finally {
        isLoading.value = false;
    }
}

// Создание планерки
async function createMeeting() {
    if (!createForm.value.date) {
        $toast.error("Укажите дату");
        return;
    }

    try {
        isLoading.value = true;
        await MeetingsService.createMeetingMeetingsPost(createForm.value);
        createModalOpen.value = false;
        await loadMeetings();
    } catch (error) {
        $toast.error(HandleOpenApiError(error).message);
    } finally {
        isLoading.value = false;
    }
}

// Редактирование планерки
async function updateMeeting() {
    if (!selectedMeeting.value?.id || !editForm.value.date) {
        $toast.error("Укажите дату");
        return;
    }

    try {
        isLoading.value = true;
        await MeetingsService.updateMeetingMeetingsMeetingIdPut(
            selectedMeeting.value.id,
            editForm.value
        );
        editModalOpen.value = false;
        await loadMeetings();
    } catch (error) {
        $toast.error(HandleOpenApiError(error).message);
    } finally {
        isLoading.value = false;
    }
}

// Удаление планерки
async function deleteMeeting() {
    if (!selectedMeeting.value?.id) return;

    try {
        isLoading.value = true;
        await MeetingsService.deleteMeetingMeetingsMeetingIdDelete(
            selectedMeeting.value.id
        );
        deleteModalOpen.value = false;
        await loadMeetings();
    } catch (error) {
        $toast.error(HandleOpenApiError(error).message);
    } finally {
        isLoading.value = false;
    }
}

// Сброс формы создания после закрытия модалки
function resetCreateForm() {
    createForm.value = { date: "" };
}

onMounted(() => {
    loadMeetings();
});
</script>

<template>
    <div class="flex-1 md:divide-accented w-full">
        <div
            class="flex md:items-center gap-2 min-h-[60px] overflow-x-auto px-2 head md:flex-row flex-col-reverse justify-between"
        >
            <div class="text-lg font-semibold">Планерки</div>
            <app-button
                v-if="isAdmin"
                active
                mini
                @click="createModalOpen = true"
            >
                Добавить планерку
            </app-button>
        </div>

        <div ref="tableContainer" class="overflow-auto">
            <UTable
                :data="data"
                :columns="columns"
                :loading="isLoading"
                sticky
            />
        </div>
    </div>

    <!-- Модалка создания (только для админов) -->
    <UModal
        v-if="isAdmin"
        v-model:open="createModalOpen"
        title="Создать планерку"
        @after-leave="resetCreateForm"
    >
        <template #body>
            <div class="flex flex-col gap-3">
                <app-input
                    v-model="createForm.date"
                    type="date"
                    label="Дата"
                    required
                    white
                />

                <div class="flex gap-2 mt-2">
                    <app-button
                        @click="createMeeting"
                        active
                        :disabled="!createForm.date || isLoading"
                    >
                        Создать
                    </app-button>
                    <app-button @click="createModalOpen = false">
                        Отмена
                    </app-button>
                </div>
            </div>
        </template>
    </UModal>

    <!-- Модалка редактирования (только для админов) -->
    <UModal
        v-if="isAdmin"
        v-model:open="editModalOpen"
        title="Редактировать планерку"
    >
        <template #body>
            <div class="flex flex-col gap-3">
                <app-input
                    v-model="editForm.date"
                    type="date"
                    label="Дата"
                    required
                    white
                />

                <div class="flex gap-2 mt-2">
                    <app-button
                        @click="updateMeeting"
                        active
                        :disabled="!editForm.date || isLoading"
                    >
                        Сохранить
                    </app-button>
                    <app-button @click="editModalOpen = false">
                        Отмена
                    </app-button>
                </div>
            </div>
        </template>
    </UModal>

    <!-- Модалка удаления (только для админов) -->
    <UModal
        v-if="isAdmin"
        v-model:open="deleteModalOpen"
        title="Удалить планерку"
    >
        <template #body>
            <div class="text-md">
                <p v-if="selectedMeeting">
                    Вы уверены, что хотите удалить планерку от
                    <strong>{{
                        new Date(selectedMeeting.date).toLocaleDateString(
                            "ru-RU"
                        )
                    }}</strong
                    >?
                </p>
            </div>
            <div class="grid grid-cols-2 gap-2 mt-4">
                <app-button active red @click="deleteMeeting">
                    Удалить
                </app-button>
                <app-button @click="deleteModalOpen = false">
                    Отмена
                </app-button>
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
