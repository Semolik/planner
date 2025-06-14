<template>
    <page-container header="Группы">
        <div class="groups-page" ref="container">
            <app-input
                v-model="searchQuery"
                placeholder="Поиск групп"
                type="text"
                height="50px"
                class="search-input"
            />
            <div v-if="gridInitialized" ref="scroller" class="scroller">
                <div class="groups-grid" v-auto-animate>
                    <nuxt-link
                        v-for="group in groups"
                        :key="group.id"
                        :group="group"
                        class="group-card"
                    >
                        <div class="group-name">
                            {{ group }}
                        </div>
                    </nuxt-link>
                </div>
                <div v-if="loading && !groups.length" class="loading">
                    Загрузка...
                </div>
                <div
                    v-if="!loading && !groups.length && searchQuery"
                    class="empty-results"
                >
                    Ничего не найдено
                </div>
                <div v-if="loading && groups.length" class="loading-more">
                    Загрузка...
                </div>
            </div>
        </div>
    </page-container>
</template>

<script setup>
import { useAuthStore } from "~/stores/auth";
import { EventsGroupsService } from "~/client";
import { ref, onMounted, onUnmounted, watch } from "vue";
import { useSeoMeta, useRoute, useRouter } from "#imports";
import { useInfiniteScroll } from "@vueuse/core";

useSeoMeta({
    title: "Группы",
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
const groups = ref([]);
const loading = ref(false);
const page = ref(1);
const hasMore = ref(true);
const searchQuery = ref("");
const gridColumns = ref(3);
const gap = ref(10);

// Сброс страницы
const resetPage = () => {
    page.value = 1;
    groups.value = [];
    hasMore.value = true;
};

// Загрузка данных
const loadGroups = async () => {
    if (loading.value || !hasMore.value) return;
    loading.value = true;
    try {
        const response =
            await EventsGroupsService.searchEventGroupsEventsGroupsSearchGet(
                searchQuery.value,
                page.value,
                "all" // всегда all, как указано
            );
        groups.value.push(...response);
        hasMore.value = response.length > 0;
        page.value++;
    } catch (error) {
        console.error("Failed to load groups:", error);
    } finally {
        loading.value = false;
    }
};

// Расчёт адаптивной сетки
const calculateGrid = () => {
    if (!container.value) return;
    const containerWidth = container.value.offsetWidth;
    const minItemWidth = 300;
    const gapValue = gap.value;
    gridColumns.value = Math.max(
        1,
        Math.floor((containerWidth + gapValue) / (minItemWidth + gapValue))
    );
    if (!gridInitialized.value) {
        gridInitialized.value = true;
    }
};

// Бесконечный скролл
useInfiniteScroll(
    scroller,
    async () => {
        if (!loading.value && hasMore.value) {
            await loadGroups();
        }
    },
    { distance: 100 }
);

onMounted(async () => {
    await loadGroups();
    calculateGrid();
    window.addEventListener("resize", calculateGrid);
});

onUnmounted(() => {
    window.removeEventListener("resize", calculateGrid);
});

// Сброс при изменении поискового запроса
watch(searchQuery, () => {
    resetPage();
});
</script>

<style scoped lang="scss">
.groups-page {
    display: flex;
    flex-direction: column;
    height: 100%;
    width: 100%;
    position: relative;
    box-sizing: border-box;
    padding: 0;

    .search-input {
        margin-bottom: 10px;
        width: 100%;
    }

    .scroller {
        flex: 1;
        width: 100%;
        overflow-y: auto;
        .groups-grid {
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

    .empty-results {
        display: flex;
        justify-content: center;
        align-items: center;
        font-size: 16px;
        color: #999;
        padding: 40px 0;
    }

    .group-card {
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-decoration: none;
        color: inherit;
        padding: 20px;
        border: 1px solid $border-color;
        border-radius: 8px;
        background-color: #fff;
        transition: border-color 0.3s;

        &:hover {
            border-color: black;
        }

        .group-name {
            font-size: 16px;
        }
    }
}
</style>
