<script setup>
import { StatisticsService, RequiredPeriodsService } from "@/client";
import { h, resolveComponent } from 'vue';
import { getGroupedRowModel } from '@tanstack/vue-table';

const periodsRaw = await RequiredPeriodsService.getRequiredPeriodsRequiredPeriodsGet();
const selectedPeriod = ref(periodsRaw[0]);
const periods = computed(() => periodsRaw.map(p => ({
    ...p,
    active: selectedPeriod.value && p.id === selectedPeriod.value.id
})));
const UButton = resolveComponent("UButton");
const UBadge = resolveComponent("UBadge");

const rawData = ref([]);
const loading = ref(false);

const loadData = async () => {
    if (!selectedPeriod.value) {
        rawData.value = [];
        return;
    }
    loading.value = true;
    try {
        const data = await StatisticsService.getStatisticsStatisticsGet(
            selectedPeriod.value.id
        );
        rawData.value = data;
    } catch (error) {
        console.error("Ошибка при загрузке статистики:", error);
    } finally {
        loading.value = false;
    }
};

watch(selectedPeriod, loadData, { immediate: true });

const monthNames = [
    "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
    "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"
];

const monthNamesGenitive = [
    "января", "февраля", "марта", "апреля", "мая", "июня",
    "июля", "августа", "сентября", "октября", "ноября", "декабря"
];

const formatDate = (isoDate, showYear = false) => {
    if (!isoDate) return "";
    const parts = String(isoDate).split("-");
    if (parts.length !== 3) return isoDate;
    const [year, month, day] = parts;
    const m = parseInt(month, 10) - 1;
    const dd = String(parseInt(day, 10));
    const monthName = monthNamesGenitive[m] || monthNames[m] || month;
    return showYear ? `${dd} ${monthName} ${year}` : `${dd} ${monthName}`;
};

const formatPeriod = (period) => {
    const start = period.period_start;
    const end = period.period_end;
    const startYear = start ? String(start).split("-")[0] : null;
    const endYear = end ? String(end).split("-")[0] : null;
    const currentYear = String(new Date().getFullYear());
    const showYear =
        startYear !== endYear || startYear !== currentYear || endYear !== currentYear;
    return `${formatDate(start, showYear)} - ${formatDate(end, showYear)}`;
};

const allMonths = computed(() => {
    return [
        ...new Set(rawData.value.flatMap((u) => Object.keys(u.stats || {}))),
    ].sort((a, b) => parseInt(a) - parseInt(b));
});

// Маппинг требуемого количества задач по ролям
const requiredTasksMap = computed(() => {
    if (!selectedPeriod.value?.roles_config) return {};
    const map = {};
    selectedPeriod.value.roles_config.forEach(config => {
        map[config.user_role] = config.count;
    });
    return map;
});

// Форматированные требования для отображения в бейджах
const formattedRequirements = computed(() => {
    if (!selectedPeriod.value?.roles_config) return [];

    const roleLabels = {
        photographer: 'Фотограф',
        copywriter: 'Копирайтер',
        designer: 'Дизайнер'
    };

    return selectedPeriod.value.roles_config.map(config => ({
        label: roleLabels[config.user_role] || config.user_role,
        count: config.count,
        role: config.user_role
    }));
});

// Преобразуем данные в плоскую структуру
const tableData = computed(() => {
    const data = [];

    rawData.value.forEach((user) => {
        const userId = user.user.id;
        const fullName = `${user.user.last_name} ${user.user.first_name}`;

        // Создаем строки для каждого типа активности
        ['photographer', 'copywriter', 'designer'].forEach((activityType) => {
            const row = {
                id: `${userId}_${activityType}`,
                user_id: userId,
                fullName: fullName,
                activityType: activityType
            };

            allMonths.value.forEach((month) => {
                const value = user.stats?.[month]?.[activityType] || 0;
                row[`month_${month}`] = value === 0 ? "-" : value;
            });

            row.total = allMonths.value.reduce((sum, month) => {
                const val = row[`month_${month}`];
                return sum + (val === "-" ? 0 : val);
            }, 0);

            data.push(row);
        });
    });

    return data;
});

const activityTypeLabels = {
    photographer: 'Фотограф',
    copywriter: 'Копирайтер',
    designer: 'Дизайнер'
};

// Проверка, достаточно ли выполнено задач
const isTaskCountSufficient = (activityType, total) => {
    const required = requiredTasksMap.value[activityType] || 0;
    return total >= required;
};

const columns = computed(() => {
    return [
        {
            id: 'title',
            header: 'ФИО / Тип активности'
        },
        {
            id: 'user_id',
            accessorKey: 'user_id'
        },
        ...allMonths.value.map((month) => ({
            accessorKey: `month_${month}`,
            header: monthNames[parseInt(month) - 1],
            cell: ({ row }) => {
                if (row.getIsGrouped()) {
                    return '';
                }
                return row.getValue(`month_${month}`);
            },
            aggregatedCell: ({ getValue }) => {
                const value = getValue();
                return value === 0 || value === '-' ? '-' : value;
            },
            aggregationFn: (columnId, leafRows) => {
                const sum = leafRows.reduce((total, row) => {
                    const val = row.getValue(columnId);
                    return total + (val === "-" ? 0 : val);
                }, 0);
                return sum;
            },
            meta: {
                class: {
                    th: 'text-center',
                    td: 'text-center'
                }
            }
        })),
        {
            accessorKey: 'total',
            header: 'Итого',
            cell: ({ row }) => {
                if (row.getIsGrouped()) {
                    return '';
                }
                return row.getValue('total');
            },
            aggregatedCell: ({ getValue }) => {
                return getValue();
            },
            aggregationFn: 'sum',
            meta: {
                class: {
                    th: 'text-center',
                    td: 'text-center font-semibold'
                }
            }
        }
    ];
});

// Настройки группировки
const groupingOptions = ref({
    groupedColumnMode: 'remove',
    getGroupedRowModel: getGroupedRowModel()
});
</script>

<template>
    <div class="space-y-4">
        <!-- Селектор периода -->
        <div class="flex gap-2 max-w-2xl flex-wrap">
            <app-button
                v-for="period in periods"
                :key="period.id"
                active
                :outline="!period.active"
                @click="selectedPeriod = period"
                class="flex-1 justify-between whitespace-nowrap min-w-[200px]"
            >
                <span class="text-sm">
                    {{ formatPeriod(period) }}
                </span>
            </app-button>
        </div>

        <!-- Бейджи с минимальными требованиями -->
        <div v-if="formattedRequirements.length > 0" class="flex gap-2 flex-wrap items-center">
            <span class="text-sm text-gray-600 font-medium">Минимум задач:</span>
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

    <UTable
        v-if="!loading"
        :columns="columns"
        :data="tableData"
        :grouping="['user_id']"
        :grouping-options="groupingOptions"
        :ui="{
            root: 'min-w-full',
            td: 'empty:p-0'
        }"
        class="mt-4"
    >
        <template #title-cell="{ row }">
            <div v-if="row.getIsGrouped()" class="flex items-center">
                <UButton
                    variant="ghost"
                    color="neutral"
                    class="mr-2"
                    size="xs"
                    :icon="row.getIsExpanded() ? 'i-lucide-chevron-down' : 'i-lucide-chevron-right'"
                    @click="row.toggleExpanded()"
                />
                <strong>{{ row.original.fullName }}</strong>
            </div>
            <div v-else class="ml-8 text-gray-600">
                {{ activityTypeLabels[row.original.activityType] }}
            </div>
        </template>

        <!-- Слоты для отображения агрегированных значений в ячейках месяцев -->
        <template v-for="month in allMonths" :key="`month_${month}`" #[`month_${month}-cell`]="{ row }">
            <div v-if="row.getIsGrouped()" class="text-center font-semibold">
                {{ row.getValue(`month_${month}`) === 0 ? '-' : row.getValue(`month_${month}`) }}
            </div>
            <div v-else class="text-center">
                {{ row.getValue(`month_${month}`) }}
            </div>
        </template>

        <!-- Слот для колонки "Итого" с условной подсветкой -->
        <template #total-cell="{ row }">
            <div v-if="row.getIsGrouped()" class="text-center font-semibold">
                {{ row.getValue('total') }}
            </div>
            <div
                v-else
                class="text-center font-semibold"
                :class="{
                    'bg-red-100 text-red-700': !isTaskCountSufficient(row.original.activityType, row.getValue('total')),
                    'bg-green-100 text-green-700': isTaskCountSufficient(row.original.activityType, row.getValue('total'))
                }"
            >
                {{ row.getValue('total') }}
            </div>
        </template>
    </UTable>
    <p v-else>Загрузка данных...</p>
</template>
