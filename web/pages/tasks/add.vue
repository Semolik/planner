<template>
    <app-form full-height headline="Создание задачи">
        <UTabs :items="items" color="neutral" v-model="activeTab">
            <template #task>
                <div v-auto-animate class="flex flex-col gap-2 min-h-[310px]">
                    <app-input v-model="name" label="Название задачи" required white />
                    <UCheckbox
                        v-model="useInPgas"
                        color="neutral"
                        variant="card"
                        label="Учитывать в ПГАС"
                        class="flex-1"
                    />
                    <UCheckbox
                        v-model="useSingleDeadline"
                        color="neutral"
                        variant="card"
                        label="Единая дата дедлайна"
                        class="flex-1"
                    />
                    <app-input
                        v-if="useSingleDeadline"
                        v-model="singleDeadline"
                        label="Общая дата дедлайна"
                        type="date"
                        required
                        white
                    />
                    <div v-for="(label, role) in labels" :key="role" class="flex gap-2">
                        <app-button
                            :outline="!tasks[role].use"
                            active
                            class="grow"
                            @click="openModal(role)"
                        >
                            {{ taskButtonText(label[1], tasks[role].use) }}
                        </app-button>

                        <app-button
                            v-if="tasks[role].use"
                            active
                            outline
                            @click="clearTask(role)"
                        >
                            <Icon name="material-symbols:delete" />
                        </app-button>
                    </div>
                </div>
            </template>
            <template #birthday>
                <div class="flex flex-col gap-2 min-h-[310px]">
                     <app-button active @click="openUserSelectModal" class="w-full" v-if="selectedUser">
                        Изменить пользователя
                    </app-button>
                    <div v-if="!selectedUser" class="flex flex-col gap-2 items-center justify-center flex-1">
                        <Icon name="material-symbols:cake" class="text-6xl text-gray-400" />
                        <p class="text-center text-gray-500">
                            Выберите пользователя для создания<br />задачи на день рождения
                        </p>
                    </div>
                    <div v-else class="flex flex-col gap-2">
                        <div class="selected-user">
                            <div class="user-info">
                                <div class="user-details">
                                    <div class="name">{{ useFullName(selectedUser) }}</div>
                                    <div v-if="selectedUser.birth_date" class="birth-date">
                                        День рождения: {{ formatDate(selectedUser.birth_date) }}
                                    </div>
                                </div>
                            </div>
                        </div>
                        <app-input
                            v-model="birthdayTaskDueDate"
                            label="Дедлайн задачи"
                            type="date"
                            required
                            white
                        />
                    </div>
                    <app-button active @click="openUserSelectModal" class="w-full mt-auto" v-if="!selectedUser">
                        Выбрать пользователя
                    </app-button>

                </div>
            </template>
        </UTabs>
        <app-button :active="isFormValidForSave" :disabled="!isFormValidForSave" @click="submitTask">
            Сохранить задачу
        </app-button>
    </app-form>

    <UModal
        v-if="currentRole"
        v-model:open="modalOpen"
        :title="`Создать подзадачу для ${labels[currentRole][1]}`"
    >
        <template #body>
            <div class="flex flex-col gap-2">
                <app-input
                    v-model="form.name"
                    label="Название подзадачи"
                    required
                    white
                />
                <UCheckbox
                    v-model="form.forSingleUser"
                    label="Для одного исполнителя"
                    color="neutral"
                    variant="card"
                />
                <app-input
                    v-model="form.dueDate"
                    label="Срок выполнения подзадачи"
                    type="date"
                    required
                    white
                />
                <app-input
                    v-model="form.description"
                    label="Описание подзадачи"
                    type="textarea"
                    white
                />

                <app-button
                    :active="formValid"
                    :disabled="!formValid"
                    @click="submitModal"
                >
                    Сохранить
                </app-button>
            </div>
        </template>
    </UModal>

    <UserSelectModal
        v-model:active="userSelectModalOpen"
        @select="handleUserSelect"
    />
</template>

<script setup>
import { UserRole, TasksService } from "~/client";
import { routesNames } from "@typed-router";

definePageMeta({ middleware: ["admin"] });

// Основное состояние формы
const name = ref("");

// Роли и их метки
const labels = {
    [UserRole.PHOTOGRAPHER]: ["Фотографы", "фотографов"],
    [UserRole.COPYWRITER]: ["Копирайтеры", "копирайтеров"],
    [UserRole.DESIGNER]: ["Дизайнеры", "дизайнеров"],
};

// Состояние задач для каждой роли
const tasks = ref({
    [UserRole.PHOTOGRAPHER]: createEmptyTask(UserRole.PHOTOGRAPHER),
    [UserRole.COPYWRITER]: createEmptyTask(UserRole.COPYWRITER),
    [UserRole.DESIGNER]: createEmptyTask(UserRole.DESIGNER),
});

// Настройки задачи
const useInPgas = ref(true);
const useSingleDeadline = ref(false);
const singleDeadline = ref("");

// Вкладки
const items = [
    { label: "Задача", slot: "task", icon: "material-symbols:task", value: "task" },
    { label: "Дни рождения", slot: "birthday", icon: "material-symbols:cake", value: "birthday" },
];
const activeTab = ref("task");

// Состояние для задачи на день рождения
const selectedUser = ref(null);
const userSelectModalOpen = ref(false);
const birthdayTaskDueDate = ref("");

// Вычисляемое свойство для определения типа задачи
const isBirthdayTask = computed(() => activeTab.value === "birthday");

// Функция для расчёта ближайшего дня рождения
const getNextBirthday = (birthDate) => {
    if (!birthDate) return "";

    const today = new Date();
    const birth = new Date(birthDate);

    // Устанавливаем день рождения на текущий год
    let nextBirthday = new Date(
        today.getFullYear(),
        birth.getMonth(),
        birth.getDate()
    );

    // Если день рождения в этом году уже прошёл, берём следующий год
    if (nextBirthday < today) {
        nextBirthday.setFullYear(today.getFullYear() + 1);
    }

    // Форматируем в YYYY-MM-DD для input type="date"
    return nextBirthday.toISOString().split('T')[0];
};

// Создание пустой задачи
function createEmptyTask(role) {
    return {
        use: false,
        name: "",
        description: "",
        deadline: "",
        for_single_user: role === UserRole.COPYWRITER || role === UserRole.DESIGNER,
    };
}

// Состояние формы модального окна
const form = ref({
    name: '',
    description: "",
    dueDate: "",
    forSingleUser: false,
});

const modalOpen = ref(false);
const currentRole = ref(null);

// Валидация формы модального окна
const formValid = computed(() => Boolean(form.value.dueDate));

// Открытие модального окна для создания подзадачи
const openModal = (role) => {
    currentRole.value = role;
    const task = tasks.value[role];

    form.value = {
        name: task.name || '',
        description: task.description,
        dueDate: useSingleDeadline.value ? (singleDeadline.value || task.deadline) : task.deadline,
        forSingleUser: task.for_single_user,
    };
    modalOpen.value = true;
};

// Сохранение подзадачи
const submitModal = () => {
    if (!formValid.value) return;

    const task = tasks.value[currentRole.value];

    task.use = true;
    task.name = form.value.name;
    task.description = form.value.description;
    task.deadline = form.value.dueDate;
    task.for_single_user = form.value.forSingleUser;

    if (useSingleDeadline.value) {
        singleDeadline.value = form.value.dueDate;
        Object.keys(tasks.value).forEach(role => {
            if (tasks.value[role].use) {
                tasks.value[role].deadline = form.value.dueDate;
            }
        });
    }

    modalOpen.value = false;
};

// Очистка задачи для роли
const clearTask = (role) => {
    tasks.value[role] = createEmptyTask(role);
};

// Текст кнопки для задачи
const taskButtonText = (roleName, isUsed) =>
    isUsed ? `Подзадача для ${roleName}` : `Создать подзадачу для ${roleName}`;

// Открытие модального окна выбора пользователя
const openUserSelectModal = () => {
    userSelectModalOpen.value = true;
};

// Обработка выбора пользователя
const handleUserSelect = (user) => {
    selectedUser.value = user;
    // Автоматически устанавливаем ближайшую дату дня рождения
    if (user.birth_date) {
        birthdayTaskDueDate.value = getNextBirthday(user.birth_date);
    }
    userSelectModalOpen.value = false;
};

// Очистка выбранного пользователя
const clearSelectedUser = () => {
    selectedUser.value = null;
    birthdayTaskDueDate.value = "";
};

// Форматирование даты
const formatDate = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('ru-RU', {
        day: 'numeric',
        month: 'long',
        year: 'numeric'
    });
};

// Валидация всей формы для сохранения
const isFormValidForSave = computed(() => {
    if (isBirthdayTask.value) {
        return selectedUser.value !== null && birthdayTaskDueDate.value.trim().length > 0;
    }

    const hasName = name.value.trim().length > 0;
    const hasAnySubtask = Object.values(tasks.value).some((task) => task.use);
    const hasSingleDeadline = !useSingleDeadline.value || singleDeadline.value.trim().length > 0;
    return hasName && hasAnySubtask && hasSingleDeadline;
});

// Получение toast для уведомлений
const { $toast } = useNuxtApp();

// Отправка задачи на сервер
const submitTask = async () => {
    if (!isFormValidForSave.value) {
        $toast.warning("Заполните все обязательные поля");
        return;
    }

    try {
        let task;

        if (isBirthdayTask.value) {
            if (!selectedUser.value) {
                $toast.warning("Выберите пользователя");
                return;
            }

            if (!birthdayTaskDueDate.value) {
                $toast.warning("Укажите дедлайн задачи");
                return;
            }

            task = await TasksService.createBirthdayTaskTasksBirthdayUserIdPost(
                selectedUser.value.id,
                birthdayTaskDueDate.value
            );
            $toast.success(`Задача на день рождения для ${useFullName(selectedUser.value)} создана`);
        } else {
            const payload = {
                name: name.value,
                use_in_pgas: useInPgas.value,
                birthday_user_id: null,
                birthday_date: null,
                typed_tasks: Object.entries(tasks.value).reduce((acc, [role, task]) => {
                    acc[role] = task.use
                        ? {
                              name: task.name,
                              description: task.description,
                              due_date: task.deadline,
                              for_single_user: task.for_single_user,
                              link: "",
                          }
                        : null;
                    return acc;
                }, {}),
            };

            task = await TasksService.createTaskTasksPost(payload);
            $toast.success("Задача успешно создана");
        }

        const router = useRouter();
        router.push({
            name: routesNames.tasksTaskId,
            params: { task_id: task.id },
        });
    } catch (error) {
        if (error.status === 422) {
            $toast.error("Ошибка валидации данных");
        } else if (error.status === 404) {
            $toast.error("Пользователь не найден");
        } else if (error.status === 409) {
            $toast.error("Задача на день рождения для этого пользователя уже существует");
        } else {
            $toast.error("Ошибка при создании задачи");
        }
        console.error("Error creating task:", error);
    }
};
</script>

<style scoped lang="scss">
.selected-user {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 12px;
    border-radius: 10px;
    border: 2px solid black;
    transition: border-color 0.2s;

    &:hover {
        border-color: black;
    }

    .user-info {
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex: 1;
        gap: 10px;
        min-width: 0;

        .user-details {
            display: flex;
            flex-direction: column;
            gap: 4px;
            min-width: 0;
            flex: 1;

            .name {
                font-size: 16px;
                font-weight: 500;
                color: $text-color-secondary;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
            }

            .birth-date {
                font-size: 14px;
                color: $text-color;
                opacity: 0.7;
            }
        }

        .badge {
            font-size: 14px;
            font-weight: 500;
            color: white;
            background-color: black;
            padding: 4px 12px;
            border-radius: 5px;
            white-space: nowrap;
        }
    }
}
</style>
