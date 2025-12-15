<template>
    <div class="typed-tasks">
        <div class="task-roles">
            <div v-for="(label, role) in labels" :key="role" class="task-role">
                <UAlert
                    v-if="isRoleDisabledByAggregation(role)"
                    color="amber"
                    variant="outline"
                    icon="material-symbols:warning"
                    :title="label[0]"
                    :description="getDisabledMessage(role)"
                />
                <div v-else class="header">
                    <div v-if="typedTasks[role]" class="badges">
                        <div class="badge">
                            дедлайн {{ typedTasks[role].due_date_string }}
                        </div>
                        <div
                            v-if="typedTasks[role].task_states.length > 0"
                            class="badge"
                        >
                            {{ typedTasks[role].task_states.length }}
                            {{
                                usePluralize(
                                    typedTasks[role].task_states.length,
                                    [
                                        "исполнитель",
                                        "исполнителя",
                                        "исполнителей",
                                    ]
                                )
                            }}
                        </div>
                    </div>
                    <div class="actions">
                        <div
                            v-if="!!typedTasks[role]"
                            class="button"
                            @click="openEditModal(typedTasks[role])"
                        >
                            <Icon name="material-symbols:edit" />
                        </div>
                        <div
                            v-if="!!typedTasks[role]"
                            class="button remove"
                            @click="
                                () => {
                                    typedTaskToRemove = typedTasks[role];
                                    removeModalOpened = true;
                                }
                            "
                        >
                            <Icon name="material-symbols:delete" />
                        </div>
                        <div
                            v-else
                            class="button"
                            @click="openCreateModal(role)"
                        >
                            <Icon name="material-symbols:add" />
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <UModal
        v-if="typedTaskToRemove"
        v-model:open="removeModalOpened"
        :title="`Удалить подзадачу ${labels[typedTaskToRemove.task_type][1]}`"
    >
        <template #body>
            <div class="text-md">
                Вы действительно хотите удалить подзадачу
                {{ labels[typedTaskToRemove.task_type][1] }}? При этом она будет
                снята с исполнителей.
            </div>
            <div class="grid grid-cols-2 gap-2 mt-4">
                <app-button
                    active
                    red
                    @click="deleteTypedTask(typedTaskToRemove.task_type)"
                >
                    Подтвердить
                </app-button>
                <app-button @click="removeModalOpened = false">
                    Отмена
                </app-button>
            </div>
        </template>
    </UModal>

    <UModal
        v-if="currentEditRole"
        v-model:open="editModalOpened"
        :title="`${isEditing ? 'Подзадача' : 'Создать подзадачу для'}  ${
            labels[currentEditRole][1]
        }`"
    >
        <template #body>
            <div class="flex flex-col gap-2">
                <UCheckbox
                    v-model="form.forSingleUser"
                    label="Для одного исполнителя"
                    color="neutral"
                    variant="card"
                />
                <app-input
                    v-model="form.name"
                    label="Название подзадачи"
                    placeholder="Например: Обложка на альбом"
                />
                <app-input
                    v-model="form.dueDate"
                    label="Срок выполнения подзадачи"
                    type="date"
                    :min="task.event ? task.event.date : ''"
                />
                <app-input
                    v-model="form.description"
                    label="Описание подзадачи"
                    type="textarea"
                />

                <app-button
                    :active="formValid"
                    :disabled="!formValid"
                    @click="isEditing ? updateTypedTask() : createTypedTask()"
                >
                    {{ isEditing ? "Сохранить" : "Создать" }}
                </app-button>
            </div>
        </template>
    </UModal>
</template>

<script setup>
import { UserRole, TypedTasksService, TasksService } from "~/client";
import { useAppSettingsStore } from "~/stores/app-settings";

const appSettingsStore = useAppSettingsStore();
const task = inject("task");
const emit = defineEmits(["update:task"]);

const labels = {
    [UserRole.PHOTOGRAPHER]: ["Фотографы", "фотографов"],
    [UserRole.COPYWRITER]: task.value.event
        ? ["Копирайтер", "копирайтера"]
        : ["Копирайтеры", "копирайтеров"],
    [UserRole.DESIGNER]: task.value.event
        ? ["Дизайнер", "дизайнера"]
        : ["Дизайнеры", "дизайнеров"],
};

const isRoleDisabledByAggregation = (role) => {
    const hasAggregateTask = task.value.event?.group?.aggregate_task;
    return hasAggregateTask && (role === UserRole.COPYWRITER || role === UserRole.DESIGNER);
};

const getDisabledMessage = (role) => {
    if (role === UserRole.COPYWRITER) {
        return 'Задача управляется через агрегированную публикацию для всей группы мероприятий';
    } else if (role === UserRole.DESIGNER) {
        return 'Задача управляется через агрегированную публикацию для всей группы мероприятий';
    }
    return '';
};

const typedTasks = computed(() => {
    return Object.keys(labels).reduce((acc, role) => {
        const filtered = task.value.typed_tasks
            .filter((t) => t.task_type === role)
            .map((t) => ({
                ...t,
                due_date_string: t.due_date
                    ? new Date(t.due_date).toLocaleDateString("ru-RU", {
                          year: "numeric",
                          month: "2-digit",
                          day: "2-digit",
                      })
                    : "",
            }));
        acc[role] = filtered.length > 0 ? filtered[0] : null;
        return acc;
    }, {});
});

const editModalOpened = ref(false);
const removeModalOpened = ref(false);
const typedTaskToRemove = ref(null);

const currentEditRole = ref(null);
const isEditing = ref(false);
const currentTypedTask = ref(null);

const form = ref({
    name: "",
    description: "",
    dueDate: "",
    forSingleUser: false,
});

const initialFormState = ref({});

watch([() => editModalOpened.value, currentEditRole], ([isOpen, role]) => {
    if (!isOpen) return;

    form.value = {
        name: "",
        description: "",
        dueDate: "",
        forSingleUser: false,
    };

    if (isEditing.value && currentTypedTask.value) {
        form.value.name = currentTypedTask.value.name || "";
        form.value.description = currentTypedTask.value.description || "";
        form.value.dueDate = currentTypedTask.value
            ? currentTypedTask.value.due_date.split("T")[0]
            : "";
        form.value.forSingleUser =
            currentTypedTask.value.for_single_user || false;
    }

    initialFormState.value = { ...form.value };

    if (role && task.value.event && !isEditing.value) {
        const date = task.value.event.date;
        switch (role) {
            case UserRole.PHOTOGRAPHER:
                form.value.dueDate = addDaysToDate(
                    date,
                    appSettingsStore.settings.photographers_deadline
                );
                form.value.forSingleUser = false;
                form.value.name = "Сдача репортажа";
                break;
            case UserRole.COPYWRITER:
                form.value.dueDate = addDaysToDate(
                    date,
                    appSettingsStore.settings.copywriters_deadline
                );
                form.value.forSingleUser = true;
                form.value.name = task.value.event ? `Текст публикации к мероприятию "${task.value.event.name}"` : "Текст публикации";
                break;
            case UserRole.DESIGNER:
                form.value.dueDate = addDaysToDate(
                    date,
                    appSettingsStore.settings.photographers_deadline +
                        appSettingsStore.settings.designers_deadline
                );
                form.value.forSingleUser = false;
                form.value.name = task.value.event ? `Обложка на альбом "${task.value.event.name}"` : "Обложка на альбом";
                break;
        }
    }
});

const hasFormChanged = computed(() => {
    return (
        form.value.name !== initialFormState.value.name ||
        form.value.description !== initialFormState.value.description ||
        form.value.dueDate !== initialFormState.value.dueDate ||
        form.value.forSingleUser !== initialFormState.value.forSingleUser
    );
});

const formValid = computed(() => {
    const isValidDueDate = form.value.dueDate !== "";
    const isValidName = form.value.name.trim().length > 0;
    return isEditing.value
        ? isValidDueDate && isValidName && hasFormChanged.value
        : isValidDueDate && isValidName;
});

function openCreateModal(role) {
    currentEditRole.value = role;
    isEditing.value = false;
    currentTypedTask.value = null;
    if (role === UserRole.PHOTOGRAPHER && task.value.event) {
        form.value.forSingleUser = false;
    } else {
        form.value.forSingleUser = true;
    }
    editModalOpened.value = true;
}

function openEditModal(typedTask) {
    currentTypedTask.value = typedTask;
    currentEditRole.value = typedTask.task_type;
    isEditing.value = true;
    editModalOpened.value = true;
}

async function createTypedTask() {
    try {
        const response =
            await TasksService.createTypedTaskTasksTaskIdTypedTasksPost(
                task.value.id,
                {
                    task_type: currentEditRole.value,
                    name: form.value.name,
                    description: form.value.description,
                    link: "",
                    for_single_user: form.value.forSingleUser,
                    due_date: form.value.dueDate,
                }
            );

        emit("update:task", {
            ...task.value,
            typed_tasks: [...task.value.typed_tasks, response],
        });

        editModalOpened.value = false;
    } catch (e) {
        console.error(e);
        $toast.error(HandleOpenApiError(e).message);
    }
}

async function updateTypedTask() {
    try {
        const updatedTask =
            await TypedTasksService.updateTypedTaskTasksTypedTasksTypedTaskIdPut(
                currentTypedTask.value.id,
                {
                    name: form.value.name,
                    description: form.value.description,
                    link: "",
                    for_single_user: form.value.forSingleUser,
                    due_date: form.value.dueDate,
                }
            );

        const newTypedTasks = task.value.typed_tasks.map((t) =>
            t.id === updatedTask.id ? updatedTask : t
        );

        emit("update:task", {
            ...task.value,
            typed_tasks: newTypedTasks,
        });

        editModalOpened.value = false;
    } catch (e) {
        console.error(e);
        $toast.error(HandleOpenApiError(e).message);
    }
}

async function deleteTypedTask(role) {
    const target = typedTasks.value[role];
    try {
        await TypedTasksService.deleteTypedTaskTasksTypedTasksTypedTaskIdDelete(
            target.id
        );

        emit("update:task", {
            ...task.value,
            typed_tasks: task.value.typed_tasks.filter(
                (t) => t.task_type !== role
            ),
        });

        removeModalOpened.value = false;
        typedTaskToRemove.value = null;
    } catch (e) {
        console.error(e);
        $toast.error(HandleOpenApiError(e).message);
    }
}
</script>

<style scoped lang="scss">
.typed-tasks {
    .task-roles {
        display: flex;
        flex-direction: column;
        gap: 10px;

        .task-role {
            border: 1px solid $text-color;
            padding: 8px;
            border-radius: 10px;
            display: flex;
            flex-direction: column;
            gap: 10px;

            .header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                gap: 10px;
                @include md(true) {
                    flex-direction: column;
                    gap: 5px;
                }
                .label {
                    margin-left: 10px;
                }
                .badges {
                    display: flex;
                    gap: 8px;
                    width: 100%;

                    .badge {
                        padding: 0px 10px;
                        background-color: black;
                        color: white;
                        border-radius: 10px;
                        font-size: 14px;
                        @include md(true) {
                            padding: 5px 10px;
                            flex-grow: 1;
                            text-align: center;
                        }
                    }
                }
                .actions {
                    display: flex;
                    gap: 8px;
                    @include md(true) {
                        width: 100%;
                    }
                    .button {
                        display: flex;
                        align-items: center;
                        justify-content: center;

                        border-radius: 10px;
                        background-color: black;
                        height: 35px;
                        cursor: pointer;
                        @include md {
                            width: 35px;
                        }
                        @include md(true) {
                            flex-grow: 1;
                        }
                        .iconify {
                            width: 20px;
                            height: 20px;
                            color: white;
                        }

                        &.remove {
                            background-color: $accent-red;
                            .iconify {
                                color: black;
                            }
                            &:hover {
                                background-color: $accent-red-hover;
                            }
                        }
                    }
                }
            }
        }
    }
}
</style>
