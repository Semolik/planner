<template>
    <page-container header="Tasks">
        <div class="filters">
            <div
                v-for="filter in filters"
                class="filter-item"
                :class="{ active: filter.active }"
                @click="selectFilter(filter)"
            >
                <Icon :name="filter.icon" />
                <span>{{ filter.label }}</span>
            </div>
        </div>
        <div ref="container" class="tasks-page">
            <div v-if="gridInitialized" ref="scroller" class="scroller">
                <div class="tasks-grid">
                    <task-card-my
                        v-for="task in tasks"
                        :key="task.id"
                        :task="task"
                    />
                </div>
            </div>
        </div>
    </page-container>
</template>

<script setup>
import { useAuthStore } from "~/stores/auth";
import { TasksService } from "~/client";
useSeoMeta({
    title: "Задачи",
});
const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();

if (!route.query.token && !authStore.logined) {
    router.push("/login");
}

const container = ref(null);
const scroller = ref(null);
const gridInitialized = ref(false);
const tasks = ref([]);
const loading = ref(false);
const page = ref(1);
const hasMore = ref(true);
const gridColumns = ref(3);
const gap = ref(10);
const filters = ref([
    {
        label: "Активные",
        icon: "material-symbols:check_circle",
        value: "active",
        active: true,
    },
    {
        label: "Все",
        icon: "material-symbols:all-inclusive",
        active: false,
        value: "all",
    },
]);
const selectFilter = (filter) => {
    filters.value.forEach((f) => (f.active = false));
    filter.active = true;
};
const activeFilter = computed(() => {
    return filters.value.find((f) => f.active);
});
const loadEvents = async () => {
    if (loading.value || !hasMore.value) return;

    loading.value = true;
    try {
        const response = await TasksService.getMyTasksTasksMyGet(page.value, {
            filter: activeFilter.value.value,
        });
        tasks.value.push(...response);
        hasMore.value = response.length > 0;
        page.value++;
    } catch (error) {
        console.error("Failed to load tasks:", error);
    } finally {
        loading.value = false;
    }
};

const calculateGrid = () => {
    if (!container.value) return;

    const containerWidth = container.value.offsetWidth;
    const minItemWidth = 350;
    const gapValue = gap.value;

    gridColumns.value = Math.max(
        1,
        Math.floor((containerWidth + gapValue) / (minItemWidth + gapValue))
    );

    if (!gridInitialized.value) {
        gridInitialized.value = true;
    }
};

const { reset } = useInfiniteScroll(
    scroller,
    async () => {
        if (!loading.value && hasMore.value) {
            await loadEvents();
        }
    },
    { distance: 100 }
);

onMounted(async () => {
    await loadEvents();
    calculateGrid();
    window.addEventListener("resize", calculateGrid);
});
watch(
    () => activeFilter.value,
    () => {
        tasks.value = [];
        page.value = 1;
        hasMore.value = true;

        reset();
    }
);
onUnmounted(() => {
    window.removeEventListener("resize", calculateGrid);
});
</script>

<style scoped lang="scss">
.tasks-page {
    display: flex;
    flex-direction: column;
    height: 100%;
    width: 100%;
    position: relative;
    box-sizing: border-box;
    padding: 0;

    .scroller {
        flex: 1;
        width: 100%;
        overflow-y: auto;

        .tasks-grid {
            display: grid;
            grid-template-columns: repeat(v-bind("gridColumns"), 1fr);
            gap: calc(v-bind("gap") * 1px);
        }
    }

    .loading,
    .loading-more {
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 20px;
        color: #666;
    }
}
.filters {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;

    .filter-item {
        display: flex;
        align-items: center;
        gap: 5px;
        padding: 3px 10px;
        border-radius: 8px;
        cursor: pointer;
        color: $text-color;
        border: 1px solid $text-color;

        &.active {
            background-color: $text-color;
            color: white;
        }
    }
}
</style>
