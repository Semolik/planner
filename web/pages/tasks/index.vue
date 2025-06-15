<template>
    <page-container header="Tasks">
        <app-input
            v-model="searchQuery"
            type="text"
            placeholder="Поиск по задачам и мероприятиям"
        />
        <div class="filters">
            <div
                class="filter-item"
                v-for="filter in filters"
                :class="{ active: filter.active }"
                @click="selectFilter(filter)"
            >
                <Icon :name="filter.icon" />
                <span>{{ filter.label }}</span>
            </div>
        </div>
        <div class="tasks-page" ref="container">
            <div v-if="gridInitialized" ref="scroller" class="scroller">
                <div class="tasks-grid">
                    <task-card
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
const searchQuery = ref("");

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
    { label: "Все", icon: "material-symbols:all-inclusive", active: true },
    {
        label: "Выполненные",
        icon: "material-symbols:check-circle",
        active: false,
    },
    { label: "Не выполненные", icon: "material-symbols:cancel", active: false },
]);
const selectFilter = (filter) => {
    filters.value.forEach((f) => (f.active = false));
    filter.active = true;
};
const loadEvents = async () => {
    if (loading.value || !hasMore.value) return;

    loading.value = true;
    try {
        const response = await TasksService.getTasksTasksGet(
            page.value,
            false,
            false,
            null
        );
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

useInfiniteScroll(
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
