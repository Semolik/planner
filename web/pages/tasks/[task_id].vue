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
                                        <div
                                            class="period"
                                            v-if="status.period"
                                        >
                                            {{
                                                status.period.period_start
                                                    .split(":")
                                                    .slice(0, 2)
                                                    .join(":")
                                            }}
                                            -
                                            {{
                                                status.period.period_end
                                                    .split(":")
                                                    .slice(0, 2)
                                                    .join(":")
                                            }}
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
            (user) => {
                selectedUser = user;
                setMeToTaskModalActive = true;
            }
        "
        exclude-user-badge-text="Уже назначен"
    />

    <UModal
        v-model:open="setMeToTaskModalActive"
        title="Назначение задачи"
        v-if="selectedTypedTask"
    >
        <template #body>
            <div class="text-md mb-4">
                {{
                    isAssigningSelf
                        ? `Вы уверены, что хотите взять в работу подзадачу`
                        : `Вы уверены, что хотите назначить пользователя на подзадачу`
                }}
                {{ typedTasksLabelsModal[selectedTypedTask.task_type] }}?
                {{
                    isFullEventTime
                        ? ""
                        : `C ${minutesToTime(selectedRange[0])} до ${minutesToTime(selectedRange[1])}`
                }}
            </div>

            <div
                class="mb-4"
                v-if="selectedTypedTask.task_type === UserRole.PHOTOGRAPHER"
            >
                <USwitch
                    v-model="isFullEventTime"
                    label="На всё время мероприятия"
                    color="neutral"
                />
            </div>

            <TimeRangeSlider
                v-if="!isFullEventTime && task.event"
                v-model="selectedRange"
                :min-time="task.event.start_time"
                :max-time="task.event.end_time"
                :step="15"
            />

            <div class="grid grid-cols-2 gap-2 mt-4">
                <app-button
                    @click="submitAssignment"
                    :active="submitAssignmentButtonActive"
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
const selectedUser = ref(null);
const isFullEventTime = ref(true);

const { task_id } = useRoute().params;
const task = ref(await TasksService.getTaskByIdTasksTaskIdGet(task_id));
const selectedRange = ref(
    task.value.event
        ? [
              timeToMinutes(task.value.event.start_time),
              timeToMinutes(task.value.event.end_time),
          ]
        : [0, 0]
);
const { $toast } = useNuxtApp();

useSeoMeta({
    title: task.value.event
        ? `Мероприятие: ${task.value.event.name}`
        : `Задача: ${task.value.name}`,
});

const isAssigningSelf = computed(() => {
    return (
        selectedUser.value?.id === authStore.userData.id || !selectedUser.value
    );
});

const excludeUsers = computed(() => {
    if (!selectedTypedTask.value) return [];
    const typed_task = task.value.typed_tasks.find(
        (tt) => tt.task_type === selectedTypedTask.value.task_type
    );
    return typed_task?.task_states.map((state) => state.user) || [];
});

const showTakeInWorkButton = computed(() => {
    const photographerTypedTask = task.value.typed_tasks.find(
        (typed_task) => typed_task.task_type === UserRole.PHOTOGRAPHER
    );
    return !(
        photographerTypedTask &&
        task.value.event &&
        task.value.event.is_passed
    );
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

const submitAssignmentButtonActive = computed(() => {
    if (!isFullEventTime.value) {
        // время начала и конца должно быть выбрано (не совпадать с началом и концом мероприятия)
        if (
            selectedRange.value[0] ===
                timeToMinutes(task.value.event.start_time) &&
            selectedRange.value[1] === timeToMinutes(task.value.event.end_time)
        ) {
            return false;
        }
    }
    return true;
});
const submitAssignment = async () => {
    const user = isAssigningSelf.value
        ? authStore.userData
        : selectedUser.value;

    await setUserToTypedTask(user, selectedTypedTask.value.task_type);
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
                {
                    comment: "",
                }
            );
        if (!isFullEventTime.value) {
            task_state.period = {
                period_start: minutesToTime(selectedRange.value[0]) + ":00",
                period_end: minutesToTime(selectedRange.value[1]) + ":00",
            };
            await TypedTasksStatesService.createTypedTaskStatePeriodTasksTypedTasksStatesTypedTaskStateIdPeriodPut(
                task_state.id,
                task_state.period
            );
        }
        selectUserModalActive.value = false;
        setMeToTaskModalActive.value = false;
        selectedUser.value = null;
        isFullEventTime.value = true;

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

    const state = typed_task.task_states.find((s) => s.user.id === user.id);

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
                        (s) => s.user.id !== user.id
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
function timeToMinutes(timeStr) {
    const [hours, minutes] = timeStr.split(":").map(Number);
    return hours * 60 + minutes;
}

function minutesToTime(minutes) {
    const h = Math.floor(minutes / 60);
    const m = minutes % 60;
    return `${h.toString().padStart(2, "0")}:${m.toString().padStart(2, "0")}`;
}
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

                            width: 100%;
                            gap: 5px;
                            min-width: 0;
                            .name {
                                font-size: 16px;
                                color: $text-color-secondary;
                                margin-right: auto;
                                white-space: nowrap;
                                overflow: hidden;
                                text-overflow: ellipsis;
                                max-width: 180px;
                                display: block;
                                text-align: center;
                            }
                            .period {
                                font-size: 14px;
                                background-color: black;
                                color: white;
                                padding: 2px 10px;
                                border-radius: 10px;
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
