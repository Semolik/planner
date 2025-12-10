<template>
    <div class="relative w-full">
        <apexchart
            type="donut"
            :options="chartOptions"
            :series="series"
            :height="height"
        />
        <div v-if="$slots.default" class="absolute inset-0 flex items-center justify-center pointer-events-none">
            <slot />
        </div>
    </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';

interface CategoryItem {
    name: string;
    color: string;
}

const props = withDefaults(defineProps<{
    data: number[];
    height?: number | string;
    categories?: Record<string, CategoryItem>;
    hideLegend?: boolean;
    radius?: number;
    arcWidth?: number;
}>(), {
    height: 275,
    hideLegend: false,
    radius: 100,
    arcWidth: 20
});

const series = computed(() => props.data);

const chartLabels = computed(() => {
    if (props.categories) {
        return Object.keys(props.categories);
    }
    return [];
});

const chartColors = computed(() => {
    if (props.categories) {
        return Object.values(props.categories).map(cat => cat.color);
    }
    return [];
});

const chartOptions = computed(() => ({
    chart: {
        type: 'donut',
        sparkline: {
            enabled: false
        }
    },
    labels: chartLabels.value,
    colors: chartColors.value,
    plotOptions: {
        pie: {
            donut: {
                size: '70%',
                labels: {
                    show: false
                }
            }
        }
    },
    legend: {
        show: !props.hideLegend,
        position: 'bottom'
    },
    responsive: [{
        breakpoint: 480,
        options: {
            chart: {
                width: 200
            },
            legend: {
                position: 'bottom'
            }
        }
    }],
    dataLabels: {
        enabled: false
    }
}));
</script>
