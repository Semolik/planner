<template>
    <page-container header="Группы">
        <div class="groups-page" ref="container">
            <div class="flex gap-2">
                <app-input
                    v-model="searchQuery"
                    placeholder="Поиск групп"
                    type="text"
                />
                <app-button
                    active
                    :to="{
                        name: routesNames.eventsGroupsNew,
                    }"
                >
                    Создать
                </app-button>
            </div>
            <div v-if="gridInitialized" ref="scroller" class="scroller">
                <div class="groups-grid">
                    <nuxt-link
                        v-for="group in groups"
                        :key="group.id"
                        :group="group"
                        class="group-card"
                        :to="{
                            name: routesNames.eventsGroupsGroupId,
                            params: { group_id: group.id },
                        }"
                    >
                        <div class="group-name">
                            {{ group.name }}
                        </div>
                        <template v-if="group.period_start && group.period_end">
                            <div
                                class="period"
                                v-if="group.period_start !== group.period_end"
                            >
                                {{ getDateString(group.period_start) }} -
                                {{ getDateString(group.period_end) }}
                            </div>
                            <div class="period" v-else>
                                {{ getDateString(group.period_start) }}
                            </div>
                        </template>
                        <div class="event-count">
                            {{ group.events_count }}
                            {{
                                usePluralize(group.events_count, [
                                    "мероприятие",
                                    "мероприятия",
                                    "мероприятий",
                                ])
                            }}
                        </div>
                    </nuxt-link>
                </div>

                <div v-if="!groups.length && searchQuery" class="empty-results">
                    Ничего не найдено
                </div>
            </div>
        </div>
    </page-container>
</template>
<script setup>
import { useAuthStore } from "~/stores/auth";
import { EventsGroupsService } from "~/client";
import { routesNames } from "@typed-router";

useSeoMeta({
    title: "Группы",
});
definePageMeta({
    middleware: ["admin"],
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

// Debounced search query
const debouncedSearchQuery = refDebounced(searchQuery, 300);

const resetPage = () => {
    page.value = 1;
    hasMore.value = true;
};

// Загрузка данных
const loadGroups = async () => {
    if (loading.value || !hasMore.value) return;
    loading.value = true;
    try {
        const response =
            await EventsGroupsService.searchEventGroupsEventsGroupsSearchGet(
                debouncedSearchQuery.value,
                page.value,
                "all"
            );
        if (page.value === 1) {
            groups.value = [];
        }
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
const { reset } = useInfiniteScroll(
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

watch(debouncedSearchQuery, () => {
    resetPage();
    reset();
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
    gap: 10px;

    .search-input {
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
            font-size: 18px;
            font-weight: bold;
        }
        .period {
            font-size: 14px;
            color: #666;
        }
        .event-count {
            color: #999;
            font-size: 14px;
        }
    }
}
</style>
