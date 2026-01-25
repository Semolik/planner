<template>
    <page-container header="Статистика">
        <div class="flex-1 md:divide-accented w-full">
            <div class="flex md:items-center gap-2 min-h-[60px] overflow-x-auto px-2 head md:flex-row flex-col-reverse justify-between">
                <div class="text-lg font-semibold">Статистика {{ user?.last_name }} {{ user?.first_name }}</div>
                <div class="flex gap-2">
                    <app-button
                        v-if="isOwnProfile"
                         mini
                         outline

                        :to="{
                            name: routesNames.usersUserIdAchievements,
                            params: {
                                user_id: props.userId
                            },
                        }"
                        >
                        ПГАС
                    </app-button>
                <app-button
                    v-if="isOwnProfile"
                    :to="`/users/${props.userId}`"
                    mini
                    outline
                    class="text-sm whitespace-nowrap"
                >
                    Перейти в профиль
                </app-button>
                    </div>
            </div>

            <div class="space-y-4 p-4">
                <!-- Селектор периода -->
                <div class="flex gap-2 max-w-2xl flex-wrap">
                    <app-button
                        v-for="period in periods"
                        :key="period.id"
                        active
                        :outline="!period.active"
                        mini
                        class="flex-1 justify-between whitespace-nowrap max-w-[300px]"
                        @click="selectedPeriod = period"
                    >
                        <span class="text-sm">
                            {{ formatPeriod(period) }}
                        </span>
                    </app-button>
                </div>

                <!-- Бейджи с требованиями -->
                <div v-if="formattedRequirements.length > 0" class="flex gap-2 flex-wrap items-center">
                    <span class="text-sm font-medium" :style="{ color: textColorTertiary }">Требуется:</span>
                    <UBadge
                        v-for="req in formattedRequirements"
                        :key="req.role"
                        color="neutral"
                        size="md"
                    >
                        {{ req.label }}: {{ req.count }}
                    </UBadge>
                </div>
            </div>

            <!-- 🔥 КРУГОВЫЕ ДИАГРАММЫ ПО ТИПАМ ЗАДАЧ -->
            <div v-if="shouldShowChart" class="px-4 py-4">
                <h3 class="text-lg font-semibold mb-4">Выполнено задач по типам</h3>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div
                        v-for="item in progressItems"
                        :key="item.role"
                        class="rounded-lg border p-4 flex flex-col items-center"
                        :style="{
                            backgroundColor: primaryBg,
                            borderColor: borderColor
                        }"
                    >
                        <ClientOnly>
                            <div style="width: 150px; height: 150px;">
                                <VChart
                                    :option="getChartOption(item)"
                                    :style="{ width: '100%', height: '100%' }"
                                    autoresize
                                />
                            </div>
                        </ClientOnly>
                        <div class="text-center mt-2">
                            <h4 class="text-sm font-semibold" :style="{ color: textColor }">
                                {{ item.label }}
                            </h4>
                            <p class="text-xs mt-1" :style="{ color: textColorTertiary }">
                                {{ item.required > 0 ? (item.count + '/' + item.required) : item.count }}
                            </p>
                            <p
                                class="text-xs font-semibold mt-1"
                                :style="{ color: item.required > 0 ? (item.count >= item.required ? accentSuccess : accentRed) : textColorTertiary }"
                            >
                                {{ item.status }}
                            </p>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 🔥 ТАБЛИЦА ФОТОГРАФА -->
            <div v-if="hasRole('photographer')" class="px-4 mt-8">
                <h3 class="text-lg font-semibold mb-4">Выполненные задачи фотографа</h3>
            </div>

            <div v-if="hasRole('photographer')" ref="tableContainer" class="overflow-auto">
                <UTable
                    :columns="getColumnsForRole('photographer')"
                    :data="getTasksForRole('photographer')"
                    empty="Нет выполненных задач"
                    :ui="{
                        root: 'min-w-full',
                        td: 'empty:p-0'
                    }"
                    sticky
                />
            </div>

            <!-- 🔥 ТАБЛИЦА КОПИРАЙТЕРА -->
            <div v-if="hasRole('copywriter')" class="px-4 mt-8">
                <h3 class="text-lg font-semibold mb-4">Выполненные задачи копирайтера</h3>
            </div>

            <div v-if="hasRole('copywriter')" ref="tableContainer2" class="overflow-auto">
                <UTable
                    :columns="getColumnsForRole('copywriter')"
                    :data="getTasksForRole('copywriter')"
                    empty="Нет выполненных задач"
                    :ui="{
                        root: 'min-w-full',
                        td: 'empty:p-0'
                    }"
                    sticky
                />
            </div>

            <!-- 🔥 ТАБЛИЦА ДИЗАЙНЕРА -->
            <div v-if="hasRole('designer')" class="px-4 mt-8">
                <h3 class="text-lg font-semibold mb-4">Выполненные задачи дизайнера</h3>
            </div>

            <div v-if="hasRole('designer')" ref="tableContainer3" class="overflow-auto">
                <UTable
                    :columns="getColumnsForRole('designer')"
                    :data="getTasksForRole('designer')"
                    empty="Нет выполненных задач"
                    :ui="{
                        root: 'min-w-full',
                        td: 'empty:p-0'
                    }"
                    sticky
                />
            </div>
        </div>
    </page-container>
</template>

<script setup lang="ts">
import { StatisticsService, RequiredPeriodsService, UsersService } from "@/client";
import { resolveComponent, ref, computed, watch, h } from 'vue';
import type { TableColumn } from "@nuxt/ui";
import { useAuthStore } from "@/stores/auth";
import { use } from 'echarts/core';
import { PieChart } from 'echarts/charts';
import { TooltipComponent } from 'echarts/components';
import { CanvasRenderer } from 'echarts/renderers';
import { routesNames } from "@typed-router";
import VChart from 'vue-echarts';

use([PieChart, TooltipComponent, CanvasRenderer]);

const props = defineProps<{
    userId: string;
}>();

const router = useRouter();
const authStore = useAuthStore();
const UBadge = resolveComponent("UBadge");

// 🔥 ЦВЕТА ИЗ SASS
const primaryBg = 'rgb(255, 255, 255)';
const secondaryBg = 'rgb(245, 245, 245)';
const textColor = 'rgb(0, 0, 0)';
const textColorSecondary = 'rgb(51, 51, 51)';
const textColorTertiary = 'rgb(100, 100, 100)';
const borderColor = 'rgba(0, 0, 0, 0.075)';
const accentRed = 'hsl(0, 100%, 60%)';
const accentSuccess = 'hsl(153, 80%, 60%)';

const isOwnProfile = computed(() => {
    // Приводим к any, чтобы избежать ошибок типов от store (локальное безопасное приведение)
    const id = (authStore.userData as any)?.id;
    return (id != null && String(id) === props.userId) || !!authStore.isAdmin;
});

// Данные пользователя
const user = ref<any>(null);

// Загрузка пользователя
const loadUser = async () => {
    try {
        user.value = await UsersService.getUserUsersUserIdGet(props.userId);
    } catch (error) {
        console.error("Ошибка загрузки пользователя:", error);
        router.push({ name: "index" });
    }
};

// Периоды (загружаются в setup)
const periodsRaw = await RequiredPeriodsService.getRequiredPeriodsRequiredPeriodsGet();
const selectedPeriod = ref(periodsRaw[0]);
const periods = computed(() => periodsRaw.map(p => ({
    ...p,
    active: selectedPeriod.value && p.id === selectedPeriod.value.id
})));

// Данные статистики
const statsData = ref<any>(null);
const tasksData = ref<any[]>([]);
const tasksLoading = ref(false);
const tableContainer = ref(null);

// 🔥 ЗАГРУЗКА ДАННЫХ С ПЕРЕДАЧЕЙ ID ПЕРИОДА
const loadData = async () => {
    if (!selectedPeriod.value) {
        statsData.value = null;
        tasksData.value = [];
        return;
    }

    tasksLoading.value = true;
    try {
        const [stats, tasks] = await Promise.all([
            StatisticsService.getUserStatisticsStatisticsUserIdGet(props.userId, selectedPeriod.value.id),
            UsersService.getUserCompletedTypedTasksUsersUserIdTypedTasksCompletedGet(props.userId, selectedPeriod.value.id)
        ]);

        statsData.value = stats;
        tasksData.value = tasks;
    } catch (error) {
        console.error("Ошибка загрузки данных:", error);
    } finally {
        tasksLoading.value = false;
    }
};

watch(selectedPeriod, loadData, { immediate: true });

onMounted(() => {
    loadUser();
});

// ФОРМАТИРОВАНИЕ
const monthNamesGenitive = [
    "января", "февраля", "марта", "апреля", "мая", "июня",
    "июля", "августа", "сентября", "октября", "ноября", "декабря"
];

const formatDate = (isoDate: string, showYear = false): string => {
    if (!isoDate) return "";
    const parts = String(isoDate).split("-");
    if (parts.length !== 3) return isoDate;
    const [year, month, day] = parts;
    const m = parseInt(month, 10) - 1;
    const dd = String(parseInt(day, 10));
    const monthName = monthNamesGenitive[m] || month;
    return showYear ? `${dd} ${monthName} ${year}` : `${dd} ${monthName}`;
};

const formatPeriod = (period: any): string => {
    const start = period.period_start;
    const end = period.period_end;
    const startYear = start ? String(start).split("-")[0] : null;
    const endYear = end ? String(end).split("-")[0] : null;
    const currentYear = String(new Date().getFullYear());
    const showYear =
        startYear !== endYear || startYear !== currentYear || endYear !== currentYear;
    return `${formatDate(start, showYear)} - ${formatDate(end, showYear)}`;
};

// ТРЕБОВАНИЯ
const requiredTasksMap = computed(() => {
    if (!selectedPeriod.value?.roles_config) return {};
    const map: Record<string, number> = {};
    selectedPeriod.value.roles_config.forEach((config: any) => {
        map[config.user_role] = config.count;
    });
    return map;
});

// ✅ ПРОВЕРКА НАЛИЧИЯ РОЛИ
const hasRole = (role: string): boolean => {
    // Проверяем роли пользователя
    const userHasRole = user.value?.roles?.includes(role) || false;

    // Проверяем наличие выполненных задач
    const hasCompletedTasks = taskStats.value[role as keyof typeof taskStats.value] > 0;

    return userHasRole || hasCompletedTasks;
};

const formattedRequirements = computed(() => {
    if (!selectedPeriod.value?.roles_config) return [];

    const roleLabels: Record<string, string> = {
        photographer: 'Фотограф',
        copywriter: 'Копирайтер',
        designer: 'Дизайнер'
    };

    return selectedPeriod.value.roles_config.map((config: any) => ({
        label: roleLabels[config.user_role] || config.user_role,
        count: config.count,
        role: config.user_role
    }));
});

// СТАТИСТИКА ПО ТИПАМ
const taskStats = computed(() => {
    const stats = {
        photographer: 0,
        copywriter: 0,
        designer: 0
    };

    if (!statsData.value?.stats) return stats;

    Object.values(statsData.value.stats).forEach((month: any) => {
        stats.photographer += month.photographer || 0;
        stats.copywriter += month.copywriter || 0;
        stats.designer += month.designer || 0;
    });

    return stats;
});

// 🔥 PIE CHARTS - КРУГОВЫЕ ДИАГРАММЫ
const chartColors = {
    photographer: '#2182A6',
    copywriter: null,
    designer: null
};

const roleLabels: Record<string, string> = {
    photographer: 'Фотограф',
    copywriter: 'Копирайтер',
    designer: 'Дизайнер'
};

const progressItems = computed(() => {
    const base = [
        { role: 'photographer', label: roleLabels.photographer, color: chartColors.photographer, count: taskStats.value.photographer },
        { role: 'copywriter', label: roleLabels.copywriter, color: null, count: taskStats.value.copywriter },
        { role: 'designer', label: roleLabels.designer, color: null, count: taskStats.value.designer }
    ];

    return base
        .map(item => {
            const userHasRole = !!user.value?.roles?.includes(item.role);
            const required = userHasRole ? (requiredTasksMap.value[item.role] || 0) : 0;
            const percentage = required ? Math.min(100, Math.round((item.count / required) * 100)) : 0;
            let status = '';

            if (required > 0) {
                status = item.count >= required ? '✓ Выполнено' : `Не хватает ${required - item.count}`;
            } else {
                // Если требования нет для пользователя (нет роли) — не показываем "Не хватает"
                status = item.count > 0 ? `${item.count} выполнено` : '';
            }

            // Определяем цвет: если нет требования — нейтральный цвет, иначе успех/ошибка
            const statusColor = required > 0
                ? (item.count >= required ? accentSuccess : accentRed)
                : textColorTertiary;

            return {
                ...item,
                required,
                percentage,
                status,
                statusColor
            };
        })
        .filter(item => hasRole(item.role));
});

const getChartOption = (item: any) => ({
    tooltip: {
        show: false
    },
    series: [
        {
            name: item.label,
            type: 'pie',
            radius: ['45%', '60%'],
            avoidLabelOverlap: false,
            itemStyle: {
                borderRadius: 0,
                borderColor: primaryBg,
                borderWidth: 2
            },
            label: {
                show: false
            },
            emphasis: {
                label: {
                    show: false
                },
                itemStyle: {
                    shadowBlur: 0,
                    shadowColor: 'transparent'
                }
            },
            labelLine: {
                show: false
            },
            hoverOffset: 0,
            data: [
                {
                    value: item.percentage,
                    name: 'Выполнено',
                    itemStyle: {
                        color: item.color,
                        opacity: 1
                    }
                },
                {
                    value: 100 - item.percentage,
                    name: 'Осталось',
                    itemStyle: {
                        color: 'rgb(215, 215, 215)',
                        opacity: 1
                    }
                }
            ]
        }
    ]
});

const shouldShowChart = computed(() => {
    return Object.values(requiredTasksMap.value).some(req => (req as number) > 0);
});

// ТАБЛИЦА
const stateLabels: Record<string, string> = {
    pending: 'В ожидании',
    completed: 'Завершено',
    canceled: 'Отменено'
};

// ✅ ФУНКЦИЯ ДЛЯ ПОЛУЧЕНИЯ ЗАДАЧ ПО РОЛИ
const getTasksForRole = (role: string) => {
    return tasksData.value
        .filter(task => task.task_type === role)
        .map(task => {
            const displayDate = task.parent_task?.event?.date || task.due_date;

            return {
                id: task.id,
                name: task.displayed_name || task.description || 'Без названия',
                dueDate: displayDate,
                link: task.link,
                lastState: task.task_states?.[task.task_states.length - 1] || null,
                parentTaskId: task.parent_task?.id
            };
        });
};

// ✅ ФУНКЦИЯ ДЛЯ ПОЛУЧЕНИЯ КОЛОНОК
const getColumnsForRole = (role: string): TableColumn<any>[] => {
    return [
        {
            accessorKey: 'name',
            header: 'Название мероприятия/задачи',
            cell: ({ row }) => row.original.name
        },
        {
            accessorKey: 'dueDate',
            header: 'Дата',
            cell: ({ row }) => formatDate(row.original.dueDate)
        },
        {
            id: 'state',
            header: 'Статус',
            cell: ({ row }) => {
                const state = row.original.lastState?.state;
                return state ? stateLabels[state] || state : 'Неизвестно';
            }
        },
        {
            id: 'actions',
            header: '',
            cell: ({ row }) => {
                return h('div', { class: 'flex justify-end' }, [
                    h(resolveComponent('app-button'), {
                        mini: true,
                        active: true,
                        to: `/tasks/${row.original.parentTaskId}`,
                        class: 'whitespace-nowrap'
                    }, {
                        default: () => 'Открыть'
                    })
                ]);
            }
        }
    ];
};
</script>

<style scoped lang="scss">
.head {
    @include md {
        border-bottom: 1px solid rgba(0, 0, 0, 0.075);
    }
}
</style>
