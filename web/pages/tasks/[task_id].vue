<template>
    <page-container :items="sections" full-height>
        <div class="task-card-container">
            <div class="task-card shadow-lg">
                <div class="head">
                    {{ task.event ? task.event.name : task.name }}
                </div>

                <template v-if="task.event">
                    <div class="badges">
                        <UBadge
                            color="neutral"
                            variant="outline"
                            size="lg"
                            icon="material-symbols:calendar-today"
                        >
                            {{ dateTextFormat(task.event.date) }}
                        </UBadge>
                        <UBadge
                            color="neutral"
                            variant="outline"
                            size="lg"
                            icon="material-symbols:nest-clock-farsight-analog-outline"
                        >
                            {{ getTime(task.event.start_time) }} -
                            {{ getTime(task.event.end_time) }}
                        </UBadge>
                        <UBadge
                            color="neutral"
                            variant="outline"
                            size="lg"
                            icon="material-symbols:location-on"
                        >
                            {{ task.event.location }}
                        </UBadge>
                        <UBadge
                            color="neutral"
                            variant="outline"
                            size="lg"
                            icon="material-symbols:hourglass-bottom"
                        >
                            {{ getWaitingTime(task.event) }}
                        </UBadge>
                    </div>
                    <div class="section" v-if="task.event.description">
                        <div class="section-head">Описание</div>
                        <div class="section-content">
                            {{ task.event.description }}
                        </div>
                    </div>

                    <div
                        class="section"
                        v-for="typed_task in typed_tasks"
                        :key="typed_task.id"
                    >
                        <div class="section-head">
                            {{ typedTasksLabels[typed_task.task_type] }}
                        </div>
                        <div class="section-content">
                            <div class="flex gap-1">
                                <app-button
                                    active
                                    mini
                                    v-if="
                                        showTakeInWorkButton &&
                                        !typed_task.has_my_state
                                    "
                                    class="w-full"
                                    @click="
                                        () => {
                                            selectedTypedTask = typed_task;
                                            setMeToTaskModalActive = true;
                                        }
                                    "
                                >
                                    Взять в работу
                                </app-button>
                                <app-button
                                    active
                                    mini
                                    class="w-full"
                                    v-else-if="typed_task.has_my_state"
                                    outline
                                    @click="
                                        () => {
                                            selectedTypedTask = typed_task;
                                            removeMeFromTaskModalActive = true;
                                        }
                                    "
                                >
                                    Отказаться от задачи
                                </app-button>
                                <app-button
                                    active
                                    mini
                                    class="w-full"
                                    v-if="authStore.isAdmin"
                                    @click="
                                        () => {
                                            selectedTypedTask = typed_task;
                                            selectUserModalActive = true;
                                        }
                                    "
                                >
                                    Назначить исполнителя
                                </app-button>
                            </div>
                            <div class="users">
                                <div
                                    class="user-item"
                                    v-for="status in typed_task.task_states"
                                    :key="status.user.id"
                                >
                                    <div class="user-item-info">
                                        <div class="name">
                                            {{ useFullName(status.user) }}
                                        </div>
                                        <div :class="['state', status.state]">
                                            <Icon
                                                name="material-symbols:check"
                                                v-if="
                                                    status.state === 'completed'
                                                "
                                            />
                                            <Icon
                                                name="material-symbols:hourglass-top"
                                                v-else-if="
                                                    status.state === 'pending'
                                                "
                                            />
                                            <Icon
                                                name="material-symbols:close-rounded"
                                                v-else
                                            />
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="section">
                        <div class="section-head">
                            Уровень мероприятия: {{ task.event.level }}
                        </div>
                    </div>
                </template>
            </div>
        </div>
    </page-container>

    <user-select-modal
        v-if="authStore.isAdmin && selectedTypedTask !== null"
        v-model:active="selectUserModalActive"
        :filter-role="selectedTypedTask.task_type"
        :exclude-users="excludeUsers"
        @select="
            (user) => setUserToTypedTask(user, selectedTypedTask.task_type)
        "
        exclude-user-badge-text="Уже назначен"
    />
    <UModal v-model:open="setMeToTaskModalActive" title="Взять в работу">
        <template #body>
            <div class="text-md">
                Вы уверены, что хотите взять в работу подзадачу
                {{ typedTasksLabelsModal[selectedTypedTask.task_type] }}?
            </div>
            <div class="grid grid-cols-2 gap-2 mt-4">
                <app-button
                    @click="
                        () =>
                            setUserToTypedTask(
                                authStore.userData,
                                selectedTypedTask.task_type
                            )
                    "
                    active
                >
                    Подтвердить
                </app-button>
                <app-button
                    @click="setMeToTaskModalActive = false"
                    class="cursor-pointer"
                >
                    Отмена
                </app-button>
            </div>
        </template>
    </UModal>
    <UModal
        v-model:open="removeMeFromTaskModalActive"
        title="Отказаться от задачи"
    >
        <template #body>
            <div class="text-md">
                Вы уверены, что хотите отказаться от подзадачи
                {{ typedTasksLabelsModal[selectedTypedTask.task_type] }}?
            </div>
            <div class="grid grid-cols-2 gap-2 mt-4">
                <app-button
                    active
                    red
                    @click="
                        () =>
                            removeUserFromTypedTask(
                                authStore.userData,
                                selectedTypedTask.task_type
                            )
                    "
                >
                    Подтвердить
                </app-button>
                <app-button
                    @click="removeMeFromTaskModalActive = false"
                    class="cursor-pointer"
                >
                    Отмена
                </app-button>
            </div>
        </template>
    </UModal>
</template>
<script setup>
import { routesNames } from "@typed-router";
import {
    TasksService,
    UserRole,
    TypedTasksService,
    TypedTasksStatesService,
} from "~/client";
import { useAuthStore } from "~/stores/auth";
definePageMeta({
    middleware: ["user"],
});
const authStore = useAuthStore();
const selectedTypedTask = ref(null);
const { task_id } = useRoute().params;
const task = ref(await TasksService.getTaskByIdTasksTaskIdGet(task_id));
const { $toast } = useNuxtApp();

useSeoMeta({
    title: task.value.event
        ? `Мероприятие: ${task.value.event.name}`
        : `Задача: ${task.value.name}`,
});
const excludeUsers = computed(() => {
    if (!selectedTypedTask.value) return [];

    for (const typed_task of task.value.typed_tasks) {
        if (typed_task.task_type === selectedTypedTask.value.task_type) {
            return typed_task.task_states.map((state) => state.user);
        }
    }
    return [];
});
const showTakeInWorkButton = computed(() => {
    const photographerTypedTask = task.value.typed_tasks.find(
        (typed_task) => typed_task.task_type === UserRole.PHOTOGRAPHER
    );
    if (
        photographerTypedTask &&
        task.value.event &&
        task.value.event.is_passed
    ) {
        return false;
    }
    return true;
});
const typedTasksCurrentUser = computed(() => {
    return task.value.typed_tasks.map((typed_task) => ({
        ...typed_task,
        has_my_state: typed_task.task_states.some(
            (state) => state.user.id === authStore.userData.id
        ),
    }));
});
const typed_tasks = computed(() => {
    if (authStore.isAdmin) {
        return typedTasksCurrentUser.value;
    }
    if (
        !showTakeInWorkButton.value &&
        typedTasksCurrentUser.value.some(
            (typed_task) => typed_task.has_my_state
        )
    ) {
        return [];
    }
    return typedTasksCurrentUser.value.filter(
        (typed_task) => typed_task.task_type in authStore.userData.roles
    );
});

const typedTasksLabels = {
    [UserRole.PHOTOGRAPHER]: "Фотографы",
    [UserRole.DESIGNER]: "Дизайнер",
    [UserRole.COPYWRITER]: "Копирайтер",
};
const typedTasksLabelsModal = {
    [UserRole.PHOTOGRAPHER]: "Фотографа",
    [UserRole.DESIGNER]: "Дизайнера",
    [UserRole.COPYWRITER]: "Копирайтера",
};
const selectUserModalActive = ref(false);
const setMeToTaskModalActive = ref(false);
const removeMeFromTaskModalActive = ref(false);
const stateMessages = {
    completed: "Завершено",
    pending: "Ожидает подтверждения",
    canceled: "Отклонено",
};
const sections = [
    {
        label: "Мероприятия и задачи",
        to: {
            name: routesNames.tasks,
        },
    },
    {
        label:
            task.value.name +
            (task.value.event ? ` (${task.value.event.name})` : ""),
        to: {
            name: routesNames.tasksTaskId,
            params: { task_id: task_id },
        },
    },
];
const dateTextFormat = (date) => {
    const options = { year: "numeric", month: "long", day: "numeric" };
    return new Date(date).toLocaleDateString(undefined, options);
};

const getTime = (time) => {
    if (!time) return "";
    const [hours, minutes] = time.split(":");
    return `${hours}:${minutes}`;
};
const setUserToTypedTask = async (user, task_type) => {
    if (!user || !task_type) return;
    const typed_task = task.value.typed_tasks.find(
        (tt) => tt.task_type === task_type
    );
    if (!typed_task) return;
    try {
        const task_state =
            await TypedTasksService.assignUserToTaskTasksTypedTasksTypedTaskIdUserUserIdPost(
                typed_task.id,
                user.id,
                { comment: "" }
            );

        selectUserModalActive.value = false;
        setMeToTaskModalActive.value = false;

        task.value.typed_tasks = task.value.typed_tasks.map((tt) => {
            if (tt.id === typed_task.id) {
                return {
                    ...tt,
                    task_states: [...tt.task_states, task_state],
                };
            }
            return tt;
        });
    } catch (error) {
        $toast.error(HandleOpenApiError(error).message);
        console.error(error);
    }
};
const removeUserFromTypedTask = async (user, task_type) => {
    if (!user || !task_type) return;
    const typed_task = task.value.typed_tasks.find(
        (tt) => tt.task_type === task_type
    );
    if (!typed_task) return;
    const state = typed_task.task_states.find(
        (state) => state.user.id === user.id
    );
    if (!state) return;
    try {
        await TypedTasksStatesService.deleteTypedTaskStateTasksTypedTasksStatesTypedTaskStateIdDelete(
            state.id
        );

        task.value.typed_tasks = task.value.typed_tasks.map((tt) => {
            if (tt.id === typed_task.id) {
                return {
                    ...tt,
                    task_states: tt.task_states.filter(
                        (state) => state.user.id !== user.id
                    ),
                };
            }
            return tt;
        });
    } catch (error) {
        $toast.error(HandleOpenApiError(error).message);
        console.error(error);
    }
    removeMeFromTaskModalActive.value = false;
};

const getWaitingTime = (event) => {
    if (!event) return "";
    const eventDate = new Date(event.date);
    const today = new Date();
    const diffTime = eventDate - today;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    if (diffDays > 0) {
        return `через ${diffDays} ${usePluralize(diffDays, [
            "день",
            "дня",
            "дней",
        ])}`;
    } else if (diffDays < 0) {
        return `${Math.abs(diffDays)} ${usePluralize(Math.abs(diffDays), [
            "день",
            "дня",
            "дней",
        ])} назад`;
    } else {
        return "Сегодня";
    }
};
</script>
<style scoped lang="scss">
.task-card-container {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100%;

    .task-card {
        width: 100%;
        max-width: 500px;
        border: 1px solid $border-color;
        border-radius: 8px;
        padding: 16px;
        display: flex;
        flex-direction: column;
        gap: 8px;
        .head {
            font-size: 1.5rem;
            color: $text-color;
        }
        .badges {
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
        }

        .section {
            display: flex;
            flex-direction: column;
            gap: 8px;
            .section-head {
                font-size: 14px;
                font-weight: bold;
                color: $text-color-secondary;
            }
            .section-content {
                color: $text-color-secondary;
                display: flex;
                flex-direction: column;
                gap: 8px;
                .users {
                    display: flex;
                    flex-direction: column;
                    .user-item {
                        display: flex;
                        align-items: center;
                        gap: 10px;
                        padding: 10px;
                        border-radius: 10px;
                        border: 1px solid $tertiary-bg;

                        cursor: pointer;
                        &:hover {
                            border-color: $text-color;
                        }

                        &.excluded {
                            cursor: not-allowed;
                        }
                        .user-item-info {
                            display: flex;
                            align-items: center;
                            justify-content: space-between;
                            width: 100%;
                            gap: 5px;
                            min-width: 0;

                            .name {
                                font-size: 16px;
                                color: $text-color-secondary;
                                white-space: nowrap;
                                overflow: hidden;
                                text-overflow: ellipsis;
                                max-width: 180px;
                                display: block;
                                text-align: center;
                            }
                            .state {
                                display: flex;
                                align-items: center;
                                justify-content: center;
                                width: 30px;
                                height: 30px;

                                gap: 5px;
                                border-radius: 10px;

                                &.completed {
                                    background-color: $accent-success;
                                    color: black;
                                }
                                &.pending {
                                    background-color: $accent-warning;
                                    color: black;
                                }
                                &.canceled {
                                    background-color: $accent-red;
                                    color: white;
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
</style>
