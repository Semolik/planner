<script setup lang="ts">
import { h, resolveComponent, ref, computed, watch, onMounted, nextTick } from "vue";
import type { TableColumn } from "@nuxt/ui";
import {
  CustomAchievementsService,
  AchievementsService,
  EventsLevelsService,
  MeetingsService,
  type AchievementRead,
  type AchievementCreate,
  type AchievementUpdate,
  type EventLevelRead,
} from "~/client";
import { useAuthStore } from "@/stores/auth";
import { storeToRefs } from "pinia";
import { validateUrl } from "~/composables/url";
import { HandleOpenApiError } from "~/composables/handleErrors";
import { NuxtLink } from "#components";
import { useLocalStorage } from "@vueuse/core";

definePageMeta({
  layout: "no-padding",
});

useHead({
  title: "ПГАС",
});

const UBadge = resolveComponent("UBadge");
const Icon = resolveComponent("Icon");
const AppInput = resolveComponent("AppInput");
const UCheckbox = resolveComponent("UCheckbox");

const { $toast } = useNuxtApp();
const authStore = useAuthStore();
const { userData } = storeToRefs(authStore);

const data = ref<AchievementRead[]>([]);
const eventLevels = ref<EventLevelRead[]>([]);
const isLoading = ref(false);
const showOnlyCustom = ref(false);

// Выбор года
const currentYear = new Date().getFullYear();
const selectedYear = ref(currentYear);

// Генерация списка годов (текущий и предыдущие 5 лет)
const availableYears = computed(() => {
  const years = [];
  for (let i = 0; i < 6; i++) {
    years.push(currentYear - i);
  }
  return years;
});

// Модалка создания
const createModalOpen = ref(false);
const createForm = ref<AchievementCreate>({
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
const editForm = ref<AchievementUpdate>({
  name: "",
  date_from: "",
  date_to: null,
  level_of_participation: null,
  link: null,
  achievement_level: null,
});

// Оригинальные данные для сравнения
const originalEditForm = ref<AchievementUpdate | null>(null);

// Модалка удаления
const deleteModalOpen = ref(false);
const selectedAchievement = ref<AchievementRead | null>(null);

// --- Модалка формирования справки ---
const reportModalOpen = ref(false);
const reportMeetings = ref<any[]>([]);
const reportLoading = ref(false);

// Ключ для localStorage зависит от года
const storageKey = computed(
  () => `pgas-report-meetings-${selectedYear.value}`,
);

// реактивный массив выбранных id планёрок
const selectedMeetingIds = useLocalStorage<string[]>(
  storageKey.value,
  [],
);

// при смене года подхватываем сохранённые значения для нового ключа
watch(
  selectedYear,
  (year) => {
    const key = `pgas-report-meetings-${year}`;
    const saved = localStorage.getItem(key);
    selectedMeetingIds.value = saved ? JSON.parse(saved) : [];
  },
  { immediate: false },
);

// --- Подсчёт задач по ролям для справки ---
const achievementsForReport = ref<AchievementRead[]>([]);
const reportStats = computed(() => {
  let copywriter = 0, designer = 0, photographer = 0;
  for (const a of achievementsForReport.value) {
    if (a.level_of_participation === 'Журналист') copywriter++;
    if (a.level_of_participation === 'Дизайнер') designer++;
    if (
      a.level_of_participation === 'Фотограф' &&
      !a.event_id &&
      !(a as any).is_aggregated // не учитывать агрегированные задачи
    ) photographer++;
  }
  return { copywriter, designer, photographer };
});

async function openReportModal() {
  reportModalOpen.value = true;
  reportLoading.value = true;
  try {
    const [meetings, achievements] = await Promise.all([
      MeetingsService.getMeetingsMeetingsGet(selectedYear.value),
      AchievementsService.getAchievementsByYearAchievementsGet(selectedYear.value, false),
    ]);
    reportMeetings.value = meetings;
    achievementsForReport.value = achievements;
    // чистим ids, которых больше нет в списке встреч
    const existingIds = new Set(meetings.map((m: any) => m.id));
    selectedMeetingIds.value = selectedMeetingIds.value.filter((id) =>
      existingIds.has(id),
    );
  } catch (e) {
    $toast.error("Ошибка загрузки планёрок или задач");
    reportMeetings.value = [];
    achievementsForReport.value = [];
  } finally {
    reportLoading.value = false;
  }
}

function closeReportModal() {
  reportModalOpen.value = false;
}

function isMeetingSelected(id: string) {
  return selectedMeetingIds.value.includes(id);
}

function toggleMeeting(id: string, value: boolean) {
  if (value) {
    if (!selectedMeetingIds.value.includes(id)) {
      selectedMeetingIds.value = [...selectedMeetingIds.value, id];
    }
  } else {
    selectedMeetingIds.value = selectedMeetingIds.value.filter(
      (mid) => mid !== id,
    );
  }
}

function confirmReportMeetings() {
  $toast.info("Выбрано: " + selectedMeetingIds.value.join(", "));
  closeReportModal();
}

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
    (level) => level.name.toLowerCase() !== "другое",
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

// Валидация ссылки
const linkIsValid = computed(() => {
  if (!createForm.value.link) return true;
  return validateUrl(createForm.value.link);
});

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
    linkIsValid.value
  );
});

// Проверка изменений в режиме редактирования
const isEditFormChanged = computed(() => {
  if (!originalEditForm.value) return false;

  return (
    editForm.value.name !== originalEditForm.value.name ||
    editForm.value.date_from !== originalEditForm.value.date_from ||
    editForm.value.date_to !== originalEditForm.value.date_to ||
    editForm.value.level_of_participation !==
      originalEditForm.value.level_of_participation ||
    editForm.value.link !== originalEditForm.value.link ||
    editForm.value.achievement_level !==
      originalEditForm.value.achievement_level
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
    return dateB - dateA;
  });
});

const columns: TableColumn<AchievementRead>[] = [
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
      if (!row.original.is_custom) {
        return h(
          NuxtLink,
          {
            to: `/tasks/${row.original.id}`,
            class: "text-blue-600 hover:underline cursor-pointer",
          },
          { default: () => row.original.name },
        );
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
            validator: () => editLinkIsValid.value,
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
          "Открыть",
        );
      }
      if (
        !row.original.is_custom &&
        ["Дизайнер", "Журналист"].includes(
          row.original.level_of_participation as string,
        )
      ) {
        return h(
          "span",
          { class: "text-gray-500 italic" },
          "указывается при выгрузке",
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
                    : "bg-gray-400 cursor-not-allowed",
                ],
                onClick: canSave
                  ? () => updateAchievement(row.original.id)
                  : undefined,
              },
              [
                h(Icon, {
                  name: "material-symbols:check",
                  class: "text-white",
                }),
              ],
            ),
            h(
              "div",
              {
                class:
                  "flex w-9 h-9 items-center justify-center bg-gray-600 rounded-xl hover:bg-gray-700 transition-colors cursor-pointer",
                onClick: cancelEdit,
              },
              [
                h(Icon, {
                  name: "material-symbols:close",
                  class: "text-white",
                }),
              ],
            ),
          ],
        );
      }

      if (row.original.is_custom) {
        return h("div", { class: "text-right flex gap-1 justify-end" }, [
          h(
            "div",
            {
              class:
                "flex w-9 h-9 items-center justify-center bg-black rounded-xl hover:bg-gray-800 transition-colors cursor-pointer",
              onClick: () => startEdit(row.original),
            },
            [
              h(Icon, {
                name: "material-symbols:edit-outline",
                class: "text-white",
              }),
            ],
          ),
          h(
            "div",
            {
              class:
                "flex w-9 h-9 items-center justify-center bg-red-600 rounded-xl hover:bg-red-700 transition-colors cursor-pointer",
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
            ],
          ),
        ]);
      }

      return h("div", { class: "text-right" }, "-");
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
    const achievements =
      await AchievementsService.getAchievementsByYearAchievementsGet(
        selectedYear.value,
        showOnlyCustom.value,
      );
    data.value = achievements;
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

  if (!linkIsValid.value) {
    $toast.error("Введите корректную ссылку");
    return;
  }

  try {
    isLoading.value = true;
    const newAchievement =
      await CustomAchievementsService.createCustomAchievementCustomAchievementsPost(
        createForm.value,
      );

    data.value.push(newAchievement);

    pendingClose.value = true;
    createModalOpen.value = false;

    $toast.success("Достижение успешно добавлено");
  } catch (error) {
    $toast.error(HandleOpenApiError(error).message);
  } finally {
    isLoading.value = false;
  }
}

function startEdit(achievement: AchievementRead) {
  if (!achievement.is_custom) return;

  editingRowId.value = achievement.id;
  editForm.value = {
    name: achievement.name,
    date_from: achievement.date_from,
    date_to: achievement.date_to,
    level_of_participation: achievement.level_of_participation,
    link: achievement.link,
    achievement_level: achievement.achievement_level,
  };
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
    const updatedAchievement =
      await CustomAchievementsService.updateCustomAchievementCustomAchievementsCustomAchievementIdPut(
        id,
        editForm.value,
      );

    const index = data.value.findIndex((item) => item.id === id);
    if (index !== -1) {
      data.value[index] = updatedAchievement;
    }

    editingRowId.value = null;
    originalEditForm.value = null;

    $toast.success("Достижение успешно обновлено");
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
      selectedAchievement.value.id,
    );

    data.value = data.value.filter(
      (item) => item.id !== selectedAchievement.value!.id,
    );

    deleteModalOpen.value = false;

    $toast.success("Достижение успешно удалено");
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
    nextTick(() => {
      createModalOpen.value = true;
      confirmCloseModalOpen.value = true;
    });
  } else if (!value && pendingClose.value) {
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

// Обработчик выбора из дропдауна
const handleDropdownSelect = (key: string) => {
  if (key === "report") {
    generateReport();
  } else if (key === "table") {
    generateTable();
  }
};

function generateReport() {
  openReportModal();
}

function generateTable() {
  $toast.info("Формирование таблицы...");
}

// Следим за изменением года и фильтра
watch([selectedYear, showOnlyCustom], () => {
  loadAchievements();
});

onMounted(() => {
  loadAchievements();
  loadEventLevels();
});

// Колонки для таблицы планёрок в модалке
const reportColumns: TableColumn<any>[] = [
  {
    accessorKey: "present",
    header: "Присутствовал",
    meta: {
      class: {
        th: "text-center w-0",              // минимальная ширина шапки
        td: "w-0 whitespace-nowrap",        // минимальная ширина ячейки
      },
    },
    cell: ({ row }) =>
      h(
        "div",
        { class: "flex items-center justify-center" },
        [
          h(UCheckbox as any, {
            color: "neutral",
            size: "lg", // или "xl"
            modelValue: isMeetingSelected(row.original.id),
            "onUpdate:modelValue": (val: boolean) =>
              toggleMeeting(row.original.id, val),
          }),
        ],
      ),
    enableSorting: false,
  },
  {
    accessorKey: "date",
    header: "Дата",
    meta: {
      class: {
        // колонка по умолчанию тянется на оставшееся место
        th: "text-left",
        td: "text-left",
      },
    },
    cell: ({ row }) =>
      new Date(row.original.date).toLocaleDateString("ru-RU"),
  },
];

// --- Универсальная фильтрация задач по ролям ---
function getTasksByRole(role: string, achievements: AchievementRead[]) {
  if (role === 'Фотограф') {
    return achievements.filter(
      (a) => a.level_of_participation === 'Фотограф' && !a.event_id && !(a as any).is_aggregated
    );
  } else if (role === 'Дизайнер') {
    return achievements.filter((a) => a.level_of_participation === 'Дизайнер');
  } else if (role === 'Журналист') {
    return achievements.filter((a) => a.level_of_participation === 'Журналист');
  }
  return [];
}

// --- Модалка предпросмотра задач по ролям ---
const previewModalOpen = ref(false);
const previewTasks = ref<AchievementRead[]>([]);
const previewRole = ref<string>("");

function openPreviewModal(role: string) {
  previewTasks.value = getTasksByRole(role, achievementsForReport.value);
  previewRole.value = role;
  previewModalOpen.value = true;
}

function previewLink(link: string | null) {
  if (link) window.open(link, '_blank');
}

</script>

<template>
  <div>
    <div class="flex-1 md:divide-accented w-full">
      <div
        class="flex md:items-center gap-2 min-h-[60px] overflow-x-auto px-2 head md:flex-row flex-col-reverse justify-between"
      >
        <div class="text-lg font-semibold">ПГАС</div>
      </div>

      <div class="overflow-auto">
        <div
          class="flex flex-wrap gap-2 items-center mb-2 px-4 py-3 bg-white justify-between"
        >
          <div class="flex gap-2 items-center flex-wrap">
            <select
              v-model="selectedYear"
              class="px-3 py-1 border rounded-lg bg-white text-sm"
            >
              <option
                v-for="year in availableYears"
                :key="year"
                :value="year"
              >
                {{ year }}
              </option>
            </select>
            <USwitch
              v-model="showOnlyCustom"
              size="sm"
              class="ml-2"
              :label="'Только кастомные'"
              color="neutral"
            />
          </div>
          <div class="flex gap-2 items-center flex-wrap">
            <app-button :active="true" mini @click="createModalOpen = true">
              Добавить достижение
            </app-button>
            <app-button :active="true" mini @click="generateReport">
              <Icon
                name="material-symbols:description-outline"
                class="mr-1"
              />
              Сформировать справку
            </app-button>
            <app-button :active="true" mini @click="generateTable">
              <Icon
                name="material-symbols:table-rows-narrow"
                class="mr-1"
              />
              Сформировать таблицу
            </app-button>
          </div>
        </div>
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
            :validator="() => linkIsValid"
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
            У вас есть несохраненные изменения. Вы уверены, что хотите закрыть
            окно? Все изменения будут потеряны.
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

    <!-- Модалка формирования справки -->
    <UModal
      :open="reportModalOpen"
      title="Сформировать справку"
      @update:open="closeReportModal"
    >
      <template #body>
        <div v-if="reportLoading" class="py-6 text-center text-gray-500">
          Загрузка...
        </div>
        <div v-else>
          <div class="mb-4 text-sm text-gray-700">
            Будет учтено:
            <div class="flex flex-col gap-2 mt-2">
              <app-button
                v-if="reportStats.copywriter"
                active
                mini
                @click="openPreviewModal('Журналист')"
              >
                {{ reportStats.copywriter }} задач копирайтера
              </app-button>
              <app-button
                v-if="reportStats.designer"
                active
                mini
                @click="openPreviewModal('Дизайнер')"
              >
                {{ reportStats.designer }} задач дизайнера
              </app-button>
              <app-button
                v-if="reportStats.photographer"
                active
                mini
                @click="openPreviewModal('Фотограф')"
              >
                {{ reportStats.photographer }} задач фотографа
              </app-button>
              <span v-if="!reportStats.copywriter && !reportStats.designer && !reportStats.photographer">нет задач по ролям</span>
            </div>
          </div>
          <div class="mb-2 text-xs text-gray-500">
            Отметьте, на каких планёрках вы присутствовали — они будут включены в справку.
          </div>
          <div
            v-if="reportMeetings.length === 0"
            class="py-6 text-center text-gray-500"
          >
            Нет планёрок за выбранный год
          </div>
          <div v-else class="flex flex-col">
            <UTable
              :data="reportMeetings"
              :columns="reportColumns"
              class="mb-4"
            />
            <app-button
                mini
                active
                :disabled="selectedMeetingIds.length === 0"
                @click="confirmReportMeetings"
              >
                Сформировать справку
              </app-button>
          </div>
        </div>
      </template>
    </UModal>

    <!-- Модалка предпросмотра задач по ролям -->
    <UModal :open="previewModalOpen" @update:open="previewModalOpen = $event" :title="`Задачи: ${previewRole}`">
      <template #body>
        <div v-if="previewTasks.length === 0" class="text-gray-500 py-4 text-center">
          Нет задач для выбранной роли
        </div>
        <div v-else class="flex flex-col gap-3">
          <div v-for="task in previewTasks" :key="task.id" class="flex items-center gap-2">
            <app-input
              :model-value="task.name + (task.date_from ? ' (' + new Date(task.date_from).toLocaleDateString('ru-RU') + ')' : '')"
              disabled


            />
            <a
              :href="`/tasks/${task.id}`"
              target="_blank"
              class="link"
              rel="noopener noreferrer"
              style="margin-left: 4px;"
            >
              <UIcon name="material-symbols:open-in-new" />
            </a>
          </div>
        </div>
      </template>
    </UModal>
  </div>
</template>

<style scoped lang="scss">
.head {
  @include md {
    border-bottom: 1px solid $border-color;
  }
}
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
