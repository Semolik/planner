<template>
    <app-form full-height headline="Создание задачи">
        <div class="flex flex-col gap-2" v-auto-animate>
            <app-input v-model="name" label="Название задачи" required white />

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

        <app-button :active="isFormValidForSave" @click="submitTask">
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
                />
                <app-input
                    v-model="form.description"
                    label="Описание подзадачи"
                    type="textarea"
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
</template>

<script setup>
import { UserRole, TasksService } from "~/client";
import { routesNames } from "@typed-router";

definePageMeta({ middleware: ["admin"] });

const name = ref("");

const labels = {
    [UserRole.PHOTOGRAPHER]: ["Фотографы", "фотографов"],
    [UserRole.COPYWRITER]: ["Копирайтеры", "копирайтеров"],
    [UserRole.DESIGNER]: ["Дизайнеры", "дизайнеров"],
};

const tasks = ref({
    [UserRole.PHOTOGRAPHER]: createEmptyTask(),
    [UserRole.COPYWRITER]: createEmptyTask(),
    [UserRole.DESIGNER]: createEmptyTask(),
});

function createEmptyTask() {
    return {
        use: false,
        description: "",
        deadline: "",
        for_single_user: false,
    };
}

const form = ref({
    description: "",
    dueDate: "",
    forSingleUser: false,
});

const modalOpen = ref(false);
const currentRole = ref(null);

const formValid = computed(() => Boolean(form.value.dueDate));

const openModal = (role) => {
    currentRole.value = role;
    const task = tasks.value[role];

    form.value = {
        description: task.description,
        dueDate: task.deadline,
        forSingleUser: task.for_single_user,
    };
    modalOpen.value = true;
};

const submitModal = () => {
    if (!formValid.value) return;

    const task = tasks.value[currentRole.value];

    task.use = true;
    task.description = form.value.description;
    task.deadline = form.value.dueDate;
    task.for_single_user = form.value.forSingleUser;

    modalOpen.value = false;
};

const clearTask = (role) => {
    tasks.value[role] = createEmptyTask();
};

const taskButtonText = (roleName, isUsed) =>
    isUsed ? `Подзадача для ${roleName}` : `Создать подзадачу для ${roleName}`;

const isFormValidForSave = computed(() => {
    const hasName = name.value.trim().length > 0;
    const hasAnySubtask = Object.values(tasks.value).some((task) => task.use);
    return hasName && hasAnySubtask;
});
const { $toast } = useNuxtApp();

const submitTask = async () => {
    const payload = {
        name: name.value,
        typed_tasks: Object.entries(tasks.value).reduce((acc, [role, task]) => {
            acc[role] = task.use
                ? {
                      description: task.description,
                      due_date: task.deadline,
                      for_single_user: task.for_single_user,
                      link: "",
                  }
                : null;
            return acc;
        }, {}),
    };
    try {
        const task = await TasksService.createTaskTasksPost(payload);
        const router = useRouter();
        $toast.success("Задача успешно создана");
        router.push({
            name: routesNames.tasksTaskId,
            params: { task_id: task.id },
        });
    } catch (error) {
        $toast.error("Ошибка при создании мероприятия");
        console.error("Error creating task:", error);
    }
};
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
                .label {
                    margin-left: 10px;
                    margin-bottom: 4px;
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
                    }
                }
                .actions {
                    display: flex;
                    gap: 8px;
                    .button {
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        width: 35px;
                        height: 35px;
                        border-radius: 10px;
                        background-color: black;
                        cursor: pointer;
                        .iconify {
                            width: 20px;
                            height: 20px;
                            color: white;
                        }
                    }
                }
            }
        }
    }
}
</style>
