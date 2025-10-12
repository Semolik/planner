<script setup>
import {StatisticsService, RequiredPeriodsService} from "@/client";

const periodsRaw = await RequiredPeriodsService.getRequiredPeriodsRequiredPeriodsGet();
const selectedPeriod = ref(periodsRaw[0]);
const periods = computed(() => periodsRaw.map(p => ({
    ...p,
    active: selectedPeriod.value && p.id === selectedPeriod.value.id
})));
const UButton = resolveComponent("UButton");



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

watch(selectedPeriod, loadData, {immediate: true});

const monthNames = [
    "Январь",
    "Февраль",
    "Март",
    "Апрель",
    "Май",
    "Июнь",
    "Июль",
    "Август",
    "Сентябрь",
    "Октябрь",
    "Ноябрь",
    "Декабрь",
];

const monthNamesGenitive = [
    "января",
    "февраля",
    "марта",
    "апреля",
    "мая",
    "июня",
    "июля",
    "августа",
    "сентября",
    "октября",
    "ноября",
    "декабря",
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
    ].sort();
});



const sortField = ref("fullName");
const sortDirection = ref("asc");
const tableData = computed(() => {
    let data = rawData.value.map((user) => {
        const row = {
            fullName: `${user.user.last_name} ${user.user.first_name}`,
            lastName: user.user.last_name,
        };
        let total = 0;
        allMonths.value.forEach(function (month) {
            const value = user.stats?.[month] ?? 0;
            row[`month_${month}`] = value === 0 ? "-" : value;
            total += value;
        });
        row.total = total;
        return row;
    });

    if (sortField.value) {
        data.sort((a, b) => {
            const aValue = a[sortField.value];
            const bValue = b[sortField.value];
            if (aValue < bValue) return sortDirection.value === "asc" ? -1 : 1;
            if (aValue > bValue) return sortDirection.value === "asc" ? 1 : -1;
            return 0;
        });
    }

    return data;
});

const createSortableHeader = (title, field) => {
    return ({column}) => {
        const isActive = sortField.value === field;
        const isAsc = sortDirection.value === "asc";
        return h(UButton, {
            color: "neutral",
            variant: "ghost",
            label: title,
            icon: isActive
                ? isAsc
                    ? "material-symbols:arrow-upward"
                    : "material-symbols:arrow-downward"
                : "material-symbols:swap-vert",
            class: "-mx-2.5",
            onClick: () => {
                if (sortField.value === field) {
                    sortDirection.value =
                        sortDirection.value === "asc" ? "desc" : "asc";
                } else {
                    sortField.value = field;
                    sortDirection.value = "asc";
                }
            },
        });
    };
};

const columns = computed(() => {
    return [
        {
            accessorKey: "fullName",
            header: createSortableHeader("ФИО", "fullName"),
        },
        ...allMonths.value.map((month) => ({
            accessorKey: `month_${month}`,
            header: monthNames[parseInt(month) - 1],
            align: "center",
        })),
        {
            accessorKey: "total",
            header: createSortableHeader("Итого", "total"),
            align: "center",
        },
    ];
});
</script>

<template>
    <div class="flex gap-2 max-w-2xl flex-wrap mb-4">
        <app-button v-for="period in periods" active :outline="!period.active" @click="selectedPeriod = period" :key="period.id" class="flex-1 justify-between whitespace-nowrap min-w-[200px]">
            <span class="text-sm">
                  {{ formatPeriod(period) }}
            </span>
        </app-button>
    </div>

    <UTable v-if="!loading" :columns="columns" :data="tableData"/>
    <p v-else>Загрузка данных...</p>
</template>
