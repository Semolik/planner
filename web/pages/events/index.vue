<template>
    <div class="tasks-page" ref="container">
        <div v-if="gridInitialized" ref="scroller" class="scroller">
            <div
                v-for="(row, rowIndex) in groupedTasks"
                :key="rowIndex"
                class="task-row"
            >
                <task-card
                    v-for="task in row"
                    :key="task.id"
                    :task="task"
                    :style="{
                        width: `${itemWidth}px`,
                        height: `${itemHeight}px`,
                        marginRight: `${gap}px`,
                    }"
                />
            </div>
            <div v-if="loading" class="loading-more">Loading more tasks...</div>
        </div>
        <div v-else class="loading">Loading...</div>
    </div>
</template>

<script setup>
import { ref, onMounted, computed } from "vue";
import { useInfiniteScroll } from "@vueuse/core";
import { useAuthStore } from "~/stores/auth";
import { TasksService } from "~/client";
import { useRoute, useRouter } from "vue-router";

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

const gridItems = ref(3);
const itemWidth = ref(350);
const itemHeight = ref(200);
const gap = ref(10);

const groupedTasks = computed(() => {
    const result = [];
    const itemsPerRow = gridItems.value;

    for (let i = 0; i < tasks.value.length; i += itemsPerRow) {
        result.push(tasks.value.slice(i, i + itemsPerRow));
    }

    return result;
});

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

    const itemsCount = Math.max(
        1,
        Math.floor((containerWidth + gapValue) / (minItemWidth + gapValue))
    );

    const actualItemWidth =
        (containerWidth - (itemsCount - 1) * gapValue) / itemsCount;

    gridItems.value = itemsCount;
    itemWidth.value = actualItemWidth;

    if (!gridInitialized.value) {
        gridInitialized.value = true;
    }
};

// Настройка бесконечного скролла
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
        padding: calc(v-bind("gap") * 1px) calc(v-bind("gap") * 1px) 0 0;
        box-sizing: border-box;
        overflow-y: auto;

        .task-row {
            display: flex;
            margin-bottom: calc(v-bind("gap") * 1px);

            &:last-child {
                margin-bottom: 0;
            }
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
</style>
