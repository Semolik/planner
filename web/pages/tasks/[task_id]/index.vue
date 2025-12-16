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
                            v-if="task.event.start_time || task.event.end_time"
                            color="neutral"
                            variant="outline"
                            size="lg"
                            icon="material-symbols:nest-clock-farsight-analog-outline"
                        >
                            {{ getTimeRange(task.event.start_time, task.event.end_time) }}
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
                        <UBadge
                            v-if="task.event.group"
                            color="info"
                            size="lg"
                            class="cursor-pointer"
                            icon="material-symbols:folder"
                            @click="
                                () =>
                                    $router.push({
                                        name: routesNames.eventsGroupsGroupId,
                                        params: {
                                            group_id: task.event.group.id,
                                        },
                                    })
                            "
                        >
                            {{ task.event.group.name }}
                        </UBadge>
                        <UBadge
                            v-if="task.event.group?.link"
                            color="neutral"
                            icon="material-symbols:link"
                            size="lg"
                            as="a"
                            :href="task.event.group.link"
                            rel="noopener noreferrer"
                            target="_blank"
                        >
                            Пост группы
                        </UBadge>
                        <UBadge
                            v-if="task.event.link"
                            color="neutral"
                            icon="material-symbols:link"
                            size="lg"
                            as="a"
                            :href="task.event.link"
                            rel="noopener noreferrer"
                            target="_blank"
                        >
                            Пост
                        </UBadge>
                        <UBadge
                            v-if="!task.use_in_pgas"
                            color="neutral"
                            variant="outline"
                            size="lg"
                            icon="material-symbols:warning"
                        >
                            Не учитывается в ПГАС
                        </UBadge>
                    </div>
                    <div v-if="task.event.group?.description" class="section">
                        <div class="section-head">
                            Описание группы мероприятий
                        </div>
                        <div class="section-content">
                            {{ task.event.group.description }}
                        </div>
                    </div>
                    <div v-if="task.event.description" class="section">
                        <div class="section-head">Описание</div>
                        <div class="section-content">
                            {{ task.event.description }}
                        </div>
                    </div>
                    <div
                        v-if="
                            task.event.organizer || task.event.group?.organizer
                        "
                        class="section"
                    >
                        <div class="section-head">Контакт организатора</div>
                        <div class="section-content">
                            <div class="flex gap-2">
                                <app-input
                                    disabled
                                    :model-value="
                                        task.event.organizer ||
                                        task.event.group?.organizer
                                    "
                                    white
                                />
                                <div class="copy" @click="copyOrganizerContact">
                                    <Icon
                                        name="material-symbols:content-copy"
                                    />
                                </div>
                            </div>
                        </div>
                    </div>
                </template>
                <div v-else-if="task.group" class="badges">
                    <UBadge
                        color="info"
                        size="lg"
                        class="cursor-pointer"
                        icon="material-symbols:folder"
                        @click="
                            () =>
                                $router.push({
                                    name: routesNames.eventsGroupsGroupId,
                                    params: { group_id: task.group.id },
                                })
                        "
                    >
                        {{ task.group.name }}
                    </UBadge>
                    <!-- Если у группы есть ссылка на пост — показываем бейдж-ссылку -->
                    <UBadge
                        v-if="task.group.link"
                        color="neutral"
                        icon="material-symbols:link"
                        size="lg"
                        as="a"
                        :href="task.group.link"
                        rel="noopener noreferrer"
                        target="_blank"
                    >
                        Пост группы
                    </UBadge>
                    <!-- Если ссылки нет — подсказка и переход в редактор группы -->
                    <UBadge
                        v-else
                        color="neutral"
                        variant="outline"
                        size="lg"
                        icon="material-symbols:edit"
                        class="cursor-pointer"
                        @click="() => $router.push({ name: routesNames.eventsGroupsGroupId, params: { group_id: task.group.id }, query: { edit: '1' } })"
                    >
                        Указать ссылку в редакторе группы
                    </UBadge>
                    <!-- Кнопка-редактирование: всегда доступна рядом -->
                    <UBadge
                        color="neutral"
                        size="lg"
                        icon="material-symbols:open_in_new"
                        class="cursor-pointer"
                        @click="() => $router.push({ name: routesNames.eventsGroupsGroupId, params: { group_id: task.group.id } })"
                    >
                        Открыть группу
                    </UBadge>
                </div>
                <div v-if="task.event?.group?.aggregate_task" class="section">
                    <UAlert
                        color="neutral"
                        variant="outline"
                        icon="material-symbols:folder"
                        title="Одна публикация на несколько мероприятий"
                        :description="`Это мероприятие входит в группу мероприятий «${task.event.group.name}», для которой создана общая задача публикации.`"
                        class="border border-dashed"
                        :actions="[
                            {
                          label: 'Перейти к задаче публикации',
                          color: 'neutral',
                          variant: 'subtle',
                          to: {
                              name: routesNames.tasksTaskId,
                              params: {
                                  task_id: task.event.group.aggregate_task.id,
                              },
                          },
                        }
                        ]"
                    />
                </div>

                <div
                    v-for="typed_task in typed_tasks"
                    :key="typed_task.id"
                    class="section"
                >
                    <div class="section-head">
                        <div class="flex justify-between items-center">
                            <span
                                >{{ typedTasksLabels[typed_task.task_type] }}
                            </span>
                            <span
                                v-if="showTypedTaskDeadlineString(typed_task)"
                                class="text-sm font-normal"
                                :class="getTypedTaskDeadlineClass(typed_task)"
                            >
                                Дедлайн
                                {{ getTypedTaskDeadline(typed_task) }}
                            </span>
                        </div>
                    </div>

                    <div class="section-content">
                        <div
                            v-if="typed_task.description"
                            class="section-description"
                        >
                            {{ typed_task.description }}
                        </div>
                       <div :class="['gap-2', authStore.isAdmin ? 'grid md:grid-cols-2 grid-cols-1' : 'flex flex-col md:flex-row md:flex-wrap']">
                            <app-button
                                v-if="
                                    showTakeInWorkButton &&
                                    !typed_task.has_my_state
                                "
                                active
                                :mini="$viewport.isGreaterThan('md')"
                                class="w-full"
                                @click="
                                    () => {
                                        selectedTypedTask = typed_task;
                                        selectedUser = userData;
                                        setMeToTaskModalActive = true;
                                    }
                                "
                            >
                                Взять в работу
                            </app-button>
                            <app-button
                                v-else-if="typed_task.has_my_state"
                                active
                                :mini="$viewport.isGreaterThan('md')"
                                class="w-full"
                                outline
                                @click="
                                    () => {
                                        selectedUser = userData;
                                        selectedTypedTask = typed_task;
                                        removeMeFromTaskModalActive = true;
                                    }
                                "
                            >
                                Отказаться от задачи
                            </app-button>
                            <app-button
                                v-if="authStore.isAdmin"
                                active
                                :mini="$viewport.isGreaterThan('md')"
                                class="w-full"
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

                        <div v-auto-animate class="users">
                            <div
                                v-for="status in typed_task.task_states"
                                :key="status.user.id"
                                class="user-item"
                                @click="() => openStateModal(status)"
                            >
                                <div class="user-item-info">
                                    <div class="name">
                                        {{ useFullName(status.user) }}
                                    </div>
                                    <div v-if="status.period" class="period">
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
                                            v-if="
                                                status.state === State.COMPLETED
                                            "
                                            name="material-symbols:check"
                                        />
                                        <Icon
                                            v-else-if="
                                                status.state === State.PENDING
                                            "
                                            name="material-symbols:hourglass-top"
                                        />
                                        <Icon
                                            v-else
                                            name="material-symbols:close-rounded"
                                        />
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div v-if="task.event" class="section">
                    <div class="section-head">
                        Уровень мероприятия: {{ task.event.level }}
                    </div>
                </div>

                <div
                    v-if="authStore.isAdmin"
                    class="grid grid-cols-2 gap-2 mt-auto"
                >
                    <app-button
                        active
                        :mini="$viewport.isGreaterThan('md')"
                        :to="{
                            name: routesNames.tasksTaskIdEdit.index,
                            params: { task_id: task.id },
                        }"
                    >
                        Редактировать
                    </app-button>
                    <app-button
                        active
                        red
                        :mini="$viewport.isGreaterThan('md')"
                        @click="deleteModalOpened = true"
                    >
                        Удалить
                    </app-button>
                </div>
            </div>
        </div>
    </page-container>

    <user-select-modal
        v-if="authStore.isAdmin && selectedTypedTask !== null"
        v-model:active="selectUserModalActive"
        :filter-role="selectedTypedTask.task_type"
        :exclude-users="excludeUsers"
        exclude-user-badge-text="Уже назначен"
        @select="
            (user) => {
                selectedUser = user;
                setMeToTaskModalActive = true;
            }
        "
    />

    <UModal
        v-if="selectedTypedTask"
        v-model:open="setMeToTaskModalActive"
        title="Назначение задачи"
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
            <template
                v-if="
                    selectedTypedTask.task_type === UserRole.PHOTOGRAPHER &&
                    hasEventTimeRange
                "
            >
                <div class="mb-4">
                    <USwitch
                        v-model="isFullEventTime"
                        label="На всё время мероприятия"
                        color="neutral"
                    />
                </div>

                <TimeRangeSlider
                    v-if="!isFullEventTime"
                    v-model="selectedRange"
                    :min-time="task.event.start_time"
                    :max-time="task.event.end_time"
                    :step="15"
                    @change="resetIfFillPeriod"
                />
            </template>

            <div class="grid grid-cols-2 gap-2 mt-4">
                <app-button
                    :active="submitAssignmentButtonActive"
                    @click="
                        async () => {
                            await setUserToTypedTask(
                                selectedUser,
                                selectedTypedTask.task_type
                            );
                        }
                    "
                >
                    Подтвердить
                </app-button>
                <app-button
                    class="cursor-pointer"
                    @click="setMeToTaskModalActive = false"
                >
                    Отмена
                </app-button>
            </div>
        </template>
    </UModal>
    <UModal
        v-model:open="removeMeFromTaskModalActive"
        :title="
            isAssigningSelf ? 'Отказаться от подзадачи' : 'Снять с подзадачи'
        "
    >
        <template #body>
            <div class="text-md">
                {{
                    isAssigningSelf
                        ? `Вы уверены, что хотите отказаться от подзадачи`
                        : `Вы уверены, что хотите снять пользователя ${useFullName(
                              selectedUser
                          )} с подзадачи`
                }}
                {{ typedTasksLabelsModal[selectedTypedTask.task_type] }}?
            </div>
            <div class="grid grid-cols-2 gap-2 mt-4">
                <app-button
                    active
                    red
                    @click="
                        () =>
                            removeUserFromTypedTask(
                                selectedUser,
                                selectedTypedTask.task_type
                            )
                    "
                >
                    Подтвердить
                </app-button>
                <app-button
                    class="cursor-pointer"
                    @click="removeMeFromTaskModalActive = false"
                >
                    Отмена
                </app-button>
            </div>
        </template>
    </UModal>
    <UModal v-model:open="stateModalOpened" title="Статус подзадачи">
        <template v-if="selectedState" #body>
            <div class="flex flex-col gap-2">
                <div class="text-md">
                    <strong>Пользователь:</strong>
                    {{ useFullName(selectedState.user) }}
                </div>

                <template
                    v-if="
                        selectedState.user.id === userData.id ||
                        authStore.isAdmin
                    "
                >
                    <div class="flex flex-col gap-1">
                        <strong>Период:</strong>
                        <UTabs
                            v-if="
                                getStateType(selectedState) ===
                                UserRole.PHOTOGRAPHER &&
                                hasEventTimeRange
                            "
                            :model-value="isFullEventTime ? 'full' : 'period'"
                            :content="false"
                            :items="[
                                {
                                    label: 'На всё время мероприятия',
                                    value: 'full',
                                },
                                { label: 'Выбрать период', value: 'period' },
                            ]"
                            color="neutral"
                            @update:model-value="
                                (value) => {
                                    isFullEventTime = value === 'full';
                                }
                            "
                        />
                    </div>

                    <TimeRangeSlider
                        v-if="!isFullEventTime && hasEventTimeRange"
                        v-model="selectedRange"
                        :min-time="task.event.start_time"
                        :max-time="task.event.end_time"
                        :step="15"
                        @change="resetIfFillPeriod"
                    />
                    <div class="flex flex-col gap-1">
                        <strong>Статус:</strong>
                        <UTabs
                            v-model="selectedStateEditable.state"
                            :items="stateTabs"
                            color="neutral"
                            :content="false"
                        />
                    </div>
                </template>
                <template v-else>
                    <div class="text-md">
                        <strong>Статус:</strong>
                        {{ statusLabels[selectedState.state] }}
                    </div>
                </template>
                <app-button
                    v-if="
                        authStore.isAdmin ||
                        selectedState.user.id === userData.id
                        "
                    :active="updateStateButtonActive"
                    @click="updateState"
                >
                    Обновить статус
                </app-button>
                <app-button
                    v-if="
                        authStore.isAdmin ||
                        selectedState.user.id === userData.id
                    "
                    active
                    @click="() => showDeleteStateModal(selectedState)"
                >
                    {{
                        selectedState.user.id === userData.id
                            ? "Отказаться от задачи"
                            : "Снять с задачи"
                    }}
                </app-button>
            </div>
        </template>
    </UModal>
    <UModal
        v-model:open="deleteModalOpened"
        :title="`Удалить ${task.event ? 'мероприятие' : 'задачу'}`"
    >
        <template #body>
            <div class="text-md">
                Вы действительно хотите удалить
                {{ task.event ? "мероприятие" : "задачу" }} "{{
                    task.event ? task.event.name : task.name
                }}"?
            </div>
            <div class="grid grid-cols-2 gap-2 mt-4">
                <app-button active red @click="deleteTask">
                    Подтвердить
                </app-button>
                <app-button
                    class="cursor-pointer"
                    @click="deleteModalOpened = false"
                >
                    Отмена
                </app-button>
            </div>
        </template>
    </UModal>
</template>

<script setup>
import { routesNames } from "@typed-router";
import copy from "copy-to-clipboard";
import {
    TasksService,
    UserRole,
    TypedTasksService,
    TypedTasksStatesService,
    State,
} from "~/client";
import { useAuthStore } from "~/stores/auth";

const authStore = useAuthStore();
const { userData } = storeToRefs(authStore);
const selectedTypedTask = ref(null);
const selectedUser = ref(null);
const isFullEventTime = ref(true);

const { task_id } = useRoute().params;
const task = ref(await TasksService.getTaskByIdTasksTaskIdGet(task_id));

const hasEventTimeRange = computed(() => {
    return task.value.event?.start_time && task.value.event?.end_time;
});

const selectedRange = ref(
    hasEventTimeRange.value
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
    return selectedUser.value?.id === userData.value?.id;
});
const stateModalOpened = ref(false);
const selectedState = ref(null);
const selectedStateEditable = ref(null);
const openStateModal = (state) => {
    selectedState.value = state;
    selectedStateEditable.value = { ...state };
    stateModalOpened.value = true;
    if (state.period) {
        selectedRange.value = [
            timeToMinutes(state.period.period_start),
            timeToMinutes(state.period.period_end),
        ];
        isFullEventTime.value = false;
    }
};
const updateState = async () => {
    if (!selectedState.value) return;

    try {
        if (isFullEventTime.value) {
            if (selectedState.value.period) {
                await TypedTasksStatesService.deleteTypedTaskStatePeriodTasksTypedTasksStatesTypedTaskStateIdPeriodDelete(
                    selectedState.value.id
                );
            }
        } else {
            await TypedTasksStatesService.createTypedTaskStatePeriodTasksTypedTasksStatesTypedTaskStateIdPeriodPut(
                selectedState.value.id,
                {
                    period_start: minutesToTime(selectedRange.value[0]) + ":00",
                    period_end: minutesToTime(selectedRange.value[1]) + ":00",
                }
            );
        }
        selectedState.value =
            await TypedTasksStatesService.updateUserTypedTaskStateTasksTypedTasksStatesTypedTaskStateIdPut(
                selectedState.value.id,
                {
                    state: selectedStateEditable.value.state,
                    comment: "",
                }
            );
        task.value.typed_tasks = task.value.typed_tasks.map((tt) => {
            if (tt.task_type === getStateType(selectedState.value)) {
                return {
                    ...tt,
                    task_states: tt.task_states.map((s) =>
                        s.id === selectedState.value.id
                            ? selectedState.value
                            : s
                    ),
                };
            }
            return tt;
        });
        stateModalOpened.value = false;
    } catch (error) {
        $toast.error(HandleOpenApiError(error).message);
        return;
    }
};
watch(
    isFullEventTime,
    (newValue) => {
        if (!hasEventTimeRange.value) return;
        if (newValue) {
            selectedRange.value = [
                timeToMinutes(task.value.event.start_time),
                timeToMinutes(task.value.event.end_time),
            ];
        }
    },
    {
        immediate: true,
    }
);
const resetIfFillPeriod = () => {
    if (!hasEventTimeRange.value) return;
    if (
        selectedRange.value[0] === timeToMinutes(task.value.event.start_time) &&
        selectedRange.value[1] === timeToMinutes(task.value.event.end_time)
    ) {
        isFullEventTime.value = true;
    }
};
const updateStateButtonActive = computed(() => {
    if (!selectedState.value) return false;

    const current = selectedState.value;
    const editable = selectedStateEditable.value;

    if (editable.state !== current.state) return true;

    const hadPeriod = !!current.period;
    const hasPeriod = !isFullEventTime.value;

    if (
        hasPeriod &&
        hasEventTimeRange.value &&
        selectedRange.value[0] === timeToMinutes(task.value.event.start_time) &&
        selectedRange.value[1] === timeToMinutes(task.value.event.end_time)
    ) {
        return false;
    }
    if (hadPeriod !== hasPeriod) {
        return true;
    }
    if (hasPeriod && hadPeriod) {
        const currentStart = timeToMinutes(current.period.period_start);
        const currentEnd = timeToMinutes(current.period.period_end);

        return (
            selectedRange.value[0] !== currentStart ||
            selectedRange.value[1] !== currentEnd
        );
    }

    return false;
});
const excludeUsers = computed(() => {
    if (!selectedTypedTask.value) return [];
    const typed_task = task.value.typed_tasks.find(
        (tt) => tt.task_type === selectedTypedTask.value.task_type
    );
    return typed_task?.task_states.map((state) => state.user) || [];
});
const getStateType = (state) => {
    if (state.task_type) {
        return state.task_type;
    }
    return task.value.typed_tasks.find((tt) =>
        tt.task_states.some((s) => s.id === state.id)
    )?.task_type;
};
const showTakeInWorkButton = computed(() => task.value.event ? task.value.event.has_assigned_photographers: true);
const typedTasksCurrentUser = computed(() => {
    return task.value.typed_tasks.map((typed_task) => ({
        ...typed_task,
        has_my_state: typed_task.task_states.some(
            (state) => state.user.id === userData.value?.id
        ),
    }));
});

const typed_tasks = computed(() => {
    const roleOrder = [
        UserRole.PHOTOGRAPHER,
        UserRole.COPYWRITER,
        UserRole.DESIGNER,
    ];

    let filteredTasks;

    if (authStore.isAdmin) {
        filteredTasks = typedTasksCurrentUser.value;
    } else {
        if (
            !showTakeInWorkButton.value
        ) {
            return [];
        }
        filteredTasks = typedTasksCurrentUser.value.filter(
            (typed_task) => userData.value.roles.includes(typed_task.task_type)
        );
    }

    return filteredTasks.sort((a, b) => {
        const aIndex = roleOrder.indexOf(a.task_type);
        const bIndex = roleOrder.indexOf(b.task_type);
        return aIndex - bIndex;
    });
});

const typedTasksLabels = computed(() => {
    const labels = {};
    for (const typed_task of task.value.typed_tasks) {
        const role = typed_task.task_type;
        labels[role] = typed_task.for_single_user
            ? {
                  [UserRole.PHOTOGRAPHER]: "Фотограф",
                  [UserRole.DESIGNER]: "Дизайнер",
                  [UserRole.COPYWRITER]: "Копирайтер",
              }[role]
            : {
                  [UserRole.PHOTOGRAPHER]: "Фотографы",
                  [UserRole.DESIGNER]: "Дизайнеры",
                  [UserRole.COPYWRITER]: "Копирайтеры",
              }[role];
    }
    return labels;
});

const typedTasksLabelsModal = {
    [UserRole.PHOTOGRAPHER]: "Фотографа",
    [UserRole.DESIGNER]: "Дизайнера",
    [UserRole.COPYWRITER]: "Копирайтера",
};
const statusLabels = {
    [State.CANCELED]: "Отменено",
    [State.PENDING]: "В работе",
    [State.COMPLETED]: "Выполнено",
};
const stateTabs = Object.entries(statusLabels).map(([key, label]) => ({
    label,
    value: key,
}));

const selectUserModalActive = ref(false);
const setMeToTaskModalActive = ref(false);
const removeMeFromTaskModalActive = ref(false);
const deleteModalOpened = ref(false);
const showDeleteStateModal = (selectedState) => {
    stateModalOpened.value = false;
    selectedTypedTask.value = task.value.typed_tasks.find((tt) =>
        tt.task_states.some((s) => s.id === selectedState.id)
    );
    selectedUser.value = selectedState.user;
    removeMeFromTaskModalActive.value = true;
};

const submitAssignmentButtonActive = computed(() => {
    if (!isFullEventTime.value && hasEventTimeRange.value) {
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
        if (
            !isFullEventTime.value &&
            typed_task.task_type === UserRole.PHOTOGRAPHER
        ) {
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
const getTimeDiff = (date) => {
    const eventDate = new Date(date);
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
const getWaitingTime = (event) => {
    if (!event) return "";
    return getTimeDiff(event.date);
};
const getTypedTaskDeadline = (typed_task) => {
    return getTimeDiff(typed_task.due_date);
};
const getTypedTaskDeadlineClass = (typed_task) => {
    const diff = new Date(typed_task.due_date) - new Date();
    if (diff < 0) return "text-red-500";
    if (diff < 24 * 60 * 60 * 1000) return "text-yellow-500";
    return "text-gray-500";
};
const deleteTask = async () => {
    try {
        await TasksService.deleteTaskTasksTaskIdDelete(task_id);
        useRouter().push({ name: routesNames.tasks });
    } catch (e) {
        $toast.error(HandleOpenApiError(e).message);
    }
};
const showTypedTaskDeadlineString = (typed_task) => {
    return (
        typed_task.task_states.length === 0 ||
        !typed_task.task_states.every(
            (state) =>
                state.state === State.COMPLETED ||
                state.state === State.CANCELED
        )
    );
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
    return new Date(date).toLocaleDateString("ru-RU", options);
};

const getTime = (time) => {
    if (!time) return "";
    const [hours, minutes] = time.split(":");
    return `${hours}:${minutes}`;
};

const getTimeRange = (startTime, endTime) => {
    const start = getTime(startTime);
    const end = getTime(endTime);
    if (start && end) return `${start} - ${end}`;
    if (start) return `с ${start}`;
    if (end) return `до ${end}`;
    return "";
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
const copyOrganizerContact = () => {
    if (!task.value.event) return;
    const contact =
        task.value.event.organizer || task.value.event.group?.organizer;
    if (contact) {
        try {
            copy(contact);
            $toast.success("Контакт организатора скопирован в буфер обмена");
        } catch (error) {
            $toast.error("Ошибка при копировании контакта организатора");
        }
    } else {
        $toast.error("Контакт организатора не указан");
    }
};
</script>

<style scoped lang="scss">
.task-card-container {
    display: flex;

    height: 100%;

    @include lg {
        justify-content: center;
        align-items: center;
        .task-card {
            max-width: 600px;
        }
    }
    .task-card {
        width: 100%;

        display: flex;
        flex-direction: column;
        gap: 8px;
        @include lg {
            border: 1px solid $border-color;
            border-radius: 8px;
            padding: 16px;
        }
        .copy {
            height: 40px;
            width: 40px;
            background-color: black;
            margin-top: auto;
            border-radius: 8px;
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;

            &:hover {
                background-color: $text-color-secondary;
            }
        }
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

                .section-description {
                    font-size: 14px;
                    color: $text-color-secondary;
                }

                .users {
                    display: flex;
                    flex-direction: column;
                    gap: 8px;
                    &:empty {
                        display: none;
                    }
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
